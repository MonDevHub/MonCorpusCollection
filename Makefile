# Commands for the corpus. Run these rather than retyping the commands behind them.
#
#     make stats        per-source table (the README Dataset table)
#     make verify       checksum manifest: contents AND coverage
#     make quality      the Data quality numbers, with the personal-data gate
#     make lint         ruff over the scripts
#     make check        verify + quality + lint, i.e. everything that can fail
#     make frequencies  regenerate results/latest/ from the shards

PYTHON ?= python3
SHARDS := shards

# ruff is not vendored. Use it if it is on PATH, otherwise fall back to uvx, which
# fetches it on demand. Both read ruff.toml, so a local run and a CI run agree.
RUFF ?= $(shell command -v ruff >/dev/null 2>&1 && echo ruff || echo 'uvx ruff')

.PHONY: all check stats verify quality lint frequencies

all: check

## check: everything that can fail. stats is excluded because it only reports.
check: verify quality lint

## stats: per-source shards, lines, characters, Mon/Myanmar share.
stats:
	$(PYTHON) scripts/shard_stats.py

## verify: check the shards against shards/SHA256SUMS.
#
# Two things have to be true and only one of them is what shasum checks.
#
# 1. The listed files still hash to what the manifest says. `shasum -c` does that.
#    It must run from inside shards/ — the manifest holds bare filenames, so from the
#    repo root every single file reports "No such file or directory".
#
# 2. The manifest covers every shard that exists. `shasum -c` does NOT do that: it
#    only looks at the lines it was given, so it exits 0 on a manifest that has gone
#    stale by omission. build_shards.py regenerates the manifest on import; this check
#    catches a shard added any other way.
verify:
	@cd $(SHARDS) && shasum -a 256 -c SHA256SUMS
	@cd $(SHARDS) && \
	  uncovered=$$(for f in *.txt; do grep -qF "  $$f" SHA256SUMS || echo "  $$f"; done); \
	  if [ -n "$$uncovered" ]; then \
	    echo "FAIL: SHA256SUMS does not cover:"; \
	    echo "$$uncovered"; \
	    echo "shasum -c exits 0 anyway - it only checks the files the manifest lists."; \
	    echo "Regenerate: cd $(SHARDS) && shasum -a 256 *.txt > SHA256SUMS"; \
	    exit 1; \
	  fi; \
	  echo "coverage: SHA256SUMS lists all $$(ls -1 *.txt | wc -l | tr -d ' ') .txt file(s) in $(SHARDS)/"

## quality: the Data Quality figures, and the no-PII gate (--check exits 1 on a violation).
quality:
	$(PYTHON) scripts/data_quality.py --check

## lint: ruff over the scripts, configured by ruff.toml.
lint:
	$(RUFF) check .

## frequencies: character, bigram and trigram tables over all shards, into results/latest/.
frequencies:
	$(PYTHON) scripts/corpus_counter_normalized.py $(SHARDS) --output-dir results/latest --all-chars
