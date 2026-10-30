# RQS v0 · Rebound Quality Shadow · bounded research prototype

**Date:** 2026-10-30 · **Owner:** existing Compass Risk-to-Action #1553 · **Scientific gate:** #1596 · **Lineage/control:** #1827.

**Status: prototype under review, not an issued signal or calibrated investment score.** This extends the existing R4P pullback/re-entry work; it is not a new engine, automated job, source owner, alert or PR-merge mandate.

## Investor question

After an already-visible decline, distinguish a price rebound **consistent with short-covering / partial position reduction** from one with evidence of sustained spot demand, ETH-relative participation and breadth. Do not classify either as proven causality, an imminent bull trap, a BUY or SELL, or probability until pre-registered, point-in-time valid and independently evaluated.

The existing public Hourly owner includes completed BTC/ETH candles, BTC taker-buy quote share, BTC/ETH quote volumes, ETH/BTC spot and OKX Open Interest. This is sufficient for a **bounded technical diagnostic**, not yet an eligible 0–100 composite or profit claim.

## Exact v0 input and clocks

- Entry: scripts/research/rebound_quality_shadow.py
- Public data owner: 03_DAILY_CAPTURE_LOGS/hourly/YYYY/MM/YYYY-MM-DD.csv (existing owner only).
- **Corrected after source audit:** `timestamp_utc` is each 1h candle's OPEN; completed candle CLOSE is `timestamp_utc + 1 hour`. `source_window_end_utc` is the producer's **collection-run coverage endpoint**, often identical for multiple distinct candles. Never deduplicate/group candles on that field. Validate only that coverage end is not before the candle's completed close.
- Each required candle exactly 1h, 16 contiguous most-recent completed hours, no fill/interpolation, no conflicting duplicate, spot_status=PASS, maximum last-end age 3h relative to supplied UTC cutoff.
- **As-of replay:** both a candle's completed close and its collection-run coverage end must be <= the evaluation cutoff. Data captured through a later run are excluded from earlier replay, even though this does not independently prove legal first-known availability. Same-calendar-day files are not sufficient for 16h near midnight; provide both relevant daily files when needed.
- A working public Hourly file is **not first-known evidence**: retrieval/availability and freeze admission need separate independent proof. Accordingly first_known_verified=false, prospective_forecast_issued=false and score_0_100=null on every v0 output.
- This script does not import/read private restricted raw and does not publish source market values as repository artifacts.

## v0 research event definition, *not optimized or authorized*

- Prior 13h **close-only** maximum drawdown ≤ -1.5%, preceding the latest 3h run. This avoids uncertain intrabar high/low order.
- BTC last 3h close-to-close return ≥ +0.75%.
- These values are frozen as prototype research parameters before outcome evaluation. Neither is a registered trading threshold. All non-candidates remain in the denominator for later missed-event analysis.
- The output reports the original 3h event, not reconstructed 12h/72h forecasts. No prediction skill is asserted.

## Evidence families

| Family | v0 observations | Correct interpretation | Limitation |
| --- | --- | --- | --- |
| Spot/price | BTC 3h return, quote-volume-weighted taker-buy share, 3h quote-volume / preceding 12h median, ETH/BTC 3h return | Direction and contemporaneous participation diagnostics | BTC spot, ETH/BTC and taker flow share source lineage and count as **one** family, not three votes |
| Derivatives | BTC OI end/start over the identical 3h, only for PASS rows | Price up + OI down = **position reduction, side unidentified**; price up + OI up = **new positioning possible** | OI is not proof of shorts closing, buying causality, or market maker action |
| Breadth | UNAVAILABLE | A source-clock-compatible, membership-consistent independent owner would be required | Same-family Top100 snapshots and stale daily proxies are **not** a same-clock third vote |

As an integrity gate, **no numeric RQS score, confidence, bull-trap probability or portfolio permission is issued by v0**. It emits feature evidence and candidate/no-candidate classifications for research only. Do not infer independent validation from a script passing its own tests.

## Scientific evaluation (existing #1596 / R4P, prospective only after approved freeze)

1. Pre-register event family, 3h entry cutoff, follow-up windows +6h/+24h/+72h, and failure/success definitions (retest, trough, sustained reclaim, alt-breadth, net execution opportunity) **before outcomes**. Event timing must be legally first-known; late delivery gets no advance-warning credit.
2. Deduplicate overlapping candidate hours and correlated BTC/ETH/alt events by market-shock/episode cluster. Count all eligible non-candidates, missed rebounds, false traps and false alarms.
3. Compare matched-clock baselines: simple price persistence, BTC-only momentum, OI-only heuristic, always WAIT/HOLD, and a shuffled/permuted negative control. Use regime-matched held-out prospective clusters and report coverage, uncertainty and false alarm rate.
4. Partition tests by fall severity, BTC/ETH and cap tier, fee/spread/slippage scenario, recovery duration and intervention clock. Gross path quality is **not** net utility. Private portfolio/wallet execution analysis stays in private governance.
5. Verify incremental value from independently source-bound breadth, valid as-of ETH/BTC, OI **and actual spot participation** before any scoring weights. Do not tune thresholds against the 2026-10-30 selloff and claim out-of-sample skill.
6. Independently review code, clocks, metric definitions, gaps, test fixture provenance and counterexamples. Only then consider a separately governed shadow score with calibrated evidence quality, NOT model-owned trade permissions.
7. Promote nothing into Official Compass or Site without source lineage, prospective sample, scientific owner gate, independent review, exact-head CI, rollback, and public readback proof. #1553 retains risk/protection owner; #1596 and #1827 retain their science/lineage mandates.

## Local validation

Run from repository root:

~~~bash
python -m unittest discover -s tests/research -p 'test_rebound_quality_shadow.py' -v
python scripts/research/rebound_quality_shadow.py \
  --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv \
  --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv \
  --asof 2026-10-30T21:00:00Z
~~~

Initial seven tests were only reported in the original draft; the reviewer identified and corrected a real source-window vs candle-clock mapping defect and added two regression fixtures. Exact-head tests are rerun on each HEAD through the existing Daily Capture Architecture Gate; later additions also enforce full UTC missing-hour denominators, source-legal post-cutoff checks, and due-only outcome maturity. Initial seven fixture intentions were: candidate remains no-score/no-trade, rising/falling OI ambiguity, missing derivative status, cutoff exclusion, duplicate conflict, stale owner, gap denial. **GitHub CI, independent review, actual public-data replay, prospective calibration and promotion are not claimed by that local test result.**

This work intentionally introduces **zero** workflow files, API calls, new recurring tasks or immediate official decisions.

## v0.1 extension · bounded replay and episode sensitivity

Optional `--scan` evaluates only the past 168 completed hourly candle closes in the supplied public CSVs. It reports candidate timestamps, coverage, missing cutoffs and **6h/12h/24h overlap grouping sensitivity**. These are DESCRIPTIVE grouping alternatives, not trained or selected parameters. No persistent automated runner or independent validation is created.

Example: `python scripts/research/rebound_quality_shadow.py --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv --asof 2026-10-30T21:00:00Z --scan`

A separate public-source inspection of 45 rows on 29–30 October found 30 complete 16h cutoffs and 4 candidate cutoffs (29 Oct 16:00Z; 30 Oct 04:00Z, 05:00Z, 06:00Z). Grouping by 6h gaps yields 2 provisional clusters; 12h merges them into 1. Neither is a verified independent market event or a trading win. Clustering must be preregistered, not optimized after observing outcomes.

The census explicitly remains `first_known_verified=false`, `performance_backtest=false`, `directional_accuracy=null`, `after_cost_edge=null`, `official_action_permission=NONE`. Requires independent review and prospective admitted data under #1596.

## v0.2 source-bound due-only outcome preview (EX-POST, not prognostic)

Command: `python scripts/research/rebound_quality_shadow.py --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv --csv 03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv --asof 2026-10-30T21:00:00Z --event-end 2026-10-29T16:00:00Z`.

This computes only descriptive realized BTC **close-to-close** changes at +6h, +24h and +72h, gated independently on every intermediate completed hour. The consumer checks that no included collection-run coverage end exceeds the REVIEW cutoff, and refuses missing source rows. Maturity after a due time without valid inputs is `UNAVAILABLE`, not an interpolated return; when not yet due, `PENDING`. No registered prospective prediction or original event first-known is proven, therefore output always states `original_prospective_registration_verified=false`, `first_known_verified=false`, `prediction_or_skill_scored=false`, `trade_permission=NONE`.

### Frozen public-blob illustration (historical development only)

Two public daily CSV Git blob identities inspected on 2026-10-30: `2026-10-29.csv` blob `a7ab3bd312ef5ecc5a40ab0d3996540671afc59c`, `2026-10-30.csv` blob `baf0ffdbb103c025e7061b95712875551f666a10`. No legal first-known or prospective receipt asserted. Use these as illustrative past-data observation snapshots, **not 4 independent issued warnings**.

| Exploratory rebound candidate UTC | BTC close at event | Observed +6h BTC close return | Observed +24h BTC close return | +72h |
| --- | ---: | ---: | ---: | --- |
| 29 Oct 16:00 | 81777.74 | -3.356% | -5.082% | PENDING |
| 30 Oct 04:00 | 78235.15 | -0.684% | PENDING | PENDING |
| 30 Oct 05:00 | 78280.01 | -0.574% | PENDING | PENDING |
| 30 Oct 06:00 | 78554.01 | -1.492% | PENDING | PENDING |

These rows came from the same market shock and include overlapping 6h/24h outcome periods. No denominators, independence, causal comparison, false alarms, efficiency or net tradability can be inferred from these four observations alone. In particular, do not use them to select a post-hoc 6h/12h episode grouping or to claim a profitable trading system. Due-only maturation should be part of an existing governance-approved observer, **never an added scheduler by this PR**.
