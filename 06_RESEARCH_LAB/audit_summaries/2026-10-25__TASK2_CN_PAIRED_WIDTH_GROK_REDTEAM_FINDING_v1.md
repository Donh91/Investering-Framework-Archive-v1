# Task 2 · R2 historical paired-width falsifier · 25 October 2026

**Status** `RESEARCH_ONLY`; **science:** `R1_NOT_ADMITTED`; **model/portfolio/public-score changes:** NONE.
**Owner:** Task2 #1596, CN source #1516, existing Supervisor #1156, Grok Bridge advisory #63.
**Executable source table:** [2026-10-25__task2_cn_w41_w42_paired_width_falsifier_v1.json](2026-10-25__task2_cn_w41_w42_paired_width_falsifier_v1.json).

## Why this is new and not a duplicate

The existing [M3 5 Oct adjudication](../m3_checkpoints/2026-10-05__RL-CN-SKILL-BASELINE-003__FINAL_ADJUDICATION_v1.md) **REJECTED established CN weekly range superiority**, and the merged [nine-week negative-outcomes census](2026-10-25__TASK2_FORECAST_SKILL_RECHECK_AND_9W_CN_FALSIFICATION_v1.md) documented 32/54 full-ISO-window containment with source chronology limitations. Both remain unchanged. This addendum provides **originally stored native 4W B1** versus CN on the same four BTC+ETH weekly target rows, *then deliberately attempts to game the same public-style metric using two cheap controls*.

Existing private [Bridge PR #63](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/63) claimed a ±15% comparator outscored CN on 18 three-window rows across W40–W42. Its scratch script is not in that PR; its **exact numeric 18-row result is NOT reproduced/ratified here**. The #63 independent adjudication correctly rejected the out-of-cohort 168h SIDEWAYS baseline and recognized zero 29-row paired lift; do not overwrite that review. This addendum uses a **different, 4-row, complete-week target**. It independently demonstrates a qualitative issue with the metric without claiming to reproduce Grok's distinct figure.

## Read-only direct recomputation (four dependent asset-week targets, only two distinct weeks)

The source-pinned report matches:
- `05_CYCLE_NAVIGATOR/weekly/2026/W41..W42/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`;
- `05_CYCLE_NAVIGATOR/weekly/2026/W41..W42/CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json` (original freeze *after* Monday 00Z);
- `05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W41..W42.json` **original B1**, four prior complete weeks, and original matching `range_baselines/scores/2026/W41..W42.json`;
- original `03_DAILY_CAPTURE_LOGS/weekly/2026/W41..W42.json`, READY with **168 completed hours each**. LOW/HIGH from the three nonoverlapping 48+48+72h weekly segments. Source names, current Git blob identities, B1 source weeks and hash, actual extrema, all 4 candidate forecast intervals and scores are in the JSON.

**Normalizations and hypotheses frozen for this addendum:** For each model, use exactly the B1 previous-week close as anchor (same asset/week); include CN original low/high, the native independent B1 low/high, an **illustrative** box *with the exact width of CN* centred on that same anchor, and a **retrospective stress/falsifier**, anchor × (0.85, 1.15). Neither the centred diagnostic nor 15% box is a legitimately original issued candidate. The latter is intentionally very broad, not a recommended new model.

All models compared against the identical full Mon–Sun archived extreme lows and highs:
- `joint_containment = actual_low >= forecast_low AND actual_high <= forecast_high`;
- `relative_width_pct = 100*(high-low)/anchor`;
- `lower_breach_pct=100*max(0,forecast_low-actual_low)/anchor`;
- `upper_breach_pct=100*max(0,actual_high-forecast_high)/anchor`;
- `intersection=max(0,min(forecast_high,actual_high)-max(forecast_low,actual_low))`;
- `jaccard=intersection/(max(forecast_high,actual_high)-min(forecast_low,actual_low))`;
- **public-formula-style, NOT official or proper joint loss:** `100*[0.7*intersection/(actual_high-actual_low) + 0.3*jaccard]`, score rounded to two decimals *per row*. This is the archived `materialize_public_scorecard.py` arithmetic, reapplied to a **different descriptive full-week cohort**, not a rewriten official CN score.

| Candidate | Complete LOW+HIGH hits / 4 | Mean width % of anchor | Mean same-metric research score | Mean Jaccard |
| --- | ---: | ---: | ---: | ---: |
| Original CN | **2/4** | **14.07%** | **70.96** | **0.444** |
| Original 4W B1 independent | **0/4** | **7.98%** | **38.60** | **0.283** |
| Centred **same CN width**, diagnostic | **2/4** | **14.07%** | **75.03** | **0.480** |
| Trivial ±15% **retrospective** box | **4/4** | **30.00%** | **78.89** | **0.296** |

**Result:** Both the same-width centred diagnostic and an overly broad ±15% stress box beat CN *on this research-only full-week score*, though the ±15% box has **twice the width** and much **worse mean Jaccard** than CN. This exactly demonstrates score gameability. It does **not** imply either hypothetical comparator is a better out-of-sample forecast, nor that B1 is worse in a proper width-adjusted independent replay.

### Strongest opposing evidence (do not hide)

- **W41 downside:** BTC actual LOW $80,393.56 was under CN floor $82,000, and ETH actual LOW $2,406.11 was under CN $2,560; both CN AND B1 missed. Here the same-width centred diagnostic has smaller lower miss than CN.
- **W42 rebound/retest:** CN held both weekly envelopes while B1 missed downside for both BTC and ETH; CN's greater width provided useful observed containment. The 15% control trivially holds everything but spends 30% of the anchor as width. W34 August high breakout and W38 early downside errors remain preserved in the separate nine-week matrix and MUST be in any broader challenge.
- Only **2 distinct market weeks**, with BTC/ETH correlated and same-series multiple candidates, is far too little evidence for confidence bounds or investor edge. Leave-one-week-out flips regime composition, so no "winner" status should be claimed.

## Causal/quote/security gate — crucial

Both CN freezes are AFTER Monday midnight (W41 2026-10-05T06:14Z; W42 2026-10-12T06:32Z). The full Mon–Sun archive contains hours **before issuance**. The official public score first clips to the post-freeze first complete hour. This private-free source-pinned **full-week diagnostic** is NOT that official scoring target, and publication identity does not imply original vendor first-known. The original CN bands are displayed as dollar ranges, while the research market extrema are Binance BTCUSDT/ETHUSDT proxies, **not an exact USD match**. The 4W B1 file was persisted, but exact historical first-receiver issuance provenance and upstream-vendor vintage are not all independently settled. Therefore `scientific_eligible_n=0` and `PREDICTIVE_SKILL=INCONCLUSIVE`.

It would be a serious methodological mistake to call the above a properly calibrated 80% joint minimum/maximum score. Never apply scalar WIS/Winkler to the paired LOW+HIGH as though it is automatically a proper joint score. All original frozen forecast files, public price scores, model weights, threshold, live site, action states and source governance remain unmodified.

## Adversarial and deterministic verification done in this exact producing pass

- All W41/W42 forecast, receipt, B1 forecast/score and 168h observed archive paths separately Git-read and Git blob-pinned (**10** source items); exactly 4 asset-week target pairs.
- Original B1 immutable expected target weeks, `baseline_sha256`, and full archival LOW/HIGH checked **against existing B1 original score** at full numeric precision. Any mismatched week/hash/predicted bounds/outcome extremum throws.
- Input source original 168h and `READY` required; missing/partial source rejects. Reverse band and nonfinite interval reject. Both original W41 CN misses and original W42 CN successes asserted, so accidental reranking cannot erase adverse evidence.
- Assertion `CN hits=2, original B1 hits=0, retrospective ±15% hits=4` executed; per-model width and public-style/actual overlap calculated directly from original values. This is an actual deterministic in-run check, **NOT a durable Python test suite or GitHub CI**; request independent Codex exact-head review and repository CI before integration.
- No code/producer/scorer modifications, no scheduled work or API costs.

## Best next move for existing S1/Task2/Grok

1. **Release this bounded research-only evidence PR** after exact-head CI + independent technical review + main readback; no new owner/agent/queue.
2. Under existing [Grok Bridge #63](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/63) / existing Task2 [Grok handoff](../hugging_face_task2_audit_20261022/28_GROK_BRIDGE_TASK2_PHASE_II_REDTEAM_HANDOFF_20261023.md): Grok independently audit this **4-row** original-data score, reconcile it without falsely reproducing its prior 18-row claim, and propose exactly **one** most informative next period/model comparison. Accept only reproducible, source-linked findings; preserve all failures and output `NO_MATERIAL_CHANGE` if none.
3. Only after original source-clock/receiver and same-quote admission, pin an untouched prospective champion/challenger run: CN vs **preissued B1** vs simple same-width (with ex-ante width selection independent of CN) vs fixed volatility-only plus missingness/abstention. Evaluate real outcome coverage, width, breaches and **paired loss with predeclared mathematical target**, after-cost decision utility separately. W43 B1 exists but is NOT matured at this date; do not score yet. Add **no** public score family or BUY/SELL action from this addendum.

**Disposition:** `RESEARCH_FALSIFICATION_SUPPORTED / SCORING_GAMEABILITY_SUPPORTED / FORECAST_ALPHA_NOT_PROVEN / SOURCE_R1_NOT_ADMITTED`.
