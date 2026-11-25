#!/usr/bin/env python3
"""Replace Cursor-specific host references with Devin equivalents across skills."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def rw(rel, pairs):
    p = REPO / rel
    t = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in t:
            print(f"MISS in {rel}: {old[:60]!r}")
        t = t.replace(old, new)
    p.write_text(t, encoding="utf-8", newline="\n")


# --- swarm: worker spawning ---
rw("skills/swarm/SKILL.md", [
    ('Spawn all N workers in one message with `subagent_type: generalPurpose`, `environment: "cloud"`, `run_in_background: true`, and the step 3 model, left unset for `auto` or `inherit-parent`. Use `environment: "local"` only when the worker needs access to something on the user\'s computer.',
     'Spawn all N workers with `run_subagent` (profile `poteto-worker`, or `subagent_general` for `auto`/`inherit-parent`), `is_background: true`, and the step 3 model as encoded in the profile. Devin has no local/cloud environment switch on spawn; plugin subagent profiles load in local CLI/Desktop sessions. In a cloud session where the pinned profile is unavailable, fall back to `subagent_general` and disclose it.'),
])

# --- arena: runner seats ---
rw("skills/arena/SKILL.md", [
    ("An `auto` or `inherit-parent` entry is the parent model, so omit `model` and spawn `generalPurpose`. If the Task tool rejects a slug, use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so.",
     "An `auto` or `inherit-parent` entry is the parent model, so use the `subagent_general` profile for that seat. Validate slugs with `devin models list --format json`; if a slug is unavailable use the nearest valid slug of the same family or drop the seat, keep at least two runners, and say so."),
])

# --- interrogate ---
rw("skills/interrogate/SKILL.md", [
    ("Spawn each adversary as `generalPurpose`.",
     "Spawn each adversary with `run_subagent` using the reviewer profile matching its model seat (`poteto-reviewer-opus`/`poteto-reviewer-gemini`) or `subagent_general` for `inherit-parent` seats."),
])

# --- how ---
rw("skills/how/SKILL.md", [
    ("Spawn one Task subagent with `subagent_type: generalPurpose` and `readonly: true` that explores and explains in one pass.",
     "Spawn one subagent with `run_subagent` (profile `subagent_explore`, read-only) that explores and explains in one pass."),
])

# --- no-comments ---
rw("skills/no-comments/SKILL.md", [
    ('1. Spawn `Task` with `subagent_type: "comment-sicko"`. Pass the scope.',
     '1. Spawn `run_subagent` with `profile: "comment-sicko"`. Pass the scope.'),
])

# --- setup-pstack generalPurpose mention ---
rw("skills/setup-pstack/SKILL.md", [
    ("# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (omit Task `model` and spawn `generalPurpose`).",
     "# `inherit-parent` or `auto` as a value: the role runs on the parent chat model (use the `subagent_general` profile, which inherits the parent model)."),
])

# --- statechart: no mise auto-install ---
rw("skills/statechart/SKILL.md", [
    ("The first run installs TLC and Java with mise and needs the network.",
     "TLC and Java are explicit prerequisites — install them yourself (any JDK 17+ and the TLA+ tools jar). Nothing is auto-installed. Without Java/TLC the tool still parses and renders graphs but cannot run model checking; it fails closed with a clear message."),
])

# --- automate-me: skills live in .devin/skills ---
rw("skills/automate-me/SKILL.md", [
    ("Look recursively for `.cursor/skills/**/*-mode/SKILL.md` and `~/.cursor/skills/*-mode/SKILL.md` matching the user's handle. Mode skills can live in a personal category directory (`.cursor/skills/<handle>/`), not only at the top level. If one exists, confirm intent with `AskQuestion` (unless they already said \"update my skill\" or similar):",
     "Look recursively for `.devin/skills/**/*-mode/SKILL.md` and `~/.config/devin/skills/*-mode/SKILL.md` matching the user's handle. Mode skills can live in a personal category directory (`.devin/skills/<handle>/`), not only at the top level. If one exists, confirm intent with the user (unless they already said \"update my skill\" or similar):"),
    ("- Path: preserve an existing mode skill's category. For a new mode, use `.cursor/skills/<handle>/<handle>-mode/SKILL.md` when the repo has an established personal category for that handle. Otherwise default to `.cursor/skills/<handle>-mode/SKILL.md` in the project (or `~/.cursor/skills/<handle>-mode/` if the user prefers a personal skill).",
     "- Path: preserve an existing mode skill's category. For a new mode, use `.devin/skills/<handle>/<handle>-mode/SKILL.md` when the repo has an established personal category for that handle. Otherwise default to `.devin/skills/<handle>-mode/SKILL.md` in the project (or `~/.config/devin/skills/<handle>-mode/` if the user prefers a personal skill)."),
    ("Locate the active workspace's transcripts before fanning out. The system prompt names the workspace's `agent-transcripts/` directory. Use only that path. Don't glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.",
     "Devin does not expose Cursor-style workspace transcripts. Use `devin_session_interact`/`devin_session_events` (MCP) for past Devin sessions in this organization, or local Devin CLI session logs when the user points at them. Never scan unrelated sessions; read only what the user names."),
])

# --- recall: transcript format is Cursor-only; degrade ---
rw("skills/recall/SKILL.md", [
    ("Transcripts live at `~/.cursor/projects/<slug>/agent-transcripts/<uuid>/<uuid>.jsonl`, where `<slug>` is the workspace path with the leading slash dropped and each \"/\" turned into \"-\" (so `/Users/you/proj` becomes `Users-you-proj`). Every line is one chat message.",
     "Devin sessions are searchable through the `devin_session_search` and `devin_session_events` MCP tools (cloud sessions) and Devin CLI local session logs. Use those instead of Cursor transcript paths, which do not exist on this host. Each Devin session event is one message or action."),
])

# --- reflect: plugin cache + install dest ---
rw("skills/reflect/SKILL.md", [
    ("Never edit a skill under `plugins/cache/`. Before approval, show its destination, `.cursor/skills/<skill>/` or `~/.cursor/skills/<skill>/`. After approval, copy the skill folder there and edit the copy. Never open a PR or push.",
     "Never edit a skill inside the plugin installation in place. Before approval, show its destination, `.devin/skills/<skill>/` or `~/.config/devin/skills/<skill>/`. After approval, copy the skill folder there and edit the copy. Never open a PR or push."),
])

# --- show-me-your-work: transcript check ---
rw("skills/show-me-your-work/SKILL.md", [
    ("At the end of the run, before handing back, check the log told the truth. Read this run's transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path). Don't glob across `~/.cursor/projects/*/`. That reads unrelated private chats.",
     "At the end of the run, before handing back, check the log told the truth. On Devin, review this session's visible action history (or `devin_session_events` for the current session id when available) rather than Cursor transcripts, which do not exist here. Never read unrelated sessions."),
])

# --- session-pickup playbook ---
rw("skills/poteto-mode/playbooks/session-pickup.md", [
    ("1. Locate the prior trail. A local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names the path. Do not glob across `~/.cursor/projects/*/`, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch.",
     "1. Locate the prior trail. A prior Devin session (search with `devin_session_search`, read with `devin_session_events`), a session URL the user pastes, or a pushed branch. Never scan unrelated private sessions."),
])

# --- eval playbook ---
rw("skills/poteto-mode/playbooks/eval.md", [
    ("6. **Verify the chain from transcripts, not self-report.** Read each candidate's local transcript under the active workspace's `agent-transcripts/` directory (the system prompt names this path). Do not glob across `~/.cursor/projects/*/`. That crosses workspace boundaries and reads private chats from unrelated projects.",
     "6. **Verify the chain from session evidence, not self-report.** Read each candidate's session events with `devin_session_events` when sessions are available, or the artifacts they produced when not. Never scan unrelated private sessions."),
])

print("host refs adapted")
