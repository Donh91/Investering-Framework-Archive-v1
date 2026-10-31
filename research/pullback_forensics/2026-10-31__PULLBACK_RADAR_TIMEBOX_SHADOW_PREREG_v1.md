# Pullback Radar 2.0: Time-boxed Warning Accountability, SHADOW v1

31 October 2026. Owners: existing #1553 Risk-to-Action, #1596 Task 2, #1827 source clock integrity. Scope: additive read-only experiment inside existing Official Compass rolling 14d / Sunday full-history research output. No new cron, model owner, risk thresholds, trade signal, buy, sell or budget. This protocol was informed by reviewed October data. It is DEVELOPMENT, NOT an untouched historical holdout or proven predictive edge.

## Pre-specified research labels

| Horizon from original warning issuance | Candidate BTC full-post-issuance hourly-close downside |
| - | - |
| 12 hours | At least 1.5% |
| 24 hours | At least 2.5% |
| 72 hours | At least 4.0% |

These research decline barriers are not new official risk levels. They must not be retrospectively optimized to October. Credit applies ONLY inside the declared window. A price decline on day 4, day 30 or six months later cannot validate a 72-hour warning.

## One fresh warning, one expiry

A fresh warning requires a qualified recent prior NORMAL/BUILDING transitioning to ELEVATED/HIGH/CONFIRMED within 24 hours. A new HIGH/CONFIRMED escalation can open a separately labelled correlated warning ONLY if it exceeds the peak risk rank so far within the currently open 72-hour episode. A NEW_WARNING/ESCALATION following transient NORMAL/ELEVATED or ELEVATED/HIGH flapping during this episode, without a new severity peak, is RETRIGGER_WITHIN_OPEN_WINDOW_NOT_SCORED: it gets ZERO new hit/false-alarm denominator and does not reset the original expiry. Repeated unchanged ELEVATED/HIGH never creates a fresh alert or extends expiry. Each fresh episode's clock starts at the original accepted issuance, and a separate eligible event can start after the 72-hour episode expires. Candidate escalations inside the same episode are correlated, not independent observations for inference. Initial ELEVATED without a trustworthy prior is LEFT_CENSORED, not a successful alert. Degraded or missing status breaks transition proof.

The baseline price is the first FULLY post-issue completed hourly BTC close, not a tradeable quote. The partly overlapping issue-hour low is excluded to prevent hindsight. For each horizon, only the correctly bounded fully completed hourly-close grid can yield a hit or false alarm. Missing hours yield UNKNOWN. Undue horizons yield PENDING. Since this conservative construction omits the partially overlapping first hour, it cannot claim precise early-warning sensitivity or executable protection. Source availability at original provider first-known time remains UNKNOWN.

## Prior work and limits

Existing M6_WARNING_EVENT_OUTCOME_v1 follows 24h, 72h, 7d, 14d and 30d warning-related market paths, but 14d/30d descriptive outcomes must not be scored as short-horizon forecast success. Existing Task 2 R1 first-known admission 0/11 remains. Existing #1850 rebound quality is separate from downside warning detection. The published 14d audit showed 143/149 ELEVATED risk states and 10/24 directional 12h wins, exactly matching simple frozen BTC momentum on matched clocks, but this cannot establish a time-boxed warning edge.

The new script scripts/learning/pullback_warning_timeliness_shadow.py is a read-only evaluator. It is included in the existing scripts/learning/compass_rolling_14d_audit.py output under pullback_warning_timebox_shadow, with three independent time-box outcome fields, transparency around PENDING/UNKNOWN and repeated states, original file SHA256 lineage, and null certified predictive skill. Original issued freezes, market prices, new model weights, alarm displays and portfolio actions are not modified.

## Forward scientific promotion requirements

1. Verify each original source first-known, immutable issuance, consumer delivery time and valid no-hindsight signal eligibility BEFORE using it for a prospective forecast score.
2. Freeze an untouched future cohort after reviewer-accepted experiment specification. Test 6-8 weeks or longer if not enough independent warnings are issued. Avoid claiming success from a small number of events.
3. Compare same-clock alert budgets against persistence, permanently ELEVATED, independent no-alert slots and matched naive control. Count misses, all non-warning market periods, false alarms per 30d, time-to-event, lead time, and warning expiry. Do not cherry-pick only actual alert rows.
4. Purge episode overlap within at least 72 hours; distinguish multiple alerts for one shock, portfolio horizon and ETH/BTC dependent inputs. Count all attempted variations, including null results.
5. Evaluate pre-specified decision utility net of executable spread, fees and missed rebounds. WAIT for new entries is not a protective SELL on existing holdings.
6. Run an independent review before any effect on official HIGH 4/5, distribution risk, trader notifications, thresholds, Master Monday, Cycle Navigator or portfolio execution. No automatic reweighting.

## Fail-closed invariants

Historical descriptive hit rate is NOT a calibrated probability or certified economic edge. First-known and true delivery are unverified. A long-lived ELEVATED state cannot get an unlimited-duration success label. Optional report execution cannot block original official outcome maturation. New alerts, external notifications, sell/buy instructions and portfolio automation are out of scope. Unknown or censored data must not be treated as absence of a market event.

## Grok Bridge #113 independent adversarial P1 disposition

Grok reproduced 72 apparent NEW_WARNING triggers across six days of alternating NORMAL/ELEVATED for one later BTC drop, plus 40 repeated HIGH/ELEVATED escalation candidates. These synthetic cases proved the original 33/33 test run did not establish proper episode-level deduplication. The researcher now retains a monotonic per-72h episode peak, suppresses within-window retriggers, and tests the exact negative permutations, a genuine higher-severity escalation, expiry and a truly new later episode. This repair changes only research outcome accounting, not the original risk classifier or any trading instruction. A green test still does not establish prospective, actionable edge.
