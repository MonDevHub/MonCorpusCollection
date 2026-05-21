# Mon Language Corpus Collection

Mon is spoken by roughly one million people across Myanmar and Thailand. [UNESCO classifies it as vulnerable](https://en.wikipedia.org/wiki/Atlas_of_the_World%27s_Languages_in_Danger) — and before this project, no NLP-grade corpus existed for it.

This is a production-grade corpus of the Mon language, curated for NLP research, LLM pre-training, and OCR model development. It is the training data source for [MonOCR](https://github.com/MonDevHub/monocr).

---

## Dataset

| Source | Shards | Lines | Characters | Mon/Myanmar | Other |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mon Wikipedia** | 4 | 891,665 | 24,676,307 | 21,037,957 | 3,638,350 |
| **Mon News Agency** | 2 | 107,882 | 11,310,762 | 10,260,088 | 1,050,674 |
| **Custom Collections** | 1 | 119,739 | 6,831,401 | 3,681,874 | 3,149,527 |
| **Telegram / Facebook** | 2 | 4,479 | 95,098 | 81,479 | 13,619 |
| **OCR Extracted** | 1 | 733 | 37,624 | 36,824 | 800 |
| **Total** | **10** | **1,124,998** | **42,951,192** | **35,098,222 (81.7%)** | **7,852,970 (18.3%)** |

Raw file size: ~113 MB (uncompressed UTF-8)

---

## Data Quality

**Unicode NFC normalization** — All text is strictly normalized to NFC, ensuring consistent grapheme cluster representation regardless of input method or source platform.

**Preservation pipeline** — The pipeline preserves all Myanmar script blocks (U+1000–U+109F, Extended-A/B) and intentional spacing essential to Mon script readability. Only non-linguistic noise is stripped (BOM, ZWJ, ZWNJ, control codes).

**Global deduplication** — Content across all shards is globally deduplicated. A document in one shard will not appear in another, preventing data leakage between training and evaluation splits.

---

## Structure

```text
MonCorpusCollection/
├── shards/                   # Training shards (~20MB each)
│   ├── monnews_shard_*.txt   # Mon News Agency articles
│   ├── wikipedia_shard_*.txt # Mon Wikipedia articles
│   ├── telegram_shard_*.txt  # Curated Telegram messages
│   └── custom_shard_*.txt    # Specialized and legacy collections
├── results/latest/           # Character frequency and bigram/trigram stats
├── scripts/                  # Corpus analysis utilities
└── README.md
```

---

## Usage

Iterate through `shards/` for model training. Each file is standard UTF-8 text.

```bash
# Generate character frequency report
python scripts/mon_cluster_counter.py
```

---

## License

MIT. If you use this data, please attribute **Mon Corpus Collection** and the original sources: **Mon News Agency (IMNA)** and **Mon Wikipedia**.

---

## Contributing

1. Normalize all text to NFC before submission.
2. Provide clear source attribution for new data.

[Janakh Pon](https://github.com/janakhpon) · [Htaw Mon](https://github.com/iammon)
