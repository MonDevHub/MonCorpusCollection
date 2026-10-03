# Mon Education Reform 2014 BHS to MNEC

- **Title:** Mon Education Reform 2014 BHS to MNEC, taken from the PDF's file name `Mon Education Reform 2014 BHS to MNEC  (1).pdf`; the printed title page was not read.
- **Author / origin:** နာဲဗညာဟံသာ. Year: 2014
- **Source PDF SHA-256:** `e9b983e039222bcf6374d8371a15eee3ba96c314d74df54cb99b5f64d126eb67`
- **Pages:** 14 in the PDF, 13 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**1** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**0** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

1 of 14: empty: 1. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- Title taken from the file name. The text layer's cover gives ၁၃၇၆ (2014). A second PDF in the archive, MNEC vs Policy နာဲဗညာဟံသာ (၁).pdf, has the same contents page for page and was not added as a duplicate.
