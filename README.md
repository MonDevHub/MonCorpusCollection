# Mon Language Corpus Collection

Mon is spoken by roughly one million people across Myanmar and Thailand and is [classified by UNESCO as vulnerable](https://en.wikipedia.org/wiki/Atlas_of_the_World%27s_Languages_in_Danger). Usable NLP corpora for it remain scarce.

This is a Mon-language text corpus for NLP research, language-model pretraining, and OCR training data. It is the training data source for [MonOCR](https://github.com/MonDevHub/monocr).

---

## Dataset

| Source | Shards | Lines | Characters | Mon/Myanmar | Other |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mon Wikipedia** | 5 | 910,080 | 25,590,114 | 21,725,259 | 3,864,855 |
| **Mon News Agency** | 3 | 121,020 | 12,066,365 | 10,993,107 | 1,073,258 |
| **Custom Collections** | 1 | 119,739 | 6,831,401 | 3,681,874 | 3,149,527 |
| **MonDictDB** | 1 | 94,658 | 2,484,241 | 2,357,122 | 127,119 |
| **Telegram / Facebook** | 2 | 4,479 | 95,098 | 81,479 | 13,619 |
| **OCR Extracted** | 1 | 733 | 37,624 | 36,824 | 800 |
| **Handwritten** | 1 | 1,501 | 97,119 | 94,669 | 2,450 |
| **Machine-generated** | 1 | 962 | 23,142 | 21,567 | 1,575 |
| **Total** | **15** | **1,253,172** | **47,225,104** | **38,991,901 (82.6%)** | **8,233,203 (17.4%)** |

Raw file size: ~124 MB (uncompressed UTF-8). Verify a copy with
`cd shards && shasum -a 256 -c SHA256SUMS`.

**What the Lines column counts.** Every newline, including the blank line that separates
documents. Measured over the 15 tracked shards on 2026-08-08: of 1,253,172 lines,
**493,857 are blank — 39.4%**, leaving 759,315 with text on them, of which 53,275 are three
characters or fewer. Budget for roughly 700K usable text lines rather than 1.25M. The
character columns are unaffected: they already exclude whitespace.

The **Other** column is not noise to be filtered out. Mon and Burmese are mixed in
ordinary written use, and any system reading real pages will meet them together —
so mixed-script material is kept as it appears rather than separated. The
MonDictDB shard is the clearest case: Mon headwords with Burmese definitions, kept
whole.

---

## Data Quality

**Unicode NFC normalization** — All text is strictly normalized to NFC, ensuring consistent grapheme cluster representation regardless of input method or source platform.

**Preservation pipeline** — The pipeline preserves all Myanmar script blocks (U+1000–U+109F, Extended-A/B) and intentional spacing essential to Mon script readability. Only non-linguistic noise is stripped (BOM, ZWJ, ZWNJ, control codes).

**Deduplication** — New content is deduplicated against the existing corpus at the sentence level (Mon-script skeleton) before it is added, so re-scraped material is not appended twice. That applies to content added through `scripts/build_shards.py`; it does not retroactively dedupe shards built before it.

Measured 2026-08-08 over the 15 tracked shards, using this repo's own dedup key: of
369,913 dedup-eligible lines, **94,007 are redundant instances — 25.4%**. The duplicates
are not short: median 63 characters across the 35,157 distinct skeletons that repeat,
longest 2,575. **4,542 distinct skeletons appear in more than one shard.**

`handwritten_shard_001` contributed 1,094 of those eligible lines and **not one
duplicate** — every redundancy figure above is identical with and without it. It is the
only shard of which that is true, which is what composed-not-collected buys.

The practical consequence: **do not split `shards/` into train and eval by file.** Roughly
4,500 sentence skeletons straddle any such boundary, which silently inflates whatever you
measure. Deduplicate across the whole corpus first, then split.

---

## Structure

```text
MonCorpusCollection/
├── shards/                        # Distribution shards (~20MB each)
│   ├── monnews_shard_*.txt        # Mon News Agency (IMNA) articles
│   ├── wikipedia_shard_*.txt      # Mon Wikipedia articles
│   ├── telegram_*_shard_*.txt     # Telegram channel messages
│   ├── facebook_shard_*.txt       # Facebook page posts
│   ├── mondictdb_shard_*.txt      # MonDictDB dictionary entries and examples
│   ├── gemini_generated_shard_*.txt  # LLM-authored, unverified — see below
│   ├── ocr_extracted_shard_*.txt  # OCR-extracted text
│   └── custom_shard_*.txt         # Specialized and legacy collections
├── results/latest/                # Character/bigram/trigram frequency over the shards
├── scripts/                       # build_shards.py, shard_stats.py, frequency counters
└── docs/CORPUS.md                 # Cleaning and normalization spec
```

---

## Usage

Iterate through `shards/` for model training. Each file is standard UTF-8 text.

```bash
# Per-source stats (shards, lines, characters, Mon/Myanmar share)
python scripts/shard_stats.py

# Character / bigram / trigram frequency over all shards
python scripts/corpus_counter_normalized.py shards --output-dir results/latest --all-chars

# Add newly scraped .txt files as deduplicated shards (dry-run first)
python scripts/build_shards.py --source monnews --input path/to/monnews --dry-run
```

---

## Sources and Attribution

**The corpus is not MIT.** MIT covers `scripts/` and the `Makefile` only — see
[LICENSE](LICENSE). The text in `shards/` and the tables in `results/` carry the
terms of whatever they were drawn from, set out per source in
[LICENSE-CORPUS.md](LICENSE-CORPUS.md).

Mon Wikipedia is CC BY-SA 4.0 and MonDictDB is MIT. Six of the eight sources are
unresolved, and redistributing those is not covered by anything in this
repository. Attribute **Mon Corpus Collection** and the underlying source below —
every shard traces to one of them.

| Source | Shards | Origin |
| :--- | :--- | :--- |
| Mon Wikipedia | `wikipedia_shard_*` | [mnw.wikipedia.org](https://mnw.wikipedia.org), CC BY-SA |
| Mon News Agency (IMNA) | `monnews_shard_*` | [Independent Mon News Agency](https://monnews.org) |
| MonDictDB | `mondictdb_shard_*` | [MonDictDB](https://github.com/Barnista/MonDictDB) by [Barnista](https://github.com/Barnista), MIT |
| Handwritten | `handwritten_shard_*` | Composed directly in Mon by a native writer — not scraped, not transcribed, not generated |
| Custom Collections | `custom_shard_*` | Specialized and legacy collections |
| Telegram / Facebook | `telegram_*`, `facebook_shard_*` | Public channel and page posts |
| OCR Extracted | `ocr_extracted_shard_*` | Text recovered from scanned material |
| Machine-generated | `gemini_generated_shard_*` | Authored by Google Gemini, not transcribed from any source |

> **On the handwritten shard.** `handwritten_shard_*` is the highest-confidence
> material here: composed directly in Mon by a native writer, so it carries no
> scraping artefacts, no recognition errors and no machine-authored text. Measured
> against the rest of the corpus at import: **97.5% Mon script**, **0.014%
> malformed tokens** (the corpus bar is 1.0%), zero URLs, and a mean charset
> survival of 0.9985 with no line below 0.50. If you need a clean evaluation or
> fine-tuning slice, start here.
>
> **On the OCR-extracted and MonDictDB shards.** `ocr_extracted_shard_*` is the
> output of an OCR system, so it can carry that system's recognition errors.
> MonDictDB records some definitions produced by machine translation; those rows
> are excluded at import, but the exclusion is a property of the importer rather
> than of this file. Treat both as lower-confidence than the Wikipedia and news
> shards if your use is sensitive to transcription accuracy.

---

## Contributing

1. Normalize all text to NFC before submission.
2. Provide clear source attribution for new data, and add a row to the table above.
3. Add shards with `scripts/build_shards.py`, which deduplicates against the
   existing corpus. Run `--dry-run` first.
4. Re-run `scripts/shard_stats.py` and update the Dataset table in the same change.

## Maintainers

[Janakh Pon](https://github.com/janakhpon) · [Htaw Mon](https://github.com/iammon) · [Barnista](https://github.com/Barnista)
