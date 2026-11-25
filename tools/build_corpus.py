#!/usr/bin/env python3
"""Import upstream pstack corpus into pstack-devin with Devin-native mechanical transforms.

Reads from UPSTREAM_SRC (cursor-plugins/pstack), writes into repo root.
Hand-authored files (listed in SKIP) are not overwritten.
"""
import re, shutil, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UPSTREAM = Path(r"C:/Users/Hafo Creative/pstack-devin-analysis/cursor-plugins/pstack")

# Files we hand-author in this repo; never overwrite.
SKIP_RELPATHS = {
    "skills/poteto-mode/SKILL.md",
    "skills/poteto-mode/scripts/watch-pr",   # ported separately
    "skills/poteto-mode/scripts/bootstrap.ts",
    "skills/poteto-mode/scripts/package.json",
    "skills/poteto-mode/scripts/worktree-audit.sh",  # replaced by .mjs
    "skills/setup-pstack/SKILL.md",
    "skills/statechart/scripts",  # copied from hardened source separately
    "skills/show-me-your-work/scripts/log.sh",  # replaced by log.mjs
}

def transform_frontmatter(text: str, skill_name: str) -> str:
    if not text.startswith("---"):
        return text
    end = text.index("\n---", 3)
    fm = text[3:end]
    body = text[end:]
    lines = fm.splitlines()
    out, had_disable = [], False
    for line in lines:
        s = line.strip()
        if s.startswith("disable-model-invocation:"):
            had_disable = True
            continue
        if s.startswith("icon:") or s.startswith("color:"):
            continue
        out.append(line)
    if had_disable:
        out.append("triggers:")
        out.append("  - user")
    return "---" + "\n".join(out) + body

def transform_body(text: str, relpath: str) -> str:
    t = text
    # Model config path — Devin project-local always-on rule.
    t = t.replace("~/.cursor/rules/pstack-models.mdc", ".devin/rules/pstack-models.md")
    t = t.replace("~/.claude/rules/pstack-models.md", ".devin/rules/pstack-models.md")
    t = t.replace("~/.agents/pstack-models.md", ".devin/rules/pstack-models.md")
    # Slash-command invocations of pstack skills -> plugin namespace.
    t = re.sub(r"(?<![\w`/.-])/([a-z][a-z0-9-]*)", lambda m: "/pstack-devin:" + m.group(1) if m.group(1) in SKILL_NAMES else m.group(0), t)
    return t

def list_skills() -> list[str]:
    return sorted(p.name for p in (UPSTREAM / "skills").iterdir() if (p / "SKILL.md").is_file())

SKILL_NAMES = set()

def should_skip(rel: str) -> bool:
    for skip in SKIP_RELPATHS:
        if rel == skip or rel.startswith(skip.rstrip("/") + "/"):
            return True
    return False

def main() -> int:
    global SKILL_NAMES
    SKILL_NAMES = set(list_skills())
    copied = transformed = 0
    # Copy skill corpus.
    for src in sorted((UPSTREAM / "skills").rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(UPSTREAM).as_posix()
        if "graphify-out" in rel or should_skip(rel):
            continue
        dest = REPO / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        raw = src.read_bytes()
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            dest.write_bytes(raw)
            copied += 1
            continue
        if src.name == "SKILL.md":
            text = transform_frontmatter(text, src.parent.name)
        if relpath_is_doc := re.match(r"^(skills/|docs/|automations/).*\.md$", rel):
            text = transform_body(text, rel)
        dest.write_text(text, encoding="utf-8", newline="\n")
        copied += 1
        transformed += 1
    # automations/benny dormant reference copy (no scripts execution content changes beyond body refs).
    benny_src = UPSTREAM / "automations" / "benny"
    if benny_src.is_dir():
        for src in sorted(benny_src.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(UPSTREAM).as_posix()
            dest = REPO / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                text = src.read_text(encoding="utf-8")
                dest.write_text(transform_body(text, rel), encoding="utf-8", newline="\n")
            except UnicodeDecodeError:
                shutil.copy2(src, dest)
            copied += 1
    # upstream docs (guide etc) for reference adaptation.
    docs_src = UPSTREAM / "docs"
    if docs_src.is_dir():
        for src in sorted(docs_src.rglob("*")):
            if not src.is_file():
                continue
            rel = src.relative_to(UPSTREAM).as_posix()
            dest = REPO / "docs" / "upstream" / src.relative_to(docs_src).as_posix()
            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                text = src.read_text(encoding="utf-8")
                dest.write_text(transform_body(text, rel), encoding="utf-8", newline="\n")
            except UnicodeDecodeError:
                shutil.copy2(src, dest)
            copied += 1
    print(f"copied={copied} transformed={transformed} skills={len(SKILL_NAMES)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
