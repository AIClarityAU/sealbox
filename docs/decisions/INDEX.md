<!-- minspec:dr-index:start -->
# Decision Register

_Architecture decisions for this project. One entry per accepted/proposed DR._

## [DR-045 — A host IDE's background-task runner is Layer-1 visibility, never a Layer-2 degrade substrate (SPEC-002 FR-9/FR-10 interaction)](DR-045.md)

*Status: accepted · Date: 2026-06-29*

<!-- dr-summary:DR-045 auto=71d2bfb18e9e -->
The host IDE (the Claude Code VS Code extension) now surfaces **pending background tasks** in the IDE whenever it spins up a batch of background agents — a fan-out queue the human can glance at and interrupt. This raised a design question against SPEC-002's dispatch model: how does it interact with **FR-9** (manual Layer-1 vs autonomous Layer-2 mode split) and **FR-10** (no container runtime → degrade to Layer-1 manual, never "off")?
<!-- /dr-summary:DR-045 -->

## [DR-046 — SealBox dispatch obeys rule #8 — dedicated-worktree isolation + symmetric base-freshness (creation AND push) as T0 invariants](DR-046.md)

*Status: accepted · Date: 2026-06-29*

<!-- dr-summary:DR-046 auto=621021227cf9 -->
SPEC-002's **FR-13** hands the agent's branch out as a diff and has the credentialed control plane push it **after the agent exits**. Its one concurrency guard is a *creation-time* sub-bullet: branch off origin/main (fetched parent-side), never the stale local main. The session question: SealBox does not run in a vacuum — concurrently the human **merges PRs** (origin/main advances), **edits main directly**, and **other Claude Code sessions work in sibling worktrees** on the same .git. Does FR-13 keep SealBox from getting…
<!-- /dr-summary:DR-046 -->

## [DR-047 — Per-task model/effort selection for agent fan-out lives at the SealBox broker (Scrooge routes there) — not in the Scrooge proxy behind Claude Code, and not as a Scrooge-owned fan-out](DR-047.md)

*Status: proposed · Date: 2026-07-01*

<!-- dr-summary:DR-047 auto=pending -->
Claude Code now ships Workflow + background agents that fan out with per-agent `{model, effort}`, raising the question: can Scrooge still save tokens by picking model/effort/thinking per task, or does the CC orchestrator own that choice now? Two layers: the **orchestrator** already picks per sub-task (CC owns it, best context); the **proxy (Scrooge)** could only re-pick by overriding the caller's model — the DR-016 never-wrong label lie. So under CC, Scrooge = cache + measure + advise, **not** picking; do not build a Scrooge-owned fan-out. The truthful per-task pick lives at the **headless SealBox broker** (DR-017): no live per-subagent label to contradict, so Scrooge can route+pick there end-to-end, disclosed in the run outcome record.
<!-- /dr-summary:DR-047 -->

## [DR-048 — The SealBox broker delegation engine — cheapest-adequate model per sub-task on limited-context sub-threads, truthfully disclosed; the token-savings engine a transparent proxy structurally cannot be](DR-048-broker-delegation-engine.md)

*Status: proposed · Date: 2026-07-16*

<!-- dr-summary:DR-048 auto=pending -->
Implements DR-047's ruling. Measured: a transparent proxy tops ~10-15% for a cached agentic user because 74% of spend is fat cache-efficient Opus turns that route at −228% (cache thrown away). The token-savings engine is **sub-thread delegation** — keep an expensive lean **spine**, peel *simple + self-contained* sub-tasks onto separate **limited-context** threads on the cheapest-adequate model (little cache to lose → genuinely cheap). Only truthful where SealBox **is** the orchestrator (the broker), never on the live-CC wire (DR-047 §1). Broker owns an offline deterministic picker; Scrooge *recommends* when present (API-key mode); subscription-mode Scrooge is out-of-wire (#74/#407) so the picker must be broker-owned. **INV-DISCLOSURE** (headless counterpart of scrooge DR-016 INV-16): the outcome record states the per-sub-task model that *actually ran*, broker-metered, authored before any auto-pick. Live-CC surface is **advise-only** (offload nudge). The **≥25% is projected, not measured** (autonomous work doesn't exist yet). 4 founder decisions surfaced (positioning lead, subscription-`$` honesty, savings baseline/risk, receipt visibility). Born proposed; no code.
<!-- /dr-summary:DR-048 -->
<!-- minspec:dr-index:end -->
