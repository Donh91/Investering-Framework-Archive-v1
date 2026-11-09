# CN multiweek calibration, existing-owner cross-project crosswalk

Status 2026-11-09, ADDITIVE_RESEARCH_ONLY. This document is a dated navigation overlay, not a new scheduler, research engine, approval or live model. Original owner issue, immutable source and main readback supersede any stale value.

## Critical verified finding: four-settlement CN learning already exists

- Canonical existing protocol: `05_CYCLE_NAVIGATOR/protocols/CN_PRECISION_LEARNING_SUPERVISOR_v1.md`; code: `scripts/cycle_navigator/cn_precision_learning_supervisor.py`; workflow: `.github/workflows/cycle-navigator-precision-learning-supervisor.yml`.
- Existing workflow executes on successful internal-precision completion, on its Monday 10:45 Europe/Copenhagen scheduled fallback, and manually. Do NOT add another schedule. One original CN settlement per week is the counting grain, with an additive checkpoint every four successful settlements, not every fourth calendar week.
- Source of truth read back from `05_CYCLE_NAVIGATOR/internal_learning/STATE.json` on Nov 9: `settled_week_count=9`, `checkpoint_sequence=2`, `last_checkpoint_settled_count=8`, `last_settled_score_key=Y2026-W45-CN33`, last checkpoint `checkpoints/2026/W44_C002.json`.
- W45 state has `rotation=PERSISTENT_WEAKNESS` with three valid latest observations scoring 50/50/50, and `intraday_day_5_7=WATCH` with 100/50/50. BTC/ETH `*_range` both show 100 across last 4 scoreable values. Null/unscored families are NOT success or independent evidence.
- Original W44_C002 four-settlement API report is already READY: rotation 50 over W41-W44, day5-7 weak, some narrative reversals, the range miss mostly episodic; no system-wide weakness proven. W45 says `WAIT_FOR_MORE_EVIDENCE`, next deep checkpoint not matured, API review `NOT_REQUIRED`.
- Internal score of 100 can be obtained by WIDE ranges. Its state checker does not establish incremental price-forecast skill relative to frozen same-clock B1 or naive matched-width benchmark. Preserve public precision scores and original historic forecasts unchanged.

## Existing research integrations, NO duplicate owners

| Reuse | Original issue/owner | Research input or output | Hard boundary |
|---|---|---|---|
| CN precision supervisor and weekly Master Monday | CN #1516 | Seven-day original publication + weekly settlement and 4-settlement weakness | No historical scores rewritten, AI never required for deterministic final settlement |
| Forecast tournament ARP-01 | Task2 #1596, CN #1516 | Original W44 #2002, newly matured W45 #2054, naive same-width #2049; future independent paired 12h/72h/168h | Exact source/quote/time, width and placement; no false alpha confidence |
| Historical Reality Engine | #1596 | Native verified 2022-2026 public spot hindsight tape and era controls | Historical first-known not established merely by checksum; 72h overlaps are dependent |
| Risk-to-Action ARP-02 | Risk #1553 | Existing cost #2040 + draft #2055, true risk 3/5 issue/delivery reconstruction still missing | WARNING != SELL, live exit rule NONE |
| Transition and market fragility ARP-03 | EDGE #1530, altseason #1918 | PIT feature families, ETH/BTC, breadth, liquidity, momentum/rebound controls | No source-late or 248 pooled calibration rows counted as independent shocks |
| News ARP-05 | News #1888 | Verified first-seen event chronology vs mere website transport | No retrospective event discovery relabeled issued-time warning |
| Microcap ARP-04 | Meme Alpha Lab #22 and sellability #98 | Public safe methodology for no-fill, price impact and capacity | Private holdings, wallet and trade identities never public |
| Learning adjudication | Strategist #1157, existing S4/CRE and learning controllers | Due-only maturity, preregistered child hypotheses, negative outcomes | Existing original owners only, no retroactive new test promotion |
| Qualified GitHub completion | S1 #1156 | Original PR HEAD/CI/review/main readback | Green CI or draft PR is not merged live integration |

## Recommended additive 7/14/28-day research, not duplicate 4w control

1. **Weekly source completeness:** after each natural Monday settlement report originally issued/not issued/censored, exact quote, source first-known and vendor mismatch, full 168h actuals, complete vs preissue candle boundaries, per-model baseline availability and publication success. Mandatory regardless of monthly API cost.
2. **Rolling 14-day early drift:** compare the last TWO source-eligible settled original CN weeks by BTC/ETH and horizon; show first and second week separately, negative/positive trend and invalid/nil counts. This is a DIAGNOSTIC/HEALTH view only, not a 2-week edge verdict.
3. **Every four successful CN settlements:** REUSE existing CN Precision checkpoint, then pair the latest four original issued frozen CN range and legitimate same-clock B1/other pre-issued baselines. Include both previous four where eligible and report same-cohort extrema containment, relative width, placement/Jaccard, downside vs upside breaches, dynamic uncertainty calibration and maturity; treat n<4 or missing quote parity as incomplete, not zero. Preserve W44/W45 separate sources and unknown independent-regime count.
4. **Every 28-day forensics, only if distinct evidence:** use existing 2026-10-13 four-week Compass forensic audit and Task1.5 #1596 to decompose regime shifts, directional-reversal asymmetry, risk-3/5 missed-warning / false-alert case studies, provider clock issues and version changes. Do not re-run expensive HRE downloads on unchanged sources.
5. **Longer 56-day evidence and preregistration:** only after adequate independent cohorts and held-out prospective outcomes, evaluate stability, false alert budget, severity lead-time, failure costs and nonstationary market regimes; do NOT select a new tuned model from the same 28d eval.
6. **Learning handoff:** a material new result/negative contradiction is logged at the ORIGINAL owner; #1157 adjudicates a bounded falsifiable child, only existing scientific admission may authorize a prospective shadow test, #1156 handles qualified merge/consumer proof. Clean NOOP when no material new evidence. This file is navigation, NOT an auto-created queue.

## Scientific stop rules

- Never count 7/14/28-day overlapping rolling windows or BTC and ETH in one market episode as independent sample size; avoid pseudo-precise confidence percentages.
- New week W46 full seven-day daily path and blue dotted site line are separate original issuer/consumer obligations. This analysis is strictly downstream and cannot create/rewrite a frozen forecast.
- Preserve original W45 0 daily published levels; do not backfill them with hindsight or score as issued numeric daily forecasts. Score new W46 daily path only when the actual original immutable issue is verified.
- No changed public precision metric, risk threshold, signal weight, API spend, scheduler, automatic promotion or trading permission from this overlay.

**Next controlled code ticket, conditional:** instrument original Task2/source owner to output 14d/28d same-cohort baseline-vs-CN diagnostics as an additive read-only artifact consumed by existing 4-settlement supervisor, with source-PIT/currency and no-sample negative tests. First verify no existing output already computes the identical comparison and do not bypass original CN #1516 or Task2 #1596 scientific gate.