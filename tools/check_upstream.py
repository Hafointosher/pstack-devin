#!/usr/bin/env python3
"""Check whether upstream pstack has drifted from the mirrored snapshot.

Fetches cursor/plugins (sparse, blobless) into a temp cache, then compares the
raw upstream `pstack/` tree at the mirrored commit (UPSTREAM.json) against the
tree at upstream HEAD. Raw-tree comparison needs no transformation re-run: if
the trees are identical there is zero upstream drift, regardless of what local
transformations the port applies.

Exit codes: 0 = in sync, 1 = drift detected, 2 = error (network, missing commit).
The temp clone is always removed.

Usage: python tools/check_upstream.py [--verbose]
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
UPSTREAM_REPO = "https://github.com/cursor/plugins"

# Files the port hand-authors rather than transforms verbatim. Drift in these
# needs a human re-port decision, not a transformer re-run. Keep in sync with
# SKIP_RELPATHS in build_corpus.py.
HAND_AUTHORED = [
    "skills/poteto-mode/SKILL.md",
    "skills/poteto-mode/scripts/watch-pr",
    "skills/poteto-mode/scripts/bootstrap.ts",
    "skills/poteto-mode/scripts/package.json",
    "skills/poteto-mode/scripts/worktree-audit.sh",
    "skills/setup-pstack/SKILL.md",
    "skills/statechart/scripts",
    "skills/show-me-your-work/scripts/log.sh",
]


def run(cmd, cwd=None, check=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {r.stderr.strip()[:400]}")
    return r


def tree_listing(clone: Path, ref: str) -> dict[str, str]:
    """Map of pstack-relative path -> blob sha at ref. Empty dict if ref/tree missing."""
    r = run(["git", "ls-tree", "-r", ref, "--", "pstack"], cwd=clone, check=False)
    if r.returncode != 0 or not r.stdout.strip():
        return {}
    out = {}
    for line in r.stdout.splitlines():
        # "<mode> blob <sha>\tpstack/<path>"
        meta, path = line.split("\t", 1)
        sha = meta.split()[2]
        out[path] = sha
    return out


def is_hand_authored(rel: str) -> bool:
    return any(rel == h or rel.startswith(h.rstrip("/") + "/") for h in HAND_AUTHORED)


def main() -> int:
    verbose = "--verbose" in sys.argv
    upstream = json.loads((REPO / "UPSTREAM.json").read_text(encoding="utf-8"))
    mirror_commit = upstream["upstreamCommit"]
    mirror_version = upstream["upstreamVersion"]
    print(f"mirrored: commit={mirror_commit} version={mirror_version}")

    cache = Path(tempfile.mkdtemp(prefix="pstack-upstream-"))
    try:
        print("fetching upstream (sparse, blobless)...")
        run(["git", "clone", "--filter=blob:none", "--sparse", "--no-checkout", UPSTREAM_REPO, str(cache)])
        run(["git", "fetch", "origin", "main", "--depth=50"], cwd=cache, check=False)

        # Resolve upstream HEAD and the mirrored commit.
        head = run(["git", "rev-parse", "origin/main"], cwd=cache).stdout.strip()
        have_mirror = run(["git", "cat-file", "-e", mirror_commit], cwd=cache, check=False).returncode == 0
        if not have_mirror:
            # Blobless clone may need the object; try fetching it specifically.
            run(["git", "fetch", "origin", mirror_commit, "--depth=1"], cwd=cache, check=False)
            have_mirror = run(["git", "cat-file", "-e", mirror_commit], cwd=cache, check=False).returncode == 0
        if not have_mirror:
            print(f"error: mirrored commit {mirror_commit} not found upstream (rewritten history?)", file=sys.stderr)
            return 2
        print(f"upstream HEAD: {head[:10]}")

        # Upstream version at HEAD.
        r = run(["git", "show", "origin/main:pstack/plugin.json"], cwd=cache, check=False)
        head_version = "unknown"
        if r.returncode == 0:
            try:
                head_version = json.loads(r.stdout).get("version", "unknown")
            except json.JSONDecodeError:
                pass
        print(f"versions: mirrored={mirror_version} upstream-head={head_version}")

        mirror_tree = tree_listing(cache, mirror_commit)
        head_tree = tree_listing(cache, head)
        if not mirror_tree:
            print(f"error: no pstack/ tree at mirrored commit {mirror_commit}", file=sys.stderr)
            return 2
        if not head_tree:
            print("error: no pstack/ tree at upstream HEAD", file=sys.stderr)
            return 2

        added = sorted(p for p in head_tree if p not in mirror_tree)
        removed = sorted(p for p in mirror_tree if p not in head_tree)
        changed = sorted(p for p in head_tree if p in mirror_tree and head_tree[p] != mirror_tree[p])

        if not added and not removed and not changed:
            print(f"\nIN SYNC: pstack/ tree identical between {mirror_commit[:10]} and upstream HEAD "
                  f"({len(head_tree)} files compared). No upstream drift since {mirror_version}.")
            return 0

        print(f"\nDRIFT DETECTED: +{len(added)} added, -{len(removed)} removed, ~{len(changed)} changed")
        def report(label, paths):
            if not paths:
                return
            print(f"\n{label}:")
            for p in paths:
                rel = p[len("pstack/"):] if p.startswith("pstack/") else p
                kind = "HAND-AUTHORED (needs manual re-port)" if is_hand_authored(rel) else "transformed (re-run pipeline)"
                print(f"  {p}  [{kind}]")
        report("added", added)
        report("removed", removed)
        report("changed", changed)
        print("\nnext steps per MIRRORING.md: re-run transformers over the new snapshot in a")
        print("scratch copy, review diffs by hand, update UPSTREAM.json, run validation.")
        return 1
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    finally:
        shutil.rmtree(cache, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
