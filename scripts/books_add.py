#!/usr/bin/env python3
"""Add a book to books/: the text, a README, a pages report, a records.csv row and a table row.

    books_add.py --slug SLUG --pdf BOOK.pdf --text FINAL.txt --report PAGES.csv
                 --title-printed "..." [--title-english "..."] [--author "..."] [--editor-or-origin "..."]
                 [--year YYYY] [--languages mon+burmese] [--source-text-layer no]
                 [--ocr-tool "..."] [--extracted-on YYYY-MM-DD] [--review "..."] [--notes "..."]

FINAL.txt and PAGES.csv come from books_filter.py. Everything that can be counted is counted here, not
typed: the checksum, the page counts by verdict and source, the characters and the script shares. What a
person has to supply is what only a person can know: the title, the author, the year. A field left blank
means not identified. Run `make books` afterwards.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BOOKS = ROOT / "books"
MON = set("ၚၛၜၝၞၟၠဳဴဵ")
MODEL = "MonOCR v3.5 @ d3d9d5e"


def is_myanmar(c: str) -> bool:
    cp = ord(c)
    return 0x1000 <= cp <= 0x109F or 0xA9E0 <= cp <= 0xA9FF or 0xAA60 <= cp <= 0xAA7F


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def span(pages: list[int]) -> str:
    """Compress [1,2,3,7] to '1-3, 7'."""
    out, start, prev = [], None, None
    for p in sorted(pages):
        if start is None:
            start = prev = p
        elif p == prev + 1:
            prev = p
        else:
            out.append(f"{start}-{prev}" if prev > start else str(start))
            start = prev = p
    if start is not None:
        out.append(f"{start}-{prev}" if prev > start else str(start))
    return ", ".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--text", type=Path, required=True)
    ap.add_argument("--report", type=Path, required=True)
    ap.add_argument("--title-printed", required=True)
    for name in ("title-english", "author", "editor-or-origin", "year", "notes"):
        ap.add_argument(f"--{name}", default="")
    ap.add_argument("--languages", default="mon")
    ap.add_argument("--source-text-layer", default="not recorded")
    ap.add_argument("--ocr-tool", default="monocr-cli 0.2.0 on monocr 0.5.0, page mode")
    ap.add_argument("--extracted-on", required=True)
    ap.add_argument("--review", default="not reviewed")
    a = ap.parse_args()

    folder = BOOKS / a.slug
    if folder.exists():
        print(f"{folder} already exists", file=sys.stderr)
        return 1
    with a.report.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    original = len(rows)
    kept = [r for r in rows if r["verdict"] == "keep"]
    again = [r for r in kept if r.get("source", "first read") != "first read"]
    dropped: dict[str, list[int]] = {}
    for r in rows:
        if r["verdict"] != "keep":
            dropped.setdefault(r["verdict"], []).append(int(r["page"]))
    detail = "; ".join(f"{k}: {span(v)}" for k, v in sorted(dropped.items())) or "none"
    text = a.text.read_text(encoding="utf-8")
    body = [ln for ln in text.splitlines() if not (ln.startswith("[page ") and ln.endswith("]"))]
    chars = [c for ln in body for c in ln if not c.isspace()]
    mm = [c for c in chars if is_myanmar(c)]
    myan_pct = round(100 * len(mm) / len(chars), 1) if chars else 0.0
    mon_pct = round(100 * sum(c in MON for c in mm) / len(mm), 2) if mm else 0.0
    digest = sha256(a.pdf)

    folder.mkdir(parents=True)
    shutil.copyfile(a.text, folder / f"{a.slug}.txt")
    shutil.copyfile(a.report, folder / "pages.csv")
    by_source = Counter(r.get("source", "first read") for r in kept)
    (folder / "README.md").write_text(
        f"""# {a.title_printed}

- **Title as printed:** {a.title_printed}{f" ({a.title_english})" if a.title_english else ""}. Read from the book's own pages by OCR, so it may carry recognition errors; the PDF's file name is `{a.pdf.name}`.
- **Author / origin:** {a.author or "not identified"}{f"; {a.editor_or_origin}" if a.editor_or_origin else ""}{f". Year: {a.year}" if a.year else ""}
- **Source PDF SHA-256:** `{digest}`
- **Pages:** {original} in the PDF, {len(kept)} usable. Only pages that could be read are kept; the rest are dropped and listed below. `pages.csv` gives the verdict for every page.
- **Text:** machine OCR ({MODEL}, [huggingface.co/janakhpon/monocr](https://huggingface.co/janakhpon/monocr); {a.ocr_tool}), not proofread. It carries the model's recognition errors.
- **Extracted:** {a.extracted_on}. Each page rendered at the tool's default resolution and read line by line.
- **Review:** {a.review}.
- **Licence:** none established; unresolved. The document states no licence. See [LICENSE-CORPUS.md](../../LICENSE-CORPUS.md).

## Layout of the text file

Pages in PDF order, each opened by a `[page N]` line with the PDF page number and separated by one blank line. Each line is one line as the OCR read it: nothing was reflowed, merged, deduplicated or corrected. The OCR does not detect paragraphs, so there are no paragraph breaks inside a page. Unicode NFC. Pages that were dropped have no marker, so the numbering has gaps.

## How pages were chosen

Every page was read, then kept only if it reads as text: not blank, not a table or photograph read as symbols, not malformed character stacking, not a table of digits. Mon, Burmese and English text are all kept. Where the first read failed, the page was read again after flattening its background and cropping to the text block (**{by_source.get("recovered", 0)}** pages), which also drops any text printed in the margins of those pages. English pages are read with Tesseract instead, because the Mon model reads English badly (**{by_source.get("english read", 0)}** pages), and kept only when Tesseract is confident. Running heads, page numbers and decoration on the kept pages were not removed.

## Pages dropped

{original - len(kept)} of {original}: {detail}. Short pages under about 100 characters (a title page, a dedication) are dropped with the blank ones, even when clean.

## Known issues

- Text over photographs or colour gradients often could not be read and is missing; `empty` and `garbled` drops are mostly that.
- Digits are unreliable.
{f"- {a.notes}" if a.notes else ""}
""",
        encoding="utf-8",
    )
    with (BOOKS / "records.csv").open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        cols, existing = reader.fieldnames or [], list(reader)
    new = dict.fromkeys(cols, "")
    new.update(
        slug=a.slug, title_printed=a.title_printed, title_english=a.title_english, author=a.author,
        editor_or_origin=a.editor_or_origin, year=a.year, languages=a.languages, source_file=a.pdf.name,
        source_sha256=digest, source_text_layer=a.source_text_layer, original_pages=str(original),
        usable_pages=str(len(kept)), recovered_pages=str(len(again)), dropped_pages=str(original - len(kept)),
        dropped_detail=detail, characters=str(len(chars)), myanmar_share_pct=str(myan_pct),
        mon_specific_pct=str(mon_pct), text_encoding="Unicode NFC", ocr_model=MODEL, ocr_tool=a.ocr_tool,
        extracted_on=a.extracted_on, review=a.review, licence="unresolved", notes=a.notes,
    )
    existing.append(new)
    with (BOOKS / "records.csv").open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        w.writerows(existing)
    readme = BOOKS / "README.md"
    lines = readme.read_text(encoding="utf-8").splitlines()
    last = max(i for i, ln in enumerate(lines) if ln.startswith("| ["))
    row = (f"| [{a.slug}]({a.slug}/) | {a.title_printed}{f' ({a.title_english})' if a.title_english else ''} | "
           f"{a.author or 'not identified'} | {len(kept)} / {original} | {len(chars):,} | {myan_pct}% | not measured | "
           f"{mon_pct}% | not applicable |")
    lines.insert(last + 1, row)
    readme.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{a.slug}: {len(kept)} of {original} pages usable ({len(again)} recovered), {len(chars):,} characters")
    return 0


if __name__ == "__main__":
    sys.exit(main())
