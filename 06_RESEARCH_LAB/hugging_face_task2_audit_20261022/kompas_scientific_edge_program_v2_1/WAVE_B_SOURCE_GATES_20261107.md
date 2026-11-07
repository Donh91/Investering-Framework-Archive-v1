# Task2 Wave B · Two independent scientific gates, no new forecast authority

**2026-11-07 · Original science owner:** [Task2 #1596](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596). **Original risk/warning owner:** [#1553](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1553). **Original weekly product owner:** [#1516](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1516). **Status:** RESEARCH_CODE_WITH_SYNTHETIC_TESTS, NOT ORIGINAL_EPISODE_RESULTS, NOT PROVEN EDGE.

## Already established source facts, not new findings

- [PR #2002](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/2002), merge e06762ed4232f8770d69b0ab3172ad0b235d90b8: the W44 hourly source has 168 canonical candle opens and 55 later collector batch endings, not missing market bars. The original post-issue result uses 162 eligible completed-hour endpoints. Batch-window end is **not** individual candle close or first-known.
- The W44 original CN BTC/ETH joint containment was 2/2, independent B1 0/2; B1 had narrower, better-overlapping descriptive intervals. W44 native forecast is USD-labelled against Binance USDT observed tape, so its apparent scores cannot establish matched-quote forecast superiority.
- [Historical pullback Round2](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/06_RESEARCH_LAB/historical_altseason_pullback_v1/ROUND2_TERMINAL_RESEARCH_DECISION.md): 46 pullbacks and 45 matched controls in the frozen historical design, 0 actionable LEADS across 42 tested universes and 0/11 tested reload policies beating HOLD. Keep those negative outcomes. Its historical tape does not establish a delivered 2026 original Kompas warning.

## Gate A · Risk level 3/5 and missing earlier alerts (L03, #1553)

Test the complete original hourly pre-event decision slots against **independently preselected** pullback and matched no-crash control anchors. The audit refuses to turn 3/5 into high-severity 4/5+, refuses to drop slots where no alert was issued, and separates legal source-first-known, actual issue and actually observed user delivery. A 4/5 after the event, an undocumented issue, an undelivered warning or a post-issue data vintage cannot receive early-warning credit. Controls with delivered 4/5+ must count as false alarms. Adjacent hours and BTC/ETH exposure within one shock are not independent wins.

**Current scientific state:** actual 2026 full original risk slot series, independently verified provider-availability clocks and authenticated delivery receipts are not bundled into this code change. Therefore there is **NO empirical lead/lag, recall, false-alarm rate or ex-ante action-value claim** from the new tests. A model cannot infer a true alert from a GitHub workflow green check.

**Eligible next input:** existing #1553 + #1827 original hash-bound issued decision/time series with all no-warning slots and separate episode/non-event anchors. External validation must certify actual Git blobs, provider availability, event selection, user delivery and independence before calling the pure scorer.

## Gate B · Weekly frozen forecasts versus cheap baselines (L02/L07, #1596)

Same original week, same target hours and same quote/instrument for original CN, existing preissued B1, and future separately frozen price persistence/momentum/volatility if actually available. Each original/candidate needs a pre-target issue, source-first-known and Git object; each comparison also needs a preissue anchor and a matured, source-identified contiguous outcome. Require original and observed quote parity; **USD vs USDT blocks numerical comparison**, no silent conversion. Report joint low/high containment, interval width relative to genuine preissue anchor, total extrema overshoot and Jaccard overlap separately. Neither Jaccard nor this two-tail diagnostic is a proper probabilistic interval score for joint weekly extrema.

**Monday issuance boundary:** A valid original weekly forecast may freeze after Monday 00:00 UTC, as W44 did at 06:57:49Z. The scorer therefore requires contiguous outcome candle closes starting at the first hourly close strictly after the actual issue, not 168 fabricated post-issue hours. For a Monday 06:57:49Z issue, 07:00Z through next Monday 00:00Z is exactly 162 eligible closed-hour outcomes. All earlier hours are excluded. This is a synthetic fixture demonstrating the timing gate, not a live W46 issuance.

**No W46 values issued in this PR.** No retrospective baseline fitting on W44; no winner or model weight changes. Any currently unavailable W46 issued forecast, real 168-hour prior-source continuity, quote parity, first-known, frozen target or GitHub Pages consumption remains **UNVERIFIED/NOT_MATURED**. Full W46 issuer/readback belongs to existing #1516/#1593, after natural Monday 2026-11-09 events.

## Engineering and actual test limits

- Pure deterministic module: scripts/research/task2_wave_b_scientific_gates_v1.py.
- 13 adversarial synthetic unit tests: tests/research/test_task2_wave_b_scientific_gates_v1.py.
- Executes via the existing original Task2 PR-only Data Architecture and Framework Learning tests loaded from tests/research/test_task2_archive_first_edge_matrix_v1.py. **No new workflow, schedule, GitHub identity, paid API, market state, public forecast, original source overwrite, portfolio or trading permission.**
- A syntactically valid 40-character Git SHA in a caller-supplied packet is **not itself authenticated ancestry**. Original domain owner must independently verify the actual exact blob, first-known and delivery receipts before deriving any historical or prospective conclusion. The pure gate enforces shape, chronology, abstention and denominators, not those external attestations.
- Design scope intentionally small: one eligible source-/quote-qualified actual new cohort unlocks next paired score; one actual original risk/control ledger unlocks original source-grounded warning atlas; otherwise record a precise block and stop, not fabricate results.

**Independent science admission:** STILL_BLOCKED, insufficient source-qualified independent matured events. **Operational code admission:** conditional on actual PR-head CI, reviews, owner qualified merge and main blob readback. **Scheduled S1 merge:** NOT CLAIMED.
