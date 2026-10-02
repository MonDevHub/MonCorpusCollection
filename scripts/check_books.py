#!/usr/bin/env python3
"""Check books/records.csv against the book folders.

The table is only worth having if it cannot drift from the texts it describes, so this fails on:
a book folder with no row, a row with no folder, a malformed checksum or date, a page count that
disagrees with the `[page N]` markers in the text, and a character count that disagrees with the
text. Exits 1 on any failure.
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

BOOKS = Path(__file__).resolve().parent.parent / "books"
SHA = re.compile(r"^[0-9a-f]{64}$")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
MARKER = re.compile(r"^\[page \d+\]$")


def measure(text_path: Path) -> tuple[int, int]:
    """Return (page markers, non-whitespace characters outside the markers)."""
    markers = chars = 0
    for line in text_path.read_text(encoding="utf-8").splitlines():
        if MARKER.match(line):
            markers += 1
        else:
            chars += sum(1 for c in line if not c.isspace())
    return markers, chars


def main() -> int:
    problems: list[str] = []
    with (BOOKS / "records.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    slugs = [r["slug"] for r in rows]
    folders = sorted(p.name for p in BOOKS.iterdir() if p.is_dir())
    for name in folders:
        if name not in slugs:
            problems.append(f"{name}: has a folder but no row in records.csv")
    for row in rows:
        slug = row["slug"]
        if slugs.count(slug) > 1:
            problems.append(f"{slug}: appears more than once")
        text = BOOKS / slug / f"{slug}.txt"
        if not text.is_file():
            problems.append(f"{slug}: no {slug}/{slug}.txt")
            continue
        if not (BOOKS / slug / "README.md").is_file():
            problems.append(f"{slug}: no README.md")
        if not SHA.match(row["source_sha256"]):
            problems.append(f"{slug}: source_sha256 is not 64 lowercase hex characters")
        if not DATE.match(row["extracted_on"]):
            problems.append(f"{slug}: extracted_on is not a YYYY-MM-DD date")
        if not row["review"].strip():
            problems.append(f"{slug}: review is empty (write 'not recorded' if unknown)")
        markers, chars = measure(text)
        if str(markers) != row["pages_kept"]:
            problems.append(f"{slug}: pages_kept is {row['pages_kept']} but the text has {markers} page markers")
        if int(row["pages_kept"]) > int(row["pages_pdf"]):
            problems.append(f"{slug}: pages_kept exceeds pages_pdf")
        if str(chars) != row["characters"]:
            problems.append(f"{slug}: characters is {row['characters']} but the text has {chars}")
    if problems:
        print("books/records.csv does not match books/:")
        for p in problems:
            print(f"  {p}")
        return 1
    print(f"books/records.csv: {len(rows)} book(s), table and texts agree")
    return 0


if __name__ == "__main__":
    sys.exit(main())
