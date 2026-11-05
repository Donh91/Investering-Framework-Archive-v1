# PRZM and peer-platform edge transfer | 2026-11-05

**Status:** RESEARCH_ONLY / SOURCE-COMPARED / DEDUP-FIRST / NO VERIFIED NEW EDGE.  
**Authority:** No live thresholds, Compass/CN changes, new agents, API spend, autonomous trades, subscriptions or new data engines.  
**Canonical owner:** Research Lab #1512, machine queue QUEUE_V1.json; Strategist #1157 adjudicates, S1 #1156 routes bounded existing-owner implementation. No displacement of production P0.

## Decision question
Do options-flow platforms contain reproducible mechanisms that improve crypto pullback early warning, re-entry decisions, altseason/distribution detection, or the economic accountability of the existing Compass? Accept a primitive only if it adds measurable information/decision value over matched frozen same-clock baselines. UX inspiration is not trading edge.

## Platform comparison from primary vendor sources, 5 Nov 2026
| Platform | Observed mechanism | Transfer to framework | Caution |
| --- | --- | --- | --- |
| PRZM https://www.przm.space/landing and https://www.przm.space/upgrade | Live US options tape, noise-filtered conviction versus price, flow / intercept / optics / afterburner / moonshots, dealer exposure, public graded-call scoreboard | Filter hedges and fake conviction before calling flow informative; grade all calls, including misses | Proprietary performance/denominator not independently audited; US equity options not crypto tape. Earlier conversation mentioned Ghost and ZERO, but these are not substantiated on presently verified PRZM pages, so exclude them. |
| Tradytics https://tradytics.com/ and https://tradytics.com/docs/mcp-tools | OPRA print details, 0DTE, gamma, FINRA darkpool, trade idea timelines, API/MCP | Publication-timestamp provenance, paired flow vs simple price comparisons | Vendor Pro API ~$69/month; no purchase authorized; fills on bid/ask do not prove opening informed direction. |
| Unusual Whales https://unusualwhales.com/public-api | OPRA options, GEX, dark pool, REST/WebSocket/MCP | Independent US options data challenger | Vendor API Basic ~$150/month; estimated dealer positioning is not observed dealer book. |
| OptionStrat https://optionstrat.com/features | Saved paper positions, drawdowns and historical path / max gain and loss | Transparent signal follow-through and shadow economics UI | Paper records and historical marks are not proof of executable trading. |
| CoinGlass https://docs.coinglass.com/reference/getting-started-with-your-api | Crypto-native OI, funding, liquidations, ETF, market structure and spot/order book | Existing crypto derivatives crowding / spot-vs-leverage separation | Actual historical endpoint, license, first-known timestamp, API and cost not yet admitted. |
| Laevitas https://docs.laevitas.ch/options/analytic and https://docs.laevitas.ch/options/historical | BTC/ETH options skew, IV, expiry/gamma, OI, risk reversals | Crypto options stress as an independent candidate feature | Enterprise-key requirements documented; free API access not assumed. |
| Deribit https://support.deribit.com/hc/en-us/articles/38507223482781-API-guidance and https://statics.deribit.com/files/DeribitInstitutionalSetupGuide.pdf | First-party options trade/market data, documented historical endpoints | Low-dependency source feasibility audit before external spend | Verify timestamp clocks, availability, coverage, pagination, terms, rate limits. |
| NautilusTrader https://nautilustrader.io/open-source/ | Event-driven deterministic replay, realistic fill/fee/latency models | Benchmark existing simulator semantics, NOT install a second engine | Already listed in existing archive open-source trading stack landscape. |

These are vendor descriptions, not proof of predictive or economic edge. No copyrighted source code or paywalled tape ingestion. Verify platform and data licenses.

## Fresh archive overlap, do not reimplement
- Research Lab QUEUE_V1.json already defines S5_DERIVATIVES_CROWDING_TO_PULLBACK_V1, baseline MERGED / prospective grading pending, PR #1515 and original #1514.
- Historical 60d/60min cross-venue funding, OI, taker, depth, liquidation gap belongs to #387. Missing history is UNKNOWN, not permission to invent backfill.
- Same-clock Task 2 PIT audits, forecast/decision counterfactuals and correlated-signal ablations belong to #1596. First-known failures and independent-episode counting limit current edge claims.
- Adaptive Evolution and all-experiment accountability already belong to #1157. AUTO_TRADING proposal-time denominator belongs to #1557. CN scorecards, Entry Signal Ledger and Shadow Registry already exist.
- Full-cycle pullback/re-entry and altseason takeoff-to-distribution scope already belongs to #1918. ETH visual analogue/fractal study belongs to #1881, separate from this microstructure source assessment.
- Nautilus and broader open-source trading tooling already assessed at 04_RESEARCH_LAB/auto_trading/OPEN_SOURCE_TRADING_STACK_LANDSCAPE_2026-09-12.md.

## Ordered, falsifiable tasks, routed only to existing owners

### H1 P0 | Economic Decision Replay and Denominator Delta | #1596 + #1157 + #1557
Research problem: Does original Kompas action BUY/SELL/HOLD/WAIT/ABSTAIN improve terminal wealth or avoid drawdown over matched HOLD/price-only/volatility baselines AFTER friction, rather than merely get direction right?
- Begin with a fresh immutable source/receipt field census, identify ONE actually missing deterministic join/fixture. Deduplicate existing scoreboard implementation. If already complete, return CLEAN_NOOP with proof.
- Match each valid as-of issuance to exact first-known publication clock, policy/model SHA, market venue, price and action horizon. Count invalid, rejected, aborted, stale, missing, censored and repeated warnings; overlapping alerts count as one economic episode. No historical chat reconstruction as prospective rows.
- Pre-register primary paired endpoint as incremental net terminal wealth per independent episode versus same-clock HOLD. Secondary metrics: 1/3/7/14/30d forward and action coverage, drawdown avoided, false exits and missed upside; next executable bar fills plus spread, fee, slippage, realistic capacity. Tax only as clearly labelled scenario, not fabricated personal rate.
- Negative controls: same-clock momentum/range, shuffled signal, repeated alerts and frozen version; causal availability > cutoff blocks admission.
- Admission: valid independent prospective denominator, fixed baseline and costs. Fail closed on missing first-known; no live portfolio rule promotion.

### H2 P1 | Crypto Crowd-Flow versus Price Ablation | existing S5 #1514, #387, #1596, #1918
Research problem: Do lagged funding+OI, directional spot taker flow, cross-venue positioning, or liquidation pressure identify *earlier* pullback/reclaim/late distribution beyond price-only and currently merged S5?
- First read existing S5 output, effective baseline, schema, 60m/60d source coverage and first-known clock. FREE/retained venue-native sources before vendor APIs. Missing history stays UNKNOWN.
- Freeze one limited BTC/ETH trial with 4h/24h/72h decision clocks and 1/3/7d economic outcome. Distinct episode families and pre/post ETF regimes are reported separately. Include healthy pullback, second flush, failed reclaim, bull trap and euphoric continuation failure as conditions, not ex-post-selected targets.
- Paired ablations B0 price+volatility, B1 existing S5, B2 S5+single orthogonal spot/leverage divergence. Match same eligible timestamps and sources; measure earliest verified warning, false alarms, missed pumps and after-cost hold versus risk reduction.
- Do not triple-count correlated funding, OI and liquidations as separate confirming votes. Negative outcome or missing independent N -> no signal authority.
- First concrete deliverable: exact source-clock/eligibility matrix and a single small unambiguous repair or preregistered ablation, not a new collector.

### H3 P2 CONDITIONAL | BTC/ETH options skew / expiry / GEX challenger | S5 #1514
Only after H2 finds a genuine residual information gap and Deribit first-party free data is independently source-eligible. Compare B0 price, B1 S5 perps, B2 + options skew/expiry on equal 24h, 3d, 7d windows, expiry-week/regime splits. GEX is an estimate. Laevitas/CoinGlass access requires explicit contract/cost proof, zero unapproved spend. If not eligible, SOURCE_BLOCKED_WITH_TRIGGER.

### H4 P3 EXPERIMENTAL | SPY/QQQ options risk appetite for BTC/ETH | S5 + Macro Shadow
Only if 3+ months of legally reusable, genuinely PIT-known same-clock US options data are accessible without new spend, and H2/H3 are lower expected VOI. Test against SPY/QQQ price, VIX/volatility, BTC price, US market-open session/calendar and crypto overnight/weekends. US options/darkpool reporting delays must be enforced. Reject if lag destroys lead or effect is equity-beta only. Never buy PRZM or US options API speculatively.

### H5 P3 PRODUCT | Anti-cherry-pick evidence presentation | #1157 / existing CN scorecards
Only after H1 yields eligible complete rows. Read-only drilldown with fixed sample/coverage, first-known SHA, rejected signals, no-edge/HOLD, pending outcomes, costs, missed upside, false exits, drawdown and reasons for research kill. Do not build a new Compass/site view in the current mission.

## Queue and completion rules
1. Record this as a METHOD_ONLY child of existing #1512 and S5, without changing the current heavy-lane ordering or opening multiple new PRs.
2. Strategist #1157 selects EXACTLY one verdict per H family: DEDUPED_TO_EXISTING_OWNER, FORWARD_TEST_PREREGISTERED, SOURCE_BLOCKED_WITH_TRIGGER, REJECTED_FALSIFIED, or NOT_DECISION_USEFUL.
3. S1 #1156 routes at most one minimal existing-owner verified source repair/experiment within production P0 and concurrent handoff limits. Comment/queue entry is NOT execution, and new paid API, Work, Codex or subscriptions require existing budget/authority gates.
4. Require exact data rows/source hashes, initial immutable clock, licensed availability, de-duplication, control comparability, frozen criteria, reproducible tests and independent review. No effective N from repeated hourly alerts or overlapping horizons.
5. End after one source census + one bounded preregistered experiment, with explicit terminal close or prospective observation trigger; keep failed tests.
6. No source code from vendors. No autonomous trading, threshold/rule promotion, canonical forecast changes, site deployment, new cron, or duplicate owner.

**Initial decision:** H1 and H2 are relevant but extensions of EXISTING open work. H3 is conditional, H4 and H5 are deferred. PRZM is a design benchmark, NOT an independently verified edge input.
