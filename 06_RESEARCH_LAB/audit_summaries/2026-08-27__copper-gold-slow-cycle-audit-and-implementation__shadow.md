# Copper/Gold slow-cycle audit and implementation

**Date:** 2026-08-27  
**Status:** `SHADOW_IMPLEMENTATION / NO_PORTFOLIO_AUTHORITY`  
**Original branch:** `agent/task-20260826-copper-gold-slow-cycle`  
**Credit-source correction:** `agent/task-20260827-nfcicredit-k17`

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

## Claude audit, corrected final disposition

- Build reproducible Copper/Gold owner: **ACCEPT, modified to World Bank period-average macro proxy and settled-only features.**
- Daily polling: **MODIFY.** Daily fetch is used for revision detection, while the information clock is monthly/settled-2M.
- Direct distribution/exit role: **REJECT.** Historical event evidence does not justify it.
- HY OAS as pre-top warning: **REJECT.**
- HY OAS as durable historical credit owner: **REJECT after source-coverage recheck.** Public FRED redistribution no longer supports the historical crypto-top test window; no new collection is scheduled.
- NFCI composite: **REJECT under K16 containment.** NFCI combines risk, credit and leverage and would structurally overlap existing dimensions.
- `NFCICREDIT`: **ACCEPT TO RESEARCH CANDIDACY ONLY.** It isolates the credit subindex and therefore does not inherit the composite NFCI K16 rejection, but it receives no vote or authority.
- Historical `NFCICREDIT`: **ALFRED VINTAGES REQUIRED** because the series is revised.
- Numeric extraction through summarising/LLM layers: **REJECT under K17.** `NOT_PRESENT` is a valid answer; deterministic parsing and provenance are mandatory.
- Other thresholds/weights: **NEEDS PROSPECTIVE TEST.** No retrospective optimization permitted.

## Source choice

Primary Copper/Gold owner source: World Bank Commodity Markets Pink Sheet monthly data. Both Copper and Gold are sourced from the same official workbook and normalized to USD/kg before ratio calculation. This is explicitly a macro proxy, not a claim to reproduce TechDev's exact futures continuous-contract series.

Credit candidate: Chicago Fed `NFCICREDIT` through deterministic FRED live CSV and ALFRED point-in-time vintages for historical tests. The full NFCI composite is not substituted.

## Historical testing boundary

The Copper/Gold event-study uses first knowable date after settled 2M bar end and includes Jan-Feb versus Feb-Mar anchor sensitivity plus a fixed +91-day placebo. It reports descriptive forward outcomes only and carries a small-N warning. No market-rule promotion can follow directly from this study.

The `NFCICREDIT` T-1 test freezes BTC tops at 2013-11-30, 2017-12-17 and 2021-11-10 and evaluates only the T-90 ALFRED vintage for each event. The preregistered rule is: if the trailing-3y percentile is below the median at T-90 for at least two of three tops, kill the distribution-warning lane. Missing vintage coverage returns `NOT_TESTABLE_SOURCE_UNAVAILABLE`, never an inferred number.

## K17 negative learning

During the source audit a summarising fetch layer produced plausible historical NFCI-family numbers that independent deterministic reads could not reproduce. Those numbers are excluded. K17 generalises the lesson: numeric observations must come from deterministic source parsing, carry source identity/provenance, permit `NOT_PRESENT`, validate source coverage, and use sanity anchors only as parser checks, never as proof of provenance.

## Cadence

- World Bank source fetch: daily, deduplicated by payload SHA-256.
- Copper/Gold information updates: monthly; 2M features only after complete pair settlement.
- `NFCICREDIT` live context: weekly source observed by the daily slow-cycle job, deduplicated by source date/content.
- `NFCICREDIT` T-1: one frozen ALFRED run when credentials are available; result is not repeatedly rescored.
- HY OAS: no new scheduled collection.
- Master Monday: context review.
- Data Ping: excluded from tactical runtime by default.
- Cycle Navigator: optional slow macro context only.

## Kill criteria at birth

The prospective experiment includes source ambiguity, lookahead, anchor fragility, lack of incremental divergence, false-positive burden, threshold fishing, small-N, K16 containment and K17 deterministic-evidence failure.

## Authority

Everything in this patch is shadow/research only. Copper/Gold or `NFCICREDIT` alone cannot produce REDUCE, EXIT, DEPLOY, rebuy permission, market-state promotion or portfolio action.
