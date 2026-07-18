#!/usr/bin/env python3
"""Render resume.tex and index.html from content.yaml.

content.yaml is the single source of truth. This script generates both the
LaTeX (PDF) source and the HTML homepage so the two can never drift. Contact
details stay out of here: the PHONE/EMAIL/HOMEPAGE placeholders are emitted
verbatim and filled in later from CI secrets/variables.

Usage: python build.py   (writes resume.tex and index.html next to this file)
"""

import html
import re
from pathlib import Path

import yaml

HERE = Path(__file__).parent


# --- escaping ---------------------------------------------------------------

_TEX_SPECIAL = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def tex(s):
    """Escape a string for LaTeX, normalising unicode punctuation to ASCII."""
    s = str(s)
    s = (s.replace("—", "---").replace("–", "--")
          .replace("’", "'").replace("‘", "'")
          .replace("“", "``").replace("”", "''"))
    return re.sub(r"[\\&%$#_{}~^]", lambda m: _TEX_SPECIAL[m.group()], s)


def h(s):
    """Escape a string for HTML text content."""
    return html.escape(str(s), quote=False)


# --- LaTeX rendering --------------------------------------------------------

TEX_PREAMBLE = r"""\documentclass[14pt, a4paper, sans]{moderncv}

\moderncvstyle{classic}
\moderncvcolor{blue}

\pdfgentounicode=1

\usepackage[scale=0.88]{geometry}
\setlength{\hintscolumnwidth}{4cm}

\renewcommand{\labelitemi}{$\bullet$}
\renewcommand{\normalsize}{\fontsize{13}{16}\selectfont}
\renewcommand{\baselinestretch}{1.2}

\firstname{%(firstname)s}
\familyname{%(familyname)s}

\title{%(title)s}
\address{}{%(location)s}
\newcommand{\phoneNumber}{PHONE_NUMBER_PLACEHOLDER}
\newcommand{\emailAddress}{EMAIL_ADDRESS_PLACEHOLDER}
\newcommand{\homePage}{HOMEPAGE_PLACEHOLDER}

\ifthenelse{\equal{\phoneNumber}{}}{}{\mobile{\phoneNumber}}
\ifthenelse{\equal{\emailAddress}{}}{}{\email{\emailAddress}}
\ifthenelse{\equal{\homePage}{}}{}{\homepage{\homePage}{}}
\renewcommand*{\quotefont}{\small\slshape}

\quote{
    \begin{minipage}{\quotewidth}
        \textit{
            \fontsize{13}{16}\selectfont
%(about)s
        }
    \end{minipage}
}

\begin{document}

    \makecvtitle
"""


def render_tex(data):
    first, _, last = data["name"].partition(" ")
    out = [TEX_PREAMBLE % {
        "firstname": tex(first),
        "familyname": tex(last),
        "title": tex(data["title"]),
        "location": tex(data["location"]),
        "about": "\n".join("            " + tex(p) for p in data["about"]),
    }]

    out.append("\n    \\section{Experience}\\label{sec:experience}\n")
    for e in data["experience"]:
        body = ["        \\fontsize{13}{16}\\selectfont",
                "        " + tex(e["summary"])]
        bullets = e.get("bullets") or []
        items = ["            \\item " + tex(b) for b in bullets]
        if e.get("tech"):
            items.append("            \\item Tech: " + tex(e["tech"]) + ".")
        if items:
            body.append("        \\begin{itemize}")
            body.extend(items)
            body.append("        \\end{itemize}")
        out.append(
            "\n    \\cventry\n"
            "    {%s -- %s}\n"
            "    {%s}\n"
            "    {\\newline \\textcolor{gray}{%s}}\n"
            "    {\\textcolor{gray}{%s}}\n"
            "    {\\textcolor{gray}{%s}}\n"
            "    {\n%s\n    }\n" % (
                tex(e["start"]), tex(e["end"]), tex(e["role"]), tex(e["org"]),
                tex(e["city"]), tex(e["country"]), "\n".join(body)))

    out.append("\n    \\section{Education}\\label{sec:education}\n")
    for ed in data["education"]:
        out.append(
            "\n    \\cventry\n"
            "    {%s -- %s}\n"
            "    {%s}\n"
            "    {%s}\n"
            "    {%s}\n"
            "    {%s}\n"
            "    {%s}\n" % (
                tex(ed["start"]), tex(ed["end"]), tex(ed["degree"]),
                tex(ed["org"]), tex(ed["city"]), tex(ed["country"]),
                tex(ed["detail"])))

    out.append("\n    \\section{Skills}\\label{sec:skills}\n\n")
    for sk in data["skills"]:
        out.append("    \\cvitem{%s}{%s}\n" % (tex(sk["label"]), tex(sk["items"])))

    out.append("\n    \\section{References}\\label{sec:references}\n")
    out.append("    \\cvitem{}{Available on request}\n\n")
    out.append("\\end{document}\n")
    return "".join(out)


# --- HTML rendering ---------------------------------------------------------

CSS = """
  :root {
    --bg: #f7f7f5; --surface: #ffffff; --ink: #1a1a1a; --muted: #6b6b6b;
    --line: #e6e6e2; --accent: #2f6f4f; --accent-ink: #ffffff;
    --shadow: 0 1px 2px rgba(0,0,0,.05), 0 8px 24px rgba(0,0,0,.06);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0f1211; --surface: #171b19; --ink: #ececec; --muted: #9aa39e;
      --line: #262c29; --accent: #57b98a; --accent-ink: #0f1211;
      --shadow: 0 1px 2px rgba(0,0,0,.3), 0 8px 30px rgba(0,0,0,.4);
    }
  }
  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font: 16px/1.65 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 760px; margin: 0 auto; padding: 0 24px; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }
  header { padding: 72px 0 40px; border-bottom: 1px solid var(--line); }
  .eyebrow { color: var(--accent); font-weight: 600; letter-spacing: .08em; text-transform: uppercase; font-size: 13px; margin: 0 0 12px; }
  h1 { font-size: clamp(34px, 6vw, 52px); line-height: 1.05; margin: 0 0 10px; letter-spacing: -0.02em; }
  .role { font-size: 20px; color: var(--muted); margin: 0 0 4px; }
  .place { color: var(--muted); margin: 0 0 28px; }
  .actions { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; }
  .btn {
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--accent); color: var(--accent-ink);
    padding: 11px 20px; border-radius: 999px; font-weight: 600; font-size: 15px;
    box-shadow: var(--shadow);
  }
  .btn:hover { text-decoration: none; filter: brightness(1.05); }
  .links { display: flex; flex-wrap: wrap; gap: 18px; font-size: 15px; }
  section { padding: 44px 0; border-bottom: 1px solid var(--line); }
  h2 { font-size: 13px; letter-spacing: .1em; text-transform: uppercase; color: var(--muted); margin: 0 0 28px; font-weight: 700; }
  .lead { font-size: 19px; line-height: 1.6; margin: 0 0 16px; }
  .lead:last-child { margin-bottom: 0; }
  .entry { display: grid; grid-template-columns: 150px 1fr; gap: 8px 28px; margin-bottom: 34px; }
  .entry:last-child { margin-bottom: 0; }
  .when { color: var(--muted); font-size: 14px; padding-top: 3px; }
  .what h3 { margin: 0; font-size: 18px; letter-spacing: -0.01em; }
  .org { color: var(--muted); font-size: 15px; margin: 2px 0 10px; }
  .what p { margin: 0 0 10px; }
  .what ul { margin: 8px 0 0; padding-left: 18px; }
  .what li { margin: 4px 0; }
  .tech { font-size: 14px; color: var(--muted); margin-top: 10px; }
  .tech strong { color: var(--ink); font-weight: 600; }
  .two { display: grid; grid-template-columns: 150px 1fr; gap: 8px 28px; }
  .two + .two { margin-top: 20px; }
  footer { padding: 40px 0 72px; color: var(--muted); font-size: 14px; }
  @media (max-width: 560px) {
    .entry, .two { grid-template-columns: 1fr; gap: 2px; }
    .when { padding-top: 0; }
    header { padding-top: 52px; }
  }
"""


def render_html(data):
    name, title = data["name"], data["title"]
    parts = []
    parts.append('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
                 '<meta charset="utf-8" />\n'
                 '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
                 '<title>' + h(name) + ' — ' + h(title) + '</title>\n'
                 '<meta name="description" content="' + h(name) + ' — ' + h(title)
                 + ', based in ' + h(data["location"]) + '. Résumé and portfolio." />\n'
                 '<style>' + CSS + '</style>\n</head>\n<body>\n  <div class="wrap">\n')

    # Header
    parts.append(
        '    <header>\n'
        '      <p class="eyebrow">' + h(data["eyebrow"]) + '</p>\n'
        '      <h1>' + h(name) + '</h1>\n'
        '      <p class="role">' + h(data["current"]) + '</p>\n'
        '      <p class="place">' + h(data["location"]) + ' · ' + h(data["country"]) + '</p>\n'
        '      <div class="actions">\n'
        '        <a class="btn" href="resume.pdf" target="_blank" rel="noopener">Open PDF résumé ↗</a>\n'
        '        <div class="links">\n'
        '          <a href="' + h(data["github"]) + '">GitHub</a>\n'
        '          <a href="https://HOMEPAGE_PLACEHOLDER">LinkedIn</a>\n'
        '          <a href="mailto:EMAIL_ADDRESS_PLACEHOLDER">Email</a>\n'
        '        </div>\n'
        '      </div>\n'
        '    </header>\n\n')

    # About
    parts.append('    <section>\n      <h2>About</h2>\n')
    for p in data["about"]:
        parts.append('      <p class="lead">' + h(p) + '</p>\n')
    parts.append('    </section>\n\n')

    # Experience
    parts.append('    <section>\n      <h2>Experience</h2>\n')
    for e in data["experience"]:
        parts.append('\n      <div class="entry">\n'
                     '        <div class="when">' + h(e["start"]) + ' — ' + h(e["end"]) + '</div>\n'
                     '        <div class="what">\n'
                     '          <h3>' + h(e["role"]) + '</h3>\n'
                     '          <div class="org">' + h(e["org"]) + ' · ' + h(e["city"]) + ', ' + h(e["country"]) + '</div>\n'
                     '          <p>' + h(e["summary"]) + '</p>\n')
        bullets = e.get("bullets") or []
        if bullets:
            parts.append('          <ul>\n')
            for b in bullets:
                parts.append('            <li>' + h(b) + '</li>\n')
            parts.append('          </ul>\n')
        if e.get("tech"):
            parts.append('          <p class="tech"><strong>Tech:</strong> ' + h(e["tech"]) + '</p>\n')
        parts.append('        </div>\n      </div>\n')
    parts.append('    </section>\n\n')

    # Education
    parts.append('    <section>\n      <h2>Education</h2>\n')
    for ed in data["education"]:
        parts.append('      <div class="two">\n'
                     '        <div class="when">' + h(ed["start"]) + ' — ' + h(ed["end"]) + '</div>\n'
                     '        <div class="what">\n'
                     '          <h3>' + h(ed["degree"]) + '</h3>\n'
                     '          <div class="org">' + h(ed["org"]) + ' · ' + h(ed["city"]) + ', ' + h(ed["country"]) + '</div>\n'
                     '          <p>' + h(ed["detail"]) + '.</p>\n'
                     '        </div>\n      </div>\n')
    parts.append('    </section>\n\n')

    # Skills
    parts.append('    <section>\n      <h2>Skills</h2>\n')
    for sk in data["skills"]:
        parts.append('      <div class="two">\n'
                     '        <div class="when">' + h(sk["label"]) + '</div>\n'
                     '        <div class="what"><p>' + h(sk["items"]) + '</p></div>\n'
                     '      </div>\n')
    parts.append('    </section>\n\n')

    parts.append(
        '    <footer>\n'
        '      References available on request. · Built from\n'
        '      <a href="' + h(data["github"]) + '/resume">kazemisoroush/resume</a>,\n'
        '      published automatically on every merge to <code>main</code>.\n'
        '    </footer>\n'
        '  </div>\n</body>\n</html>\n')
    return "".join(parts)


def main():
    data = yaml.safe_load((HERE / "content.yaml").read_text())
    (HERE / "resume.tex").write_text(render_tex(data))
    (HERE / "index.html").write_text(render_html(data))
    print("Generated resume.tex and index.html from content.yaml")


if __name__ == "__main__":
    main()
