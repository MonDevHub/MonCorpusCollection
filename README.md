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
| **Telegram / Facebook** | 2 | 4,479 | 95,098 | 81,479 | 13,619 |
| **OCR Extracted** | 1 | 733 | 37,624 | 36,824 | 800 |
| **Total** | **12** | **1,156,051** | **44,620,602** | **36,518,543 (81.8%)** | **8,102,059 (18.2%)** |

Raw file size: ~117 MB (uncompressed UTF-8)

---

## Data Quality

**Unicode NFC normalization** — All text is strictly normalized to NFC, ensuring consistent grapheme cluster representation regardless of input method or source platform.

**Preservation pipeline** — The pipeline preserves all Myanmar script blocks (U+1000–U+109F, Extended-A/B) and intentional spacing essential to Mon script readability. Only non-linguistic noise is stripped (BOM, ZWJ, ZWNJ, control codes).

**Deduplication** — New content is deduplicated against the existing corpus at the sentence level (Mon-script skeleton) before it is added, so re-scraped material is not appended twice. A small number of short segments still recur across shards, so treat shard boundaries as packaging rather than guaranteed dedup splits.

---

## Structure

```text
MonCorpusCollection/
├── shards/                        # Distribution shards (~20MB each)
│   ├── monnews_shard_*.txt        # Mon News Agency (IMNA) articles
│   ├── wikipedia_shard_*.txt      # Mon Wikipedia articles
│   ├── telegram_*_shard_*.txt     # Telegram channel messages
│   ├── facebook_shard_*.txt       # Facebook page posts
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

## License

MIT. If you use this data, please attribute **Mon Corpus Collection** and the original sources: **Mon News Agency (IMNA)** and **Mon Wikipedia**.

---

## Contributing

1. Normalize all text to NFC before submission.
2. Provide clear source attribution for new data.

[Janakh Pon](https://github.com/janakhpon) · [Htaw Mon](https://github.com/iammon)
