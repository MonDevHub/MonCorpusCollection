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

New data is added to `shards/` with `scripts/build_shards.py`, which applies minimal cleaning.

**This section describes the importer, not every shard on disk.** `build_shards.py` dates
from 2026-07-26; most shards were built before it and did not pass through it. Measured
2026-08-08, **9,228 URLs remain** in the corpus, concentrated in two shards
(`wikipedia_shard_003.txt` 5,457 and `monnews_shard_001.txt` 3,715), while
`wikipedia_shard_001/002/004` instead carry orphan `"` lines where a "Retrieved from"
prefix was stripped. Treat the rules below as what new data goes through, and check a
shard before assuming it is clean.

1.  **Unusable-character removal**:
    - Strips Zero-Width Spaces (ZWSP), Zero-Width Joiners (ZWJ), Non-Joiners (ZWNJ), and Byte Order Marks (BOM).
    - Removes control codes (`\x00-\x1F`) and URLs.
2.  **Whitespace collapsing**:
    - Reduces runs of spaces to a single space and trims each line.
    - Documents are stored one sentence per line, separated by a single blank line.
      **Three shards do not follow this**, measured 2026-08-08: `mondictdb_shard_001`
      (4 blank lines in 94,659), `gemini_generated_shard_001` (2 in 963) and
      `custom_shard_001` (599 in 119,740, 0.5%). The rest sit at 31-50%. `mondictdb` is a
      flat lexical stream rather than prose, so splitting it on blank lines yields one
      7.5 MB document. Check a shard's blank-line ratio before treating blank lines as a
      document boundary.
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


---

## Frequency analyses

`results/latest/` holds character, bigram and trigram frequencies computed over the
tracked shards. It is reproducible:

```bash
python scripts/corpus_counter_normalized.py shards --output-dir results/latest --all-chars
```

Its `total_raw_text_length` of 52,156,464 matches an independent byte count of the tracked
shards exactly.

### The removed `--normalize-mon-nga` trees (2026-08-08)

Four other trees used to sit under `results/` — the root CSVs plus `custom/`, `monnews/`,
`telegram/` and `wikipedia/`. They were removed because they described a different corpus
and were silently misleading.

They were generated from **8,823 raw scraper files that are not in this repository**, with
`--normalize-mon-nga` enabled, which rewrote **438,900 instances of `င` (U+1004, Burmese
NGA) into `ၚ` (U+105A, Mon NGA)**. Nothing in the output recorded that. The consequence:

| file | `င` U+1004 | `ၚ` U+105A |
| :--- | ---: | ---: |
| removed `results/character_frequency.csv` | **row absent entirely** | 1,143,707 |
| current `results/latest/character_frequency.csv` | 579,086 | 900,749 |

A reader of the removed file would conclude that Burmese NGA does not occur in Mon text.
It does, 579,086 times in the tracked shards.

The underlying question is real and worth revisiting: Burmese NGA appears where Mon NGA is
expected often enough that a normalization pass found 438,900 candidates. That is a
linguistic finding about the source material. It is recorded here rather than left in an
undocumented CSV that states it wrongly. The files remain in git history.
