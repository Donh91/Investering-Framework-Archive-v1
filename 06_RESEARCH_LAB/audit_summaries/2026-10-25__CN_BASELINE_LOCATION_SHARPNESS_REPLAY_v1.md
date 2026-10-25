# Task 2 · CN location, sharpness and simple box controls · 2026-10-25

**Authority:** `RESEARCH_ONLY / NO_PIT_SCIENCE_ADMISSION / NO_MODEL_PROMOTION`. **Owner:** existing Task2 #1596, source #1516, Supervisor #1156, external Grok review via existing Bridge. This is a companion to the **merged** [nine-week historical matrix](2026-10-25__task2_cn_weekly_retrospective_originals_v1.json) and [critical falsification write-up](2026-10-25__TASK2_FORECAST_SKILL_RECHECK_AND_9W_CN_FALSIFICATION_v1.md), **not** a new owner or a redefinition of official CN scoring.

## Real research comparison, not a predictive-skills certificate

A separate independent analyst performed a read-only calculation against the original immutable forecast source refs, archived 168h market outcome packs and the last prior-week settlement `DAY5_7.close` anchor; its implementation is now proposed as reusable deterministic [Python analysis](../../scripts/research/cn_historical_location_baseline.py) with [contract tests](../../tests/research/test_cn_historical_location_baseline.py). Run after checkout:

```bash
python3 -m unittest discover -s tests/research -p test_cn_historical_location_baseline.py -v
python3 scripts/research/cn_historical_location_baseline.py --repo-root . --output /tmp/cn_position_sharpness_replay.json
```

The original nine-week sample has 54 BTC/ETH x D1–2, D3–4, D5–7 comparisons. **W33 is excluded from anchor-based comparison** because the *immediately preceding W32 source pack is DEGRADED with only 40/168 hours*. Do not quietly use that prior close as a verified full-week baseline anchor. This leaves **8 weeks / 48 asset-window comparisons**. For all comparisons the same archived actual LOW/HIGH pair and instrument label is used, but USD vs USDT parity is unresolved and full ISO first windows may straddle issue. Historical provider first-known remains NOT_ADMITTED.

| Competitor / exact description | Joint low+high contained | Mean band width as % of previous close | Mean normalized total breach | Mean Jaccard overlap |
|---|---:|---:|---:|---:|
| CN *original published bands* | **27 / 48 = 56.25%** | **9.411%** | **2.337%** | **0.4376** |
| Same original CN width, recentered on **previous-week CLOSE** | **25 / 48 = 52.08%** | **9.411%** | **2.600%** | **0.4065** |
| Fixed dumb box ±15% of **previous-week CLOSE** | **44 / 48 = 91.67%** | **30.000%** | **0.930%** | **0.1705** |

Interpretation: CN has slightly better placement/overlap against the **width-conditioned same-band control** on this retrospective sample, but that control **copies the CN range width**. It is not an independent forecasting benchmark and therefore does not prove CN incremental skill. The wide ±15% control shows why containment alone is misleading: it covers many more paths but has **much worse Jaccard** (0.1705 vs 0.4376) and **3.19×** the average width. Nor does this establish CN superiority over independently pre-frozen four-week B1 or the M3 DUMB/ATR controls: those separate results already exist and the **2026-10-05 M3 verdict rejected stable CN superiority**.

In the **later Day3–4/Day5–7 subset** (not source-admitted, 32 paired windows): CN **17/32**, width-conditioned previous-close **17/32**, ±15% box **28/32**. Same-width control has **zero incremental hit count advantage** in this subset. This is not an 'out-of-sample' certified comparison: same original issue caveats and asset/event dependence apply.

## Failure-first findings

- **W34 violent upside expansion:** CN BTC weekly HIGH $65,800 vs actual $79,500 (+$13,700 breach); ETH actual $2,546.78 vs $2,000 (+$546.78). A wide band is not an alpha model; never present it as a cost-free fix for a surprise breakout.
- **W38 downside:** BTC D1–2 LOW $74,967.97 vs lower floor $77,000 (−$2,032.03).
- **W41 downside:** BTC D3–4 LOW $80,393.56 vs lower floor $83,000 (−$2,606.44); ETH $2,406.11 vs $2,600 (−$193.89). The direction of **tail failure changes** between W34 and W38/W41; a one-sided widen-downside patch may trade away opportunity or fail bullish pumps.
- **W40 success** does not justify model promotion; both original bands and same-width previous-close bands contained the 6/6 windows.
- **W42 tiny ETH breach** of $2 in the D3–4 window counts as MISS, not rounded to HIT.

## Guards and scientific limits

1. Historical source identity is validated against recorded **Git blob SHA-1** before scoring; actual observation file identity likewise. This is an integrity check on current archived files, **NOT** an upstream first-known proof. Return explicit exception on mismatch.
2. Prior week's pack must be `READY` with `168/168` observed hours. On known source issue timestamps, the prior pack's archive generation cannot be after issue. Unknown original publication time remains UNKNOWN (never 'approved').
3. Extra tests reject contaminated source/actual SHA, duplicate rows, inverted interval bounds, retrospective impossible pack timestamp, timezone-naive source issue and falsified original joint containment. These tests prove fail-closed behavior, **not** forecast edge.
4. No future price, post-issue feature fitting, new API, private-provider value publication, new workflow, rule weight, forecast producer, scorecard rule or portfolio/execution change. No inferred daily CLOSE curve.
5. This script records per-row **joint containment, normalized width, lower/upper breach and Jaccard**. No composite alpha score, random resampling, p-value or **proper probabilistic interval score** is applied to a paired LOW/HIGH extrema target. Raw n=48 does not mean 48 independent market events; 8 weeks spans few regimes.
6. Grok is an **adversarial auditor** of this frozen evidence, never independent scientific validity through AI consensus; require original source hash, exact row math, timestamp/quote control, *negative outcomes retained* and one finite falsifier. Existing [Bridge Grok #63](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/63) includes a scratch-only ±15% hypothesis requiring independent reproduction; this code is a separately verifiable comparison using a DIFFERENT, wider eight-week cohort and **does not retroactively verify #63's 18-row 74.57 vs 72.28 claim**.

## Requested owner-adjudicated next action

If actual GitHub tests and exact-head independent reviewer allow it, merge **research-only** script, tests and this note under existing #1596/#1156. Then use the currently ACTIVE Bridge policy and existing provider-native Grok routine *only if provider runtime readback confirms actually running* for ONE bounded falsification of W34/W38/W41 and matched-clock width controls. Never create a parallel review queue, scheduler, or public 'better AI score'. Skill promotion remains blocked until independent, source-qualified prospective events beat fixed controls and investor false-exit costs are measured.
