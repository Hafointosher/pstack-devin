#!/usr/bin/env python3
"""Validate pstack-devin packaging: manifest, skills, frontmatter, links."""
import json, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
errors, warnings = [], []

def err(m): errors.append(m)
def warn(m): warnings.append(m)

# 1. Manifest
mp = REPO / ".devin-plugin/plugin.json"
if not mp.is_file(): err("missing .devin-plugin/plugin.json")
else:
    try:
        manifest = json.loads(mp.read_text(encoding="utf-8"))
        for key in ("name", "version"):
            if key not in manifest: err(f"plugin.json missing {key}")
    except json.JSONDecodeError as e: err(f"plugin.json invalid JSON: {e}")

# 2. Skills inventory
skills = sorted(p.parent.name for p in (REPO / "skills").glob("*/SKILL.md"))
if len(skills) != 59: err(f"expected 59 skills, found {len(skills)}")
principles = [s for s in skills if s.startswith("principle-")]
if len(principles) != 24: err(f"expected 24 principle skills, found {len(principles)}")

# 3. Frontmatter checks
for sk in sorted((REPO / "skills").glob("*/SKILL.md")):
    text = sk.read_text(encoding="utf-8")
    rel = sk.relative_to(REPO).as_posix()
    if not text.startswith("---"): err(f"{rel}: no frontmatter"); continue
    try: fm = text[3:text.index("\n---", 3)]
    except ValueError: err(f"{rel}: unterminated frontmatter"); continue
    if "name:" not in fm: err(f"{rel}: no name")
    if "description:" not in fm: err(f"{rel}: no description")
    for bad in ("disable-model-invocation", "icon:", "color:"):
        if bad in fm: err(f"{rel}: cursor-only frontmatter key {bad}")

# 4. Playbooks
pb = sorted((REPO / "skills/poteto-mode/playbooks").glob("*.md")) if (REPO/"skills/poteto-mode/playbooks").is_dir() else []
if len(pb) != 22: err(f"expected 22 playbooks, found {len(pb)}")

# 5. Helpers exist
for h in ("skills/poteto-mode/scripts/watch-pr/watch-pr",
          "skills/poteto-mode/scripts/watch-pr/watch-pr.cmd",
          "skills/poteto-mode/scripts/worktree-audit.mjs",
          "skills/show-me-your-work/scripts/log.mjs",
          "skills/statechart/scripts/statechart.ts"):
    if not (REPO / h).is_file(): err(f"missing helper {h}")

# 6. Agents
agents = sorted(p.name for p in (REPO / "agents").glob("*.md"))
need = {"poteto-agent.md","poteto-worker.md","poteto-runner-fable.md","poteto-runner-opus.md","poteto-runner-gemini.md","poteto-reviewer-opus.md","poteto-reviewer-gemini.md","comment-sicko.md"}
missing = need - set(agents)
if missing: err(f"missing agents: {sorted(missing)}")

# 7. Leftover host-specific references in skill bodies (warnings, triaged in docs)
patterns = [r"cursor-team-kit", r"/loop", r"subagent_type", r"generalPurpose", r"~/.cursor", r"\.mdc", r"Bun", r"bun", r"mise"]
leftovers = {}
for sk in sorted((REPO / "skills").rglob("*.md")):
    text = sk.read_text(encoding="utf-8")
    rel = sk.relative_to(REPO).as_posix()
    hits = sorted({p for p in patterns for m in re.finditer(p, text) if m})
    if hits: leftovers[rel] = hits

print(f"skills={len(skills)} principles={len(principles)} playbooks={len(pb)} agents={len(agents)}")
print(f"errors={len(errors)} warnings={len(warnings)}")
for e in errors: print("ERROR:", e)
print(f"files-with-host-leftovers={len(leftovers)}")
for f, h in sorted(leftovers.items())[:80]: print("LEFTOVER:", f, ",".join(h))
sys.exit(1 if errors else 0)
