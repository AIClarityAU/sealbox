// Guards the scratch-directory / .gitignore pairing (#1967).
//
// Runs on plain Node (no deps): `node --test scripts/scratch-dirs-ignored.test.js`.
// Wired into CI's `test` job (ci.yml) via its `*.test.js` discovery under
// `.github/scripts` and `scripts`, so this suite cannot silently stop running.
//
// Why this exists: `.local/` was adopted as a multi-session scratch directory
// without a matching `.gitignore` entry, so any sweeping `git add`/`git add -A`
// published every concurrent session's drafts in one commit (#1967). The repo
// already had two machine-local scratch directories correctly ignored
// (`.codegraph/`, `.minspec/queue/` and friends) — the convention and the
// ignore file had simply drifted apart for the third one, silently.
//
// SCRATCH_DIRS below is the single source of truth for "directories used as
// per-session/machine-local scratch". Adding a new scratch directory to the
// repo's conventions (in docs, AGENTS.md, session tooling, etc.) without
// adding it here means it is NOT covered by this gate — add it to this list
// in the same change that introduces the convention.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');
const { execFileSync } = require('node:child_process');
const path = require('node:path');

const REPO_ROOT = path.resolve(__dirname, '..');

const SCRATCH_DIRS = [
  // Per-session scratch: draft PR bodies, issue comments, measurements (#1967).
  '.local/',
  // CodeGraph local index: machine-local, rebuilt on demand.
  '.codegraph/',
];

// Uses real `git check-ignore` semantics (not a hand-rolled glob matcher)
// against a placeholder file inside each directory, so the assertion tracks
// however `.gitignore` patterns actually resolve — including directory-only
// patterns, which do not match the bare directory name in every git version.
function isIgnored(dir) {
  const probe = path.join(dir, '.scratch-dirs-ignored-probe');
  try {
    execFileSync('git', ['check-ignore', '--quiet', probe], {
      cwd: REPO_ROOT,
    });
    return true;
  } catch (err) {
    if (typeof err.status === 'number') {
      // Exit code 1 from `git check-ignore` means "not ignored" — a real
      // result, not a failure to run the check.
      return false;
    }
    throw err;
  }
}

for (const dir of SCRATCH_DIRS) {
  test(`scratch directory ${dir} is gitignored`, () => {
    assert.equal(
      isIgnored(dir),
      true,
      `${dir} is used as machine-local/per-session scratch but has no ` +
        `matching .gitignore rule — a sweeping "git add" would publish it. ` +
        `Add "${dir}" (or an equivalent pattern) to .gitignore.`
    );
  });
}
