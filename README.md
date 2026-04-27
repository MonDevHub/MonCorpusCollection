# Mon Corpus Collection

A repository of Mon language (mnw) text data for NLP research, linguistic analysis, and model training.

## Corpus Statistics

The collection contains data from news, encyclopedia entries, and social media.

### Overview (2026-04-27)

| Metric | Value |
| :--- | :--- |
| Total Files | 8,783 |
| Mon-related Characters | 29,407,428 |
| Raw Text Length | 36,586,341 |
| Language | Mon (mnw) |
| Script | Mon/Burmese Unicode |

### Public Dataset (Open Source)

| Source | Files | Mon Chars | Content Type |
| :--- | :---: | :---: | :--- |
| Wikipedia | 4,208 | 18,966,185 | Encyclopedia articles |
| Mon News Agency | 3,682 | 10,229,891 | News and interviews |
| Telegram | 889 | 53,131 | Public social media |
| **Total Public** | **8,779** | **29,249,207** | **Open Data Collection** |

### Additional Sources

| Source | Files | Mon Chars | Content Type |
| :--- | :---: | :---: | :--- |
| Custom Collections | 4 | 158,221 | Curated/Miscellaneous |

## Technical Specifications

### Encoding and Normalization
- **Encoding**: UTF-8.
- **Unicode Blocks**: Myanmar block (U+1000–U+109F) and extended blocks.
- **Normalization**: NFC normalization is required for all data.
- **Linguistic Variants**: Distinguishes between standard Myanmar characters and Mon-specific variants (e.g., ၚ U+1021 vs င U+1004).

### Data Quality
- Metadata and UI boilerplate are removed during extraction.
- Files under 50 characters are excluded from the core collection.

## Project Structure

```text
.
├── monnews/               # Mon News Agency (IMNA) data
├── wikipedia/             # Mon Wikipedia data
├── telegram_mot_tip/      # Telegram channel messages
├── custom/                # Curated and legacy data
├── results/               # Analysis outputs (CSV/JSON)
├── AGENTS.md              # Engineering standards and role context
└── corpus_counter.py      # Corpus analysis utility
```

## Usage

### Analyzing the Corpus
Use the analysis script to generate character and n-gram statistics.

```bash
# Basic analysis
python3 corpus_counter_normalized.py . --output-dir results

# Analysis with Mon-specific Nga normalization (င -> ၚ)
python3 corpus_counter_normalized.py . --output-dir results --normalize-mon-nga
```

### Core Scripts
- `corpus_counter_normalized.py`: Calculates character, bigram, and trigram frequencies.
- `mon_cluster_counter.py`: Analyzes grapheme clusters.

## License and Attribution

This corpus is released under the MIT License.

If you use this data, attribute the Mon Corpus Collection and the original sources (IMNA, Wikipedia).

## Contributing

1. Ensure all text is NFC normalized.
2. Follow the character standards defined in AGENTS.md.
3. Provide source attribution for new data.

Contributors: Janakh Pon, Htaw Mon
