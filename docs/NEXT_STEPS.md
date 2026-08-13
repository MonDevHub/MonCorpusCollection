# Next steps

The single place forward work lives for this repository. Findings come from
[AUDIT-2026-08-08.md](AUDIT-2026-08-08.md); **status below was re-verified by
measurement on 2026-08-12**, not carried over from what the audit said.

Read the first section before any other. Two findings here are not engineering
work, they gate whether this corpus can be used by anyone at all.

---

## 0. Blocking

Neither is fixed by code, and everything else in this file is worth less until
they are closed. Every downstream consumer inherits both, including
[MonOCR](https://github.com/MonDevHub/monocr), which `README.md:5` names as a
dependent.

### 0.1 The licence is defective — C1, open

Re-verified 2026-08-13: `LICENSE:1` reads `SCOPE — READ THIS FIRST` and scopes
the MIT grant to `scripts/*.py` and the `Makefile`, and `LICENSE-CORPUS.md`
states the terms per source. `15b8839` did both.

**The sentence that stood here was false, and worth recording as such.** It said
`LICENSE` was "still a verbatim MIT grant". `15b8839` had already scoped it at
00:04:06; `8a081fa` wrote the denial 47 seconds later, and `b6f5375` rewrote this
file that morning without touching the line. A re-verification dated to yesterday
is not a re-verification.

The corpus redistributes **CC BY-SA Mon Wikipedia at 25,589,404 of 47,221,746
counted characters (54.2%)** and **12,064,310 characters of Mon News Agency
archive with no stated licence (25.5%)** — both reproduced by `make stats` on
2026-08-13. MIT no longer reaches either. What it never did was satisfy them.

**Exit criteria.** One of three is met:

1. **Open.** `LICENSE` is CC BY-SA 4.0, or the shards that require it are removed.
   Neither: `wikipedia_shard_001`–`005` are all still tracked, and the MIT grant
   was scoped away from the text rather than replaced over it. `LICENSE-CORPUS.md`
   does declare CC BY-SA 4.0 for the prefix and lists the changes §3(a)(1)(B)
   requires — but it also records that per-article attribution is not
   reconstructable, and §3(a)(1)(A) requires that. Removing the wrong grant is not
   the same as supplying the right one.
2. **Met** 2026-08-13, by `15b8839`. `LICENSE-CORPUS.md` states the licence and
   attribution **per source**, keyed to the shard prefix, so a consumer can
   resolve any line back to its terms.
3. **Open.** IMNA permission is obtained in writing, or `monnews_shard_*` is
   dropped. Neither: `monnews_shard_001`–`003` are tracked, and no permission is
   recorded anywhere in the tree — `git ls-files` returns no such file, and
   `LICENSE-CORPUS.md` still carries the row as **Unresolved**.

Item 3 is the one that takes calendar time. Start it first; it can run while the
rest of this file is worked.

**Owner decision, not an engineering task.** Recorded here so it is not mistaken
for something the roadmap closes on its own.

### 0.2 Personal data — C2, half closed

**The working tree is clean. The history is not.**

Closed 2026-08-12: a redaction pass removed **21 lines across six shards**, whole
lines rather than masks, because most of the material paired a personal name with
a number and masking the number leaves the association intact. Twelve further
blank lines went with them, where a removed line was its own document and would
otherwise have left a doubled separator.

| shard | PII lines removed | blank separators | total |
| :--- | ---: | ---: | ---: |
| `custom_shard_001.txt` | 2 | 0 | 2 |
| `facebook_shard_001.txt` | 5 | 1 | 6 |
| `monnews_shard_001.txt` | 3 | 3 | 6 |
| `monnews_shard_002.txt` | 3 | 3 | 6 |
| `telegram_mot_tip_ebook_shard_001.txt` | 5 | 2 | 7 |
| `wikipedia_shard_001.txt` | 3 | 3 | 6 |
| **total** | **21** | **12** | **33** |

Before: 4 email-shaped and 23 phone-shaped strings across 6 of 15 shards. After:
zero of both. `python3 scripts/data_quality.py --check` exits non-zero if either
reappears, and `docs/CORPUS.md:64` records the policy.

**Three of the 23 were written in Myanmar numerals** (U+1040–U+1049) and no `\d`
pattern matches them. The check covers both numeral systems. This is the failure
mode most likely to recur, because an ASCII-only scan reports a clean corpus.

**Still open: the history.** Every removed line remains reachable in earlier
commits. Until the rewrite below is run and force-pushed, `git log -p` returns
the roster.

**Do not publish to Hugging Face before the history rewrite lands.** A dataset
release is a second distribution channel with its own cache and its own mirrors,
and it makes takedown materially harder.

#### The history rewrite

`git filter-repo` is not installed by default: `brew install git-filter-repo` or
`pip install git-filter-repo`.

**Read this first.** The rewrite changes **every commit hash in the repository**,
not only the ones that touched shards. Every existing clone becomes incompatible
and must be re-cloned — a `git pull` into an old clone reintroduces the old
history. Open pull requests must be recreated. Anyone who has cloned needs
telling directly, because nothing about a force-push notifies them.

Run it **after** the redaction is committed, and from a fresh clone, which is what
`filter-repo` expects:

```bash
# 1. Note the commit that contains the redaction, then get a clean copy.
cd /path/to/work
git clone --no-local /path/to/MonCorpusCollection MonCorpusCollection-rewrite
cd MonCorpusCollection-rewrite
REDACTION_COMMIT=<sha of the redaction commit>

# 2. Build the replacement spec from that commit's own diff, so the values are
#    never typed out and never land in a file inside the repository.
#    Scope to *.txt: shards/SHA256SUMS also changed in that commit, and its old
#    hashes are not content to redact.
git show "$REDACTION_COMMIT" -- 'shards/*.txt' \
  | grep '^-' | grep -v '^---' | sed 's/^-//' \
  | grep -v '^[[:space:]]*$' \
  | sed 's/$/==>/' | sed 's/^/literal:/' > ../redactions.txt
wc -l ../redactions.txt        # must print 21; stop if it does not

# 3. Rewrite every blob in every commit.
git filter-repo --replace-text ../redactions.txt

# 4. Verify: no hit anywhere in history, in either numeral system.
git log --all -p -- shards/ | grep -cE '[0-9]{9,}|@[a-z0-9.-]+\.[a-z]{2,}'
python3 scripts/data_quality.py --check

# 5. Destroy the spec file. It is a list of exactly the strings being removed.
shred -u ../redactions.txt 2>/dev/null || rm -P ../redactions.txt

# 6. Re-point at the real remote and force-push every ref.
git remote add origin git@github.com:MonDevHub/MonCorpusCollection.git
git push --force --all origin
git push --force --tags origin
```

Then, outside git: ask GitHub Support to purge cached views of the old objects.
A force-push leaves unreferenced commits reachable by SHA through the web UI and
the API until GitHub garbage-collects them, and a fork keeps them indefinitely.
Check for forks before assuming the rewrite finished the job.

**Exit criteria.**

1. ~~A redaction pass over every shard.~~ Done 2026-08-12.
2. History rewrite, force-push, and a note to anyone who has cloned.
3. ~~A PII policy in `docs/CORPUS.md`, and a detection step that **fails**~~ —
   done: `docs/CORPUS.md:64` and `scripts/data_quality.py --check`. Still to do:
   call that check from `build_shards.py` so an import cannot introduce PII
   without the build failing.
4. ~~`SHA256SUMS` regenerated.~~ Done — all 15 shards, verified with
   `shasum -a 256 -c SHA256SUMS`. **Every downstream pin changed; say so in the
   release note.**

---

## 1. Truthfulness — documented claims that measurement contradicts

A document claiming a property the data does not have causes someone to act on
something untrue, which is why this ranks above simplicity here.

| | Work | Finding | Status |
|---|---|---|---|
| 1.1 | `docs/CORPUS.md` says URLs are stripped. **9,228 remain.** Either strip them or change the sentence to describe what the pipeline does | H1 | **Open.** The sentence now scopes itself to the importer and gives the per-shard counts, but the URLs are still in the data |
| 1.2 | The deduplication claim understates the real figure by an order of magnitude. State the measured rate with its denominator | H2 | **Closed** 2026-08-12. 369,898 eligible lines, 94,006 redundant, 25.4%, reproducible with `scripts/data_quality.py` |
| 1.3 | Root `results/` ships character counts from a **different pipeline** than the one documented | H3 | **Closed** 2026-08-12. `results/latest/` regenerated over all 15 shards; it previously described 14 and had no row for `handwritten_shard_001.txt` |

Also closed 2026-08-12, found while checking the above:

- `docs/CORPUS.md` claimed `total_raw_text_length` "matches an independent byte
  count exactly". It is a **character** count, and the byte count is 2.49x larger.
- Three shard-count claims were wrong: "10 of the fourteen shards", "9 of 15
  shards do not end in a newline" (it is 10), and "52 tracked files". The tracked
  file count moves with every commit, so it is now cited as the command that
  produces it, `git ls-files | wc -l`, rather than as a number.
- `README.md` claimed `handwritten_shard_001` was the only shard contributing no
  duplicates. Four others do, and `mondictdb_shard_001` contributes 54,457
  eligible lines with no repeats at all.
- Every `.md` line citation in both audit documents had rotted onto blank lines
  and has been re-resolved. The `.py` citations were all still correct.

**Exit:** every number in `README.md` and `docs/CORPUS.md` is reproducible by a
command in the repository, and that command is named beside the number. This now
holds for the Dataset table (`scripts/shard_stats.py`) and the Data Quality
section (`scripts/data_quality.py`).

---

## 2. Engineering hygiene

Proportionate to what this is: a handful of scripts and fifteen data files,
maintained by one person. It does not need a package, a service or a plugin
architecture.

| | Work | Why now |
|---|---|---|
| 2.1 | ~~**A `Makefile`** with `stats`, `quality` and `verify` targets~~ **done** `b68b794`. `make check` runs all three, and `verify` also asserts the manifest covers every shard, because `shasum -c` exits 0 when it lists fewer files than exist | — |
| 2.2 | ~~**`ruff`**, then `ruff check --fix`~~ **done** `b68b794`, in `ruff.toml` rather than a `pyproject.toml` this repo does not have. `make lint` is clean. `RUF001-003` are ignored: they read MYANMAR DIGIT ZERO as a typo for Latin `o` | — |
| 2.3 | **CI** running the `verify` and `quality` targets on push | The PII gate is only a gate if something runs it. Right now it has to be run by hand |
| 2.4 | **A test for `build_shards.py`'s shard-boundary and dedup behaviour** | It produces the artifact everything downstream trains on. `scripts/data_quality.py` measures the corpus but asserts nothing about the importer |
| 2.5 | **A stated Python floor.** `shard_stats.py:20` uses PEP 585 generics and `build_shards.py:142` uses `X \| None` | One README line closes it |

**Exit:** a single command runs lint, the statistics and the PII gate, and CI runs
it on push.

---

## 3. Distribution

Blocked on section 0. Recorded so the sequence is visible.

| | Work | Note |
|---|---|---|
| 3.1 | **Stop shipping 124 MiB of `.txt` through git.** Git has no streaming reader, no column types, and every clone pays the full history | Hugging Face Datasets, or release tarballs with checksums |
| 3.2 | **Publish as a Hugging Face dataset with a datasheet** — provenance, licence and known limitations per shard | **Gated on 0.1 and the 0.2 history rewrite.** This is the item that makes the corpus citable, and publishing before the licence and the history are resolved multiplies both problems |
| 3.3 | **A held-out evaluation split, reserved and never trained on** | `handwritten_shard_001.txt` is the highest-confidence Mon here: 1,501 lines, 1,094 dedup-eligible, and not one of them duplicated anywhere in the corpus. MonOCR already trains on 1,055 of its lines, so carving it out later means excluding them there first |

---

## 4. Four commits `make check` cannot answer for

The gates landed before the code they gate was clean, so four commits fail
`make check` for reasons that have nothing to do with any bug being hunted.
**History is staying as it is** — the SHAs below are already cited from this file
and from `AUDIT-2026-08-08.md`, and a rebase to tidy four commits would rewrite
every one of them. The defect is recorded rather than removed.

| Commit | `make check` | Why |
|---|---|---|
| `26680cd` | exits 2 | Predates the `Makefile`. `make: *** No rule to make target 'check'` |
| `15b8839` | exits 2 | Same |
| `b68b794` | exits 2 at `lint` | Added `Makefile` and `ruff.toml`, and `ruff.toml` selects `UP`. 8 findings |
| `28913bb` | exits 2 at `lint` | 2 findings left in `build_shards.py` |

`b68b794` is the one worth spelling out. It introduced the lint gate while
`scripts/corpus_counter_normalized.py:33` and `scripts/mon_cluster_counter.py:40`
still read `from typing import Iterable`, which is `UP035`. Both were rewritten in
the next commit, `28913bb` — but that commit is still red, because `build_shards.py`
carried `C420` at `:47` and `C408` at `:126` until `6ba4e6e`. `verify` and `quality`
pass at both; only `lint` fails.

**`6ba4e6e` is the first commit where `make check` exits 0.** Bisecting with
`make check` as the test marks everything before it bad. Bisect on the specific
symptom instead, or `git bisect skip` the four.

Measured with ruff 0.16.2, which the `Makefile` fetches through `uvx` and does not
pin — a later ruff can change the finding counts above, though not which commits
are red.

The 0.2 history rewrite invalidates every SHA in this section. Re-derive them from
the rewritten history if it lands.

---

## What we are deliberately not doing

| Not doing | Why |
|---|---|
| **A database or a query layer** | 15 files and one maintainer. `grep` and a few scripts are the right size, and the audit found nothing a schema would have caught |
| **Automatic PII detection as the only control** | Pattern scanning finds email and phone shapes. It does not find a name beside a number, which is the actual finding. It supplements the redaction pass and does not replace it |
| **Re-scraping to fix provenance** | The licence problem is not that the record is missing; it is that the terms conflict. A fresh scrape under the same terms changes nothing |
| **Growing the corpus** | Volume is not the constraint. 1,253,139 lines against 39.4% blank and 25.4% redundant means the next useful line comes from cleaning, not collecting |

---

## How this file stays true

Every status line above says **re-verified** and gives the date and the
measurement, or it says the finding is carried from the audit unchecked. When a
finding closes, move it out of this file rather than striking it through, and put
the closing measurement in `AUDIT-2026-08-08.md` beside the finding.

A status that cannot be re-derived by a command is a status nobody can trust.
