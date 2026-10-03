# မွန် - မြန်မာ အဘိဓါန် နှင့် သဒ္ဒါနှိုင်းယှဉ်ချက်

- **Title as printed:** မွန် - မြန်မာ အဘိဓါန် နှင့် သဒ္ဒါနှိုင်းယှဉ်ချက် (Mon-Myanmar Dictionary and Grammar Comparison). Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `Mon-Myanmar Dictionary.pdf`.
- **Author / origin:** နိုင်ထွန်းသိန်း (Nai Tun Thein); edited by ဒေါက်တာ နိုင်ပန်းလှ (Nai Pan Hla)
- **Source PDF SHA-256:** `38a5f67377727100f010177106b614c83e3ee3e4799a73da69a0d5396e70fd22`
- **Pages:** 255 in the PDF, 181 usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR (MonOCR v3.5 @ d3d9d5e, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); monocr-cli 0.2.0 on monocr 0.5.0, page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-03. Each page rendered at the tool's default resolution and read line by line.
- **Review:** not reviewed.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**54** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**0** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

74 of 255: empty: 5, 38-39, 44, 50-51, 55, 60-61, 66, 72-74, 77-79, 82-84, 87-88, 95, 99, 108-109, 114, 122-123, 126-127, 129, 144, 150, 155, 164-166, 171-172, 189, 191, 193-194, 205, 210, 230, 240-241, 244, 253, 255; garbled: 7, 12, 15, 18, 22, 32, 59, 91, 100, 120, 160, 200, 228, 234, 237, 247; symbols: 115, 124, 141, 159, 185, 192, 227. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
- Same work as mon-myanmar-dictionary-nai-tun-thein, from a different PDF (255 pages against 380). Compared page by page: no page has more than 80% of its 8-character runs in the other text and the median is 45%, so it is kept as its own text. The printing year was not read.
