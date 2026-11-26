# pstack-devin

Devin-native port of [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), upstream version 0.15.48.

pstack is a disciplined agent workflow system: **poteto-mode** orchestrates 22 playbooks, 24 engineering principles, and workflow skills with deliberate, model-routed subagent delegation. This port runs natively on [Devin](https://devin.ai) CLI/Desktop, with first-class Windows support — every helper verified by real test runs, not claims.

## Install

```bash
devin plugins install Hafointosher/pstack-devin
```

Skills invoke as `/pstack-devin:<skill>`:

```
/pstack-devin:poteto-mode <your task>
/pstack-devin:setup-pstack      # configure per-role models + budget, generates .devin/agents/ overrides
/pstack-devin:poteto-help       # guided tour
```

## What ships

- **59 skills** (24 principles, 35 workflow), **22 playbooks**, **8 custom subagent profiles** with upstream-pinned model slugs
- `watch-pr` — zero-dependency Node port of the PR watcher (no Bun, no npm installs, no bootstrap)
- `worktree-audit.mjs` — read-only worktree audit: wip/scratch split, merge/remote/PR evidence, never deletes
- `log.mjs` — decision logger for show-me-your-work, upstream six-field schema
- `statechart` — TLA+ statechart model checking with Windows-native wrappers, explicit Java/TLC prerequisites

## Verification evidence

Everything below is from real runs on Windows 11 with Node 24, Eclipse Temurin JDK 17, TLC 2.19 — see `docs/VALIDATION.md` for the full matrix.

| Suite | Result |
|---|---|
| statechart `cli.test.ts` whole-file | **145 pass, 0 fail**, 14 skipped-with-reasons, exit 0 |
| statechart corpus matrix (33 specs × LF/CRLF) | 66/66 against real TLC output |
| config-fuzz vs live TLC oracle | 4000 configs, exact match |
| watch-pr node:test suite | 53 pass, 0 fail |
| helpers smoke (`tests/test_helpers.py`) | 25 pass, 0 fail |
| packaging validator (`tools/validate_repo.py`) | 0 errors, 0 warnings |

The 145/0 result was itself produced by dogfooding this plugin's own bug-fix playbook: the investigation root-caused a test harness defect that had silently masked ~46 tests on Windows (a POSIX `ps` dependency zeroing out into `process.kill(0)` — which terminates the caller itself on Windows) plus four real product bugs in `--out` handling and cleanup. The full evidence chain is in `docs/VALIDATION.md` and the commit history.

## Requirements

- Windows/macOS/Linux. PowerShell or any shell; **Git Bash not required**
- Node.js 22.18+ for the helpers; Python 3.x only for repo validation tooling
- Optional: Java 17+ and `tla2tools.jar` for statechart model checking (set `JAVA`/`TLA2TOOLS`); `gh` CLI for watch-pr
- Nothing is auto-installed. Ever. Missing prerequisites fail closed with a clear message.

## Documentation

- `docs/CAPABILITIES.md` — what is Ported / Adapted / Degraded / Unavailable, honestly
- `docs/WINDOWS.md` — Windows support matrix
- `docs/MODELS.md` — model routing architecture and fallback chain
- `docs/VALIDATION.md` — test evidence, including the root-cause writeup
- `docs/PARITY.md` — upstream feature mapping
- `MIRRORING.md` — how to sync with upstream
- `UPSTREAM.json` — provenance (upstream commit, license, adaptations)

## License

MIT — copyright Lauren Tan, upstream pstack. See `LICENSE`. Adaptations carry the same license with attribution preserved per-file.
