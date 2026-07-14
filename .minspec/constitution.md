# sealbox — Constitution

## Invariants

Rules that must never be violated. All changes must preserve them.

1. **Agent never executes in the extension host.** The agent process (`claude -p` or equivalent) runs only inside the execution-plane container/worktree — never in the vsix / VS Code extension host, which is the user's own credentialed process (SPEC-002 FR-1, two-plane split).
2. **Sandbox holds no host credentials and no egress except the broker seam.** No `~/.claude`, no `gh`/`CLOUDFLARE_API_TOKEN`/FTP/psql/wrangler creds, no `~/.config`/`~/.cache`/keychain, no network beyond the single allowlisted host-side broker socket (SPEC-002 FR-3, FR-6).
3. **Attestation fails closed.** Any should-be-denied capability that *succeeds* inside the sandbox aborts the dispatch — the agent never runs. A deny-check whose positive control also fails yields verdict FAIL, never an inferred "secure" (SPEC-002 FR-6, FR-7 — never infer safety from a dead probe).
4. **Untrusted issue/spec body is DATA, never instructions; the agent is credential-free.** Injection at worst yields a bad advisory or degraded output — never an action, approval, exfiltration, or write (SPEC-002 FR-15, DR-030 data-framing).
5. **No in-sandbox push.** The branch exits as a diff + `.agent-summary.md`; the credentialed control plane pushes and comments *after* the agent process has exited. The agent never holds the `gh` token (SPEC-002 FR-13).
6. **SealBox obeys global rule #8 — never mutates the user's shared checkout.** Every dispatched agent runs in a dedicated git worktree rooted outside every checkout (`~/code/.worktrees/<repo>/sealbox-<runId>/`). No SealBox code path runs a HEAD-moving git op, force-push, or force-delete on the user's primary checkout; the primary checkout's branch NAME and HEAD are verified unchanged before and after handoff (DR-046).
7. **Base-freshness is gated symmetrically — creation and push.** No agent branch is pushed against a base older than `origin/main` at push time: pinned SHA at creation, re-fetch + rebase-in-worktree (or fail-soft to `needs-review`) at push (DR-046, closing the FR-13 validator-asymmetry class).
8. **MinSpec core never depends on this extension.** No code path in `packages/minspec` or `packages/shared` may depend on agent-execute, the container runtime, the broker, or any network/AI module — MinSpec stays Tier-0 / air-gapped (SPEC-002 FR-16).
9. **Billing defaults to subscription quota — no silent PAYG.** The broker tries the dev's Pro/Max subscription first in every mode; a pay-as-you-go API key is injected only as capped overage spillover, and never appears in the sandbox (SPEC-002 FR-5).

## Principles

Guidelines that should be followed. Can be bent in exceptional circumstances with justification.

1. Honor CLAUDE.md project instructions — they override default behavior.
2. Record hard-to-reverse decisions as decision records before implementing.
3. **Agents you can trust because they stop.** The product's differentiator is tier-gated HITL, not "an AI that does everything" — T1–T2 auto-dispatch, T3–T4 wait for human spec/plan approval (EPIC-007 goal, SPEC-002 FR-12).
4. **No container runtime → degrade to Layer-1 manual, never "off".** Losing docker downgrades autonomy, never the trust boundary; the agent still never runs in the extension host (SPEC-002 FR-10).
5. **Never infer "secure" from a dead probe.** Every negative deny-check is paired with a positive control that must succeed — an unreachable canary could mean egress-blocked, curl-missing, or canary-down, never assume the safe reading (SPEC-002 FR-7).
6. **Scope honesty.** Attestation proves "as configured, this box cannot reach X" — a config-correctness gate, not a kernel/container-escape guarantee. State that residual explicitly rather than overclaiming (SPEC-002 FR-8).

## Constraints

Technical or business constraints that bound the solution space.

1. The substrate is consumed through one `SandboxRunner` port (spawn → attest → run → collect-diff → teardown); ~95% of the extension must stay testable against a mock runner with no docker daemon (SPEC-002 FR-2).
2. A global concurrency cap bounds in-flight sandboxes at all times, respecting the shared subscription account's window/weekly/session limits; API mode additionally carries a spend cap read from the broker's own meter (SPEC-002 FR-14).
3. Pushes target a per-dispatch-unique branch and are create/fast-forward-only — never `--force`, `--force-with-lease`, or any reset of a remote ref (SPEC-002 FR-13 push protocol, DR-046).
4. v1 is scoped to trusted, self-authored issue/spec bodies only; dispatching untrusted (non-self-authored) bodies is gated on the microVM/gVisor hardening path (SPEC-002 FR-15, open question #73).
5. Node.js 18+ runtime; VS Code extension packaging conventions (publisher `aiclarity`, extension id `aiclarity.sealbox`).

## Goals

What this project is trying to achieve. The outcomes work should ladder up to.

1. **Execution never contaminates the methodology core.** Ship SealBox as a separate,
   opt-in Tier-1 extension so MinSpec itself stays air-gapped (Tier 0) — credentials,
   network, and autonomy live only behind this boundary (EPIC-007 Principle).
2. **An escaped or misbehaving agent has nothing to exfiltrate.** Unattended dispatch
   is gated on no-credential execution isolation — the sandbox holds no secrets and
   reaches models only through a host-side broker that injects credentials it never
   sees (DR-008, DR-017).
3. **Trust is a boundary, not a prompt.** Credential-free, no-egress, attested,
   diff-only-handoff, tier-gated HITL — the product pitch is mechanism, not a claim of
   infallibility (README, SPEC-002).
4. **Default cost posture protects the dev's wallet.** Subscription-first billing with
   no silent PAYG spend; ScroogeLLM cost-routing is an explicit opt-in layered on top,
   never a default (DR-016, DR-047).
- Trace specs to their owning epic so scope ladders up to a goal.
