# KOMPAS PRO · continuous decision-quality learning roadmap v0.1

**Owner mandate:** 2026-10-30. Improve KOMPAS as the user's investment decision cockpit, grounded in trusted evidence, measured predictive and economic utility, and honest missingness. **Additive research only**, not a second Compass engine, autonomous trading permission, or a new scheduled collector.

**One operating route:** existing Hourly Capture → Auto Market State/QA → Official Compass and risk owner → frozen research-only challenger → due outcomes → evidence ledger → reviewed human interpretation. Reuse #1553 Risk-to-Action, #1596 Task 2 PIT/edge, #1827 lineage/integrity, #1516 Forward Path, #1156 existing Supervisor and the existing Weekly Master Monday + CN. Any work must be deduplicated against their open PR/head before execution.

## New candidate research families, ordered by investor value

| Lane | Research question | Existing owner inputs | Outcome / falsifier | Promotion blocker |
| --- | --- | --- | --- | --- |
| RQS | Is a bounce supported by spot participation or mostly position reduction, and does it endure? | Hourly BTC/ETH spot taker quote, OI, ETH/BTC; independent breadth optional | +6h/+24h/+72h sustained reclaim, retest/bull trap, fees and false alarms vs naive price-only | No independent first-known timestamps, breadth join, or prospective baseline edge |
| Pullback lead time | Could risk state have escalated before a material drawdown without excessive false positives? | #1553 official risk class, #1596 original freeze vs actual, 26h Hourly | onset lead/lag, missed crash families, false HIGH alarms, first actionable pre-event time | Never use realized lows as pre-event features |
| Participation quality | Does ETH/BTC/breadth/spot-flow recovery survive 6–24h vs transient BTC squeeze? | public source-qualified ETHBTC, Top100 membership-hash, same-clock breadth if available | subsequent breadth persistence, ETH/BTC realized path, source family independence | No same-cohort/family quality = UNAVAILABLE |
| Supply/absorption | Is price resilient despite selling, or is taker-flow strength misleading? | spot flow, OI, funding only at valid clock, order-book/depth if immutable | 1h/4h/24h adverse excursion, retest, durable bid absorption | OI and book snapshots cannot prove trade side or capital motivation |
| Horizon coherence | Does 12h NOW direction disagree with real 1–3d/5–7d forecasts, and is disagreement actionable? | Official, Shadow v2, CN frozen weekly and strategic | matched-clock directional and utility outcomes vs persistence, HOLD and NO_EDGE | 12h nowcast must not be scored as a 12h forecast |
| Investor cost and protection | Does earlier WAIT/trim-review actually help a holder or incoming-cash investor after costs? | existing risk owner, fee/spread/slippage, admissible tier universe | net opportunity cost, missed rebound upside, exit/reentry regret | SELL unavailable remains unavailable; never mint trade permission |

## Operating rules and implementation sequencing

1. **No new collector yet.** Existing Hourly captures completed UTC candles on its current cadence, and includes taker volume / OI. Inspect its actual missingness and first-known status. Do not claim repeated rows in one collection-run coverage window are duplicated candles. `timestamp_utc` is candle OPEN; `source_window_end_utc` is collector WINDOW END, not a candle-specific end.
2. **Current draft PR #1850** supplies bounded 16h evidence-only diagnostics, a 168h exploratory candidate census and negative tests. CI is added to the **existing Daily Capture Architecture Gate**, not a new workflow. This is not production or a score. Existing routines must remain unaffected.
3. **Outcomes**: preregister candidate event and independent episode rules, followed by +6h/+24h/+72h snapshots with immutable first-known evidence. No observation can be issued retroactively. At a minimum measure coverage, event N, lead time, sensitivity to cohort definitions, false-positive and false-negative frequencies, incremental edge versus price/OI baselines, after-cost utility, confidence limits and source degradation.
4. **Automatic research follow-through, bounded:** when the existing scheduled owner/Supervisor next reviews #1553/#1596, have it check the draft/head and the same existing Hourly source once, then perform a *due-only* maturation review. No new hourly running model, Action cron, background Agent, budget increase or unlimited PR loop. If prospective source or experiment admission is not authorized or not READY, emit BLOCKED / UNKNOWN with exact cause. Do not silently replace stale signals.
5. **Future site/Chat presentation, if independently admitted:** display source-verified qualitative tags such as `RECOVERY_UNCONFIRMED`, `POSITION_REDUCTION_PATTERN`, `SPOT_DEMAND_SUPPORTED` only if the authoring source truly owns the evidence. Display source age, evidence quality, and how the interpretation could be falsified. Never claim that a tag is a validated trade signal or calibrated probability without the corresponding prospective proof.
6. **Scientific go/no-go**: internal synthesis or beautiful charts are not proof of value. Require robust out-of-sample incremental signal or investor utility over same-clock baselines plus independent code/lineage review, CI, rollback and exact main+site readback before a visible official or public change.

## Review ledger and failure-safe

Record per check (under existing owner): exact owner/source SHA, immutable original observation/first-known clock, event/candidate ID, source-family set, data degradation, preregistration ref, test results and independent review. Count an underlying market move as ONE episode, not BTC+ETH+hourly repetitions. `NO_EDGE` and `UNAVAILABLE` are valid outcomes.

**Next safe action:** complete exact-head #1850 CI, obtain independent review and scientific owner feedback, then audit the public Hourly dataset and whether the existing pipeline can produce legal forward-only shadow receipts. Keep the PR draft and main signals untouched until the evidence gates close.

**Important:** This document adds research proposals and a bounded handoff; it does NOT create, enable or schedule any automation, authorize API cost or claim any findings have been scientifically proven.
