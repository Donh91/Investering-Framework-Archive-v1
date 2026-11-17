# W47 risk challenger, pre-registration CANDIDATE (owner-approved research specification)

Created 2026-11-15. **NOT A PROVEN IMMUTABLE PREISSUE FREEZE.** GitHub commit/first-main timestamp and original Monday W47 issuance/delivery must be independently checked before any prospective claim. If commit occurs after issuance, mark LATE/EXPLORATORY. Never backdate.

## Governance and source boundaries
Original authority Task2 #1596; risk #1553; CN #1516; source #1827; Bridge #173. No producer, score, workflow, trade or paid model modifications. W46 is developmental retrospective, one dependent week. Do not tune on W46 or count its five closes as independent weeks. All source inputs require original event timestamp, publication time, collection time, consumer first-delivery, asset, venue, currency, and SHA. Unverifiable clocks => SOURCE_BLOCKED, never silently imputed.

## Fixed question H-W47-RISK-01
Does a source-safe *consecutive downside breach escalation* improve time-to-warning before independently observed 72-hour >=5% adverse BTC/ETH moves compared with BOTH (B0) a pre-known price/ATR/drawdown comparator and (B1) original issued CN/pullback risk, at equal alert budget and without excessive false alerts? Research-only hypothesis, no expected direction of W47 returns.

## Fixed arms
- **B0**: pre-known prior completed-hour spot price and the existing archived pre-issue ATR/drawdown rule. If ATR parameters are not documented preissue, mark B0_ATR_UNSPECIFIED and use only frozen simple price baseline, not fitted postissue ATR.
- **B1**: exact original issuer-signed CN and pullback risk state at its first issue, unchanged.
- **C1**: one shadow-only rule requiring sequential independently verified breach of original daily downside envelope and then original weekly downside envelope, plus only a pre-existing documented volatility/momentum qualifier. Do not invent thresholds or a 4/5 risk mapping. If qualifier or escalation mapping is not preissue documented, C1_UNSPECIFIED and no prospective efficacy claim.

## Outcome and evaluation
Primary event: adverse >=5% move from eligible decision reference price within following 72h, assessed using first eligible independently archived 1h spot bars; report both max adverse excursion and first breach time. Use asset-week/event clusters rather than treating hours as independent samples. Compare first actionable alert lead time, precision, recall, false alerts per quiet 72h window, missed episodes, and alert-cost-weighted net utility. Apply identical coverage, issuance time, observation lag and alert budget to B0/B1/C1. Record UNKNOWN, missing and stale periods in denominators. Avoid overlapping-window pseudo-replication; cluster uncertainty by week/episode, disclose insufficient sample size.

Secondary: daily expected-close MAE versus preissue flat price; original band coverage versus equal-width baseline. Keep USDT and USD distinct. Daily UTC close is final fully completed 23:00-23:59 UTC hourly candle, mature at next 00:00 UTC; no intrabar close. Range-floor breach uses hourly LOW, not daily close, and is NOT a historical live warning without original delivery receipt.

## Leakage and negative controls
Never use W46 outcomes to fit C1; never use ETF/stablecoin publication after the target issue. Explicitly test shifted source timestamps, absent delivery receipts, stale price, incorrect milliseconds/seconds, mismatched venue/quote, overlapping events, and postissue revised forecasts. No source first-known => reject from prospective set. Include quiet periods and upward opportunity-cost controls.

## Decision / kill rule
C1 only eligible for scientific promotion after multiple independent forward event and quiet clusters with verifiable first-known evidence, and improvement against BOTH B0 and B1 in cost-adjusted utility AND warning lead time at equal false-alarm budget. Otherwise REJECTED or INSUFFICIENT_N / SOURCE_BLOCKED. No production escalation from this prereg alone. Original owners must approve metric thresholds and exact implementation before first issue; unspecified thresholds cannot be tuned after results.

## Monday freeze checklist
Record: exact Git commit SHA of this prereg; GitHub first-main commit time; original W47 CN/Challenger A first issue SHA and UTC timestamp; consumer first-delivery receipt; first relevant outcomes; original B0/B1/C1 source hashes; independent Claude methodology review. If any preissue pin fails, this document remains a research design, NOT a valid prospective W47 preregistration.

## Paid Astra separation
No Astra run performed here. Astra HIGH prompt should investigate source-clock root causes, W46 MAE failure, risk severity lag, multi-regime challenger falsification, negative controls, and lowest-complexity implementable improvement. Do not dispatch until separately reviewed executor and provider total-cost cap are verified; existing false && and authorized_paid_dispatch=false remain binding.
