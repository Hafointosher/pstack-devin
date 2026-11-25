# Mirroring upstream pstack

1. Fetch upstream: `git clone --filter=blob:none --sparse https://github.com/cursor/plugins` then `git sparse-checkout set pstack`.
2. Diff `skills/`, `agents/` against this repo's copies, ignoring the transformations listed in `tools/build_corpus.py`, `tools/adapt_core.py`, `tools/adapt_setup.py`, `tools/adapt_host_refs.py`.
3. Re-run those transformers over the new upstream snapshot in a scratch copy, then review diffs by hand before merging.
4. Update `UPSTREAM.json` (commit, version, date).
5. Run `python tools/validate_repo.py` and `python tests/test_helpers.py` plus the node:test suite.

Transformation rules that must never regress: no auto-install, no Bun/mise/POSIX hard dependency, `triggers: [user]` for explicit-only skills, Devin profile-based model routing, `.devin/rules/pstack-models.md` paths.
