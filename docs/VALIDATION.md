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

## TLC end-to-end evidence (Java 17 + tla2tools 1.7.4 installed)

Validated with Eclipse Temurin JDK 17.0.21 and `tla2tools.jar` v1.7.4 (TLC 2.19), `TLA2TOOLS`/`JAVA` env vars:

| Evidence | Result |
|---|---|
| Live TLC run on `Counter.tla` via direct Node | PASS — real model check, chart + report written |
| Live TLC run on `CounterDeadlock.tla` | PASS — correctly reports `NotThree`/`NoDeadlock` breaking with shortest counterexample paths |
| `statechart.cmd` through real `cmd.exe` | PASS — Windows-native path verified end-to-end |
| cli.test.ts corpus matrix: all 33 specs × (LF + Windows-line-end variants), replaying recorded TLC output byte-identical against committed charts/reports | **66/66 pass** |
| config-fuzz.test.ts: 4000 fuzzed configs parsed identically by the skill and by real TLC (`ConfigOracle.java` compiled and run live) | **PASS** |
| chart.test.ts parser unit tests | 52/52 pass |
| SIGKILL cleanup: temp folders removed, no partial writes, process tree killed | 2/2 pass |
| POSIX shell launcher tests (shebang/symlink/exit-127 semantics) | 6 skipped on win32 — they test the optional Unix wrapper, not the Windows path |

## Known limitations (honest, unverified)

- RESOLVED (root-caused 2026-11-25 via the pstack bug-fix playbook itself): cli.test.ts whole-file runs previously exited nonzero at file level with all visible tests passing. The documented hypothesis (async cleanup of worker/janitor kill chains) was wrong. Runtime evidence chain: (1) TAP diagnostics showed `failureType: testCodeFailure, exitCode: 1` with no test-level failures and no exit event — external termination; (2) the test "a check killed by a signal stops the command with exit 2" ran `process.kill(Number(ps.stdout), "SIGKILL")` where MSYS `ps.exe` rejects `-o ppid=`, making stdout empty and `Number("")` zero; (3) a direct experiment proved `process.kill(0, "SIGKILL")` on Windows terminates the calling process itself instantly (exit code 1, no output flush) — the test process was killing itself mid-file; (4) test counts corroborated exactly: the 69 passes were precisely the tests ordered before the killer test, meaning ~46 later tests had never executed on Windows. Fixes: the sleepy-java fixture now records `process.ppid` itself (no POSIX ps dependency on any platform), the SIGKILL-assertion is platform-adapted (Windows termination reports exit 1 with null signalCode, so no signal can be named), 8 graceful-signal tests skip on win32 with reasons (Windows cannot deliver SIGINT/SIGTERM to a child; hard-kill cleanup is covered by the SIGKILL tests), and four real product/test bugs the newly unmasked tests exposed were fixed: `fs.renameSync` EPERM when `--out` is an existing empty directory (Windows cannot rename over any directory), EPERM-prone `rmSync` cleanup after process kills (now retries, the standard Windows idiom), test view fixtures importing raw `C:\` paths instead of `file://` URLs, and a POSIX-sh-only test fixture rewritten as cross-platform Node. Final result: 145 pass, 0 fail, 14 skipped-with-reasons — the entire suite executes on Windows for the first time.
- TLC's own stdout on Windows may contain CRLF; the parser handles both (`splitLines` tolerates `
`), and the corpus matrix explicitly verifies the "Windows line ends" variant byte-for-byte.
- statechart cli.test.ts / config-fuzz.test.ts require Java + TLC jar. They now pass with those installed.
- One upstream github.test.ts case fakes `gh` as a POSIX shell script — skipped on Windows; the same parsing is covered in-process.
- `.cmd` shim resolution for `gh` is unnecessary in practice (Windows `gh` is `gh.exe`, resolved by CreateProcess). Users with shim-only installs (rare) should install the official CLI.
- Devin end-to-end skill loading (`devin doctor` in a consumer project) — validated for manifest shape and agent-profile acceptance in probes; a full installed-plugin smoke in a separate consumer project is the remaining integration step.
- Cloud sessions: plugin custom subagent profiles are local-only per Devin docs; degradation path documented but not yet exercised in a cloud session.
