#!/usr/bin/env python3
"""Fetch recent publications for the KISysBio profile README.

Tries Google Scholar first (Dr Tsoka's profile), then falls back to OpenAlex
if Scholar rate-limits the request.
"""

from __future__ import annotations

import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import urllib.request

SCHOLAR_USER_ID = "LUU0EFgAAAAJ"
OPENALEX_AUTHOR_ID = "A5076507299"
MAX_PUBLICATIONS = 10
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "profile" / "data" / "publications.json"

SKIP_TITLE_PATTERN = re.compile(
    r"^(figure|supplementary|supplement)\b",
    re.IGNORECASE,
)


def http_get_json(url: str, timeout: int = 30) -> dict:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "KISysBio-profile-bot/1.0 (https://github.com/KISysBio)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode())


def normalise_publication(
    title: str,
    year: str,
    venue: str,
    url: str,
    citations: int | None = None,
) -> dict | None:
    title = (title or "").strip()
    if not title or SKIP_TITLE_PATTERN.search(title):
        return None
    return {
        "title": title,
        "year": str(year) if year else "",
        "venue": (venue or "").strip(),
        "url": (url or "").strip(),
        "citations": citations,
    }


def fetch_from_openalex(limit: int = MAX_PUBLICATIONS) -> list[dict]:
    url = (
        "https://api.openalex.org/works"
        f"?filter=author.id:{OPENALEX_AUTHOR_ID}"
        "&sort=publication_date:desc"
        f"&per_page={limit * 3}"
    )
    payload = http_get_json(url)
    publications: list[dict] = []
    for work in payload.get("results", []):
        title = work.get("title") or work.get("display_name") or ""
        year = (work.get("publication_date") or "")[:4]
        venue = ((work.get("primary_location") or {}).get("source") or {}).get(
            "display_name", ""
        )
        link = work.get("doi") or work.get("id") or ""
        if link and link.startswith("https://doi.org/"):
            pass
        elif work.get("doi"):
            link = f"https://doi.org/{work['doi'].removeprefix('https://doi.org/')}"
        else:
            link = work.get("id", "")

        pub = normalise_publication(
            title=title,
            year=year,
            venue=venue,
            url=link,
            citations=work.get("cited_by_count"),
        )
        if pub:
            publications.append(pub)
        if len(publications) >= limit:
            break
    return publications


def fetch_from_scholar(limit: int = MAX_PUBLICATIONS) -> list[dict]:
    from scholarly import scholarly

    author = scholarly.search_author_id(SCHOLAR_USER_ID)
    author = scholarly.fill(author, sections=["publications"])

    candidates: list[dict] = []
    for pub in author.get("publications", []):
        bib = pub.get("bib", {})
        title = bib.get("title")
        year = bib.get("pub_year")
        if not title:
            continue
        candidates.append(
            {
                "title": title,
                "year": str(year) if year else "",
                "venue": bib.get("venue") or bib.get("journal") or "",
                "url": "",
                "citations": pub.get("num_citations"),
                "_pub": pub,
            }
        )

    candidates.sort(key=lambda item: int(item["year"] or 0), reverse=True)

    publications: list[dict] = []
    for candidate in candidates:
        if len(publications) >= limit:
            break
        pub = candidate["_pub"]
        try:
            filled = scholarly.fill(pub)
            bib = filled.get("bib", {})
            normalised = normalise_publication(
                title=bib.get("title") or candidate["title"],
                year=str(bib.get("pub_year") or candidate["year"]),
                venue=bib.get("venue") or bib.get("journal") or candidate["venue"],
                url=filled.get("pub_url") or filled.get("eprint_url") or "",
                citations=filled.get("num_citations", candidate.get("citations")),
            )
            if normalised:
                publications.append(normalised)
            time.sleep(1.5)
        except Exception:
            normalised = normalise_publication(
                title=candidate["title"],
                year=candidate["year"],
                venue=candidate["venue"],
                url="",
                citations=candidate.get("citations"),
            )
            if normalised:
                publications.append(normalised)
    return publications


def fetch_publications() -> dict:
    source = "google_scholar"
    scholar_url = f"https://scholar.google.com/citations?user={SCHOLAR_USER_ID}&hl=en"
    error = None
    publications: list[dict] = []

    try:
        publications = fetch_from_scholar()
    except Exception as exc:
        error = str(exc)
        source = "openalex"
        publications = fetch_from_openalex()

    return {
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "source": source,
        "scholar_profile": scholar_url,
        "scholar_user_id": SCHOLAR_USER_ID,
        "fetch_error": error,
        "publications": publications,
    }


def main() -> int:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = fetch_publications()
    DATA_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(payload['publications'])} publications to {DATA_PATH} (source: {payload['source']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
