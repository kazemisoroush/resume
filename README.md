# Résumé

My résumé and portfolio, generated from a single source and published on every
merge to `main`:

- **PDF** — LaTeX ([moderncv](https://ctan.org/pkg/moderncv)) → `resume.pdf`
- **Homepage** — a static site at **https://kazemisoroush.github.io/resume/**

## Single source of truth

Edit **`content.yaml`** only. [`build.py`](build.py) renders both `resume.tex`
and `index.html` from it, so the PDF and the web page can never drift. Those two
files are generated (git-ignored) — don't edit them by hand.

Contact details are **not** in the content. The `PHONE_NUMBER` / `EMAIL_ADDRESS`
/ `HOMEPAGE` placeholders are filled in at build time from repo settings, so no
personal phone/email lives in the source. Any unset value renders blank.

Configure under **Settings → Secrets and variables → Actions**:

| Name | Kind | Example |
|---|---|---|
| `PHONE_NUMBER` | Secret | `04xx xxx xxx` (optional; omit to leave off the public PDF) |
| `EMAIL_ADDRESS` | Variable | `you@example.com` |
| `HOMEPAGE` | Variable | `www.linkedin.com/in/kazemisoroush` |

## How CI publishes

`.github/workflows/latex-ci.yml` on every push to `main`:
`build.py` (generate) → inject contact placeholders → compile PDF
(`xu-cheng/latex-action`) → assemble `_site/` (homepage + `resume.pdf`) →
deploy to GitHub Pages. Pull requests run the `build` job as a check but do not
deploy.

## Build locally

```bash
python3 -m pip install pyyaml
python3 build.py            # regenerates resume.tex and index.html

# preview the PDF (contact fields render blank unless you set the vars first)
export EMAIL_ADDRESS="you@example.com" HOMEPAGE="www.linkedin.com/in/kazemisoroush"
sed -e "s|PHONE_NUMBER_PLACEHOLDER||g" \
    -e "s|EMAIL_ADDRESS_PLACEHOLDER|${EMAIL_ADDRESS}|g" \
    -e "s|HOMEPAGE_PLACEHOLDER|${HOMEPAGE}|g" \
    resume.tex > resume_replaced.tex
pdflatex -interaction=nonstopmode resume_replaced.tex
open resume_replaced.pdf   # macOS; xdg-open on Linux

# preview the homepage
open index.html
```
