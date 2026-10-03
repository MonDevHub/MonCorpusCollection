# လျးရတ်တၟိကၞပ်(၆)

- **Title as printed:** လျးရတ်တၟိကၞပ်(၆). Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `လျးရတ်တၟိကၞပ်(၆) .pdf`.
- **Author / origin:** not identified. Year: 2011
- **Source PDF SHA-256:** `c5f58566a2224cdefbd7d15bd93bd4616d3493a74b5ddbb59f6aea04b365c8f6`
- **Pages:** 222 in the PDF, 130 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**11** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**0** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

92 of 222: empty: 1-2, 8, 18, 23, 25, 27-28, 35, 37, 43, 49, 51, 53, 57, 63-64, 73, 78, 81, 85, 95, 97, 104-105, 108, 110-111, 119, 125-127, 135, 138, 140, 142-143, 152, 158-159, 164, 166, 169, 172, 175-177, 191, 198, 217, 220, 222; garbled: 7, 9-12, 16, 33, 45-46, 52, 56, 88, 96, 99, 103, 106-107, 109, 112-113, 121-122, 124, 129, 132, 139, 144, 162, 165, 168, 170, 173, 179, 195, 201, 210-212, 221; symbols: 101. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- A periodical issue. The first page, as the OCR read it, gives July 2011 and Buddhist era 2555; not checked against the printed page.
