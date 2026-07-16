// Focused unit tests for the #810 SHA-bound review-check witness and its gating
// in decideStatus. Runs on plain Node (no deps):
//   node --test .github/scripts/ai-review-guard.test.js
//
// The invariant under test: `ready-to-merge` greens iff the reviewer App's
// `ai-review` CHECK-RUN on the CURRENT head SHA concluded success/neutral — a pass
// on an OLD head, an in-progress run, a newer failure, or a forged/wrong-App
// check-run must all stay RED. This is the security-critical binding the #810 fix
// moved from the best-effort `ai-review/pass` commit status onto the always-on
// required check-run.

'use strict';

const { test } = require('node:test');
const assert = require('node:assert/strict');

const {
  PASS,
  CHANGES,
  parseAllowlist,
  verifyHeadReviewCheck,
  REVIEW_APP_SLUG,
  decideStatus,
} = require('./ai-review-guard.js');

const APP = REVIEW_APP_SLUG; // the hardcoded reviewer App slug
const T1 = '2026-07-16T10:00:00Z';
const T2 = '2026-07-16T10:05:00Z'; // strictly after T1

// A single completed `ai-review` run from the reviewer App.
function run({
  conclusion = 'success',
  status = 'completed',
  slug = APP,
  name = 'ai-review',
  started_at = T1,
  id = 1,
} = {}) {
  return { name, status, conclusion, started_at, id, app: { slug } };
}

// ── REVIEW_APP_SLUG is a real constant, not an unset env var ──────────────────
test('REVIEW_APP_SLUG is a non-empty hardcoded constant (cannot silently go unset)', () => {
  assert.equal(typeof REVIEW_APP_SLUG, 'string');
  assert.ok(REVIEW_APP_SLUG.length > 0);
});

// ── verifyHeadReviewCheck ─────────────────────────────────────────────────────
test('verified: completed success from the reviewer App', () => {
  assert.equal(verifyHeadReviewCheck({ checkRuns: [run()], appSlug: APP }).verified, true);
});

test('verified: completed neutral (machinery exemption) from the reviewer App', () => {
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [run({ conclusion: 'neutral' })], appSlug: APP }).verified,
    true,
  );
});

test('RED: absence — no ai-review check-run on this head SHA (stale/never-reviewed)', () => {
  assert.equal(verifyHeadReviewCheck({ checkRuns: [], appSlug: APP }).verified, false);
  assert.equal(verifyHeadReviewCheck({ checkRuns: undefined, appSlug: APP }).verified, false);
});

test('RED: newest run is a failure — a genuine changes verdict on this head', () => {
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [run({ conclusion: 'failure' })], appSlug: APP }).verified,
    false,
  );
});

test('RED: not completed (queued/in_progress) fails closed', () => {
  assert.equal(
    verifyHeadReviewCheck({
      checkRuns: [run({ status: 'in_progress', conclusion: null })],
      appSlug: APP,
    }).verified,
    false,
  );
});

test('RED: provenance — a check-run under a DIFFERENT App slug does not count (no fake green)', () => {
  // A user token / other action cannot mint a run under the reviewer App's slug.
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [run({ slug: 'github-actions' })], appSlug: APP }).verified,
    false,
  );
});

test('RED: a check-run of a different NAME under the reviewer App is ignored', () => {
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [run({ name: 'ai-review-retry' })], appSlug: APP }).verified,
    false,
  );
});

test('RED: empty/missing appSlug fails closed (never trusts an unconfigured slug)', () => {
  assert.equal(verifyHeadReviewCheck({ checkRuns: [run()], appSlug: '' }).verified, false);
  assert.equal(verifyHeadReviewCheck({ checkRuns: [run()] }).verified, false);
});

test('newest-wins: an OLD success must NOT override a NEWER failure (by started_at)', () => {
  const oldSuccess = run({ conclusion: 'success', started_at: T1, id: 10 });
  const newFailure = run({ conclusion: 'failure', started_at: T2, id: 11 });
  // order-independent
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [oldSuccess, newFailure], appSlug: APP }).verified,
    false,
  );
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [newFailure, oldSuccess], appSlug: APP }).verified,
    false,
  );
});

test('newest-wins: a NEWER success DOES override an older failure', () => {
  const oldFailure = run({ conclusion: 'failure', started_at: T1, id: 10 });
  const newSuccess = run({ conclusion: 'success', started_at: T2, id: 11 });
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [oldFailure, newSuccess], appSlug: APP }).verified,
    true,
  );
});

test('newest-wins: tiebreak on id when started_at is equal', () => {
  const a = run({ conclusion: 'failure', started_at: T1, id: 5 });
  const b = run({ conclusion: 'success', started_at: T1, id: 6 }); // later run, larger id
  assert.equal(verifyHeadReviewCheck({ checkRuns: [a, b], appSlug: APP }).verified, true);
  const c = run({ conclusion: 'success', started_at: T1, id: 5 });
  const d = run({ conclusion: 'failure', started_at: T1, id: 6 });
  assert.equal(verifyHeadReviewCheck({ checkRuns: [c, d], appSlug: APP }).verified, false);
});

test('slug match is case-insensitive', () => {
  assert.equal(
    verifyHeadReviewCheck({ checkRuns: [run({ slug: APP.toUpperCase() })], appSlug: APP }).verified,
    true,
  );
});

// ── decideStatus gating on headCheck (the whole point of the fix) ─────────────
const VERIFIED_LABEL = { verified: true }; // provenance-verified pass label
const GOOD_CHECK = { verified: true };
const BAD_CHECK = { verified: false, reason: 'no ai-review check-run on this head' };

test('GREEN: genuine head-bound pass — verified label + verified head check-run + no changes', () => {
  const s = decideStatus({
    labels: [PASS],
    passProvenance: VERIFIED_LABEL,
    headCheck: GOOD_CHECK,
  });
  assert.equal(s.state, 'success');
});

test('RED: stale/absent head check-run blocks green even with a provenance-verified label', () => {
  const s = decideStatus({
    labels: [PASS],
    passProvenance: VERIFIED_LABEL,
    headCheck: BAD_CHECK,
  });
  assert.equal(s.state, 'failure');
  assert.match(s.description, /not bound to this commit/);
});

test('RED: forged/unverified label stays red regardless of a passing head check-run', () => {
  const s = decideStatus({
    labels: [PASS],
    passProvenance: { verified: false, reason: 'not an allowlisted reviewer' },
    headCheck: GOOD_CHECK,
  });
  assert.equal(s.state, 'failure');
});

test('RED: ai-review:changes present blocks green even with verified label + head check-run', () => {
  const s = decideStatus({
    labels: [PASS, CHANGES],
    passProvenance: VERIFIED_LABEL,
    headCheck: GOOD_CHECK,
  });
  assert.equal(s.state, 'failure');
});

test('no scope-widening: machinery PR (no pass label) stays red', () => {
  const s = decideStatus({
    labels: [CHANGES],
    passProvenance: { verified: false, reason: 'ai-review:pass not present' },
    headCheck: GOOD_CHECK,
  });
  assert.equal(s.state, 'failure');
});

test('rollout compatibility: headCheck undefined ⇒ not required (prior behaviour preserved)', () => {
  const s = decideStatus({
    labels: [PASS],
    passProvenance: VERIFIED_LABEL,
    // headCheck omitted — a base guard predating #810
  });
  assert.equal(s.state, 'success');
});

// End-to-end wiring: the workflow computes headCheck via verifyHeadReviewCheck,
// so confirm the two compose the way the gate depends on.
test('end-to-end: verifyHeadReviewCheck result feeds decideStatus (stale head ⇒ red)', () => {
  const allowlist = parseAllowlist('minspec-sdd[bot]'); // (unused by check path; sanity)
  assert.ok(Array.isArray(allowlist));
  const headCheck = verifyHeadReviewCheck({ checkRuns: [], appSlug: APP }); // stale/absent
  const s = decideStatus({ labels: [PASS], passProvenance: VERIFIED_LABEL, headCheck });
  assert.equal(s.state, 'failure');

  const headCheck2 = verifyHeadReviewCheck({ checkRuns: [run()], appSlug: APP }); // fresh success
  const s2 = decideStatus({ labels: [PASS], passProvenance: VERIFIED_LABEL, headCheck: headCheck2 });
  assert.equal(s2.state, 'success');
});
