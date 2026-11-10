# INDEPENDENT EXECUTION ALPHA ATLAS v1.0
Owner-authorized research archive, 2026-11-10. Research-only, public-safe method/source pointers, no canonical market/portfolio or automatic execution authority.

## Owner decision and exact scope
Mission: extract maximum zero-incremental-cost, reproducible microcap execution knowledge from 0x.org as inspiration, but primarily from first-party public Pons V2, Uniswap V4, Robinhood chain, Blockscout, public swaps and open-source tooling. Convert ten method ideas into falsifiable original-owner research and make approved, source-bound outputs usable by future Alpha Lab Pro site. DO NOT reproduce private 0x code, request new tokens/API subscriptions, scrape proprietary API/data, create extra jobs/scanners/agents, trade, modify Compass/CN forecasts or publish private Alpha research.

Research Parallel Lanes skill source: .agents/skills/research-parallel-lanes/SKILL.md. This is a coordination plan only, NOT evidence that ten independent AI agents ran. One incumbent lead, one heavy lane at a time, at most two to four actual existing independently authorized compute jobs when strictly useful. No new recurrent GitHub workflow. Existing S1 and Claude Bridge may review source-bound design, not automatically deploy it.

Current original owners: Meme-Alpha-Lab #98 sized sellability and negative route truth; #194/#126 exact CA-pool binding; #120/#70 Pons capture/cursor/source continuity; #77/#85/S4 matured forward outcomes; #88 wallet evidence; #124 provider challenger; #228 site and Strategy Arena. Archive #1512 external specialist Research Lab, Archive #1340 complete denominator, #1157 Strategist, #1156 sole S1 supervisor. Do not clone these domains or create ten PRs by default.

Source snapshot and prior work checked 2026-11-10:
- Alpha AGENTS.md blob 040b706c1af06e7b8662b416e1ffe25dc337bae8, existing source first/read privacy and science contracts.
- Alpha Pons source-verified guide research/discovery/PONS_V2_PUBLIC_SOURCE_TRANSFER_2026-10-05.md blob 5898cc765d0c83f31bc000c756b952990d89f98c; CURVE_BUY/SELL event decode already exists.
- Alpha scripts/collectors/pons_curve_quote_shadow_v1.py blob 3270c7911a6d04580cc1f1471aa1ce17344841c4: marginal virtual reserve ratio proxy, NOT a whole-size executable buy/sell quote.
- Alpha research/sellability/README.md blob 3d8a04e866a05eea2b76ecbd51031194b928e338, GoPlus provider challenger plus internal mechanics ledgers and explicit still-missing negative execution proof. 2026-11-09 #98 reports original PR #250 source audit detected ZERO verified paired exits, NOT proof zero exits exist.
- Alpha strategy_arena/README.md blob 3368b670960091bcbbc45291feca4b1d5f30764f: 8 offline shadow arms; zero source-attested economics.
- Alpha Alpha Lab Pro roadmap blob 7cc3a21c6e4bf715a406360fe706008798f92591 and build state blob de17f1fd9e050d8fa1e868730f1758b774e36c3b: D2.5 private staging, no approved published live feed, source/identity/outcome and Safari/publication gates open. Do not infer today's production freshness from older snapshot.
- Source original technical triage in #98 comments 6763755562 and 6768688125; #120 comments 6698894685 and 6768697114; Research Lab #1512 comments 6763765003 and 6768715923. This Atlas consolidates and extends them instead of creating a second authority.

## Rights and money first
0x Swap API chain support may include Robinhood 4663, Pons curve and Uniswap V2/V3/V4 per official July 2026 changelog, but a chain-source claim is NOT a qualified exact token/routing quote. Official 0x API requires a key and its public pricing warns that continuous quotes without orders can be limited. API terms govern reproduction, retention and derivative or competitive use of 0x Data. No 0x account, trial, key, quote polling or historical provider data ingestion from this mission. Original docs: https://docs.0x.org/ ; https://0x.org/pricing ; https://0x.org/legal/api-license-agreement ; https://docs.0x.org/changelog/2026/7/31 .

Use the following independent sources and only their stated lawful scope:
- Pons documented public protocol and direct chain eth_call/events: https://docs.ponsfamily.com/v2 . Token/curve provenance, interface or code licensing separately verified before copying any source.
- Uniswap V4 state/quote docs: https://developers.uniswap.org/docs/protocols/v4/guides/state-view and https://developers.uniswap.org/docs/sdks/v4/guides/swapping/quoting . Protocol source parts have mixed licenses. Don't assume MIT for V4.
- 0x-parser MIT for observing ACTUAL 0x transactions only (requires trace availability): https://github.com/0xProject/0x-parser .
- Foundry Anvil for local, unsent fork experiments: https://getfoundry.sh/anvil/index.html ; REVM (MIT) https://github.com/bluealloy/revm .
- Blockscout Robinhood documented public/free-cap APIs: https://github.com/blockscout/docs/blob/main/robinhood-api.mdx . Documented 1,000-record cap is provider/endpoint specific and NOT universal RPC truth.
- Ponder MIT self-hostable indexer: https://github.com/ponder-sh/ponder ; optional code/method inspiration, not a second deployed collector.
- DefiLlama price endpoint only when chain and quote asset coverage/rights proven: https://api-docs.defillama.com/ .
- Jupiter Solana public docs and limited free routes: https://developers.jup.ag/ . Availability and allowed rate are not reliable fill evidence and can change.

No claim that source URLs, provider accounts, deep-research products or model API grants free infinite access. Strict per-mission added cash spend = USD 0, model API request count = 0 by default. Already owned Claude Max subscription can be used within its existing single auditor when actually picked up and documented, not as a new cost/unattended service. Do not circumvent paywalls, use a cloned 0x quote stream, copy source whose license is unknown, or present marketing accuracy as proven.

## The ten preserved candidate methods, rank by expected cross-system leverage

### 01 P0 / highest - Native Pons exact-size bidirectional quote + state machine
Question: can Alpha reproduce expected buy and SELL for quantity q at source-bound block b, across phases and actual creator/trade/snipe tax, better than the current marginal ratio proxy?
Source: https://docs.ponsfamily.com/v2 (Getting a quote, Reading state, Buying/selling, Graduation, Custom pairs).
Method: independently read phase, readyToGraduate, getReserves and real/sellable supply, tax/fee parameters and quote asset decimals at same finality-confirmed block/hash. Apply Solidity integer order/rounding, tax on proper side, early-buyer recipient snipe only on relevant BUY, cap exhausted inventory and refunds. Phase 0 curve; phase 1 swept/cannot assume SELL; phase 2 V4; phase 3 rescue/UNKNOWN; readyToGraduate true may close curve SELL while not graduated.
Baseline: existing marginal Pons reserve price ratio, raw CurveSell/CurveBuy receipt. Falsifier: native reproduced quote systematically diverges from observed independent event values beyond exact documented rounding/fee allowance or requires unavailable internal state.
Gate: first exact same-block historical or forward onchain transaction event, deterministic positive/negative fixtures, no market data fabrication. Owner #98 with #120/#194.

### 02 P0 - Native Uniswap V4 PoolKey / hook-aware read-only quoter
Question: can Alpha size exits after graduation and account for Pons-specific hooks/tick liquidity instead of treating all LP liquidity as v2 reserves?
Method: verify onchain PoolManager, 32-byte PoolId vs 20-byte token, actual PoolKey token pair, fee/tickSpacing/hook, current liquidity/ticks, valid StateView/Quoter eth_call and hook-specific output deltas/fee tax. Do not double charge pool fee; do not treat simulation as onchain executed trade.
Baseline: simple price ratio and current source pool snapshot. False controls: wrong hook, wrong pool, fee mutation, stale block, zero liquidity, unsupported V4 hook, source reorg. Owner #98/#194.

### 03 P0 - Locally reproduced negative exit / route failure proofs
Question: can a supposed SAFE microcap be bought but fail a full-size SELL at the same source state?
Method: local Anvil/REVM fork or faithful exact-source deterministic replay. Use synthetic test wallet, never a private user wallet. Same-block buy/sell, allowance, approval, tax, blacklists, proxy/hook, route, actual exception, full-position size and gas. Evidence status is VERIFIED_REVERT / NO_ROUTE_IN_TESTED_UNIVERSE / SIMULATED_SELLABLE / ARCHIVE_STATE_UNAVAILABLE / UNKNOWN; never universally UNSellABLE from one missing 0x route.
Baseline: existing GoPlus label and #98 internal mechanics. Gate: local fork reproducible under free historical archive RPC or mark BLOCKED. Owner #98.

### 04 P0 - Actual executed swap receipt and balance-delta truth
Question: what did a real wallet receive after gas, taxes and routed swaps, not what a chart promised?
Use first-party chain tx receipts, ERC20/native balance diffs and traced router internals when genuinely available. 0x-parser only for relevant 0x transactions, native Pons and v4 needs independent decoding. Keep payer/seller versus recipient separate. Baseline: old snapshot/DEX candle; falsifier: mismatch after fee+recipient decomposition. Keep failed and incomplete traces. Owner #98/#77.

### 05 P0 - First-known, contiguous source event tape and anti-truncation
Question: are launch and exit histories complete enough to support point-in-time claims?
Existing #120 issue and public HOT/COLD source come first. Provider-specific eth_getLogs 1,000 or 10,000 limits must be checked against the exact endpoint, with adaptive windows, no single-block fail-open, explicit thinned-event and total event counters, reorg/finality, exact txHash:logIndex, gap custody and source timestamps. No new collector until a real original source defect requires one. Baseline: existing Pons public HOT/COLD and Alpha current cursor; objective pass: two native healthy consecutive source windows plus coverage evidence, not a green unit fixture. Owner #120/#70.

### 06 P1 - Position-size capacity curve and drawdown/liquidity stress
Question: do signal winners remain net profitable at $50/$100/$250/$500/$1,000 and 100% of a frozen hypothetical position?
Compute same-source same-block two-sided actual-size quote (not fabricated fill), gas/fee/tax/price-impact, route/revert and 25/50/80% hypothetical depth shocks. Shock scenarios are stress exercises, NOT predicted price or fill. Compare cost/size loss distributions, time to illiquidity and missed-winner cost. Baseline: constant-size chart-return/virtual ratio. Owner #98/#77.

### 07 P1 - Quote currency and actual as-of USD conversion
Question: can non-ETH Pons custom token/USDG/tokenized-share pairs be valued without currency and decimal mistakes?
Read pairToken, decimals, original amounts, original quote asset reference, independently attested as-of price source if available. Keep NATIVE_QUOTE_ONLY when USD source missing; don't assume all stablecoins $1 or same ticker equals same asset. Check implied FX exposure and depeg/market hours. Owner #98/#194 plus source QC.

### 08 P1 - Minimal independent AMM route comparator
Question: given only licensed public onchain pool state, can one direct or one-hop route improve net expected quote over a single canonical route?
Enumerate bounded known verified Pons curve/V2/V3/V4 pool graph, compare total net after gas/fees at one pinned block with explicit provider boundary and ignored missing pools. Do NOT clone proprietary 0x RFQ API, rely on 0x quote stream, or deploy a trading router. Baseline: best directly verified native route. Owner #98/#194.

### 09 P1 - Task 2 / Strategy Arena after-cost ablation
Question: which of 4x2 existing prospectively frozen Alpha Pro strategies survives the difference between displayed price and realizable paper exit?
Reuse #228 Strategy Arena, #77/S4 and #85 forward original freezer, Archive #1340 denominator. No retrospective winning arm tuning. Compare naive price vs Pons ratio vs native full-size quote vs valid verified exit/failed/no-route and liquidity path at +15m/+1h/+6h/+24h/+72h/+7d. Include zero opportunity, no quote, unsellable, rug, wrong-identity and stale source. Primary target = incremental net expected paper-realisable return against a pre-registered equal-time matched baseline, conditional on sufficient coverage; quote outcome NOT actual fill. Owner #77/#85/#228.

### 10 P2 - Solana free, source-bounded independent challenger
Small bounded Jupiter price quote for confirmed exact mint/pool at allowed FREE rate and source-specific SLA, compared with native Solana program/account decoding. Never interpret one chain's fee/approval model as another's; Jupiter quote is not real fill or proof of sellability. Priority only after Robinhood P0 and subject to zero incremental budget. Owner #194/#98, no separate Solana scanner.

## Research result contracts and quantitative adjudication
Every original-owner result must be inspectable via one source-pinned receipt: mission_id, lane_id, owner, source repo SHA and blob/ref, chain ID + exact CA + curve/pool ID, block number/hash, original event timestamp, first machine seen UTC, provider received UTC (if available), quote valid UTC and expiry, quote currency + decimals, size, fee/gas/tax assumptions, source coverage, use-rights, simulated versus verified actual tx, negative outcome, failure class and SHA256 of any evidence saved. Preserve source identity only in public Archive; raw private/proprietary or user wallet evidence stays in governed private plane. Never publish credentials, personal wallets or restricted results.

Status classes: SOURCE_UNAVAILABLE, SOURCE_LIMITED, CHAIN_UNVERIFIED, PAIR_IDENTITY_CONFLICT, T0_UNATTESTED, PRICE_PROXY_ONLY, SIZE_QUOTE_SIMULATED, ROUNDTRIP_SIMULATED, REAL_TX_VERIFIED_AT_SIZE_TIME, NO_ROUTE_IN_TESTED_UNIVERSE, VERIFIED_REVERT, UNKNOWN, CENSORED_OUTCOME. Keep provider economic truth separate from provider marketing. Negative result is not LOST if logged.

Primary science: full eligible denominator, independent T0, same-horizon price/liquidity state and no-lookahead, 20–50 prospective cases for feasibility then sample sizing by measured variance, matched controls including failed/unscored launches and no-pool tokens. Sample number is NOT automatic promotion. Evaluate source+quote coverage, false SAFE/false UNSAFE, calibration, MAE/MFE, after-cost hypothetical returns, 100% position exit capacity, median latency, zero quote and missed winner cost. Stop/kill each method if source repeatedly unavailable, materially worse than simple native liquidity baseline, unlawful/no free access, no incremental action changes or unsafe false-owner/false-sell inference.

## Deep Research, Claude, API decision
- Deterministic source code and public contract reads: use ChatGPT + connected GitHub + local/unit tests first; incremental USD 0. Complex public docs research can be done in this chat/Deep Research mode if user has native feature, but that mode is not an autonomous live scanner or S1 action and its report is never source authority alone.
- Claude already has ONE scheduled auditor via standing private Bridge #173 and claude/log. Request an independent adversarial method audit, do not spawn/modify schedules, do not impersonate a scheduled S1 review request or claim Claude ran until exact branch report and SHA readback. Prioritize contract phases, V4 fees, simulation trust, license and streaming/site publication boundaries; produce one high-value delta with exact original owner, falsifier and patch candidate, else explicit NO_INCREMENTAL_VALUE.
- PAID MODEL API: NO by default under owner's current zero extra payment constraint, regardless of a general past model budget. Research first; only if unique public/source-safe unresolved reasoning actually warrants it, and with separately authorized cost + official gateway/strict cap/immutable receipt using the existing shared Sol MAX runbook, not a new client. Never send private Alpha positions or source values to public model API.
- Comparative ROI of Deep Research/Claude/API: prefer 0-dollar existing Claude for adversarial synthesis once source-grounded; use independent code/fork/onchain events for numeric evidence. A model cannot replace native source truth, a verified quote, a legal license or out-of-sample proof.

## Phased dependency order and stopping rules
G0 Reconcile original owners/PRs/current safe source, rights and exact-Pons token case. G1 Pons phase-aware exact-quantity quote with negative fixtures and at least one original native independent event; G2 free trace/fork viability plus source continuity; G3 V4 postgraduation and capacity grid; G4 prospective same-T0 outcomes and Strategy Arena; G5 site publication only after separate privacy and original source gates. Other independent public research lanes may run in parallel conceptually, but no heavy source-dependent job can claim completion before upstream gates.

A fully executed outcome means native original PR or source receipt, exact-head CI where required, protected branch/review gates, main readback, honest coverage and linked original owner issues. This ATLAS itself is documentation, not that executed outcome.

Companion machine contract: 2026-11-10__INDEPENDENT_EXECUTION_ALPHA_LANES_V1.json.
Companion site mapping: 2026-11-10__ALPHA_PRO_EXECUTION_SITE_BRIDGE_V1.md.
