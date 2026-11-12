# Kompas Pro 2.0 | Public Swing Matrix Source and Release Audit

Date: 2026-11-11. Public product owner: Archive #1516. Reviewed as a source-bound, presentation-only feature.

**Decision: GO WITH RELEASE GATES.** One compact, always-visible Swing overview is within the existing Kompas product. This document contains only the public presentation contract, not unpublished research or private product specifications.

## 1. Public capitalization references

Approximate descriptive *circulating* market capitalization classes, not thresholds issued by the Official Compass source:

| Reference class | Approximate circulating cap |
| --- | --- |
| Large | USD 10 billion or more |
| Mid | USD 1 billion to below 10 billion |
| Small | USD 100 million to below 1 billion |
| Micro | Below USD 100 million |

These conventional analyst reference labels are not universal and must **not** overwrite the canonical source-owned capitalization_ladder or imply token eligibility. Circulating cap is contemporary price times circulating supply. Unknown circulating supply, token/pool identity or source-time price means market cap is **unverified**; FDV, total supply, pool liquidity and realizable execution are different quantities. References: [CoinMarketCap market capitalization](https://coinmarketcap.com/academy/glossary/market-capitalization-market-cap-mcap), [CoinGecko explanation](https://www.coingecko.com/learn/what-is-market-cap-in-crypto) and [Binance Academy](https://www.binance.com/en/academy/articles/crypto-market-capitalization-explained).

## 2. Canonical public site and displayed information

The official production homepage is the existing canonical unified root, not an independent page or a competing forecasting service. A single Swing Kompas should be visible on the existing Kompas Pro surface without requiring the user to open the optional details panel.

- **Three source-issued market-wide directional windows:** 1–3 days, 5–7 days and 2–3 weeks. Each is shown strictly according to the currently eligible original source.
- **Four source-issued capitalization NOW statuses:** Large, Mid, Small and Micro. These are present-time states, not forward class-specific predictions.
- **Twelve class-by-horizon future cells:** all explicitly NOT_ISSUED until the canonical source actually supplies independently issued group forecasts. Never create forecasts or BUY/SELL actions by multiplying the three overall windows by the four current class states.
- MEMES stays a distinct source category, never silently substituted for the Micro group.
- Existing detailed tables can remain optional. No new backend, scanner, writer, scheduler or trading authority is introduced.

The site must use the original PUBLIC_COMPASS_PROJECTION_v1 source, the source-owned current data_status, matching source/compass identity, unexpired validity, an action echo and exactly one known status per group. Stale, missing, duplicated, contradictory or unrecognized input shows **UNAVAILABLE** with no inferred buy/sell signal, model confidence, position, ETA or price prediction.

## 3. Release and regression gates

1. On the **canonical unified-root output**, assert one Swing overview exists outside the optional cn-pro-more disclosure and is actually connected to the root runtime's source reader. A working standalone vnext preview is insufficient.
2. Fail closed for stale expiry, wrong source identity, missing tiers, duplicate tier keys, MEMES-as-Micro and any attempted class-specific forecast synthesis.
3. Verify original SITE build allowlist, immutable PATH/CSS root contracts, existing Graph B, original official action and rollback without duplicate roots or modules.
4. Run exact-head native site validation and real-browser 390/430 px tests for visibility, accessibility, text legibility and absence of overflow. Green unrelated CI does not replace those steps.
5. Obtain independent exact-head technical/security review and **public/private boundary** review; verify native branch rules, applicable HIGH_IMPACT gates and source/Vault recovery and custody separation before qualified merge.
6. After any qualified release, verify main blobs, the actual published GitHub Pages artifact and natural browser render. A merged PR alone does not prove publication.

## 4. Research boundary

Any non-public strategy designs, tactical capitalization experiments, private issue references, internal cohorts, filters, research arms or experimental methodology belong exclusively to their existing restricted owners. **None are reproduced, endorsed or exported in this public report or site UI.** The public presentation does not claim class-specific forecast precision or trading edge.

The 12 unavailable cells may be condensed later through a separate product review if they impair readability, but that does not license creation of missing predictions. Prospective research cannot retroactively turn today's preliminary display into a validated signal.

## 5. Product conclusion

A compact three-horizon overview plus four capital-group current statuses is supported by the existing public source contract. Twelve independent per-class forward signals **are not issued**. Release status remains **HOLD** until native exact-head CI, independent review, public/private boundary audit and original source/custody rules pass.

`PUBLIC_SITE_RELEASE_GATED` · `OFFICIAL_SEGMENT_FORECASTS_NOT_ISSUED` · `NO_PRIVATE_RESEARCH_EXPORT`
