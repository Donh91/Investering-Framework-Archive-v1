# Onchain Options x REA — adoption, value-capture and derivative challenger (2026-11-01)

**Classification:** RESEARCH_ONLY / SHADOW / PREREGISTRATION + SOURCE_FEASIBILITY_PASS / NOT_AN_ACTIVE_FORWARD_TEST  
**Owner:** existing External Specialist Dissection #1512, **S10** Protocol Value Capture (primary) and **S5** Derivatives Crowding to Pullback (conditional). **REA** is bounded product-claim verification within existing Meme Alpha Lab research, NOT a new engine.  
**No authority:** no canonical market state, Compass, Task2, thresholds, BUY/SELL, token promotion, token-ranking system, scheduled data collection, paid source, workflow, secret or production integration.

## Executive decision

The original "does onchain options volume predict token returns?" experiment is too broad, susceptible to selection bias and has poor claim-to-value linkage. Adopt a **two-lane qualification** instead:

1. **Primary S10/REA, adoption-to-cashflow-to-tokenholder reality:** Test whether sustained, options-only premium activity becomes attributable protocol fees/revenue and economically enforceable tokenholder benefit. A protocol with growing headline notional and no net value capture is a falsifying case, not a winner.
2. **Secondary S5 options challengers:** Only after existing S5 spot/futures/OI/funding baseline has prospective mature outcomes, test whether options observations add incremental pullback information. Do not relabel onchain options market share, cumulative premium or generic OI as GEX, put skew, or a directional early warning.

The same source may supply descriptive data for both, but **claims and outcomes remain separate**. Task2 and Kompas Pro remain untouched. This is not an Alpha Lab meme new-launch signal.

## Sources examined on 2026-11-01 (source metadata, not immutable first-known history)

- [Momilio article (2026-10-26)](https://x.com/momilio/status/2114749296142626820): "The Biggest Opportunity In Crypto", explicitly a promotional/excerpt thesis on future distribution of retail onchain options. Historical TradFi adoption is **not** evidence of future onchain token returns. Author also owns/promotes dashboard.
- [onchaingreeks dashboard](https://www.onchaingreeks.xyz/) and [methodology](https://www.onchaingreeks.xyz/methodology): venue-level options-only premium, notional, OI, trade tape, underlying split, RFQ execution and vault TVL. Dashboard observation ~USD 73.94m 30d premium, USD 4.063bn 30d notional, ~89.4% Derive premium share and onchain/Deribit 30d notional ~6.8% **as displayed at inspection**, not frozen trading evidence. October premium down ~6.5% vs September; article bullishness is not an observed acceleration. **Source risk:** Derive v3 migration 2026-10-06 changed historical aggregation; early Aevo token-incentive periods inflated; Rysk vault seller premiums differ from two-sided exchange trade volumes; CallPut/Dream scope varies; headline venue denominator is not a stable underlying asset cohort.
- [DefiLlama free API docs](https://api-docs.defillama.com/), [options](https://defillama.com/options) and [Derive V3](https://defillama.com/protocol/derive-v3-options): documented no-key public \`/overview/options\`, \`/summary/options/{protocol}\` and fee/revenue endpoints. A bounded public endpoint probe of \`https://api.llama.fi/summary/options/derive-v3-options?dataType=dailyPremiumVolume\` returned dated historical options-volume JSON structure. Fee endpoint \`https://api.llama.fi/summary/fees/derive-v3-options\` exposed fee/revenue methodology (source response not independently verified for all historical rows). Do not interpret a successful response as stable long-term access, schema, cost/terms permission or timestamp-qualified PIT. Read/confirm public API usage terms before future automated collection.
- [Derive V3 fees/holders methodology](https://defillama.com/protocol/derive-v3-options): options trading fees can be attributable; **DRV buybacks/holders revenue are derived from ALL Derive markets**, including perps/spot, not solely options. **Do not divide cross-product holders revenue by options-only volume and call it options tokenholder capture.** A token-buyback benefit to treasury is not the same as directly distributable tokenholder cashflow. v2 and v3 data can overlap/move across adapters.
- [Existing S5 spec](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/04_RESEARCH_LAB/external_specialist_dissection/S5_DERIVATIVES_CROWDING_TO_PULLBACK_V1.md); [S5 queue](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json); [Pullback Forensics](https://github.com/Donh91/Investering-Framework-Archive-v1/blob/main/research/pullback_forensics/PULLBACK_FORENSICS_PASSIVE_PILOT_v1.md): existing owner has Deribit exchange-native moneyness-skew rider (NOT 25-delta); S5 already owns first-party spot/futures/oi/funding feature and M6 outcome horizons. Existing queue explicitly says to add options only after baseline can be graded.
- [Existing REA meaning](https://github.com/Donh91/Meme-Alpha-Lab/blob/main/research/discovery/ALLIUM_ALPHA_REA_DEEP_RESEARCH_DECISION_2026-10-13.md): bounded project/product claims and differential evidence, not an autonomous signal service.

**Source disagreement is an important finding:** OnchainGreeks, DefiLlama and venue-native data use differing scopes for OI, premium, v2/v3, vault collateral and fee attribution. Reconciliation must be unit/scope/epoch-aware; agreement between reaggregators using the same upstream does not count as independent verification.

## Targeted candidate algorithms (descriptive, NO composite score)

All measurements require a \`decision_cutoff_utc\` and distinct \`source_available_at_utc\` (real first-known if available, else mark unavailable). Enforce one completed UTC venue/day, options-only source qualification, deduped trades and stable adapter epoch. Never forward-fill unavailable as zero.

**A. Cash premium growth**: 7 complete UTC days' options-only cash premium / the preceding comparable 7 complete days, minus 1. Cross-check 14/30-day persistence, negative periods, source changes and new listings. Notional growth is secondary and does not measure cash deployment.

**B. Premium conversion and market concentration**: 7d premium / 7d notional, same product/venue/period; cash premium venue share and HHI from a declared *complete* venue census. These are mix descriptors, not product-margins, price forecasts or "institutional positioning" by themselves.

**C. Options activity to actual revenue**: compare per-venue options-only \`fees/premium\`, net options revenue and fee retention with source-scope matches. For mixed spot/perp/options fee fields report \`SCOPE_MISMATCH\`; for maker rebates/incentives subtract verified incentive costs or leave \`UNKNOWN\`. A visible trade or vault TVL is not necessarily an active organic distinct user.

**D. Tokenholder economic reality (REA)**: trace \`product claim -> deployed app/contract -> public options tape -> attributable option fees -> net revenue -> buybacks/burns/distributions -> legally/economically substantiated tokenholder effect\`. Freeze proof at every step and separate \`ONCHAIN_TRANSFER\`, \`TREASURY_BUYBACK\`, \`DIRECT_TOKENHOLDER_PAYMENT\`, \`CLAIM_ONLY\`, \`UNAVAILABLE\`. Include circulating dilution/unlocks, total supply, governance controls, treasury restrictions and value leakage. Never infer positive token-return beta from fee growth alone.

**E. Optional S5 derivatives challenger**: compare venue-native Deribit moneyness/skew/OI/funding baseline against separately reconstructed onchain trade-side/expiry/strike distributions, **only if** trade direction, counterparty, expiry and first-known timestamps are separately validated. Do not infer net bullish demand from a displayed "Buy Call" without trade context, open/close inventory or hedging; do not label calculated options HHI as gamma. No GEX/IV signal from aggregate dashboard totals.

## Pre-registered falsification and measurement (not activated)

**H-REA-01 (primary):** sustained attributable premium and net fees distinguish sustainable options platforms better than headline notional. Compare to (1) notional-only, (2) raw premium only, (3) simple fees alone and (4) sector/market beta. Outcome: subsequent 7/14/30d *net fees and revenue persistence* first; token returns after fees/slippage/dilution only in a later separately admitted investment test. Include fallen/closed/incentivized platforms and unrewarded periods. No selective hindsight examples.

**H-REA-02 (conditional):** source-qualified economically enforceable tokenholder capture improves cross-issuer ranking beyond protocol usage alone. Requires identity mapping, attributable supply and treasury accounting; else \`NOT_MEASURABLE\`.

**H-S5-OPTIONS-01 (conditional):** time-qualified option flow/expiry structure improves M6 24h,72h,7d,14d,30d MAE, forecast discrimination or warning lead-time over price/OI/funding/full S5 vector. Predefine exact counterpart baselines and event clusters. Grade only after S5 base prospective outcomes mature. Do not claim edge from in-sample fitting.

**Metrics:** coverage/clock admission, eligible opportunity denominator, source lineage, lead/lag, skipped/UNKNOWN rate, matched-control incremental lift, PR-AUC/Brier or log-loss when probabilistic predictions are preregistered, false positives, false negatives, estimated fees/slippage and opportunity cost. Bootstrap by independent market episode and hold out later time blocks; do not count repeated hours or correlated derivatives snapshots as independent observations.

**Promotion:** no automatic score. \`SOURCE_QUALIFIED\` requires recorded raw endpoint schema, coverage, terms, API access, availability clock and independent source reconciliation. \`READY_FOR_FORWARD\` additionally requires matched eligible assets and an immutable prospective contract. \`TESTABLE_EDGE\` requires mature, non-overlapping outcomes and predeclared comparison. Current state: **SOURCE_FEASIBILITY_PARTIAL / METHOD_PROTOTYPE_ONLY / PROSPECTIVE_ROWS=0 / EDGE_UNTESTED**.

**Kill/defer:** unusable licensing/free API; mismatched v2/v3 product epochs; absent true availability timestamps; positive usage but no token capture; insufficient eligible events, source concentration, incentive distortion; no incremental prediction against simpler baselines; duplication of an existing S5/S10/REA owner.

## Deterministic minimal prototype delivered in this branch

- \`onchain_options_2026_11/sector_metrics.py\`: pure-source-agnostic calculators for 14 settled days' premium growth, premium/notional, strictly scope-qualified fees/premium and full-census same-day premium HHI. Fail-closed on missing, duplicate, future-known, unfinalized or non-option rows. No network, API, token-price or scheduled calls.
- \`onchain_options_2026_11/test_sector_metrics.py\`: synthetic negative controls. These establish mechanics, **not live data correctness or predictive value**.

Suggested local test (no external spending):
\`\`\`bash
python -m unittest discover -s 04_RESEARCH_LAB/external_specialist_dissection/onchain_options_2026_11 -p 'test_sector_metrics.py' -v
\`\`\`

## Next bounded existing-owner actions

1. REA/S10 owner qualifies exactly 2–3 historical providers (Derive V3, Aevo, optionally Rysk) for options-only premium and fee scope; source reconciliation is done before adding tokens. Preserve v2/v3 discontinuity and incentive flags.
2. Only when permitted and reusable, use **existing** data capture path and restricted data plane for any raw/normalized restricted provider rows. No new scheduled workflow or API spend. Preregister event time, first-known vs retrieved, token eligibility, fee alignment and full denominator.
3. Keep S5 optional until first-party spot/futures baseline and M6 outcomes can show independent episodes. No crossover into Task2 / Compass PRO before independent governed qualification.
4. Give Research Lab #1512 a single indexed source/method pointer. Do **not** re-rank its already higher priority S1/S2/S3/S4 tasks or reopen a duplicate owner.

**Actual completed now:** source/methodology/owner audit and bounded public endpoint feasibility probe; fail-closed research calculator and synthetic checks proposed in PR. **Not completed:** production data acquisition, 90d source reconciliation, historical backtest, forward data capture, economic edge validation.
