#!/usr/bin/env python3
"""
corpus_counter_normalized.py

Recursively scans folders/files, reads text corpora, and tallies:
- raw Unicode code point frequencies
- bigram frequencies
- trigram frequencies
- per-file statistics

This version also supports optional Mon-oriented normalization:
    င -> ၚ

Important:
- This script counts underlying Unicode code points, not visual glyphs.
- The normalization is optional and should be treated as an analysis choice,
  not as irreversible source modification.

Examples:
    python3 corpus_counter_normalized.py . --output-dir results_raw
    python3 corpus_counter_normalized.py . --output-dir results_mon_norm --normalize-mon-nga
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Iterable


# -----------------------------
# Unicode filtering
# -----------------------------

def is_myanmar_related(char: str) -> bool:
    """
    Return True if the character is in a Myanmar-related Unicode block.
    Includes:
    - U+1000–U+109F  Myanmar
    - U+AA60–U+AA7F  Myanmar Extended-A
    - U+A9E0–U+A9FF  Myanmar Extended-B
    """
    code = ord(char)
    return (
        0x1000 <= code <= 0x109F
        or 0xAA60 <= code <= 0xAA7F
        or 0xA9E0 <= code <= 0xA9FF
    )


def normalize_text(text: str, form: str = "NFC") -> str:
    """
    Apply Unicode normalization.
    """
    return unicodedata.normalize(form, text)


def apply_mon_normalization(
    text: str,
    normalize_mon_nga: bool = False,
) -> tuple[str, dict[str, int]]:
    """
    Apply optional Mon-specific normalization rules.

    Currently supported:
    - င -> ၚ

    Returns:
        normalized_text, replacement_stats
    """
    replacement_stats: dict[str, int] = {
        "nga_to_mon_nga": 0,
    }

    if normalize_mon_nga:
        count = text.count("င")
        if count:
            text = text.replace("င", "ၚ")
            replacement_stats["nga_to_mon_nga"] = count

    return text, replacement_stats


# -----------------------------
# File reading
# -----------------------------

def try_read_text_file(path: Path) -> str | None:
    """
    Try reading a file using several common encodings.
    Returns text or None if all attempts fail.
    """
    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
    ]

    for encoding in encodings_to_try:
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
        except OSError:
            return None

    return None


# -----------------------------
# Counting helpers
# -----------------------------

def filtered_characters(text: str, count_all_chars: bool = False) -> list[str]:
    """
    Return the characters that should be counted.

    If count_all_chars is False:
        count only Myanmar-related Unicode characters.
    If True:
        count every non-whitespace character.
    """
    chars: list[str] = []

    for char in text:
        if count_all_chars:
            if not char.isspace():
                chars.append(char)
        else:
            if is_myanmar_related(char):
                chars.append(char)

    return chars


def update_ngram_counter(counter: Counter[str], chars: list[str], n: int) -> None:
    """
    Update an n-gram counter from a list of characters.
    """
    if len(chars) < n:
        return

    for index in range(len(chars) - n + 1):
        gram = "".join(chars[index:index + n])
        counter[gram] += 1


# -----------------------------
# CSV writing
# -----------------------------

def write_counter_csv(
    output_path: Path,
    counter: Counter[str],
    label_name: str,
) -> None:
    """
    Write a counter to CSV with Unicode metadata.
    """
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([label_name, "count", "codepoints", "unicode_names"])

        for item, count in counter.most_common():
            codepoints = " ".join(f"U+{ord(ch):04X}" for ch in item)
            unicode_names = " | ".join(
                unicodedata.name(ch, "<UNKNOWN>")
                for ch in item
            )
            writer.writerow([item, count, codepoints, unicode_names])


def write_file_stats_csv(output_path: Path, file_rows: list[dict[str, object]]) -> None:
    """
    Write per-file statistics.
    """
    fieldnames = [
        "file",
        "characters_counted",
        "all_text_length",
        "nga_to_mon_nga_replacements",
        "status",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(file_rows)


# -----------------------------
# File discovery
# -----------------------------

def iter_input_files(root: Path, extensions: set[str], skip_dirs: set[str]) -> Iterable[Path]:
    """
    Yield matching files recursively, skipping directories by name.
    """
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in skip_dirs for part in path.parts):
            continue

        if extensions and path.suffix.lower() not in extensions:
            continue

        yield path


# -----------------------------
# Main analysis
# -----------------------------

def analyze_corpus(
    input_root: Path,
    output_dir: Path,
    extensions: set[str],
    skip_dirs: set[str],
    count_all_chars: bool,
    normalization_form: str,
    normalize_mon_nga: bool,
) -> int:
    """
    Analyze corpus files and write result files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    char_counter: Counter[str] = Counter()
    bigram_counter: Counter[str] = Counter()
    trigram_counter: Counter[str] = Counter()

    file_rows: list[dict[str, object]] = []

    totals = {
        "files_seen": 0,
        "files_read_successfully": 0,
        "files_failed": 0,
        "total_counted_characters": 0,
        "total_raw_text_length": 0,
        "total_nga_to_mon_nga_replacements": 0,
    }

    for path in iter_input_files(input_root, extensions, skip_dirs):
        totals["files_seen"] += 1

        text = try_read_text_file(path)
        if text is None:
            totals["files_failed"] += 1
            file_rows.append({
                "file": str(path),
                "characters_counted": 0,
                "all_text_length": 0,
                "nga_to_mon_nga_replacements": 0,
                "status": "read_failed",
            })
            continue

        raw_length = len(text)
        text = normalize_text(text, normalization_form)
        text, replacement_stats = apply_mon_normalization(
            text,
            normalize_mon_nga=normalize_mon_nga,
        )

        chars = filtered_characters(text, count_all_chars=count_all_chars)

        char_counter.update(chars)
        update_ngram_counter(bigram_counter, chars, 2)
        update_ngram_counter(trigram_counter, chars, 3)

        counted = len(chars)
        nga_replacements = replacement_stats["nga_to_mon_nga"]

        totals["files_read_successfully"] += 1
        totals["total_counted_characters"] += counted
        totals["total_raw_text_length"] += raw_length
        totals["total_nga_to_mon_nga_replacements"] += nga_replacements

        file_rows.append({
            "file": str(path),
            "characters_counted": counted,
            "all_text_length": raw_length,
            "nga_to_mon_nga_replacements": nga_replacements,
            "status": "ok",
        })

    write_counter_csv(output_dir / "character_frequency.csv", char_counter, "character")
    write_counter_csv(output_dir / "bigram_frequency.csv", bigram_counter, "bigram")
    write_counter_csv(output_dir / "trigram_frequency.csv", trigram_counter, "trigram")
    write_file_stats_csv(output_dir / "file_stats.csv", file_rows)

    summary = {
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "extensions": sorted(extensions),
        "skip_dirs": sorted(skip_dirs),
        "count_all_chars": count_all_chars,
        "normalization_form": normalization_form,
        "normalize_mon_nga": normalize_mon_nga,
        "totals": totals,
        "top_50_characters": char_counter.most_common(50),
        "top_50_bigrams": bigram_counter.most_common(50),
        "top_50_trigrams": trigram_counter.most_common(50),
    }

    with (output_dir / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("Analysis complete.")
    print(f"Files seen:                         {totals['files_seen']}")
    print(f"Files read successfully:           {totals['files_read_successfully']}")
    print(f"Files failed:                      {totals['files_failed']}")
    print(f"Counted characters:                {totals['total_counted_characters']}")
    print(f"Raw text length:                   {totals['total_raw_text_length']}")
    print(f"င -> ၚ replacements applied:       {totals['total_nga_to_mon_nga_replacements']}")
    print(f"Results written to:                {output_dir}")

    return 0


# -----------------------------
# CLI
# -----------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Mon/Myanmar corpus files recursively, with optional Mon normalization."
    )

    parser.add_argument(
        "input_path",
        type=Path,
        help="Root folder containing corpus files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("corpus_results"),
        help="Directory where CSV/JSON results will be written.",
    )

    parser.add_argument(
        "--extensions",
        nargs="*",
        default=[".txt"],
        help="File extensions to include, e.g. .txt .md .json",
    )

    parser.add_argument(
        "--skip-dirs",
        nargs="*",
        default=["results", "__pycache__", ".git"],
        help="Directory names to skip during recursive scanning.",
    )

    parser.add_argument(
        "--all-chars",
        action="store_true",
        help="Count all non-whitespace characters instead of only Myanmar-related Unicode.",
    )

    parser.add_argument(
        "--normalization",
        default="NFC",
        choices=["NFC", "NFD", "NFKC", "NFKD"],
        help="Unicode normalization form to apply before counting.",
    )

    parser.add_argument(
        "--normalize-mon-nga",
        action="store_true",
        help="Replace င with ၚ before counting.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_root = args.input_path
    if not input_root.exists():
        print(f"Error: input path does not exist: {input_root}", file=sys.stderr)
        return 1

    extensions = {
        ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        for ext in args.extensions
    }

    skip_dirs = set(args.skip_dirs)

    return analyze_corpus(
        input_root=input_root,
        output_dir=args.output_dir,
        extensions=extensions,
        skip_dirs=skip_dirs,
        count_all_chars=args.all_chars,
        normalization_form=args.normalization,
        normalize_mon_nga=args.normalize_mon_nga,
    )


if __name__ == "__main__":
    raise SystemExit(main())
