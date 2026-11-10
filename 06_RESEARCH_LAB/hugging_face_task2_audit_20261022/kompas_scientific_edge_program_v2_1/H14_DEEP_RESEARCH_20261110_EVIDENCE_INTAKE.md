# Task2 | Kompas H14 Deep Research 2026-11-10 | Evidence intake

**Classification:** USER_SUPPLIED_REPORT_INTAKE + DIRECT_ORIGINAL_CORROBORATION + P0_CODE_HANDOFF.

**Existing owners:** Task2 #1596, CN #1516, original source #1827, risk #1553, S1 #1156. Not a new owner, forecast producer, model, registry, scheduler or approval route.

## PDF identity and actual scope

User uploaded the completed 13-page report "Kompas Pro 14 Horizons - Deep Research.pdf" into this conversation. Its exact uploaded file SHA-256 measured locally is b0e90b9a399ef0650a9300a38ffdf549d74e1b120f737839e03e1c38c82b4f0a (115501 bytes). The original PDF bytes are **not** uploaded to GitHub by this change, only this attributed source synopsis. Do not fabricate a remote PDF file or citation.

The report explicitly says its research was not a complete recursive scan. It could not access Claude Bridge or original Ironflow through its own web connection and therefore treats those two as uncorroborated. This subsequent owner-thread GitHub intake **did** read native text reports, and retains their native limits rather than treating adviser claims as direct trade evidence.

The report's core numerical findings: 170 retrospective 1h rows 45.88% direction correct vs 46.47% simple momentum; 330 4h rows 44.85% vs 48.48%; 318 24h rows 44.97% vs 43.71%. All 818 retrospective rows overlap in time and cannot count as independent forecasts. W44 original Cycle Navigator captured BTC+ETH full weekly extremes (2/2) while B1 did not (0/2), but CN intervals were 2.25x and 1.81x wider and the B1 interval-placement Jaccard was stronger. The report prioritizes original time-bound source integrity, daily-close score, fair baseline and outcome maturity over adding indicators or projecting 12-month point prices.

## Direct primary source verification through connected GitHub

1. Claude status on Donh91/Investering-AI-Audit-Bridge branch claude/log is accessible, as is the actual CLAUDE-AUDIT-03b-20261110T021333Z.md. That audit reports no existing 7-daily-close scorer. It separately identifies an unsafe final-scorer fallback when an attested-week site receipt is absent. Archive PR #2070 already owns that **separate** receipt fix, so this intake leaves the original public-score producer unchanged.
2. Native CLAUDE-AUDIT-04b-20261110T051442Z.md directly documents 33 healthy original Compass packets October 4–9 that retained BUILDING/MIXED/HOLD_WAIT while in-packet breadth dropped 0.83→0.08. This is an evidenced **bounded historical episode**, NOT an out-of-sample warning edge. Actual site/user delivery, two unexplained DEGRADED packets, quiet-period controls and entire-2026 false alarm denominators are still open. Its 0.15 breadth trigger is hindsight-exposed exploratory shadow, not official policy.
3. Original Archive IRONFLOW_FULL18M_EMBARGO_CORRECTED_SCIENCE_V2_20261107.md was read directly. The corrected 25-hour label embargo and February 2026 OI missing/censor cases support a retrospective null for stable incremental derivatives Brier skill and a stress-risk undercalibration warning. Neither original 374MB raw files nor vintage provider first-known was independently downloaded by this intake; this does not certify historic decision-time source availability.
4. Original W46 Cycle Navigator forecast freeze and site publication receipt were read directly. The first valid amended issuance is 2026-11-09T10:52:34.925867Z, with scoring from 11:00Z, BTC/ETH USDT and frozen forecast SHA-256 1cee0508f21b7974f3200f60dc65ea51c81c536f7f9c155c89e58fec39ba7f0b. W46 day-1 24 canonical hourly source rows settle BTC actual 75368.41 vs original expected close 74516.84, absolute error 851.57. ETH actual 2135.24 vs original 2113.64, absolute error 21.60. Only hours from 11:00Z are eligible for postissue extrema. Those first-day bands may not be scored as **full-day** range accuracy because 11 of the 24 hours preceded issuance.

## Real code in the current original Task2 research branch

- scripts/research/task2_cn_daily_path_score_v1.py produces 14 **asset-day** records (2 assets × 7 days, not the product's fourteen canonical horizon IDs); checks exact immutable forecast digest and issue/validity clocks, quote, seven published points, maturity, hourly source gap, duplicates, status, OHLC. It does NOT write a new canonical ledger, issue a new forecast or update signals.
- tests/research/test_task2_cn_daily_path_score_v1.py includes positive, source mutation, missing receipt, fake future maturity, duplicate/missing candle, quote mismatch, clock and original actual W46 regression.
- Existing framework-learning-operations.yml PR-only validation gate is extended minimally to compile/test and retain a seven-day evidence artifact. Its scheduled main writer, schedule, rights and publication owner are unchanged. The file is not a new workflow and its new step has the pull_request-only guard.

The first W46 completed daily close can be measured descriptively. The baseline and scientifically admissible edge **cannot** be claimed until trustworthy last-known-at-issue prices and effective independent event sample are source-verified; proper interval scores also require issued quantile/coverage semantics. This work intentionally declares both unavailable.

## Prioritized native owner actions, not a new research queue

| Rank | Owner | Precise evidence and test | Stop rule |
|---|---|---|---|
| P0 | CN #1516 + Task2 #1596 | W46 each daily close plus distinct whole-day vs postissue range statuses, real immutable receipt and due maturity | No 7/7 skill claim until entire UTC target week matures |
| P0 | Source #1827 + Task2 | original provider first-known / last known preissue baseline B0/B1, matched quote and UTC clock | Missing source-time = descriptive-only, no incremental edge |
| P0 | Risk #1553 + Task2 | replicate Claude issued packet stall with genuine source clocks, quiet days, false alarms and risk miss-cost pre-registration | No production breadth threshold chosen from Oct episode |
| P1 | Task2 + CRE | horizon-specific paired direction/close/range/path and action utility after fees, nonoverlap episode denominators | Never convert a 7/10 evidence balance into 70% probability |
| P1 | RPL + Task2 | recheck Ironflow derivatives null and Feb source gap before any prospective ablation | Missing source age or independent cohort means no new production feature |
| P2 | CN #1516 + existing strategic owners | 14/21/30/56-day forward-only scenario hypothesis and long-cycle 1–12m event power | Abstain when original issuance, cycles or sample size insufficient |

The canonical fourteen-horizon registry remains 07_PROMPTS_AND_AGENTS/action_compass/KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json. Separate docs/scientific crosswalk sit in Archive PR #2072, not a second authority. Private Round3 remains PROSPECTIVE_COLLECTION_ONLY, outcome analysis OFF. No private source values, credentials, live trades, paid API or new schedules.

**Source limits:** original PDF fully read; original Bridge and Ironflow text directly read; raw external Ironflow parquet not read; private source plane intentionally not read; deployed CDN user delivery not verified; no claimed complete archive scan, no newly demonstrated predictive edge.