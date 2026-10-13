# Task 2 · Deep Research 01–04 · CFGI incremental-information intake v2

**Date:** 2026-10-13. **Authority:** RESEARCH_ONLY / SECONDARY_REPORT_CLAIMS / NO OUTCOME OR PIT ADMISSION. **Public control-plane base:** `4f55f4a499bbee1034aeb81da1598fb7da0c488b`. This intake complements, not replaces, [the preserved DR01–03 synthesis](2026-10-13__TASK2_DR01_DR03_PUBLIC_RESEARCH_INTAKE_v1.md) and its [30-study source-reported readiness register](2026-10-13__TASK2_DR01_DR03_PUBLIC_RESEARCH_INTAKE_v1.json). It is linked from the existing Task 2 R0–R7 handoff. No duplicate new engine, scheduler, source-of-truth or Active Test Registry.

## New user-supplied report and trace

- **DR04:** *CFGI Predictive Edge Laboratory*, 17-page PDF, 2026-10-13. Exact uploaded PDF SHA-256: `198fb059396338b02681addc34f6743a232648dff1cf765cfc7f88e6ee17ffb4`. Original PDF is a conversation attachment, **not present in this public GitHub**.
- Report-derived statements below are **secondary-source claims** until independently reproduced against actual authorized, immutable provider receipts. Restricted market values, individual user data and private research payloads must remain outside public PRs. Refer to source by **report ID and page**, not by asserting that a reported private GitHub revision is current.
- The report's dated repository commit checks do **not** certify currently admissible data or imply R2–R7 execution.

## What is newly learned (reported hypotheses, not implemented rules)

1. **Raw CFGI is not established as independent predictive alpha** (DR04 pp. 1–2, 16): score can describe simultaneous market regime; economic action edge not established. `CFGI LOW => BUY` and `CFGI HIGH => SELL` must not be inferred. Existing Task 2 R0/R1 remains binding.
2. **Price contamination and fair baseline (DR04 pp. 1, 6–7):** today's vendor engine reportedly weights Price and Impulse 30% each (60% jointly); other components 5% each. This **current** weight vector is NOT proof about the vendor's pre-upgrade 2025 engine. Test each non-price component's marginal OOS lift beyond same-clock price, momentum, volatility and volume; don't reward double-counted price information.
3. **Engine-vintage discontinuity (DR04 pp. 2, 14–15):** provider reported algorithm upgrade effective **2026-07-08**, plus API v2→v3/timestamp changes. The legacy 2025 CFGI slice and 2026 snapshots may not be pooled or model-fit jointly without explicit feature schema, source first-known, era stratification and comparability tests. Proposed categorical labels `LEGACY_PRE_2026-07-08` and `UPGRADED_POST_2026-07-08` are a **research contract proposal, not a production field added by this PR**.
4. **More discriminating signal candidates (DR04 pp. 5–7, 16):** recovery velocity, failed recovery, price/sentiment divergence, individual component dispersion, non-price residuals, multi-timeframe disagreement and conditional regimes. These remain candidates; H11 individual attribution highest research priority. `Score level` and broad `Greed => sell` are poor standalone claims.
5. **MAEVE selection vs behavior (DR04 pp. 3–4, 7–8, 13–14):** historical actions support studying fear→recovery behavior, but not profitable entry selection without matched `NONE` opportunities. Recovered `analisis_hora`/component entry snapshots are lookahead suspect. DCA economics must use parent positions, equal capital reserve/exposure, benchmark, costs and missed upside, not headline win rates.
6. **Small independent samples (DR04 pp. 3–4, 11–13):** CFGI event window comparisons and multi-timeframe samples have severe overlap/serial dependence; observation rows are not independent market families. Eligible `N`, embargo, horizon and OOS era must be explicitly frozen.
7. **Strict economic endpoint (DR04 pp. 8–10, 13–14):** `INFORMATION_EDGE != ACTION_EDGE`. No CFGI-driven live SELL/re-entry inference. M6/Pullback current eligible episode denominator is inadequate in the report. HOLD, matched capital and realistic execution remain mandatory.
8. **Buying data is premature (DR04 pp. 14–16):** keep `REUSE_EXISTING_BEFORE_ANY_BACKFILL`. Any future CFGI acquisition must follow first-known adjudication, matched NONE census and information-gain target selection and separate budget approval.

## Specific R0/R1 design upgrades (not yet implemented)

- **R0 source registry:** provider + vendor-engine vintage + native algorithm timeframe + actual observation/capture UTC + first-known UTC + API schema/version. A 4h/1d value sampled every 15 minutes remains a 4h/1d algorithm, not native 15m.
- **R1 negative cases:** pre-2026-07-08 state mislabeled current, synthetic mixing across engine eras; post-entry snapshot masquerading as entry-time; updated/revised provider data assigned to earlier first-known; same 4h state repeated as independent 15m trials; future-based residualization, threshold fitting or training on sealed holdout.
- **No-action denominator:** build eligible `NONE | ENTRY | DCA | EXIT` on common asset+timeframe+market-clock, including decisions NOT to buy. Separate matched prospective data from retrospective selection.
- **No independent conclusion from report only:** require one-to-one immutable provenance, effective-N by shock-family, test preregistration, time-ordered train/validation/test, purged overlapping windows and multiple-testing correction.

## Ten-arm fair comparison (DR04 p. 10)

| Arm | Eligible input | Interpretation |
| --- | --- | --- |
| A | Price returns | Minimum baseline |
| B | A + realized volatility | Stress baseline |
| C | Price, momentum, volume | **Mandatory strong mechanical comparator** |
| D | CFGI composite alone | Standalone sentiment test |
| E | C + composite | Composite marginal lift |
| F | C + individual components | Non-price/individual marginal lift |
| G | F + preregistered regime | Conditional interactions |
| H | Existing framework minus CFGI | Unmodified system comparator |
| I | Existing framework plus CFGI | Actual integration lift |
| J | C + residual sentiment orthogonalized on train-only data | **Best test of non-price incremental value** |

**All arms must share exact eligible clock, horizon, event family, vintage, outcome source and evaluation metric.** Transformations and residualization must fit on the training fold only; preserve failed arms and total variant count. Do not promote a winner from the sparse frozen event windows.

## DR04 E01–E12 experiment proposals

All 12 are **source-report-proposed only** and remain `TASK2_ADMISSION=false; EXECUTED=false` in this intake. Exact source-reported statuses and baseline details are in the adjacent [machine map](2026-10-13__TASK2_DR01_DR04_PUBLIC_RESEARCH_INTAKE_v2.json). At most, methods research and synthetic negative controls can proceed within R0/R1. Never classify these as actual approved or historical backtests.

| Packet | Purpose | Gate |
| --- | --- | --- |
| E01–E02 | composite and non-price marginal information against price controls | restricted-data + PIT, strong benchmark |
| E03–E04 | velocity, failed-recovery forward signal | restricted + small-N family OOS |
| E05 | duration of fear regime vs fresh fear | blocked broad opportunity denominator |
| E06 | observed multi-timeframe disagreement | discovery only; no native 15m confusion |
| E07–E08 | MAEVE selection and apparent 4h superiority | blocked matched NONE / sample confounding |
| E09 | CFGI-filtered DCA vs actual DCA/no-DCA | restricted; capital matched |
| E10 | CFGI+breadth warning vs breadth alone | discovery only |
| E11 | ETH/BTC residual sentiment rotation | prospective only |
| E12 | CFGI-enhanced exit/re-entry vs HOLD | blocked temporal/action admission |

## Ownership and stop rules

Existing owner/routing only: Task 2 R0/R1 [handoff](../../04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_FULL_STACK_NO_HINDSIGHT_AUDIT_WORK_HANDOFF_v1.md) (from repository root), #1596 Task 1.5 chronology, #1530 EDGE Governor, #1553 Compass risk-to-action, plus existing CFGI+MAEVE archived inventory and Research Lab. Do not re-open terminal experimental hypotheses, overwrite negative evidence, change production CFGI weights, create public private bindings, authorize data purchases or copy restricted values. DR05+ add another versioned intake and the same handoff pointer; never silently revise the source-specific original verdicts.

**This PR delivers only research intake and routing. No actual historical simulation, statistical skill score, trading policy, current sensor rule, task scheduler or economic advantage was created or demonstrated.**
