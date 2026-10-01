# လိက်ဂတဵုဇၞော်မန် ၂

- **Title as printed:** လိခ်ဂတဵုဇၞော်မဉ် (running header); file title လိက်ဂတဵုဇၞော်မန် ၂. Part 2 of a longer work: the printed page numbers run ၂၂ to ၃၈.
- **Origin:** redistributed by www.monlibrary.com, whose header and watermark are on every page; PDF metadata author: Minmon007
- **Source PDF SHA-256:** `bd43ad9d19354f46e0dfe8fadaf7641fcd48f13099c950a9061e891a71089fdf`
- **Pages:** 17
- **Text:** machine OCR (MonOCR model v3.5, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr) @ `d3d9d5e`), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-01. Each page rendered to about 2,400 px tall (218 DPI), printed rules removed, then read line by line.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by
one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged,
deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph
breaks inside a page. Unicode NFC.

## What was removed

Only lines that are not the book's text: the www.monlibrary.com page header and diagonal
watermark, which the OCR reads as Latin noise such as `"YNm9nli2rary0m`; the
မူလဖအံက် catchword at the foot of each page; and the running headers with their page
numbers (လိခ်ဂတဵုဇၞော်မဉ်, လၟေၚ်ဖ္ဍောတ်ဝတ်, ဂါထာလ္ၚောဝ်ကျာ် အစိန္တေယျ ၂၅ ပိုဒ်).
47 lines in all.

## Known issues

- **Digits are unreliable.** The printed page numbers ၂၂ and ၃၇ were read as ၃၃ and ၄၈.
- Two running headers survived because the OCR read them differently from the rest:
  ဂ္အိလိရ်ဂတဵုဇၞော်မဉ်၃၃ on page 1 and လၟေၚ်ဖ္ဍောတ်ဝတ်၄ဝ on page 8.
- With the running headers gone, the section names appear only in the closing lines of
  each section.
- Page 17 is blank apart from the header and watermark, so it has a marker and no text.
- `င` (U+1004) and `ၚ` (U+105A): 31 and 246. Character-order errors on 10.4% of lines,
  the highest of the four.
