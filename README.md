# Mon Language Corpus Collection

A Mon-language text corpus for NLP research, language-model pretraining and OCR
training data. It is the training data source for
[MonOCR](https://github.com/MonDevHub/monocr).

Related: the [MonOCR model card](https://huggingface.co/janakhpon/monocr), the
[Mon tokenizer](https://github.com/Code-Yay-Mal/mon_tokenizer), the
[Mon language detector](https://github.com/janakhpon/mon-language-detector) and the
[awesome-mon-nlp](https://github.com/MonDevHub/awesome-mon-nlp) list.

**The corpus is not MIT, and seven of its nine sources have no established licence.**
Read [Licence](#licence) before redistributing any shard or book text.

## Dataset

| Source | Shards | Lines | Characters | Mon/Myanmar | Other |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mon Wikipedia** | 5 | 904,616 | 24,420,117 | 21,724,647 | 2,695,470 |
| **Mon News Agency** | 3 | 117,292 | 11,229,713 | 10,991,170 | 238,543 |
| **Custom Collections** | 1 | 119,737 | 6,831,335 | 3,681,830 | 3,149,505 |
| **MonDictDB** | 1 | 94,658 | 2,484,241 | 2,357,122 | 127,119 |
| **Telegram** | 1 | 2,271 | 54,638 | 48,941 | 5,697 |
| **Facebook** | 1 | 1,315 | 36,546 | 32,187 | 4,359 |
| **OCR Extracted** | 1 | 733 | 37,624 | 36,824 | 800 |
| **Handwritten** | 1 | 1,501 | 97,119 | 94,669 | 2,450 |
| **Machine-generated** | 1 | 962 | 23,142 | 21,567 | 1,575 |
| **Total** | **15** | **1,243,085** | **45,214,475** | **38,988,957 (86.2%)** | **6,225,518 (13.8%)** |

`make stats` (`scripts/shard_stats.py`) prints every cell. Raw size is 128,410,801
bytes, 122 MiB of uncompressed UTF-8 (`cat shards/*.txt | wc -c`).

- **Lines counts every newline,** including the blank line between documents.
  493,842 lines are blank (39.7%), leaving 749,243 with text, of which 53,154 are
  three characters or fewer. Budget for roughly 700K usable lines, not 1.24M. The
  character columns already exclude whitespace. `make quality` prints these counts.
- **Other is not noise.** Mon and Burmese are mixed in ordinary written use, so
  mixed-script text is kept as written. MonDictDB is the clearest case: Mon
  headwords with Burmese definitions.

## Data quality

`make quality` (`scripts/data_quality.py --check`) prints these figures and fails if
personal data reappears. [docs/CORPUS.md](docs/CORPUS.md) has the full datasheet.

- **Normalization.** All text is Unicode NFC. BOM, ZWJ, ZWNJ and control codes are
  stripped; all Myanmar script blocks (U+1000–U+109F, Extended-A/B) and intentional
  spacing are kept.
- **URLs remain in two older shards:** 56 in all, 52 in
  `telegram_mot_tip_ebook_shard_001` and 4 in `facebook_shard_001`.
- **Crawl logs are out of the text.** The scraper's lists of fetched pages had been
  packed in as text: 3,715 monnews URLs, 5,457 Wikipedia URLs and 879 Telegram
  message IDs. They now sit, sorted, in [`provenance/`](provenance/).
- **Personal data.** Every line holding an email address or a mobile-number-shaped
  string was removed (21 lines across six shards), whole rather than masked. The
  check scans ASCII and Myanmar numerals. **Earlier commits still contain the
  removed lines:** if you mirror or redistribute, take the current tree, not the
  history.
- **Duplication.** 94,006 of 369,898 eligible lines (25.4%) are redundant, and 4,542
  dedup keys (Mon-script skeletons) appear in more than one shard.
  `scripts/build_shards.py` dedupes new material against the corpus, but not the
  shards built before it. Breakdown in
  [docs/CORPUS.md](docs/CORPUS.md#3-how-shards-are-built).

**Do not split `shards/` into train and eval by file.** Roughly 4,500 skeletons
straddle any file boundary and inflate whatever you measure. Deduplicate across the
whole corpus first, then split.

## Books

[`books/`](books/) holds sixteen documents read by OCR (fifteen in Mon, one in
English; two are printings of one dictionary), one folder each, kept as page-by-page
texts rather than shards. They are machine OCR, not proofread, and their terms are
unresolved. `make stats`, `make quality` and `results/latest/` cover the shards only,
so none of the figures above include them.

## Structure

```text
MonCorpusCollection/
├── shards/           # <source>_shard_NNN.txt, up to ~20 MB each, plus SHA256SUMS
├── provenance/       # Fetched-page URL and message-ID lists (Wikipedia, IMNA, Telegram), not text
├── books/            # OCR-read Mon documents, one folder each (not shards)
├── results/latest/   # Character/bigram/trigram frequency over the shards
├── scripts/          # stdlib-only Python: stats, quality, import, counters
└── docs/CORPUS.md    # Datasheet: sources, build, cleaning, limitations
```

The shard filename prefix names the source; the [Licence](#licence) table maps each
prefix to its origin and terms.

## Usage

The scripts use only the Python standard library and need Python 3.10 or newer.

Each shard is UTF-8 text, one segment per line. Do not treat a blank line as a
document boundary everywhere: `mondictdb_shard_001` has 3 in 94,658 lines, and
[docs/CORPUS.md](docs/CORPUS.md#2-file-format) lists the other low ones.

```bash
make stats         # per-source table above
make verify        # shards against shards/SHA256SUMS, including coverage
make quality       # data-quality figures and the personal-data gate
make books         # books/records.csv agrees with the book folders
make check         # verify + quality + books + lint
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
| Books | `books/` | Sixteen OCR-read documents; sources in [books/README.md](books/README.md) | **Unresolved** |

Only the Wikipedia and MonDictDB shards are covered, under CC BY-SA 4.0 and MIT.
Redistributing any **Unresolved** shard or book text is not covered by anything in
this repository. Attribute **Mon Corpus Collection** and the underlying source of
each shard or book you use. For the Wikipedia shards, use the CC BY-SA 4.0
attribution and list of changes in [LICENSE-CORPUS.md](LICENSE-CORPUS.md#cc-by-sa-40-attribution-for-wikipedia_shard_),
and [`provenance/wikipedia_urls.txt`](provenance/wikipedia_urls.txt) for the article
URLs that survive.

### Confidence by source

If your use is sensitive to transcription accuracy, treat OCR Extracted, Books and
MonDictDB as lower-confidence than the Wikipedia and news shards.

- **Handwritten** is the cleanest material here: no scraping artefacts, recognition
  errors or machine-authored text. It is the best start for a clean evaluation or
  fine-tuning slice once the writer's grant is recorded; until then its terms are
  unresolved. MonOCR's training text already includes it, so it is not held out from
  MonOCR. Import measurements are in [docs/CORPUS.md](docs/CORPUS.md#1-sources).
- **OCR Extracted** can carry the recognition errors of the OCR system that read it.
- **Books** are machine OCR, not proofread; each book's README lists its known errors.
- **MonDictDB** upstream marks some definitions as machine-translated. Those rows
  were excluded at import; that is a property of the importer, not of the shard file.
- **Machine-generated** text is LLM-authored and unverified, and separable by filename.

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
