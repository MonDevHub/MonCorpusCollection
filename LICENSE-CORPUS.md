# Corpus licence and attribution

This file governs the corpus text in `shards/` and the derived tables in `results/`.
The code is separate: `LICENSE` is an MIT grant scoped to `scripts/` and `Makefile`.

**There is no single licence for this corpus, and this file does not invent one.**
`shards/` is a *collection*: each source occupies its own files, identified by the
filename prefix, and each source carries its own terms. Some of those terms are
established and some are not. The table below is keyed to the prefix so any line in
any shard resolves to its own terms.

Run `make stats` for the current per-source mass. Wikipedia is the largest source by
character count and IMNA the second, which is why the two rows below decide the
practical answer for most consumers.

## Terms per source

| Shard prefix | Source | Terms | Status |
| :--- | :--- | :--- | :--- |
| `wikipedia_shard_*` | [Mon Wikipedia](https://mnw.wikipedia.org) | **CC BY-SA 4.0** | Verified 2026-08-12 |
| `mondictdb_shard_*` | [MonDictDB](https://github.com/Barnista/MonDictDB) by [Barnista](https://github.com/Barnista) | **MIT** | Verified 2026-08-12 |
| `monnews_shard_*` | [Independent Mon News Agency](https://monnews.org) | **None established** | **Unresolved** |
| `telegram_*_shard_*`, `facebook_shard_*` | Public Telegram channel and Facebook page posts | **None established** | **Unresolved** |
| `ocr_extracted_shard_*` | Text recovered from scanned material | **None established** | **Unresolved** |
| `custom_shard_*` | Specialized and legacy collections | **None established** | **Unresolved** |
| `gemini_generated_shard_*` | Authored by Google Gemini | **None established** | **Unresolved** |
| `handwritten_shard_*` | Composed directly in Mon by a native writer | **None recorded** | **Unresolved** |

"Verified" means the upstream statement was read at the URL given, on the date given:
the [Wikimedia Terms of Use](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use)
for Wikipedia, and the repository's own `LICENSE` for MonDictDB.

## What "unresolved" means

For every row marked **Unresolved**, no licence has been obtained, and this project has
no authority to grant one. **Redistribution of those shards is not covered by this file
or by any other file in this repository.** They are present because they were collected
before the terms were settled; that is a fact about the repository's history, not a
permission.

This is not a formality for `monnews_shard_*` in particular. IMNA is a working news
agency and those shards are a large fraction of its archive. Treat that row as an open
legal obligation on the maintainers, not as a licensing detail.

`handwritten_shard_*` is the one row the maintainers can close unilaterally, by
recording the writer's grant in this file. Until that is written down, "commissioned for
this project" is not a licence and the row stays unresolved.

## CC BY-SA 4.0 attribution for `wikipedia_shard_*`

CC BY-SA 4.0 requires attribution, a licence link, an indication of changes, and that
adaptations are shared under the same licence. `wikipedia_shard_*` is Adapted Material,
because the text was cleaned and repacked as listed below, so all four apply.

> Text in `wikipedia_shard_*` is derived from [Mon Wikipedia](https://mnw.wikipedia.org),
> by its contributors, used under
> [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). The text has been
> modified. Adaptations of it must be shared under CC BY-SA 4.0.

**Changes made to the Wikipedia text**, as required by CC BY-SA 4.0 §3(a)(1)(B):

- normalized to Unicode NFC;
- URLs, control codes and invisible format characters removed;
- article boundaries flattened into one segment per line, blank line between documents;
- near-duplicate segments dropped against the rest of the corpus;
- articles concatenated and repacked into ~20 MB shards.

**A known gap in the attribution.** CC BY-SA 4.0 is satisfied by a link to each article
or a list of authors. Neither is reconstructable from these shards: per-article URLs were
stripped at import, and only `wikipedia_shard_003` retains a partial set. The attribution
above therefore credits the project rather than the individual contributors the licence
names. Recording the source URL per document at import is the fix; it is not something
this file can do retroactively.

## Using this corpus

- Using **only** `wikipedia_shard_*` and `mondictdb_shard_*` is covered: comply with
  CC BY-SA 4.0 and MIT respectively.
- Using any **Unresolved** shard is not covered by this repository. Resolve the terms
  with the source before redistributing that material.
- `results/` is computed over all shards and inherits the same split. Whether a
  character-frequency table is a derivative work of the text it counts is an open
  question the maintainers have not taken advice on; it is flagged here rather than
  answered.

If you use this data, attribute **Mon Corpus Collection** *and* the underlying source
of each shard you used.

## Reporting a problem

If you hold rights in material here and it should not be redistributed, open an issue on
[MonDevHub/MonCorpusCollection](https://github.com/MonDevHub/MonCorpusCollection) and the
affected shards will be removed.
