#!/usr/bin/env python3
"""Report how long monocr-cli took to read pages and lines, from its manifests.

    books_speed.py MANIFEST.jsonl [MANIFEST.jsonl ...]

Each manifest row is one page with its wall time `ms` and its recognised `lines`. A resumed run appends
duplicate rows, so the last row of a page wins. Prints one row per manifest and a total: pages, median and
mean seconds per page, lines per page, and mean seconds per line (page time divided by its lines, which
includes segmentation and page preparation, not only recognition). The time is wall-clock, so it depends on
how busy the machine was; say so beside any figure quoted from this.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path


def read_pages(path: Path) -> dict[int, tuple[float, int]]:
    """Page number -> (milliseconds, line count); the last row for a page wins."""
    pages: dict[int, tuple[float, int]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "page" in row and "ms" in row:
            pages[row["page"]] = (float(row["ms"]), len(row.get("lines", [])))
    return pages


def summarise(pages: dict[int, tuple[float, int]]) -> dict[str, float]:
    ms = [m for m, _ in pages.values()]
    lines = sum(n for _, n in pages.values())
    return {
        "pages": len(pages),
        "median_s_per_page": statistics.median(ms) / 1000,
        "mean_s_per_page": sum(ms) / len(ms) / 1000,
        "lines_per_page": lines / len(pages),
        "s_per_line": sum(ms) / 1000 / max(lines, 1),
    }


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    everything: dict[tuple[str, int], tuple[float, int]] = {}
    print("pages  median s/page  mean s/page  lines/page  s/line  manifest")
    for arg in argv:
        path = Path(arg)
        pages = read_pages(path)
        if not pages:
            continue
        s = summarise(pages)
        print(
            f"{s['pages']:5d}  {s['median_s_per_page']:13.1f}  {s['mean_s_per_page']:11.1f}  "
            f"{s['lines_per_page']:10.1f}  {s['s_per_line']:6.2f}  {path.parent.name}"
        )
        for page, value in pages.items():
            everything[(str(path), page)] = value
    if everything:
        s = summarise(dict(enumerate(everything.values())))
        print(
            f"{s['pages']:5d}  {s['median_s_per_page']:13.1f}  {s['mean_s_per_page']:11.1f}  "
            f"{s['lines_per_page']:10.1f}  {s['s_per_line']:6.2f}  all"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
