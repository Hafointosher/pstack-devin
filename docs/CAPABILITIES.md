# Capability matrix

Legend: **Ported** = works as upstream · **Adapted** = works, mechanism changed · **Degraded** = partial · **Unavailable** = cannot work on this host.

## Core orchestration

| Feature | Status | Notes |
|---|---|---|
| poteto-mode + 22 playbooks | Adapted | subagent spawning via Devin `run_subagent` profiles |
| 24 principle skills | Ported | pure doctrine, frontmatter converted to Devin format |
| worker.md contract | Ported | unchanged, shipped verbatim |
| Explicit-only invocation | Adapted | `disable-model-invocation` → `triggers: [user]` |
| poteto-agent persona | Adapted | Devin custom profile, plugin-cache search paths updated |
| comment-sicko persona | Ported | read-only reviewer profile |

## Model routing

| Feature | Status | Notes |
|---|---|---|
| Per-role models | Adapted | Devin has no per-spawn model argument; encoded in pinned profiles |
| Upstream default slugs | Ported | `claude-opus-5-5-xhigh-fast`, `claude-opus-5-5-high-fast`, `claude-fable-5-2-high`, `gemini-4-neon-xhigh` validated in Devin catalog |
| setup-pstack budget config | Adapted | writes `.devin/rules/pstack-models.md` (project-local, `trigger: always_on`) instead of `~/.cursor/rules/*.mdc`; validates against `devin models list --format json` |
| `inherit-parent`/`auto` | Adapted | `subagent_general` for write-capable; read-only exact-parent-model has no perfect equivalent |
| Panel diversity (arena/interrogate) | Ported | pinned runner/reviewer profiles per vendor seat |

## Helpers

| Feature | Status | Notes |
|---|---|---|
| watch-pr | Ported | zero-dependency Node port; commander replaced by local shim; 53/54 upstream tests pass on Windows (1 POSIX-only skip) |
| worktree-audit | Adapted | Node `.mjs`; local-only, `deletionAuthorized: false`, no transcript scan (Cursor transcripts don't exist) |
| show-me-your-work logging | Ported | `log.mjs`, full behavior incl. formula escaping, arity errors |
| statechart | Adapted | no mise auto-install; Java/TLC explicit; direct Node invocation canonical |

## Degraded / Unavailable

| Feature | Status | Notes |
|---|---|---|
| cursor-team-kit (`/deslop`, `control-ui`, `control-cli`) | Unavailable | Cursor-only; unslop passes + browser/desktop drivers substitute |
| `/loop` | Adapted | Devin scheduled sessions / bounded watcher loops |
| Cursor transcripts (`~/.cursor/projects/`) | Unavailable | `devin_session_events`/`devin_session_search` substitute where possible |
| Custom Modes | Unavailable | invoke `/pstack-devin:poteto-mode` per task |
| Cloud agents | Adapted | background subagents; note plugin custom profiles are local-only in Devin — cloud sessions fall back to `subagent_general` with disclosure |
| Benny automation | Degraded | shipped as dormant reference in `automations/benny/`, not a live automation |
