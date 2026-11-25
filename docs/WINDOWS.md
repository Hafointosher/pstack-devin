# Windows support matrix

| Surface | Status |
|---|---|
| Pure Markdown skills (most of the 59) | Work everywhere; no runtime needed |
| PowerShell / direct `node` invocation | Canonical, required path — tested |
| Git Bash / POSIX wrappers | Optional convenience only, never required |
| watch-pr | Node 22.18+/24, zero dependencies, `.cmd` wrapper included |
| worktree-audit.mjs | Node; local git only, no network |
| log.mjs | Node; paths with spaces safe |
| statechart | Node direct invocation; Java/TLC explicit prerequisites, fail-closed when absent |
| Python | Validation tooling only (`tools/`, `tests/`), not an end-user dependency |

## Windows-specific notes

- `gh` on Windows is `gh.exe`; Node's spawn resolves it through CreateProcess `.exe` suffix search, so no shell is needed. `gh` authenticated with `gh auth login` is required for watch-pr.
- TypeScript helpers run through Node type stripping (`node --disable-warning=ExperimentalWarning`); the `.cmd` wrappers pass that flag.
- watch-pr upstream tests had three Unix-isms, fixed in this port: `import.meta.dir` (Bun-only) → `import.meta.dirname`; `node -e` inline ESM needs `--input-type=module`; absolute-path ESM imports need `pathToFileURL`. One test that fakes `gh` as a POSIX shell script is skipped on Windows (in-process fake-reader tests cover the same parsing).
- CRLF line endings: helpers read/write with explicit `\n` and tolerate `\r\n` on input.
