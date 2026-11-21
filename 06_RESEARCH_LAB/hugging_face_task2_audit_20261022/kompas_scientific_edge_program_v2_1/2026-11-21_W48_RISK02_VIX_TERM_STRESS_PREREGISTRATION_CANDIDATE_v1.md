# H-W48-RISK-02 | Prospective VIX term-stress shadow challenger | preregistration candidate v1

**State: DRAFT, NOT FROZEN, NOT ACTIVE.** Research-only. Never rewrite W47, score Round 3, assert economic edge, send live alerts, modify protection, allocate funds, dispatch paid API or create a scheduler. This text is a proposed prospective protocol, not certification that any source was available pre-issue.

**Owner decision D3:** Bridge reports/claude/plan/OWNER_DECISIONS_20261121.md at 7f44694. W48 may begin only if this final-head preregistration is frozen, independently Codex-reviewed and merged on main strictly before Sun 2026-11-22 23:00 UTC; otherwise W49 or later. No retrospective admission. Original owners are #1596, #1553, #1516, #1827; Strategist #1157 and S1 #1156 govern handoff. Method anchor: #1596 comment 7049659898. W47 RISK-01 stays C1_UNSPECIFIED. Retrospective VIX study (Fisher p approximately 0.10 with post-hoc subgroups) is weak development evidence, not a demonstrated effect.

## 1. Frozen question

Does one strictly as-of VIX term-structure stress augmentation of the unchanged original Compass risk state detect future BTC/ETH downside episodes earlier than BOTH (B0) a simple fixed price rule and (B1) the original issued CN/protection state, with the SAME allowed alert budget and without additional false warnings? W47 and all previously examined years are developmental. Hypothesis can fail. No source information from after a decision may enter its signal.

## 2. Exactly three prespecified shadow arms

B0 PRICE-ONLY control: use last completed Binance spot BTCUSDT/ETHUSDT hourly CLOSE, and the maximum CLOSE of the preceding 24 complete hours, excluding the current hour. Trigger if current close is 3.0% or more below that peak. This is a deliberately simple prospective benchmark with a fixed -3% threshold, NOT a claim of historically validated or previously approved ATR calibration. Missing preceding bars makes it UNKNOWN.

B1 ORIGINAL ISSUED control: trigger only on the originally issued, structured Compass/CN protection state ELEVATED or an explicitly documented more-severe state, pinned by original immutable issue hash, issuer time, first-known and consumer availability. If severity ordering, issuance provenance or consumer availability is unprovable, B1_SOURCE_BLOCKED. No textual inference or retrospective reclassification.

C2 ONE VIX augmentation: trigger if B1 is triggered, OR if ALL of these source-admitted same-equity-session facts are simultaneously true:
- VIX close >=20.
- VIX9D close > VIX close > VIX3M close.
- VIX close relative to the VIX close five COMPLETED equity sessions earlier is >=1.20.
- Each value has its own immutable original-source/value digest, session, original publication time, first capture and consumer availability before the decision.

No further qualifiers, weights or fitted thresholds. On weekends and exchange holidays, last-known VIX is descriptive STALE only, NEVER fresh. A missing, revised-after-decision, unproven or unmatched term-structure reading makes the augmentation UNKNOWN; it cannot create an alert. C2 may mirror an independently valid B1 trigger. These VIX thresholds are the candidate stated by #1596/7049659898; no claim of out-of-sample validity.

## 3. Fair clock, quota and source coverage

First potentially eligible W48 week starts Mon 2026-11-23 00:00 UTC only after §7 gates. Observe candidate decisions at the end of each fully completed UTC 1-hour bar, with each source's producer publication, provider/source first-known, capture and consumer delivery timestamps strictly no later than the decision. Before the first admissible original B1 issue, all arms are NOT_YET_AVAILABLE, never backfilled. Count missingness and stale data separately, including unmatched equity sessions and unavailable BTC/ETH source windows.

Equal MAXIMUM alert budget for EACH arm: one hypothetical warning per asset per UTC ISO week, two total possible per week. Choose each arm's FIRST eligible trigger, suppress subsequent ones, retain suppressed counts. Never force a quota-filling alert. Compare actual alerts, missed episodes, false alerts, coverage, and unused capacity at equal permitted budget; do not mislabel unequal actual counts as equal actual utilization. Use the intersection of genuinely available decision times for the primary three-arm comparison, and report the union missingness denominators separately so exclusion cannot make a candidate appear effective.

No new live notification or trading path. These are hypothetical research warnings, NOT delivered user alerts. Original B1 provenance must still be independently verified.

## 4. Endpoint and falsification fixed in advance

For each eligible decision reference price P0 (most recent fully completed hourly spot CLOSE), primary event = LOW <=0.95 x P0 in ANY of the NEXT 72 fully completed 1h bars. Exclude the decision bar and unfinished bars. Report earliest adverse-low bar completion, first actionable warning lead hours, adverse excursion, and event maturity. Same asset, exchange/venue, USDT quote and exposure for all arms. Historical HTTP retrieval is NOT proof of old provider first-known or prior consumer availability.

Overlapping 72-hour windows in one asset are merged into one episode, and related BTC/ETH events in the same stress interval into one correlated family for inference. Hours and two correlated assets must NOT be counted as independent events. Quiet intervals are explicit negative controls. Outcomes without a fully mature 72h tape are UNMATURED.

Primary abstract cost: each false warning costs 1 unit; each missed eligible adverse event costs 3 units, and a timely lead must be positive. Report paired sensitivity with missed-event costs 1 and 5 units, without selecting a favorable ratio post hoc. This is NOT trading PnL or an empirical portfolio cost. Primary superiority only if C2 has LOWER cost than BOTH B0 and B1, strictly positive lead for any incremental true warning, and no higher false-warning rate at the same eligible exposure and maximum budget. Otherwise NOT_SUPERIOR. Report episode recall, precision, lead, false alarms per quiet 72h, suppressed alerts, absent/late source hours and uncertainty. No pooled-hour statistical significance.

Secondary opportunity cost: quiet/upward-market warning burden, reported separately from the adverse-low endpoint. No source-safe executable price or fill claim is implied by an abstract warning. Round 3 remains prospective collection only; no hypothesis testing, PnL, effect estimation or outcome scoring on Round 3 data.

## 5. Predeclared study duration and kill

No weekly outcome-driven edits or winner selection. Minimum observation horizon 26 eligible ISO weeks AND 10 independent matured downside families; administrative cap 52 eligible weeks. If 10 families have not matured by the cap, state INSUFFICIENT_N, not successful. Maintain an all-calendar-week ledger, including ineligible weeks. A material practical gain candidate additionally needs >=6h median earlier timely warning among incremental true warnings and no increased false alarms. If there is no incremental true warning, lead improvement is NOT_ESTIMABLE. These are prospective exploratory criteria, not predicted empirical gains. No automatic promotion even if passed; independent scientific review and original-owner approval would still be required.

No source version or first-known proof => SOURCE_BLOCKED, not zero or false. No adequate common B0/B1 clock => SCIENTIFIC_HOLD. If existing HRE/CRE has an eligible identical study, route there; do not create a parallel evaluator. Roll back by reverting this research-only file.

## 6. Adversarial method fixtures required before scoring

Wrong asset or venue/quote; incorrect milliseconds/seconds; missing 1h bar; future-hour look-ahead; VIX9D/VIX/VIX3M mismatched equity sessions; weekend carry-forward; first publication/capture after decision; revised VIX retrofitted; five-session comparison using future values; B1 source published or delivered later; no documented B1 severity ordering; duplicate episode; two correlated assets called independent; current uncompleted bar used as future LOW; an alert after the first event counted early; >1 alert/asset-week; stale source treated as normal; mutated prereg after source freeze. Each case must reject or return explicit UNKNOWN/blocked. Negative mutation checks must not reuse the same faulty production hash formula.

## 7. Before W48 is scientifically eligible, ALL must pass

1. Exact final Git blob frozen in a PR; independent Codex review on that exact head under AGENTS.md §0.2f (no unresolved P0/P1/P2) and green native exact-head CI. Original methodology owners acknowledge one fixed arm definition and no post-issue tuning.
2. Independently proven as-of source receipts for the B0/B1 spot and issued protection comparators and matched VIX series; preissue access to each rule, dataset version and delivery clock. If source adapter, original B1 availability, or B0 exact rule is not frozen and validated before the first observation, stop at SCIENTIFIC_HOLD. The present PR supplies NONE of those runtime receipts.
3. Owner-present squash merge to main BEFORE 2026-11-22 23:00 UTC; read back final file blob, reviewer, CI run IDs, merge commit/time. No workflow, scheduler, paid API, live decision or S1 grant.

If ANY gate misses the Sunday deadline, W48 = NOT_ADMITTED. Candidate earliest cohort becomes W49 only after new as-of certification; never retroactively admit W48 or quietly relabel reviewed W48 development data as untouched W49 evidence.
