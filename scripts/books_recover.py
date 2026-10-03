#!/usr/bin/env python3
"""Second read for the pages the first read could not use.

A page often fails because of its background, not its text: a tinted panel, a printed frame, a title
banner over a photograph. The line finder then returns the header and the page number and nothing else.
This flattens the background and crops to the text block, then reads the page again.

    books_recover.py BOOK.pdf REPORT.csv --workdir DIR --cli PATH_TO_monocr-cli
                     [--verdicts empty garbled symbols]

REPORT.csv is the page report written by books_filter.py. Only pages with one of the listed verdicts
are prepared. DIR/prep holds the prepared images and DIR/out the second read, whose manifest is passed
back to books_filter.py with --recovered. Needs pdftoppm, ImageMagick (magick) and monocr-cli.

The crop (80% x 72% of the page, centred, nudged up 1%) removes the frame, banner and page number, and so
also any text printed in those margins. It is for pages that failed, never for pages that read.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
from pathlib import Path

FLATTEN = ["(", "+clone", "-blur", "0x30", ")", "-compose", "Divide_Src", "-composite",
           "-normalize", "-level", "55%,100%"]
CROP = ["-gravity", "center", "-crop", "80%x72%+0-1%", "+repage"]


def prepare(pdf: Path, page: int, target: Path) -> bool:
    stem = target.with_suffix("")
    render = subprocess.run(
        ["pdftoppm", "-r", "300", "-gray", "-f", str(page), "-l", str(page), "-png", "-singlefile", str(pdf), str(stem)],
        capture_output=True,
    )
    if render.returncode != 0 or not target.is_file():
        return False
    flat = subprocess.run(["magick", str(target), *FLATTEN, *CROP, str(target)], capture_output=True)
    return flat.returncode == 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("pdf", type=Path)
    p.add_argument("report", type=Path)
    p.add_argument("--workdir", type=Path, required=True)
    p.add_argument("--cli", type=Path, required=True)
    p.add_argument("--verdicts", nargs="+", default=["empty", "garbled", "symbols"])
    a = p.parse_args()
    with a.report.open(encoding="utf-8", newline="") as fh:
        pages = [int(r["page"]) for r in csv.DictReader(fh) if r["verdict"] in a.verdicts]
    if not pages:
        print("no pages to recover")
        return 0
    prep = a.workdir / "prep"
    prep.mkdir(parents=True, exist_ok=True)
    made = [pg for pg in pages if prepare(a.pdf, pg, prep / f"p{pg:04d}.png")]
    print(f"prepared {len(made)} of {len(pages)} pages")
    if not made:
        return 1
    out = a.workdir / "out"
    result = subprocess.run([str(a.cli), "extract", str(prep), "-o", str(out), "--mode", "page", "--resume"], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr.strip()[-400:], file=sys.stderr)
        return 1
    print(f"second read written to {out}/manifest.jsonl")
    return 0


if __name__ == "__main__":
    sys.exit(main())
