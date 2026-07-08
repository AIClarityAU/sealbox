# sealbox — Agent Instructions

## For AI Coding Assistants

This project uses MinSpec SDD (Specification-Driven Development). Before implementing any change:

1. **Check scope** — How far does this change reach (files, lines, boundaries)? That sets the tier — not how hard the change feels.
2. **Read the spec** — Check `specs/` for existing specs related to your task.
3. **Follow the tier** — Don't over-specify small-scope tasks. Don't under-specify wide-scope ones. The predicted tier is a floor: raise it (never lower it) if a small change is subtler than its footprint.

## Specs Directory

All specifications live in `specs/`. Each spec file uses Spec Kit-compatible markdown with YAML frontmatter.

## Decision Records

Architecture decisions are documented in `docs/decisions/`. Check existing decisions before proposing conflicting approaches.

## Constitution

Project invariants, principles, and constraints are in `.minspec/constitution.md`. These rules must never be violated.

## Task Classification Guide

Before starting work, classify the task by its **mechanical scope** (blast radius), not by how hard it is to think through:

- **T1 (Contained):** Single file, one-line fix, typo, config change. One sentence of spec is enough.
- **T2 (Standard):** A few files, contained feature, no cross-boundary changes. Needs spec + plan.
- **T3 (Wide):** Many files, new APIs, schema/dependency changes. Full spec cycle.
- **T4 (Architectural):** Cross-project impact, new services, breaking changes. Complete ceremony required.

The classifier sees scope, not difficulty. A subtle one-line fix and a trivial one are the same size — so the predicted tier is a **floor**: raise it when a change is harder than its footprint, never lower it below the prediction.

## Rules

1. Never skip the spec phase, even for T1.
2. User override always wins — if the human says "just do it," do it. The predicted tier only ratchets up, never auto-down.
3. Ceremony must be proportional to scope — don't over-engineer small-scope tasks.

<!-- minspec:slash-commands:start -->

## Spec Kit Slash Commands

Generic agents can invoke the following commands. Each routes to a MinSpec SDD phase against the active spec.

| Command | Phase | Purpose |
|---|---|---|
| `/specify` | Specify | Start or update the Specify phase for the active MinSpec spec |
| `/clarify` | Clarify | Resolve open questions before planning |
| `/plan` | Plan | Draft the technical approach for the active spec |
| `/tasks` | Tasks | Break the plan into ordered, checkable tasks |
| `/analyze` | Analyze | Cross-check spec, plan, and tasks for consistency |
| `/implement` | Implement | Execute the task list against the active spec |

Full per-command instructions live in `.claude/commands/*.md` (Claude Code) and `.cursor/rules/spec-kit-commands.mdc` (Cursor) when those tools are detected.

<!-- minspec:slash-commands:end -->
