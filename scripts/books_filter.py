#!/usr/bin/env python3
"""Turn a monocr-cli manifest into a book text, keeping the pages that read and dropping the rest.

The policy is the owner's (2026-10-02): recover what can be recovered and drop what cannot, cleanly,
without asking about each page. Dropped pages are listed with the reason, so a drop is auditable.

    books_filter.py MANIFEST.jsonl --out book.txt --report pages.csv [--top 110] [--bottom 3150]
                    [--head-band 280 340]

Lines are removed by their position on the page (the web viewer's header and footer, a running head),
not by their text, because the OCR misreads those differently on every page. A page is dropped when:

  empty        fewer than --min-chars characters survive
  symbols      symbols a Mon or Burmese page seldom prints are more than --max-symbols of the page
               (the signature of a table, a photograph or a decorative title read as text)
  mixed        more than --max-mixed of its lines mix Myanmar and Latin script (an English page read
               by a Mon model comes out as this)
  digits       Myanmar digits are more than --max-digits of the page (a contents or index table)
  english      Latin letters are at least --max-latin of the page. The model reads English badly
               (run-together words, Myanmar glyphs mixed in), so these pages are set aside for a
               later read with an English OCR, not kept as they are
  garbled      malformed character stacking is more than --max-garble per 100 Myanmar characters
               (a virama not followed by a consonant, or doubled): what a Mon model returns for a
               table or a photograph

The thresholds were set on the Nai Tun Thein dictionary (374 good pages, 6 known-bad) and on eight trial
pages from two other books; `--selftest` pins the page shapes. The garble cutoff rests on little data
(good pages stayed under 2.6, bad ones were 3.6 or more), so treat it as a starting point.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from pathlib import Path

SYMBOLS = set("`'\"•*^_~|´°¦¬§©«»")
MYANMAR_DIGITS = set("၀၁၂၃၄၅၆၇၈၉")
VIRAMA = "\u1039"
CONSONANTS = {chr(c) for c in range(0x1000, 0x1022)} | {"\u103f", "\u1050", "\u1051"}


def is_myanmar(c: str) -> bool:
    cp = ord(c)
    return 0x1000 <= cp <= 0x109F or 0xA9E0 <= cp <= 0xA9FF or 0xAA60 <= cp <= 0xAA7F


def is_latin(c: str) -> bool:
    return c.isascii() and c.isalpha()


def garble_rate(text: str) -> float:
    """Malformed virama uses per 100 Myanmar characters."""
    myanmar = sum(map(is_myanmar, text))
    bad = 0
    for i, c in enumerate(text):
        if c == VIRAMA:
            nxt = text[i + 1] if i + 1 < len(text) else ""
            prv = text[i - 1] if i else ""
            if nxt not in CONSONANTS or prv in (VIRAMA, "\n", " ", ""):
                bad += 1
    return 100 * bad / myanmar if myanmar else 0.0


def measure(lines: list[str]) -> dict[str, float]:
    kept = [x for x in lines if x.strip()]
    chars = [c for x in kept for c in x if not c.isspace()]
    if not chars:
        return {"chars": 0, "symbols": 0.0, "mixed": 0.0, "digits": 0.0, "latin": 0.0, "garble": 0.0, "lines": 0}
    mixed = 0
    for x in kept:
        cs = [c for c in x if not c.isspace()]
        if cs and sum(map(is_myanmar, cs)) / len(cs) >= 0.2 and sum(map(is_latin, cs)) / len(cs) >= 0.2:
            mixed += 1
    return {
        "chars": len(chars),
        "symbols": sum(c in SYMBOLS for c in chars) / len(chars),
        "mixed": mixed / len(kept),
        "digits": sum(c in MYANMAR_DIGITS for c in chars) / len(chars),
        "latin": sum(map(is_latin, chars)) / len(chars),
        "garble": garble_rate("\n".join(kept)),
        "lines": len(kept),
    }


def verdict(m: dict[str, float], a: argparse.Namespace) -> str:
    if m["chars"] < a.min_chars:
        return "empty"
    if m["latin"] >= a.max_latin:
        return "english"
    if m["symbols"] > a.max_symbols:
        return "symbols"
    if m["mixed"] > a.max_mixed:
        return "mixed"
    if m["digits"] > a.max_digits:
        return "digits"
    if m["garble"] > a.max_garble:
        return "garbled"
    return "keep"


def page_lines(row: dict, a: argparse.Namespace) -> list[str]:
    out = []
    for line in row["lines"]:
        y = line["y"]
        if y < a.top or y > a.bottom or a.head_band[0] <= y <= a.head_band[1]:
            continue
        if line["text"].strip():
            out.append(line["text"].strip())
    return out


def run(manifest: Path, a: argparse.Namespace) -> tuple[str, list[dict]]:
    blocks, report = [], []
    # A resumed run appends the pages it re-reads, so a page can appear twice: the last row wins.
    rows = {}
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        row = json.loads(raw)
        rows[row["page"]] = row
    for row in (rows[k] for k in sorted(rows)):
        lines = page_lines(row, a)
        m = measure(lines)
        v = verdict(m, a)
        report.append({"page": row["page"], "verdict": v, **{k: round(m[k], 4) for k in m}})
        if v == "keep":
            blocks.append(f"[page {row['page']}]\n" + "\n".join(lines))
    text = unicodedata.normalize("NFC", "\n\n".join(blocks) + "\n") if blocks else ""
    return text, report


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("manifest", nargs="?", type=Path)
    p.add_argument("--out", type=Path)
    p.add_argument("--report", type=Path)
    p.add_argument("--top", type=int, default=110, help="drop lines above this y (web-viewer header)")
    p.add_argument("--bottom", type=int, default=3150, help="drop lines below this y (footer)")
    p.add_argument("--head-band", type=int, nargs=2, default=(280, 340), metavar=("Y0", "Y1"))
    p.add_argument("--min-chars", type=int, default=100)
    p.add_argument("--max-symbols", type=float, default=0.05)
    p.add_argument("--max-mixed", type=float, default=0.4)
    p.add_argument("--max-digits", type=float, default=0.3)
    p.add_argument("--max-latin", type=float, default=0.5)
    p.add_argument("--max-garble", type=float, default=3.0)
    p.add_argument("--selftest", action="store_true")
    return p


def main() -> int:
    a = parser().parse_args()
    if a.selftest:
        return selftest(a)
    if not a.manifest or not a.out:
        print("manifest and --out are required", file=sys.stderr)
        return 2
    text, report = run(a.manifest, a)
    a.out.write_text(text, encoding="utf-8")
    if a.report:
        with a.report.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(report[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(report)
    kept = sum(r["verdict"] == "keep" for r in report)
    reasons: dict[str, int] = {}
    for r in report:
        if r["verdict"] != "keep":
            reasons[r["verdict"]] = reasons.get(r["verdict"], 0) + 1
    print(f"{kept} of {len(report)} pages kept; dropped: {reasons or 'none'}")
    return 0


def selftest(a: argparse.Namespace) -> int:
    """Each case is a page shape the filter must get right, with the reason it must."""
    good = ["ထမတ် (န) ဆွမ်းတော်တင်သောဆွမ်း။ ပင်... = ဆွမ်းတော်ထမင်း။"] * 8
    table = [".  : , - ,”   ,  , ` . . .-..၁-  *", ".-.‘..‘‘•..", "ၚ,“,•..;,“•.:,`•,.°,`.,၁၉"] * 3
    english = ["How to build the Kanad dancing and the original of Kanadancing ၇၉"] * 8
    garbled = ["ဒ္္ိပ္ၟဒိန္ိ ၚ္ံၚ္တၚ် န္္်္ဒ္် ္ၚ", "အကဍိုးံ့အဖဨြစပြုသည်။ ၚ်္ၚဵ ္ၚ"] * 4
    contents = ["၉၂၀၉၂၁၄", "န်၂၁၄၂၃၁၉", "၀၂၁၉၂၄၈", "၂၄၉-၂၅၆"] * 6
    cases = {"good": (good, "keep"), "table": (table, "symbols"), "english": (english, "english"),
             "contents": (contents, "digits"), "blank": ([], "empty"), "garbled": (garbled, "garbled")}
    failed = [n for n, (ls, want) in cases.items() if verdict(measure(ls), a) != want]
    for n in failed:
        print(f"selftest FAIL: {n}")
    print(f"selftest: {len(cases)} case(s), {len(failed)} failure(s)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
