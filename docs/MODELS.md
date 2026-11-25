# Model routing architecture

Upstream Cursor spawns subagents with a per-call `model` argument. Devin's `run_subagent` selects a **profile**, not a model. This port therefore encodes routing in custom subagent profiles, each pinned to an upstream default model:

| Profile | Model | Role |
|---|---|---|
| poteto-agent | claude-opus-5-5-xhigh-fast | code/prose/judgment delegates |
| poteto-worker | claude-opus-5-5-high-fast | mechanical swarm workers + verification |
| poteto-runner-fable | claude-fable-5-2-high | panel seat |
| poteto-runner-opus | claude-opus-5-5-high-fast | panel seat |
| poteto-runner-gemini | gemini-4-neon-xhigh | panel seat |
| poteto-reviewer-opus | claude-opus-5-5-high-fast | read-only reviewer |
| poteto-reviewer-gemini | gemini-4-neon-xhigh | read-only reviewer |
| comment-sicko | (unpinned) | comment reviewer |

The default pins are the high-fidelity, high-cost upstream posture. `/pstack-devin:setup-pstack` is the cost-control mechanism: it validates slugs against `devin models list --format json`, takes the user's budget (`large`/`medium`/`small`), writes `.devin/rules/pstack-models.md`, and with explicit confirmation generates project-local `.devin/agents/` overrides. Plugin files are never edited in place.

Fallback order when a slug/profile is unavailable: project override → user override → plugin pinned default → nearest validated same-family slug → `agent.subagent_model` → `subagent_general` → serial execution. Every fallback is disclosed.

Known imperfect edge: a read-only subagent at exactly the parent's model. `subagent_explore` is read-only but uses the router default, not the parent model; `subagent_general` inherits the parent but is write-capable. Choose per task and disclose.
