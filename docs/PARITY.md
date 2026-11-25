# Upstream parity map

All 59 upstream skills and 22 poteto-mode playbooks are present under their original names (Devin namespaces invocations as `/pstack-devin:<name>`). Inventory verified by `tools/validate_repo.py`.

## Transformation classes applied

1. **Frontmatter** (all skills): `disable-model-invocation: true` → `triggers: [user]`; `icon`/`color` dropped (Devin ignores them).
2. **Slash references**: `/skill` → `/pstack-devin:skill` for pstack skills.
3. **Model config path**: `~/.cursor/rules/pstack-models.mdc` → `.devin/rules/pstack-models.md`.
4. **Subagent mechanics**: Cursor `Task`/`subagent_type`/`generalPurpose`/`environment:"cloud"` → Devin `run_subagent` + named profiles (see docs/MODELS.md).
5. **Cursor-only features annotated**: cursor-team-kit, `/loop`, transcripts, Custom Modes — replaced or marked degraded in place.
6. **Helper ports**: watch-pr (Bun+commander → zero-dep Node), log.sh → log.mjs, worktree-audit.sh → worktree-audit.mjs, bootstrap.ts removed entirely.
7. **Dormant**: `automations/benny/` copied as reference, not active.

## Files intentionally absent vs upstream

- `watch-pr` `package.json`/`bun.lock`/`bootstrap.ts` — no dependencies remain to install.
- `watch-pr` `types.compile.ts` compile-time type assertions — dropped with the Bun/typecheck harness; runtime behavior is covered by the 53-case node:test suite.
- worktree-audit transcript scan — Cursor chats are local files; Devin sessions are not, so recency verification is an explicit user-confirmation gate in the playbook (documented there). PR state is a best-effort `gh` lookup, matching upstream's evidence wherever `gh` is available.
- `plugin.json` (Cursor format) — replaced by `.devin-plugin/plugin.json`.
- Root-level Cursor marketplace metadata.

## Source provenance

`worktree-audit.mjs` and the statechart `kill.ts`/Windows hardening derive from `hoangnb24/pstack-codex` (itself an MIT adaptation of upstream); everything else derives from upstream cursor/plugins@41e4009, pstack 0.15.48.
