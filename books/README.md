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

**Characters** excludes whitespace and the `[page N]` marker lines, and is counted on the text files. The other measures are
taken on the OCR output before the header, footer, e-mail and watermark lines were removed:

- **Myanmar script** is the share of Myanmar-block characters once URL and running-header
  lines are excluded.
- **Malformed lines** fail a Mon well-formedness check.
- **Mon-specific letters** is the share of ၚ ၛ ၜ ၝ ၞ ၟ ၠ ဳ ဴ ဵ among Myanmar-block
  characters.
- **Yield** is OCR characters divided by the glyphs in the PDF's own text layer.

No line was found to be fused from several printed lines.
