# Agent-Execute (third "Execute" vsix) — Naming Brief

> **STATUS: DECIDED — "Sealbox" (2026-06-27).** The user chose **Sealbox** and registered
> **sealbox.dev on Cloudflare** (zone active on the shared CF token, beside
> minspec.dev/scroogellm.com). Ext id → **`aiclarity.sealbox`**. Availability confirmed via
> CLI: VS Code marketplace **0 matches**, scoped npm **`@aiclarity/sealbox` free** (publish
> scoped — bare npm `sealbox` is a niche encryption lib by "gooncity", Dec 2025). **STILL
> OWED: USPTO/EUIPO trademark knockout** (the security-adjacent bare-npm name raises this).
> Cascade pending: DR-015 + SPEC-002 `agent-execute`→`sealbox` id refs, #66 resolution, CF
> Pages site. The shortlist/analysis below is retained as the rationale of record.
>
> *History: produced by the #66 workflow (`wf_8f93b5e7-238`); Scan+Generate completed, the
> live-web Vet+Synthesize phases were cut by a session limit, so the per-candidate collision
> calls below were model-knowledge only — superseded for Sealbox by the CLI checks above.*

## Scan findings (3 of 4 solid; SEO scan failed)

- **Open-lane finding (trust-wedge scan — strong).** **Nobody owns the product-level lane
  "an agent you can trust because it physically *can't* betray you."** It is **OPEN** at the
  IDE/marketplace coding-agent level; only **crowded at the plumbing/library level** (closest
  prior art: *Infisical Agent Vault* — a backend credential-proxy lib, not a product).
  → **Lead the security/credential-boundary wedge.** Confirms the 2026-06-27 positioning note.
- **Competitive scan.** The "autonomous AI software engineer" lane is owned (Devin = person-name,
  "hire an AI engineer"; Cursor/Aider/Codegen/Sweep/Amp crowd "fast autonomous coding").
  Don't fight there — the bounded/gated/credential-free lane is the opening.
- **Naming-craft scan.** **Coined compound (two fused morphemes) is the safest pattern for the
  third sibling** — it scans as a set with **Min+Spec** and **Scrooge+LLM**, and compounds are
  the most trademark-defensible class. Do **not** gate on a short `.com` (effectively
  impossible in 2026); `.dev`/`.ai`/`.sh` are normal for dev tools.
- **SEO scan — DISCARD.** The keyword/SEO agent returned a schema stub (`"test"`/`a,b,c,d`) —
  no real data. Re-run needed; non-blocking (the trust-wedge + competitive scans carried the
  signal).

## The 16 candidates + preliminary (knowledge-only) triage

Lead angles: **SB** security-boundary · **EV** execute-verb · **TS** trust-stop · **CO** coined.

| # | Brand | id | Angle | Preliminary collision read (⚠️ not web-verified) | Lean |
|---|---|---|---|---|---|
| 1 | **Airlock** | aiclarity.airlock | SB | **Airlock Digital** (app-allowlisting *security* vendor) — collision in our exact space | ✂️ cut |
| 2 | **Sealbox** | aiclarity.sealbox | SB | Mild echo of libsodium "sealed box" / Bitnami "Sealed Secrets" — thematically apt, low brand collision | ✅ keep |
| 3 | **Wardline** | aiclarity.wardline | SB | "Ward Line" = a defunct historic steamship co; ~no modern tech collision; coined compound | ✅ keep |
| 4 | **Aegis** | aiclarity.aegis | SB | Saturated: Aegis Authenticator (2FA), Aegis Combat System, crypto Aegis — generic | ✂️ cut |
| 5 | **ShipGate** | aiclarity.shipgate | EV | Low tech-brand collision; clear ship(execute)+gate(HITL) dual meaning; coined compound | ✅ keep |
| 6 | **Landlock** | aiclarity.landlock | EV | **Linux Landlock** = a famous *kernel sandbox API* — same-domain collision + descriptive | ✂️ cut |
| 7 | **Forgegate** | aiclarity.forgegate | EV | "Forge" saturated (SourceForge/Laravel Forge/Forgejo); "-gate" = scandal suffix baggage | ✂️ lean-cut |
| 8 | **Dispatchward** | aiclarity.dispatchward | EV | Low collision but clunky/long/hard to say (flagged by generator) | ✂️ cut |
| 9 | **Halton** | aiclarity.halton | TS | **Halton Group** (HVAC co) + Halton region (CA/UK); reads as place/surname, weak "halt" link | ✂️ lean-cut |
| 10 | **Askfirst** | aiclarity.askfirst | TS | **AskFirst** = Ada/NHS symptom-checker (health domain); clearest HITL meaning of the set | 🟡 maybe |
| 11 | **Holdfast** | aiclarity.holdfast | TS | *Holdfast: Nations at War* (game) + Patagonia "Holdfast"; evocative (stop+secure), a bit archaic | 🟡 maybe |
| 12 | **Checkrein** | aiclarity.checkrein | TS | Obscure horse-tack term; very low collision, precise "bounded autonomy"; spelling/say friction | 🟡 maybe |
| 13 | **Tendril** | aiclarity.tendril | CO | **Tendril** (energy/IoT co, acq. Uplight); weak execute/trust semantics ("reaches but tethered") | ✂️ lean-cut |
| 14 | **Velo** | aiclarity.velo | CO | **Wix Velo** (a *dev platform* — same space) + "velo"=bike; reads as bike not "veil" | ✂️ cut |
| 15 | **Cinch** | aiclarity.cinch | CO | **cinch.co.uk** (big UK car retailer) + Cinch gem/gaming; busy brand; "easy" undercuts "secure" | ✂️ lean-cut |
| 16 | **Tetherd** | aiclarity.tetherd | CO | **Tether** (USDT) confusion + dropped-e reads as typo / hard to say aloud | 🟡 maybe |

## Preliminary top picks (to web-vet first)

Best fit = **lead angle (security-boundary)** × **coined-compound sibling pattern** × **low collision**:

1. **Wardline** *(SB, coined compound)* — "a warded line your agent — and your secrets — never
   cross." Scans cleanly beside MinSpec/ScroogeLLM; dodges the taken "Warden"; strongest
   on-wedge + on-pattern. **Top pick to vet.**
2. **Sealbox** *(SB, coined compound)* — "sealed by default; a box it can't break out of."
   Deny-by-default containment without the taken Vault/Enclave/Bastion.
3. **ShipGate** *(EV, coined compound)* — "code ships through a gate, not around you." Pick this
   if you'd rather foreground the **Execute** verb than the security boundary.

Clearest **trust-stop** expression if you lead the HITL angle instead: **Askfirst** (verify the
health-app collision) — "it asks first: plan gate, findings gate, diff-before-push."

## Before committing (human action — web-vet pending)

Every row above needs the live checks the Vet phase didn't reach:
- **Registrar:** `.dev`/`.ai`/`.sh` availability for the top 2-3 (don't gate on `.com`).
- **Trademark:** USPTO + EUIPO knockout search (esp. dev/software class 9/42).
- **Marketplace/npm/GitHub-org:** `aiclarity.<name>` id free; no `<name>` npm/ext collision.
- **Live product collision:** the ⚠️ reads above are knowledge-only — confirm on the open web.

## Finishing the analysis

Resume after the 09:00 UTC limit reset re-runs **only** the 16 Vet agents + Synthesize
(Scan+Generate are cached). Note the cached SEO scan is the garbage stub — non-blocking, but
re-run it if keyword/CPC data is wanted. Resume:
`Workflow({scriptPath: ".../agent-execute-naming-analysis-wf_8f93b5e7-238.js", resumeFromRunId: "wf_8f93b5e7-238"})`
