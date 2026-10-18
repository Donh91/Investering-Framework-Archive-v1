# TASK 2 · R0/R1 source audit, synthetic falsification and next legal tests

Date: 2026-10-12. Existing mission: COMPASS-HORIZON-EDGE-20261011. Parent draft PR: #1573. Task 1 handoff: PR #1592. Evidence snapshot from control-plane main **a939cf5df42f3e9a6db1503d59a55e4305fa3c38**, not from the stale research branch. This document is an evidence-bound research checkpoint, not scientific admission, an improved forecast, a trade instruction, a new research owner or a completed historical backtest.

Machine receipt: [TASK2_R0_READONLY_RECEIPT_v1.json](2026-10-12__TASK2_R0_READONLY_RECEIPT_v1.json). Runnable independent synthetic check: [task2_synthetic_oracle_v1.mjs](2026-10-12__task2_synthetic_oracle_v1.mjs).

## A. Task 1 supersession, ownership and separation

- PR #1590 was independently handled by the existing Supervisor and **merged** at commit 79d73b334e641394c4fb84c3953e136231217714, 2026-10-12 20:30:05 UTC. PR #1592 was an earlier valid-as-of historical snapshot describing it as not yet merged. Do NOT mutate old evidence booleans, and do NOT have Task 2 review/merge #1590 again.
- #1573 remains the single research PR for the horizon/EDGE study; existing EDGE owner #1530, risk/action #1553, trial-accounting #1557, Forward Path #1516 and existing CN/M3 score owners retain authority.
- Source plane: public control-plane metadata only. AGENTS.md and 00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md prohibit copying or inferring restricted provider data from Donh91/secrets. No new schedule, parallel market owner or API/Work spending.
- Research artifacts on this PR remain DRAFT, research-only, no model/signal/threshold changes. Neither warning nor HOLD_WAIT is a SELL decision.

## B. Data-source and chronological quality

### B1. Public EDGE M6 lineage

At pinned main:

| Read-only source | Git blob SHA | Observed status |
| --- | --- | --- |
| research/framework_memory/m6_warning_events/LATEST.json | 1acf875c958253b44e78f23e9fd0f84208143f80 | 16 warning rows, **2 provisional observation clusters** |
| research/framework_memory/edge001_tsunami_features/LATEST.json | f56a87ef2a49433a57d3838ccfa92e3a2d620a32 | 16 feature freezes, outcome_joined=false |
| research/framework_memory/edge_compound_governor/LATEST.json | b45aa0465da95ebf0c1da841dbc44da81f2fe380 | generated 2026-10-12 20:30:56Z, COLLECT |
| research/framework_memory/action_compass_calibration/LATEST_EXIT_WARNING_CALIBRATION.json | efe1cc88ade2e20a02593f31642009d68780566a | 212 eligible series rows, zero typed-warning rows |
| EDGE-001 T2B_PROVENANCE_PREFLIGHT_v1.json | 87aeafdd0e96fe4aac7bdf54761abe8b99f208f2 | 94 annotations; original typed historical Claim A NOT_TESTABLE_AT_PIT |
| Pullback ELIGIBILITY_STATUS_v1.json | 84053fac2da1800d01d5a13b24e0371152c43339 | SUSPENDED_NO_ELIGIBILITY_CONTRACT |
| Pullback PERFORMANCE_SUMMARY.json | 5007dc1ff593d585df210ac3f3f524856967b9b5 | zero eligible closed episodes, return uplift null |
| 144_VARIANT_FROZEN_MANIFEST_v1.json | a75055851c41d2b4cd2532945c16bdecdef46c2d | 144 declared variants, no historical scoring |

Chronological cross-check of all **16** public feature records: 16/16 carried all four inspected clocks; 16/16 have candle close no later than declared first-main-commit time; 16/16 have declared first-main-commit no later than warning knowledge; 16/16 match warning issued time to declared knowledge; no future candle close. Observed candle-close-to-warning age ranges approximately **0.1933 to 2.8875 hours**. This is an INTERNAL CONSISTENCY CHECK of recorded metadata, not proof that every upstream provider sample was legally available as-of, or an owner-approved source-specific freshness SLA. Independent first-known and immutable restricted binding remain required for real historical admission.

The governor's natural post-#1586 payload receipt is newly populated: **m6_matured_payload_integrity PASS (checked 48, invalid 0)**; 16 feature rows and 16 M6 events match; zero typed warning rows in the calibration source. Thus the previous *missing new natural EDGE receipt* blocker is resolved technically on pinned main. That does NOT close PIT admissibility, independent event-family classification or economic information edge.

The 16 warning observations split **12 in provisional cluster M6F-20260919T092156Z** and **4 in provisional cluster M6F-20261012T064626Z**. At 24h / 72h / 7d / 14d there are 12 matured records per horizon, all belonging to the one earlier provisional cluster. 30d matured count is zero. The count of independently verified adverse price-shock families remains **NULL**, as does the number of independently verified normal/V-recovery controls. Neither 48 matured per-horizon event results nor the two provisional clusters are 48 or two validated independent adverse families.

### B2. Original Official and Shadow population inventory, not retroactive re-scoring

Public Git tree census of the immutable OUTCOME FILE TREE at pinned source snapshot:

| Cohort | Tree SHA | JSON outcome files | Distinct source forecast IDs by filename | 12h / 72h / 168h |
| --- | --- | ---: | ---: | --- |
| Official | b544250c5c760191a346a31652ee5d7e259d3a1d | 352 | 147 | 130 / 126 / 96 |
| Shadow v2 | deabe8d542e93a306ea8ce2ac3f7c814508366e7 | 53 | 27 | 23 / 20 / 10 |

Each tree listing returned truncated=false. This is a FILE-AND-FILENAME census, not a full per-file class/version/censor census and NOT a number of independent market events. Official files span 2026-09-16 through 2026-10-11; Shadow 2026-09-30 through 2026-10-11. Multiple horizons per freeze share an origin and overlapping prices; do not multiply them into independent trials.

Two independently fetched representative outcome blobs were legacy v2: Official 2026-10-11 example blob 72968312baa86f1eff612f1969c2d91a09f5b759, scoring contract OFFICIAL_DAILY_COMPASS_SCORING_v2; Shadow 2026-10-11 example blob d75830dbe639d65ce3ad208e12a963de0e53cac0, SHADOW_COMPASS_V2_SCORING_v2. The observed Official legacy example was ABSTAINED on both BTC and ETH; the Shadow example was INCORRECT on both, and they are NOT a scientifically paired comparison. Do not generalize these samples to population accuracy.

Natural Official/Shadow outcome run #38300787727 after #1581: Official 352 ALREADY_MATURED + 116 PENDING_SCORING_CONTRACT_MISMATCH; Shadow 53 ALREADY_MATURED + 34 PENDING_SCORING_CONTRACT_MISMATCH; 0 newly matured v3; 0 admitted matched pairs, 53 quarantined historic Shadow pairs. Latest issued Official forecast on 2026-10-12 19:59:38Z declares OFFICIAL_DAILY_COMPASS_SCORING_v3. A new v3 freeze is not a matured v3 result. The v2 target-observation-clock contamination remains quarantined; v2 must never be silently rescored into v3.

**Known limits:** Full v1/v2/v3 frozen-forecast census, true number of censored vs actually matured registry receipts, source proof of every forecast first-known time, and independent scoreable v3 paired counts are NOT yet available. Issue #1557 remains open. Its sample of 50 censored-only outcomes and 20 misclassified prospective flags is an observed warning, not the full global attempted-trial count. NULL stays NULL.

### B3. Source time definition before a performance test

For every admitted future record, archive immutable: source contract/schema/version; provider and dataset commit+hash; observed bar OPEN; calculated bar CLOSE; batch collected/received time; first repository commit; owner-ratified **legal first-known**; original forecast issue+publication+delivery time; policy/scoring version; horizon target and original maturity; quality/freshness SLA; null/censor reason. Candle-close is not itself evidence of first knowledge; an aggregate source_window_end cannot be used as each hourly candle's actual first-known. Data captured after a cutoff cannot become an earlier signal. Batch-shared times cannot create fake hourly persistence. Source-specific SLA MUST be fixed by owner before replay. Missing fields => QUARANTINED, never filled by hindsight.

## C. Actual synthetic experiment: complete independent 144-cell enumeration

Runnable file: 2026-10-12__task2_synthetic_oracle_v1.mjs. From repo root with Node 20+: 
    node 04_MARKET_LEARNING/handlekompas/research/2026-10-12__task2_synthetic_oracle_v1.mjs

This independent JS oracle was actually executed with the frozen manifest loaded by the GitHub connector. Exact JSON tuple+order comparison PASS; 3 severity x 4 persistence x 3 delay x 4 cooldown = **144 unique declared variants**; **14 deliberately artificial scenarios x 144 = 2,016 scenario-variant executions**; 6 malformed/unsafe input controls correctly rejected. Structural assertions cover NORMAL with no warnings, stale trickle, continuous HIGH, missing hour, UNKNOWN/UNAVAILABLE/degraded reset, source segment/policy cutover, simultaneous batch and same decision-hour slot, synthetic V-recovery, and asset-isolated mechanics.

Specific objective synthetic negatives: NO_WARNING activated 0/144 variants; STALE_TRICKLE activated 0/144; delayed/batched/policy/no-data fixtures did not establish false multi-hour confirmation; one decision-hour could not create duplicate one-confirmation alerts. The recovery fixture intentionally includes a warning followed by synthetic NORMAL; it proves the control scenario is representable, not that the real forecaster predicts recovery or incurs a measured false-sale cost.

This is a **separate oracle**, not exact execution of the repository's production Python harness during this Task 2 session. Pre-existing independent CI on #1590 tested the production self-test, but that is a separate historical receipt. Synthetic age windows (15, 180 and 240 minutes for different deliberately fabricated cases) are *test fixtures*, NEVER approved production source SLAs. The oracle's total artificial alert counts are not precision, false-positive rates, event N, PnL or a selected best variant. No historical input, score or return enters this experiment. Before scientific adoption, run this separate oracle in an independently recorded CI/job alongside the actual Python harness and cross-check all variant per-case outputs, including time representation and source-age constraints.

## D. Freeze candidate hypotheses BEFORE observing any new future outcome

These are TEST PROPOSALS, not confirmed conclusions. The actual prospective cohort cutoff, horizon, exact source and episode-label rules must be independently frozen and approved by relevant owners before any live test.

| ID | Falsifiable hypothesis | Same-decision-clock baseline | Required eligible population | Admission now |
| --- | --- | --- | --- | --- |
| H7D | A frozen 5–7d BTC/ETH range yields better containment vs width / tail miss than native weekly carry and pre-frozen ATR-only ranges | Existing same-horizon CN/M3 range and naive carry | Independent eligible weekly freezes, same horizon, first-known source and daily realized path | BLOCKED / design |
| HPATH | Prospective 14–21d path identifies directional participation, ordering and invalidation beyond naive continuation/reversal | Same-source naive trend and no-change, abstention counted separately | #1516 freeze before outcome, 3–7 / 8–14 / 15–21d path checkpoints | BLOCKED / no admitted cohort |
| HLEAD | M6 early warnings add lead vs pre-frozen same-clock price-only P1/P2 without overtriggering on normal or V-recovery | P1 5%, P2 3%, no-warning and continuity controls | Independent adverse and matched normal families with typed PIT warnings, delivery clocks | BLOCKED / typed historical joins=0 |
| HPULL | A 5h dip, 72h correction and 2–3w continuation are distinguishable before the trough without claiming rebound timing hindsight | Prior as-of trend/volatility state, no-classification abstention | Ratified pullback episode specification and prospectively sealed onset/trough/recovery windows | BLOCKED / pullback suspended, closed episodes=0 |
| HROT | ETH/BTC + real breadth and pre-freeze sector rotation can distinguish distribution from genuine broad alt participation beyond BTC-only risk | BTC-only and static no-rotation controls | Source timestamp/constituent/version eligibility; independent regime episodes | DESIGN ONLY / proxy breadth noncanonical |
| HACTION | Warning/7D/21D disagreement changes a real incumbent holder or fresh-cash decision and adds net drawdown-aware utility | Existing holder HOLD versus fresh cash WAIT, same costs | Independently timed emission/delivery/executability; asset liquidity, spread, slippage, missed upside, tax sensitivity | BLOCKED / no governed economic tape |

Predeclared outcomes must include **abstentions, censored/pending, failed deliveries, source errors and missing instruments** in denominators. Report calibration only when exact event+horizon probabilities were issued prospectively and numerators/denominators are independently verified. HIGH severity and a 1–10 visual risk grade are not probabilities.

### Adverse and negative-control family pre-registration rules

1. Anchor all candidates at a **pre-outcome decision cutoff** and a fixed asset/instrument universe from the existing owner. Enroll consecutive eligible issuance windows, not only hours preceding known crashes. Keep unissued/unknown and no-warning cohorts visible without falsely calling unobserved warnings negative.
2. Freeze independent *adverse shock family* criteria, lookback/overlap embargo, first onset, event severity tier, clustered BTC/ETH correlation and hierarchy **before** reading outcome extremes; reuse the EDGE owner. Separately freeze matched normal continuation, V-recovery, bull acceleration and consolidation controls by pre-event regime/source quality/horizon, with selection blind to later return or trough.
3. Record both event detection lead and **false warning/time-out-of-market opportunity cost**, using actual first delivered and earliest executable decision, not model output publication alone. For micro/memes, require separate liquidity and spread sources; BTC spot references are non-executable proxies.
4. Pair identical timeframe/frozen feature snapshots across baseline and challenger. Do not credit 12 hourly warning rows as 12 independent market episodes or 12h/72h/7d/14d windows as four independent bets.
5. No cherry-picked 2020–21 or 2025–26 unseen holdout: those market episodes have already been exposed to development. A new genuine prospective holdout requires a separately sealed manifest before outcome, no peeking, publication embargo, owner unseal and independent adjudicator.
6. Record every proposed trial, failed read, replay, policy revision, attempted parameter cell and duplicate under #1557's governed global multiplicity denominator. No broad multi-arm winner search while missing/ambiguous. Multiplicity adjustment, blocked bootstrap and leave-one-family-out are required only if admissible independent N eventually exists.
7. Treat ABSENCE OF COVERAGE as UNKNOWN, not NO_WARNING. Distribution and pullback horizons without typed PIT source and censor expiry stay NOT_TESTABLE. No direct policy/margin/SELL update from these studies.

### Failure patterns targeted, not proven

- Forecast correctness inflated by SIDEWAYS/MIXED/abstain labels, wide bands or overlapping hourly reissues.
- Wrong bar-open/close or batch availability causing artificial predictive lead, now partially guarded by scoring v3 and frozen clocks.
- 1 matured cluster reused for 48 window-wise metrics, giving false sample-size certainty.
- Only testing declines and omitting V-shaped reversals, normal regimes, sudden rallies and macro/ETF-induced source latency.
- Forecasted distribution after the trough rather than warning before first executable deterioration; fresh cash and incumbent holdings require separate baseline.
- Confusing 2–3w structural risk with 5–7d entry zones and 12–72h permission; mixing proxy alt breadth with canonical confirmation.
- Overreactive short warning or underreactive weekly projection, neither of which automatically means SELL; unquantified stablecoin conversion and re-entry friction.
- Retrospective thresholds, changes in policy version, data-discovery timestamp drift and post-selection benchmark improvement.

## E. Explicit stage adjudication and owned next actions

| Stage | Task 2 verdict | Source-bound next action and owner |
| --- | --- | --- |
| R0 source and chronology | PARTIAL PASS, public metadata only | #1530 ratify source-specific first-known + freshness; restricted input stays private |
| R0 synthetic 144 and controls | PASS independent oracle, production harness not freshly executed here | #1530 independently run both oracles in controlled CI, check semantic differential |
| R1 Original Official/Shadow and censor population | PARTIAL, tree file census and post-#1581 natural run only | #1553 publish read-only original-contract outcome/forecast/censor reason census, no v2 replay |
| R1 global multiplicity | BLOCKED | #1557 derive monotonic proposal-time denominator; #1157 read-only consumption |
| R2 7D baseline / 14D path metrics | NOT RUN | existing CN/M3 and #1516 freeze each horizon prospectively with same-clock controls |
| R3 14/21D turning path | NOT RUN | #1516 first prospective schema and immutable issuance; wait for maturity |
| R4/R4P economics / pullback | BLOCKED | #1553 restore research eligibility only via negative-tested owner contract; DEL separate economic permission |
| R5 historical 144x negative family replay | BLOCKED | #1530 need independently admitted typed PIT source, control family and sealed holdout |
| R6 learn and mature | WAITING FOR LEGAL NEW v3 OUTCOMES | existing natural Official/Shadow workflow and owner, not this draft PR |
| R7 information / trade-edge claim | PENDING INDEPENDENT SCIENCE REVIEW | no positive alpha verdict until all relevant gates met |

**Immediate next lawful outcome:** keep new 16-row feature/M6 acquisition and natural governor on their existing schedule, harvest first new real v3 matured source receipt when it arrives, and let #1530 adjudicate one bounded source-attestation decision. #1557's censored/outcome-denominator remediation is the highest-impact research integrity prerequisite; #1553 can independently specify Pullback research re-entry without premature deployment. Do NOT spin up new schedulers or parallel owners. No user portfolio position, new paid API call or Work credit was required for this R0 work.

**Exit verdict:** R0 synthetic mechanics reproducibly exercised; public-source metadata consistent; natural governor technical integrity achieved; original historical typed information edge and all action/PnL claims remain scientifically **NOT ESTABLISHED**. Blockers are explicit scientific missingness, not permission to manufacture scores.