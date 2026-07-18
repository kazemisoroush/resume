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

COUNTRY_CODE = {"Australia": "AU", "Iran": "IR"}


def ccode(country):
    return COUNTRY_CODE.get(country, str(country)[:2].upper())


CSS = """
  :root {
    --bg: #eef0f3; --surface: #ffffff; --surface-2: #f6f7f9;
    --ink: #14171d; --ink-2: #3b414d; --muted: #6b7280; --faint: #9aa1ac;
    --line: #dde1e7; --line-strong: #cbd0d9;
    --accent: #b06b1e; --accent-ink: #ffffff; --accent-soft: rgba(176,107,30,.12);
    --shadow: 0 1px 2px rgba(20,23,29,.04), 0 10px 30px rgba(20,23,29,.06);
    --font-display: ui-serif, "New York", "Iowan Old Style", Palatino, Georgia, serif;
    --font-sans: -apple-system, system-ui, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    --font-mono: ui-monospace, "SF Mono", "JetBrains Mono", Menlo, Consolas, monospace;
    --measure: 800px;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #0d0f13; --surface: #15181e; --surface-2: #1a1e25;
      --ink: #e9ebee; --ink-2: #c2c7d0; --muted: #8b93a1; --faint: #667080;
      --line: #262b33; --line-strong: #333a44;
      --accent: #e0a15c; --accent-ink: #14171d; --accent-soft: rgba(224,161,92,.14);
      --shadow: 0 1px 2px rgba(0,0,0,.4), 0 12px 34px rgba(0,0,0,.5);
    }
  }
  :root[data-theme="light"] {
    --bg: #eef0f3; --surface: #ffffff; --surface-2: #f6f7f9;
    --ink: #14171d; --ink-2: #3b414d; --muted: #6b7280; --faint: #9aa1ac;
    --line: #dde1e7; --line-strong: #cbd0d9;
    --accent: #b06b1e; --accent-ink: #ffffff; --accent-soft: rgba(176,107,30,.12);
    --shadow: 0 1px 2px rgba(20,23,29,.04), 0 10px 30px rgba(20,23,29,.06);
  }
  :root[data-theme="dark"] {
    --bg: #0d0f13; --surface: #15181e; --surface-2: #1a1e25;
    --ink: #e9ebee; --ink-2: #c2c7d0; --muted: #8b93a1; --faint: #667080;
    --line: #262b33; --line-strong: #333a44;
    --accent: #e0a15c; --accent-ink: #14171d; --accent-soft: rgba(224,161,92,.14);
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 12px 34px rgba(0,0,0,.5);
  }

  * { box-sizing: border-box; }
  html { scroll-behavior: smooth; }
  body {
    margin: 0; background: var(--bg); color: var(--ink);
    font-family: var(--font-sans); font-size: 16.5px; line-height: 1.62;
    -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
  }
  .wrap { max-width: var(--measure); margin: 0 auto; padding: 0 28px; }
  a { color: inherit; text-decoration: none; }

  .label {
    display: inline-flex; align-items: center; gap: 10px;
    font-family: var(--font-mono); font-size: 11.5px; letter-spacing: .18em;
    text-transform: uppercase; color: var(--muted); font-weight: 500;
  }
  .label::before { content: ""; width: 22px; height: 2px; background: var(--accent); border-radius: 2px; flex: none; }
  .rule-head { display: grid; grid-template-columns: auto 1fr; align-items: center; gap: 18px; margin: 0 0 34px; }
  .rule-head::after { content: ""; height: 1px; background: var(--line); }

  header.hero { padding: 84px 0 40px; }
  .hero-grid { display: grid; grid-template-columns: 1fr auto; gap: 44px; align-items: center; }
  .portrait {
    width: 172px; height: 215px; object-fit: cover; object-position: 50% 22%;
    border-radius: 16px; border: 1px solid var(--line); box-shadow: var(--shadow); flex: none;
  }
  .kicker { font-family: var(--font-mono); font-size: 12px; letter-spacing: .16em; text-transform: uppercase; color: var(--accent); margin: 0 0 20px; font-weight: 500; }
  h1 { font-family: var(--font-display); font-weight: 600; font-size: clamp(44px, 7.5vw, 74px); line-height: 1.02; letter-spacing: -0.02em; margin: 0; text-wrap: balance; }
  .subline { margin: 18px 0 0; font-size: 19px; color: var(--ink-2); }
  .subline b { font-weight: 600; color: var(--ink); }
  .meta-row { margin-top: 8px; font-family: var(--font-mono); font-size: 13px; color: var(--muted); letter-spacing: .02em; }
  .actions { display: flex; flex-wrap: wrap; align-items: center; gap: 14px 22px; margin-top: 30px; }
  .btn {
    display: inline-flex; align-items: center; gap: 9px;
    background: var(--accent); color: var(--accent-ink); font-weight: 600; font-size: 15px;
    padding: 12px 22px; border-radius: 8px; box-shadow: var(--shadow);
    transition: transform .16s ease, filter .16s ease;
  }
  .btn:hover { transform: translateY(-1px); filter: brightness(1.05); }
  .links { display: flex; flex-wrap: wrap; gap: 20px; font-family: var(--font-mono); font-size: 13.5px; }
  .links a { color: var(--muted); border-bottom: 1px solid transparent; padding-bottom: 1px; transition: color .15s ease, border-color .15s ease; }
  .links a:hover { color: var(--accent); border-color: var(--accent); }

  section { padding: 46px 0; border-top: 1px solid var(--line); }
  section:first-of-type { border-top: 0; }

  .about p { font-family: var(--font-display); font-size: clamp(19px, 2.4vw, 23px); line-height: 1.55; color: var(--ink-2); margin: 0 0 18px; max-width: 62ch; text-wrap: pretty; }
  .about p:last-child { margin-bottom: 0; }

  .entry { display: grid; grid-template-columns: 140px 1fr; gap: 6px 30px; padding: 6px 0 30px; }
  .entry:last-child { padding-bottom: 0; }
  .when { font-family: var(--font-mono); font-size: 12.5px; color: var(--muted); font-variant-numeric: tabular-nums; letter-spacing: .01em; padding-top: 5px; line-height: 1.5; }
  .when .now { color: var(--accent); }
  .place { display: block; color: var(--faint); margin-top: 3px; }
  .role { font-family: var(--font-display); font-size: 21px; font-weight: 600; letter-spacing: -0.01em; margin: 0; }
  .org { color: var(--muted); font-size: 14.5px; margin: 3px 0 12px; }
  .org b { color: var(--ink-2); font-weight: 600; }
  .summary { margin: 0 0 12px; color: var(--ink-2); }
  ul.bul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 7px; }
  ul.bul li { position: relative; padding-left: 20px; color: var(--ink-2); }
  ul.bul li::before { content: ""; position: absolute; left: 3px; top: 11px; width: 5px; height: 5px; border: 1.5px solid var(--accent); border-radius: 50%; }
  .stack { margin-top: 14px; font-family: var(--font-mono); font-size: 12px; line-height: 1.9; color: var(--muted); letter-spacing: .01em; }
  .stack .k { color: var(--faint); text-transform: uppercase; letter-spacing: .14em; margin-right: 8px; }

  .rows { display: flex; flex-direction: column; gap: 20px; }
  .row { display: grid; grid-template-columns: 140px 1fr; gap: 8px 30px; }
  .row .k { font-family: var(--font-mono); font-size: 12.5px; color: var(--muted); text-transform: uppercase; letter-spacing: .08em; padding-top: 2px; }
  .row .v { color: var(--ink-2); }
  .row .v .deg { font-family: var(--font-display); font-size: 18px; color: var(--ink); font-weight: 600; }
  .row .v .sub { color: var(--muted); font-size: 14px; }

  footer { padding: 40px 0 76px; border-top: 1px solid var(--line); color: var(--faint); font-family: var(--font-mono); font-size: 12.5px; line-height: 1.8; }

  a:focus-visible, .btn:focus-visible, .theme-toggle:focus-visible { outline: 2px solid var(--accent); outline-offset: 3px; border-radius: 6px; }

  .theme-toggle {
    position: fixed; top: 16px; right: 16px; z-index: 20;
    width: 40px; height: 40px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--surface); color: var(--ink-2);
    border: 1px solid var(--line); box-shadow: var(--shadow);
    cursor: pointer; transition: color .16s ease, border-color .16s ease, transform .16s ease;
  }
  .theme-toggle:hover { color: var(--accent); border-color: var(--line-strong); transform: translateY(-1px); }
  .theme-toggle svg { display: block; }

  @keyframes rise { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }
  .anim { opacity: 0; animation: rise .6s cubic-bezier(.2,.6,.2,1) forwards; }
  .d1 { animation-delay: .05s; } .d2 { animation-delay: .13s; } .d3 { animation-delay: .21s; } .d4 { animation-delay: .29s; }
  @media (prefers-reduced-motion: reduce) { .anim { opacity: 1; animation: none; } html { scroll-behavior: auto; } }

  @media (max-width: 620px) {
    .entry, .row { grid-template-columns: 1fr; gap: 4px; }
    .when { padding-top: 0; }
    header.hero { padding-top: 56px; }
    .hero-grid { grid-template-columns: 1fr; gap: 26px; justify-items: start; }
    .portrait { width: 132px; height: 165px; order: -1; }
  }
"""

SCRIPT = """
  (function () {
    var root = document.documentElement;
    var btn = document.getElementById('theme-toggle');
    var MOON = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>';
    var SUN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
    function isDark() {
      var t = root.getAttribute('data-theme');
      if (t === 'dark') return true;
      if (t === 'light') return false;
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    function paint() {
      btn.innerHTML = isDark() ? SUN : MOON;
      btn.setAttribute('aria-label', isDark() ? 'Switch to light theme' : 'Switch to dark theme');
    }
    var saved = null;
    try { saved = localStorage.getItem('theme'); } catch (e) {}
    if (saved === 'dark' || saved === 'light') root.setAttribute('data-theme', saved);
    paint();
    btn.addEventListener('click', function () {
      var next = isDark() ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      paint();
    });
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function () {
      if (!root.getAttribute('data-theme')) paint();
    });
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.anim').forEach(function (el) { el.style.opacity = 1; });
    }
  })();
"""


def render_html(data):
    name, title = data["name"], data["title"]
    exp0 = data["experience"][0]
    p = []
    p.append('<!DOCTYPE html>\n<html lang="en">\n<head>\n'
             '<meta charset="utf-8" />\n'
             '<meta name="viewport" content="width=device-width, initial-scale=1" />\n'
             '<title>' + h(name) + ' — ' + h(title) + '</title>\n'
             '<meta name="description" content="' + h(name) + ' — ' + h(title)
             + ', based in ' + h(data["location"]) + '. Résumé and portfolio." />\n'
             '<style>' + CSS + '</style>\n</head>\n<body>\n')

    p.append('<button class="theme-toggle" id="theme-toggle" type="button" aria-label="Toggle colour theme"></button>\n\n')
    p.append('  <div class="wrap">\n')

    # Hero
    p.append(
        '    <header class="hero">\n'
        '      <div class="hero-grid">\n'
        '        <div class="hero-text">\n'
        '          <p class="kicker anim d1">' + h(data["eyebrow"]) + '</p>\n'
        '          <h1 class="anim d1">' + h(name) + '</h1>\n'
        '          <p class="subline anim d2"><b>' + h(exp0["role"]) + '</b> at ' + h(exp0["org"])
        + ' — ' + h(data["tagline"]) + '</p>\n'
        '          <p class="meta-row anim d2">' + h(data["location"]) + ' · ' + h(data["country"]) + '</p>\n'
        '          <div class="actions anim d3">\n'
        '            <a class="btn" href="resume.pdf" target="_blank" rel="noopener">Open PDF résumé ↗</a>\n'
        '            <nav class="links">\n'
        '              <a href="' + h(data["github"]) + '" target="_blank" rel="noopener">GitHub</a>\n'
        '              <a href="https://HOMEPAGE_PLACEHOLDER" target="_blank" rel="noopener">LinkedIn</a>\n'
        '              <a href="mailto:EMAIL_ADDRESS_PLACEHOLDER">Email</a>\n'
        '            </nav>\n'
        '          </div>\n'
        '        </div>\n'
        '        <img class="portrait anim d2" src="' + h(data["photo"]) + '" alt="' + h(name)
        + '" width="172" height="215" />\n'
        '      </div>\n'
        '    </header>\n\n')

    # About
    p.append('    <section class="about anim d4">\n')
    for para in data["about"]:
        p.append('      <p>' + h(para) + '</p>\n')
    p.append('    </section>\n\n')

    # Experience
    p.append('    <section>\n      <div class="rule-head"><span class="label">Experience</span></div>\n')
    for e in data["experience"]:
        place = h(e["city"]) + ", " + ccode(e["country"])
        if str(e["end"]).lower() == "present":
            when = ('<span class="now">' + h(e["start"]) + ' — Now</span>'
                    '<span class="place">' + place + '</span>')
        else:
            when = h(e["start"]) + ' — ' + h(e["end"]) + '<span class="place">' + place + '</span>'
        p.append('\n      <div class="entry">\n'
                 '        <div class="when">' + when + '</div>\n'
                 '        <div class="what">\n'
                 '          <h3 class="role">' + h(e["role"]) + '</h3>\n'
                 '          <p class="org"><b>' + h(e["org"]) + '</b></p>\n'
                 '          <p class="summary">' + h(e["summary"]) + '</p>\n')
        bullets = e.get("bullets") or []
        if bullets:
            p.append('          <ul class="bul">\n')
            for b in bullets:
                p.append('            <li>' + h(b) + '</li>\n')
            p.append('          </ul>\n')
        if e.get("tech"):
            stack = " · ".join(t.strip() for t in str(e["tech"]).split(","))
            p.append('          <p class="stack"><span class="k">Stack</span>' + h(stack) + '</p>\n')
        p.append('        </div>\n      </div>\n')
    p.append('    </section>\n\n')

    # Skills
    p.append('    <section>\n      <div class="rule-head"><span class="label">Skills</span></div>\n      <div class="rows">\n')
    for sk in data["skills"]:
        p.append('        <div class="row">\n'
                 '          <div class="k">' + h(sk["label"]) + '</div>\n'
                 '          <div class="v">' + h(sk["items"]) + '</div>\n'
                 '        </div>\n')
    p.append('      </div>\n    </section>\n\n')

    # Education
    p.append('    <section>\n      <div class="rule-head"><span class="label">Education</span></div>\n      <div class="rows">\n')
    for ed in data["education"]:
        p.append('        <div class="row">\n'
                 '          <div class="k">' + h(ed["start"]) + ' — ' + h(ed["end"]) + '</div>\n'
                 '          <div class="v"><span class="deg">' + h(ed["degree"]) + '</span><br>'
                 '<span class="sub">' + h(ed["org"]) + ' · ' + h(ed["detail"]) + '</span></div>\n'
                 '        </div>\n')
    p.append('      </div>\n    </section>\n\n')

    p.append('    <footer>\n      References available on request.\n    </footer>\n')
    p.append('  </div>\n\n<script>' + SCRIPT + '</script>\n</body>\n</html>\n')
    return "".join(p)


def main():
    data = yaml.safe_load((HERE / "content.yaml").read_text())
    (HERE / "resume.tex").write_text(render_tex(data))
    (HERE / "index.html").write_text(render_html(data))
    print("Generated resume.tex and index.html from content.yaml")


if __name__ == "__main__":
    main()
