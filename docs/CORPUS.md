# Mon Corpus datasheet

What the shards contain, how they are built and cleaned, and what they still carry
that a user should know about. Per-source line and character counts are in the
[README Dataset table](../README.md#dataset) (`make stats`); licence terms are in
[LICENSE-CORPUS.md](../LICENSE-CORPUS.md), which governs.

## 1. Sources

Each source occupies its own files, identified by the shard filename prefix.

| Prefix | What it is | Caveats |
| :--- | :--- | :--- |
| `wikipedia_shard_*` | Articles from [Mon Wikipedia](https://mnw.wikipedia.org) | Per-article URLs were stripped, so individual articles cannot be traced back; `wikipedia_shard_003` keeps a partial set. Carries orphan `"` lines and URLs, see section 4 |
| `monnews_shard_*` | Articles from the [Independent Mon News Agency](https://monnews.org) | `monnews_shard_001` carries URLs, see section 4 |
| `custom_shard_*` | Specialized and legacy collections | Mixed Mon and Burmese; 0.5% blank lines, so blank lines are not document boundaries |
| `mondictdb_shard_*` | Entries and examples from [MonDictDB](https://github.com/Barnista/MonDictDB) | Mon headwords with Burmese definitions. Rows the upstream records as machine-translated were excluded at import. A flat lexical stream, not prose |
| `telegram_*_shard_*` | Public Telegram channel messages | |
| `facebook_shard_*` | Public Facebook page posts | |
| `ocr_extracted_shard_*` | Text recovered from scanned material by an OCR system | Can carry recognition errors |
| `handwritten_shard_*` | Composed directly in Mon by a native writer | Not scraped, transcribed or generated. [MonOCR](https://github.com/MonDevHub/monocr)'s training text includes it, so it is not held out from MonOCR |
| `gemini_generated_shard_*` | Authored by Google Gemini | LLM-authored and unverified; not transcribed from any source |

## 2. File format

- UTF-8, Unicode NFC, no BOM, no CRLF line endings.
- One segment per line, with a blank line between documents.
- About 20 MB per shard at most. A source with more text is split into numbered shards,
  `<source>_shard_001.txt`, `_002`, and so on.
- `shards/SHA256SUMS` holds a SHA-256 for every shard (section 7).

**Blank lines are not a reliable document boundary.** Measured by
`scripts/data_quality.py`, seven of the fifteen shards sit below 31% blank lines:
`mondictdb_shard_001` (3 in 94,658, 0.0%), `gemini_generated_shard_001` (1 in 962,
0.1%), `handwritten_shard_001` (1 in 1,501, 0.1%), `custom_shard_001` (599 in 119,737,
0.5%), `wikipedia_shard_005` (5.3%), `ocr_extracted_shard_001` (7.1%) and
`monnews_shard_003` (10.1%). The other eight run 32.0–49.8%. Splitting
`mondictdb_shard_001` on blank lines yields one 7.5 MB document. Check a shard's
blank-line share before treating blank lines as document boundaries.

**Most shards do not end in a newline.** Ten of the fifteen stop mid-line; only
`gemini_generated_shard_001`, `handwritten_shard_001`, `mondictdb_shard_001`,
`monnews_shard_003` and `wikipedia_shard_005` end in one. A missing final newline is
therefore not a sign of truncation; use `SHA256SUMS` for that.

## 3. How shards are built

`scripts/build_shards.py` adds new material. It takes a directory of `.txt` files, one
document per file, and for each document:

1. **Cleans** it (section 4).
2. **Splits** it into segments at Mon/Burmese clause and sentence endings and at ASCII
   `. ! ? , ; :`. Because Mon writing uses ASCII punctuation freely, the unit is a
   clause rather than a sentence, and a date or decimal such as `၃၁.၈.၂၀၂၅` splits into
   three. Over the current shards this rule yields 1,462,490 units, against 1,241,854
   under Mon-only endings, 15.1% more.
3. **Deduplicates** each segment against the existing corpus and the rest of the batch,
   using a Mon-script skeleton (Myanmar-block characters only). A segment is dropped
   only when its skeleton has at least 15 Mon characters and already exists; shorter
   segments are always kept. A document is skipped only when every segment in it is
   already present. Documents with under 20 Mon characters are kept and flagged.
4. **Packs** the surviving documents into new, higher-numbered shards for that source,
   one segment per line and a blank line between documents.
5. **Regenerates** `shards/SHA256SUMS` over every shard.

It never modifies or overwrites an existing shard; it refuses if a target file exists.
Run it with `--dry-run` first.

**Deduplication is not retroactive.** It applies to new material against what is
already there; it does not dedupe shards that were built before it. The README's
[Duplication](../README.md#duplication) section gives the measured redundancy across
the whole corpus. Deduplicate across all shards before splitting train from eval.

## 4. Cleaning

What `build_shards.py` applies to new material:

1. **NFC normalization.**
2. **Invisible format characters removed**: zero-width space, ZWJ, ZWNJ, BOM, soft
   hyphen, word joiner, left-to-right and right-to-left marks, bidi embedding, override
   and isolate controls, and the invisible math operators.
3. **Control codes removed** (`\x00`–`\x1F` except tab, newline and carriage return).
4. **Non-ASCII spaces folded** to a plain space (no-break space, thin space and the
   other Unicode spaces), not deleted, so adjacent words stay apart.
5. **URLs removed**, matching `http://`, `https://` or `www.` up to the first character
   that cannot appear in a URI. Because Mon does not separate words with spaces, the
   match does not run to the next space, which would swallow the Mon text after a URL.
6. **Whitespace collapsed**: runs of spaces reduced to one, lines trimmed, empty lines
   dropped within a document.
7. **Script preserved**: Mon, Burmese and English mixed content is kept. Nothing is
   dropped for being non-Mon, because Mon and Burmese are mixed in ordinary written use.

**Most shards were built before the importer and did not go through it.** Measured over
the current shards, they still carry:

| Residue | Count | Where |
| :--- | ---: | :--- |
| URLs | 9,228 | `wikipedia_shard_003` 5,457, `monnews_shard_001` 3,715, `telegram_mot_tip_ebook_shard_001` 52, `facebook_shard_001` 4 |
| Lines that are a lone `"`; in the Wikipedia shards, what is left of a stripped "Retrieved from" prefix | 5,602 | `wikipedia_shard_001` 1,975, `_002` 1,670, `_003` 1,410, `_004` 545; one each in `custom_shard_001` and `telegram_mot_tip_ebook_shard_001` |
| U+00AD SOFT HYPHEN | 94 | `wikipedia_shard_001` |
| U+200E LEFT-TO-RIGHT MARK | 13 | `custom_shard_001`, `telegram_mot_tip_ebook_shard_001`, `wikipedia_shard_001`, `_003`, `_005` |
| U+2060 WORD JOINER | 5 | `wikipedia_shard_001` |
| U+2061 FUNCTION APPLICATION | 5 | `wikipedia_shard_001`, `_002` |
| U+00A0 NO-BREAK SPACE | 13,800 | several |
| U+2009 THIN SPACE | 6 | |

`make quality` prints the URL count per shard. The other rows reproduce with:

```bash
grep -cx '"' shards/*.txt     # lone-quote lines per shard
python3 -c "import glob; t=''.join(open(f, encoding='utf-8').read() for f in glob.glob('shards/*_shard_*.txt')); [print(f'U+{c:04X}', t.count(chr(c))) for c in (0xAD, 0x200E, 0x2060, 0x2061, 0xA0, 0x2009)]"
```

Run your own cleaning pass if your use is sensitive to any of these;
`clean_document()` in `scripts/build_shards.py` applies the rules above to any text.

## 5. Normalization and script

- **NFC throughout.** Mon relies on combining marks and stacked consonants; NFC keeps
  tokenizers and models consistent. All fifteen shards are NFC as stored.
- **Preserved as structural**: virama (U+1039) for stacked consonants, asat (U+103A)
  for syllable-final consonants, and the medials (U+103B–U+103E).
- **Mon NGA is not normalized.** Mon `ၚ` (U+105A) is sometimes typed as Burmese `င`
  (U+1004). The shards keep what was written: U+1004 occurs 581,296 times and U+105A
  902,634 times (`results/latest/character_frequency.csv`). `scripts/corpus_counter_normalized.py --normalize-mon-nga` maps
  U+1004 to U+105A for analysis only; it never changes a shard, and it is off for the
  tables in `results/latest/`.

## 6. Personal data

The shards carry no email addresses and no mobile-number-shaped strings.
`scripts/data_quality.py --check` (run by `make quality` and `make check`) exits
non-zero if either appears.

**What was removed.** One redaction pass removed 21 lines across six shards:
`custom_shard_001`, `facebook_shard_001`, `monnews_shard_001`, `monnews_shard_002`,
`telegram_mot_tip_ebook_shard_001` and `wikipedia_shard_001`. Whole lines were
removed, never masked: most of the material paired a personal name with a number, and
masking the number leaves the name and the association intact. Where a removed line
was its own document, one adjacent blank line went with it, 12 in all, so document
separators stayed single.

**Earlier commits still contain the removed lines.** The redaction changed the current
files, not the repository's git history. If you mirror or redistribute this
repository, take the current tree, not the full history.

**What the check looks for.**

- Email addresses, by the ordinary `local@domain.tld` shape.
- Mobile-number shapes for the two dialling plans the sources use: Myanmar (`09…`,
  `+959…`) and Thailand (`0[689]…`, `0[2-7]…`). Not "any long digit run": the corpus is
  full of ISBNs, DOIs, years and populations, which a loose pattern would report.
- **Both numeral systems.** Myanmar digits U+1040–U+1049 are not matched by `\d`, so an
  ASCII-only scan misses a number written `၀၉…`. The check transliterates them and
  applies the same shape test.

**What it does not find.** A name next to a number is the real exposure, and pattern
scanning sees only the number. The check is a floor, not a substitute for reading
material before importing it.

**Known non-matches, verified by inspection.** Nine ISBN-10s in
`wikipedia_shard_001`–`004` strip to ten digits beginning `09` and are excluded by the
`ISBN` label on the preceding line; one DOI, one astronomical value in AU and one Zoom
meeting ID are excluded by shape. None is personal data.

## 7. Integrity

`shards/SHA256SUMS` lists a SHA-256 for every shard. Verify a copy with:

```bash
cd shards && shasum -a 256 -c SHA256SUMS     # or sha256sum -c on Linux
```

`make verify` runs that check and also fails if any shard is missing from the manifest,
which `shasum -c` alone does not detect. Git's object hashes protect a clone; the
manifest is what protects a tarball, a partial copy or a single downloaded shard.

`build_shards.py` regenerates the manifest after an import. If you edit a shard any
other way, regenerate it:

```bash
cd shards && shasum -a 256 *.txt > SHA256SUMS
```

## 8. Frequency tables

`results/latest/` holds character, bigram and trigram frequencies and per-file counts
over all shards, with no `--normalize-mon-nga` mapping. Regenerate it with
`make frequencies`, which runs:

```bash
python3 scripts/corpus_counter_normalized.py shards --output-dir results/latest --all-chars
```

In `summary.json`, `total_raw_text_length` (52,256,919) is a **character** count, `len()`
over the decoded text, not a byte count. The shards are 130,428,126 bytes, 2.49 times
larger, because Myanmar-script code points take three bytes each in UTF-8.
`total_counted_characters` (47,221,746) is the non-whitespace count and equals the
README's Characters total.

`results/` is derived from every shard and inherits the per-source terms; see
[LICENSE-CORPUS.md](../LICENSE-CORPUS.md).

## 9. Known limitations

- **Licence.** Only the Wikipedia and MonDictDB shards have established terms; the
  others are unresolved. See [LICENSE-CORPUS.md](../LICENSE-CORPUS.md).
- **Attribution.** Wikipedia shards cannot be attributed per article (section 1).
- **Duplication** across and within shards, about a quarter of eligible lines. Not
  removed from older shards (section 3).
- **Residue** in shards that predate the importer: URLs, orphan quote lines and
  invisible characters (section 4).
- **Blank lines** are not a consistent document boundary (section 2).
- **Lower-confidence sources**: OCR Extracted can carry recognition errors, and the
  Machine-generated shard is unverified LLM text.
- **Personal data** in git history (section 6).

To report a normalization problem, data corruption or material that should not be
here, open an issue on
[MonDevHub/MonCorpusCollection](https://github.com/MonDevHub/MonCorpusCollection).
