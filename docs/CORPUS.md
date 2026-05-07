# Mon Corpus Technical Specification

This document details the technical standards, normalization rules, and cleaning philosophy used to produce the Mon Language Corpus.

## 1. Normalization Standards

### Unicode NFC (Normal Form C)
The Mon script relies heavily on combining marks and stacked consonants. To ensure interoperability between different tokenizers and models, we enforce **NFC** normalization. 

**Example transition:**
- `U+1000` (က) + `U+1039` (္) + `U+1000` (က) remains consistent as a single cluster sequence in NFC.
- Decomposed sequences (NFD) are automatically converted to their canonical composed forms during the `clean` and `wrangle` phases.

### Character Substitutions
While we avoid aggressive character stripping, we normalize certain variations for better analysis:
- **Mon 'Nga' (ၚ)**: Often incorrectly typed as the Burmese 'Nga' (င) + a combining mark. Our pipeline detects and normalizes these to the correct Mon-specific Unicode character `U+1021` (ၚ) where appropriate for linguistic consistency.

## 2. Cleaning Philosophy: "Balanced Fidelity"

Our cleaning engine (`shared/cleaning.py`) follows a **High-Fidelity** approach:

1.  **Invisible Noise Removal**: 
    - Strips Zero-Width Spaces (ZWSP), Zero-Width Joiners (ZWJ), and Non-Joiners (ZWNJ).
    - Removes Byte Order Marks (BOM) and legacy control codes (`\x00-\x1F`).
2.  **Whitespace Collapsing**:
    - Reduces 2+ consecutive spaces to 1.
    - Reduces 3+ consecutive newlines to 2 (max one blank line between paragraphs).
3.  **Script Preservation**:
    - Explicitly preserves all characters in the Myanmar block (`U+1000` to `U+109F`).
    - Preserves basic Latin and standard punctuation to maintain context for multi-lingual or code-mixed samples.

## 3. Data Lifecycle

The corpus follows a strict lifecycle to ensure reproducibility:

1.  **Raw (`data/raw/`)**: Original, untouched scrapes with all UI noise and artifacts.
2.  **Cleaned (`data/cleaned/`)**: Mirrors raw structure but applies `clean_fidelity`. Used for human auditing.
3.  **Shards (`shards/`)**: The final distribution format. Globally deduplicated and packed into 20MB chunks.

## 4. Linguistic Constraints

- **Virama (U+1039)**: Preserved as it is structural for stacked characters.
- **Asat (U+103A)**: Preserved as it denotes syllable-final consonants.
- **Medials (U+103B–U+103E)**: Preserved as they are phonologically distinct.

## 5. Contact & Support
For issues regarding character normalization or potential data corruption, please open an issue in the main research repository.
