#!/usr/bin/env python3
"""Windows smoke tests for pstack-devin helpers. Runs real commands, asserts real behavior."""
import json, os, subprocess, sys, tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NODE = ["node", "--disable-warning=ExperimentalWarning"]
failures = []
passed = []

def check(name, cond, detail=""):
    (passed if cond else failures).append(f"{name}{' :: '+detail if detail and not cond else ''}")
    print(("PASS" if cond else "FAIL"), name, detail if detail and not cond else "")

def run(cmd, cwd=None):
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=60)

# --- log.mjs ---
with tempfile.TemporaryDirectory() as td:
    logf = os.path.join(td, "sub dir", "decisions.tsv")
    r = run(["node", str(REPO/"skills/show-me-your-work/scripts/log.mjs"), logf, "decide x", "because y", "evidence z", "next w"])
    check("log.mjs exit 0", r.returncode == 0, r.stderr[:200])
    content = Path(logf).read_text(encoding="utf-8") if Path(logf).exists() else ""
    lines = content.splitlines()
    check("log.mjs header + row", len(lines) == 2 and lines[0].startswith("ts\tdecision"))
    check("log.mjs path with spaces", Path(logf).exists())
    check("log.mjs tab-separated", len(lines[1].split("\t")) == 5 if len(lines) == 2 else False)
    # formula escaping
    r2 = run(["node", str(REPO/"skills/show-me-your-work/scripts/log.mjs"), logf, "=evil", "+x", "-y", "@z"])
    row2 = Path(logf).read_text(encoding="utf-8").splitlines()[2]
    check("log.mjs formula escape", "'=evil" in row2 and "'+x" in row2, row2)
    # arity error
    r3 = run(["node", str(REPO/"skills/show-me-your-work/scripts/log.mjs"), logf, "only", "two"])
    check("log.mjs bad arity nonzero", r3.returncode != 0)
    # tabs/newlines normalized
    run(["node", str(REPO/"skills/show-me-your-work/scripts/log.mjs"), logf, "a\tb", "c\nd", "e", "f"])
    row3 = Path(logf).read_text(encoding="utf-8").splitlines()[3]
    check("log.mjs tab/newline normalized", len(row3.split("\t")) == 5, row3)

# --- worktree-audit.mjs ---
with tempfile.TemporaryDirectory() as td:
    run(["git", "init", "-q"], cwd=td)
    run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init"], cwd=td)
    r = run(["node", str(REPO/"skills/poteto-mode/scripts/worktree-audit.mjs"), td])
    check("worktree-audit exit 0", r.returncode == 0, r.stderr[:200])
    try:
        data = json.loads(r.stdout)
        check("worktree-audit valid json", True)
        check("worktree-audit deletionAuthorized false", data.get("deletionAuthorized") is False)
        check("worktree-audit main held", data["worktrees"][0]["bucket"] == "hold-main", str(data["worktrees"][0].get("bucket")))
        check("worktree-audit no network fields", data.get("remotePrState") == "not-queried")
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        check("worktree-audit valid json", False, str(e) + r.stdout[:200])

# --- watch-pr arg parsing ---
wp = REPO/"skills/poteto-mode/scripts/watch-pr/watch-pr"
r = run(NODE + [str(wp), "--help"])
check("watch-pr --help exit 0", r.returncode == 0, (r.stderr or r.stdout)[:200])
check("watch-pr help text", "queued" in r.stdout)
r = run(NODE + [str(wp), "--pr", "abc"])
check("watch-pr rejects bad pr", r.returncode == 64, f"rc={r.returncode}")
r = run(NODE + [str(wp), "--stack-prs", "1,1", "--queued-stack"])
check("watch-pr rejects duplicate stack", "duplicate" in (r.stderr + r.stdout).lower(), (r.stderr+r.stdout)[:150])
r = run(NODE + [str(wp), "--stack-prs", "1,2"])
check("watch-pr stack-prs requires queued-stack", "requires --queued-stack" in (r.stderr + r.stdout), (r.stderr+r.stdout)[:150])
r = run(NODE + [str(wp), "--interval", "-5"])
check("watch-pr rejects negative interval", r.returncode == 64)
r = run(NODE + [str(wp), "--bogus"])
check("watch-pr unknown option", "unknown option" in (r.stderr+r.stdout), (r.stderr+r.stdout)[:150])

# --- watch-pr behavioral coverage ---
# End-to-end behavior is covered in-process by the upstream test suite ported to node:test
# (cli.test.ts / github.test.ts / policy.test.ts with fake readers). Run it here and count results.
r = run(NODE + ["--test",
    str(REPO/"skills/poteto-mode/scripts/watch-pr/cli.test.ts"),
    str(REPO/"skills/poteto-mode/scripts/watch-pr/github.test.ts"),
    str(REPO/"skills/poteto-mode/scripts/watch-pr/policy.test.ts")])
out = r.stdout
import re as _re
passm = _re.search(r"pass (\d+)$", out, _re.M)
failm = _re.search(r"fail (\d+)$", out, _re.M)
npass = int(passm.group(1)) if passm else 0
nfail = int(failm.group(1)) if failm else -1
check("watch-pr node:test suite 53 pass 0 fail", npass == 53 and nfail == 0, f"pass={npass} fail={nfail}")

# --- statechart usage ---
r = run(NODE + [str(REPO/"skills/statechart/scripts/statechart.ts")])
check("statechart usage nonzero", r.returncode != 0)
check("statechart usage text", "SPEC" in (r.stdout + r.stderr))

print(f"\n{len(passed)} passed, {len(failures)} failed")
sys.exit(1 if failures else 0)
