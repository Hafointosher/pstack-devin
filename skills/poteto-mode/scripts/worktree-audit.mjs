#!/usr/bin/env node
// Adapted from Lauren Tan pstack (MIT); see repository LICENSE.
// Read-only worktree prune audit: size, age, merge state, uncommitted work,
// remote/PR state per worktree, with a suggested bucket. Never deletes anything
// and no bucket authorizes deletion — the human gates in the playbook do.
// Devin adaptation: there is no Cursor transcript scan (chats are not local
// files), so recency verification is a user-confirmation gate in the playbook,
// and the PR lookup is a best-effort gh query, empty when gh is unavailable.
// The base fetch is best-effort like upstream: a stale base only makes the
// merged column conservative, never wrong in the unsafe direction.
import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const git = (cwd, args) => spawnSync('git', ['--no-optional-locks', '-c', 'core.fsmonitor=false', '-C', cwd, ...args], {
  encoding: 'utf8', timeout: 15000, env: { ...process.env, GIT_OPTIONAL_LOCKS: '0', GIT_TERMINAL_PROMPT: '0' },
});

function dirSizeBytes(root) {
  let total = 0;
  const stack = [root];
  while (stack.length) {
    const dir = stack.pop();
    let entries;
    try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { continue; }
    for (const e of entries) {
      const p = path.join(dir, e.name);
      try {
        if (e.isDirectory()) { if (e.name !== '.git') stack.push(p); }
        else total += fs.statSync(p).size;
      } catch {}
    }
  }
  return total;
}

function resolveBase(repo, requested) {
  if (requested) return { base: requested, warning: null };
  for (const cand of ['origin/HEAD', 'origin/main', 'origin/master']) {
    const ref = cand === 'origin/HEAD'
      ? git(repo, ['symbolic-ref', '--short', 'refs/remotes/origin/HEAD'])
      : null;
    const name = cand === 'origin/HEAD'
      ? (ref && ref.status === 0 ? ref.stdout.trim() : '')
      : cand;
    if (name && git(repo, ['rev-parse', '--verify', '--end-of-options', `${name}^{commit}`]).status === 0)
      return { base: name, warning: `no -b given; merged checks against ${name}` };
  }
  return { base: null, warning: 'no base ref (origin/HEAD, origin/main, origin/master all missing); pass a base ref' };
}

function listPrs(repo) {
  const gh = spawnSync('gh', ['pr', 'list', '--author', '@me', '--state', 'all', '--limit', '1000', '--json', 'number,state,headRefName'], {
    encoding: 'utf8', timeout: 20000, cwd: repo, env: { ...process.env, GH_PROMPT_DISABLED: '1' },
  });
  if (gh.status !== 0 || !gh.stdout) return { prs: [], source: 'unavailable' };
  try {
    return {
      prs: JSON.parse(gh.stdout).map((p) => ({ number: p.number, state: String(p.state).toLowerCase(), head: p.headRefName })),
      source: 'gh',
    };
  } catch { return { prs: [], source: 'unavailable' }; }
}

export function audit(repo = '.', requestedBase) {
  const top = git(repo, ['rev-parse', '--show-toplevel']);
  if (top.status !== 0) throw new Error(`not a git repo: ${repo}`);
  repo = top.stdout.trim();

  const { base, warning } = resolveBase(repo, requestedBase);
  const warnings = warning ? [warning] : [];

  // Best-effort fetch of the base, as upstream does; staleness only makes the
  // merged column conservative. With no base at all (a local-only repo) the
  // audit still runs: every merge check degrades to null and nothing is ever
  // safe-by-merge-evidence.
  if (base && base.startsWith('origin/')) {
    const fetch = git(repo, ['fetch', 'origin', `+refs/heads/${base.slice(7)}:refs/remotes/${base}`, '--quiet']);
    if (fetch.status !== 0) warnings.push(`could not fetch ${base}; merged column may be stale`);
  }
  const ref = base ? git(repo, ['rev-parse', '--verify', '--end-of-options', `${base}^{commit}`]) : null;
  const baseSha = ref && ref.status === 0 ? ref.stdout.trim() : null;
  if (base && !baseSha) warnings.push(`base ref not found: ${base}; merged column is unknown`);

  const listing = git(repo, ['worktree', 'list', '--porcelain', '-z']);
  if (listing.status !== 0) throw new Error(`Cannot list worktrees: ${listing.error?.message ?? listing.stderr.trim()}`);
  const records = [];
  let current = null;
  for (const field of listing.stdout.split('\0')) {
    if (field.startsWith('worktree ')) { current = { path: field.slice(9) }; records.push(current); }
    else if (current && field) {
      const split = field.indexOf(' ');
      current[split < 0 ? field : field.slice(0, split)] = split < 0 ? true : field.slice(split + 1);
    }
  }

  const { prs, source: prSource } = listPrs(repo);
  const now = Math.floor(Date.now() / 1000);

  return {
    schemaVersion: 2, base, baseSha, warnings,
    prSource, chatActivity: 'not-available-on-devin', deletionAuthorized: false,
    worktrees: records.map((entry, index) => {
      const status = git(entry.path, ['status', '--porcelain=v1', '--untracked-files=all']);
      const lines = status.status === 0 ? status.stdout.split('\n').filter(Boolean) : [];
      const wip = lines.filter((l) => !l.startsWith('??')).length;
      const scratch = lines.filter((l) => l.startsWith('??')).length;
      const dirty = status.status !== 0 ? 'unknown' : lines.length === 0 ? 'clean' : wip > 0 ? `wip:${wip}` : `scratch:${scratch}`;

      const head = git(entry.path, ['rev-parse', '--verify', 'HEAD']);
      const headSha = head.status === 0 ? head.stdout.trim() : null;
      const ts = git(entry.path, ['log', '-1', '--format=%ct', 'HEAD']);
      const ageDays = ts.status === 0 && Number(ts.stdout.trim()) > 0
        ? Math.floor((now - Number(ts.stdout.trim())) / 86400) : null;

      const ancestry = headSha && baseSha ? git(repo, ['merge-base', '--is-ancestor', headSha, baseSha]) : null;
      const mergedIntoLocalBase = ancestry?.status === 0 ? true : ancestry?.status === 1 ? false : null;

      const branchRef = git(entry.path, ['symbolic-ref', '--quiet', '--short', 'HEAD']);
      const branch = branchRef.status === 0 ? branchRef.stdout.trim() : null;
      let remote;
      if (!branch) remote = 'detached';
      else if (git(entry.path, ['show-ref', '--verify', '--quiet', `refs/remotes/origin/${branch}`]).status !== 0) remote = 'no-remote';
      else {
        const remoteSha = git(entry.path, ['rev-parse', `origin/${branch}`]);
        if (remoteSha.status === 0 && remoteSha.stdout.trim() === headSha) remote = 'pushed';
        else {
          const count = git(entry.path, ['rev-list', '--count', `origin/${branch}..HEAD`]);
          remote = `ahead${count.status === 0 ? count.stdout.trim() : '?'}`;
        }
      }

      const pr = branch ? prs.find((p) => p.head === branch) : null;
      const prState = pr ? `#${pr.number}/${pr.state}` : null;

      const sizeBytes = fs.existsSync(entry.path) ? dirSizeBytes(entry.path) : 0;

      // Buckets. wip always holds. An open or draft PR holds. Everything else
      // is review or safe-by-merge-evidence, but no bucket authorizes deletion:
      // without transcript evidence there is no recency signal on Devin, so
      // the playbook's user-confirmation gate decides every candidate.
      let bucket;
      if (index === 0) bucket = 'hold-main';
      else if (entry.locked) bucket = 'hold-locked';
      else if (status.status !== 0 || !headSha) bucket = 'hold-unknown';
      else if (wip > 0) bucket = 'hold-wip';
      else if (pr && (pr.state === 'open' || pr.state === 'draft')) bucket = 'hold-open-pr';
      else if (mergedIntoLocalBase === true || pr) bucket = 'safe-by-merge-evidence';
      else bucket = 'review';

      return {
        path: entry.path, branch, detached: !branch,
        locked: entry.locked ?? false, prunable: entry.prunable ?? false,
        headSha, ageDays, sizeBytes,
        mergedIntoLocalBase, dirty, remote, pr: prState,
        bucket, deletionAuthorized: false,
        error: status.status !== 0 ? status.error?.message ?? status.stderr.trim() : null,
      };
    }),
  };
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  if (args.includes('--help') || args.includes('-h')) {
    console.log('Usage: node worktree-audit.mjs [-b|--base <ref>] [repo-path]\nRead-only JSON audit: size, age, merge state, dirty split, remote/PR state, bucket.\nBest-effort base fetch and gh PR lookup. No result authorizes deletion.');
  } else {
    let base; const rest = [];
    for (let i = 0; i < args.length; i++) {
      if (args[i] === '-b' || args[i] === '--base') { base = args[++i]; if (base === undefined) { console.error(`error: ${args[i - 1]} needs a ref`); process.exit(2); } }
      else if (args[i].startsWith('-')) { console.error(`error: unknown option: ${args[i]}`); process.exit(2); }
      else rest.push(args[i]);
    }
    if (rest.length > 1) { console.error('Too many arguments'); process.exit(2); }
    try { console.log(JSON.stringify(audit(rest[0], base), null, 2)); }
    catch (error) { console.error(error.message); process.exitCode = 1; }
  }
}
