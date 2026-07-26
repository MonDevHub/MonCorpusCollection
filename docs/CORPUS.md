# Mon Corpus Technical Specification

This document details the technical standards, normalization rules, and cleaning philosophy used to produce the Mon Language Corpus.

## 1. Normalization Standards

### Unicode NFC (Normal Form C)
The Mon script relies heavily on combining marks and stacked consonants. To ensure interoperability between different tokenizers and models, we enforce **NFC** normalization. 

**Example transition:**
- `U+1000` (က) + `U+1039` (္) + `U+1000` (က) remains consistent as a single cluster sequence in NFC.
- Decomposed sequences (NFD) are converted to their canonical composed forms during cleaning.

### Character Substitutions
The analysis tooling can optionally normalize certain variations:
- **Mon 'Nga' (ၚ)**: sometimes typed as the Burmese 'Nga' (`င`, `U+1004`). `corpus_counter_normalized.py --normalize-mon-nga` maps `င` (`U+1004`) to the Mon-specific `ၚ` (`U+105A`) for linguistic consistency. This is an analysis option, not an irreversible change to the source shards.

## 2. Cleaning Philosophy

New data is added to `shards/` with `scripts/build_shards.py`, which applies minimal cleaning:

1.  **Unusable-character removal**:
    - Strips Zero-Width Spaces (ZWSP), Zero-Width Joiners (ZWJ), Non-Joiners (ZWNJ), and Byte Order Marks (BOM).
    - Removes control codes (`\x00-\x1F`) and URLs.
2.  **Whitespace collapsing**:
    - Reduces runs of spaces to a single space and trims each line.
    - Documents are stored one sentence per line, separated by a single blank line.
3.  **Script preservation**:
    - Keeps all Mon, Burmese, and English mixed content. Nothing is dropped for being non-Mon.

## 3. Data Lifecycle

1.  **Raw scrapes**: original `.txt` files, one document each, from the scrapers (e.g. mon-corpus-scraper). Not stored in this repo.
2.  **Shards (`shards/`)**: the distribution format. `scripts/build_shards.py` cleans each document, deduplicates it against the existing corpus at the sentence level, and packs the result into ~20 MB chunks. Existing shards are never modified.

## 4. Linguistic Constraints

- **Virama (U+1039)**: Preserved as it is structural for stacked characters.
- **Asat (U+103A)**: Preserved as it denotes syllable-final consonants.
- **Medials (U+103B–U+103E)**: Preserved as they are phonologically distinct.

## 5. Contact & Support
For issues regarding character normalization or potential data corruption, please open an issue in the main research repository.
