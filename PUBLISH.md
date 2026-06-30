# KISysBio GitHub Organization Profile

This folder contains the **organization profile README** for [KISysBio](https://github.com/KISysBio).

GitHub displays `profile/README.md` from the `.github` repository on the org's main page.

## Structure

```
.github/                    → push contents of this folder to KISysBio/.github
├── profile/README.md       → main org profile page
└── assets/banner.svg       → animated network banner (SVG)
```

## Publish

```bash
cd kisysbio-github
git init
git remote add origin git@github.com:KISysBio/.github.git
git add profile/ assets/
git commit -m "Add organization profile README with team and research overview"
git branch -M main
git push -u origin main
```

After pushing, visit https://github.com/KISysBio — the README should appear within a minute.

## Customise

- **Member bios:** Edit the "Group members" and "Alumni" tables in `profile/README.md`.
- **Repositories:** Add or remove rows in the "Featured repositories" table as new projects are published.
- **Publications:** Auto-updated monthly via `.github/workflows/update-publications.yml`. To refresh manually, run `workflow_dispatch` on that workflow in GitHub Actions, or locally:

  ```bash
  pip install scholarly
  python scripts/fetch_publications.py
  python scripts/update_profile_publications.py
  ```

- **Banner colours:** Edit `assets/banner.svg` — indigo/purple theme matches KCL crimson accents in the badges.

## Notes

- Animated elements use [readme-typing-svg](https://github.com/DenverCoder1/readme-typing-svg) and SMIL animations in the SVG banner (supported on GitHub).
- The waving footer uses [capsule-render](https://github.com/kyechan99/capsule-render).
