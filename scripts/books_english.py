#!/usr/bin/env python3
"""Read the English pages of a book with an English OCR.

The Mon model reads English badly (run-together words, Myanmar glyphs mixed in). books_filter.py marks
such pages `english`; this reads them again with Tesseract's English model so they are kept, not lost.

    books_english.py BOOK.pdf REPORT.csv --out DIR

Writes DIR/pNNNN.txt for each page the report marks `english` whose read is confident, and DIR/confidence.csv
with every page's mean word confidence. A page the first read called English is often a Mon page it
misread as Latin noise, and Tesseract then turns the Myanmar script into more Latin noise, so a page is
kept only when Tesseract's own mean word confidence is at least --min-confidence (default 75) over at
least --min-words words. Pass DIR to books_filter.py with --english-dir. Needs pdftoppm and tesseract
with the `eng` language.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path


def read_page(pdf: Path, page: int) -> tuple[str, float, int] | None:
    """Return (text, mean word confidence, word count) for one page."""
    with tempfile.TemporaryDirectory() as tmp:
        stem = Path(tmp) / "page"
        render = subprocess.run(
            ["pdftoppm", "-r", "300", "-gray", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf), str(stem)],
            capture_output=True,
        )
        if render.returncode != 0:
            return None
        text = subprocess.run(["tesseract", str(stem) + ".png", "stdout", "-l", "eng"], capture_output=True, text=True)
        tsv = subprocess.run(["tesseract", str(stem) + ".png", "stdout", "-l", "eng", "tsv"], capture_output=True, text=True)
        if text.returncode != 0 or tsv.returncode != 0:
            return None
        confs = []
        for row in tsv.stdout.splitlines()[1:]:
            cols = row.split("\t")
            if len(cols) >= 12 and cols[0] == "5" and cols[11].strip() and float(cols[10]) >= 0:
                confs.append(float(cols[10]))
        return text.stdout, (sum(confs) / len(confs) if confs else 0.0), len(confs)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pdf", type=Path)
    p.add_argument("report", type=Path)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--min-confidence", type=float, default=75.0)
    p.add_argument("--min-words", type=int, default=30)
    a = p.parse_args()
    with a.report.open(encoding="utf-8", newline="") as fh:
        pages = [int(r["page"]) for r in csv.DictReader(fh) if r["verdict"] == "english"]
    a.out.mkdir(parents=True, exist_ok=True)
    kept = 0
    with (a.out / "confidence.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["page", "mean_confidence", "words", "kept"])
        for pg in pages:
            got = read_page(a.pdf, pg)
            if got is None:
                w.writerow([pg, "", "", "no"])
                continue
            text, conf, words = got
            ok = conf >= a.min_confidence and words >= a.min_words
            w.writerow([pg, round(conf, 1), words, "yes" if ok else "no"])
            if ok:
                (a.out / f"p{pg:04d}.txt").write_text(text, encoding="utf-8")
                kept += 1
    print(f"{kept} of {len(pages)} pages the first read called English are confident English")
    return 0


if __name__ == "__main__":
    sys.exit(main())
