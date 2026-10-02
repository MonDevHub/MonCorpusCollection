# Books

Mon-language documents read from their PDF pages by OCR, kept as readable texts: one
folder per document, holding the text and a README with its source and known issues.
These are not shards. They are not deduplicated, clause-split or counted by `make stats`.

**Machine OCR, not proofread.** Every text carries the model's recognition errors.
**Terms: none established. Status: unresolved.** See [LICENSE-CORPUS.md](../LICENSE-CORPUS.md).

| Folder | Document | Author / origin | Pages | Characters | Myanmar script | Malformed lines | Mon-specific letters | OCR / text-layer yield |
| :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| [mnec-reform-paper-3-2019](mnec-reform-paper-3-2019/) | MNEC Reform Paper No 3, April 2019 | နာဲဗညာဟံသာ | 17 | 29,842 | 98.3% | 1.47% | 7.02% | 1.010 |
| [mnec-early-childhood-reform-paper-5-2019](mnec-early-childhood-reform-paper-5-2019/) | MNEC vs Mon Early Childhood Education Reform Paper No 5, 2019 | နာဲဗညာဟံသာ | 18 | 35,804 | 98.4% | 3.92% | 7.20% | 1.003 |
| [journal-of-mon-studies-guideline-2024](journal-of-mon-studies-guideline-2024/) | Journal of Mon Studies editorial guideline, amended 3 Nov 2024 | Mon National College | 4 | 5,956 | 95.7% | 4.95% | 5.56% | 1.022 |
| [gatui-mon-2](gatui-mon-2/) | လိက်ဂတဵုဇၞော်မန် ၂ | www.monlibrary.com | 17 | 15,034 | 97.8% | 2.55% | 4.91% | 1.015 |
| [mon-myanmar-dictionary-nai-tun-thein](mon-myanmar-dictionary-nai-tun-thein/) | မွန်-မြန်မာ အဘိဓာန် နှင့် သဒ္ဒါနှိုင်းယှဉ်ချက်, 2nd printing, March 2020 | နိုင်ထွန်းသိန်း, edited by နိုင်ပန်းလှ | 374 of 380 | 306,674 | 88.8% | not measured | 1.32% | not applicable (no text layer) |

The dictionary's Myanmar-script share is lower and its Mon-specific share much lower than the others because it is mostly Burmese definitions with dictionary punctuation, and its malformed-line and yield figures were not computed.

## Records

[`records.csv`](records.csv) is the metadata for every book, one row each, in the same order as the table above
and with more columns. `make books` fails if a folder has no row, a row has no folder, or the page and
character counts no longer match the text. Add the row in the same commit as the book.

| Column | Meaning |
| :--- | :--- |
| `slug`, `title_printed`, `title_english` | Folder name; the title as printed (Mon or Burmese script); an English rendering |
| `author`, `editor_or_origin`, `year` | As printed or as the PDF states. Blank means not identified, not "none" |
| `languages` | `mon`, `burmese`, `english`, joined with `+` |
| `source_file`, `source_sha256`, `source_text_layer` | The PDF it was read from, its checksum, and whether it already held text |
| `pages_pdf`, `pages_kept` | Pages in the PDF, and pages in the text (blank or unreadable pages are dropped; the README says which) |
| `characters`, `myanmar_share_pct`, `malformed_lines_pct`, `mon_specific_pct`, `text_layer_yield` | The figures defined below. Blank means not measured |
| `text_encoding` | The encoding of the text in this repository |
| `ocr_model`, `ocr_tool`, `extracted_on` | What read it, with which tool, and when |
| `review`, `error_rate` | How the text was checked, and the error rate if one was measured |
| `licence`, `notes` | The licence status, and anything else worth knowing |

**There is no per-line confidence.** The OCR model does not report one; what it returns for each line is
text and position. The honest measure of confidence here is `review`: `not recorded`, `spot-read by a
non-native reader`, or `spot-read by a Mon reader`, with `error_rate` filled in only when someone measured it.

**Characters** excludes whitespace and the `[page N]` marker lines, and is counted on the text files. The other measures are
taken on the OCR output before the header, footer, e-mail and watermark lines were removed:

- **Myanmar script** is the share of Myanmar-block characters once URL and running-header
  lines are excluded.
- **Malformed lines** fail a Mon well-formedness check.
- **Mon-specific letters** is the share of ၚ ၛ ၜ ၝ ၞ ၟ ၠ ဳ ဴ ဵ among Myanmar-block
  characters.
- **Yield** is OCR characters divided by the glyphs in the PDF's own text layer.

No line was found to be fused from several printed lines.
