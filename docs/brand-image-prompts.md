# SealBox — Image-Generation Prompts

Brand: **SealBox** — "the coding agent that can't betray you." Security/credential-boundary
wedge. Sits beside **MinSpec** (blue `#6c9cfc`) and **ScroogeLLM** (green/gold), so SealBox
owns **teal**.

**Palette:** near-black `#0d0f14` bg · surfaces `#14171f`/`#181c26` · borders `#272b38` ·
accent teal `#2dd4bf` · bright teal `#5eead4` · text `#e4e7ee`.
**Feel:** serious, trustworthy, technical, minimal, geometric. A developer tool, not a toy.
The metaphor is a **sealed box / vault / airlock** — something closed *by construction*.

**Workflow tips**
- Generate the **mark without text** — set the "SealBox" wordmark in CSS/SVG for crisp type.
  (If you want text baked in, use **Ideogram** or **Google Imagen** — they render letters best.)
- Logo/icon → export **transparent PNG + SVG**. Illustration/cards → **Midjourney v6 / SDXL / Imagen**.
- Always include the avoid-list; AI loves to add gradients, drop shadows, and stock-clip-art locks.

---

## 1. Primary logo mark (icon, no text) — pick one direction

**1A — Padlock-on-a-box (matches current favicon, safest)**
> A minimalist geometric logo mark: a rounded square container ("box") viewed head-on with a
> small padlock shackle emerging from its top edge, and a subtle keyhole at center. Single flat
> teal stroke (`#2dd4bf`) on transparent background, 2px-equivalent uniform line weight, rounded
> joints, no fill or a very dark fill (`#14171f`). Modern developer-tool app-icon style, crisp at
> 32px, balanced negative space. Flat vector, no gradient, no shadow, no 3D, no photorealism.

**1B — Sealed vault / airlock door (boldest, most "secure")**
> A minimalist logo mark of a circular vault/airlock door set into a rounded square, with a
> bold central locking-pin hub and four short radial bolts, faint concentric ring. Flat
> two-tone: teal `#2dd4bf` linework and accents on a near-black `#0d0f14` rounded-square tile.
> Geometric, confident, symmetrical, fintech-grade trust. Vector, flat, no gradient, no shadow,
> no realism, no text.

**1C — Isometric sealed cube with a seam of light (most distinctive)**
> A minimalist isometric cube ("box") sealed shut, with a single thin glowing teal seam of light
> tracing the closed lid — implying something contained that cannot get out. Flat teal `#2dd4bf`
> / bright teal `#5eead4` edges on transparent, subtle inner darkness `#0d0f14`. Clean geometric
> line-art, tech-brand mark, readable at small sizes. No gradient mesh, no heavy 3D shading, no
> photorealism, no text, no clipart lock.

*Aim for a mark that still reads at 24–32px. Ask for variations on a transparent background.*

---

## 2. Logo lockup (icon + wordmark)

> Horizontal logo lockup: the SealBox box-and-lock mark to the left, the wordmark "SealBox" to
> the right in a geometric humanist sans-serif (think Inter / Geist / Söhne), medium-bold, with
> "Seal" in light text `#e4e7ee` and "Box" in teal `#2dd4bf`, tight letter-spacing. On both a
> transparent and a near-black `#0d0f14` background. Clean, balanced, SaaS developer-tool brand.
> No tagline, no gradient, no shadow.

*(Easiest path: keep the CSS wordmark already on the site and only generate the icon in §1.)*

---

## 3. App icon / favicon (square, fills the tile)

> A square app icon, fully filled rounded-square tile in near-black `#0d0f14` with a subtle
> top-down teal glow. Centered: the SealBox sealed-box-with-padlock mark in bright teal
> `#5eead4`, bold enough to read at 16px. Flat, crisp, high-contrast, no text, no gradient banding.

Export 512×512 and 32×32; a transparent SVG already ships at `sites/sealbox.dev/favicon.svg`.

---

## 4. Open Graph / social card — 1200×630 (needed; site currently has none)

> A 1200×630 social share card, near-black `#0d0f14` background with a soft teal radial glow
> top-center. Left-aligned bold headline in white "The coding agent that can't betray you." with
> "can't betray you" in teal `#2dd4bf`; a smaller muted subline "Credential-free, sealed
> execution · sealbox.dev". The SealBox sealed-box-with-lock mark glowing teal in the upper-left
> or right third. Generous margins, premium developer-tool aesthetic, sharp legible type, flat
> design, no stock photos, no clutter.

Save as `sites/sealbox.dev/img/og-sealbox.jpg` (1200×630), then add to `index.html`:
`<meta property="og:image" content="https://sealbox.dev/img/og-sealbox.jpg">` (+ width/height/alt).
*Use Ideogram/Imagen for the baked-in text, or generate the background only and overlay text yourself for pixel-perfect copy.*

---

## 5. Hero background (optional — site currently uses a CSS glow)

> An abstract, dark, subtle hero background, 2400×1400, near-black `#0d0f14` deepening to the
> right. Faint geometric motifs evoking a sealed enclosure: a soft grid of thin teal lines, a
> single concentric "vault ring" of light low-opacity off to one side, gentle teal `#2dd4bf`
> radial bloom. Very low contrast so white text sits cleanly on top — atmospheric, not busy. No
> subject, no text, no harsh highlights.

Export `.webp` + `.jpg` to `sites/sealbox.dev/img/` and wire into the `.hero` background like
minspec.dev does (it currently uses only a CSS gradient — drop-in optional).

---

## 6. Section spot-icons (optional set of 6 — the "How it's sealed" cards)

> A cohesive set of six minimalist line icons, uniform 2px teal `#2dd4bf` stroke on transparent,
> rounded joints, 48px grid, matching geometric style: (1) an open box with no keys inside
> [credential-free], (2) a box with a single outbound arrow into a small "broker" diamond, all
> other arrows blocked [no egress but the model], (3) a box emitting a "diff" document, push
> arrow crossed out [can't push], (4) a shield with a checkmark formed from a probe line
> [attested], (5) a hand/stop bar halting a gear [stops to ask], (6) a document wrapped in
> quotes inside a box [untrusted input is data]. Consistent weight and corner radius across all
> six. Flat, no fill, no gradient, no shadow, no text.

*(The site currently uses simple teal dots — swap in this set if you want richer cards.)*

---

## 7. Optional mascot / character

SealBox leads a **security/trust** message, so a mascot is optional and risks undercutting the
serious tone (unlike ScroogeLLM's frugal mascot). If you want one anyway:

> A friendly but stoic robot/guardian character shaped like a small sealed strongbox with simple
> glowing teal eyes and short sturdy arms folded, standing watch in front of a vault door.
> Flat-shaded modern mascot, teal `#2dd4bf` and dark `#181c26` palette, clean vector style,
> trustworthy and calm (a loyal guard, not a villain). Transparent background. No text.

**Recommendation:** ship §1 (mark) + §3 (icon) + §4 (OG card) first — those are load-bearing.
§5/§6/§7 are polish.
