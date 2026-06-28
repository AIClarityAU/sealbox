# sealbox — Project Instructions

## Overview

sealbox project managed with MinSpec SDD methodology.

- **Specs directory:** `specs/`
- **Decisions directory:** `docs/decisions/`

## Invariants

These rules must never be violated. All changes must preserve them.

<!-- Add project invariants here -->

## SDD Methodology

This project uses Specification-Driven Development. Tasks are classified by **mechanical scope** (blast radius — files, lines, boundaries touched), not by how hard they are to reason about. The predicted tier is an upward-only floor: it never lowers ceremony on its own, and you can always raise it.

| Tier | Ceremony | Phases Required |
|------|----------|-----------------|
| T1 | One-sentence spec | specify |
| T2 | Spec + plan | specify, plan |
| T3 | Full spec cycle | specify, plan, tasks, implement |
| T4 | Complete ceremony | all phases |

## File Locations

| Artifact | Location |
|---|---|
| Specs | `specs/` |
| Decisions | `docs/decisions/` |
| Constitution | `.minspec/constitution.md` |
| Config | `.minspec/config.json` |

## Commands

MinSpec is a **VS Code extension**, not a CLI — run everything from the Command Palette (`Ctrl/Cmd+Shift+P`), typing "MinSpec:".

| Command Palette | Purpose |
|---|---|
| *MinSpec: Initialize SDD Structure* | Scaffold `.minspec/` + harness files. Also offered automatically when you open an un-initialized project. |
| *MinSpec: Refresh Harness Files* | Re-merge harness templates, preserving your edits. |
| *MinSpec: Classify Task Complexity* | Classify the current change into a tier (T1–T4). |
| *MinSpec: Show SDD Status* | Show the current phase and spec status. |
| *MinSpec: Create Architecture Decision Record* | Create a new `DR-NNN` in `docs/decisions/`. |
