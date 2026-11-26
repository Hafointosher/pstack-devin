# Mirroring upstream pstack

## Drift check (automated)

```
python tools/check_upstream.py
```

Fetches cursor/plugins (sparse, blobless, temp-dir cache that is always cleaned up) and
compares the raw upstream `pstack/` tree at the mirrored commit in `UPSTREAM.json` against
upstream HEAD. Exit 0 = identical trees, zero drift. Exit 1 = drift, with each added /
removed / changed file classified as either `transformed` (safe to re-port mechanically)
or `HAND-AUTHORED` (watch-pr, statechart scripts, log.mjs replacements, core SKILL.md
files — these need a human re-port decision, never a blind overwrite). Exit 2 = network
or history error.

Because the comparison is raw-upstream-vs-raw-upstream, the port's own transformations
never produce false positives.

## Applying a sync (when drift exists)

1. Fetch upstream: `git clone --filter=blob:none --sparse https://github.com/cursor/plugins` then `git sparse-checkout set pstack`.
2. Diff `skills/`, `agents/` against this repo's copies, ignoring the transformations listed in `tools/build_corpus.py`, `tools/adapt_core.py`, `tools/adapt_setup.py`, `tools/adapt_host_refs.py`.
3. Re-run those transformers over the new upstream snapshot in a scratch copy, then review diffs by hand before merging.
4. Update `UPSTREAM.json` (commit, version, date).
5. Run `python tools/validate_repo.py` and `python tests/test_helpers.py` plus the node:test suite.

Transformation rules that must never regress: no auto-install, no Bun/mise/POSIX hard dependency, `triggers: [user]` for explicit-only skills, Devin profile-based model routing, `.devin/rules/pstack-models.md` paths.
