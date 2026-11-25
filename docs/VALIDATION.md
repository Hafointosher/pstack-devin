# Validation evidence

Validated on Windows 11, Node v24.20.0, Python 3.14, no Bun, no Java. Reproduce with `python tests/test_helpers.py`.

## Passing (with evidence)

| Suite | Result |
|---|---|
| Repo validation (`tools/validate_repo.py`) | 59 skills, 24 principles, 22 playbooks, 8 agents, 0 errors |
| Helper smoke tests (`tests/test_helpers.py`) | 22/22 pass |
| — log.mjs: exit codes, header, TSV shape, formula escaping, arity errors, tab/newline normalization, paths with spaces | 7/7 |
| — worktree-audit.mjs: valid JSON, `deletionAuthorized:false`, hold-main protection, no-network fields | 5/5 |
| — watch-pr arg validation: bad PR, duplicate stack, constraint violations, unknown options, exit codes | 7/7 |
| watch-pr upstream test suite (ported bun:test → node:test via `bun-test-shim.ts`) | **53/54 pass, 1 skipped** |
| — cli.test.ts | 9/9 |
| — github.test.ts | 26/27 (1 skipped: POSIX-shell fake-gh test, inherently Unix) |
| — policy.test.ts | 18/18 |
| statechart chart.test.ts | **52/52 pass** (after corpus LF normalization; see below) |
| statechart usage/error surface | correct usage message, nonzero exit |

## Windows bugs found and fixed during the port

1. watch-pr tests used `import.meta.dir` (Bun-only) → `import.meta.dirname`.
2. Inline ESM subprocess tests needed `--input-type=module` (Bun auto-detects).
3. Absolute-path ESM imports on Windows need `pathToFileURL`.
4. statechart corpus `.out` fixtures are committed upstream with CRLF and the wrap-reassembly assertions are byte-length sensitive → corpus normalized to LF + `.gitattributes` (`text=lf`) added. Runtime input parsing (`splitLines`) is CRLF-tolerant already.

## Known limitations (honest, unverified)

- statechart cli.test.ts / config-fuzz.test.ts require Java + TLC jar, absent on the validation machine. TLC end-to-end model checking is **unverified** until those are installed; the tool fails closed with a clear message when they are missing.
- One upstream github.test.ts case fakes `gh` as a POSIX shell script — skipped on Windows; the same parsing is covered in-process.
- `.cmd` shim resolution for `gh` is unnecessary in practice (Windows `gh` is `gh.exe`, resolved by CreateProcess). Users with shim-only installs (rare) should install the official CLI.
- Devin end-to-end skill loading (`devin doctor` in a consumer project) — validated for manifest shape and agent-profile acceptance in probes; a full installed-plugin smoke in a separate consumer project is the remaining integration step.
- Cloud sessions: plugin custom subagent profiles are local-only per Devin docs; degradation path documented but not yet exercised in a cloud session.
