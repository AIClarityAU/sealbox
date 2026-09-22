---
id: SPEC-003
type: requirements
# 🔒 Once approved, hash-locked: approved bytes recorded in .minspec/approvals.json[SPEC-003].specHash. ANY edit voids approval (hash → stale) — re-run "MinSpec: Approve Spec". DR-012.
status: specifying
tier: T3
product: sealbox
epic: EPIC-007  # Agent Execute Extension
depends_on: [DR-012]  # DR-012 approval hash-lock semantics — the guarantee this spec exists to keep intact across the TS/Python twins
relates_to: [SPEC-001, SPEC-002]  # both are hash-locked (DR-012) via the same canonical hasher this spec is about
---

# Canonical Hasher Twin Parity — ASCII-Scoped Case-Insensitive Link Matching (Step 5)

> **[Issue #1960](https://github.com/AIClarityAU/sealbox/issues/1960).** A second
> TS/Python canonicalizer divergence, sibling to
> [#1668](https://github.com/AIClarityAU/minspec/issues/1668) (which covers step 6,
> trailing codepoints — a *different* step, not covered here). Rests on
> [DR-012](https://github.com/AIClarityAU/minspec/blob/main/docs/decisions/DR-012.md)
> (approval hash-lock) and the upstream canonical-hashing spec/decision
> `SPEC-022`/`DR-034` (FR-3) cited by this repo's own vendored copy of the hasher
> (`scripts/hooks/canonical.py:4,27`). **Nothing here is implemented** — this is the
> Specify-phase requirements record.

**Date:** 2026-09-22
**Decision:** no new DR minted by this spec (see *Decisions needed* — the fix is a bug
fix, not an irreversible-in-a-day architectural choice per the DR-359 ADR filter).
**Epic:** [EPIC-007 Agent Execute Extension](../../../docs/epics/EPIC-007-sealbox.md)

**Tier — T3.** Full ceremony (specify → plan → tasks → implement; Clarify optional per
`.minspec/config.json`). The mechanical blast radius is small (a regex + a couple of
test/CI files) but the reasoning is not: it spans two languages' Unicode case-folding
semantics, a cross-repo ownership boundary (see Context), and this repo's own
drift-detection CI (`minspec-ci-parity.yml`) that actively resists a naive local patch.
Genuine human calls exist (see *Decisions needed*); they are captured there rather than
forcing a mandatory Clarify phase, since none of them blocks writing the plan.

---

## Context

**What the bug is.** Step 5 of `canonicalizeSpec` collapses relative markdown links to
`](RELLINK)` using a pattern that is byte-identical between the TS module
(`packages/shared/src/canonical.ts`, upstream, not present in this repo) and this
repo's vendored Python twin (`scripts/hooks/canonical.py:77`). Byte-identical source
text does not imply identical behavior: under `re.IGNORECASE`, Python's `[a-z]` does
full Unicode case-folding and matches U+212A (KELVIN SIGN) and U+017F (LATIN SMALL
LETTER LONG S); JavaScript's non-`u` `/i` flag deliberately does not fold non-ASCII
codepoints to ASCII. A link whose scheme's first character is one of these two
codepoints (e.g. `[x](Ky:z)`) is read as *external* by Python (kept) and as *relative*
by JavaScript (collapsed to `RELLINK`) — the two engines disagree on the canonical
string, and therefore on its sha256.

**Why that matters here, specifically.** This repo does not own
`packages/shared/src/canonical.ts` — it doesn't exist in this tree at all. What this
repo *does* own is a live consumer of both sides of that parity guarantee:

- `scripts/hooks/canonical.py`'s `spec_hash` is the Python-side hash used by this
  repo's own `.minspec/hooks` PreToolUse spec-gate to check a spec's bytes against its
  recorded approval (`.minspec/approvals/*.json`, DR-012 hash-lock — see the frontmatter
  comment on this file and on SPEC-001/SPEC-002).
- The *same* function backs `scripts/approval-provenance.py`, which
  `scripts/review-branch.sh` feeds to the AI review panel as a **TRUSTED,
  machine-generated** fact block (`report_for()`/`build_report()`), explicitly
  contrasted with the **untrusted** diff — it is the mechanism that stopped the panel
  from calling a genuine human re-approval a "forged sign-off" (PR #1017 postmortem,
  `scripts/approval-provenance.py:6-22`).
- The TS-side hash this Python twin must match is computed by the actual MinSpec VS
  Code extension (Tier-0 core) when a human runs *MinSpec: Approve Spec*. If the two
  engines disagree on a spec containing one of the divergent codepoints, this repo's
  gate and its review panel would trust a specHash the extension itself would call
  stale, or vice versa — exactly the failure this repo's own tooling exists to prevent.

**Why the obvious fix — patch `scripts/hooks/canonical.py` here — doesn't close the
loop.** The block is explicitly managed (`>>> minspec:managed:canonical-hasher-python
>>>` … `<<< … <<<`), scaffolded byte-for-byte from `AIClarityAU/minspec`'s public
`main`. `.github/workflows/minspec-ci-parity.yml` fetches that canonical source on
every PR touching `scripts/hooks/canonical.py` (and weekly) and **fails this repo's own
CI on any drift inside the managed markers**, directing the dev to run *MinSpec:
Refresh Harness Files* — i.e. to pull the *upstream* version back in. A same-repo-only
patch to the managed region would be flagged as drift by the very gate meant to keep
this file honest, and a subsequent refresh would silently overwrite it with the
still-buggy upstream text. **The durable fix has to land upstream first.**

**Current exposure.** Zero — the issue reports scanning all `specs/**/*.md` for U+212A
and U+017F with no hits, and this repo's own `specs/` tree (SPEC-001, SPEC-002, and now
this spec) contains neither codepoint. The gate that would have caught an *active*
instance is `packages/minspec/tests/canonical-parity.test.ts` (upstream), which is
corpus-witnessed only — it cannot see a divergence no spec yet exercises.

## Requirements

### Upstream dependency (the authoritative fix)

- **FR-1 (the source fix is out of this repo's file ownership).** The regex fix —
  scoping the Python-side character class to ASCII (e.g. `[A-Za-z]` outside the
  Unicode-folding scope of `re.I`, or an explicit `re.ASCII`-scoped sub-pattern for just
  that class) so it stops matching U+212A/U+017F — must be authored in
  `AIClarityAU/minspec`, in both `packages/shared/src/canonical.ts`'s Python twin
  source and the harness template `scripts/hooks/canonical.py` is scaffolded from. This
  repo (sealbox) has no path to a durable independent fix inside the managed block (see
  Context); this requirement records the dependency rather than restating the fix
  mechanics the issue already proposes.
- **FR-2 (refresh + re-verification once upstream lands).** After the upstream fix
  ships, this repo runs *MinSpec: Refresh Harness Files*, confirms
  `minspec-ci-parity.yml` reports no drift on `scripts/hooks/canonical.py`, and
  re-verifies that `scripts/approval-provenance.py`'s hash output is **unchanged** for
  every spec currently under `specs/**` (expected, since the corpus has zero divergent
  codepoints today — but asserted, not assumed, per the Evidence-discipline convention
  these specs already follow).

### Interim compensating controls (this repo's own scope, pending the upstream fix)

- **FR-3 (local regression coverage independent of upstream's).** Add a test, owned by
  this repo and **outside** the managed markers (so a harness refresh cannot silently
  delete it), that calls `scripts/hooks/canonical.py`'s `canonicalize_spec`/`spec_hash`
  against fixtures built from the issue's own reproduction (`[x](Ky:z)`, `[x](ſy:z)`)
  and asserts the *relative-link* reading (collapsed to `RELLINK`), i.e. asserts the
  **post-fix** behavior. Collected by whatever suite this repo actually runs in CI —
  the issue names the analogous upstream gap (`scripts/hooks/test_canonical.py` not
  collected by pytest, #1669) as a cautionary precedent not to repeat here.
- **FR-4 (defensive corpus guard — keep "zero hits" true, not just observed).** A
  CI-enforced check over `specs/**/*.md` (and any other tree this repo's spec-gate
  hashes) that fails the build if a relative-markdown-link scheme position contains a
  codepoint Python's `re.IGNORECASE` folds into `[a-z]` but JavaScript's non-`u` `/i`
  does not — a stopgap that keeps today's zero-exposure fact true going forward, for as
  long as the upstream fix is pending. Placed outside the managed region for the same
  reason as FR-3.
- **FR-5 (no silent trust of a mismatched hash).** Verify — and do not regress —
  that `scripts/approval-provenance.py`'s existing behavior on a specHash mismatch
  (`report_for()`'s `VERDICT: MISMATCH`, never a silent pass) and the PreToolUse
  spec-gate's stale-hash handling both fail closed. This FR asks for a **check**, not
  new mechanism: nothing in this spec's scope should ever make either path treat a
  Python-computed hash as authoritative over a stale/mismatched extension-recorded one,
  or vice versa, without surfacing it.

## Costly to Refactor

*The expensive-to-reverse commitments — read these closely; everything else is cheap to
change. Ranked most→least costly.*

1. **Treating the upstream fix as a hard dependency rather than forking the managed
   block** (FR-1) — forking would desynchronize this repo from
   `minspec-ci-parity.yml`'s drift contract permanently (the parity job would need a
   standing suppression for this one file), which is far harder to undo cleanly later
   than waiting. *Check: no PR patches inside the `minspec:managed:canonical-hasher-python`
   markers in this repo.*
2. **Interim guard lives outside the managed region** (FR-3, FR-4) — if placed inside
   the markers, the next harness refresh silently deletes it and the compensating
   control disappears with no error. *Check: new test/guard files are not between the
   `>>> minspec:managed:... >>>` / `<<< ... <<<` comment pairs.*

## Invariants (must hold)

- **INV — DR-012 hash-lock semantics stay intact.** An approved spec's recorded
  `specHash` continues to mean "these exact approved bytes," independent of which
  engine (TS extension or this repo's Python twin) computed it, for every spec in this
  repo's corpus (FR-2, FR-5; DR-012).
- **INV — TS/Python canonical-hash parity, enforced going forward, not just observed
  today.** No spec under `specs/**` may rely on a codepoint where the two engines'
  step-5 link-matching disagrees; the corpus stays at zero such hits by construction
  (CI-checked), not by accident (FR-4).
- **INV — Managed-region discipline.** No sealbox-authored content is added inside a
  `minspec:managed:*` block; anything this repo needs that upstream doesn't yet provide
  lives beside the managed block, never inside it (FR-3, FR-4; existing
  `minspec-ci-parity.yml` contract).
- **INV — MinSpec Tier-0 core never depends on this extension (constitution #8).**
  Nothing in this spec's scope adds a dependency from `packages/minspec` /
  `packages/shared` onto sealbox; both remain outside this repo's tree entirely (N/A by
  construction here, restated for completeness).

## Acceptance Criteria

*Definition-of-done — each item traces its FR(s). All unchecked: nothing here is built
(Specify-phase record).*

- [ ] **(FR-1)** A tracked, linked dependency exists from this spec to the upstream fix
  in `AIClarityAU/minspec` (issue and/or PR reference recorded once opened); this
  repo's plan does not attempt to carry the fix itself inside the managed block.
- [ ] **(FR-2)** After the upstream fix merges: *MinSpec: Refresh Harness Files* run,
  `minspec-ci-parity.yml` green on `scripts/hooks/canonical.py`, and a diff of
  `spec_hash()` over every current spec in `specs/**` shows **no change** (recorded as
  evidence, not assumed).
- [ ] **(FR-3)** A regression test outside the managed region exercises the issue's
  exact repro inputs (U+212A and U+017F as a link scheme's first character) against
  `canonicalize_spec`/`spec_hash` and is collected by this repo's actual CI-run test
  suite (not merely present on disk, per the #1669 cautionary precedent).
- [ ] **(FR-4)** A CI job fails the build if any file in `specs/**/*.md` contains a
  divergent-fold codepoint in a step-5-relevant relative-link scheme position; a fixture
  PR that intentionally introduces one is used to prove the guard actually fires before
  merge (not just exists).
- [ ] **(FR-5)** A fixture pair (base sidecar with a stale hash, head sidecar with a
  fresh one) run through `scripts/approval-provenance.py` still reports `VERDICT:
  MISMATCH` for a genuinely-stale record; no code path added by this spec's scope
  short-circuits that check.

## Out of scope

- **Authoring the regex fix itself inside `packages/shared/src/canonical.ts` or the
  upstream harness template.** Not this repo's file tree; tracked as an upstream
  dependency (FR-1).
- **Step 6 (trailing-codepoint) divergence.** Sibling issue
  [#1668](https://github.com/AIClarityAU/minspec/issues/1668); a different step, a
  different spec.
- **A general audit of every other case-insensitive regex in the canonicalizer for the
  same class of engine divergence.** Worth doing, but not scoped here — this spec is
  step 5 only, matching the issue.

## Decisions needed (Clarify)

- **D1 — Fork the managed block locally, or block on the upstream repo's timeline?**
  Waiting (FR-1) keeps this repo honest with `minspec-ci-parity.yml` but makes sealbox's
  fix land on `AIClarityAU/minspec`'s schedule, which this team doesn't control.
  Forking (suppressing parity checking for just this file) unblocks sealbox
  immediately but permanently weakens the drift gate that exists specifically to catch
  "this repo silently diverged from minspec's canonical" (`minspec-ci-parity.yml`'s own
  stated purpose). **Recommend waiting** (reflected in FR-1/Costly-to-Refactor #1) —
  the human should confirm, especially if the upstream fix has no owner/timeline yet.
- **D2 — How precisely should the interim corpus guard (FR-4) replicate the bug's exact
  divergence set?** A strict-ASCII-only rule for every relative link scheme character is
  simple and provably safe, but broader than the actual bug (it would also flag
  codepoints that happen not to diverge). Enumerating the true divergent set (via the
  issue's own fuzz/property methodology — compare Python `re.I` folding vs. JS non-`u`
  `/i` across the Unicode range) is more precise but is itself nontrivial engineering
  that risks becoming its own source of drift from the eventual upstream fix. The human
  should pick a precision level before Plan.
- **D3 — Does this bug even belong to a sealbox spec, or should the issue be
  transferred/duplicated to `AIClarityAU/minspec` with this sealbox spec narrowed to
  "consume the upstream fix + carry FR-3/FR-4 interim guards" only?** As written, FR-1
  already treats the source fix as fully out-of-repo; the human should confirm whether
  tracking it here (vs. a cross-repo issue link only) is the right home, given this
  spec's own Out-of-scope statement that the fix itself is not sealbox's to author.
