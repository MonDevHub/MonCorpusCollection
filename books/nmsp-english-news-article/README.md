# Union-level Peace-making group and NMSP ink initial peace deal

- **Title as printed:** Union-level Peace-making group and NMSP ink initial peace deal. Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `NMSP by BHS 1997  in Mon.pdf`.
- **Author / origin:** not identified; New Light of Myanmar, 27 February 2012. Year: 2012
- **Source PDF SHA-256:** `8e11d1b4bf56f075a481a8a76296e8c4a71637d6ac732cee80c55fa5351b805b`
- **Pages:** 8 in the PDF, 3 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode; English pages: Tesseract eng), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**0** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**3** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

5 of 8: garbled: 1-5. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- The PDF's file name is NMSP by BHS 1997 in Mon. Only pages 6 to 8 could be read: an English news article, read with Tesseract. Pages 1 to 5, in Mon, read as garbled on both reads and are dropped.
