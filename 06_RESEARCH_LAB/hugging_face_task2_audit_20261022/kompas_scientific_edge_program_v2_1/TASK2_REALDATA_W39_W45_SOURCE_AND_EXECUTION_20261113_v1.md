# Task 2 | Native real-data research W39-W45 | 2026-11-13

**Original owners:** Task 2 #1596, CN #1516/#1593, Risk #1553 and Source #1827.
**Class:** source-bound retrospective exploratory research, not proven Kompas edge. No new agent, automation, trading, model or budget authority.

## Actual GitHub Actions receipts

Existing Research Parallel Lanes Skill Contract CI run 43432636748 performed two independent GitHub compute jobs on actual Archive data.

**Forecast job:** GitHub artifact 14040451340 (task2-realdata-range-native) contains forecast_rows.csv and forecast_summary.json, original ZIP SHA256 140011cd00f4cb6e902fc3cd5d450d3331d8792f55f8b96ab844917cae6acbc5. This is the post-bootstrap and native-tested result.

**Risk job:** GitHub artifact 14040445876 (task2-realdata-risk-native) contains risk_rows.csv and risk_summary.json, original ZIP SHA256 6a82d456b4751408437e1124ddf65665cccdc4099d009f8bb4cd3ebe0b2d7a6d. All inputs are publicly archived under 03_DAILY_CAPTURE_LOGS/weekly/2026/W39..W45.

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

Source: 1,176 rows BTCUSDT/ETHUSDT from W39..W45 enriched hourly CSV tapes. 16 complete noon-UTC decision origins per asset meet SAME-CUTOFF source-approved anchor and complete 72h maturity; 30 decision days refused because data arrived after cutoff.

- BTC 8% downside within next 72h: **0 positive / 16**. BTC -3% prior-24h trigger yields TP0 / FP1 / FN0 / TN15. No positive sample, so recall is NOT measured.
- ETH: **0 positive / 16 eligible decision cutoffs** after Codex P2 correction. ETH -3% prior-24h trigger TP0 / FP2 / FN0 / TN14. The -5% trigger TP0 / FP1 / FN0 / TN15; joint acceleration -3%+4h -1.5% trigger TP0 / FP0 / FN0 / TN16. Initial 4 positive apparent ETH outcomes from 45 cutoffs were **INVALIDATED** because the model used stale lagged bar close as the decision anchor. This is an explicit scientific retraction of those 4 positives, not a null proving that crashes do not occur.
- Claimed benefit from assuming a 0.3% roundtrip is an illustrative quote-price comparison, NOT verified execution, fills, slippage, gas or Alpha Paper Wallet v4 after-cost utility.

Original official Kompas 3/5 risk output is NOT reconstructed in this historical test. These are posthoc price-only challenger controls and must never be described as an issued 4/5 signal. W46 public hourly source pack at Monday generation had 0/168 hours, so W46 is not smuggled into this complete-week sample.

## Fable/Claude original owner separation

Existing Fable R1-R4 were completed 2026-11-12. Fable R5 is DATA_GATED to W47+ prospective truth, R6 Alpha × Kompas paper wallet data-gated. This real-data historic replay is original Task2 intake and does not restart or duplicate Fable. Later R5 requires fresh genuine W47+ records, not an extra retrospective split.

Immediate research value: archive original clock/data eligibility, compare CN against cheap baselines, retain both positive and negative results, isolate 7 independent week groups and origin-specific problems. To justify any model promotion, require mature prospective W47+, original issuer/consumer stamp and valid source publication, event-group embargo and actual after-cost paper fills.

**All outputs advisory only. Source digest rows and native job/artifact IDs are in the downloaded JSON evidence.** No main merge until actual PR-head checks/review; no new paid API has been dispatched by this PR.

## P2 audit correction and retained chronology

Codex independently found a stale decision anchor at 2026-10-07T12:00:00Z: earlier source-qualified ETH 2616.32 vs actual decision-aligned ETH 2578.94. Earlier analysis wrongly counted 4/45 ETH-positive 72h cases. Exact-cutoff source-window availability is now a mandatory condition; 30 decision days are ABSTAIN/REFUSED, leaving 16 per asset and zero positive outcomes. The evidence scope shrank substantially. DO NOT infer warning recall, profitable exits or higher live risk levels from this selection. The original initial zip artifacts remain identified in PR discussion as NEGATIVE AUDIT TRAIL and MUST NOT be sent to Astra as final valid inputs. Current corrected native output at GitHub Actions run 43432636748, independent jobs + 14/14 tests. Paired origin-week bootstrap CN penalty diff to widest baseline -2.451014, 95% CI [-5.606661, +1.016042], crosses 0.
