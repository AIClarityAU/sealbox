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

*Status: superseded · Date: 2026-07-01*

<!-- dr-summary:DR-047 auto=b1e06bbc40f0 -->
Claude Code now ships **Workflow** + **background agents** — orchestrator-side fan-out where each spawned agent carries its own {model, effort} (agent(prompt, {model, effort}), plus the CLAUDE.md *Subagent Model & Effort Selection* table). This raised the question: with the orchestrator already choosing a model per sub-task, does **Scrooge** — sitting at ANTHROPIC_BASE_URL — still get to do the thing that *is* its value, pick the most appropriate model/effort/thinking per task? And if not, do we need Scrooge or SealBox to provide…
<!-- /dr-summary:DR-047 -->

## [DR-048 — The SealBox broker delegation engine — cheapest-adequate model per sub-task on limited-context sub-threads, truthfully disclosed; the token-savings engine a transparent proxy structurally cannot be](DR-048-broker-delegation-engine.md)

*Status: superseded · Date: 2026-07-16*

<!-- dr-summary:DR-048 auto=7b9459307438 -->
DR-047 answered *where* a truthful per-task model pick may live: not in the Scrooge proxy behind live Claude Code (any wire-level swap contradicts CC's own per-subagent label — the DR-016 lie), but at the **headless SealBox broker**, where SealBox *is* the orchestrator and there is no live label to contradict. DR-047 left the engine itself unbuilt and named two costly-to-refactor seams: the broker↔Scrooge selection interface, and the per-sub-task disclosure record.
<!-- /dr-summary:DR-048 -->
<!-- minspec:dr-index:end -->
