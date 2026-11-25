# pstack-devin

Devin-native port of [Lauren Tan's pstack](https://github.com/cursor/plugins/tree/main/pstack) (MIT), upstream version 0.15.48.

pstack is a disciplined agent workflow system: **poteto-mode** orchestrates 22 playbooks, 24 engineering principles, and workflow skills with deliberate, model-routed subagent delegation.

## Install

Install as a Devin plugin from this repository (local path or git URL). Skills invoke as `/pstack-devin:<skill>`.

```
/pstack-devin:poteto-mode <your task>
/pstack-devin:setup-pstack      # configure per-role models + budget
```

## What ships

- 59 skills (24 principles, 35 workflow), 22 playbooks, 8 custom subagent profiles
- `watch-pr` — zero-dependency Node port (no Bun, no npm installs)
- `worktree-audit.mjs` — read-only local worktree audit, never deletes
- `log.mjs` — decision logger for show-me-your-work
- `statechart` — TLA+ statechart tooling, explicit Java/TLC prerequisites

## Requirements

- Windows/macOS/Linux. PowerShell or any shell; **Git Bash not required**
- Node.js 22.18+ (helpers); Python 3.x only for repo validation tooling
- Optional: Java + TLA+ tools for statechart model checking; `gh` CLI for watch-pr
- Nothing is auto-installed. Ever.

## Documentation

- `docs/CAPABILITIES.md` — what is Ported / Adapted / Degraded / Unavailable
- `docs/WINDOWS.md` — Windows support matrix
- `docs/MODELS.md` — model routing architecture
- `docs/VALIDATION.md` — test evidence
- `docs/PARITY.md` — upstream mapping
- `MIRRORING.md` — how to sync with upstream
