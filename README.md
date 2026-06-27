# SealBox

> The credential-free **"Execute"** agent — third extension in the MinSpec line
> (MinSpec → ScroogeLLM → **SealBox**). An autonomous coding agent that runs in a
> **sealed box it can't break out of**: no host credentials, no egress except a brokered
> model call, and it **can't push without your review**.

**Status: pre-launch.** Waitlist site live at **[sealbox.dev](https://sealbox.dev)**. The
extension itself is not built — its requirements were harvested as `SPEC-019` (execution
substrate) in the MinSpec monorepo and are being migrated here (split out of
`harvest316/minspec` per the decision that created this repo; mirrors the ScroogeLLM split,
DR-027). Publisher: **Audit&Fix** · marketplace publisher id `aiclarity` · ext id (planned)
`aiclarity.sealbox`.

## Why it exists

Most coding agents run with *your* credentials. SealBox is built so the agent simply never
has them — trust is a **boundary**, not a prompt:

- **Credential-free** isolated execution (no tokens, keys, or `~/.claude`).
- **No egress** but a host-side broker for the model call.
- **No in-sandbox push** — work leaves as a diff the host reviews and pushes.
- **Attested boundary** that must *fail closed* before any run.
- **Tier-gated human-in-the-loop** — it stops to ask on complex/risky work.

## Layout

| Path | What |
|---|---|
| `sites/sealbox.dev/` | The marketing + waitlist site (Cloudflare Pages, project `sealbox-dev`). |
| `sites/sealbox.dev/functions/api/waitlist.js` | Waitlist capture (Pages Function → Workers KV `WAITLIST`). |
| `.github/workflows/deploy-site.yml` | Auto-deploys the site to CF Pages on push to `main`. |

Product specs/code land here as the `agent-execute` → `sealbox` migration proceeds.

## Deploy

The site auto-deploys on push to `main` (needs repo secret `CLOUDFLARE_API_TOKEN`). Manual:

```bash
npx wrangler@4 pages deploy sites/sealbox.dev --project-name=sealbox-dev --branch=main
```
