# အနာဂတ်မန်ကၞပ်(၁၂)

- **Title as printed:** အနာဂတ်မန်ကၞပ်(၁၂) (Anagat Mon (Mon Future), issue 12). Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `အနာဂတ်မန်ကၞပ်(၁၂).pdf`.
- **Author / origin:** not identified
- **Source PDF SHA-256:** `f708a21487e77c41f61f9b535d27fa08a79bcf5d7bb1b4a039cad8ab2170056f`
- **Pages:** 206 in the PDF, 134 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**7** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**40** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

72 of 206: empty: 1-4, 9-17, 26, 33, 37, 40, 47, 51-52, 54, 56, 63-65, 80, 84, 87, 89-90, 103, 107, 109, 111, 115, 118-120, 129-130, 145-146, 155, 204-205; english: 5; garbled: 6, 27, 30, 39, 42, 48, 55, 62, 70, 77, 88, 91, 99-101, 106, 108, 113, 122, 127-128, 136, 148, 151, 153-154. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- A magazine issue. Forty English pages were read with Tesseract and are kept; one page the Mon model called English was a Mon contents table and is dropped.
