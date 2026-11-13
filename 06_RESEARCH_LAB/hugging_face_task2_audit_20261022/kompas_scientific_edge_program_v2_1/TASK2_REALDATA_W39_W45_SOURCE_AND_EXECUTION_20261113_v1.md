# Task 2 | Native real-data research W39-W45 | 2026-11-13

**Original owners:** Task 2 #1596, CN #1516/#1593, Risk #1553 and Source #1827.
**Class:** source-bound retrospective exploratory research, not proven Kompas edge. No new agent, automation, trading, model or budget authority.

## Actual GitHub Actions receipts

Existing Research Parallel Lanes Skill Contract CI run 43431179518 performed two independent GitHub compute jobs on actual Archive data.

**Forecast job:** GitHub artifact 14040042597 (task2-realdata-range-native) contains forecast_rows.csv and forecast_summary.json, original ZIP SHA256 ba6887e5b7094b031ea2b5f187bcda51c1c82f2b22b96305e33cd40c6e33364a. This is the pre-bootstrap result, to be superseded by final PR-head jobs.

**Risk job:** GitHub artifact 14040197074 (task2-realdata-risk-native) contains risk_rows.csv and risk_summary.json, original ZIP SHA256 6787f6921972d829e4dd60a9a6e676fe0fc5fbf1ad3873542e102d2460bdf0c9. All inputs are publicly archived under 03_DAILY_CAPTURE_LOGS/weekly/2026/W39..W45.

## Real original CN versus three native cheap baselines

From W39-W45, seven forecast origin weeks, two assets and two fully post-Monday-issuance windows (day3-4 and day5-7), **28 qualifying origin/asset/window groups** and 112 same-target four-arm rows were computed. W40 duplicated issue numbers have identical numeric freeze data and were deduplicated, with duplicate count recorded. W46 is unscored until maturity, and full D1-2/weekly windows are excluded because their periods began before forecast issuance.

| Model | Actual entire low/high contained | Mean width / prior close | Mean exploratory width+breach penalty |
|---|---:|---:|---:|
| Original CN frozen bounds | 75.00% | 13.1725% | 23.5389 |
| Previous week full low/high | 21.43% | 8.4300% | 59.0051 |
| Previous close ± half previous week's range | 39.29% | 8.4300% | 41.6365 |
| Previous close ± whole previous week's range | 85.71% | 16.8599% | 25.9899 |

**Important:** The width+breach diagnostic is NOT proof that the original CN bands were calibrated to 90% nominal confidence. First provider publication and first user delivery remain UNKNOWN. Data are after-maturity archival truth, NOT originally PIT-verified provider tape.

**Paired 7-week uncertainty:** For original CN minus wide previous-close full-range baseline, mean penalty difference -2.4510 (smaller is better), CN better in five of seven origin weeks. Deterministic 5,000-resample bootstrap over paired weekly averages, 95% CI approximately [-5.607,+1.016]. This INCLUDES ZERO. W41 has an extreme penalty spike; do not hide it, over-weight 28 correlated rows, or claim significance.

## Genuine archived 1h downside controls, not original risk warnings

Source: 1,176 rows BTCUSDT/ETHUSDT from W39..W45 enriched hourly CSV tapes. 45 complete noon-UTC 72h forward decision origins per asset met lookback and full-maturity rules.

- BTC 8% downside within next 72h: **0 positive / 45**. BTC -3% prior-24h trigger yields TP0 / FP1 / FN0 / TN44. No positive sample, so recall is NOT measured.
- ETH: **4 positive / 45** overlapping daily cutoffs, at most 3 separated event clusters. ETH -3% prior-24h trigger TP1 / FP2 / FN3 / TN39. The -5% trigger TP0 / FP1 / FN4 / TN40, and simple acceleration -3%+4h -1.5% trigger TP0 / FP0 / FN4 / TN41.
- Claimed benefit from assuming a 0.3% roundtrip is an illustrative quote-price comparison, NOT verified execution, fills, slippage, gas or Alpha Paper Wallet v4 after-cost utility.

Original official Kompas 3/5 risk output is NOT reconstructed in this historical test. These are posthoc price-only challenger controls and must never be described as an issued 4/5 signal. W46 public hourly source pack at Monday generation had 0/168 hours, so W46 is not smuggled into this complete-week sample.

## Fable/Claude original owner separation

Existing Fable R1-R4 were completed 2026-11-12. Fable R5 is DATA_GATED to W47+ prospective truth, R6 Alpha × Kompas paper wallet data-gated. This real-data historic replay is original Task2 intake and does not restart or duplicate Fable. Later R5 requires fresh genuine W47+ records, not an extra retrospective split.

Immediate research value: archive original clock/data eligibility, compare CN against cheap baselines, retain both positive and negative results, isolate 7 independent week groups and origin-specific problems. To justify any model promotion, require mature prospective W47+, original issuer/consumer stamp and valid source publication, event-group embargo and actual after-cost paper fills.

**All outputs advisory only. Source digest rows and native job/artifact IDs are in the downloaded JSON evidence.** No main merge until actual PR-head checks/review; no new paid API has been dispatched by this PR.