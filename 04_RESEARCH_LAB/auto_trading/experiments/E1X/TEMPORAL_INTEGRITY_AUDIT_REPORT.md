# Temporal Integrity / Lookahead Leakage Kill Test v1 (E1X)

| | |
|---|---|
| Audited main SHA | `48555838d7292290802887f01aeaf70a45721d85` (2026-09-22T16:56:18Z, "ops: provider budget readback 35757276210") |
| Run date | 2026-09-22 |
| Experiment | `AT-E1X-0001`, extends `AT-E1-0001` (`scripts/experiments/strategy_factor_leakage_e1.py`); no parallel owner or engine |
| Posture | `EVIDENCE MACHINE / RESEARCH ONLY / NO EXECUTION LAYER` |
| Authority | research only; no canonical, threshold, weight, portfolio or budget effect; no historical artifact rewritten |
| Suite validity | `SUITE_VALID`: 14 of 14 detector and classification controls met their expectation before any production verdict was read |
| **Final state** | **A. TRUE LEAKS FOUND AND REPRODUCED.** Two research evidence paths carry mechanically reproduced lookahead. No active production path (live state, DATA PING assembly, Master Monday live run, CN publication, intraday snapshot, pullback ledger) carries one. |

---

## 1. Starting-rule checks

| Check | Result |
|---|---|
| Fresh main | cloned 2026-09-22; SHA above |
| Existing leakage owner | `scripts/experiments/strategy_factor_leakage_e1.py` + `E1_LEAKAGE_VALIDATION_RESULT_v1.json`. Its right/left truncation proof runs on **toy trailing mean/z-score on a 12-row synthetic fixture only**. Artifact re-verified: `--verify-artifact` PASS. |
| Other temporal owners | AT-EXP-004 persistence fix (merged `c180d3ca5`, 2026-09-14) covers write-order / downgrade invariance, not truncation of computations. T12 temporal coherence (Director context, unmerged branch) covers cross-owner age spread. WP02C forecast temporal parity (unmerged branch). A project-only D_RT detector suite (`claude/E1_sensor_integrity_detector_suite_v1.py`) was applied to `build_hourly_sequence.py` only and never persisted to main. |
| Codex queue | 21 `CODEX_READY` tasks in `LATEST_CODEX_READY_TASKS.json` (08:49Z); none concerns leakage, truncation, warm-up or vintages. |
| Open PRs | GitHub API and the PR web page are not reachable from this session. 15 PRs carry live `refs/pull/*/merge` refs (812, 867, 889, 955, 977, 1006, 1055, 1085, 1094, 1096, 1132, 1135, 1142, 1158, 1187). Their diffs were inspected; #955 (Phase-0 historical shadow simulation spec/report) is historical-simulation-adjacent but touches no computation tested here. None duplicates this work. Open issues: `UNKNOWN` (no API access). |
| Gap decision | Equivalent production-computation truncation testing does not exist. The smallest proven gap is: real production adapters, knowledge-time truncation, suffix minimisation, warm-up series, classification. Implemented as an extension of E1, not a new framework. |

## 2. What the harness does

`scripts/experiments/strategy_factor_leakage_e1_production.py`

1. Every input is a `Record(available_at, kind, key, payload)`. `available_at` is the **knowledge time**: completed 1h candle = open+1h; 4h candle = open+4h; monthly World Bank average = publication; ETF row = documented retrieval; capture = `captured_at_utc`; file vintage = commit time.
2. For each output the production code claims at time `t`, the real production function is rerun on the point-in-time view `{records with available_at <= t}`. Records a declared outcome label legitimately needs after `t` are value-poisoned instead of removed, and only decision fields are compared.
3. Every field is compared; exact changed fields and deltas are reported.
4. Every mismatch is minimised (exponential then binary search) to the smallest future suffix that changes the value; the first contaminating record's kind, key and lead time are reported.
5. Classification comes from the contaminating record, never by assumption: `VALUE` → TRUE_FUTURE_LEAKAGE; `REVISION`/`VINTAGE` → SOURCE_VINTAGE_RISK; `MEMBERSHIP` → EXPECTED_CROSS_SECTIONAL_DIFFERENCE only for a declared live-only owner. Irreproducible output on identical input → NONDETERMINISM for the whole case. Zero comparisons → `NOT_RUN`, never PASS.
6. Warm-up is separate: the target output is recomputed with growing history; drift is split into honest nulls (insufficient window, fail-closed) and wrong values.

**Most important design result:** truncating by *label* time is blind. The PDLT defect below passes a label-time truncation (control RT-A07-LABEL_TIME: PASS) and fails a knowledge-time truncation. Any detector that cuts on candle open, period end or row index cannot see publication-lag or unclosed-bar leakage.

### Detector controls (all must hold before production verdicts count)

| Control | Expected | Observed | Minimal suffix |
|---|---|---|---|
| C01 clean E1 trailing mean on real hourly BTC | PASS | PASS | - |
| C02 seeded `shift(-1)` routed through production `build_hourly_volatility` | TRUE_FUTURE_LEAKAGE | TRUE_FUTURE_LEAKAGE | 1 |
| C03 seeded full-sample z-score on production copper/gold ratio | TRUE_FUTURE_LEAKAGE | TRUE_FUTURE_LEAKAGE | 1 |
| C04 seeded centred rolling(5) on ETF totals | TRUE_FUTURE_LEAKAGE | TRUE_FUTURE_LEAKAGE | 2 |
| C05 seeded `bfill` over missing closes | TRUE_FUTURE_LEAKAGE | TRUE_FUTURE_LEAKAGE | 1 |
| C06a seeded EMA(100) right truncation | PASS (recursive ≠ leak) | PASS | - |
| C06b/c seeded EMA(100) warm-up, declared history 150 / 1000 | INSUFFICIENT_WARMUP / RECURSIVE_CONVERGENCE_DRIFT | same (converges at 600) | - |
| C07 unseeded noise | NONDETERMINISM | NONDETERMINISM | - |
| C08 late listing in cross-section (production `matched_return`) | PASS | PASS | - |
| C09a membership change, live-only owner | EXPECTED_CROSS_SECTIONAL_DIFFERENCE | same | 2 |
| C09b same difference, historical recomputation | TRUE_FUTURE_LEAKAGE | same | 2 |
| C10 injected later vintage of one month | SOURCE_VINTAGE_RISK | same | 9 |
| PDLT label-time truncation (blindness control) | PASS (blind) | PASS | - |

## 3. Coverage map (real production code, 7 independent owners)

| Case | Owner / path | Records | Comparisons | Result |
|---|---|---|---|---|
| RT-A01 | backtest_engine `w30_replay.build_hourly_volatility` | 1086 real hourly | 48 | PASS |
| RT-A02 | backtest_engine `build_daily_utc` | 1086 | 48 | PASS |
| RT-A03a | backtest_engine `build_etf_trailing`, claimed knowledge time | 1153 ETF sessions | 43 | PASS |
| RT-A03b | same, with the one documented Farside timing | 1154 | 3423 | **FAIL** (F04) |
| RT-A04 | truth-layer ETF pack `build_etf_flow_features.py` (pandas, end-to-end) | 1164 | 28 | PASS |
| RT-A05 | data_terminal `world_bank_copper_gold_owner` monthly + settled 2M | 800 months | 59 | PASS |
| RT-A06a | research `copper_gold_slow_cycle_event_study`, bar end as knowledge | 6587 | 40 | PASS |
| RT-A06b | same, publication as knowledge | 6587 | 40 | **FAIL** (F01) |
| RT-A07 | AT `pdlt_discovery.build_dataset` (production-shaped synthetic; real inputs restricted) | 1350 | 20 | **FAIL** (F02) |
| RT-A07 repair | same with completed-candle anchor | 1350 | 20 | PASS |
| RT-A08 | AT E2 `feature_row` via production hourly adapter | 240 | 48 | PASS |
| RT-A09 | AT E3 N5 `extract_rows + build_examples`, event-time anchor | 308 captures | 48 | **FAIL** (F03, LOW) |
| RT-A09 capture | same, capture-time anchor | 308 | 48 | PASS |
| RT-A10 | intraday execution `hourly_rows + asset_features` (feeds direction confidence) | 1086 | 55 | PASS |
| RT-A11 | pullback ledger loader, replay path | 137 obs | 36 | FAIL, latent only (F06) |
| — | pullback ledger live stored ranks vs point-in-time recomputation | 113 | 113 | PASS (0 mismatches) |
| RT-A12 | DATA PING `auto_market_state.btc_d` over 31 git vintages | 31 | 36 | FAIL, SOURCE_VINTAGE_RISK (F05) |
| RT-A13 | AT SPAR-v1 `detect_events` | 280 snapshots | 33 | PASS |
| RT-A14 | Master Monday preflight v3 selectors, replay path | 1341 | 21 | FAIL, latent only (F07) |
| WU-W01..W06 | copper/gold 2M + monthly, backtest vol/running high, ETF streak, E2 windows, CN ATR protocol | — | — | see §5 |

## 4. Confirmed findings

### E1X-F01 · TRUE_FUTURE_LEAKAGE · MEDIUM · copper/gold event study joins bars before publication

- **Path:** `scripts/research/copper_gold_slow_cycle_event_study.py` (`latest_settled_state`, `signal_events`).
- **Mechanism:** the study treats `bar_end_timestamp` (month end 23:59:59Z) as knowledge time and enters BTC at the end of the bar-end day. The monthly World Bank average is published later. The owner's own receipts show July 2026 data on 2026-08-04 and August 2026 data on 2026-09-02. Every published signal event enters on the bar-end day (e.g. FEB_MAR TURNING_NEGATIVE 2011-09 → entry 2011-09-30), so each one is 1–4+ days before its input existed.
- **Mechanical evidence:** RT-A06b fails on 16/16 signal events. Example: `SIG|JAN_FEB|TURNING_POSITIVE|2010-12` at 2011-01-01T00:00Z is present on full data and missing when the future is removed. The minimal suffix is the bar's own record, available one day later even under the most charitable lag (the minimum observed, 1 day + 1 s). The same code passes when bar end is assumed to be knowledge time (RT-A06a), so the defect is the knowledge assumption, not the arithmetic. All 24 peak-episode state joins pass under the observed lag range (1–4 days). The tightest is 2013-12-04 (FEB_MAR bar 2013-11), which has 4 days of slack and would change only if the true 2013-11 publication lag exceeded that. That lag is UNKNOWN.
- **Impact:** measured with the unchanged production `signal_events(shift_days=L)` on the exact published inputs. Coin Metrics `btc.csv` sha `06495ff8…` and the feature vintage `a008fd47d` reproduce the published `anchor_results` byte-identically at L=0.

| median | published (L=0) | L=2 (min. observed) | L=4 (max. observed) |
|---|---|---|---|
| FEB_MAR TURNING_NEGATIVE 60d | −11.32% | −12.89% | −14.27% |
| FEB_MAR TURNING_POSITIVE (control) 60d | **+23.61%** | +8.88% | **−9.65%** |
| FEB_MAR NEG−POS 60d separation | 34.9 pp | 21.8 pp | **4.6 pp** |
| JAN_FEB TURNING_NEGATIVE 60d / 120d | +29.14% / +33.97% | +19.50% / +24.29% | +18.06% / +20.19% |
| JAN_FEB TURNING_POSITIVE 60d | +112.56% | +116.42% | +92.26% |

  The FEB_MAR contrast between a turning-negative signal and its positive control mostly disappears once publication lag is respected. That is exactly what preregistered kill criterion K02 describes ("lookahead ... required to retain apparent edge"). n=4 per cell. The study is already labelled exploratory.
- **Contaminated:** `research/experiments/copper_gold_slow_cycle_shadow_v1/HISTORICAL_EVENT_STUDY_v2.json` → `anchor_results` (all signal-event summaries). Not contaminated: `objective_btc_peak_episodes`. Keep v2 as evidence and regenerate as v3 with a knowledge-time join. The live owner (`world_bank_copper_gold_owner.py`) is clean (RT-A05 PASS) and its live state is stamped by retrieval time.
- **Remediation:** not implemented. A historical publication date is `UNKNOWN` before 2026-07, so the fix needs an explicit lag policy. Choosing that number is a governance choice, and inventing it in code would fabricate history. Codex candidate `codex-research-copper-gold-event-study-knowledge-time-join-v1` requires the lag as an explicit input and fails closed without it. It passes the repo's own intake validator (`VALID`) and is NOT_PERSISTED.

### E1X-F02 · TRUE_FUTURE_LEAKAGE · MEDIUM · PDLT discovery anchors labels on an unclosed candle

- **Path:** `scripts/experiments/pdlt_discovery.py` (`locate`, `forward_stats`, `build_dataset`).
- **Mechanism:** `locate()` returns the last 4h candle whose **open** is ≤ the CFGI timestamp. `forward_stats()` then uses that candle's **close** (open+4h) as the decision-time `start`. The anchor is therefore always after the signal: 0–4h after it, exactly 4h when timestamps sit on 4h boundaries. Every `event72/event7d/event14d` label is measured from a future price and skips the first 0–4h of the path.
- **Why the CFGI timestamp is the knowledge time:** 308 live CFGI 4h rows in `03_DAILY_CAPTURE_LOGS/captures` sit at unaligned minutes (e.g. 21:19:14Z) and were first captured 72–879 s after their timestamp.
- **Mechanical evidence:** RT-A07 fails 20/20. The only changed fields are `72h.start / 7d.start / 14d.start`. The minimal suffix is 1 record, the candle containing the timestamp, with lead 13 246 s (unaligned) or 14 400 s (aligned). The completed-candle anchor passes (repair proven). A label-time truncation would have passed the defect.
- **Train/serve skew:** prospective `pdlt_maturation.py` anchors on the frozen live price and 1h candles strictly after the freeze, so discovery labels and matured outcomes answer different questions.
- **Contaminated:** every discovery label `build_dataset` has produced, plus the fixed-calendar holdout screen. No discovery report or frozen model is present on main (`PDLT_LIFECYCLE_FREEZE_2026-09-02`), and the real inputs are restricted-plane. Real-data magnitude: `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`, not claimed.
- **Remediation:** not implemented. PDLT is frozen, and reopening needs `INDEPENDENT_REVIEW_OF_DISCOVERY_REPAIR`, which this finding now feeds. Codex candidate `codex-research-pdlt-discovery-completed-candle-anchor-v1` (VALID, NOT_PERSISTED) carries an explicit escalation condition in case restricted evidence shows period-start timestamps.

### E1X-F03 · TRUE_FUTURE_LEAKAGE · LOW · AT-E3 N5 entry anchored before the row was knowable

- `factor_test_n5_independent.py` anchors features and entry price at the CFGI event timestamp, but each row was first captured 72–879 s later (RT-A09 event-time FAIL; capture-time anchor PASS).
- On a 24h horizon this is about 1% of the window. The trial was adjudicated `INDEPENDENT_NOT_SUPPORTED`, and a lookahead could only have pushed it toward support, so the conclusion stands. No action for the closed trial; anchor future factor tests at capture time.

### E1X-F04 · TRUE_FUTURE_LEAKAGE + SOURCE_VINTAGE_RISK · MEDIUM · ETF knowledge time claimed at session close

- `backtest_engine/w30_replay.build_etf_trailing` sets `feature_knowledge_available_at_utc = not_before_session_close_utc`. That is a lower bound, used as a point.
- In-repo evidence: for BTC 2026-07-16, the accepted packet at 03:41:48Z next day held 45.7 with IBIT not reported. The complete 79.1 was verified at 06:34:00Z.
- RT-A03b: at the claimed 20:00Z the row is not knowable for 7.7 h (TRUE_FUTURE_LEAKAGE against the claim). At 05:00Z the known value is the provisional one and differs from the pack (SOURCE_VINTAGE_RISK, lead 1.6 h). At 12:00Z: PASS.
- The 2026-07-26 history pack is a single retrospective vintage (1 commit per partition, no per-row publication times). Its README already forbids same-session attribution and starts labels at the next trading session, which is consistent with the evidence. The W30 claim is not.
- Only one session has publication evidence. All others are `UNKNOWN` and are not guessed.
- Route: framework owner decides the ETF knowledge-time policy (next-session rule, or first verified complete retrieval). Not a code-only fix.

### E1X-F05 · SOURCE_VINTAGE_RISK · LOW · BTC.D vintages rewrite verification time

- Every re-publication of `BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv` stamps every historical row with the run's `source_verified_timestamp`.
- A replay of `btc_d(now=t)` over a later vintage fails closed (`BTC_D_FRESHNESS_TIMESTAMP_INVALID`), while the point-in-time vintage returns a value (e.g. 59.2835% at 2026-08-24T06:36Z).
- Values show 0 revisions across 31 vintages (2026-08-23 → 2026-09-22). The live path reads the pinned commit.
- No action; replays must bind the vintage commit.

### E1X-S01 · SOURCE_VINTAGE_RISK · MEDIUM · hourly derived columns (previously known)

- Git-vintage probe over 352 file versions: 168 of 1086 hourly rows (15.5%) changed derived values after first persistence (`*_return_1h_pct`, `*_price_oi_state`, long/short). Last change 2026-09-13; none after the AT-EXP-004 remediation (2026-09-14).
- This confirms AT-EXP-004 independently and deduplicates to it. The quarantine of those columns for 2026-08-08..09-13 stands. Raw OHLCV is unaffected.

### E1X-D01 · outside the temporal taxonomy · MEDIUM · ETF history pack row integrity (incidental)

- 9 BTC and 2 ETH rows are one value short. `Total` is missing and the last fund column holds the total, so fund attribution is shifted. The pack's feature builder silently computes over NaN totals.
- 26 NYSE full-closure dates (16 BTC, 10 ETH; 2024-01-15..2025-06-19) are recorded as 0.0-flow sessions. As a result, "N-session" windows count non-sessions, and zeros reset streaks.
- Not leakage. Owner data fix required.

### Latent replay paths (no current caller, INFO)

- **F06 pullback ledger:** `load_recent_observations()` returns the last 180 files on disk. A historical replay over today's archive ranks against later observations (RT-A11 FAIL). The live writer is clean: 113/113 stored ranks reproduce exactly from prior observations.
- **F07 Master Monday preflight v3:** `--freeze-start/--freeze-end` filter only accepted DATA PING packets. `latest_capture`/`latest_hourly` always take the newest file (RT-A14 FAIL on replay). Both workflows run live at freeze time without those arguments. Optional small candidate: apply the window to both selectors or drop the arguments.

## 5. Warm-up / convergence

| Case | Production history | Converged from | Classification | Material effect |
|---|---|---|---|---|
| W01 copper/gold 2M MACD(12,26,9)/RSI14 | ≥612 months before first crypto-era bar | 600 months (<1 ppm) | RECURSIVE_CONVERGENCE_DRIFT | Production is converged. A reproduction with 48 months flips `regime_state` (3 of 14 targets); with 192 months MACD still drifts up to 5.7%. Relevant to any TDBC rebuild from a short history. |
| W02 copper/gold monthly RSI14 (MA/z-score exact) | 695 | 480 | RECURSIVE_CONVERGENCE_DRIFT | none |
| W03 backtest running high / drawdown | 167 rows (W30 fixture) | 336 | INSUFFICIENT_WARMUP (start-anchored) | At 2026-09-14T06:00Z the drawdown is −2.64% with W30 length vs −5.09% with ≥336 rows. Realized vol is exact at 24/72. Engineering fixture only; label it "since fixture start". |
| W04 backtest ETF streak / rolling 20 | 4 (W30 week) | 20 (nulls only) | NO_ISSUE | windows fail closed to null |
| W05 CN forward-range protocol Wilder ATR14 | 59 (protocol minimum 60 candles) | 120 | INSUFFICIENT_WARMUP | ATR differs by 1.9–6.4 USD (0.08–0.29%) at 60 candles, changing the whole-USD ATR on all 4 dates tested. DUMB_1.5 width is 3×ATR. Protocol-only: no executable owner on main. Pin the history length (≥250 candles gives 4e-9 drift). |
| W06 AT E2 12-bar windows | 12 | 12 | NO_ISSUE | exact |

## 6. Source-vintage audit

| Source | Observation time | Publication time | Vintage time | Retrieval time | Verdict |
|---|---|---|---|---|---|
| World Bank Pink Sheet (copper/gold) | month (period end) | recorded only for 2026-07/08 (`workbook_updated_on`) | per payload hash revision receipts (2; ADDED only) | `retrieved_at_utc` | live owner OK; research consumer F01 |
| Farside ETF history pack | session date | not recorded (README states it) | single retrospective vintage 2026-07-26 | pack build | F04 / D01 |
| Farside live settled ETF owner | session date | `session_final` + `total_parity` gates | per run | per run | live NO_ISSUE (finality gated) |
| CMC BTC.D | UTC date | — | 31 git vintages, no value revisions | verification stamp rewritten per run | F05 |
| Hourly sequence (Binance/OKX) | candle open | candle close | git; derived columns revised (AT-EXP-004) | fetch window | S01 (known, remediated forward) |
| FRED DGS2/DGS10/VIXCLS/DTWEXBGS | observation date | not modelled | append-only receipts | per run | live-only; no historical consumer found; LOW |
| NFCICREDIT (ALFRED) | week | `realtime_start = realtime_end = as-of` | pinned vintage | receipt | exemplary; NO_ISSUE |
| ETF absorption experiment | session date | `known_at = retrieved_at` | as-of join with conflict fail-closed | yes | NO_ISSUE |
| CFGI historical lab v3 | hour | as-of previous ≤1h, explicit `future_read_violations` | — | — | NO_ISSUE |

## 7. Dismissed suspects (static pass → reasoned or dynamic dismissal)

| Suspect | Why dismissed |
|---|---|
| `techdev_dominance_20260830/audit.py` `prices.shift(-1)` | forward return indexed by entry date, used only as outcome; explicit `NONCAUSAL_SP_CLASSIFICATION` guard |
| E2 `_evaluation_label_next_1h_pct` | guarded: rejected if present in the public envelope; features PASS (RT-A08) |
| E2 inclusive-open cutoff | affects only the last label row, never a feature |
| `pdlt_maturation.stats` future window | outcome by design; strictly after freeze |
| `factor_test_n5 nearest_future`, SPAR `outcome`, `pdlt forward_stats` window | declared outcome labels, excluded from decision fields and poisoned rather than removed |
| `auto_market_state.btc_d` `max(eligible)` | bounded by `source_timestamp <= now` and a verification check; replay issue is F05 only |
| `compass_outcomes.closest_target` | outcome matching within ±2h, outcome side |
| `build_weekly_calibration` min/max/mean | bounded to the ISO-week window, run after week close |
| `shadow_registry_weekly`, `native_ota_adaptive_gate` | no adaptive statistics computed |
| `top100_breadth_owner_collector`, `rich_breadth_checkpoint` | live-only (`backfill_materialized_as_daily_rows: false`); membership difference would be EXPECTED_CROSS_SECTIONAL_DIFFERENCE (C09a) |
| ETF pack pandas `rolling(min_periods=1)`, z-score(20, min 5), cumsum | RT-A04 PASS; cumsum is anchored at ETF inception (the true origin) |
| CN weekly builder | LLM-authored ranges frozen before the week; the ATR baseline has no code owner (W05) |

## 8. Historical contamination and required regeneration

| Artifact | Status | Action |
|---|---|---|
| `research/experiments/copper_gold_slow_cycle_shadow_v1/HISTORICAL_EVENT_STUDY_v2.json` `anchor_results` | CONTAMINATED (F01) | keep v2; regenerate v3 after the candidate merges; re-read K02 |
| PDLT discovery labels / any discovery report derived from `build_dataset` | CONTAMINATED (F02), magnitude private | regenerate only inside a reviewed reopen |
| `E3_TRIAL_N5_INDEPENDENT_RESULT.json` | minor lookahead ≤15 min; conclusion unaffected | none |
| Hourly derived columns 2026-08-08..09-13 | previously quarantined (AT-EXP-004) | none new |
| Anything consuming the ETF pack at session-close knowledge time | at risk (F04, D01) | owner policy + data fix |
| Live state, DATA PING assembly, Master Monday live, CN publication, pullback ledger, intraday snapshot | CLEAN | none |

## 9. Reproducible commands

```bash
git checkout 48555838d7292290802887f01aeaf70a45721d85   # plus the E1X branch
# external, hash-pinned inputs (public, not committed)
curl -o btc.csv https://raw.githubusercontent.com/coinmetrics/data/f1a36afb962731c387bb03982758ab0103063da5/csv/btc.csv
#   sha256 06495ff8e643432e6948b7b4686ce44fc106217287dabdc1b38351d9ddec46c3
git show a008fd47d:03_DAILY_CAPTURE_LOGS/slow_cycle/copper_gold/derived/settled_2m_features.csv > cg_features_a008.csv
curl -o kraken.json "https://api.kraken.com/0/public/OHLC?pair=XBTUSD&interval=1440"
#   run used sha256 3224af2876f3a230a06bea06d22cb1eebfa3be8b4cf3d59482878b667fc076b3 (live endpoint; W05 only)

python scripts/experiments/strategy_factor_leakage_e1_production.py \
  --coinmetrics-btc btc.csv --event-features cg_features_a008.csv --kraken-ohlc kraken.json \
  --output 04_RESEARCH_LAB/auto_trading/experiments/E1X/E1X_PRODUCTION_TEMPORAL_INTEGRITY_RESULT_v1.json \
  --findings-output 04_RESEARCH_LAB/auto_trading/experiments/E1X/E1X_TEMPORAL_INTEGRITY_FINDINGS_v1.jsonl
python -m unittest tests.experiments.test_strategy_factor_leakage_e1_production
python scripts/experiments/strategy_factor_leakage_e1.py --verify-artifact 04_RESEARCH_LAB/auto_trading/experiments/E1_LEAKAGE_VALIDATION_RESULT_v1.json
```

Without the optional inputs the event-study cases and W05 report `NOT_RUN`, never PASS. Git-vintage probes need full history (`--no-git-probes` to skip).

## 10. Test results

- New: `tests/experiments/test_strategy_factor_leakage_e1_production.py`, 14 tests (6 subtests), all pass, about 12 s; stable over 3 consecutive runs. Covers the known-clean case, a seeded future leak through a production function, seeded warm-up drift, nondeterminism, vintage/membership classification, and the PDLT, event-study and ETF findings.
- Existing owners re-run: E1, backtest_engine, copper/gold owner + event study, PDLT hardening, AT-EXP-004 persistence, historical replay guard: 69 passed, 211 subtests.
- Full harness run twice: right-truncation, warm-up, notes and non-random controls are byte-identical between runs.

## 11. Implementation / PR status

- Local branch `agent/task-20260922-temporal-integrity-kill-test-v1` (harness + tests + evidence + this report) and `agent/task-20260922-codex-intake-knowledge-time-anchors-v1` (two intake candidates). Both are delivered as git bundles and patches.
- **No PR opened.** The session proxy refused a credential for this repository (`git push --dry-run`: 403 "not in this session's authorized repository set"), and api.github.com returned 403. Nothing was merged. Production code was not changed: the governed route for research findings is Codex intake, and research may not self-declare `CODEX_READY`.

## 12. Coverage gaps (explicit)

- PDLT real inputs, the MAEVE ledger and the 851k-row hourly panel sit in `Donh91/secrets`: `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`.
- LLM-authored outputs (RAW forecasts, Master Monday prose, CN ranges, Director output) are not deterministic computations. Their temporal integrity lives in existing freeze/provenance gates (`forecast-source-temporal-provenance-gate`, prospective ledgers), which were not re-audited here.
- `Donh91/Eksperimenter-framework-` (execution plane) was not in scope of this clone.
- ETF publication time is known for one session only; FRED revision history was not measured (live-only consumer).
- Open issues and PR titles: not readable without API access.