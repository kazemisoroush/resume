# Résumé

LaTeX résumé built with [moderncv](https://ctan.org/pkg/moderncv). Contact
details are kept out of the source via placeholders that get filled in at build
time, so no personal phone/email lives in this repo.

## Build in CI

Every push to `main` runs `.github/workflows/latex-ci.yml`, which fills in the
placeholders and compiles `resume.tex`. Download the compiled PDF from the
workflow run's **Artifacts** (`resume-pdf`).

Configure these under repo **Settings → Secrets and variables → Actions**:

| Name | Kind | Example |
|---|---|---|
| `PHONE_NUMBER` | Secret | `04xx xxx xxx` |
| `EMAIL_ADDRESS` | Secret | `you@example.com` |
| `HOMEPAGE` | Variable | `www.linkedin.com/in/kazemisoroush` |

Any placeholder left unset simply renders blank on the résumé.

## Build locally

Set your details as environment variables, then compile:

```bash
export PHONE_NUMBER="04xx xxx xxx"
export EMAIL_ADDRESS="you@example.com"
export HOMEPAGE="www.linkedin.com/in/kazemisoroush"

sed -e "s|PHONE_NUMBER_PLACEHOLDER|${PHONE_NUMBER}|g" \
    -e "s|EMAIL_ADDRESS_PLACEHOLDER|${EMAIL_ADDRESS}|g" \
    -e "s|HOMEPAGE_PLACEHOLDER|${HOMEPAGE}|g" \
    resume.tex > resume_replaced.tex

pdflatex -interaction=nonstopmode resume_replaced.tex
open resume_replaced.pdf   # macOS; use xdg-open on Linux
```

`resume_replaced.*` build outputs are git-ignored.
