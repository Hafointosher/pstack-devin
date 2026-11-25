#!/usr/bin/env python3
"""Adapt setup-pstack for Devin and write agent profiles."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UP = Path(r"C:/Users/Hafo Creative/pstack-devin-analysis/cursor-plugins/pstack")

def adapt_setup():
    src = (UP / "skills/setup-pstack/SKILL.md").read_text(encoding="utf-8")
    t = src
    t = t.replace("~/.cursor/rules/pstack-models.mdc", ".devin/rules/pstack-models.md")
    t = t.replace(
        "Write `.devin/rules/pstack-models.md`, an always-applied rule that sets pstack's model per role.",
        "Write `.devin/rules/pstack-models.md`, a project-local always-on Devin rule that sets pstack's model per role, and optionally generate project-local `.devin/agents/` profile overrides after explicit user confirmation. Never write outside the project without confirmation, never edit plugin files in place."
    )
    t = t.replace(
        "Enumerate the model slugs you can pass to a `Task` subagent in this session. That is the dependable source. If Cursor also exposes a models API or CLI that lists the user's entitled models, prefer it for completeness. If you cannot detect any, ask the user to paste the slugs they have access to.",
        "Run `devin models list --format json` and read the model `uid` values. That is the dependable source. If the command fails, ask the user to paste the slugs they have access to."
    )
    # frontmatter triggers: setup should be user-invocable (it is a slash command); leave invocable by default but add user trigger per upstream explicit-only posture? upstream has no disable flag, keep as is.
    (REPO / "skills/setup-pstack/SKILL.md").write_text(t, encoding="utf-8", newline="\n")
    print("setup-pstack adapted")

AGENT_HEADER = {
    "poteto-agent": ("claude-opus-5-5-xhigh-fast", "Delegate subagent for code-writing and helper tasks spawned during a `/pstack-devin:poteto-mode` run."),
    "poteto-worker": ("claude-opus-5-5-high-fast", "Mechanical-edit worker for swarm-style fan-out in pstack."),
    "poteto-runner-fable": ("claude-fable-5-2-high", "Arena/interrogate panel runner seat (Fable)."),
    "poteto-runner-opus": ("claude-opus-5-5-high-fast", "Arena/interrogate panel runner seat (Opus)."),
    "poteto-runner-gemini": ("gemini-4-neon-xhigh", "Arena/interrogate panel runner seat (Gemini)."),
    "poteto-reviewer-opus": ("claude-opus-5-5-high-fast", "Read-only reviewer seat (Opus) for arena/interrogate."),
    "poteto-reviewer-gemini": ("gemini-4-neon-xhigh", "Read-only reviewer seat (Gemini) for arena/interrogate."),
}

def write_agents():
    up_agent = (UP / "agents/poteto-agent.md").read_text(encoding="utf-8")
    body = up_agent.split("---", 2)[2]
    # Adapt the body: replace Cursor plugin search path instruction.
    body = body.replace(
        "With no path, before any other work, search `~/.cursor/plugins/` for a file whose path ends in `skills/poteto-mode/SKILL.md`. If more than one file matches, use the copy whose `.cursor-plugin/plugin.json` has the highest `version`. Your skill catalog hides this skill, so a missing catalog entry does not mean pstack is absent. If no such file exists, stop and tell your parent.",
        "With no path, before any other work, search the Devin plugin cache (`~/.devin/plugins/` or the path your parent session reports) for a file whose path ends in `skills/poteto-mode/SKILL.md`; if the user installed from source, also check the checkout they named. If more than one file matches, use the copy whose `.devin-plugin/plugin.json` has the highest `version`. Your skill catalog hides this skill, so a missing catalog entry does not mean pstack is absent. If no such file exists, stop and tell your parent."
    )
    body = body.replace("`/poteto-mode`", "`/pstack-devin:poteto-mode`")
    for name, (model, desc) in AGENT_HEADER.items():
        fm = f"---\nname: {name}\ndescription: {desc}\nmodel: {model}\n---\n"
        if name == "poteto-agent":
            content = fm + body
        else:
            note = "\n\nRead the `poteto-mode` skill's `SKILL.md` in full before doing any work, including its inline Principles index, using the absolute path your parent gave you. If none was given, locate it as the poteto-agent profile describes. Navigate to a leaf `principle-*` skill whenever you apply that principle.\n"
            ro = ""
            if "reviewer" in name:
                ro = "\nYou are a read-only reviewer. Never edit files, never commit, never push. Report findings only.\n"
            content = fm + f"\n# {name}\n" + note + ro + "\nYou are one seat in a pstack panel or fan-out. Follow your kickoff exactly; the bar in it is the whole bar.\n"
        (REPO / "agents" / f"{name}.md").write_text(content, encoding="utf-8", newline="\n")
    # comment-sicko
    sicko = (UP / "agents/comment-sicko.md").read_text(encoding="utf-8")
    sicko = sicko.replace("is_background: true\n", "")
    (REPO / "agents/comment-sicko.md").write_text(sicko, encoding="utf-8", newline="\n")
    print("agents written:", sorted(p.name for p in (REPO/'agents').glob('*.md')))

adapt_setup()
write_agents()
