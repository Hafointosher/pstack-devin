#!/usr/bin/env python3
"""Apply surgical Devin adaptations to core files copied from upstream."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UP = Path(r"C:/Users/Hafo Creative/pstack-devin-analysis/cursor-plugins/pstack")

def adapt_poteto_mode():
    src = (UP / "skills/poteto-mode/SKILL.md").read_text(encoding="utf-8")
    t = src
    # Frontmatter: Devin format
    t = t.replace("disable-model-invocation: true\nicon: crown\ncolor: yellow\n", "triggers:\n  - user\n")
    # Devin has no cursor-team-kit; degrade deslop/control-ui/control-cli explicitly.
    t = t.replace(
        "- Before commit → `/deslop` from the `cursor-team-kit` plugin. Before review → **no-comments**.",
        "- Before review → **no-comments**. (`cursor-team-kit`'s `/deslop` is Cursor-only and not ported; review slop manually per **unslop**.)"
    )
    t = t.replace(
        "- Shipping UI / IDE / CLI → `control-ui` or `control-cli` from `cursor-team-kit`.",
        "- Shipping UI / IDE / CLI → drive it with the best available tool (Devin browser/desktop tools, Playwright MCP, or the app's own CLI) and verify visually or behaviorally; `cursor-team-kit`'s `control-ui`/`control-cli` are Cursor-only."
    )
    t = t.replace(
        "- PR status → the **Babysit** playbook, not Cursor's built-in babysit skill. Landing a green stack → the **Shipping** playbook.",
        "- PR status → the **Babysit** playbook. Landing a green stack → the **Shipping** playbook."
    )
    # Subagent section: rewrite for Devin run_subagent profiles.
    old_sub_start = t.index("## Subagents")
    old_sub_end = t.index("## Writing the reply")
    devin_sub = """## Subagents

**Use the `poteto-agent` custom subagent profile for any subagent you spawn directly inside a playbook step.** In Devin this means `run_subagent` with `profile: "poteto-agent"`. The chat that receives `/pstack-devin:poteto-mode` runs the playbook itself. Routed workflow skills (`interrogate`, `swarm`) choose their own profiles. Respect it.

**Defaults for every spawn.** Background execution where supported, file pointers not inlined context, and an explicit model per role. The custom profiles ship pinned upstream default models; `/pstack-devin:setup-pstack` writes `.devin/rules/pstack-models.md` and can generate project-local `.devin/agents/` overrides whose per-role lines override the pinned defaults below and the role models in the routed skills (`arena`, `swarm`, `interrogate`). A role with no line keeps its default. A line of `inherit-parent` or `auto` means use the `subagent_general` profile (which inherits the parent model) for write-capable work, or a generated unpinned profile for read-only work. If the rule has no `# defaults: 3` line, an older setup wrote it. Keep honoring its lines, and tell the user once per session to rerun `/pstack-devin:setup-pstack`.

- Code, prose, and judgment: `claude-opus-5-5-xhigh-fast` (profile `poteto-agent`).
- Trivial mechanical edits: `claude-opus-5-5-high-fast` (profile `poteto-worker`).
- Diverse review and design panels: one runner each on `claude-fable-5-2-high` (`poteto-runner-fable`), `claude-opus-5-5-high-fast` (`poteto-runner-opus`), and `gemini-4-neon-xhigh` (`poteto-runner-gemini`); reviewers use `poteto-reviewer-opus` / `poteto-reviewer-gemini` (read-only instructions).

Devin spawns subagents by profile, not by per-call model, so model routing is encoded in these profiles. Validate slugs with `devin models list --format json` before relying on them; a missing slug falls back to the generated project override, then the closest validated same-family slug, then `agent.subagent_model`, then `subagent_general`. Disclose every fallback.

**Fable 5.2 is an exception.** It runs outside a panel only when the user named it for this task or two Opus 5.5 xhigh runs of the same brief failed its check. Say which. Difficulty alone never qualifies.

**Match the model to the job.** Start from the role's line or default, keep its family, and set the level the job needs. The `/pstack-devin:setup-pstack` budget sets each role's starting level. Panel seats keep their listed level. Raise any other role one step, up to xhigh, for the hardest or subtlest work, lower it one step for judgment, and two or more steps for routine work. No role runs above xhigh. Raising or lowering a role's level means generating or editing the project-local profile override for it (the setup skill automates this); plugin-shipped pins do not change. Opus 5.5 always runs its `-fast` slug. Verification always runs on the `swarm workers` model, `claude-opus-5-5-high-fast` by default. A Gemini seat runs at `gemini-4-neon-xhigh` unless its line names another level.

You own every subagent's work. Review the diff and write your own summary. A second opinion is the same prompt on another vendor's model.

**Fresh subagents by default.** Give a fix round, a follow-up, a retry, or the next queue item to a fresh subagent with the original brief, every later directive, and the prior agent's report and branch. In Devin, `run_subagent` has a `resume` parameter for continuing an existing agent; use it only when the work needs state that lives in it and is costly to move: its checkout, its uncommitted changes, or a process it still runs.

"""
    t = t[:old_sub_start] + devin_sub + t[old_sub_end:]
    # Task subagent phrasing in non-negotiables
    t = t.replace(
        "Starting any agent, whether a Task subagent or a Project worker →",
        "Starting any agent, whether a spawned subagent or a project worker →"
    )
    (REPO / "skills/poteto-mode/SKILL.md").write_text(t, encoding="utf-8", newline="\n")
    print("poteto-mode adapted")

def adapt_setup():
    src = (UP / "skills/setup-pstack/SKILL.md").read_text(encoding="utf-8")
    print("--- upstream setup-pstack length:", len(src.splitlines()))
    return src

adapt_poteto_mode()
src = adapt_setup()
print(src[:3000])
