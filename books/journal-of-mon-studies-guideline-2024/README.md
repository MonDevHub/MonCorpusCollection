# Journal of Mon Studies: editorial guideline (amended 3 November 2024)

- **Title as printed:** ကဝ်လိက်ကောန်ဂကူမန် (ညဳသာ) — လိက်ကၞပ်ကွတ်လ္ၚတ်မန် (ဝါ) ဂျာနလ်ကဝ်လိက်ကောန်ဂကူမန် — Journal of Mon Studies (or) Journal of Mon National College
- **Origin as printed:** Mon National College (ကဝ်လိက်ကောန်ဂကူမန်); the closing paragraph records the revision by နာဲဗညာဟံသာ dated (၃) နဝ်ဝေမ်ဗာ ၂၀၂၄
- **Source PDF SHA-256:** `293eba1a7a10ae704d4efa11f07e2ad3c9369a983d42ee506e3cf66c8b80ead9`
- **Pages:** 4
- **Text:** machine OCR (MonOCR model v3.5, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr) @ `d3d9d5e`), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-01. Each page rendered to about 2,400 px tall (218 DPI), printed rules removed, then read line by line.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by
one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged,
deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph
breaks inside a page. Unicode NFC.

## What was removed

One line on page 3 holding a contact e-mail address.

## Known issues

- The second title line is misread as လိက်ကၞပ်က္ွတ်လ္ဍတ်မန်; the print has ကွတ်လ္ၚတ်.
- `င` (U+1004) and `ၚ` (U+105A) are mixed for the same printed letter: 103 and 111. Left as
  produced.
- 4.95% of lines fail the Mon well-formedness check, the highest of the four books.
