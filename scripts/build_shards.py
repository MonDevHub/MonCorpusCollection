#!/usr/bin/env python3
"""
build_shards.py

Add newly scraped .txt files (one document per file) to shards/ WITHOUT touching
or losing any existing data. Follows the corpus conventions in docs/CORPUS.md.

Safety guarantees:
- Never reads-modifies-writes an existing shard. Only creates new, higher-numbered
  shard files for the given source. Refuses to overwrite an existing file.
- Cleaning is minimal: keep all Mon/Burmese/English mixed content; remove only URLs
  and unusable chars (control codes, zero-width marks, BOM). No content is dropped
  for being English or mixed-language.
- Deduplication is biased toward keeping: a segment is dropped only when its
  Mon-script skeleton (Myanmar-block chars only) of at least MIN_SKELETON characters
  already exists in the corpus. Short segments are always kept. A document is skipped
  only when every segment in it is already in the corpus (nothing new to add).

  The dedup unit is a CLAUSE, not a sentence. SENT_SPLIT_RE breaks on ASCII `. ! ? , ; :`
  as well as the Mon/Burmese endings, and Mon writing uses ASCII punctuation freely, so
  the unit is finer than a sentence. Measured over the tracked shards on 2026-08-12:
  1,462,515 units under the current rule vs 1,241,879 under Mon-only endings — 220,636
  extra fragments, 15.1%. 6,953 of the ASCII break points sit between two digits, i.e.
  inside a date or decimal (`၃၁.၈.၂၀၂၅` fragments into three units). This is documented
  rather than fixed: the split defines the dedup key, so narrowing it would silently
  restate every published dedup number in README.md and docs/CORPUS.md against a key
  nothing was measured with. See SENT_SPLIT_RE below.

Pipeline per document:
  clean (NFC, strip URLs + format chars, fold Unicode spaces, collapse whitespace)
    -> split into segments (clauses, see above)
    -> drop segments whose Mon skeleton is already in the corpus (or seen this run)
    -> keep the document if any new segment remains
    -> pack surviving documents into ~20 MB shards, one segment per line,
       blank line between documents (matching existing shards).

Examples:
    python3 scripts/build_shards.py --source monnews \\
        --input ../mon-corpus-scraper/data/monnews --dry-run
    python3 scripts/build_shards.py --source wikipedia \\
        --input ../mon-corpus-scraper/data/wikipedia
"""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
import unicodedata
from pathlib import Path

DEFAULT_SHARD_BYTES = 20 * 1024 * 1024      # ~20 MB, matching existing shards
MIN_SKELETON = 15                            # min Mon chars for a sentence to be deduped
MIN_DOC_MON_CHARS = 20                       # kept docs below this are flagged near-English (not dropped)

# Format characters that carry no glyph. Deleting them loses nothing legible, and leaving
# them in splits otherwise-identical text into distinct dedup keys.
#
# The original set was FEFF/200B/200C/200D. Measured across the tracked shards on
# 2026-08-12, that set left behind: 94 x U+00AD SOFT HYPHEN and 5 x U+2060 WORD JOINER
# (both wikipedia_shard_001), 13 x U+200E LEFT-TO-RIGHT MARK (four shards) and 5 x U+2061
# FUNCTION APPLICATION. All of them are Default_Ignorable_Code_Point, so the fix is to
# cover that category rather than to keep appending one code point per bug report.
INVISIBLE = dict.fromkeys((
    0x00AD,                                  # SOFT HYPHEN
    0x200B, 0x200C, 0x200D,                  # ZWSP, ZWNJ, ZWJ
    0x200E, 0x200F,                          # LRM, RLM
    0x202A, 0x202B, 0x202C, 0x202D, 0x202E,  # bidi embedding / override
    0x2060,                                  # WORD JOINER
    0x2061, 0x2062, 0x2063, 0x2064,          # invisible math operators
    0x2066, 0x2067, 0x2068, 0x2069,          # bidi isolates
    0xFEFF,                                  # BOM / ZERO WIDTH NO-BREAK SPACE
))
# Non-ASCII spaces are folded to a plain space, NOT deleted: deleting U+00A0 welds two
# words into one. 13,800 NO-BREAK SPACE and 6 THIN SPACE survive in the tracked shards.
# They are whitespace to str.isspace(), so the published character counts (which exclude
# whitespace) do not move — but they do make identical lines compare unequal.
UNICODE_SPACE_RE = re.compile("[\u00a0\u1680\u2000-\u200a\u202f\u205f\u3000]")
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
# URL matching stops at the first character that cannot appear in a URI (RFC 3986), not at
# the next whitespace. `http\S+` was wrong for this corpus specifically: Mon does not mark
# word boundaries with spaces, so `http://x.com၏မန်ဘာသာ` had the trailing Mon clause eaten
# along with the URL and nothing counted the loss. Parenthesised paths (common in Wikipedia
# links) are matched as a balanced group so `.../Mon_(Unicode_block)` survives intact while
# a sentence's own closing bracket does not get swallowed. The trailing lookbehind keeps
# sentence punctuation out of the match. Verified to still find all 9,228 URLs in the
# tracked shards, and clean_document() now reports how many it removed.
URL_RE = re.compile(
    r"(?:https?://|www\.)"
    r"(?:[A-Za-z0-9\-._~:/?#\[\]@!$&'*+,;=%]|\([^\s()]*\))+"
    r"(?<![.,;:!?'\"])"
)
MULTISPACE_RE = re.compile(r"[ \t]{2,}")
# Myanmar-block characters only (matches is_myanmar_related in corpus_counter_normalized.py).
NON_MON_RE = re.compile(r"[^က-႟ꩠ-ꩿꧠ-꧿]")
# Segment boundaries: Mon/Burmese endings plus ASCII sentence punctuation. Despite the name
# this yields clauses, not sentences — see the module docstring for the measured cost
# (220,636 extra fragments, 15.1%) and for why it is documented instead of narrowed.
SENT_SPLIT_RE = re.compile(r"(?<=[။၊၍၎၏ၐၑ\.\!\?\,\;\:])")
SHARD_NAME_RE = re.compile(r"^(?P<source>.+)_shard_(?P<index>\d{3})\.txt$")
# A source name becomes both a filename and a glob() pattern, so it is restricted to
# characters that are inert in both. See validate_source().
SOURCE_RE = re.compile(r"^[a-z0-9][a-z0-9_]*$")


def clean_document(text: str, stats: dict | None = None) -> str:
    """Minimal cleaning: keep all Mon/Burmese/English mixed content; remove only
    URLs and unusable chars (control codes, invisible format chars, BOM); fold
    non-ASCII spaces to a plain space and collapse runs.

    Pass a dict as `stats` to accumulate what was removed. URL removal is the only
    step that can delete real words, so it is the only one that is counted: before
    this, a bad URL pattern could eat Mon text with nothing in the output to show it.
    The parameter is optional so that callers which only want the text — including
    scripts/data_quality.py, which imports this function — are unaffected.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.translate(INVISIBLE)
    text = CONTROL_RE.sub("", text)
    text = UNICODE_SPACE_RE.sub(" ", text)
    if stats is not None:
        removed = URL_RE.findall(text)
        stats["urls_removed"] = stats.get("urls_removed", 0) + len(removed)
        stats["url_chars_removed"] = stats.get("url_chars_removed", 0) + sum(len(u) for u in removed)
    text = URL_RE.sub(" ", text)
    lines = [MULTISPACE_RE.sub(" ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line)


def split_sentences(text: str) -> list[str]:
    out: list[str] = []
    for line in text.split("\n"):
        out.extend(part.strip() for part in SENT_SPLIT_RE.split(line) if part.strip())
    return out


def mon_skeleton(sentence: str) -> str:
    return NON_MON_RE.sub("", unicodedata.normalize("NFC", sentence))


def skeleton_key(sentence: str) -> str | None:
    """Dedup key for a sentence, or None if it is too short to dedup safely."""
    skel = mon_skeleton(sentence)
    if len(skel) < MIN_SKELETON:
        return None
    return hashlib.sha1(skel.encode("utf-8")).hexdigest()


def iter_shard_docs(shard_text: str):
    for block in re.split(r"\n\s*\n", shard_text):
        block = block.strip("\n")
        if block.strip():
            yield block


def load_corpus_skeletons(shards_dir: Path) -> set[str]:
    """Skeleton keys of every sentence already in shards/."""
    keys: set[str] = set()
    for shard in sorted(shards_dir.glob("*_shard_*.txt")):
        for doc in iter_shard_docs(shard.read_text("utf-8")):
            for sent in split_sentences(clean_document(doc)):
                k = skeleton_key(sent)
                if k:
                    keys.add(k)
    return keys


def validate_source(source: str) -> str:
    """Reject a --source value that is not safe as both a filename and a glob pattern.

    The value is interpolated into two places, and each fails differently:

      flush_shard()      -> f"{source}_shard_{index:03d}.txt", then shards_dir / name.
                            `--source ../../x` writes outside shards/ entirely.
      next_shard_index() -> shards_dir.glob(f"{source}_shard_*.txt").
                            A `[`, `*` or `?` is a glob metacharacter, so the scan for
                            the highest existing index silently matches a different set
                            of files — or none. That is the input to the next index, so
                            it can hand flush_shard() an index that is already taken.
                            The overwrite guard still refuses, but the guard is meant to
                            be unreachable; reaching it means the numbering was wrong.

    Every existing shard prefix (monnews, wikipedia, mondictdb, custom, facebook,
    ocr_extracted, gemini_generated, handwritten, telegram_mot_tip_ebook) already fits
    the pattern, so this rejects nothing that is in use.
    """
    if not SOURCE_RE.match(source):
        raise SystemExit(
            f"Invalid --source {source!r}: expected lowercase letters, digits and "
            f"underscores only, starting with a letter or digit (e.g. monnews). "
            f"The value becomes both a filename and a glob pattern."
        )
    return source


def next_shard_index(shards_dir: Path, source: str) -> int:
    highest = 0
    for shard in shards_dir.glob(f"{source}_shard_*.txt"):
        m = SHARD_NAME_RE.match(shard.name)
        if m and m.group("source") == source:
            highest = max(highest, int(m.group("index")))
    return highest + 1


def write_checksums(shards_dir: Path) -> Path:
    """Regenerate shards/SHA256SUMS over every *.txt in shards/.

    Wired into the import because the manual step documented in docs/CORPUS.md is the
    step nobody remembers, and forgetting it is silent in both directions: the new shard
    is simply absent from the manifest, and `shasum -c` still exits 0 because it only
    verifies the files it lists. A manifest that passes while covering fewer files than
    exist is worse than no manifest.

    Format matches `cd shards && shasum -a 256 *.txt` byte for byte: lowercase hex, two
    spaces, then the bare filename. The paths are relative, so verification must run from
    inside shards/ (see the `verify` target in the Makefile).
    """
    lines = []
    for path in sorted(shards_dir.glob("*.txt")):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}\n")
    target = shards_dir / "SHA256SUMS"
    target.write_text("".join(lines), "utf-8")
    return target


def mon_char_count(text: str) -> int:
    # NON_MON_RE.sub("", text) removes every non-Mon char, leaving only Mon chars.
    return len(NON_MON_RE.sub("", text)) if text else 0


def build(source: str, input_dir: Path, shards_dir: Path, shard_bytes: int, dry_run: bool) -> int:
    corpus_keys = load_corpus_skeletons(shards_dir)
    seen = set(corpus_keys)  # includes intra-batch dedup as we go

    kept_docs: list[str] = []
    stats = {"input_docs": 0, "dup_sentences": 0, "kept_sentences": 0,
             "fully_dup_docs": 0, "english_only_docs": 0, "kept_docs": 0, "kept_chars": 0}
    clean_stats: dict[str, int] = {}
    dup_samples: list[str] = []
    english_samples: list[str] = []

    # rglob, not glob. A non-recursive scan of a nested scrape layout
    # (input/2026-01/*.txt, input/by-section/*/*.txt) finds zero files and then reports
    # "Nothing new to add." with exit 0 — the same output as a run where every document
    # was already in the corpus. Two opposite outcomes, one message. rglob fixes the
    # common layout; the exit-2 branch below makes the remaining case distinguishable.
    for path in sorted(input_dir.rglob("*.txt")):
        if path.name.startswith("downloaded_"):
            continue
        stats["input_docs"] += 1
        cleaned = clean_document(path.read_text("utf-8"), stats=clean_stats)
        if not cleaned:
            continue

        kept_sentences: list[str] = []
        for sent in split_sentences(cleaned):
            k = skeleton_key(sent)
            if k is not None and k in seen:
                stats["dup_sentences"] += 1
                if len(dup_samples) < 4 and mon_char_count(sent) > 30:
                    dup_samples.append(sent)
                continue
            if k is not None:
                seen.add(k)
            kept_sentences.append(sent)

        doc_text = "\n".join(kept_sentences)
        if not doc_text.strip():           # every sentence already in the corpus
            stats["fully_dup_docs"] += 1
            continue

        if mon_char_count(doc_text) < MIN_DOC_MON_CHARS:   # flagged for review, still kept
            stats["english_only_docs"] += 1
            if len(english_samples) < 5:
                english_samples.append(doc_text[:100])

        kept_docs.append(doc_text)
        stats["kept_sentences"] += len(kept_sentences)
        stats["kept_chars"] += len(doc_text)

    stats["kept_docs"] = len(kept_docs)

    print(f"source:                 {source}")
    print(f"corpus sentences indexed (>= {MIN_SKELETON} Mon chars): {len(corpus_keys)}")
    print(f"input documents:        {stats['input_docs']}")
    print(f"duplicate sentences dropped (already in corpus): {stats['dup_sentences']}")
    print(f"fully-duplicate documents skipped: {stats['fully_dup_docs']}")
    print(f"KEPT documents:         {stats['kept_docs']}")
    print(f"KEPT sentences:         {stats['kept_sentences']}")
    print(f"KEPT characters:        {stats['kept_chars']}")
    print(f"URLs removed:           {clean_stats.get('urls_removed', 0)} "
          f"({clean_stats.get('url_chars_removed', 0)} characters)")
    print(f"  note: {stats['english_only_docs']} kept doc(s) are near-pure English/non-Mon (flagged, kept per policy)")
    if dup_samples:
        print("  sample dropped-duplicate sentences (already in corpus):")
        for s in dup_samples:
            print(f"    - {s[:100]}")
    if english_samples:
        print("  sample near-pure-English kept documents (flagged, NOT dropped):")
        for s in english_samples:
            print(f"    - {s[:90]}")

    # "Found nothing to read" and "read everything, all of it was already here" are
    # different outcomes and used to print the same line with the same exit 0. A typo in
    # --input, or a layout rglob still does not cover, is now an error rather than a
    # cheerful no-op.
    if stats["input_docs"] == 0:
        sys.stdout.flush()   # keep the error after the report it explains
        print(f"Error: no .txt files found under {input_dir} (searched recursively). "
              f"Nothing was read, which is not the same as nothing being new.",
              file=sys.stderr)
        return 2
    if not kept_docs:
        print(f"Nothing new to add: all {stats['input_docs']} input document(s) were "
              f"already in the corpus.")
        return 0
    if dry_run:
        approx = sum(len((d + '\n\n').encode('utf-8')) for d in kept_docs)
        # Ceiling, not floor+1: `approx // shard_bytes + 1` reported 2 shards for an
        # exact 20 MB payload and 3 for an exact 40 MB one, because it added a shard for
        # a remainder of zero. The real loop flushes at doc boundaries, so this is a
        # lower bound — a payload can spill into one more shard than the arithmetic says.
        print(f"[dry-run] would write >={-(-approx // shard_bytes)} shard(s), "
              f"~{approx} bytes. No files changed.")
        return 0

    index = next_shard_index(shards_dir, source)
    written: list[str] = []
    buf: list[str] = []
    size = 0
    for doc in kept_docs:
        block = doc + "\n\n"
        buf.append(block)
        size += len(block.encode("utf-8"))
        if size >= shard_bytes:
            written.append(flush_shard(shards_dir, source, index, buf))
            index += 1
            buf, size = [], 0
    if buf:
        written.append(flush_shard(shards_dir, source, index, buf))

    print(f"wrote {len(written)} shard(s): {', '.join(written)}")

    manifest = write_checksums(shards_dir)
    print(f"regenerated {manifest} over {len(list(shards_dir.glob('*.txt')))} file(s)")
    return 0


def flush_shard(shards_dir: Path, source: str, index: int, buf: list[str]) -> str:
    name = f"{source}_shard_{index:03d}.txt"
    target = shards_dir / name
    if target.exists():  # never overwrite existing data
        raise SystemExit(f"Refusing to overwrite existing shard: {target}")
    target.write_text("".join(buf), "utf-8")
    return name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add scraped .txt files to shards/ (dedup + junk filter).")
    parser.add_argument("--source", required=True,
                        help="Source name: lowercase letters, digits and underscores, "
                             "e.g. monnews or telegram_mot_tip_ebook.")
    parser.add_argument("--input", type=Path, required=True, help="Directory of raw .txt files.")
    parser.add_argument("--shards-dir", type=Path, default=Path(__file__).resolve().parent.parent / "shards")
    parser.add_argument("--shard-bytes", type=int, default=DEFAULT_SHARD_BYTES)
    parser.add_argument("--dry-run", action="store_true", help="Report without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source = validate_source(args.source)
    if not args.input.is_dir():
        print(f"Error: input directory not found: {args.input}", file=sys.stderr)
        return 1
    args.shards_dir.mkdir(parents=True, exist_ok=True)
    # Exit codes are distinct on purpose: 0 wrote or had nothing new, 1 bad input path,
    # 2 read no documents at all. A caller in a pipeline can tell them apart.
    return build(source, args.input, args.shards_dir, args.shard_bytes, args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
