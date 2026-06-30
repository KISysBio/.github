#!/usr/bin/env python3
"""Inject publication markdown into profile/README.md between marker comments."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README_PATH = ROOT / "profile" / "README.md"
DATA_PATH = ROOT / "profile" / "data" / "publications.json"

START = "<!-- PUBLICATIONS:START -->"
END = "<!-- PUBLICATIONS:END -->"


def escape_md(text: str) -> str:
    return text.replace("|", "\\|")


def render_publications(payload: dict) -> str:
    publications = payload.get("publications", [])
    updated = payload.get("updated_at", "unknown")
    scholar_url = payload.get("scholar_profile", "")
    source = payload.get("source", "unknown")

    lines = [
        "## Recent publications",
        "",
        f"Recent research from the group (auto-updated monthly from "
        f"[Dr Sophia Tsoka's Google Scholar profile]({scholar_url}); "
        f"last sync: **{updated}**).",
        "",
    ]

    if not publications:
        lines.append("_Publications could not be fetched automatically. See the "
                      f"[Google Scholar profile]({scholar_url}) for the latest work._")
        lines.append("")
        return "\n".join(lines)

    lines.extend(
        [
            "| Year | Publication | Venue |",
            "| :--: | :-- | :-- |",
        ]
    )

    for pub in publications:
        year = pub.get("year") or "—"
        title = escape_md(pub.get("title", ""))
        venue = escape_md(pub.get("venue") or "—")
        url = pub.get("url", "")
        if url:
            title_cell = f"[{title}]({url})"
        else:
            title_cell = title
        lines.append(f"| {year} | {title_cell} | {venue} |")

    lines.extend(
        [
            "",
            f"<sub>Source: {source} · "
            f"[View full publication list on Google Scholar →]({scholar_url})</sub>",
            "",
        ]
    )
    return "\n".join(lines)


def update_readme(section: str) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    if START not in content or END not in content:
        raise SystemExit(f"README is missing {START} / {END} markers")

    start_idx = content.index(START)
    end_idx = content.index(END) + len(END)
    new_content = content[:start_idx] + START + "\n\n" + section.rstrip() + "\n\n" + END + content[end_idx:]
    README_PATH.write_text(new_content, encoding="utf-8")


def main() -> int:
    if not DATA_PATH.exists():
        raise SystemExit(f"Missing data file: {DATA_PATH}")

    payload = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    section = render_publications(payload)
    update_readme(section)
    print(f"Updated publications section in {README_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
