<!-- minspec:dr-index:start -->
# Decision Register

_Architecture decisions for this project. One entry per accepted/proposed DR._

## [DR-045 — A host IDE's background-task runner is Layer-1 visibility, never a Layer-2 degrade substrate (SPEC-019 FR-9/FR-10 interaction)](DR-045.md)

*Status: accepted · Date: 2026-06-29*

<!-- dr-summary:DR-045 auto=71d2bfb18e9e -->
The host IDE (the Claude Code VS Code extension) now surfaces **pending background tasks** in the IDE whenever it spins up a batch of background agents — a fan-out queue the human can glance at and interrupt. This raised a design question against SPEC-019's dispatch model: how does it interact with **FR-9** (manual Layer-1 vs autonomous Layer-2 mode split) and **FR-10** (no container runtime → degrade to Layer-1 manual, never "off")?
<!-- /dr-summary:DR-045 -->

## [DR-046 — SealBox dispatch obeys rule #8 — dedicated-worktree isolation + symmetric base-freshness (creation AND push) as T0 invariants](DR-046.md)

*Status: accepted · Date: 2026-06-29*

<!-- dr-summary:DR-046 auto=621021227cf9 -->
SPEC-019's **FR-13** hands the agent's branch out as a diff and has the credentialed control plane push it **after the agent exits**. Its one concurrency guard is a *creation-time* sub-bullet: branch off origin/main (fetched parent-side), never the stale local main. The session question: SealBox does not run in a vacuum — concurrently the human **merges PRs** (origin/main advances), **edits main directly**, and **other Claude Code sessions work in sibling worktrees** on the same .git. Does FR-13 keep SealBox from getting…
<!-- /dr-summary:DR-046 -->
<!-- minspec:dr-index:end -->
