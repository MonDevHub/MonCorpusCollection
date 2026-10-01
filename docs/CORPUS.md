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
2026-08-12, **9,228 URLs remain** in the corpus, concentrated in two shards
(`wikipedia_shard_003.txt` 5,457 and `monnews_shard_001.txt` 3,715, with 52 in
`telegram_mot_tip_ebook_shard_001.txt` and 4 in `facebook_shard_001.txt`), while
`wikipedia_shard_001/002/004` instead carry orphan `"` lines where a "Retrieved from"
prefix was stripped. Treat the rules below as what new data goes through, and check a
shard before assuming it is clean.

1.  **Unusable-character removal**:
    - Strips Zero-Width Spaces (ZWSP), Zero-Width Joiners (ZWJ), Non-Joiners (ZWNJ), and Byte Order Marks (BOM).
    - Removes control codes (`\x00-\x1F`) and URLs.
2.  **Whitespace collapsing**:
    - Reduces runs of spaces to a single space and trims each line.
    - Documents are stored one sentence per line, separated by a single blank line.
      **Blank-line share varies too much to assume it**, measured 2026-08-12 by
      `scripts/data_quality.py`. Seven of the fifteen shards sit below 31%:
      `mondictdb_shard_001` (3 blank lines in 94,658, 0.0%),
      `gemini_generated_shard_001` (1 in 962, 0.1%), `handwritten_shard_001`
      (1 in 1,501, 0.1%), `custom_shard_001` (599 in 119,737, 0.5%),
      `wikipedia_shard_005` (5.3%), `ocr_extracted_shard_001` (7.1%) and
      `monnews_shard_003` (10.1%). The remaining eight run 32.0-49.8%. `mondictdb` is a
      flat lexical stream rather than prose, so splitting it on blank lines yields one
      7.5 MB document. Check a shard's blank-line ratio before treating blank lines as a
      document boundary.
3.  **Script preservation**:
    - Keeps all Mon, Burmese, and English mixed content. Nothing is dropped for being non-Mon.

## 3. Data Lifecycle

1.  **Raw scrapes**: original `.txt` files, one document each, from the scrapers (e.g. mon-corpus-scraper). Not stored in this repo.
2.  **Shards (`shards/`)**: the distribution format. `scripts/build_shards.py` cleans each document, deduplicates it against the existing corpus at the clause level, and packs the result into ~20 MB chunks. Existing shards are never modified.

## 4. Linguistic Constraints

- **Virama (U+1039)**: Preserved as it is structural for stacked characters.
- **Asat (U+103A)**: Preserved as it denotes syllable-final consonants.
- **Medials (U+103B–U+103E)**: Preserved as they are phonologically distinct.

## 5. Contact & Support
For issues regarding character normalization or potential data corruption, please open an issue in the main research repository.

## 6. Personal data

The corpus carries no email addresses and no mobile-number-shaped strings. This is a
policy, not an observation: `scripts/data_quality.py --check` exits non-zero if either
reappears, so it fails a build rather than producing a note nobody reads.

**What was removed.** A pass on 2026-08-12 removed 21 lines across six shards, listed in
[NEXT_STEPS.md](NEXT_STEPS.md). Whole lines, never masks — most of the material paired a
personal name with a number, and masking the number leaves the name and the association
intact. Where a removed line was its own document, one adjacent blank line went with it so
the document separator stayed single.

**What the check looks for.**

- Email addresses, by the ordinary `local@domain.tld` shape.
- Mobile-number shapes for the two dialling plans the sources use: Myanmar (`09…`,
  `+959…`) and Thailand (`0[689]…`, `0[2-7]…`). Deliberately not "any long digit run" —
  the corpus is full of ISBNs, DOIs, years and populations, and a loose pattern reports
  hundreds of matches, which makes it useless as a gate.
- **Both numeral systems.** Myanmar digits U+1040–U+1049 are not `\d`, so an ASCII-only
  scan reports a clean corpus while a number written `၀၉…` in Myanmar digits sits in it.
  Three of the removed numbers were written that way. This is the failure mode most likely to recur.

**What it does not find.** A name beside a number is the actual finding here, and pattern
scanning cannot see it — it only sees the number. The check is a floor, not a substitute
for reading a shard before importing it.

**Known non-matches, verified by inspection.** Nine ISBN-10s in `wikipedia_shard_001/002/
003/004` strip to ten digits beginning `09` and are excluded by the `ISBN` label on the
preceding line; one DOI, one astronomical value in AU, and one Zoom meeting ID are
excluded by shape. None is personal data.


---

## Frequency analyses

`results/latest/` holds character, bigram and trigram frequencies computed over the
tracked shards. It is reproducible:

```bash
python scripts/corpus_counter_normalized.py shards --output-dir results/latest --all-chars
```

Regenerated 2026-08-12 over all 15 tracked shards, after the PII redaction.

Its `total_raw_text_length` of 52,256,919 is a **character** count, not a byte count:
`len()` over the decoded UTF-8 text of the 15 shards. The byte count is 130,428,126,
2.49x larger, because Myanmar-script code points occupy three bytes each in UTF-8.
Both are reproducible:

```bash
python3 -c "from pathlib import Path; print(sum(len(p.read_text('utf-8')) for p in sorted(Path('shards').glob('*.txt'))))"
cat shards/*.txt | wc -c
```

Its `total_counted_characters` of 47,221,746 is the non-whitespace character count, and
matches the Characters total in the README's Dataset table exactly — that one is a
genuine cross-check between two independent scripts.

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


## Integrity

`shards/SHA256SUMS` carries a SHA-256 for every tracked shard. Verify a copy with the
standard tool:

```bash
cd shards && shasum -a 256 -c SHA256SUMS     # or sha256sum -c on Linux
```

This matters more than it looks. **Ten of the fifteen shards do not end in a newline**, so
"the file ends mid-token" is the normal state here and cannot be used to spot a truncated
download. Git's own object hashes protect a clone; they do nothing for a tarball, a partial
copy, or a shard fetched over a flaky link. `scripts/data_quality.py` reports the count.

`build_shards.py` regenerates it after a successful import. Regenerate by hand
only if you edited a shard outside the importer:

```bash
cd shards && shasum -a 256 *.txt > SHA256SUMS
```
