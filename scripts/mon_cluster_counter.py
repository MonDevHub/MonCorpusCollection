#!/usr/bin/env python3
"""
mon_cluster_counter.py

Recursively scans corpus files and counts Mon/Myanmar script clusters.

This script:
- reads files recursively
- optionally normalizes င -> ၚ
- optionally removes Mon/Myanmar half stop and full stop (၊ and ။)
- segments text into orthographic clusters
- counts clusters, cluster bigrams, and cluster trigrams
- writes CSV and JSON summaries

This is more appropriate than whitespace word counting for Mon,
because Mon text often does not mark word boundaries with spaces.

Example usage:
    python3 mon_cluster_counter.py . --output-dir cluster_results
    python3 mon_cluster_counter.py . --output-dir cluster_results_norm --normalize-mon-nga
    python3 mon_cluster_counter.py . --output-dir cluster_results_no_stops --remove-mon-stops
    python3 mon_cluster_counter.py . --output-dir cluster_results_clean --normalize-mon-nga --remove-mon-stops

Preset usage:
    python3 mon_cluster_counter.py . --preset raw
    python3 mon_cluster_counter.py . --preset norm
    python3 mon_cluster_counter.py . --preset no-stops
    python3 mon_cluster_counter.py . --preset clean
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


# ---------------------------------
# Unicode helpers
# ---------------------------------

def is_myanmar_related(char: str) -> bool:
    code = ord(char)
    return (
        0x1000 <= code <= 0x109F
        or 0xAA60 <= code <= 0xAA7F
        or 0xA9E0 <= code <= 0xA9FF
    )


def normalize_text(text: str, form: str = "NFC") -> str:
    return unicodedata.normalize(form, text)


def apply_mon_normalization(
    text: str,
    normalize_mon_nga: bool = False,
    remove_mon_stops: bool = False,
) -> tuple[str, dict[str, int]]:
    stats = {
        "nga_to_mon_nga": 0,
        "mon_half_stop_removed": 0,
        "mon_full_stop_removed": 0,
    }

    if normalize_mon_nga:
        count = text.count("င")
        if count:
            text = text.replace("င", "ၚ")
            stats["nga_to_mon_nga"] = count

    if remove_mon_stops:
        half_stop_count = text.count("၊")
        full_stop_count = text.count("။")

        if half_stop_count:
            text = text.replace("၊", "")
            stats["mon_half_stop_removed"] = half_stop_count

        if full_stop_count:
            text = text.replace("။", "")
            stats["mon_full_stop_removed"] = full_stop_count

    return text, stats


# ---------------------------------
# File reading
# ---------------------------------

def try_read_text_file(path: Path) -> str | None:
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


def iter_input_files(root: Path, extensions: set[str], skip_dirs: set[str]) -> Iterable[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue

        if any(part in skip_dirs for part in path.parts):
            continue

        if extensions and path.suffix.lower() not in extensions:
            continue

        yield path


# ---------------------------------
# Cluster segmentation
# ---------------------------------

# Characters that can begin a cluster.
# This is intentionally broad for Myanmar/Mon-related text.
def is_cluster_base(char: str) -> bool:
    code = ord(char)

    # Main Myanmar letters and extensions that can behave like bases
    base_ranges = [
        (0x1000, 0x102A),
        (0x103F, 0x103F),
        (0x104C, 0x104F),
        (0x1050, 0x109F),
        (0xAA60, 0xAA7F),
        (0xA9E0, 0xA9FF),
    ]

    for start, end in base_ranges:
        if start <= code <= end:
            return True

    return False


# Characters that usually continue the current cluster.
def is_cluster_mark(char: str) -> bool:
    code = ord(char)

    mark_ranges = [
        (0x102B, 0x103E),  # vowels, medials, virama, asat, tones
        (0x105E, 0x1060),  # Mon medials
    ]

    for start, end in mark_ranges:
        if start <= code <= end:
            return True

    return False


def extract_myanmar_runs(text: str) -> list[str]:
    """
    Split text into contiguous Myanmar-related runs.
    Non-Myanmar text is discarded.
    """
    runs: list[str] = []
    current: list[str] = []

    for ch in text:
        if is_myanmar_related(ch):
            current.append(ch)
        else:
            if current:
                runs.append("".join(current))
                current = []

    if current:
        runs.append("".join(current))

    return runs


def segment_run_into_clusters(run: str) -> list[str]:
    """
    Segment one contiguous Myanmar-script run into clusters.

    Heuristic rules:
    - Start a new cluster at a base character
    - Attach following marks to the same cluster
    - If virama U+1039 appears, attach it and the following base to the same cluster
    - Keep subsequent marks attached as well

    This is not perfect linguistic segmentation, but it is a very useful
    orthographic cluster approximation for Mon/Myanmar text.
    """
    clusters: list[str] = []
    i = 0
    n = len(run)

    while i < n:
        ch = run[i]

        # If text starts with a mark unexpectedly, treat it as its own cluster starter.
        cluster = [ch]
        i += 1

        # If current char is a base, absorb marks and virama-linked bases.
        if is_cluster_base(ch):
            while i < n:
                nxt = run[i]

                if is_cluster_mark(nxt):
                    cluster.append(nxt)
                    i += 1

                    # If virama, attach following base and its marks too.
                    if ord(nxt) == 0x1039 and i < n:
                        cluster.append(run[i])
                        i += 1

                        while i < n and is_cluster_mark(run[i]):
                            cluster.append(run[i])
                            i += 1
                    continue

                # New base starts next cluster
                if is_cluster_base(nxt):
                    break

                # Fallback: attach unexpected Myanmar char to current cluster
                cluster.append(nxt)
                i += 1

        else:
            # If not a base, still absorb subsequent marks to avoid fragmentation.
            while i < n and is_cluster_mark(run[i]):
                cluster.append(run[i])
                i += 1

        clusters.append("".join(cluster))

    return clusters


def extract_clusters(text: str) -> list[str]:
    clusters: list[str] = []
    runs = extract_myanmar_runs(text)

    for run in runs:
        clusters.extend(segment_run_into_clusters(run))

    return clusters


# ---------------------------------
# N-gram helpers
# ---------------------------------

def update_ngram_counter(counter: Counter[str], items: list[str], n: int) -> None:
    if len(items) < n:
        return

    for i in range(len(items) - n + 1):
        gram = " ".join(items[i:i + n])
        counter[gram] += 1


# ---------------------------------
# CSV output
# ---------------------------------

def write_counter_csv(output_path: Path, counter: Counter[str], label_name: str) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([label_name, "count"])

        for item, count in counter.most_common():
            writer.writerow([item, count])


def write_file_stats_csv(output_path: Path, file_rows: list[dict[str, object]]) -> None:
    fieldnames = [
        "file",
        "cluster_count",
        "raw_text_length",
        "nga_to_mon_nga_replacements",
        "mon_half_stop_removed",
        "mon_full_stop_removed",
        "status",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(file_rows)


# ---------------------------------
# Main analysis
# ---------------------------------

def analyze_corpus(
    input_root: Path,
    output_dir: Path,
    extensions: set[str],
    skip_dirs: set[str],
    normalization_form: str,
    normalize_mon_nga: bool,
    remove_mon_stops: bool,
) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)

    cluster_counter: Counter[str] = Counter()
    cluster_bigram_counter: Counter[str] = Counter()
    cluster_trigram_counter: Counter[str] = Counter()

    file_rows: list[dict[str, object]] = []

    totals = {
        "files_seen": 0,
        "files_read_successfully": 0,
        "files_failed": 0,
        "total_clusters": 0,
        "total_raw_text_length": 0,
        "total_nga_to_mon_nga_replacements": 0,
        "total_mon_half_stop_removed": 0,
        "total_mon_full_stop_removed": 0,
    }

    for path in iter_input_files(input_root, extensions, skip_dirs):
        totals["files_seen"] += 1

        text = try_read_text_file(path)
        if text is None:
            totals["files_failed"] += 1
            file_rows.append({
                "file": str(path),
                "cluster_count": 0,
                "raw_text_length": 0,
                "nga_to_mon_nga_replacements": 0,
                "mon_half_stop_removed": 0,
                "mon_full_stop_removed": 0,
                "status": "read_failed",
            })
            continue

        raw_length = len(text)
        text = normalize_text(text, normalization_form)
        text, replacement_stats = apply_mon_normalization(
            text,
            normalize_mon_nga=normalize_mon_nga,
            remove_mon_stops=remove_mon_stops,
        )

        clusters = extract_clusters(text)

        cluster_counter.update(clusters)
        update_ngram_counter(cluster_bigram_counter, clusters, 2)
        update_ngram_counter(cluster_trigram_counter, clusters, 3)

        cluster_count = len(clusters)
        nga_replacements = replacement_stats["nga_to_mon_nga"]
        half_stop_removed = replacement_stats["mon_half_stop_removed"]
        full_stop_removed = replacement_stats["mon_full_stop_removed"]

        totals["files_read_successfully"] += 1
        totals["total_clusters"] += cluster_count
        totals["total_raw_text_length"] += raw_length
        totals["total_nga_to_mon_nga_replacements"] += nga_replacements
        totals["total_mon_half_stop_removed"] += half_stop_removed
        totals["total_mon_full_stop_removed"] += full_stop_removed

        file_rows.append({
            "file": str(path),
            "cluster_count": cluster_count,
            "raw_text_length": raw_length,
            "nga_to_mon_nga_replacements": nga_replacements,
            "mon_half_stop_removed": half_stop_removed,
            "mon_full_stop_removed": full_stop_removed,
            "status": "ok",
        })

    write_counter_csv(output_dir / "cluster_frequency.csv", cluster_counter, "cluster")
    write_counter_csv(
        output_dir / "cluster_bigram_frequency.csv",
        cluster_bigram_counter,
        "cluster_bigram",
    )
    write_counter_csv(
        output_dir / "cluster_trigram_frequency.csv",
        cluster_trigram_counter,
        "cluster_trigram",
    )
    write_file_stats_csv(output_dir / "file_stats.csv", file_rows)

    summary = {
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "extensions": sorted(extensions),
        "skip_dirs": sorted(skip_dirs),
        "normalization_form": normalization_form,
        "normalize_mon_nga": normalize_mon_nga,
        "remove_mon_stops": remove_mon_stops,
        "totals": totals,
        "top_50_clusters": cluster_counter.most_common(50),
        "top_50_cluster_bigrams": cluster_bigram_counter.most_common(50),
        "top_50_cluster_trigrams": cluster_trigram_counter.most_common(50),
    }

    with (output_dir / "summary.json").open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    print("Cluster analysis complete.")
    print(f"Files seen:                         {totals['files_seen']}")
    print(f"Files read successfully:           {totals['files_read_successfully']}")
    print(f"Files failed:                      {totals['files_failed']}")
    print(f"Total clusters:                    {totals['total_clusters']}")
    print(f"Raw text length:                   {totals['total_raw_text_length']}")
    print(f"င -> ၚ replacements applied:       {totals['total_nga_to_mon_nga_replacements']}")
    print(f"Mon half stops removed (၊):        {totals['total_mon_half_stop_removed']}")
    print(f"Mon full stops removed (။):        {totals['total_mon_full_stop_removed']}")
    print(f"Results written to:                {output_dir}")

    return 0


# ---------------------------------
# CLI
# ---------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Count Mon/Myanmar orthographic clusters recursively."
    )

    parser.add_argument(
        "input_path",
        type=Path,
        help="Root folder containing corpus files.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("cluster_results"),
        help="Directory where results will be written.",
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
        default=["results", "results_raw", "results_mon_normalized", "__pycache__", ".git"],
        help="Directory names to skip during recursive scanning.",
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

    parser.add_argument(
        "--remove-mon-stops",
        action="store_true",
        help="Remove Mon/Myanmar half stop (၊) and full stop (။) before counting.",
    )

    parser.add_argument(
        "--preset",
        choices=["raw", "norm", "no-stops", "clean"],
        help="Use a predefined configuration: raw, norm, no-stops, or clean.",
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

    normalize_mon_nga = args.normalize_mon_nga
    remove_mon_stops = args.remove_mon_stops
    output_dir = args.output_dir

    if args.preset:
        if args.preset == "raw":
            if output_dir == Path("cluster_results"):
                output_dir = Path("cluster_results_raw")
        elif args.preset == "norm":
            normalize_mon_nga = True
            if output_dir == Path("cluster_results"):
                output_dir = Path("cluster_results_norm")
        elif args.preset == "no-stops":
            remove_mon_stops = True
            if output_dir == Path("cluster_results"):
                output_dir = Path("cluster_results_no_stops")
        elif args.preset == "clean":
            normalize_mon_nga = True
            remove_mon_stops = True
            if output_dir == Path("cluster_results"):
                output_dir = Path("cluster_results_clean")

    return analyze_corpus(
        input_root=input_root,
        output_dir=output_dir,
        extensions=extensions,
        skip_dirs=skip_dirs,
        normalization_form=args.normalization,
        normalize_mon_nga=normalize_mon_nga,
        remove_mon_stops=remove_mon_stops,
    )


if __name__ == "__main__":
    raise SystemExit(main())
