---
id: SPEC-003
type: requirements
# 🔒 Once approved, hash-locked: approved bytes recorded in .minspec/approvals.json[SPEC-003].specHash. ANY edit voids approval (hash → stale) — re-run "MinSpec: Approve Spec". DR-012.
status: specifying
tier: T3
product: sealbox
epic: EPIC-007  # Agent Execute Extension — see "Decisions needed" #D1: this spec's subject may not actually belong to this epic
relates_to: [SPEC-002]  # SPEC-002 FR-1/Out-of-scope names the vsix as the control-plane artifact; SPEC-001 §mitigation-basis references the same "installed build" assumption this issue undermines
---

# vsix build identity — every packaged build gets a distinguishable version

> **Specify-phase requirements record for [issue #1952](https://github.com/AIClarityAU/minspec/issues/1952).**
> Nothing here is built. See **Decisions needed (Clarify)** — this spec cannot be
> approved into Plan until #D1 (repo placement) is resolved by a human; everything
> else below is written so Plan can proceed the moment #D1 lands.

**Date:** 2026-09-22
**Issue:** [#1952](https://github.com/AIClarityAU/minspec/issues/1952) — `.vsix` version is reused across builds, so "which build is
installed" is unanswerable and `--force` is load-bearing.
**Epic:** [EPIC-007 Agent Execute Extension](../../../docs/epics/EPIC-007-sealbox.md) (tentative — see #D1)

**Tier — T3.** Spec + plan + tasks + implement. Not T4: the design has exactly one
axis that needs a human call (the version-string format, #D2) and it is bounded and
reversible pre-launch (no shipped Marketplace listing yet per `README.md` "Status:
pre-launch"), so mandatory Clarify ceremony is not warranted — Plan can carry #D2 as
an explicit input once #D1 is answered. Raise to T4 if #D1 resolves to "implement in
this repo AND a published Marketplace listing already exists" (see #D1 options).

---

## Context

Issue #1952 reports that `packages/minspec/package.json`'s `version` field is not
bumped per build, so `npm run package` (or equivalent `vsce package`) keeps emitting
a `.vsix` file with an identical filename across builds with **different contents**.
The issue measured two `minspec-0.1.26.vsix` files, six weeks apart, 700 KB apart in
size, with different sha256 prefixes — same declared identity, different bytes.

This is not cosmetic. [SPEC-002](../SPEC-002-execution-substrate/requirements.md)'s
harness-refresh design (mitigating minspec#1095 and minspec#1492, per the issue body)
rests on an assumption: a harness refresh writes from the **currently installed**
build's embedded canonical. If the version string cannot distinguish which build is
installed, the standing mitigation advice ("rebuild and install a current build
first") is unverifiable from the editor — the version label the user would check
reads identically regardless of which build actually landed. The issue also names a
second, related failure path: `code --install-extension` silently no-ops on a
same-version reinstall unless `--force` is passed, so a same-numbered rebuild can
appear to install successfully while leaving the stale build in place.

**Evidence discipline (CLAUDE.md / DR-003).** The issue's own author flags that path
2 (the `--force` no-op) was not measured in their environment — no `code` /
`code-insiders` / `codium` / `code-server` binary was available to test against — and
is stated as "documented CLI contract, not observed." This spec treats that claim
with the same status: plausible and consistent with published VS Code extension CLI
behavior, but **not independently verified here either** — this container has no
such binary. Confirming it (or finding it does not hold, or finding a flag that makes
`code --install-extension` fail-loud instead of silently skip) is Acceptance
Criterion AC-4 below, not an assumption Plan should carry unverified into Tasks.

## Requirements

### Build identity

- **FR-1 (every packaged build is version-distinguishable).** The version string
  emitted into a packaged `.vsix` — and read back by VS Code / the Marketplace /
  `code --list-extensions --show-versions` — changes on every build that packages
  different source content. Two `.vsix` files that differ in content never carry the
  same version string. Traces to the issue's core defect: "Same version string.
  Different content."
- **FR-2 (deterministic from source, not from wall-clock or build-machine state).**
  The build identifier is derived from something that changes exactly when the
  packaged content changes — the natural candidate is the source commit
  (`git rev-parse --short HEAD` at package time) or an equivalent content hash —
  **not** a timestamp or a machine-local counter that could repeat or drift across
  build environments (CI vs. local). A rebuild of the identical commit with no
  working-tree changes MAY reuse the same identifier (that is a legitimate "same
  build" case, distinct from the defect); a rebuild after any source change MUST
  not.
- **FR-3 (build identity is surfaced in the running extension, not just the
  filename).** "Which build am I running" is answerable **from inside the editor**,
  not only by inspecting the `.vsix` file on disk — since by the time a mismatch
  matters (mid harness-refresh), the file that was installed from may already be
  gone or ambiguous. The installed build's identifier (commit SHA or equivalent)
  appears in at least one of: the extension's own output channel/log on activation,
  a status/about command, or `MinSpec: Show SDD Status`. This is the FR that closes
  the issue's actual complaint — a version number nobody can cross-check is exactly
  as unanswerable as no version number.
- **FR-4 (format is compatible with the tools that parse it).** Whatever format is
  chosen (see #D2) is validated against what the VS Code Marketplace publish
  pipeline (`vsce publish`) and `code --install-extension` actually accept and
  correctly order — the issue itself flags that a `+build` metadata suffix is
  ignored by some semver tooling for ordering purposes, so "looks right" is not
  sufficient; it must be checked against the real tool contracts before Plan locks a
  format (see AC-3).
- **FR-5 (same-version reinstall does not silently no-op).** Given FR-1–FR-2, a
  content-changing rebuild always produces a new version, so the specific
  `--force`-is-load-bearing failure path in the issue is closed structurally (a
  genuinely new build is a genuinely new version, so `code --install-extension`
  installs it without needing `--force`). The rebuild-then-refresh procedure this
  issue references is updated to no longer depend on the operator remembering
  `--force`.

## Invariants (must not break)

- **INV-8 (MinSpec core stays Tier-0 / air-gapped).** Whatever mechanism computes
  the build identifier (git SHA read, file hash, etc.) is a **build-time** concern —
  it runs in the packaging script, never as a runtime dependency the shipped
  extension takes on git, network, or an AI/agent module. The *shipped* extension
  only **displays** a string that was baked in at package time (FR-3); it must not
  shell out to `git` or reach the network at activation to compute it. Traces to
  constitution Invariant #8 / SPEC-002 FR-16.
- **INV-4 (no behavior change to untrusted-input handling).** This is a packaging/
  versioning change only; it must not touch how issue/spec bodies are read or acted
  on. (Not directly implicated by this issue, stated for completeness since the
  change touches build tooling that could tempt scope creep into runtime code.)

## Acceptance Criteria

*Tier-scaled (T3). Checked = built + verified, not merely present in a diff.*

- [ ] **AC-1 — no same-string, different-content builds.** Building from two
  different commits (or one commit with any staged/committed content difference)
  produces two `.vsix` files with different version strings. Building the same
  commit twice with a clean tree produces the same string. *(FR-1, FR-2)*
- [ ] **AC-2 — build identity visible in-editor.** With the packaged extension
  installed, the build identifier is readable from inside VS Code without opening
  the `.vsix` file — via output channel, a status command, or `MinSpec: Show SDD
  Status`. *(FR-3)*
- [ ] **AC-3 — format checked against real tool contracts, not assumed.** Before
  Plan locks a version-string format, it is checked against (a) what `vsce
  package`/`vsce publish` accept, and (b) how the VS Code Marketplace and `code
  --install-extension`/`--list-extensions --show-versions` order and display it —
  documented with a source (VS Code / vsce docs or an actual run), not inferred.
  *(FR-4)*
- [ ] **AC-4 — the `--force` no-op claim is confirmed or refuted, not carried as
  assumption.** Using whatever `code`/`code-insiders`/`codium`/`code-server` binary
  is available in the implementing environment (none was available when this issue
  was filed — flag if still true and this AC cannot close), reinstalling an
  identical-version `.vsix` without `--force` is verified to either no-op silently
  (confirming the issue's documented-not-measured claim) or behave otherwise
  (refuting it) — and the rebuild/refresh procedure is written to match what was
  actually observed. *(FR-5)*
- [ ] **AC-5 — no runtime dependency added.** The shipped extension's activation
  path gains a static string, not a `git`/network call. *(INV-8)*

## Risks & Mitigations

| # | Risk | Likelihood · Impact | Mitigation |
|---|---|---|---|
| R1 | Chosen version format is accepted by `vsce package` locally but rejected or mis-ordered by the Marketplace publish step or `code --install-extension`, discovered only at ship time. | Med · Med | AC-3 — check the real tool contracts before Plan locks the format, not after. |
| R2 | Build-identifier computation (e.g. `git rev-parse`) creeps from build-time-only into a runtime dependency of the shipped extension, breaking Tier-0 air-gap. | Low · High | INV-8 stated explicitly; AC-5 verifies the shipped activation path takes no new runtime dependency. |
| R3 | Stale `.vsix` files remain on disk after a rebuild (issue's "path 1"), independent of the version-string fix, and someone installs an old file from elsewhere by hand. | Med · Low | Out of scope for this spec (see below) but named so Plan can decide whether a packaging-script cleanup step is cheap enough to bundle in; the version-string fix (FR-1) makes this failure at least *detectable* (the installed build's identifier, FR-3, would show the old one) even if not prevented. |
| R4 | This spec is written in the wrong repo (#D1) and Plan/Tasks/Implement never happen because nobody owns `packages/minspec` from here. | Med · High if unresolved | #D1 flagged for human decision before this spec leaves Specify; spec content is written so it can be copied/opened against the correct repo with minimal rework if #D1 says "elsewhere." |

## Out of scope

- **Deleting stale `.vsix` files after packaging** (the issue's third option). Named
  in R3; a human can fold it into Plan as a cheap addition once #D1/#D2 are settled,
  but it does not by itself close the "which build is installed" question (issue's
  own assessment: "removes path 1 and not path 2, and an agent or human can still
  install an older artifact from elsewhere") and is not required to satisfy FR-1–FR-5.
- **Publishing to the Marketplace, or any change to `deploy-site.yml` / CI publish
  workflows.** This spec covers build-identity correctness only.
- **A general provenance/signing story for `.vsix` artifacts.** Out of scope; FR-3's
  in-editor surfacing is the bound of "answerable from the editor," not a
  cryptographic attestation of build origin.

## Decisions needed (Clarify)

- **#D1 — which repo does this spec's implementation actually belong to?** This
  worktree's `git remote` is `AIClarityAU/sealbox.git`, and there is no `packages/`
  directory anywhere in this checkout — `README.md` states the extension itself
  "is not built" here and that "product specs/code land here as the `agent-execute`
  → `sealbox` migration proceeds." The file the issue names,
  `packages/minspec/package.json`, and the `npm run package` command that emits the
  `.vsix`, belong to the **MinSpec core** packaging pipeline, which per this repo's
  own `README.md` was split *out of* `AIClarityAU/minspec` to create this repo
  (DR-027) — i.e. `packages/minspec` most likely still lives in `AIClarityAU/minspec`
  itself, not here. This spec was authored in this repo because that is where issue
  #1952 was dispatched; a human needs to confirm whether:
  (a) `packages/minspec` has since moved into this repo (checkout/branch state is
  stale and it will reappear on the default branch — verify before Plan), or
  (b) the fix belongs in `AIClarityAU/minspec` and this spec should be transplanted
  there (this document's Requirements/Acceptance-Criteria content is written to be
  portable to that repo's own spec numbering with minimal change), or
  (c) both repos now package a vsix from their own `packages/minspec`-equivalent and
  each needs its own instance of this fix.
  **Blocks Plan** — Plan cannot pick a packaging-script location without this
  answered.
- **#D2 — version-string format.** The issue's recommended option names two
  candidates and does not pick between them: (i) a prerelease/build-metadata suffix
  on the existing semver, e.g. `0.1.26+719878d6`, or (ii) an auto-incrementing
  version proper, e.g. `0.1.27`, `0.1.28`, ... per build. Trade-off from the issue:
  a `+meta` suffix is human-legible (ties back to a commit) but the issue flags it
  may be **ignored by some tooling for ordering** — needs checking against what the
  Marketplace/`vsce`/`code --install-extension` actually respect (AC-3) before
  locking this in. An auto-increment orders correctly everywhere semver is
  understood but loses the direct commit linkage unless paired with FR-3's in-editor
  surfacing (which this spec requires regardless, so the two options are not as far
  apart as they first look — FR-3 supplies the traceability either way). Resolve at
  Plan, informed by AC-3's tool-contract check.

## Open questions

- **OQ-1 — does `packages/shared` (or any other co-packaged extension in the same
  pipeline, e.g. ScroogeLLM per DR-015/DR-027) have the same reused-version defect?**
  The issue only measured `packages/minspec`. If the packaging script is shared
  across the MinSpec-line extensions, Plan should check whether the fix needs to
  land once (shared script) or per-extension.
- **OQ-2 — CI packaging path.** Does `.github/workflows/*` (in whichever repo #D1
  resolves to) already compute anything commit-derived for artifact naming that FR-2
  could reuse, or does this need a new step? Not knowable from this repo's workflows
  (this repo's `.github/workflows/` has no vsix-packaging job — see `ci.yml`,
  `minspec-validate.yml`, `deploy-site.yml`, none of which build a `.vsix`).
