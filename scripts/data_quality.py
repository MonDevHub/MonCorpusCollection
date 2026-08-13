#!/usr/bin/env python3
"""Compute every number the README's Data Quality section and docs/CORPUS.md claim.

Before this script existed, each of those figures came from throwaway code that was
never committed, so a doc claim could drift from the data with nothing to catch it.
Every number printed here is the number that belongs in the docs; nothing in the docs
should be hand-adjusted afterwards.

    python3 scripts/data_quality.py                 # human-readable report
    python3 scripts/data_quality.py --json          # same numbers, machine-readable
    python3 scripts/data_quality.py --check         # exit 1 if a gate is violated

Gates (--check):
  - zero email-shaped strings in any shard
  - zero mobile-number-shaped strings in any shard
Both are the redaction invariant from AUDIT-2026-08-08 C2. They are gates rather than
observations because the audit found the corpus had no PII policy at all, and a policy
that is only a paragraph does not survive the next import.

Line counting matches scripts/shard_stats.py exactly: a "line" is a newline character,
so a file that does not end in one has its trailing fragment excluded from the count.
Both scripts must agree or the README contradicts itself.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

# The dedup key is build_shards.py's, not a reimplementation. A second copy would
# drift, and then the measured dedup rate would describe a key nothing else uses.
from build_shards import URL_RE, clean_document, skeleton_key

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")

# Mobile-number shapes, not "any long digit run". The corpus is full of ISBNs, DOIs,
# years and populations; a loose pattern reports hundreds of matches and is therefore
# useless as a gate. Anchored on the two dialling plans the sources actually use:
# Myanmar (09..., +959...) and Thailand (0[689]........), since the Facebook and
# Telegram material is from Mon communities in both countries.
PHONE_CANDIDATE_RE = re.compile(r"(?<![\d\w/.])[+]?\d[\d\s.\-()]{6,}\d(?![\d])")
BIBLIO_RE = re.compile(r"ISBN|ISSN|DOI|OCLC", re.I)
DECIMAL_RE = re.compile(r"\d\.\d")

# Myanmar numerals must be swept too, and this is the half a `\d` pattern silently
# misses: U+1040..U+1049 are not \d, so an ASCII-only scan reports a clean corpus while
# "ဂၞန်ဖုၚ် (၀၉-၄၉၈ ၂၇၀ ၉၇)" sits in it. Three of the 23 phone-shaped strings the
# redaction removed were written this way, in monnews_shard_001 only.
#
# Transliterate, then apply exactly the same shape test as ASCII. Requiring a nearby
# "phone" label was tried first and is both weaker and noisier: it missed nothing here
# but matched inside "Hubble Space Telescope", and dropping it costs nothing because
# is_mobile_shape over the whole corpus yields zero false positives in either numeral
# system -- Myanmar-numeral years and dates are far too short to reach nine digits.
MM_DIGITS = str.maketrans("၀၁၂၃၄၅၆၇၈၉", "0123456789")
MM_RUN_RE = re.compile(r"(?<![၀-၉])[၀-၉][၀-၉\s.\-()]{6,}[၀-၉](?![၀-၉])")


def is_mobile_shape(candidate: str) -> bool:
    """True for Myanmar/Thai mobile shapes only.

    Rejects decimals outright: `0.37271925 AU` in wikipedia_shard_001 strips to nine
    digits that would otherwise pass as a Thai landline.
    """
    if DECIMAL_RE.search(candidate):
        return False
    digits = re.sub(r"\D", "", candidate)
    if re.fullmatch(r"09\d{7,9}", digits):          # Myanmar mobile, national form
        return True
    if candidate.startswith("+") and re.fullmatch(r"959\d{7,9}", digits):
        # International form only. A bare 959... is not distinctive enough: the Zoom
        # meeting ID in wikipedia_shard_003 is ten digits beginning 59.
        return True
    # Thai mobile, then Thai landline. Kept as one expression so ruff's SIM103
    # does not fire on a trailing `if ...: return True` / `return False` pair.
    return bool(
        re.fullmatch(r"0[689]\d{8}", digits) or re.fullmatch(r"0[2-7]\d{7}", digits)
    )


def find_phones(line: str, prev_nonblank: str) -> tuple[list[str], list[str]]:
    """Mobile-shaped strings in `line` as (ascii_numerals, myanmar_numerals).

    The two forms are returned separately because they fail differently: an ASCII-only
    scan reports zero and looks clean, so the split is what makes the Myanmar-numeral
    coverage visible in the report rather than merely present in the code.

    `prev_nonblank` matters because the Wikipedia shards put the bare number on its own
    line with the literal word ISBN on the line above: nine of the corpus's remaining
    long digit runs are ISBN-10s in exactly that layout, and an ISBN-10 such as
    0-914868-21-7 strips to ten digits beginning 09.
    """
    if BIBLIO_RE.search(line) or BIBLIO_RE.fullmatch(prev_nonblank.strip()):
        return [], []
    ascii_hits = [m.group(0) for m in PHONE_CANDIDATE_RE.finditer(line)
                  if is_mobile_shape(m.group(0))]
    mm_hits = [m.group(0) for m in MM_RUN_RE.finditer(line)
               if is_mobile_shape(m.group(0).translate(MM_DIGITS))]
    return ascii_hits, mm_hits


def measure(shards_dir: Path) -> dict:
    per_shard: list[dict] = []
    totals = Counter()
    no_trailing_newline: list[str] = []

    # Dedup state, corpus-wide.
    #
    # Granularity is the cleaned non-blank LINE, not the sentence. build_shards.py
    # dedups per sentence when it imports, but the shards on disk are stored one
    # sentence per line, so the line is the unit a consumer actually sees and the unit
    # the README's figures describe. Measuring per sentence instead re-splits lines the
    # importer already split and reports a different population: 653,512 eligible
    # against the 369,898 this script prints, which is why the granularity is stated
    # rather than implied.
    key_counts: Counter[str] = Counter()
    key_shards: dict[str, set[str]] = defaultdict(set)
    key_length: dict[str, int] = {}
    redundant_chars = 0
    # Keys per shard, kept so the per-shard "shares a key with something else" column
    # can be computed once global counts are known. It is what backs the README's claim
    # that handwritten_shard_001 contributes no duplicates at all.
    shard_keys: dict[str, list[str]] = {}

    for path in sorted(shards_dir.glob("*_shard_*.txt")):
        text = path.read_text("utf-8")
        ends_newline = text.endswith("\n")
        if not ends_newline:
            no_trailing_newline.append(path.name)

        # lines[:-1] is exactly text.count("\n") entries, matching shard_stats.py
        split = text.split("\n")
        counted = split[:-1]
        lines = len(counted)
        blank = sum(1 for ln in counted if not ln.strip())

        urls = len(URL_RE.findall(text))

        emails = 0
        phones_ascii = 0
        phones_mm = 0
        prev_nonblank = ""
        for ln in counted:
            emails += len(EMAIL_RE.findall(ln))
            a, m = find_phones(ln, prev_nonblank)
            phones_ascii += len(a)
            phones_mm += len(m)
            if ln.strip():
                prev_nonblank = ln
        phones = phones_ascii + phones_mm

        # Lines with text but almost none of it. The README budgets usable lines, and a
        # 1-3 character line is a fragment rather than a training example.
        short_text = sum(1 for ln in counted if ln.strip() and len(ln.strip()) <= 3)

        eligible = 0
        keys_here: list[str] = []
        for line in clean_document(text).split("\n"):
            if not line.strip():
                continue
            key = skeleton_key(line)
            if key is None:      # skeleton under MIN_SKELETON Mon chars, never deduped
                continue
            eligible += 1
            keys_here.append(key)
            key_counts[key] += 1
            key_shards[key].add(path.name)
            if key in key_length:
                # Every instance after the first is what deduplication would drop, so
                # its own length is what deduplication would save. Summing the first
                # instance's length (count - 1) times instead is an estimate, and
                # differs here by 0.04%.
                redundant_chars += len(line)
            else:
                key_length[key] = len(line)

        shard_keys[path.name] = keys_here
        per_shard.append({
            "shard": path.name,
            "lines": lines,
            "blank_lines": blank,
            "short_text_lines": short_text,
            "blank_share_pct": round(100 * blank / lines, 1) if lines else 0.0,
            "urls": urls,
            "email_matches": emails,
            "phone_matches": phones,
            "phone_matches_ascii_numerals": phones_ascii,
            "phone_matches_myanmar_numerals": phones_mm,
            "dedup_eligible_lines": eligible,
            "ends_with_newline": ends_newline,
        })
        totals["lines"] += lines
        totals["blank_lines"] += blank
        totals["short_text_lines"] += short_text
        totals["urls"] += urls
        totals["email_matches"] += emails
        totals["phone_matches"] += phones
        totals["phone_matches_ascii_numerals"] += phones_ascii
        totals["phone_matches_myanmar_numerals"] += phones_mm
        totals["dedup_eligible_lines"] += eligible

    eligible = totals["dedup_eligible_lines"]
    unique = len(key_counts)
    redundant = eligible - unique
    repeated = [k for k, c in key_counts.items() if c > 1]
    dup_lengths = sorted(key_length[k] for k in repeated)
    cross_shard = sum(1 for k in repeated if len(key_shards[k]) > 1)

    # Attribute repetition back to each shard now that global counts are final.
    for s in per_shard:
        s["eligible_lines_sharing_a_key"] = sum(
            1 for k in shard_keys[s["shard"]] if key_counts[k] > 1)

    return {
        "shards": len(per_shard),
        "per_shard": per_shard,
        "lines": totals["lines"],
        "blank_lines": totals["blank_lines"],
        "blank_share_pct": round(100 * totals["blank_lines"] / totals["lines"], 1),
        "text_lines": totals["lines"] - totals["blank_lines"],
        "short_text_lines": totals["short_text_lines"],
        "urls": totals["urls"],
        "email_matches": totals["email_matches"],
        "phone_matches": totals["phone_matches"],
        "phone_matches_ascii_numerals": totals["phone_matches_ascii_numerals"],
        "phone_matches_myanmar_numerals": totals["phone_matches_myanmar_numerals"],
        "shards_without_trailing_newline": len(no_trailing_newline),
        "shards_without_trailing_newline_names": no_trailing_newline,
        "dedup": {
            "eligible_lines": eligible,
            "unique_skeletons": unique,
            "redundant_instances": redundant,
            "redundant_pct": round(100 * redundant / eligible, 1) if eligible else 0.0,
            "redundant_characters": redundant_chars,
            "repeated_skeletons": len(repeated),
            "cross_shard_skeletons": cross_shard,
            "repeated_median_chars": int(statistics.median(dup_lengths)) if dup_lengths else 0,
            "repeated_p90_chars": dup_lengths[int(0.9 * len(dup_lengths))] if dup_lengths else 0,
            "repeated_max_chars": max(dup_lengths) if dup_lengths else 0,
        },
    }


def report(m: dict) -> None:
    print(f"shards measured: {m['shards']}\n")

    # ph-A / ph-MM are split because an ASCII-only scan of this corpus reports zero
    # and looks clean while Myanmar-numeral contacts sit in monnews_shard_001.
    head = (f"{'shard':40} {'lines':>9} {'blank':>9} {'blank%':>7} {'urls':>6} "
            f"{'email':>6} {'ph-A':>5} {'ph-MM':>6} {'eol':>4}")
    print(head)
    print("-" * len(head))
    for s in m["per_shard"]:
        print(f"{s['shard']:40} {s['lines']:>9,} {s['blank_lines']:>9,} "
              f"{s['blank_share_pct']:>6.1f}% {s['urls']:>6,} {s['email_matches']:>6} "
              f"{s['phone_matches_ascii_numerals']:>5} "
              f"{s['phone_matches_myanmar_numerals']:>6} "
              f"{'Y' if s['ends_with_newline'] else 'n':>4}")
    print("-" * len(head))
    print(f"{'TOTAL':40} {m['lines']:>9,} {m['blank_lines']:>9,} "
          f"{m['blank_share_pct']:>6.1f}% {m['urls']:>6,} {m['email_matches']:>6} "
          f"{m['phone_matches_ascii_numerals']:>5} "
          f"{m['phone_matches_myanmar_numerals']:>6}")

    print(f"\nblank lines            {m['blank_lines']:,} of {m['lines']:,} "
          f"({m['blank_share_pct']}%), leaving {m['text_lines']:,} with text")
    print(f"  of those, <=3 chars  {m['short_text_lines']:,}")
    print(f"URLs remaining         {m['urls']:,}")
    print(f"email-shaped strings   {m['email_matches']}")
    print(f"phone-shaped strings   {m['phone_matches']} "
          f"({m['phone_matches_ascii_numerals']} ASCII numerals, "
          f"{m['phone_matches_myanmar_numerals']} Myanmar numerals)")
    print(f"shards not ending in a newline: {m['shards_without_trailing_newline']} "
          f"of {m['shards']}")

    d = m["dedup"]
    print("\ndedup, using build_shards.py's own skeleton key")
    print(f"  eligible lines       {d['eligible_lines']:,}")
    print(f"  unique skeletons     {d['unique_skeletons']:,}")
    print(f"  redundant instances  {d['redundant_instances']:,} ({d['redundant_pct']}%)")
    print(f"  redundant characters {d['redundant_characters']:,}")
    print(f"  skeletons repeating  {d['repeated_skeletons']:,}")
    print(f"  in >1 shard          {d['cross_shard_skeletons']:,}")
    print(f"  repeat length        median {d['repeated_median_chars']}, "
          f"p90 {d['repeated_p90_chars']}, max {d['repeated_max_chars']}")

    print("\nper-shard dedup contribution")
    print(f"  {'shard':40} {'eligible':>9} {'shares a key':>13}")
    for s in m["per_shard"]:
        print(f"  {s['shard']:40} {s['dedup_eligible_lines']:>9,} "
              f"{s['eligible_lines_sharing_a_key']:>13,}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("shards_dir", nargs="?", type=Path,
                        default=Path(__file__).resolve().parent.parent / "shards")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of a table.")
    parser.add_argument("--check", action="store_true",
                        help="Exit 1 if a PII gate is violated.")
    args = parser.parse_args()

    if not args.shards_dir.is_dir():
        print(f"Error: shards directory not found: {args.shards_dir}", file=sys.stderr)
        return 1

    m = measure(args.shards_dir)

    if args.json:
        print(json.dumps(m, ensure_ascii=False, indent=2))
    else:
        report(m)

    if args.check:
        failures = []
        if m["email_matches"]:
            failures.append(f"{m['email_matches']} email-shaped string(s) in shards/")
        if m["phone_matches"]:
            failures.append(f"{m['phone_matches']} mobile-shaped string(s) in shards/")
        if failures:
            print("\nFAIL", file=sys.stderr)
            for f in failures:
                print(f"  {f}", file=sys.stderr)
            print("  See docs/CORPUS.md section 6 for the redaction policy.", file=sys.stderr)
            return 1
        print("\nOK: no email-shaped or mobile-shaped strings in shards/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
