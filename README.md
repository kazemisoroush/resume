# Résumé

My résumé and portfolio, generated from a single source and published on every
merge to `main`:

- **Homepage**: a static site at **https://kazemisoroush.github.io/resume/**
- **PDF**: an editorial print document at `/resume.pdf`

## Single source of truth

Edit **`content.yaml`** only. [`build.py`](build.py) renders everything from it:

| Output | What |
|---|---|
| `index.html` | the portfolio homepage, with schema.org Person data |
| `resume.pdf` | a tagged PDF from `resume-print.html` via [WeasyPrint](https://weasyprint.org), with `resume.json` attached |
| `resume.json` | the résumé in the [JSON Resume](https://jsonresume.org) schema |
| `resume.txt` | a plain-text résumé |
| `llms.txt` | a discovery file that points AI agents to the files above |

These formats let AI, agents, scrapers, and applicant tracking systems read the résumé as data. The PDF is a single-column, tagged document, so its text extracts in reading order.

All three are generated (git-ignored). Do not edit them by hand. `portrait.jpg`
is the hero photo (web only; the PDF stays photo-free).

Contact details are **not** in the content. `build.py` reads `PHONE_NUMBER` /
`EMAIL_ADDRESS` / `HOMEPAGE` from the environment at build time, so no personal
phone/email lives in the source. Any value that is unset is omitted.

Configure under **Settings → Secrets and variables → Actions**:

| Name | Kind | Example |
|---|---|---|
| `PHONE_NUMBER` | Secret | `+61 4xx xxx xxx` (optional; omit to leave off the PDF) |
| `EMAIL_ADDRESS` | Variable | `you@example.com` |
| `HOMEPAGE` | Variable | `www.linkedin.com/in/kazemisoroush` |

## How CI publishes

`.github/workflows/ci.yml`, on every push to `main`: install WeasyPrint + IBM
Plex fonts → `build.py` (generate site + PDF) → assemble `_site/` (homepage,
`resume.pdf`, `portrait.jpg`) → deploy to GitHub Pages. Pull requests run the
`build` job as a check (and upload the PDF as a downloadable artifact) but do
not deploy.

## Build locally

```bash
python3 -m pip install pyyaml weasyprint   # WeasyPrint needs pango/cairo (brew install pango on macOS)
export EMAIL_ADDRESS="you@example.com" HOMEPAGE="www.linkedin.com/in/kazemisoroush"
python3 build.py            # writes index.html, resume-print.html, resume.pdf
open index.html
open resume.pdf
```

Without WeasyPrint installed, `build.py` still writes the HTML and just skips the PDF.
