# Kompas Pro · 83-day rebound quality development audit v1

**Research evidence date:** 2026-10-31 (Europe/Copenhagen). **Status:** `EX_POST_DEVELOPMENT_ONLY`, NOT original-issued PIT, not a shadow registered prospective prediction, not a formal backtest of investor returns, not an eligible signal. **Owner:** existing #1553, #1596; source/clock #1827; experimental code PR #1850.

## Research question

After a BTC selloff and >=0.75% close-to-close 3h relief move, does contemporaneous spot-buy quote share, quote volume, derivatives OI or market regime distinguish a recoverable rebound from another drawdown? This is a hypothesis to FALSIFY, not a new trading permission.

## Source provenance: 17 exact public Git blobs

Read-only source files from `Donh91/Investering-Framework-Archive-v1`. **Use ONLY primitive BTC/ETH spot OHLC, taker quote volumes, OI and status, not the weekly file's derived forward returns or feature columns.** The original as-issued retrieval time is NOT pinned by these Git blobs. `source_window_end_utc` in weekly files is producer run COVERAGE, not individual candle close or legal original first-known time.

| Input | Git blob SHA1 | Rows |
| --- | --- | ---: |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W32/WEEKLY_HOURLY_ENRICHED.csv` | `1d08cd273f48015996d993797f5730fccf91fba4` | 40 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W33/WEEKLY_HOURLY_ENRICHED.csv` | `90189381443c5bce836cd2190dba0ab28b75d0ff` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W34/WEEKLY_HOURLY_ENRICHED.csv` | `ffbcacaa0223d08db27b5d9fd9cfe492780e692c` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W35/WEEKLY_HOURLY_ENRICHED.csv` | `09f0f19276e8c88e30afd6ed3b31619bf2aa2b01` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W36/WEEKLY_HOURLY_ENRICHED.csv` | `34dc8125aef0f85252ffd0a37a73c0e1f7aa4eac` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W37/WEEKLY_HOURLY_ENRICHED.csv` | `1b84d81e399541b41624ba016b0f37b76179bdee` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W38/WEEKLY_HOURLY_ENRICHED.csv` | `8b82bd412c4e252e8786d1ce0df27471c9e901bb` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W39/WEEKLY_HOURLY_ENRICHED.csv` | `02cc2db27d0ebc070853e1535088d1b9e2c656d2` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W40/WEEKLY_HOURLY_ENRICHED.csv` | `33e0d1366c8de7e69ea1bd9655a96764aeabc70f` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W41/WEEKLY_HOURLY_ENRICHED.csv` | `56c68795ad9564cebd0c1d17e32c71522bbd4e99` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W42/WEEKLY_HOURLY_ENRICHED.csv` | `78a3706fe1b1a39d0a4974ea1539dc948362b908` | 168 |
| `03_DAILY_CAPTURE_LOGS/weekly/2026/W43/WEEKLY_HOURLY_ENRICHED.csv` | `256e63e6b18b9839c3d7694c137f25eecad0150c` | 168 |
| `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-26.csv` | `9866e34b490d1684514ed31eddf35000db131ec4` | 24 |
| `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-27.csv` | `8cb948f024418d6be3497968f11eedc62e0f0a1d` | 24 |
| `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-28.csv` | `fb34cd6299b9e1a97b7a06e70f7070cf38b6eb85` | 24 |
| `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-29.csv` | `a7ab3bd312ef5ecc5a40ab0d3996540671afc59c` | 24 |
| `03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv` | `baf0ffdbb103c025e7061b95712875551f666a10` | 21 |

**Manifest scope:** 2,005 actual distinct contiguous UTC close hours from 2026-08-08 09:00Z to 2026-10-30 21:00Z; no duplicate UTC opens, UTC misalignment or time-gaps in this snapshot. 15h warmup excluded from the 16-hour diagnostic, leaving 1,990 *EX-POST FEATURE-COMPUTABLE* cutoffs. They are NOT 1,990 legally first-known issued signals. **STRICT as-of producer-coverage checks reject almost all weekly reaggregated rows**, so the research must never present these as PIT-admissible inputs.

## Read-only independent exploratory arithmetic

At each eligible 16-completed-hour window, prior close-only drawdown is the maximum peak-to-trough decline across the **first 13 closes**, using a running peak. The return of the **latest 3 completed hours** is `(BTC_close_at_window_end / BTC_close_3_hours_earlier - 1)*100`.

- Fixed research-only candidate: earlier drawdown <= -1.5% and latest 3h close return >= +0.75% (same provisional thresholds as PR #1850). Thresholds were not tuned during this specific evaluation.
- Development-only: calculate full-series historical candidate features from stored **later-aggregated** data, deliberately **without pretending that the historical weekly file passed the as-issued/first-known gate**.
- **Future price outcomes:** compare BTC closes at +6h/+24h/+72h ONLY when all intermediate source closes exist and PASS. PENDING otherwise. This is an ex-post realized path analysis; do not read future-derived weekly feature columns at decision time.
- Group adjacent raw candidate hours into illustrative 6h, 12h and 24h cooldown clusters, using first candidate in 12h cluster for a *descriptive* overlap reduction. No prespecified statistical independence or verified event definition.
- Exploratory control: all windows with the same initial <=-1.5% drawdown, regardless of last 3h positive return, NOT matched independent controls. Its overlapping-hour means cannot be compared as alpha or economic edge.

## Results, descriptive only

| Quantity | Value |
| --- | ---: |
| Source hours / 16h ex-post feature windows | 2,005 / 1,990 |
| Raw fixed-rule candidate hourly cutoffs | 34 |
| Illustrative 6h / 12h / 24h clusters | 18 / 14 / 14 |
| 12h first-event sample | 14 (not independently PIT-issued) |
| Raw candidate observed +6h return | 20 positive / 34 mature, mean -0.135% |
| Raw candidate observed +24h return | 16 positive / 31 mature, mean -0.180% |
| Raw candidate observed +72h return | 19 positive / 29 mature, mean +0.682% |
| First of 12h clusters, +24h return | 8 positive / 14 mature, mean -0.030% |
| Initial selloff-only control windows | 390 (strongly overlapping; NOT matched) |

### Regime variation, not a proof of predictability

| Month | 16h ex-post windows | Raw candidate hours | Raw candidate +24h mean | 12h-group first events |
| --- | ---: | ---: | ---: | ---: |
| Aug 2026 | 552 | 9 | +0.332% (9 mature) | 3 |
| Sep 2026 | 720 | 7 | -0.162% (7 mature) | 5 |
| Oct 2026 | 718 | 18 | -0.495% (15 mature) | 6 |

This historical sample is small and clustered, and the last October events have immature 24h/72h outcomes. Do NOT claim October is a held-out test: RQS research and selection already saw October market behavior. No confidence interval or calibration probability is justified from 14 partially dependent, retrospectively selected episodes.

### Challenging our intuition

- Falling OI occurred in **28/34** raw recovery cutoffs, rising OI in **6/34**. Observed +24h was positive in 14/26 for falling OI and 2/5 for rising OI. This does not establish short-covering causality, healthy recovery or a reliable predictor.
- BTC three-hour taker-buy quote share >50% occurred in **28/34** raw recovery cutoffs. Its observed +24h was positive in 13/27; for <=50%, 3/4. **This counters any simplistic claim that higher taker-buy share guarantees durable rebound**. The tiny, selected comparison is underpowered and not a validated contrarian edge.
- The first 12h-cluster candidate has +24h positive rate 8/14. Gross price continuation around half the sample is not a reliable trading rule or a calibrated likelihood.
- Source provenance and clock availability are the chief P0 bottleneck, NOT the number of visually compelling features.

## Independent Grok Bridge #98 adjudication, scientific HOLD

Grok advisor source report: `Donh91/Investering-AI-Audit-Bridge` PR [#98](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/98), signed original Archive PR head `48a4ba028a08aa3dfa8edf339027461af7fc3270` and report file `reports/grok/automated/2026/10/2026-10-30T234727Z_GROK_INVESTERING-FRAMEWORK-ARCHIVE-V1_PR1850_48a4ba02_0a6e72da.md`. Grok independently reproduced all principal 83-day historical aggregates using the 17 frozen blobs, not the moving main. Findings are ADVISORY, not formal GitHub approval or statistical validation.

**Source revision, important:** The original manifest above intentionally pins the immutable 2026-10-30 file blob `baf0ffdbb103c025e7061b95712875551f666a10`, containing **21 hourly rows on this PR branch**. The current main path at the new check is blob `ef4c2992085c760683b11259d8329bcd5b598b69`, now **23 hourly rows**. This is a later, different data revision, and must not be silently substituted into the 2,005-candle dataset, the 34-candidate denominator or Grok's baseline. The report is tied to the original commit/blob context, not current main. This resolves the alleged inconsistent provenance by explicitly distinguishing the two versions; it does NOT prove the original first-known clock.

**Independent baseline failure (Grok F6):** Across 31 mature candidate raw hours, 16/31 (51.6%) had positive BTC +24h close returns, often rounded as 52%. The full ex-post eligible 16h-window baseline was approximately **51.6% positive** (Grok independent local computation); its mean +24h return approximately **+0.24%**, versus **-0.18%** on candidate windows. A generic last-3h >=0.75% move without earlier drawdown restriction was 74/156 (47%) positive +24h. The 12h-group first-candidate positive result 8/14 is consistent with chance in Grok's exploratory 20,000-draw permutation (p approximately 0.44), but source/episode dependence means this is **not** a formal p-value. **Verdict: NO DEMONSTRATED EDGE.** Neither predictive calibration nor after-cost improvement is established.

**Source-clock obstacle (Grok F7):** In 1,318 of 2,005 rows, the archival collector coverage end was more than one hour after the individual candle close. This is **consistent with late reaggregation**, not proof that the upstream market provider was late. Most rows cannot establish a legal as-issued hourly signal based only on these files. Any historical operational model with original publication-time assumptions would be invalid. There is no permitted retrospective back-credit.

**Code correction (Grok F1):** Source branch now adds UTC-hour-alignment validation both for `event_end_utc` and for every `timestamp_utc` inside `due_only_outcome_preview` (previously only `assess` enforced this), with two adversarial negative tests. F4 benign duplicate re-collection with revised coverage timestamp remains a distinct P3 usability issue; future remediation should preserve earliest eligible provenance and distinguish market-payload conflicts without tolerating real data revisions.

**Formal verdict:** `SCIENTIFIC_HOLD` for 83-day outcome learning; `INSUFFICIENT_SOURCE_PROOF` for prospective admission and any official Kompas risk/action. Retrospective development descriptions may continue on immutable source files only, if explicitly labeled. Do not publish or train live probabilities from this backtest.

## Five bounded decision-relevant research lanes, implemented as ex-post diagnostics

A new pure read-only module `scripts/research/rqs_five_lanes_expost.py` and deterministic tests `tests/research/test_rqs_five_lanes_expost.py` expand the research without an extra collector, scheduler or classification owner. They expose only aggregate, non-authoritative outputs:

1. **Rebound Failure Detector:** fixed rebound candidates, a provisional 12h grouping, +24h negative continuation/retest of the pre-rebound close trough and +72h realized path.
2. **Early Pullback Warning:** baseline indicator from past 4h price move <=-1% compared with next 24h worst CLOSE below -3%; report false alarms/misses, never claim direct comparison to official 3/5 alert timing until original issued alert snapshots exist.
3. **Regime-Conditional Recovery:** fixed preceding 24h high-low CLOSE range >=3% vs below, plus monthly splits, without fitted decision weights or forward regime inference.
4. **Capital Rotation & Breadth:** ETH/BTC 3h relative direction, BTC taker-buy share, derivative OI side-UNKNOWN. Independent, same-clock altcoin breadth is explicitly `UNAVAILABLE` rather than guessed or counted as a second spot vote.
5. **Decision Utility Learning:** hypothetical 24h BTC gross return for candidate groups compared with an all-hour historical reference and zero-entry WAIT, plus 0.2%/0.6% total round-trip cost sensitivity. This is **not** an executable strategy, true price matching, net wallet P&L or demonstrated trade alpha.

All five permanently retain `source_first_known_verified=false`, `calibrated_edge=null`, `trade_permission=NONE`; **the code has no network access, automated signal issuance, persistent episode output or active model retraining**. The existing adaptive Pullback Learning episode owner remains suspended under its own eligibility contract. Tests are included in the existing Daily Capture Architecture Gate; full exact-head CI must be independently read back after this source/document change.

## Research expansion, priority order

1. **Source-time integrity:** bind original collector issuance/first-known to each eligible candle, with ingest time, object sha, source quality and exact owner SHA; explicitly distinguish capture/run coverage from original provider availability; no time back-credit. Do not inject weekly enriched rows into original-issued PIT backtests.
2. **Shock-to-rebound episode atlas:** purely research-only label morphology by first known selloff start, worst pre-event drawdown, recovery speed, new local-low/retest, second leg, and time spent underwater, *after* an original frozen source joins. Keep outcome labels downstream of the feature cutoff and deny new official Pullback episodes while `ELIGIBILITY_STATUS_v1.json` remains suspended.
3. **Regime-conditional ablations:** compare historical episode families stratified by BTC drawdown severity, volatility, ETH/BTC, breadth persistence, spot participation and OI, but count one underlying market shock as one cluster. Apply purge/embargo >=72h on time folds to avoid overlapping future labels contaminating training.
4. **Liquidity and order-flow quality:** taker quote-volume intensity vs its 12 immediate preceding hours; seek exchange-independent spot evidence (not just another Binance-derived metric). Study price-per-unit-quote-volume response and post-impact decay, noting these are not actual orderbook depth or net institutional flows.
5. **Rebound durability and adverse excursion:** prospective fixed labels +6h/+24h/+72h after one registered event; quantify +6h false-recovery rate, 24h retest, 72h repeat-low, MAE/MFE (bar high/low order unknown), and investor regret after realistic spread/slippage bands.
6. **Actions must add utility:** compare HOLD/WAIT baseline, simple BTC price persistence and RQS challenger at matched, legally first-known clocks; include abstentions, missed recoveries, false negatives and after-cost utility, not direction accuracy alone.
7. **Scientific controls:** placebo time-shift, permuted labels within regime, negative-control no-event windows, adjacent-event leakage checks, missingness and revised-source stress. Pre-register one finite family and freeze all parameters before any future held-out tests.

## Continuous logging proposal, without unauthorized activation

Reuse existing Hourly owner + existing GitHub supervised research and Task2 maturation; do NOT create a duplicate live collector, new Work S1, cron or experimental slot. A governed future append-only **value-free** event manifest should have `event_id, source_repository, source_commit_sha, source_blob_sha, original_first_known_at, observation_candle_end_utc, research_contract_sha, signal_issued_at, available_families, freshness, provisional_event_cluster_id, forecast_horizon, maturity_due_at, outcome_available_at, outcome_source_sha, baseline_id, independent_review, score_status`. Importantly: if initial legal clocks are unavailable, set `first_known_verified=false` and refuse forward skill claims; never retroactively forge issuance from the current repository history.

**Mandatory block:** Existing adaptive Pullback Learning `04_MARKET_LEARNING/pullback_learning/ELIGIBILITY_STATUS_v1.json` explicitly suspends mechanical research classification, new episode creation and maturation pending its own eligibility contract. This discovery report does not reopen that owner. Existing Hourly data capture continues; research-only due-only previews do NOT equal permitted live episode issuance or portfolio actions.

**External review:** Have existing Grok Bot via `Investering-AI-Audit-Bridge` independently challenge source clocks, 12h grouping, small-N, data leakage, denominator correctness and whether any candidate actually beats independent controls. Grok's Bridge report is advisory and NOT formal GitHub APPROVED or automatic merge authority.

**Decision now:** Strong priority on *legal source clocks + independent events + matched baseline*. No new numeric RQS score, trade entry, top/bottom claim, BUY/SELL or market authority.
