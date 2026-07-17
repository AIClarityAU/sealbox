---
id: DR-048
status: proposed
date: 2026-07-16
epic: EPIC-007  # Agent Execute / SealBox Extension
tier: T3
relates_to: [SPEC-002, DR-047, DR-045, DR-017, DR-016, DR-020]
tags: [sealbox, agent-execute, scrooge, broker, delegation, model-selection, fan-out, never-wrong, sub-thread, token-savings, disclosure, cache]
title: The SealBox broker delegation engine — cheapest-adequate model per sub-task on limited-context sub-threads, truthfully disclosed; the token-savings engine a transparent proxy structurally cannot be
triggered_by: "Session 2026-07-16 sizing the SealBox token-savings engine on measured dogfood traffic (1640 req, data/requests.jsonl): a transparent proxy tops out ~10-15% for a cached agentic user because 74% of spend is fat cached-Opus main-thread turns that are cache-catastrophic to route per-turn (all-Opus→Sonnet = −228%). The genuine ≥25% lever is sub-thread delegation — keep the expensive spine lean, peel self-contained sub-tasks onto separate limited-context threads on the cheapest-adequate model. DR-047 already ruled that delegation is truthful only where SealBox IS the orchestrator (the broker), not on the live-CC wire. This DR designs that engine."
---

# DR-048: The SealBox broker delegation engine — the token-savings mechanism a transparent proxy structurally cannot be

> **Born `proposed`** (acceptance is a separate human act — *MinSpec: Accept ADR*).
> Records the direction + the disclosure invariant shape; mandates SPEC-002 / cross-repo follow-ups.
> **No code** — SealBox is unbuilt (no `src/`), SPEC-002 in Specify phase, the broker is a
> **Layer-2** feature (CL-9/CL-15) that ships *after* v1's manual Layer-1. This DR **extends**
> DR-047; it does not revisit or loosen DR-047's live-CC wall.

## Context

DR-047 answered *where* a truthful per-task model pick may live: not in the Scrooge proxy behind
live Claude Code (any wire-level swap contradicts CC's own per-subagent label — the DR-016 lie),
but at the **headless SealBox broker**, where SealBox *is* the orchestrator and there is no live
label to contradict. DR-047 left the engine itself unbuilt and named two costly-to-refactor
seams: the broker↔Scrooge selection interface, and the per-sub-task disclosure record.

This DR designs that engine, sized on measured reality rather than intuition.

**The measured wall (`data/requests.jsonl`, 1640 req, 2026-07-15).** 94.5% of input on a cached
agentic user is warm cache-reads at 0.1×; **74% of spend is fat, already-cache-efficient Opus
main-thread turns.** There are two ways to touch that spend, and they have opposite sign:

- **Per-turn routing (the −228% trap).** Mid-session the agent holds a ~150K-token warm Opus
  cache. Route that turn Opus→Sonnet and you pay twice: Opus's warm cache is abandoned (sunk),
  and Sonnet must **cache-write the entire 150K context fresh at 1.25×** before answering one
  turn. Measured **−196%** on >150K-ctx turns, **−228%** routing all Opus→Sonnet. This is why a
  transparent proxy tops out ~10-15% (small-call routing ~6% + 1hr-TTL ~2-4% + safe compression
  ~2-5%) and why Scrooge-behind-CC must never swap (DR-047 §1).

- **Sub-thread delegation (the projected ≥25% win).** The peeled sub-task **never rides the
  spine.** It is a fresh `claude -p` with only its own inputs (~5K tokens, not 150K). The
  *autonomous* mechanism has **two** compounding savings: (1) **model delta** — cheapest-adequate
  model (illustratively ~10-12× cheaper per token Opus→Haiku, from the pricing table — not a
  measured average); (2) **context delta** — 5K vs 150K makes the sub-task's absolute cost tiny
  regardless of model, its one cache-write small and paid once. A **third** lever,
  **spine-leanness** (peeled work never accretes onto the Opus spine, so the 74%-of-spend fat
  turns *stop growing*), belongs to the **live-CC relocation** surface — it applies when you move
  work *out* of an existing fat live session, not to a natively-lean autonomous run, so it is
  **not** folded into the autonomous ≥25%.

**The −228% and the +25% are one fact read two ways.** Routing gives a cheap model a *huge fresh
context* (disaster); delegation gives a cheap model a *small fresh context* (genuinely cheap).
Limited context is load-bearing, and it is native to CC's own `Agent` primitive: each sub-agent
already spawns with its own `{model, effort}` and its own **isolated context window** that does
not inherit the parent's warm cache. The SealBox delegation engine is the autonomous analog of
exactly this. This is precisely why the engine belongs in SealBox (which controls the
conversation) and not in Scrooge (a wire-level proxy that cannot peel a sub-thread) — a
restatement of DR-047 §2/§3 in cost-physics terms.

> **Honesty caveat (evidence discipline — RCDD / DR-003, INV-13).** The −228% / −196% routing
> figures are **measured** on the 1640-req trace. The **≥25% delegation figure is *projected*** —
> modeled on autonomous work that *does not exist yet* (SealBox is unbuilt; no autonomous traffic
> has been metered). It is a design target, not a measured result; FD-3's baseline choice gates
> whether it holds; and a sampled shadow-A/B (validating the heuristic classifier's picks) must
> confirm it before it is ever *published*. Every "≥25%" below carries this caveat.

**The honest two-surface split (do not conflate).** Live CC and autonomous SealBox deliver
*structurally different* value, and treating them as the same thing at two magnitudes is the
label-lie in economic form:

| Surface | Honest value | Mechanism | Honest ceiling |
|---|---|---|---|
| **Live interactive CC** (daily driver) | Relief + visibility + charm + trust — **not** a headline savings %. | Scrooge = cache + measure + **advise**. CC's *own* orchestrator may delegate grunt to cheap subagents (nudged, never intercepted). | ~10-15% quota, and only if CC follows the nudge. |
| **Autonomous SealBox runs** (offloaded work) | Engineered savings + honest-delight disclosure — a **projected ≥25%** (modeled, not yet measured). | The broker/SealBox **is** the orchestrator → cheapest-adequate model + tight context per sub-task → little cache to lose → genuinely cheap. Disclosed in the outcome record. | ≥25% projected, truthful once measured (no live per-subagent label to contradict). |

The daily-driver savings do **not** come from shrinking the live session — DR-047 forbids it and
the cache math confirms it is a mirage. They come from **relocation**: moving self-contained grunt
work *off* the expensive interactive plane *onto* the cheap autonomous plane, where SealBox
truthfully spawns cheap-model, tight-context sub-threads on the same subscription and discloses
exactly what ran. "Make your Max plan last" = stop grinding grunt work in your expensive
interactive window; hand it to the cheap plane.

**Subscription decouples the two products (ToS-aware).** For a Max/subscription user,
Scrooge-the-proxy is **not in the wire path** — subscription-mode broker rewrite is ToS-blocked
(minspec DR-017 OQ / #74 / #407); the ideal collapses to spawning the real CLI with
`CLAUDE_CODE_OAUTH_TOKEN` direct to Anthropic, no reroute. So for the founder, autonomous savings
come from **SealBox naming a cheaper model at spawn + giving each sub-task tight context** —
truthful because SealBox *is* the orchestrator writing the routing, not a proxy swapping under a
label. Scrooge's per-task *routing* only matters for API-key / PAYG / Teams users; for the Max
user Scrooge's role shrinks to exactly its DR-047 live role — **measure + advise, never wire.**
This lets the Max-user savings story ship **without** waiting on the #74/#407 legal decision.

## Decision

This DR extends DR-047. Everything below is Layer-2, born-proposed, and does not alter DR-047's
live-CC posture.

**1 — The token-savings mechanism is delegation, not routing: keep work OFF the fat thread, do
not swap the model ON it.** SealBox, as orchestrator of an autonomous run, keeps an expensive
lean **spine** thread (the plan, cross-cutting judgment, diff assembly) and peels simple,
self-contained **sub-tasks** onto separate **limited-context sub-threads**, each on the
cheapest-adequate model. Per-turn routing of the fat spine is explicitly rejected as the −228%
trap. This is the ≥25% lever and it is only reachable because SealBox controls the conversation.

**2 — The delegation planner is a new SealBox orchestration surface, distinct from existing
concepts.** It is **not** FR-14 whole-issue concurrency (parallelism across whole issues against a
global cap) and **not** the DR-045 fan-out visibility queue (Layer-1 glance/interrupt). It
decomposes **one run** into `spine + peelable sub-threads`. A sub-task is *peelable* iff it is
**simple AND self-contained** — needs only its own small inputs, returns a bounded artifact
(mechanical rename, doc/research write-up, single-file test stub, data extraction, lint pass,
lookup). Anything needing the spine's accumulated context stays on the spine.

**3 — Execution is credential-free in the exec plane; "cheap" is never an excuse to run
in-host.** A peeled sub-thread spawns into the exec plane (L2 container / L1 subprocess-in-worktree),
**never** the ext host (invariant #1). Its only egress is the broker socket; it reaches a model
*only* through the broker (invariant #2). Writing sub-tasks each get their own
`~/code/.worktrees/<repo>/sealbox-<runId>-<subId>/` (invariant #6); non-writing sub-tasks
(research/lookup/mechanical read) need no worktree.

**4 — Adequacy is "cheapest-adequate", conservative and upward-biased — reuse the live Phase-0
classifier, and respect its proven limit.** The picker's inputs are the content-safe labels the
shadow classifier already derives (`classify.mjs`: `difficulty` 0..1, `task_type`, `delegatable`,
`ask_chars` — **labels/sizes derived in-memory, never prompt content** — the same content-safety
property that instrument was built with, distinct from any numbered invariant), recomputed
per sub-task by the broker. Because the picker consumes only these labels — never
the raw body — the untrusted issue/spec/tool body stays **data, not instructions** to the planner
(invariant #4): a prompt-injected body can at worst provoke a bad/costly *pick*, never an action
or exfil, bounded by the credential-free exec plane + broker-only egress.
But the validated finding (n=120, Fleiss κ=0.80) holds: the classifier measures **mechanical
scope, not cognitive difficulty** (a subtle 1-line bug and a trivial 1-line fix are
size-identical; threshold-tuning and AST signals were dead ends). Therefore, mirroring DR-021's
upward-only ratchet:
- **Adequacy errs *up* under uncertainty.** The classifier gives a sound *lower bound* on required
  capability, not a point estimate. When ambiguous, pick the *more* capable model — the economics
  are asymmetric: a wrong-cheap pick that fails and is redone on the capable model costs ~2× the
  task, wiping out the delegation savings and then some. "Cheapest-adequate" = *cheapest model
  whose expected success on this task-shape clears a confidence bar*, not "cheapest model."
- **Only peel `delegatable === true`.** A `continuation` (tool_result turn) or `complex` ask is
  not cleanly peelable — leave it on the spine, where the context is.
- **The labels are a floor, not the ceiling — the picker MAY use the network (see §5).** SealBox is
  **Tier-1**: the host-side broker is network-capable *by design* (Goal 1 — "credentials, network,
  and autonomy live only behind this boundary"; invariant #2 constrains the **sandbox's** egress,
  not the broker's). So the picker is **not** limited to the regex heuristic: a **cheap LLM
  adequacy judge** (e.g. a few hundred Haiku tokens, ~$0.001/sub-task — economically trivial
  against the delegation saving) can judge "could a cheap model do this sub-task?" far better than
  mechanical-scope signals, directly attacking the κ=0.80 limit above. Treat the deterministic
  label picker as the **always-available floor** (works with no network and no Scrooge) and the
  LLM judge as an upgrade the broker may use when reachable. **Open:** whether the judge is v1 or
  a later ratchet (Costly-to-Refactor).

**5 — The broker owns the picker; the binding constraint is "works without *Scrooge*", NOT
"offline".** This resolves DR-047's costly-to-refactor interface OQ, and the subscription ToS
constraint forces it: in subscription-default mode (the common path) Scrooge
is **not in the wire at all** (#74/#407), so if the pick were *delegated* to Scrooge the default
path would have **no picker**. The picker therefore lives in the broker and must be
**Scrooge-independent** — self-sufficient when Scrooge is absent, uninstalled, or out-of-wire.
> **Do not conflate Scrooge-independence with air-gapping.** An earlier draft called this a
> "Tier-0 offline picker, no network". That is **MinSpec's** posture (its constitution's
> works-offline invariant; SealBox invariant #8 exists precisely to keep *MinSpec* air-gapped) —
> it is **not SealBox's**. SealBox is the **Tier-1** boundary *behind which network lives*
> (Goal 1). Nothing forbids the broker's picker from using the network; the deterministic
> label-only path is a **fallback floor** (nice for no-network/no-Scrooge robustness), not a
> policy requirement. Conflating the two would have foreclosed the LLM adequacy judge (§4) — the
> single best mitigation for the classifier's proven weakness.

When installed (opt-in API-key mode) Scrooge returns a *recommendation* — the richer
brain (live price table, cross-run priors, cache-state awareness, DR-013 attribution). The broker
**applies or overrides** and is always the actuator + the meter. This keeps the moat honest:
Scrooge stays *route/cache/measure/**advise*** — advising a machine (the broker) it may act on
truthfully *because the disclosure record (§7) closes the honesty loop*, never becoming the
authority over a seam it isn't always present at. Write the contract **API-key-mode-first**; treat
subscription-mode Scrooge routing as blocked on #74/#407.

**6 — Subscription-first, including the cheap picks (invariant #9).** Every per-task pick — the
cheap ones too — tries the dev's Pro/Max **subscription quota first**; PAYG API is injected only
as **capped overage spillover** (FR-14) when subscription is unavailable or its ceiling is hit,
and never inside the sandbox. The true objective is "**cheapest-adequate within subscription
first, PAYG only on spillover**" — cheapest-adequate must never silently mean cheapest-PAYG. The
"cheapest" ranking is therefore **quota-aware, not price-aware** (see Follow-ups: whether Scrooge
returns a single pick or a ranked list the broker filters by subscription-availability).

**7 — Disclosure is the outcome record, and it is designed BEFORE the picker.** DR-047 §4: a
truthful auto-pick is legitimate *only because* a headless run has no live label to contradict —
which holds *only if* every sub-task's actually-run model is disclosed. The invisible auto-pick is
**permitted precisely because it is disclosed after the fact**; disclosure and delight are one
artifact, not two features. Extend CL-5's agent-output contract (today
`{fix_description, confidence, tests_passed, files_changed}` — **no model field**) with a
per-sub-task record, persisted to the CL-4 OutcomeStore
(`.minspec/agent-execute/outcomes/<ulid>.json`, gitignored, Zod-validated, one file per attempt →
zero write contention), **sourced from the broker meter (CL-15) — the only truthful source, since
the exec plane is credential-free and structurally cannot observe billing.** Proposed shape:

```
subTasks: [{
  id, role,                        // "plan-change" | "rename-symbol" | "write-regression-test" | …
  plannedModel, plannedEffort,     // what the SealBox orchestrator ASKED the broker for
  ranModel, ranEffort,             // what the broker meter says ACTUALLY executed  ← the disclosure
  provider, billingMode,           // "subscription" | "api" | "scrooge"  (CL-9 precedence)
  pickedBy,                        // "broker-deterministic" | "scrooge-recommendation" | "human-override"
  adequacy: { difficulty, task_type, delegatable, ask_chars, confidence },
  inputTokens, outputTokens, cacheReadTokens, cacheWriteTokens,
  costUsd | null,                  // null in subscription mode (no per-call $ meter exists there — see §Consequences)
  quotaShare | null,               // fraction of the 5h/weekly window this sub-task consumed
  outcome,                         // "completed" | "failed" | "retried_up"
  retryOf | null,                  // set iff this is a cheap-failed → capable-redo
  fallbackReason | null }]         // set iff ranModel ≠ plannedModel (rate-limit, spend-cap degrade, …)
```

**8 — INV-DISCLOSURE (propose as a T0 in SPEC-002 — the headless counterpart of scrooge DR-016's
live-label invariant):** *A run's outcome record MUST state, per fanned-out sub-task, the model +
effort that actually executed and who picked it, sourced from the broker meter — never back-filled
from `plannedModel`.* If the broker cannot attribute a wire call to a sub-task, the field is
`"unknown"` (honest), never guessed from intent. Absent this record, auto-pick is a silent swap =
the lie; present, it is truthful. **The disclosure schema is authored before any model gets
auto-picked** (retrofitting "what actually ran" is the never-wrong-regressing path). **Recommended:
elevate INV-DISCLOSURE from a SPEC-002 T0 to a SealBox *constitution* invariant** — its live
counterpart (scrooge INV-16) is a ratified constitution invariant, so the never-wrong guarantee
should have equal standing on both surfaces, not merely spec-level on the headless one.

**9 — Savings are disclosed *net of retries*, never gross (mirrors DR-020 / INV-13 billing
honesty — realized deltas only, never counterfactuals as fact).** A sub-task that failed cheap
then succeeded capable (`retried_up`) counts its **full** cost against that run's delegation
savings. The receipt must be willing — and visibly designed — to **report a zero**: when a run's
work was all deeply-contextual and nothing was delegatable, it says so ("Nothing to delegate this
run — every sub-task needed the full plan context. No savings, and that's the correct call."). A
receipt that always shows a win is a liar; the willingness to report `$0` correctly is what makes
the run that reports `1.5% kept` believable.

**10 — The live-CC surface is advise-only; it never intercepts (re-affirming DR-047 §1/§3).**
Under live CC, SealBox/Scrooge only *detects + recommends*: a Scrooge statusline (window-remaining
+ honest per-session measured numbers, never a fabricated "we saved you X") plus an **offload
nudge** — when a self-contained delegatable unit is detected on the fat thread, advise "hand this
to SealBox" with a one-keystroke path (keyboard-first, hotkey shown per user pref), one line,
end-of-turn/session, never a mid-flow modal, respecting the upsell-trust cooldowns (24h delay, 7d
cooldown). The precision bar is the whole game: fire **only** on genuinely-delegatable units — a
false nudge on deeply-contextual work destroys trust instantly; better to under-nudge than cry
wolf. This nudge is honestly a **skill / CLAUDE.md advisory + measurement that depends on CC
cooperating**, not an engineered SealBox proxy feature — and it must be messaged as such. It is
the top of the funnel; the headless receipt is the payoff.

**11 — The fall-in-love value is SPLIT across the two surfaces, and each is named for what it can
honestly deliver.** Daily emotional touchpoint on live CC = **relief + charm + trust** (measured
window-remaining, never-locked-out relief, credential-free local-first trust) — lead with relief
and visibility, **not** a savings %. Weekly "holy cow" on autonomous runs = **engineered savings +
honest-delight disclosure** — the run receipt ("built these 6 issues overnight on your plan; used
~1/3 the window your main thread would have — here's exactly which model ran each sub-task"). The
≥25% headline belongs **only** to the autonomous surface. The honest risk, stated plainly: an
alpha who lives only in live CC and never adopts the offload workflow gets the charm and relief but
**not** the headline — their honest number is ~10-15%, mostly CC's own subagent cooperation.

## Alternatives considered

- **Per-turn wire routing of the fat thread to a cheaper model (the "obvious" proxy savings).**
  Rejected on measured evidence: −196% on >150K-ctx turns, −228% all-Opus→Sonnet. Forces a
  big-context cache-write onto a cheap model. This is the trap, not the lever.
- **Delegate the model pick entirely to Scrooge (broker is a dumb relay).** Rejected: in
  subscription-default mode Scrooge is not in the wire (#74/#407), so the default path would have
  *no picker*. The picker must be broker-owned and **Scrooge-independent** (self-sufficient when
  Scrooge is absent) — which is *not* the same as offline: SealBox is Tier-1 and its broker may
  use the network (§4/§5).
- **Scrooge returns the authoritative pick even in API mode.** Rejected: makes Scrooge the
  authority over a seam it isn't always present at, and CL-9 already makes the broker the single
  resolution seam. Scrooge advises; the broker actuates + meters.
- **Ship the receipt/disclosure after the picker (retrofit "what ran").** Rejected by DR-047 §4 /
  DR-016 footer precedent: retrofitting disclosure onto an autonomous substrate is the costly,
  never-wrong-regressing path. Schema first, picker second.
- **A hard "$ saved" headline in subscription mode.** Rejected: no dollars are spent on a flat
  sub, so any "$ saved" is pure counterfactual — the subscription-mode label lie. Quota-headroom
  is the only honest headline there (see Consequences; final call is a founder decision).
- **Message both surfaces with one ≥25% number.** Rejected: conflating a ~10-15% live ceiling with
  a ≥25% autonomous mechanism is the label-lie in economic form. Name them separately.

## Costly to Refactor

- **The broker↔Scrooge selection contract (`recommend(taskShape) → …`).** Single `{model, effort,
  thinking, confidence}` vs a *ranked* list the broker filters by subscription-quota-availability.
  Load-bearing; pins scrooge #41's API surface. Define with the broker, not after.
- **The per-sub-task disclosure record + INV-DISCLOSURE (§7/§8).** The headless honesty contract;
  must exist from v1-of-the-feature. Author the schema *before* the picker.
- **Who authors the decomposition (the new planner's core contract).** (a) control plane
  deterministically peels *declared* sub-tasks from the spec/task list, (b) the spine agent emits
  explicit `delegate(subtask)` calls like CC's `Agent` tool (lean recommendation: context-aware +
  truthful — the actor holding the task context decides what to peel), or (c) a heuristic
  auto-detects delegatable spans. Unspecified in SPEC-002; the engine's core orchestration seam.
- **Whether the OutcomeStore feeds back into the picker as learned per-repo adequacy priors.**
  Recording success/failure per `(model, task_type, difficulty-band)` turns the heuristic
  classifier into a *measured* per-repo prior (the classifier finding's demanded
  "sampled-shadow-A/B before acting"), but makes the picker **stateful** (reads the store the
  broker writes) — a scope/architecture decision, not a knob.
- **Whether the adequacy picker gets a cheap LLM judge (§4), and in v1 or later.** SealBox is
  Tier-1, so the broker *may* call out: a few-hundred-token Haiku judge (~$0.001/sub-task) would
  likely beat the mechanical-scope heuristic on the exact axis the κ=0.80 finding says it fails
  (cognitive difficulty). Load-bearing because it changes the picker's shape (deterministic-only
  floor vs floor + network-upgrade path) and its failure modes. Do **not** re-derive the picker as
  offline-only — that was an inherited MinSpec-Tier-0 assumption, not a SealBox constraint.
- **Peeled sub-threads count against the global concurrency cap (constitution constraint #2).**
  Delegation multiplies in-flight sandboxes; if unbounded it can blow the very window it is trying
  to preserve. The planner must schedule spine + peeled sub-threads under one shared cap — define
  the accounting with the scheduler, not after.
- **Multi-worktree diff reconciliation.** Each *writing* sub-task gets its own worktree (§3); how N
  sub-task diffs merge back into the run's single push-protocol branch (invariants #5/#7, no
  in-sandbox push) is unspecified. Load-bearing seam — name the assembly + conflict protocol with
  the planner.

## Consequences

### Positive
- Lifts the honest savings ceiling from the proxy's ~10-15% to a **projected ≥25%** on the
  autonomous surface (a modeled target pending measurement — see the Context honesty caveat), by
  changing *what the expensive thread carries* rather than swapping models under a label.
- Turns DR-047's wall into the product's **spine**: the live session stays fat/Opus/cached for
  what needs a human; grunt relocates to the cheap plane. Relief + charm daily; engineered savings
  weekly.
- **Decouples the two products' value stories** so the Max-user savings story ships *without* the
  #74/#407 legal decision (SealBox spawns cheaper models direct-to-Anthropic; Scrooge routing is
  reserved for API/Teams).
- The disclosure record makes "cheapest-adequate" **auditable** and honest delight real; because
  the meter is on the **trusted host side** (the credential-free sandbox structurally cannot
  observe billing), the savings figure **cannot be inflated by a compromised sandbox** — a
  strictly stronger honesty guarantee than a self-reporting proxy, and a measurement-is-the-moat
  differentiator.
- Reuses the *already-live* Phase-0 classifier as the picker's input (no new content-touching
  surface, INV-10 preserved) and its OutcomeStore as the path to a measured per-repo adequacy
  prior — closing the "heuristic ≠ truth" gap empirically over time.

### Negative / accepted
- **The engine is Layer-2** (CL-9/CL-15), gated on spike #74 (subscription-oauth
  broker-injectability) + a dedicated security review. **v1 ships manual Layer-1 with no broker
  and no delegation.** The delegation engine must not be presented as part of the first shipped
  slice.
- **In subscription mode there is no per-call `$`** — any "$ saved" is entirely counterfactual.
  Accepted consequence: the honest headline meter in subscription mode is **quota-headroom-preserved**,
  with `$` suppressed or at most a clearly-labeled "≈ at API rates" secondary that never leads
  (which-meter-leads is mode-driven, not a fixed layout). Whether a labeled `$`-equivalent is
  acceptable at all is a **founder decision** (below).
- **The ≥25% requires a behavior shift** — the alpha must move whole self-contained tasks *out* of
  live CC *into* autonomous SealBox. If they won't, the honest live-CC number is ~10-15% and we
  must not imply we shrink the live session. Whether alphas make the shift is the pivotal unknown.
- The picker inherits the classifier's mechanical-scope-not-difficulty limit; mitigated by the
  upward-only adequacy bias + net-of-retry disclosure, but not eliminated — cheap-fail→capable-redo
  costs ~2× and erodes net savings on mis-picks.
- Adds a broker↔Scrooge recommend seam + a stateful-picker option (two cross-repo surfaces beyond
  DR-047's).
- **No code** — SealBox unbuilt, SPEC-002 in Specify; Tier-0 untouched; no cred/egress added.

## FOUNDER DECISIONS NEEDED

*(Genuine value / never-wrong / positioning calls this DR deliberately does NOT resolve — they
need a human. The architecture-shape opens are tracked in Costly-to-Refactor + Follow-ups.)*

1. **Positioning lead (the pivotal call).** Lead the alpha with **(A)** "your live session quietly
   gets leaner where you already work" — honest ceiling ~10-15%, relief-dominant, savings-modest —
   or **(B)** "a cheap autonomous plane to offload grunt work TO" — honest ≥25% but requires
   adopting an offload workflow. Different products, different first-run "wow". We **cannot**
   honestly put a ≥25% headline on a daily-driver-live-CC promise.
2. **Subscription-mode `$` honesty (sharp never-wrong call).** In subscription mode no dollars are
   spent, so any "$ saved" is pure counterfactual. Recommend **quota-headroom-preserved as the
   only honest headline meter there**, `$` suppressed or heavily-labeled "≈ at API rates". Accept
   quota-only, or is a labeled `$`-equivalent acceptable?
3. **Savings baseline + adequacy risk appetite.** (a) Is the counterfactual denominator
   "vs all-main-model (all-Opus)" or "vs no-SealBox at all"? — a never-wrong-sensitive choice we
   must defend on hover. (b) How aggressive is "cheapest-adequate"? Conservative (few retries-up,
   smaller gross, higher net certainty) vs aggressive (higher gross, retry-eroded net). Both need
   the Phase-0 distribution + a founder risk call. *(The net-of-retry honesty rule itself is not a
   founder call — it is fixed in §9 as an INV-13 application: a cheap-fail→capable-redo always
   counts its full cost against disclosed savings.)*
4. **Receipt team-visibility.** Does the receipt post as a `gh issue comment` by default (arrives
   where the user already is) — putting per-sub-task model + cost data into the issue tracker, a
   privacy call some orgs refuse — or IDE-pane-only / configurable? (Minor sibling calibration:
   Scrooge voice intensity on the receipt — full character vs restrained-plus-one-warm-line.)

## Follow-ups (tracked)

- **SealBox issue — the delegation planner surface (Layer-2).** File on `AIClarityAU/sealbox`:
  the spine + peelable-sub-thread decomposer (distinct from FR-14 concurrency and the DR-045
  visibility queue), including the decomposition-authorship decision (Costly-to-Refactor (c)).
  Extends DR-047 SealBox #2.
- **SealBox issue — the OutcomeStore disclosure record + INV-DISCLOSURE T0 (author BEFORE the
  picker).** File on `AIClarityAU/sealbox`: the CL-5 output-contract extension
  (`plannedModel`/`ranModel`/`provider`/`pickedBy`/`fallbackReason`/net-of-retry) + the T0
  invariant. This is DR-047's mandated-but-unwritten SPEC-002 FR; the whole never-wrong property
  depends on the record existing before any model auto-picks.
- **SealBox issue — the run receipt surface (Layer-1 single-model first, Layer-2 per-sub-task
  rows).** File on `AIClarityAU/sealbox`: v1 Layer-1 receipt discloses the single model the whole
  run used (establishing the honesty discipline); Layer-2 adds per-sub-task rows without
  retrofitting disclosure. Renders the two-meter (quota reclaimed · cash saved) mode-driven layout
  + the zero-honesty rule.
- **SealBox issue — the live-CC offload nudge + Scrooge statusline (advise-only).** File on
  `AIClarityAU/sealbox` (or the Scrooge skill repo): detect + recommend + one-keystroke, precision
  bar, cooldowns; explicitly *not* an interceptor. Note the sequencing/honesty call: it advertises
  L2 delegation not yet built — decide whether it ships before the broker exists.
- **Scrooge issue [#41](https://github.com/AIClarityAU/scroogellm/issues/41) (extend).** Pin the
  `recommend(taskShape) → {model, effort, thinking, confidence}` **or** ranked-list API surface
  (Costly-to-Refactor item 1); API-key-mode-first, subscription routing blocked on #74/#407.
- **SPEC-002 FRs (Specify-phase).** Author: (i) the broker↔Scrooge model-selection contract FR;
  (ii) the per-sub-task disclosure invariant (INV-DISCLOSURE) as a T0; (iii) the delegation-planner
  FR. All three mandated by DR-047 §Follow-ups / this DR; none written; deferred to SPEC-002, no
  `src/` yet.
- **#74 / #407 (blocking, human).** Subscription-oauth broker-injectability spike + the
  Anthropic-ToS "route subscription creds through another tool" legal decision. Gates the
  Scrooge-in-wire path; does **not** gate the SealBox-spawn quota-preservation path.

## Related

- **DR-047** (per-task model selection lives at the broker, not the live-CC proxy) — this DR is its
  **implementation design**: the delegation engine, the picker home, the disclosure record it
  mandated.
- **scrooge DR-016** (model/effort label honesty — no truthful auto-switch of a *live* session):
  INV-DISCLOSURE (§8) is its headless counterpart — the broker is where auto-pick becomes truthful
  because no live label contradicts it, *provided* the record discloses what ran.
- **scrooge DR-020** (subscription zero-marginal monetisation basis / INV-13 billing honesty) — the
  net-of-retry, no-gross-counterfactual disclosure rule (§9) and the subscription-mode `$`-suppression
  are direct applications.
- **scrooge DR-013** (usage-attribution dimensions / `X-Scrooge-Tag`) — the measure surface the
  broker meter feeds per sub-task.
- **DR-017** (host-side broker) — the credential-free model-call chokepoint this engine's picker +
  meter live at.
- **DR-045** (host IDE fan-out queue = Layer-1 visibility) — prior art for the receipt's agent-queue
  pane; explicitly *not* the delegation planner.
- **DR-046 / constitution invariants #1/#2/#6/#9** — credential-free exec-plane, broker-only egress,
  dedicated-worktree isolation, and subscription-first, all of which the peeled sub-threads obey.
- **MinSpecPro CLAUDE.md — "Scrooge Model-Fit Advisory"** — the advisory-only nag posture the
  live-CC surface (§10) inherits.

Triggered by: 2026-07-16 sizing the SealBox token-savings engine on measured dogfood traffic —
a transparent proxy tops out ~10-15% because 74% of spend is cache-efficient fat-Opus turns that
route at −228%; the ≥25% lever is sub-thread delegation (keep the spine lean, peel self-contained
sub-tasks onto cheap limited-context threads). Answered: build the delegation engine at the
SealBox broker (broker-owned Scrooge-independent picker — Scrooge-independent is not offline;
SealBox is Tier-1 and the broker may use the network, incl. an optional cheap LLM adequacy
judge — with Scrooge recommending when present), disclose the
actually-run model per sub-task as a T0 invariant authored before the picker, keep the live-CC
surface advise-only, and locate the honest ≥25% headline on the autonomous surface only — with the
positioning, subscription-`$`, baseline/risk, and team-visibility calls surfaced to the founder.
