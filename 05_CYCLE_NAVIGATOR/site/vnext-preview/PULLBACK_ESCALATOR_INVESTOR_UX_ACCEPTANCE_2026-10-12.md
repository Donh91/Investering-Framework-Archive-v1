# Cycle Navigator · Pullback escalator + investor disclosure · 2026-10-12

**Parent:** Existing vNext site Draft PR #1576 / production work owner #1578.  
**Research:** Same Compass Horizon Edge mission #1573 `R4P_PULLBACK_INVESTOR_DECISION_EDGE_20261012`, governed risk owners #1553 / #1530 and Forward Path #1516.  
**Status:** SOURCE-ONLY CODED and scoped CI PASS on branch once verified at exact HEAD. No live production/Pages release, no authenticated 1–10 odds, no approved SELL or experimental risk rule.

## Intent

Retain the user-approved **Quiet Precision / minimal Kompas**: no new tabs, no dark radar, no redundant card, no extra always-open paragraphs, two compact tables (5 horizons + 7 asset classes), Bull/Bear unchanged, DA/EN. One small, **genuinely useful categorical Pullback escalator** directly underneath the existing immediate three-metric strip; a concise owner-issued stage and possible ETA remain in existing Overview risk row. All long details remain inside the **same existing Pullback, beskyttelse & re-entry native dropdown**, closed by default. Absolutely no site-side market/SELL ownership.

## Visual contract

1. **Five disconnected small marks** `NORMAL | BUILDING | ELEVATED | HIGH | CONFIRMED`. Highlight **only the exact current source class**, not everything to its left. Never show an animated filling progress bar or numbers 1–10: severity is not a countdown/probability. A decline can be averted; next read may regress to NORMAL or lose data and clear every highlight.
2. One adjacent text line source-risk class + plain-language status; **source ETA / unsupported timing** distinctly visible, never convert HIGH to "5 hours" or week 42 to a promised event date.
3. Source-led qualitative `LOW/MEDIUM/HIGH` is **evidence quality**, never a 70/80/90% event probability.
4. **Existing disclosure**, 10 concise facts (not a new panel):
   - possible onset/ETA (official source only);
   - likelihood 1–10 **NOT CALIBRATED** until true pre-registered event/horizon/outcome calibration;
   - BTC/ETH dip magnitude **NOT QUANTIFIED**;
   - large/mid/small/micro/memes impact **NOT QUANTIFIED**;
   - duration / trough/re-entry speed **NOT ASSESSED**;
   - original source 2–3W direction, **not** inferred bear label;
   - original source 4–8W cycle direction, separate from 2–3W;
   - longer structural bear transition **NOT CLASSIFIED**;
   - public typed `watch_for` only if risk and week match;
   - public typed `weakens_if` or existing owner invalidation, never fabricated.
5. Existing SELL, Distribution and Re-entry states remain distinct, still under Official Compass, no user wallet on public site. `HOLD_WAIT` does not imply a validated incumbent-holder SELL/HOLD recommendation, and not a claim that microcaps are safe.
6. No public chronological forecast unless underlying owner source is issued and legally available **before** event (PIT, first-known clock). The static preview seed is 2026-W41 and MUST say archival, not live W42. 
7. Accessible mobile 390/430 and DA/EN: group aria-label for source class; marks are decorative within group `aria-hidden`, native disclosure toggles accessible, reduced motion, no horizontal scrolling. Short factual hierarchy above; fine detail only after expansion.

## Source/data files and tests

| File | Authority/function |
|---|---|
| `premium-index.html`, `premium.css` | Tiny categorical escalator + **existing** disclosure facts, no layout overhaul |
| `premium.js` | Displays first-party validated stage, ETA, evidence and factual dropdown after translation; no signal creation |
| `premium-i18n.js` | Static DA/EN labels; dynamic source-data lines rendered after global language switch |
| `official-pullback-stage.mjs`, `official-pullback-eta.mjs` | Existing validated risk states and typed time readback |
| `official-pullback-investor-view.mjs` | New zero-secret descriptive adapter for 10 pieces of available/unavailable investor context |
| `official-feed-parity.mjs` | Existing future live adapter; exposes these values only when fresh and aligned official source/CN identity |
| `test-official-pullback-stage.mjs` / `test-official-pullback-eta.mjs` / `test-official-pullback-investor-view.mjs` / `test-official-feed-parity.mjs` | Negative cases for uncalibrated 1–10, source mismatch, stage, invalid ETA, sell separation, stale source, DA/EN, 2–3W/4–8W identities |
| `check-premium.mjs` / `verify-vite-bundle.mjs` | Static HTML/JS control and real production bundling, including pure modules |

**Actual official current W42 source was reviewed**: `CMP-20261012-3f1e99c2868e`, issued 2026-10-12T16:18:05Z: ELEVATED risk, LOW evidence quality, null onset start/end, source week 42, separate SELL UNAVAILABLE and Distribution UNKNOWN. Nothing on the site is allowed to translate this to "HIGH probability", a 24h crash prediction, BTC -10%, alt -30%, confirmed bear, or stablecoin SELL.

**Scientific blocker**: `04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json` explicitly `SUSPENDED_NO_ELIGIBILITY_CONTRACT`; `PERFORMANCE_SUMMARY.json` has **0 closed episodes** and NULL theoretical 10%-trim outcome data. These descriptive samples cannot train a live 1–10 probability or justify SELL/re-entry. Research lives in the same R4P mission and #1553; site only displays source-confirmed truth.

## Deploy/Work release steps

1. Fresh-read current main, design PR #1576 and Edge research PR #1573; inspect other active writers, source contracts, privacy restrictions and exact git SHAs. All CI applicable exact-head GREEN.
2. AppDeploy existing preview `cycle-navigator-vnext-preview-l1nbkq` **only after free-host quota permits**. Existing stable preview may still lack latest ETA/progression; do not claim deployed based on GitHub commits.
3. In the existing [PULLBACK_ETA_RELEASE_NOTE_2026-10-12.md](PULLBACK_ETA_RELEASE_NOTE_2026-10-12.md) AppDeploy file mapping, add `official-pullback-investor-view.mjs → src/official-pullback-investor-view.mjs`; preserve `official-pullback-stage.mjs` import and the two others. Leave the frozen W41 seed untouched. Require READY receipt.
4. Real iPhone 390×844 and 430×932 with source 5/5, all five stage labels, no overflow, both language modes, dynamic risk ETA translated, 5+7 tables, stage rollback to NORMAL/unavailable on stub fixtures, dropdown collapse/expand, keyboard/VoiceOver and no stale-as-LIVE banner.
5. Integrate the current official live feed separately under existing production compiler and full site NOW/PATH/WHY/PROOF inventory. Rollback and independent source acceptance required; *never merge entire design PR directly into main.* If live source cannot support 1–10, magnitude or duration, default is UNKNOWN while still showing official stage.
6. Keep public Score Era frozen claims untouched; independent performance evolution only from EDGE mission after mature prospective episodes. Until actual release, status **DESIGN_AND_CI_ONLY**.

## Owners

- Scientific cross-asset severity/onset/alt-basket and validity: existing #1553 / #1530; Horizon Edge PR #1573 R4P addendum and #1516.
- Portfolio liquidity/sell/re-entry and private wallet-specific overlay: existing #1071 / #1133; NO private data published to this site.
- Site code, DA/EN, iPhone/browser and release: existing #1578 / Draft PR #1576. No second cron, API runner, parallel trading engine, or public site.
