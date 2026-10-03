# Mon Youth Progressive Journal-Volume (11)

- **Title as printed:** Mon Youth Progressive Journal-Volume (11) (Mon Youth Progressive Journal, volume 11). Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `mypo journal11 (1).pdf`.
- **Author / origin:** not identified. Year: 2006
- **Source PDF SHA-256:** `52120981868ef7160133e93a4444a5cbe0cf3a6ad5c799206de7cd085ea20e77`
- **Pages:** 24 in the PDF, 23 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**0** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**0** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

1 of 24: garbled: 12. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- The contents page, as the OCR read it, is dated September 2006; the PDF was created in October 2006.
