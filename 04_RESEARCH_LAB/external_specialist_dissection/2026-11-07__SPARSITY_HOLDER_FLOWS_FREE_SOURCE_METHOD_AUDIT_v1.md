# Sparsity Research + public/free source methods: Alpha Lab intake v1

Date: 2026-11-07. **Owner:** existing [External Specialist Dissection #1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512) and existing Alpha Lab S2/S3/S4/S6/S7 research owners. **Class:** PUBLIC-ONLY, RESEARCH-ONLY, SOURCE QA AND METHODS, NO EMPIRICAL ALPHA. **User authorization:** deep research and evidence-backed GitHub logging, without subscriptions, new automations, extra owners or real trading.

Repo-local Research Parallel Lanes v1 was used in **mode A**, independent read-only public source requests were made concurrently inside one coordinating chat. No separate AI agent, GitHub Actions research job, full-chain replay, actual forward test, new code execution, or model change occurred.

## Decision

Sparsity is relevant as a **specialist inspiration** for entity-adjusted holder resilience, trade-origin whale flows and drawdown-recovery sequencing. Its finished index, scores, rankings, exact weightings and UI do **not** become Alpha Lab inputs. New predictive value is unproven. Existing S3, S4, S6 and S7 cover adjacent methods, so choose at most one minimal original-data challenger after a duplication audit.

**License firewall:** [Sparsity legal terms](https://sparsitydata.com/terms) permit ordinary reading, links and small attributed quotations/screenshots; expressly forbid bulk copying/scraping or building datasets, models or products from their text/scores/readings without written permission. No site-data collector, score scraper, replicated proprietary scoring model or training data import is authorized. Publicly explained generic research questions may instead be implemented independently from authorized **raw chain data, public contract ABIs and separately licensed APIs**, without copying Sparsity's outputs or proprietary weighting scheme. No provider dataset is copied into this report.

## Five source-audited research lanes and findings

### L01: Holder cohort resilience and concentration

Primary: [Sparsity holder-strength methodology](https://sparsitydata.com/holderstrength) and [example coin metric explanations](https://sparsitydata.com/coins/PONS).

Vendor describes concepts including supply continuity, drawdown survivors, full-portfolio concentration, active holder growth, whale accumulation, dip absorption, liquidity depth and chain/launchpad-relative returns. It publishes daily after the previous completed day, with different handling for coins too young for some components. Classification of contracts, pools, exchanges, burns, custody and automation is provider-derived and not chain-ground truth.

**Our independent candidate: PRE-DRAWDOWN_ENTITY_RETENTION.** At an eligible time t0, freeze the holders and funding clusters then known; track how much of their token inventory persists through a subsequent drawdown. Preserve all t0 wallets, including every wallet which sold to zero. Compare raw wallet count, retained supply, independent-entity count, entity-adjusted concentration, early-buy retention and the existing S3/S4 baseline. Distinguish intermittent snapshot holdings from uninterrupted lot-level tenure; a sell-and-rebuy between two snapshots must not be counted as unbroken holding. Exclude source-proven pool/router/CEX/bridge/burn infrastructure, but do not infer common ownership from shared exchange funding alone.

**New risk:** Selecting today's surviving holders and retrospectively counting the drawdowns they survived is a **survivor-conditioned history**, not proof a signal was known before those drawdowns. High holder commitment also may mean trapped illiquid supply, project treasury ownership or inadequate exit routes. “Full-portfolio conviction” can only be estimated if cross-chain wallet holdings/price coverage and missingness are recorded; one chain's balances cannot support a universal portfolio attribution.

**Falsifier:** no out-of-time after-cost improvement beyond existing age/liquidity, S3 entity-adjusted concentration and S4 buyer-retention baselines, or collapse under entity/dust/airdrop sensitivity checks. No new smart-wallet score.

### L02: Whale/shark/retail net DEX flows

Primary: [Sparsity net flows](https://sparsitydata.com/flows).

Vendor defines participant categories using their same-token holdings **at the beginning OR the end of each week, whichever is larger**, and sums buy-minus-sell quote value from chosen main liquidity pools; untracked pools and missing history are explicitly excluded.

**Key finding:** End-of-week balance used to classify a trade earlier in that week would introduce FUTURE DATA into intraperiod prediction. Our research must independently freeze cohort membership from the last known pre-trade or pre-window balance, and must not relabel an earlier trade based on its owner's later price gains or accumulated tokens.

Original candidate: independently classify self-initiated DEX swaps using original transaction logs and router/pool/LP semantics, not ERC-20 transfers alone. Compare quote-valued net flows across pre-frozen entity/holding cohorts; preserve market-maker and bot unknowns, pool coverage %, bridge routes and slippage. Incoming wallet transfers, LP withdrawals and airdrops are not economically proven market buys. Large outbound transfers are not confirmed sales.

**Baseline:** existing S6 distribution/egress and S3/S4 wallet-forensics, plus simple price/volume and liquidity. **Falsifier:** apparent gains vanish when cohort labels cannot depend on week-end holdings, when wash/router/LP activity is removed, or when source pools are broadened.

### L03: Drawdown recovery and bottoming

Primary: [Sparsity bottoming test](https://sparsitydata.com/bottoming). The public explanation uses three ordered observations: holders realizing losses, a low continuing to hold, then increased buyer participation/new wallet demand. Source says Dune trades and available cost bases in its covered main pools; a coin can be excluded for insufficient cost-basis coverage. These are vendor method claims, not validated forecasts.

Our independent method is an event-time-safe research state machine: drawdown eligibility defined using an **as-of rolling high and observed rolling low only**; evidence of real seller losses with known pre-sale acquisition cost and a coverage denominator; stability measured without hindsight about the final trough; independently identified demand recovery with buy-actor and liquidity coverage. Record step-onset UTC, first-seen availability and nontransitions. Include dead tokens, rugs, halted pools and assets missing mature +72h/+7d outcomes as negatives/censored, never only the coins on today's bottom map.

**Risk:** cross-venue or bridged inventory may have unknown cost basis; missing cost basis is UNKNOWN, not “seller broke even.” A current bottom-sign map excludes non-drawdowns, which cannot be treated as an unbiased whole-universe model sample.

**Baseline:** existing G2/M6 pullback, price/volume, executable liquidity and S4 retention. **Falsifier:** no added false-bottom rejection or improved executable after-cost return versus simple price/liquidity stabilization, or missing cost-basis coverage dominates.

### L04: Cross-chain participation regime

Primary: [Sparsity sentiment](https://sparsitydata.com/sentiment) and [heatmap](https://sparsitydata.com/heatmap). Chain-specific activity uses launchpad trade counts, launch supply, trading bot fees and holder activity. The vendor itself notes that the **holder component entered its historical sentiment series only on 2026-09-27**; earlier values use a different construction.

Our original candidate: separate chain-normalized participation intensity (trade flow / launch count / fees) from directional demand (independent retained buyers), using independent historic baselines and explicit launchpad/factory regime changes. Compare it against current S7 attention-conversion and Altseason breadth. Avoid joining a composite with a structural definition break as though it were homogeneous. Bots fees and intense activity can signal panic/MEV, not bullishness.

**Falsifier:** no incremental lead over existing cross-chain breadth after correcting factory migration, low-liquidity regimes, BTC market beta and selection effects.

### L05: Public/free source feasibility and similar specialists

| Source | Official evidence | Honest free/rights classification | Owner use |
|---|---|---|---|
| Raw chain + verified ABI and historical snapshots | First-party ledger, token events, trade traces | Publicly inspectable, free access quotas/archive node costs not guaranteed | Primary; reuse existing collector/indexer, not a second engine |
| [DEX Screener API](https://docs.dexscreener.com/api/reference) | Pair/pool market details; documented endpoint groups at 60 or 300 rpm | Free public endpoints with documented rate caps; check terms and storage before adapter | Existing price/liquidity/visibility source; not on-chain wallet ledger |
| [GeckoTerminal Public API](https://apiguide.geckoterminal.com/) | Pools, market data, OHLCV; public beta | Public free API, attribution/version/rate and historical depth must be verified | Compare independently with DexScreener |
| [Crius holder documentation](https://docs.crius.sh/reference/holders/) | Robinhood-chain holder snapshots at timestamp/block on Free credit tier; cohorts on Starter | Free-credit bounded, Robinhood-only; cannot assert unlimited no-cost automation | Optional exact-block QA challenger, no subscription |
| [Kendu Conviction API](https://kenduconviction.com/developers) | Holder ages, balances, transfers, pool activity, historical snapshots and chain-level hashes; only KENDU | Explicit **CC BY 4.0**, free incl. commercial with credit | Strong *independent dataset and provenance* reference / QA fixture, single-token limitation |
| [Dune rate limits](https://docs.dune.com/api-reference/overview/rate-limits) | Public query UI and indexed chain analytical methods | As of this audit, **Free = view-only; API not available without paid plan/trial** | Human/public research references only; no free production API dependency |
| [Bitquery free guide](https://bitquery.io/blog/how-to-conduct-blockchain-analysis-for-free) | Free explorer but time-limited API trial, paid long-history | Free exploration != recurring free data feed | Targeted manual cross-check only |
| [DefiLlama API](https://api-docs.defillama.com/) | Public protocol/DEX/stablecoin aggregate context | Select free endpoints, not full per-wallet holdings | Macro/liquidity context only |
| [GMGN MIT code](https://github.com/GMGNAI/gmgn-skills) | Public wallet/holder-analysis methodology implementation | MIT applies to repository code, not blanket hosted-data rights | Already existing S2 wallet-skill owner; no duplicate |
| [HoldTech MIT project](https://github.com/co-numina/holdtech) | Public holder clustering and bundling code candidate | MIT repository, but Helius API + deployment and paid hosted features separate | Lower-priority S3 source-code method check, not a trusted label |

**Free means distinct things:** public UI, open source code, trial credits, free API tier, CC-licensed data and unlimited raw chain availability are not interchangeable. Dune API is particularly NOT a perpetual free source, and Crius Free credits do not imply free unlimited historical collection. No purchased provider access, wallet signing or production API changes were performed.

## Cross-source risks that can produce false alpha

1. **Lookahead:** same-week ending balance used for prior trade's whale cohort, current universe used historically, or future trough used to call a bottom.
2. **Survivorship:** today's 69 selected index coins are not the denominator of all original launches, bankrupt projects, delistings and rug outcomes. Rebuild the original eligible universe from as-of sources.
3. **Clock mismatch:** source event, blockchain block, first-publication, received-by-collector and generated-report times differ. Different Sparsity modules can update on different schedules.
4. **Cohort and entity ambiguity:** one controller can split wallets; exchange/bridge address overlap does not prove same owner; Safe and ERC-4337 can be genuine holders.
5. **Fake demand from transfers:** self-custody movements, LP adjustments, token rewards, airdrops, wash trades or changes in token USD price are not buy demand.
6. **Missing metric semantics:** young coins are scored on available subsets. Treat unavailable data as UNKNOWN with a metric coverage vector, not good or bad.
7. **Trapped holder bias:** holdings that do not move may be untradeable, treasury-controlled or underwater, not bullish “conviction.”
8. **Attribution/cost:** sold token cost basis is often unknown; high activity does not establish realized profit; DEX costs must be measured at executable notional.
9. **Comparability:** a change in vendor definition or chain universe invalidates unadjusted historical comparisons. Sparsity changed sentiment composition 2026-09-27.
10. **Data license:** a free dashboard does not grant model-building rights. Sparsity's terms are a HARD NO for copying model-input scores absent written permission.

## One minimal existing-owner experiment (NOT launched)

**Primary incremental hypothesis:** ENTITY_ADJUSTED_DRAWDOWN_HOLDER_RESILIENCE_CHALLENGER_V1.

**Owner:** existing S3 entity-adjusted holder/cluster and S4 early buyer retention, under Archive #1512 and MAL #1087/#1134. No new source scanner, research owner, schedule, index or wallet-score pipeline.

**Frozen sample:** same-chain/factory/age/market-cap/liquidity matched eligible tokens in the *original observed discovery stream*, including failures, delisted and zero-liquidity outcomes. Fixed original cutoff t0, and no feature learned from any point after t0. Preserve full denominator and data-health status, with explicit UNKNOWN and censored outcomes.

**Challenger:** one original raw-chain derived, auditable holder cohort survival delta under a known preceding drawdown. Separate entity-adjusted retention, continuous holder tenure, excluded-wallet count and coverage uncertainty. Self-initiated DEX buyer and LP/sellability proof required before any strength claim.

**Controls:** original G2+S3+S4 without proposed new feature; age/chain/factory/cap/liquidity controls, plus a cheap price/volume-only comparator. For channel separation, split wallet held supply and qualified quote-flow features rather than copying one opaque score. Preregister test window, join keys, missingness rules and thresholds before reading outcomes.

**Outcomes:** +15m, +1h, +6h, +24h, +72h, +7d where genuinely mature, executable sellable return after gas/taxes/slippage at frozen notional, MAE/MFE, risk rejection precision/false negatives and operational/compute cost. Hold out time and correlated token/creator clusters; never score immature or restricted Round 3 results.

**Accept:** source provenance + complete cohort denominator + no future contamination + robust out-of-time economic benefit over incumbent and no critical evidence loss. **Kill:** zero incremental utility, repeated source gaps, unverifiable wallet independence, $0 budget infeasibility, materially worse false negatives or hidden license dependency. No numeric lift threshold or signal weight is approved here.

## Disposition / owner routing

- **SOURCE_ONLY:** Sparsity method descriptions, not data/product access.
- **DEDUPED_TO_EXISTING_OWNER:** holder survival to S3/S4; flows to S6; chain regime to S7; known wallet-skill source to S2. At most one original small challenger under S3/S4 if owner and Strategist adjudicate delta.
- **SOURCE_BLOCKED_WITH_TRIGGER:** Sparsity data ingestion until documented written permission; Dune automated API until genuinely $0 perpetual terms; any paid hosted holder cohort endpoint.
- **NO_CHANGE:** Keep existing canonical external specialist queue's current next action FIRST_FORWARD_PONS_BUYER_QUALITY_CASE_V1. Do not displace existing high priority P0, upgrade a model, generate BUY/SELL or assert backtested edge.
- **NEXT AUTHORIZED GATE:** Strategist #1157 assesses whether existing S3/S4 already cover the delta, and route a bounded preregistered independent raw-chain test only with current source coverage/cost proof and normal CI/release. Until then retain this negative/positive learning as research record.

## Verifiable primary source registry (public official links checked 2026-11-07)

Sparsity: https://sparsitydata.com/ ; https://sparsitydata.com/holderstrength ; https://sparsitydata.com/flows ; https://sparsitydata.com/bottoming ; https://sparsitydata.com/sentiment ; https://sparsitydata.com/heatmap ; https://sparsitydata.com/coins/PONS ; https://sparsitydata.com/research ; https://sparsitydata.com/terms .

Public comparators: https://docs.dune.com/api-reference/overview/rate-limits ; https://docs.dexscreener.com/api/reference ; https://apiguide.geckoterminal.com/ ; https://docs.crius.sh/reference/holders/ ; https://kenduconviction.com/developers ; https://api-docs.defillama.com/ ; https://bitquery.io/blog/how-to-conduct-blockchain-analysis-for-free ; https://github.com/GMGNAI/gmgn-skills ; https://github.com/co-numina/holdtech .

Existing internal owners: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512 ; https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1134 ; https://github.com/Donh91/Meme-Alpha-Lab/blob/main/architecture/EXTERNAL_SPECIALIST_DISSECTION_V1.md .

**Actual research result:** public methodology/source-rights audit completed; predictive edge, statistical uplift, exact production data cost and full historical reconstruction remain UNKNOWN / NOT EXECUTED.
