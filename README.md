# Mon Language Corpus Collection

A Mon-language text corpus for NLP research, language-model pretraining and OCR
training data. It is the training data source for
[MonOCR](https://github.com/MonDevHub/monocr).

**The corpus is not MIT, and seven of its nine sources have no established licence.**
Read [Licence](#licence) before redistributing any shard or book text.

## Dataset

| Source | Shards | Lines | Characters | Mon/Myanmar | Other |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mon Wikipedia** | 5 | 910,074 | 25,589,404 | 21,724,647 | 3,864,757 |
| **Mon News Agency** | 3 | 121,008 | 12,064,310 | 10,991,170 | 1,073,140 |
| **Custom Collections** | 1 | 119,737 | 6,831,335 | 3,681,830 | 3,149,505 |
| **MonDictDB** | 1 | 94,658 | 2,484,241 | 2,357,122 | 127,119 |
| **Telegram** | 1 | 3,151 | 58,025 | 48,941 | 9,084 |
| **Facebook** | 1 | 1,315 | 36,546 | 32,187 | 4,359 |
| **OCR Extracted** | 1 | 733 | 37,624 | 36,824 | 800 |
| **Handwritten** | 1 | 1,501 | 97,119 | 94,669 | 2,450 |
| **Machine-generated** | 1 | 962 | 23,142 | 21,567 | 1,575 |
| **Total** | **15** | **1,253,139** | **47,221,746** | **38,988,957 (82.6%)** | **8,232,789 (17.4%)** |

Every cell is printed by `make stats` (`scripts/shard_stats.py`). Raw size is
130,428,126 bytes, 124 MiB of uncompressed UTF-8 (`cat shards/*.txt | wc -c`).

**Lines counts every newline**, including the blank line between documents.
493,845 of the 1,253,139 lines are blank (39.4%), leaving 759,294 with text, of
which 53,275 are three characters or fewer. Budget for roughly 700K usable text
lines, not 1.25M. The character columns already exclude whitespace. `make quality`
prints these counts.

**Other is not noise.** Mon and Burmese are mixed in ordinary written use, so
mixed-script material is kept as it appears. MonDictDB is the clearest case: Mon
headwords with Burmese definitions, kept whole.

## Data quality

`make quality` (`scripts/data_quality.py --check`) prints the URL and duplication
figures below and fails if personal data reappears.

- **NFC.** All text is normalized to Unicode NFC.
- **What is stripped.** BOM, ZWJ, ZWNJ and control codes. All Myanmar script
  blocks (U+1000–U+109F, Extended-A/B) and intentional spacing are kept.
- **URLs remain in older shards.** 9,228 of them, almost all in
  `wikipedia_shard_003` and `monnews_shard_001`, which predate the importer's URL
  rule.
- **Personal data.** Every email address and mobile-number-shaped string was
  removed from the shards in one redaction pass: 21 lines across six shards. Whole
  lines were removed rather than masked, because the material was mostly
  name-and-number rosters and masking the number leaves the name beside the gap. The check scans both ASCII and Myanmar
  numerals (U+1040–U+1049), which a `\d` pattern misses. Earlier commits in the
  git history still contain the removed lines.

### Duplication

`scripts/build_shards.py` deduplicates new content against the existing corpus at
the clause level (a Mon-script skeleton) before adding it, so re-scraped
material is not appended twice. It does not retroactively dedupe shards built
before it.

Measured with that same key over each cleaned non-blank line: of 369,898 eligible
lines, **94,006 are redundant instances (25.4%)**, 4,708,496 characters. The
duplicates are not short: median 63 characters across the 35,156 skeletons that
repeat, p90 180, longest 2,575. **4,542 skeletons appear in more than one shard.**
Five shards contribute no duplicates at all, `mondictdb_shard_001` (54,457
eligible lines) and `handwritten_shard_001` among them; `make quality` prints the
per-shard breakdown.

**Do not split `shards/` into train and eval by file.** Roughly 4,500 skeletons
straddle any such boundary and inflate whatever you measure. Deduplicate across
the whole corpus first, then split.

## Books

[`books/`](books/) holds four Mon documents read by OCR, one folder each, kept as
readable page-by-page texts rather than shards. They are machine OCR, not proofread, and
their terms are unresolved. `make stats`, `make quality` and `results/latest/` cover the
shards only, so none of the figures above include them.

## Structure

```text
MonCorpusCollection/
├── shards/                           # Distribution shards, up to ~20 MB each, plus SHA256SUMS
│   ├── wikipedia_shard_*.txt         # Mon Wikipedia articles
│   ├── monnews_shard_*.txt           # Mon News Agency (IMNA) articles
│   ├── custom_shard_*.txt            # Specialized and legacy collections
│   ├── mondictdb_shard_*.txt         # MonDictDB dictionary entries and examples
│   ├── telegram_*_shard_*.txt        # Telegram channel messages
│   ├── facebook_shard_*.txt          # Facebook page posts
│   ├── ocr_extracted_shard_*.txt     # OCR-extracted text
│   ├── handwritten_shard_*.txt       # Composed directly in Mon by a native writer
│   └── gemini_generated_shard_*.txt  # LLM-authored, unverified
├── books/                            # OCR-read Mon documents, one folder each (not shards)
├── results/latest/                   # Character/bigram/trigram frequency over the shards
├── scripts/                          # stdlib-only Python: stats, quality, import, counters
└── docs/CORPUS.md                    # Datasheet: sources, build, cleaning, limitations
```

## Usage

The scripts use only the Python standard library and need Python 3.10 or newer.

Each shard is UTF-8 text, one segment per line. Blank-line density varies too
much to treat a blank line as a document boundary everywhere: `mondictdb_shard_001`
has 3 in 94,658 lines, and [docs/CORPUS.md](docs/CORPUS.md) lists the other low
ones.

```bash
make stats     # per-source table above
make verify    # shards against shards/SHA256SUMS, including coverage
make quality   # data-quality figures and the personal-data gate
make check     # verify + quality + lint
make frequencies   # regenerate results/latest/ (character, bigram, trigram tables)

# Add newly scraped .txt files as deduplicated shards (dry-run first)
python3 scripts/build_shards.py --source monnews --input path/to/monnews --dry-run
```

## Licence

MIT covers `scripts/` and the `Makefile` only; see [LICENSE](LICENSE). The text in
`shards/` and `books/` and the tables in `results/` carry the terms of their sources,
set out per source in [LICENSE-CORPUS.md](LICENSE-CORPUS.md), which governs.

| Source | Files | Origin | Terms |
| :--- | :--- | :--- | :--- |
| Mon Wikipedia | `wikipedia_shard_*` | [mnw.wikipedia.org](https://mnw.wikipedia.org) | CC BY-SA 4.0 |
| MonDictDB | `mondictdb_shard_*` | [MonDictDB](https://github.com/Barnista/MonDictDB) by [Barnista](https://github.com/Barnista) | MIT |
| Mon News Agency (IMNA) | `monnews_shard_*` | [Independent Mon News Agency](https://monnews.org) | **Unresolved** |
| Telegram / Facebook | `telegram_*_shard_*`, `facebook_shard_*` | Public channel and page posts | **Unresolved** |
| OCR Extracted | `ocr_extracted_shard_*` | Text recovered from scanned material | **Unresolved** |
| Custom Collections | `custom_shard_*` | Specialized and legacy collections | **Unresolved** |
| Machine-generated | `gemini_generated_shard_*` | Authored by Google Gemini, not transcribed from any source | **Unresolved** |
| Handwritten | `handwritten_shard_*` | Composed directly in Mon by a native writer: not scraped, transcribed or generated | **Unresolved** |
| Books | `books/` | Four Mon documents read by OCR; sources in [books/README.md](books/README.md) | **Unresolved** |

Only the Wikipedia and MonDictDB shards are covered, under CC BY-SA 4.0 and MIT.
Redistributing any **Unresolved** shard or book text is not covered by anything in
this repository. Attribute **Mon Corpus Collection** and the underlying source of
each shard or book you use; for the Wikipedia shards, use the CC BY-SA 4.0
attribution and list of changes in [LICENSE-CORPUS.md](LICENSE-CORPUS.md#cc-by-sa-40-attribution-for-wikipedia_shard_).

### Confidence by source

- **Handwritten** is the cleanest material here: no scraping artefacts, no
  recognition errors, no machine-authored text. Measured against the rest of the
  corpus at import: 97.5% Mon script, 0.014% malformed tokens (the corpus bar is
  1.0%), zero URLs, and a mean charset survival of 0.9985 with no line below 0.50.
  It would be the best start for a clean evaluation or fine-tuning slice once the
  writer's grant is recorded; until then its terms are unresolved. MonOCR's training
  text already includes it, so it is not held out from MonOCR.
- **OCR Extracted** is the output of an OCR system and can carry its recognition
  errors.
- **Books** are machine OCR, not proofread; each book's README lists its known
  recognition errors.
- **MonDictDB** upstream records some definitions as machine-translated. Those
  rows are excluded at import, but that is a property of the importer, not of the
  shard file.
- **Machine-generated** text is LLM-authored and unverified, and separable by
  filename.

Treat OCR Extracted, Books and MonDictDB as lower-confidence than the Wikipedia and
news shards if your use is sensitive to transcription accuracy.

## Contributing

1. Normalize all text to NFC before submission.
2. Record the source and its terms: a row in the Licence table above and in
   [LICENSE-CORPUS.md](LICENSE-CORPUS.md).
3. Add shards with `scripts/build_shards.py`, which deduplicates against the
   existing corpus and regenerates `shards/SHA256SUMS`. Run `--dry-run` first.
4. Run `make check`, then `make stats`, and update the Dataset table in the same
   change.

## Maintainers

[Janakh Pon](https://github.com/janakhpon) · [Htaw Mon](https://github.com/iammon) · [Barnista](https://github.com/Barnista)
