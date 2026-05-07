# Mon Language (mnw) Corpus Collection

A high-fidelity, production-grade corpus of the Mon language, curated for NLP research, LLM pre-training, and OCR model development. This repository provides consolidated training shards derived from a diverse range of digital Mon script sources.

## Dataset Overview

The corpus is distributed in **training-ready shards** to facilitate high-throughput machine learning workflows.

| Source Category         | Shards | Lines         | Characters     | Mon/Myanmar            | Other (Eng/Digits)    |
| ----------------------- | ------ | ------------- | -------------- | ---------------------- | --------------------- |
| **Mon Wikipedia**       | 4      | 891,665       | 24,676,307     | 21,037,957             | 3,638,350             |
| **Mon News Agency**     | 2      | 107,882       | 11,310,762     | 10,260,088             | 1,050,674             |
| **Custom Collections**  | 1      | 119,739       | 6,831,401      | 3,681,874              | 3,149,527             |
| **Telegram / Facebook** | 2      | 4,479         | 95,098         | 81,479                 | 13,619                |
| **OCR Extracted**       | 1      | 733           | 37,624         | 36,824                 | 800                   |
| **Total**               | **10** | **1,124,998** | **42,951,192** | **35,098,222 (81.7%)** | **7,852,970 (18.3%)** |

### Statistical Summary

- **Total Lines**: 1,124,998
- **Total Characters (Unicode)**: 42,951,192
- **Mon/Myanmar Characters**: 35,098,222
- **Raw File Size**: ~113 MB (Uncompressed UTF-8)

## Project Structure

```text
MonCorpusCollection/
├── shards/                 # Consolidated training shards (20MB each)
│   ├── monnews_shard_*.txt # Mon News Agency articles
│   ├── wikipedia_shard_*.txt # Mon Wikipedia articles
│   ├── telegram_shard_*.txt # Curated Telegram messages
│   └── custom_shard_*.txt  # Specialized and legacy collections
├── results/                # Analysis reports and statistics
│   └── latest/             # Latest character frequency and bigram/trigram stats
├── scripts/                # Utility scripts for corpus analysis
├── README.md               # Project overview (Last Update: 2026-05-07)
└── AGENTS.md               # Engineering standards and context
```

## Dataset Characteristics

### 1. High Fidelity

We prioritize the preservation of the Mon language's digital footprint. Unlike generic cleaners that strip "unknown" characters, our pipeline:

- Preserves all Myanmar script blocks (U+1000–U+109F, Extended-A/B).
- Maintains intentional spacing essential for Mon script readability.
- Strips only non-linguistic digital noise (BOM, ZWJ, ZWNJ, and control codes).

### 2. Unicode Normalization (NFC)

All text in this repository is strictly normalized to **Unicode NFC (Normal Form C)**. This ensures that grapheme clusters are represented consistently, regardless of the original input method or source platform.

### 3. Global Deduplication

The content within the `shards/` directory has been globally deduplicated. A document appearing in one shard will not appear in another, preventing data leakage during model training and evaluation.

## Getting Started

### Data Ingestion

For model training, simply iterate through the `shards/` directory. Each file is a standard UTF-8 text file.

### Analysis

Run the provided scripts to generate character frequency reports or script cluster analysis:

```bash
python scripts/mon_cluster_counter.py
```

## License and Attribution

This corpus is released under the **MIT License**.

If you use this data in your research or applications, please attribute the **Mon Corpus Collection** and the original sources:

- **Mon News Agency (IMNA)**
- **Mon Wikipedia**

## Contributing

We welcome contributions to expand the Mon language digital corpus. Please follow these guidelines:

1. **Normalization**: Ensure all text is **NFC normalized** before submission.
2. **Attribution**: Provide clear source attribution for all new data collections.

### Contributors

- **Janakh Pon** ([GitHub](https://github.com/janakhpon))
- **Htaw Mon** ([GitHub](https://github.com/iammon))

---

Maintained as part of the Mon AI Research project. Built for the community.
