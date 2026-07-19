"""Checks that the generated résumé outputs are correct and machine-readable.

Run with: python -m pytest -q
The PDF reading-order test is skipped when WeasyPrint is not installed.
"""

import json
import os
from pathlib import Path

import pytest

os.environ.setdefault("EMAIL_ADDRESS", "kazemi.soroush@gmail.com")
os.environ.setdefault("HOMEPAGE", "www.linkedin.com/in/kazemisoroush")

import build

HERE = Path(build.__file__).parent


@pytest.fixture(scope="session", autouse=True)
def built():
    build.main()


def read(name):
    return (HERE / name).read_text()


def test_json_resume_is_valid_and_ordered():
    r = json.loads(read("resume.json"))
    assert r["basics"]["name"] == "Soroush Kazemi"
    assert r["work"][0]["name"] == "Macquarie Group"
    assert r["work"][0]["position"] == "Senior Manager"
    assert r["work"][0]["highlights"], "the current role should have highlights"
    # A skill group with a parenthesised list stays as one keyword group.
    assert any("AWS (EKS" in kw for sk in r["skills"] for kw in sk["keywords"])


def test_plain_text_has_all_sections():
    t = read("resume.txt")
    for token in ("SUMMARY", "EXPERIENCE", "SKILLS", "EDUCATION",
                  "Macquarie Group", "Senior Manager"):
        assert token in t


def test_homepage_has_person_data():
    html = read("index.html")
    assert "application/ld+json" in html
    assert '"@type": "Person"' in html
    assert '"jobTitle": "Technology Leader"' in html


def test_llms_points_to_the_files():
    t = read("llms.txt")
    assert "resume.json" in t
    assert "resume.pdf" in t
    assert "resume.txt" in t


def test_pdf_reads_top_to_bottom():
    pdf = HERE / "resume.pdf"
    if not pdf.exists():
        pytest.skip("resume.pdf not generated (WeasyPrint not installed)")
    from pypdf import PdfReader
    text = "\n".join(p.extract_text() for p in PdfReader(str(pdf)).pages)
    i_macquarie = text.find("Senior Manager")
    i_macquarie_bullet = text.find("Led the design and delivery")
    i_evergen = text.find("Lead Software Engineer")
    assert i_macquarie != -1 and i_macquarie_bullet != -1 and i_evergen != -1
    assert i_macquarie < i_macquarie_bullet < i_evergen, \
        "the Macquarie bullet must sit under Macquarie and before Evergen"
