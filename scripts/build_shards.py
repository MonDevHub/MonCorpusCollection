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
- Deduplication is biased toward keeping: a sentence is dropped only when its
  Mon-script skeleton (Myanmar-block chars only) of at least MIN_SKELETON characters
  already exists in the corpus. Short sentences are always kept. A document is skipped
  only when every sentence in it is already in the corpus (nothing new to add).

Pipeline per document:
  clean (NFC, strip URLs + BOM/ZWSP/ZWJ/ZWNJ/control, collapse whitespace)
    -> split into sentences
    -> drop sentences whose Mon skeleton is already in the corpus (or seen this run)
    -> keep the document if any new sentence remains
    -> pack surviving documents into ~20 MB shards, one sentence per line,
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

INVISIBLE = {cp: None for cp in (0xFEFF, 0x200B, 0x200C, 0x200D)}
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
URL_RE = re.compile(r"http\S+|www\.\S+")
MULTISPACE_RE = re.compile(r"[ \t]{2,}")
# Myanmar-block characters only (matches is_myanmar_related in corpus_counter_normalized.py).
NON_MON_RE = re.compile(r"[^က-႟ꩠ-ꩿꧠ-꧿]")
# Sentence boundaries: Mon/Burmese endings plus ASCII sentence punctuation.
SENT_SPLIT_RE = re.compile(r"(?<=[။၊၍၎၏ၐၑ\.\!\?\,\;\:])")
SHARD_NAME_RE = re.compile(r"^(?P<source>.+)_shard_(?P<index>\d{3})\.txt$")


def clean_document(text: str) -> str:
    """Minimal cleaning: keep all Mon/Burmese/English mixed content; remove only
    URLs and unusable chars (control codes, zero-width marks, BOM); collapse spaces."""
    text = unicodedata.normalize("NFC", text)
    text = text.translate(INVISIBLE)
    text = CONTROL_RE.sub("", text)
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


def next_shard_index(shards_dir: Path, source: str) -> int:
    highest = 0
    for shard in shards_dir.glob(f"{source}_shard_*.txt"):
        m = SHARD_NAME_RE.match(shard.name)
        if m and m.group("source") == source:
            highest = max(highest, int(m.group("index")))
    return highest + 1


def mon_char_count(text: str) -> int:
    # NON_MON_RE.sub("", text) removes every non-Mon char, leaving only Mon chars.
    return len(NON_MON_RE.sub("", text)) if text else 0


def build(source: str, input_dir: Path, shards_dir: Path, shard_bytes: int, dry_run: bool):
    corpus_keys = load_corpus_skeletons(shards_dir)
    seen = set(corpus_keys)  # includes intra-batch dedup as we go

    kept_docs: list[str] = []
    stats = dict(input_docs=0, dup_sentences=0, kept_sentences=0,
                 fully_dup_docs=0, english_only_docs=0, kept_docs=0, kept_chars=0)
    dup_samples: list[str] = []
    english_samples: list[str] = []

    for path in sorted(input_dir.glob("*.txt")):
        if path.name.startswith("downloaded_"):
            continue
        stats["input_docs"] += 1
        cleaned = clean_document(path.read_text("utf-8"))
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
    print(f"  note: {stats['english_only_docs']} kept doc(s) are near-pure English/non-Mon (flagged, kept per policy)")
    if dup_samples:
        print("  sample dropped-duplicate sentences (already in corpus):")
        for s in dup_samples:
            print(f"    - {s[:100]}")
    if english_samples:
        print("  sample near-pure-English kept documents (flagged, NOT dropped):")
        for s in english_samples:
            print(f"    - {s[:90]}")

    if not kept_docs:
        print("Nothing new to add.")
        return
    if dry_run:
        approx = sum(len((d + '\n\n').encode('utf-8')) for d in kept_docs)
        print(f"[dry-run] would write ~{approx // shard_bytes + 1} shard(s), "
              f"~{approx} bytes. No files changed.")
        return

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


def flush_shard(shards_dir: Path, source: str, index: int, buf: list[str]) -> str:
    name = f"{source}_shard_{index:03d}.txt"
    target = shards_dir / name
    if target.exists():  # never overwrite existing data
        raise SystemExit(f"Refusing to overwrite existing shard: {target}")
    target.write_text("".join(buf), "utf-8")
    return name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Add scraped .txt files to shards/ (dedup + junk filter).")
    parser.add_argument("--source", required=True, help="Source name, e.g. monnews or wikipedia.")
    parser.add_argument("--input", type=Path, required=True, help="Directory of raw .txt files.")
    parser.add_argument("--shards-dir", type=Path, default=Path(__file__).resolve().parent.parent / "shards")
    parser.add_argument("--shard-bytes", type=int, default=DEFAULT_SHARD_BYTES)
    parser.add_argument("--dry-run", action="store_true", help="Report without writing.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.input.is_dir():
        print(f"Error: input directory not found: {args.input}", file=sys.stderr)
        return 1
    args.shards_dir.mkdir(parents=True, exist_ok=True)
    build(args.source, args.input, args.shards_dir, args.shard_bytes, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
