#!/usr/bin/env python3
"""Per-source corpus statistics for shards/, matching the README Dataset table:
shards, lines, characters (non-whitespace), Mon/Myanmar (Myanmar-block), Other.

    python3 scripts/shard_stats.py            # uses ../shards
    python3 scripts/shard_stats.py path/to/shards
"""
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

MON_RE = re.compile(r"[က-႟ꩠ-ꩿꧠ-꧿]")
NAME_RE = re.compile(r"(?P<source>.+)_shard_\d{3}\.txt$")


def main() -> int:
    shards_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "shards"
    agg: dict[str, dict[str, int]] = defaultdict(lambda: {"shards": 0, "lines": 0, "chars": 0, "mon": 0})
    malformed: list[str] = []
    for path in sorted(shards_dir.glob("*_shard_*.txt")):
        m = NAME_RE.match(path.name)
        if not m:
            # The glob is looser than NAME_RE, so this is reachable: `foo_shard_1.txt`
            # and `foo_shard_0001.txt` both glob but neither matches `\d{3}`. The old
            # code fell back to path.stem, which silently invented a source row named
            # after the file and put it in the README's Dataset table as if it were a
            # real source. Refuse instead — this script's output is the table, and a
            # wrong table is worse than a failed run. build_shards.py always writes
            # %03d, so hitting this means a file was added by hand.
            malformed.append(path.name)
            continue
        source = m.group("source")
        text = unicodedata.normalize("NFC", path.read_text("utf-8"))
        a = agg[source]
        a["shards"] += 1
        a["lines"] += text.count("\n")
        a["chars"] += sum(1 for ch in text if not ch.isspace())
        a["mon"] += len(MON_RE.findall(text))

    if malformed:
        print("Error: shard filenames do not match "
              "<source>_shard_<three digits>.txt, so their source cannot be "
              "determined and they are not counted:", file=sys.stderr)
        for name in malformed:
            print(f"  {name}", file=sys.stderr)
        return 1

    header = f"{'source':24} {'shards':>6} {'lines':>12} {'chars':>14} {'mon':>14} {'other':>12}"
    print(header)
    print("-" * len(header))
    total = {"shards": 0, "lines": 0, "chars": 0, "mon": 0}
    for source in sorted(agg):
        a = agg[source]
        other = a["chars"] - a["mon"]
        print(f"{source:24} {a['shards']:>6} {a['lines']:>12,} {a['chars']:>14,} {a['mon']:>14,} {other:>12,}")
        for k in total:
            total[k] += a[k]
    other = total["chars"] - total["mon"]
    pct = 100 * total["mon"] / total["chars"] if total["chars"] else 0.0
    print("-" * len(header))
    print(f"{'TOTAL':24} {total['shards']:>6} {total['lines']:>12,} {total['chars']:>14,} {total['mon']:>14,} {other:>12,}")
    print(f"Mon/Myanmar share: {pct:.1f}%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
