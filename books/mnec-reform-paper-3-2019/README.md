# MNEC Reform Paper No 3 (April 2019)

- **Title as printed:** လိခ်လညာတ် သ္ဂောံသၠုင်ပတိုန် ကဆံင်ပရေင်ပညာ ကောန်ဂကူမန် ခေတ်တၟိ (လၟေင် ၃)
- **Author as printed:** နာဲဗညာဟံသာ (ဍုင်အဝ်သတြေလျာ); PDF metadata author: Hongsar Banya
- **Source PDF SHA-256:** `0db83a508bfead0a2013b7032a70f781ba633e0b5a0b48eab5de0c870a667a65`
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

Only lines that are not the paper's text: 17 page-number footers (`pg. N` plus the running
title), 17 running author footers, and 17 footer lines carrying the author's e-mail address.

## Known issues

- `င` (U+1004) and `ၚ` (U+105A) are mixed for the same printed letter: 458 and 634. Left as
  produced.
- Character-order errors (a vowel sign after asat, or `:`/`?` after a Myanmar letter) on 3.3%
  of lines.
