# မွန်-မြန်မာ အဘိဓာန် နှင့် သဒ္ဒါနှိုင်းယှဉ်ချက်

- **Title as printed:** ကျောင်းသုံး မွန်-မြန်မာ အဘိဓာန် နှင့် သဒ္ဒါနှိုင်းယှဉ်ချက် (a school-use Mon-Myanmar dictionary and grammar comparison). The viewer's page title reads "Mon-Myanmar Dictionary__Nai Tun Thein".
- **Author / origin:** compiled by နိုင်ထွန်းသိန်း (Nai Tun Thein), edited by နိုင်ပန်းလှ (Nai Pan Hla), as printed on the title page. Second printing, March 2020, per the printing record on page 4. The PDF is a print-out of a web page viewer (FlipHTML5) saved on 2026-04-30, so it holds page images with no text layer of its own.
- **Source PDF SHA-256:** `4d4d0fb6a185e2ac0ccd4359bb6e2ce2a98d72af54b9115ac6301e2c6f77c37f`
- **Pages:** 380 in the PDF, 374 kept. Pages 2, 50, 379 and 380 are blank, and pages 13 and 14 are the dictionary's contents table, whose page numbers the OCR read as digit noise. They are left out, and the remaining pages keep their PDF page numbers, so the numbering has gaps there.
- **Text:** machine OCR (MonOCR model v3.5, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr) @ `d3d9d5e`, read with `monocr-cli` 0.2.0 on `monocr` 0.5.0 in page mode), not proofread. It carries the model's recognition errors.
- **Extracted:** 2026-10-02. Each page rendered at 300 DPI (about 3,300 px tall) and read line by line.
- **Read by a Mon reader:** the project owner read pages of the output and judged the extraction good. That is a spot reading, not a measured error rate.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC (it changed 2 characters).

The text mixes three kinds of content: the Mon headwords (printed in bold, which the OCR does not mark), their Burmese definitions, and the dictionary's punctuation, mainly `(န)`-style part-of-speech tags and `=` before a gloss. Latin letters are almost absent (437 in the PDF, before cleaning).

## What was removed

Only lines that are not the book's text, taken out by their position on the page: the web viewer's print header and its URL footer on every page (380 and 380 lines), and the book's own running head with its page number on 367 pages. Fourteen lines made only of digits (strings of 0s and 1s the OCR read from printed rules, on pages 10, 84, 267, 333 and others) are removed too. Pages 2, 13, 14, 50, 379 and 380 are dropped whole.

## Known issues

- **Small slips on most lines.** In a check of pages 100 and 260 against the page images, nearly every line had one: an extra letter inserted (`ချိတ်ဆွဲသစည်` for `ချိတ်ဆွဲသည်`, `နဂားလည်` for `နားလည်`), a diacritic changed, and now and then a whole word wrong (`လေဘာခွေး` for `တောခွေး`). Headwords are the most important place for them, since an error there is a wrong word. The check was by a non-native reader and gives no error rate.
- **Digits are unreliable.** The OCR confuses Myanmar digits with Latin ones and with other characters; this is why the contents pages were dropped.
- **Stray characters on pages 1 and 5**, the cover and the dedication, where the printing is decorative.
- **The Mon-specific letter share is low** (below) because most of the text is the Burmese definitions, not Mon.
- **Possible overlap with another scan.** The archive's `books/` folder holds a 255-page "Mon-Myanmar Dictionary and Grammar Comparison", which looks like another printing of the same work. It was not compared with this one.
