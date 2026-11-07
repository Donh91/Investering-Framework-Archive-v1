# Kompas PRO, Precision Edition, visual finish specification

**Date:** 2026-11-07  
**Owner priority:** The original Monday-issued, source-frozen seven-day BTC forecast is P0. This document is *presentation only*.
**Delivery boundary:** GitHub repository and the existing GitHub Pages site ONLY. No AppDeploy or outside hosting.

## Reference and present acceptance stage

- Monday and Wednesday preview previously accepted as **concept direction**, not simulated forecasts.
- New Precision Edition Monday/Wednesday PNGs in the owner conversation were rendered from working SVG/HTML code. They are not yet exact screenshots of the original TradingView runtime. No claim of 1:1 visual parity.
- This branch implements the following restricted native-source QA tokens and an Original/Precision selector **only at** `/kompas-pro-test/` and `/kompas-pro-test/graf.html`.
- **Current state:** visual review candidate only. Do not merge/promote to canonical production styling without owner visual acceptance of the actual GitHub-native QA.

## Exact native-source tokens, QA opt-in only

| Layer | Existing canonical | Precision QA |
| --- | --- | --- |
| Forecast close path | #5f96ff; native TradingView Dash, width 2 | #86bbff; **same** native TradingView Dash, width 2 |
| Forecast markers | hidden | exactly original seven knots, native markers radius 2 |
| Green observed path | #27c59a; width 4 | **same** color, width 3, markers radius 2 |
| Daily envelope | rgba(95,150,255,.09) | rgba(95,150,255,.065) |
| Vertical grid | rgba(147,166,190,.055) | rgba(147,166,190,.035) |
| Horizontal grid | rgba(147,166,190,.09) | rgba(147,166,190,.065) |
| Axis text | #91a2b9 | #a4b8d3 |

The controlled CSS legend uses #86bbff to match the exact native QA forecast stroke.

This is an **optional renderer input**, not a second renderer or new market data contract:
`data-kompas-precision-qa` on the existing approved Graph B chart-area. When absent, all old values and original source behavior remain in effect.

## Functional invariant and controls

1. The seven original source-owned UTC daily closing-price coordinates must be byte-identical between Monday and Wednesday. No spline, interpolation, forward points, backfill, fake day ranges, price projection or inferred close.
2. The 7 per-day lower and upper bounds are the same source-owned points in both modes. The optional tint is not a confidence interval or probability unless source-calibrated.
3. Verified green observations may arrive late. The last factual timestamp is always shown; a delayed green series must not block the original Monday freeze.
4. The actual TradingView graph must continue to reject missing 7/7, wrong forecast quote, invalid provenance and future samples. No mixing USD and USDT.
5. Existing 7/14/21 display controls and Graph History stay source-bound. Day 8–21 must never gain invented blue prices.
6. Compare `Precision Edition` and `Nuværende original` on the same isolated GitHub QA page. The comparison changes *presentation only*, keeping the same fixture.
7. No synthetic QA input may enter canonical `/data/latest.json`, production freeze, scoring or trading.

## Release gates

- GitHub exact-head CI; browser renders at 390, 430 and desktop; inspect responsive alignment, price-axis labels and source cutoff.
- Source readback: both toggles have identical original forecast price/times/low-high, same actual timestamps, same week/issue and source metadata.
- Positive tests: seven issued source points and Monday->Wednesday unchanged; separate accurate as-of actual line; graph history link.
- Negative tests: no original forecast, cross-quote, malformed day order, missing source, actual gaps, future observations.
- Owner visual confirmation of GitHub-native screen, **separate from** this SVG concept screenshot.
- Only after positive owner acceptance and binding CI: qualified merge, deployed main SHA, actual Pages/CDN parity. Rollback remains original token path by removing QA flag.

**Do not let this design task delay Monday 2026-11-09 genuine W46 source issuance.**
