# 14 | Scientific falsification, adversarial tests, baselines and kill gates
**Status:** preregistration REQUIREMENTS / NOT A PREREGISTERED EXPERIMENT / NO OUTCOME CLAIM. Before any actual run freeze exact trial ID and parameters in existing Active Test Registry through authorized owner. This document defines what must be frozen, it does not retroactively register cohorts.

## I. Null hypotheses and estimands
**H0-INFO:** original as-issued model forecasts give no additional information beyond matched same-clock mechanical model(s) under a fixed loss function on admissible independent event families.
**H0-ACTION:** after latency, fees, slippage, opportunity cost, exposure matching and reentry discipline, a rule using the signal does not improve net wealth/risk-adjusted utility over the correct HOLD (incumbent capital) or WAIT (new cash) comparator.
**H0-HF:** added Hugging Face public source or pretrained model provides no **independent, lawful, contemporaneously observable** increment over current existing source/cheap model, conditional on first-known and provenance.
**H0-DEFENSE:** protection warnings do not improve after-cost outcome when evaluated against false early exits and missed rebound upside.
**H0-OFFENSE:** graduated entry/readiness does not improve risk-adjusted upside capture compared with existing guarded policies, after accounting for adverse fills and security/fakeout exposure.
**H0-COMPLEXITY:** richer score ensemble does not outperform a smaller selected sensor set after multiplicity, correlated-feature and overhead taxes.

All six may remain unresolved due no eligible outcomes. Source availability does not reject a null.

## II. Freeze an experiment card before scoring
Required `trial_id`, original signed owner, canonical effective policy SHA, underlying issue version/first-delivery clock, question and narrow population, eligibility/exclusions, data class, last pre-outcome cutoff, independent family definition, forecast and target horizon, original outcome source, missing/censored/pending treatment, source revisions and first-known, treatment vs baseline arms, loss/utility, transaction assumptions, primary endpoint, secondary descriptive endpoints, uncertainty method, multiplicity family, held-out period, minimum information threshold and STOP/promotion conditions.
Record reason for every discarded row and keep all attempted rows in denominator. A prereg written after first access to relevant labels is `DEVELOPMENT_ONLY` regardless of its formal timestamp.
For repeated event-family or time-series reuse: purged/embargoed forward walk; cluster event families; block bootstrap or HAC when justified; sensitivity to alternative non-overlapping windows; do not call each same-day coin/candle a new independent trial.

## III. Negative-control battery
| ID | Inject/adversarial case | Mandatory outcome |
|---|---|---|
| N01 | original issue timestamp after target price move | `PIT_REJECTED` |
| N02 | 1H candle open precedes issue but close is after it | `FEATURE_UNAVAILABLE` |
| N03 | source receives fresh verification today but CMC last settled market print older than allowed 72h | `BTCD_CMC_SETTLED_PRINT_STALE`, no eligible row |
| N04 | Shared Row display includes matching contract label but wrong SHA vs original Git source | monitor FAIL/NOT_ELIGIBLE, never counted |
| N05 | owner floor says Sep30 while frozen core prospective start Oct24 12:00Z | reject owner matrix |
| N06 | private repository original missing/inaccessible | `PRIVATE_DATA_AUTHORITY_UNAVAILABLE` |
| N07 | historical provider data revision uses today retrieval as 2025 first-known | research-only truth tape, no historic PIT |
| N08 | duplicate source/event/chain or two BTC/ETH horizons share the same shock | cluster/dependence count, never naive sum |
| N09 | no-issue, abstain, CENSORED or UNKNOWN removed from attempted denominator | ledger validation FAIL |
| N10 | outcome matured today without original issue or natural delivery | no action edge; partial info only if time proof |
| N11 | market quote known only after resolution (Polymarket) | reject odds/action feature |
| N12 | orderbook one-sided, crossed or fee unknown | no executable fill claim |
| N13 | liquidation instrument universe changes 5→800 | venue-comparable cohort split or REJECT aggregate |
| N14 | stablecoin bridge/mint and raw transfers treated as same inflow twice | reject aggregate deployment claim |
| N15 | HF pump.fun 69.09h outage or negative token age / unavailable reach at decision | fail affected feature/time admission, denominator retained |
| N16 | HF source mutable `resolve/main` switches between features, labels and split | reject unless same pinned revision and manifest digests |
| N17 | selection of usable predictors from held-out test distribution before train/holdout split | reject clean-OOS classification until training-only selection |
| N18 | source model pretrained after forecast era, marketed as contemporary historical original | classify counterfactual modern challenger, no original period forecast claim |
| N19 | duplicate news wire URLs/new timestamps after market move | one story family; no early novelty credit |
| N20 | falsely positive stock/crypto sentiment with irrelevant asset | reject/abstain and include false positive |
| N21 | source license non-commercial/restricted yet commercial/live rollout | licensing HOLD, zero deployment |
| N22 | 'predictive win' comes only from widening huge intervals | proper interval score + sharpness penalty exposes it |
| N23 | simple persistence wins but model reports standalone 87.5% range overlap | reject incremental-skill claim |
| N24 | 144 synthetic variants claimed as 144 backtests | classification FAIL: SYNTHETIC only |
| N25 | warning correctly describes a crash but first delivery after trough | no actionable pre-emptive utility |
| N26 | exit improves drawdown but fails to reenter before rebound | charge foregone upside, recompute net |
| N27 | microcap never had meaningful liquidity to fill at assumed bid | null/partial fills + slippage, not theoretical P&L |
| N28 | adverse move judged using surviving token list from after the event | universe as-of/delisting correction |
| N29 | one feature correlated with 4 others counted as 5 independent confirmations | ablation/dependency rejection |
| N30 | prospectively immature observation counted as model win/loss | PENDING/CENSORED proper treatment |
| N31 | Core/round3 data used before signed analysis gate | forbidden query, immediate STOP |
| N32 | positive outcome reported despite failed consumer readback | `POST_FIX_OBSERVATION`, not resolved |

Where an old test already exists, map the fixture to it instead of producing new files or running duplicated CI. Negative tests are admissibility checks, not tests of economic effectiveness.

## IV. Correct baselines and endpoints by family
**Direction:** previous issued market-packet sign, persistence/zero change, random with fixed seed, previous-bar momentum/reversal. Primary: balanced direction score and full confusion by class, conditional on *actual* issued original labels. Report all-attempt coverage, abstention, class base rates and confidence intervals. Use Brier/log loss only where a model actually emitted a probabilistic forecast of that outcome; do not manufacture probability from prose.
**Price bands:** no-lookahead ATR/recent realized-vol range, historical last-week fixed band, seasonal naive. Primary: valid proper interval loss and empirical containment at true intraday points; report band sharpness, center error, breach severity and regime. Jaccard weekly high/low overlap and X publication percentages are transparency/accountability metrics, not proof of economic edge.
**Rotation/altseason:** fixed cohort membership and universe known as-of issue; dumb equal-weight ex-BTC breadth, ETH/BTC persistence and BTC.D; predeclared phase labels/duration and survival criteria. Include fast bullish minority rotation that violates default ETF-era prior (F12) as required falsifier. A delayed hard gate may protect funds *and* miss the profit window.
**Macro/ETF/stables:** true source-release vintage, revision delay, provider observed time, independently timed spot movement; avoid 'ETF flow = direction' or 'stablecoin issue = deployment' simplifications.
**CFGI:** original first-known API observations, separate 2026 engine-era break, same-clock price/volatility controls; retrospective v3 retrieval of 2025 observations is not original 2025 issuance evidence.
**Pullback/distribution:** compare HOLD (holder) or WAIT (new cash), static partial risk ladder, existing protection policy and simulated tested challenger only after eligible original issue; proper event controls not only handpicked drawdowns. Annualize cautiously across short sample. Capture false negatives and late triggers, not only avoided drawdowns.
**News:** no-news, URL normalization/title dedup, simple lexical topic baseline, then embedding/sentiment model; count market-first, later wire pickup, publisher correction, false rumor, non-result articles, story clusters and latency.
**Alpha:** base rates over *entire eligible launch universe*, chain and timestamp differences, contract-address/publicity time, source/creator/wallet provenance; model graduation/exit impossibility and adverse risk, NOT 5x/10x achieved economic payoff without actual executable historical sale path.
**Polymarket:** matched market mid vs spot/volatility, fee/quote/latency and resolution bias controls; no replay outcome label in predictor feature.
**Model selection:** compare one transparent cheapest naive, one parsimonious asset-tailored rule and one advanced family per hypothesis. If advanced family fails, stop expanding variants. Research question must determine model size, not reverse.

## V. Four distinct score layers, no composite camouflage
1. `SOURCE_SCORE`: provenance and availability audit, independent of economic result.
2. `INFORMATION_SCORE`: original forecast versus cheap baseline, on admissible independent units, with coverage and uncertainty.
3. `ACTION_SCORE`: original first actionability, net fill and counterfactual after costs.
4. `OPERATIONAL_SCORE`: can workflow issue and consumer show the same frozen result with timely source and no silent fallback.
A win in one cannot silently imply another. Include negative, missing and no-action examples as separate explicit counts.

## VI. Uncertainty and anti-overfit
Before claiming superiority define a smallest meaningful economic/information effect, statistical decision criterion and evaluation budget, all approved by an existing owner. Require positive cohort size and number of **independent clusters**, not just raw candle rows. Use cluster resampling respecting time/venue/chain, two-sided uncertainty and sensitivity to dataset vintage; report multiple-testing family, not unadjusted best out of dozens. As preregistered model selection becomes adaptive, reserve an untouched prospective test lane. A pilot with 5–20 independent events is typically **exploratory**, not a scientific promotion, irrespective of p-value. Multi-regime generalization often impossible before observation accumulates: say `INSUFFICIENT_POWER` rather than producing a false ETA.

## VII. Decision loss and complexity price
Compare:
- costly **false positive**: whipsaw early entry, avoidable drawdown, liquidation exposure, delayed reentry after false warning;
- costly **false negative**: late deployment, missed fast rotation, missed recovery, excessive confirmation latency;
- **censoring**: unmatured outcome is pending, not proof/no-proof of profitability;
- **source risk**: missing or delayed native first-known;
- **complexity tax**: data acquisition, model inference, monitoring, feature drift, maintenance/incident rate, CPU/GPU and Actions/API spend.
Pair each new feature or model with an explicit incremental decision divergence. If it merely explains the past, classify `EXPLANATORY_ONLY` and do not add it to production.

## VIII. Candidate kill and promotion contracts
Before beginning every model or dataset pilot declare:
```yaml
candidate_id: ...
existing_owner: ...
hypothesis: ...
decision_that_could_change: ...
time_horizon: ...
smallest_meaningful_effect: ...
cheapest_matched_baseline: ...
eligible_original_issue_cohort: ...
independent_family_definition: ...
negative_controls: [...]
license_and_privacy_gate: ...
resource_ceiling: ...
falsifier: ...
kill_condition: ...
abstention_behavior: ...
prospective_freeze_required: true
first_review_trigger: ...
possible_evidence_state: SOURCE_ONLY | RESEARCH_ONLY | FORWARD_TEST
forbidden_actions: [PRODUCTION_PROMOTION, TRADE, SELF_MERGE, RETROSPECTIVE_REWRITE]
```
**Default disposition after pilot:** REJECT redundant complexity; SOURCE_ONLY if useful external context; DATA_BLOCKED if original source unavailable; FORWARD_TEST only after real scientific preflight and owner confirmation. No self-promotion.

## IX. Independent challenge panel
Independent technical critique must attempt to make one strongest positive claim fail, then do the converse for one unjustifiably defensive negative. Codex review of code catches implementation problems, but distinct model/chat identities do not by themselves create statistically independent forecasts or authorized GitHub approvals. Human owner/GitHub platform/review requirements remain as in current AGENTS. Before release, require exact-head source/CI/reviews and later consumer evidence. Keep Research Lab minority/falsifying view visible in terminal report.
