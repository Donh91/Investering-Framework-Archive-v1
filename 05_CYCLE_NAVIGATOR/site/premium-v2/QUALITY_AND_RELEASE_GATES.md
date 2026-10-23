# Premium v2.1 · staged candidate acceptance matrix

**Date:** 2026-10-23 · **Owner:** SITE #1578 · **Oversight:** #1156  
**Current state:** ISOLATED DEVELOPMENT ONLY, NOT LIVE, NOT OWNER VISUALLY APPROVED.  
**DRAFT PR:** #1769. Do not merge or switch canonical root from this status.

## Source and design freeze

- [x] Design Registry established with explicit acceptance hierarchy, 12 Oct minimalist Kompas, approved Graph B reference, PATH 10-phase spec and Proof FROZEN→OBSERVED→ASSESS
- [x] All nine source AppDeploy B/C files captured at app snapshot `1792595071401`, unchanged, reference-only and NOT PUBLIC ASSET
- [x] Actual B markup/SVG copied from original AppDeploy DOM into graph-b, demo starting quote/forecast restore switch removed
- [x] Original authored AppDeploy CSS copied for B with only three non-browser `@tailwind` directives removed; original quarantined untouched
- [x] Proof external source must link to exact 40-hex commit + allowlisted public path, with independently sealed proof explicitly false
- [ ] Owner's approved 390/430 physical iPhone screenshots captured as hash-bound visual reference in GitHub under approved privacy/metadata controls
- [ ] Actual candidate B screenshot compared pixel/geometry/text hierarchy against B/C original reference. **No longer assume CSS style equals original visual.**

## Source authority and model firewall

| Evidence | Status | Required behavior |
| --- | --- | --- |
| Current W43 expected-close daily path | UNAVAILABLE | no blue expected day-by-day price curve |
| Genuine aggregate original D1–2, D3–4, D5–7 ranges | AVAILABLE | source-exact shaded interval windows, never interpolated blue midpoints |
| First-party BTC/ETH hourly closes | AVAILABLE but time-sensitive | only eligible original hourly spot PASS source, preserve UTC gaps |
| Official Compass action | source-issued | show as current ONLY while `valid_until_utc` not reached, otherwise explicitly historical |
| PATH position | UNAVAILABLE | no blue “we are here” or inferred ETA |
| 70/30 source-reported live price-range precision | PROVISIONAL | labelled original-score-to-date, separate from Direction/Edge and investment return |
| Public Edge Scorebook | PROVISIONAL_NOT_SEALED | 10/10 ABSTAIN W42 and W43; no invented binary accuracy |
| Original Git SHA + public source URL | navigation identity only | does NOT independently establish an ex-ante timestamp |
| Original score proof seal | NOT VERIFIED | independent witness + immutable publication + recomputed score missing |

## Current development code and tests

`graph-b/official-source-adapter.mjs`: 8 positive/negative source tests  
`proof/public-source-links.mjs`: 7 public commit/ABSTAIN tests  
`proof/price-range-proof.mjs`: 5 three-window original source/coverage tests  
`compass/official-compass-path.mjs`: 4 five-horizon/seven-tier/expiry/phase tests  
`preflight.test.mjs`: 5 original source/quarantine/root builder tests  
`build-next.test.mjs`: 4 noncanonical staging isolation tests

Mandatory normal Node commands from repository root (using existing installation, no new packages required):

```sh
node --test 05_CYCLE_NAVIGATOR/site/premium-v2/graph-b/official-source-adapter.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/proof/public-source-links.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/proof/price-range-proof.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/compass/official-compass-path.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/preflight.test.mjs \
  05_CYCLE_NAVIGATOR/site/premium-v2/build-next.test.mjs
```

The owner-approved NEXT-only bundle is packaged locally **only after normal build** with:

```sh
node 05_CYCLE_NAVIGATOR/site/premium-v2/build-next.mjs
```

This emits `site/dist/next/`, never rewrites `site/dist/index.html`, and bundles ONLY the allowlisted 11 source UI files plus a staging `index.html`. It must not be connected to the existing production Pages action without a reviewed safety change and explicit staging gate.

## Visual/manual browser requirements

- [ ] Open noncanonical staged `/next/graph-b/source-graph-b.html` on the actual host once available. No AppDeploy link substituted as proof.
- [ ] Compare at 390×844 and 430×932 with exact approved AppDeploy B screenshots; inspect white frame/card spacing, Deep Navy plot, original dashed blue source-only condition, green actual, low/high shaded window geometry, typography, readable right price axis and 44px touch targets.
- [ ] DA/EN switch updates ALL B, Proof, Compass/PATH sections, not merely header language attribute.
- [ ] Genuine BTC→ETH→BTC switching, time scrub to earlier actual hour and missing hourly gap behavior.
- [ ] Source stale→fresh, now→expired in an **already-open tab**; late bundle must not show current action.
- [ ] Browser network verifies `/data/latest.json`, `/data/compass.json`, `/data/publication-lineage.json`, and public scores; CORS failure means Proof links unavailable (NOT silently verified).
- [ ] Price-range Proof FROZEN→OBSERVED→SCORED transitions show original immutable ranges, source-reported coverage 42/42, 48/48, 15/72 at verified W43 historical test time, no recomputed score and no stale “current” claim.
- [ ] Edge: original public source link resolves to source commit; exact blob SHA and source SHA-256 checked. Fail without original.
- [ ] Keyboard, VoiceOver, focus visibility, reduced motion, 200% text size, safe area insets; iPhone Safari on physical device required.
- [ ] New front end remains performant; no extra market fetch loop, no new paid backend/data provider, no server-side task or external model router.
- [ ] Existing legacy NOW, PATH, PROOF continue working; verify measured behavior rather than assuming old root is fully compatible.

## Governance/readback

- [ ] Real Node tests, exact PR HEAD checks, source and independent adversarial review.
- [ ] Compare current main against branch; rebase/reconcile any new unrelated main changes before safe merge (never force-push unseen changes).
- [ ] NEXT-only staging build can be viewed on PUBLIC GitHub Pages without changing canonical root and with an explicit “DEVELOPMENT ONLY” disclaimer.
- [ ] Only after owner accepts paired visual & functional test and verified source issue/expiry, prepare **separate** official-root release PR, with exact build/CDN hash, reversal rehearsal and no silent AppDeploy promotion.
- [ ] Final owner release decision recorded separately. No production root changes before then.

**Hard stop:** A screenshot/mock/blue sine wave is never a real issued market forecast; a green CI signal is never a substitute for owner-approved visual geometry.
