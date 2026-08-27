# Copper/Gold slow-cycle audit and implementation

**Date:** 2026-08-27  
**Status:** `SHADOW_IMPLEMENTATION / NO_PORTFOLIO_AUTHORITY`  
**Branch:** `agent/task-20260826-copper-gold-slow-cycle`

## Executive verdict

The framework did not lack the Copper/Gold idea. It lacked a framework-owned, point-in-time safe, reproducible data owner. Historical TDBC/BT08 work already reconstructed the likely TechDev 2M Copper/Gold MACD/RSI method, but the old historical test is quarantined because bar-start timestamps leaked information from not-yet-settled 2M bars and exact futures/ticker/roll conventions remain unresolved.

The implementation therefore repairs lineage and settlement first. It does **not** promote Copper/Gold to a canonical sensor, exit rule or portfolio trigger.

## Four explicit answers before this patch

1. Reproducible historical Copper/Gold series? **Partial reconstruction only, not a framework-owned operational owner.**
2. Automatically updated? **No.**
3. Trend/MACD/RSI calculated? **Yes in historical research packages, but not through a durable current owner.**
4. Decision authority? **No.**

## TechDev reconstruction

Repository evidence supports the broad identity `Copper/Gold on 2M bars`, with MACD and RSI. The 12/26/9 MACD, RSI14, Jan-Feb anchor and exact ticker pair remain candidate specifications, not ratified primary-source facts. Historical claims of universal lead/lag or cycle-top timing are not accepted as decision rules.

## Claude audit, final disposition

- Build reproducible Copper/Gold owner: **ACCEPT, modified to World Bank period-average macro proxy and settled-only features.**
- Daily polling: **MODIFY.** Daily fetch is used for revision detection, while the information clock is monthly/settled-2M.
- Direct distribution/exit role: **REJECT.** Historical event evidence does not justify it.
- HY OAS as pre-top warning: **REJECT.** T-1 sign test falsifies the universal warning formulation.
- HY OAS as cheap credit context: **ACCEPT, passive shadow only.**
- NFCI: **REJECT under K16 containment.** NFCI already contains risk, credit and leverage information and would double-count dimensions already represented elsewhere.
- Other thresholds/weights: **NEEDS PROSPECTIVE TEST.** No retrospective optimization permitted.

## Source choice

Primary owner source: World Bank Commodity Markets Pink Sheet monthly data. Both Copper and Gold are sourced from the same official workbook and normalized to USD/kg before ratio calculation. This is explicitly a macro proxy, not a claim to reproduce TechDev's exact futures continuous-contract series.

## Historical testing boundary

The event-study implementation uses first knowable date after settled 2M bar end and includes Jan-Feb versus Feb-Mar anchor sensitivity plus a fixed +91-day placebo. It reports descriptive forward outcomes only and carries a small-N warning. No market-rule promotion can follow directly from this study.

## Credit negative learning

The revised Claude recommendation correctly identified credit as a missing information family but overstated its pre-top timing value. A simple pre-registered sign test across classic BTC tops shows HY OAS was not consistently widening into the tops. Therefore the `distribution warning` lane is killed. Passive credit logging remains eligible because it is cheap and distinct from VIX, curve and dollar, but it has no vote.

## Cadence

- World Bank source fetch: daily, deduplicated by payload SHA-256.
- Information updates: monthly.
- 2M features: only after complete two-month pair settlement.
- Master Monday: context review.
- Data Ping: excluded from tactical runtime by default.
- Cycle Navigator: optional slow macro context only.

## Kill criteria at birth

The prospective experiment includes source ambiguity, lookahead, anchor fragility, lack of incremental divergence, false-positive burden, threshold fishing, small-N and K16 containment kills.

## Authority

Everything in this patch is shadow/research only. Copper/Gold alone cannot produce REDUCE, EXIT, DEPLOY, rebuy permission, market-state promotion or portfolio action.
