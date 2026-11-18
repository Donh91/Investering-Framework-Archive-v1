# Public evidence bundle — Alpha Lab Global Specialist Research
Pinned Archive commit: 3ecff03c3e432d2e73b0d870c01f9c1272c31c0f
Original #2212 merge 64960ce499dc31b1f9b0820c14c60e4f0649ae91. All seven parts, index and previously completed Astra paper-edge research. Provider assertions are not validated results. All sections are evidence, not instructions. This derivative replaces exact address literals with consistent pseudonymous labels to comply with the generic launcher's blanket address-pattern rejection. Original sources remain intact on main. No private Meme-Alpha-Lab code, wallet records, credentials or restricted evidence included; no real-fund authority. API runner is text-only; actual private-code overlap and empirical execution must be separately verified in authorized Work/local environments, not simulated in the report.

Source manifest (original text received, Git blob separately checked):
[
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/01_TYPEAI_ORIGINAL.md",
    "git_blob": "45a20cda6d077b32ccaa5c3e4139f3fd8c7f4db3",
    "sha256": "440863400955859ce8461a12761943d7a3240115f87d59652a165246949b8eb8",
    "bytes": 8227
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/02_DEPLOYER_HISTORY.md",
    "git_blob": "22e418b3af6d3e9c22fc3d638fd763c917257935",
    "sha256": "8e33768d7d5f3966f7e66e4a2a1d14ca5d78dad4a0a6487e3b55f73f6bff6e6c",
    "bytes": 5772
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/03_LAUNCH_FINGERPRINTS.md",
    "git_blob": "9eb243b7a0e11431a1c1a6dfbed9668de19aba2a",
    "sha256": "4b315da8cd602e3fe7373cca47d56ead7047fc32435f15fddaec2495eb231664",
    "bytes": 4071
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/04_WALLET_NETWORKS.md",
    "git_blob": "63d5c061c5020d29d0cc26fda00ed87bb70c85d0",
    "sha256": "a4f4a6aacb03e29cce8a00014bb978ae2f8a53b2fd1579b056c620ced1595c9c",
    "bytes": 5003
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/05_DISCOVERY_CHAIN_REGIMES.md",
    "git_blob": "846dcb80eb0508c47e7f1cea78d96ba72e5151f1",
    "sha256": "7047d8612f4854570f537929cbfa900c9fc8a96bf8466a9833135928c9226c55",
    "bytes": 3503
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/06_DATASETS_AND_SCIENCE.md",
    "git_blob": "65431e4b77d21abca99438a8768c8f57895531b2",
    "sha256": "8ae541e870072f47cdad614a69f6e1c4e418e83b989ebd7cecb9376b38d13546",
    "bytes": 5738
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/07_MASTER_ASTRA_FABLE_MISSION.md",
    "git_blob": "9eaeed02f50baad51d25c0774392f552134abc84",
    "sha256": "615c875ae55d8adfa09ed19f5bb8445fc3fd193ac8412e5cfc757a61d77d1bdc",
    "bytes": 7999
  },
  {
    "path": "06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/README.md",
    "git_blob": "00ccdf7977a73ef9955141fa6d96d47a80b81070",
    "sha256": "aa0203f48e640309aa51708f0ed7d531385ae03c6acc5fb73aac3f59c7ad6eaa",
    "bytes": 1003
  },
  {
    "path": "06_RESEARCH_LAB/astra_program_20261116/results/alpha_lab/ASTRA_ALPHA_LAB_PRO_PAPER_EDGE_RESEARCH.md",
    "git_blob": "b1f444a7f23a96d70c9aa9e5f27ee686d2cee4fe",
    "sha256": "a3c5880525057846dadf80ee90ac40cbfe6a59e8144c398f3323a3a49184a16b",
    "bytes": 65320
  }
]

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/01_TYPEAI_ORIGINAL.md | blob 45a20cda6d077b32ccaa5c3e4139f3fd8c7f4db3 =====
## TYPEAI_SPECIALIST_DISSECTION_20261117_V1 | owner-requested reverse engineering | research only
Source: user supplied TypeAI 17 Nov X screenshots and https://www.typeai.online/; public MIT client https://github.com/Type-AI-Technologies/typeai-mcp/tree/4209aa26a608574709348449990355a0d6d6b1b1. Read main pointers: Archive 007eb0944025f5f88abce7a5b502b910535d2339; MAL b9037206e9231a64194c0e9955d40d46c2a3ea23. Source pins: config.js 978224807931dc1bf0f1f18db4c3ca3aad5f834f; robinhood.js 04954e43fa45fcec93802a7bb3809d68be683e10; index.js 6aca165164699de55809f153c7a40cc987b5c602; http.js 832450db81d8eaa5b119810ab7b4b1ccec000a12; client.test.js 5071fef533b53880aae634ff22870750dbc19132. Client is MIT; backend risk weights/resolution logic and upstream provenance are NOT disclosed. Test file mocks backend; not validation of predictive accuracy or security. Website fetched successfully; marketing/demo is not proof.

**New bounded read-only source observations (17 Nov session; no independently sealed UTC/response hash, not PIT-admitted)**:
- GET https://api.typeai.online/api/mcp/v1/tokens?list=trending returned chain Robinhood Chain; ten ranked entries but eight distinct addresses: CASHCAT [PUBLIC_ADDRESS_OMITTED_01] rank 1/5 (price .0445116756360671/.0447246638579603, vol 2313182.01618245/156419.606897963), PONS [PUBLIC_ADDRESS_OMITTED_02] rank 3/7 (price .110583062765385/.111317246403685, vol 1910548.52668421/100422.705060084). No pool identifier, provider observation timestamp or rank methodology in the result. Pool-level duplication is a hypothesis, not proven. Other unique addresses: GIGATENEV [PUBLIC_ADDRESS_OMITTED_03], HOOKR [PUBLIC_ADDRESS_OMITTED_04], AI [PUBLIC_ADDRESS_OMITTED_05], PRIORS [PUBLIC_ADDRESS_OMITTED_06], HMM [PUBLIC_ADDRESS_OMITTED_07], TORCH [PUBLIC_ADDRESS_OMITTED_08].
- GET /quote?token=[PUBLIC_ADDRESS_OMITTED_08]&amountEth=0.001&slippagePercent=1 returned pay 0.001 ETH, receive 583.7102 TORCH, payUsd 1.79, receiveUsd 1.72, gasUsd .0128, fee .00001 ETH (1%), slippagePercent 1, slippageBps 100, same CA, decimals 18, buyTaxPercent 2, sellTaxPercent 0, honeypot false, canSwap true. No actual transaction, reverse route, block, minOut, or proved full exit. Explicit slippage 1% vs buy tax 2% is a semantic test candidate, not proof of failed routing. Preserve raw quote components and avoid double-counting embedded fee/impact.
- /tokens/TORCH and /tokens/TORCH/safety returned HTTP503 through fetch intermediary; exact CA detail/safety timed out; /tokens?list=losers HTTP503. Distinguish transport from origin certainty. Quote + list worked only in this bounded sample; no SLA, independent upstream, data freshness or continuing access established.
- Client GET surfaces list/details/safety/public wallet balance/ETH->token quote; POST /swap, local signing server and status lifecycle are EXCLUDED from Alpha use. No wallet connections or signing. Quote MCP wrapper drops canSwap/slippageBps/amountEth from displayed result: prefer validated raw structured observation if permitted, never assume missing flag is true. 45s timeout and 429 handling; no validated sustained rate limit or backoff strategy.

**Overlap & admission:** Existing Astra HIGH Alpha report already archived (blob b1f444a7f23a96d70c9aa9e5f27ee686d2cee4fe; receipt cbfef77781c6fba20cf2ec48b65abd7860a0e94d; report says design-only/not evaluable, prioritizes first-known, exact identity, full-size exit and accounting). Do not relaunch that consumed mission or create another scanner/paper wallet. Existing MAL program P009–P014, #194/#126/#84 identity, #98 sellability, #77/#85 denominator, #155 source independence, #228 UI, #38 heavy queue, Archive #1512 -> #1157 -> #1156. Read AGENTS and specialist queue 410749484cd399581d2b69ba50019cee969e81f5. Current live_shadow receipt 4849461cdbbb61ef6159ed05f2efa55ef5759d806688d26b9b2af063e905b189 shows 0 five-gate passes, scanner false, 7,097,079 backlog blocks; precision harvest L05 reports zero pairs. No claims of new alpha. Method performance exact guessed path returned 404: full overlap check still needed via actual tree.

**Single proposed heavy Work mission (Astra xhigh preferred, Fable independent review only if separately frozen/authorized):** TYPEAI_ALPHA_PRO_SOURCE_DISSECTION_001. QUESTION: can publicly observable TypeAI claims provide incremental value over raw RPC/Pons/DexScreener and existing sellability and intake owners on identical eligible cases? WHY HEAVY: cross-layer identity, execution semantics, ranking bias and UI provenance; only after deterministic source probe. DECISION SURFACE: at most one actionable delta per family, implement via existing owners only. VOI: safer exact-CA joins and avoid fictitious paper fills before new scores. WORK ceiling xhigh, API ceiling $0 (Work only; if unavailable and paid model required, original budget/owner admission needed). No new scheduler, no backend reversal beyond public authorized interfaces, no credentials, no trade, no API rate-limit circumvention, no copying proprietary code. MIT reuse only with license notice if actually copying.
1. Identity: exact chain+CA, pool ID separately, multiple pools/bridged/native, spoofed liquid ticker, ambiguous aliases, exact CA wins or explicit UNKNOWN. Don’t use CoinGecko listing/liquidity as identity proof; rank alternate candidates only. Use #194/#126/#84.
2. Discovery: freeze raw response + captured UTC, source clock/unknown, CA/pool provenance; dedup without merging incompatible volumes. Compare trending/gainers/losers against Pons census + same-cutoff existing scanner, matched misses/losers/early launches; no retrospective feed as first-known. Source independence audit #155. Kill if no incremental lead/coverage, duplicate upstream, stale sources or poor availability. Existing #77/#85 + P009/P010.
3. Sellability: bounded tests of tax, mint/admin/proxy/blacklist/LP, holder concentration adjusted for LP/burn/router/bridge with unknown state. Compare TypeAI flags against native mechanical truth at same block, raw route, size; stratify safe/infeasible/unknown. $100/$500/$1000 existing size buckets plus existing tiny quote fixture only. Native full-position sell must be separately modeled. #98 + X0 disagreement, no replacement of safety gate. If safety endpoint unavailable then SOURCE_BLOCKED_WITH_TRIGGER.
4. Paper execution: reuse existing execution_shadow_v4 + five policy work from Astra report, record amount/token units, quote clocks, route/phase, gas, fees, expected/minimum receive, actual simulated fill or no-fill, reverse quote, latency, failure and exit liquidity. Compare net realized feasible return + coverage to simple baseline, not chart MFE. No user wallet.
5. UI/companion: #228 existing private read model only; distinct identity, safety, alpha, execution evidence, freshness, missingness, source disagreements, ownership and coverage; candidate compare and plain-language evidence trail, learning from frozen outcomes only; never use preference to bypass identity/risk. Reuse D3/D4/D5 roadmap and existing future Fable R9, no separate product roadmap.
6. Deliver frozen source manifest + reproducible bounded fixtures and one priority delta/falsifier per family, compare against existing registry and recent Astra report, Strategist disposition then S1 original-owner route. Prospective cohort only after source approval and actual eligible capture; matched failures, 1h/24h/72h/7d, report denominator and cost. No statistical edge inference from the 2 successful API probes. Freeze on current main, actual raw UTC response receipts and licensing/access check before any test admission. If no new actionable evidence, DEDUPED or SOURCE_BLOCKED with precise trigger. No second paid Astra run or new Fable round without applicable review/authorization and served-model receipt.

Request to #1157/#1156: prioritize next bounded existing-owner validation of duplicate exact CAs and quote/exit semantics; record disposition and whether heavy Work can be admitted without displacing current active lane. Research intake only, NOT_DISPATCHED / no model run yet.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/02_DEPLOYER_HISTORY.md | blob 22e418b3af6d3e9c22fc3d638fd763c917257935 =====
# Part 2 — Deployer history: separate launch activity, economic exit and durability
Date: 2026-11-17. Status: SOURCE_RESEARCH / NOT A BACKTEST BY ALPHA LAB. Parent #1512; original MAL#224, #120, #126, #88, #98, #77. No new monitoring/trading authority.

## Specialist evidence and transfer
- Pumpdata: https://pumpdata.fun/pump-fun-api and https://pumpdata.fun/methodology. Documented free lookups: /free/deployer/{wallet}, /free/launch/{mint}, /similar, /public/baserate.json, /launches/since.json, /status.json; 30 calls/5min, 300/day per IP advertised, verify terms and header semantics; never pay x402 or bypass 429. Deep history refreshed from archive; live fill has different clocks. Provider distinguishes prior record at launch vs record now. Own-launch buy/sell, first-10s concentration, age-matched analogues, peak vs persistent performance, no-trade records are separate. Copyable leaderboard withdrawn because actual PumpSwap fees made copying lose: important negative evidence.
- Bounded public no-key /free/deployer documented example returned 982 launches, 164 graduations, 517 measured in last 90d, 68 doubled, 7 10x, 3 held 2x, median own exit 14 seconds in its stated recent own-coin sample; provider's current-record values, not frozen features or a candidate recommendation. The same session returned /status.json checked_at 2026-11-09 and baserate generated 2026-10-31, stale relative to Nov 17! Do not infer live health from HTTP 200. Retrieval intermediary may cache; capture origin headers, source time, raw digest and exact UTC before admissibility. Source claims not independently reproduced; compare provider 90d subset definitions with actual ledger. The source's dead_next_day means no priced trade in its window, not an economic rug.
- Cabal Hunter: https://cabal-hunter.com/dev-launch-radar; https://cabal-hunter.com/methodology; https://github.com/paulf280-ui/cabal-hunter-mcp README blob 99dc55c27ba6f27054ac1f0e4a073a05e7588b38, MIT client. Market-driven graduation vs same-block/dev-signed graduation, Mayhem exclusion, observed launch count lower bound, two feeds, timing and follow-up of losers. Published own test: 798,430 launches, 0.5 SOL at 30s, exit 1h incl fees; 5+ prior / >=20% grad -20.3%, 3+ and >=1 grad -5.8%, 3+ no grad -2%, all -3.9%. This is a strong counterexample to reputation-only alpha, not independent proof or universal verdict. Claimed latency 0.77s median is not our achievable latency. Radar $99/month advertised; no purchase. Risk methodology notes funding trace had no verified true positives after infrastructure bug fix; previously misattributed bonding curve payouts to shared funders. Treat funding as evidence, not intent. Provider code wraps backend; no proprietary reversal.
- RobinX https://robinx.io/methodology and https://robinx.io/callers. Provider describes score on other launches, real activity defined by >=1 WETH volume and >=20 traders. Its forward claim of 41% real launches / 5.5x baseline for high score is activity prediction, NOT return or copyable profit. Earlier RobinFun pool-at-creation does not equal Pons graduation. Need reproduce temporal scoring with prior mature labels, independent denominator, remove wash/economic duplicates and tokenized equities.
- PocketCoin https://pocketcoin.app/robinhood/wallet-network is already a source for KITSU MAL#224. Advertised windows: first 10m launch data 6d; trade ledger 14d; LP 7d. Public source page discovered but timed out in direct fetch. Do not rely on rolling labels as historical facts or copy private addresses.

## Proposed mechanism and empirical targets
Reuse MAL#224's KITSU + 4 preceding launch replay as a diagnostic (not validation). A deployer can be active, produce transient peaks, sustain liquidity, or exhibit extraction risk; retain independent axes rather than one trust score. Classify platform/service vs actual beneficial issuer unknown using signer, creator argument, fee payer, factory role, liquidity source and tx proofs. For every historical launch only use evidence available before a new launch. Compute counts, coverage, launch intervals, prior organic graduations, time-to-peak distributions, size-aware positive-return frequency, survival and liquidation failure, loss distributions, prior seller/treasury behavior, confidence and recency. Include zero-trade, inaccessible quote, no-exit and dead cases. Distinguish gross 2x/5x/10x/50x/100x chart events from executable outcomes, no assumed fill. 100x is an outcome label, not promise or buy trigger. Rare event metrics: PR-AUC, precision at fixed research capacity, calibration, net-return distribution with complete eligible opportunity set, entity-cluster uncertainty. Competing risk: organic continuation, collapse, liquidity removal, untradeable, unknown. Train only on settled earlier histories; unseen launchers get shrinkage toward chain/venue/age baseline. Holdout by time and deployer/entity group; stress fee and latency and censoring. Avoid any live following of suspected manipulation; coordination flags are risk/veto/evidence, not entry permission.
## Acceptance / falsifier
Compare frozen transparent age/liquidity/volume baseline vs prior launcher history alone and history plus independent public-trade features, identical decision clock. Use simple regularized model before complex graph/ML. Source owner #224 runs ONLY under existing gates; source clocks and complete coverage first. Retire if apparent improvement vanishes after costs, controls, removal of privileged actors or leakage. Existing #224 min 30 forward and kill review after 50 eligible cases are pilot rules; not sufficient to establish rare 100x probability. Larger power analysis before generalization. No new scanner, scoring threshold change or model launch.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/03_LAUNCH_FINGERPRINTS.md | blob 9eb243b7a0e11431a1c1a6dfbed9668de19aba2a =====
# Part 3 — Launch provenance and deployer-family fingerprinting
Date 2026-11-17. Public research. Owner MAL#126/#194 and existing entity resolver #105 (closed implementation; extensions only with owner review), #224 for serial-launcher replay.

## Sources
Chain of Title https://chainoftitle.org/ ; https://chainoftitle.org/method ; https://chainoftitle.org/api. Public method and example: 15 distinct wallets used the identical 694-byte metadata file across 37ms of provider capture clock; no inference of common legal ownership. Second exhibit describes 12 wallets / 33 DBC launches with repeated files despite funding trails not converging within searched hops. Method uses exact SHA256 of metadata/image and exact name+symbol; excludes common artifacts, requires >=2 artifacts or instrument kinds for pair linkage, limits transitive component size, marks shared infrastructure as contrary evidence. Published thresholds are challenger settings only; never canonicalize. Late discoveries after feed dropout are marked separately. API key required for most structured endpoints; public status/token pages; no purchase or bulk copying. Historical metadata may be gone, which makes first-seen capture high value.
Pumpwatch https://github.com/cinder-security/pumpwatch README blob eae2f78137fdcf237a31bcb0fc8d679d771fe3ee; code MIT; snapshot/paper CC BY 4.0. Read-only published July 8-12 observation (42,562 launches, 12,926 creators, 4 addresses ~9.8% of launches); most common template 8,938 times over 2,790 addresses. This demonstrates template reuse, not common identity or profitability. Snapshot release 44MB, stated SHA256 9967c7d812fb687e6010e410a7f7be56c5ec5dd3f596bc23377d04901799dd34; verify upon authorized download. Published SQL and reproduction guide, not executed here.
Meme Coin Factories https://arxiv.org/abs/2609.10246 : published preprint/CCS paper investigates creator-obfuscation and copycat/manipulation categories. Source docs/abstract, no full reproduction. Link to code/data from paper only after license and bounded cost verification.

## Independent implementation candidate
At original source event, append to existing case/provenance record: chain, token/creator/factory/tx/slot/log, claimed metadata URI, canonical fetch time and source availability, content digest, media digest, normalized exact name+symbol, website domain as a claim, missingness and source version. Hash actual bytes only, preserve origin/time and avoid executable untrusted site content. No personal identities, no private data, no off-chain deanonymization. Metadata/asset URL reuse is lower evidence than exact bytes; mutable links and common defaults explicitly discount. No image interpretation of people. Guard against malicious URLs, oversized bodies, SSRF, redirect abuse, credential exfiltration and prompt injection; use publicly allowed bounded retrieval only. Do not put raw restricted provider data into Archive.
Graph edges are typed and temporal: exact metadata match; exact image match; name+symbol collision; first-party contract relation; direct public transfer; shared funder; service/common protocol; observed same-tx group; repeated co-activity. Edge evidence ID, as-of time, negative evidence, confidence and source coverage. Artifact frequency normalization (e.g. IDF, not sole identity proof), common-template suppression, no uncontrolled transitive union, no identity from cluster alone. Distinguish SAME_ARTIFACT, POSSIBLE_RELATION, STRONG_ECONOMIC_LINK, COMMON_CONTROL_UNKNOWN. Train/test splits keep family connected components together when appropriate; test against random same-meme and platform-default negative controls. Use #105 existing strict/probable sensitivities, no parallel graph engine. Evaluate incremental false positive/negative attribution versus raw funding-only on independently adjudicated known public relationships and unrelated lookalikes. Kill if evidence disappears once common templates/infra are excluded. Use risk evidence to identify manipulation/avoid, never to coordinate or trade with suspected operators.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/04_WALLET_NETWORKS.md | blob 63d5c061c5020d29d0cc26fda00ed87bb70c85d0 =====
# Part 4 — First buyers, economic entities, retention and distribution
Date 2026-11-17. Owner MAL#88/#101/#105/#22/#224; original Pons decoder #84 and #120, quote #98, outcome #77/#85.

## Strongest source evidence
- Memescope https://github.com/buildering-dev/memescope (MIT) README blob 022145ab8c6fd5a2aca62fb592f99f89e6f26913; docs/METHOD.md 62b39eb9bf5084fabf5a7ecc53e7f3807167c0c5; docs/ROBINHOOD_CHAIN.md d16fa5a942467b44808d4d61e96a245662c17cf2. Dashboard https://buildering-dev.github.io/memescope/. Random 12 launches/hour/chain, fetched >=6h; first 10 buyers / creator / top 5 sellers, <=3 funding hops; stops at hubs; raw gzip, bounded history and truncation. Separate volume-bot, coordinated exit and free-transfer cases. October 6-10 own sample (1,161 Solana, 462 RH) claims 80.8% of positive realized SOL PnL to flagged roles, 16.1% profitable unflagged closed-wallet sample; those figures are label- and closure-sensitive, not replicated. Robinhood ETH PnL explicitly approximate and excluded from profit share/persistence. Their prereg smart-wallet test (rank 2 weeks, untouched 2 weeks + realistic costs) was still waiting on dashboard; verify actual test_status before using. Retain open illiquid losing positions as marked-to-liquidation or censored, not exclude from investor economic results. Future-wide insider labeling in a training period may leak if applied retrospectively; compute only known-time exclusions.
- Notable correction: free-token transfers to fresh sellers inflated apparent outsider profits; group-level cost-basis reconciliation changes accounting radically. Must classify MARKET_BUY vs TRANSFER/AIRDROP, sender vs effective trader vs recipient and original cost lots. Do not equate any transfer group to common ownership. On Pons, ERC20 transfer direction alone insufficient for ETH cash flows; our CurveBuy/CurveSell decoder is stronger where verified; handle V4 PoolManager, PoolKey, hooks, routers, ERC4337 userOps and EIP7702. Quote or execution missing = UNKNOWN.
- Cabal Hunter methodology above: shared-funder bug and same-slot noncausal coordination; documented risk and honeypot separated. Retain negative controls from MAL#105.
- Halvion https://halvion.io/ and https://halvion.io/docs/funding-chains lists first 100 buyers, held/sold amounts, public funder hops, cross-chain bridge references, explicit labels and private custom groups. Homepage includes SAMPLE DATA; no live coverage/ownership verified. API plans unverified. No identity deanonymization; no user private watchlist upload. Transfer classification and coverage UIs are useful inspiration.
- GMGN https://gmgn.ai/blog/what-to-check-after-finding-a-trending-memecoin/ and original MAL#101 already cover dev history, first buyer holdings, wallet qualification. No new standalone GMGN project.
- PocketCoin KITSU source is already in #224; provider labels are hypotheses with narrow rolling retention, not established misconduct.

## Research decomposition
Build an as-of behavior graph in existing method registry: actor role, event timestamp/block/index, net paid/received, remaining units, entity support, independent demand versus clustered supply, early recurrent wallets vs high-frequency omnivores, funding evidence quality, buy-before-public-call vs public follower, absolute and relative acquisition times, cost-basis and sell/transfer routes. First-N cohorts (10/20/50/100), fixed time slices vs event counts, share of independent quote capital, sold fraction, liquidity-adjusted overhang, effective participant count, temporal decay, normalized co-occurrence vs expected random rate adjusted for wallet activity and venue. Only public pseudonymous chain evidence; not a list to follow suspected insiders. Coordination, insider opportunity, independent skill and ordinary launch exposure are distinct. No participation in market manipulation, no front-running or evasion. Review attribution against matched same-launch and same-funder service controls. Explicit unresolved state. Test independent-wallet information for incremental prediction only after excluding manipulative/deployer-controlled cases from actionable paper policies. Detect possible extraction to veto or characterize risk, never as a route to exploit participants.
## Proposed acceptance
Benchmark existing independent wallet model vs simple activity/volume/liquidity vs entity-adjusted features under time and wallet/entity holdout. For each compare realized after-cost returns on complete eligible opportunities, coverage, false positives, failure and abstention. No auto score promotions. Existing MAL#88 matched-control requirement and #101 independent copyability criteria remain. Audit first 10 peer KITSU launch patterns under #224 historically and include failures. Distinguish detection of a publicly observable launch from real-time source capability; hourly backlog cannot prove second-level entry. No new tracker/scheduler; prove source health and existing event-to-candidate processing first.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/05_DISCOVERY_CHAIN_REGIMES.md | blob 846dcb80eb0508c47e7f1cea78d96ba72e5151f1 =====
# Part 5 — Discovery, runners, source integrity and chain-specific strategy families
Date 2026-11-17. Original MAL#120/#194/#126/#77/#85/#228, Archive#1340 and #1512. Research only.

## PumpPill research
https://www.pumppill.org/research, https://www.pumppill.org/learn/how-to-find-runners-early-on-robinhood-chain, https://www.pumppill.org/wallets, https://www.pumppill.org/data, https://www.pumppill.org/scan.
Provider research page returned 2026-11-17 19:25 UTC own logged sample: on Solana n=49,873; doubled 20.9%, 5x 6.3%, 10x 2.6%, 50x 0.4%, never moved >10% 53.8%. RH pure memes n=20,754 / doubled 5.2%; stock-paired memes n=2,062 / 11.7%; working-product tokens n=1,238 / 25.1%. Provider excludes tokenized stocks due to float/MC distortion. Not random census; entry floor plus peak-reading eligibility selection, provider-specific class, price/MC not executable PnL, and variable observation length. Separate dated lesson (Aug 5-Oct 2 sample) reports 200 RH 10x cases median peak 52h vs Solana 4.1h on its proven set; selection on winners makes these NOT optimal entry or exit horizons. Range Finder records coils and breakout candidates including failures; published 296 non-equity breakouts, 36 reached 2x in 7d, 119 never >10% above, median peak 1.18x. Three model-missed big breakouts named, useful missed-signal logic not independent edge. User goal: 1-3d, 5-7d, 2-3w distinct. Validate chain x venue x launch phase x token class x market regime; add separate stage/age and liquidity-compatible baselines. Product classification must use evidence actually available at cutoff, not future adoption. Price change and circulating cap/supply changes must be separated. Funding/wallet score and paid /data API features are challengers, no payment or proprietary copying.

## MadeOnSol structured SDK
https://github.com/MadeOnSol/robinhood-chain-rs README blob af856bb9573fd80961dbd5565e919dd89e2d2128, MIT client. Documented v0.13 endpoints and coverage fields: dev event cursor, repeat history/trajectory, effective ERC4337 actor, first buyers, token bundles, position exit ledger, actual current balance verification, FIFO cost method/status, price as-of, liquidity source/status, holder history coverage, source gap and not_tracked. Rich contract ideas, especially explicit Option fields and raw quantities as strings. Many endpoints PRO+; free key advertised but endpoint entitlement not tested. No API key collection or paid subscription; no copytrade/automation endpoints. Inspect source provenance and compare first-party events; no double-credit shared upstream.
## Market-class and source acceptance
Native launchpad census first; sources can contribute independently time-stamped observations but no retroactive first-seen; if feed lacks exact pool ID, reject aggregate or preserve ambiguity. Distinguish same symbol vs same CA and competing pools. Discovery recall needs full independent denominator; compare coverage/latency at actual observation clock, not provider claims. Existing MAL#120 current backlog and #77 maturation are prerequisite, not solved by external source. For research alone, run fixed source interop fixtures/authorized free tests of timeouts, 429, 402, stale HTTP200, response schema, duplicate CA, wrong chain; cost cap $0; deterministic retry/backoff already owned. Use TypeAI duplicate CA example and Pumpdata stale status as regressions. New source may be useful historical challenger without live promotion. No chart-only return claim, no live position.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/06_DATASETS_AND_SCIENCE.md | blob 65431e4b77d21abca99438a8768c8f57895531b2 =====
# Part 6 — Reproducible datasets, negative evidence and scientific gate
Date 2026-11-17. Source audit and experiment plan only; no downloaded dataset, no actual new backtest.

## Candidate data
1. Slinky21 Pumpfun_Memecoin_Corpus https://huggingface.co/datasets/Slinky21/Pumpfun_Memecoin_Corpus ; README and KNOWN_ISSUES read directly via raw public pages. CC BY 4.0 with attribution/change indication. Claims 798,430 June 5–July14 launches, 33,581,765 trades, 26,934,864 snapshots plus post-graduation outcomes, migrations and wallet table. Cabal Hunter reports exact same launch count/window, therefore presume possible dataset overlap, never independent confirmations without proof. **Mandatory** reproduce issue handling: Mayhem 2B supply vs 1B default (109,561 affected; use corrected concentration), 1,486 suspect bonding-curve holder leaks (exclude affected feature, retain denominator), 1,136,321 inconsistent SOL amount rows (source filter ratio outside .01–100, stricter sensitivity), 2,360,061 null SOL/price rows (missing vs corrupt), 6,690,901 rows involving System Program contaminating wallet metrics (exclude program from participant counts, investigate trade attribution), Jul3 collection outage and curve overshoot regime break, stale wallet_stats (only 37.7% exact trade-count matches in provider's 100k check; rebuild from eligible trades). Read full current KNOWN_ISSUES and pin revision, reconcile stated row counts/fractions, test raw chain examples before analysis. Use temporal and group splits, no future-labeled postgard features. Download only subset after budget/storage/terms verification. Source: https://huggingface.co/datasets/Slinky21/Pumpfun_Memecoin_Corpus/raw/main/KNOWN_ISSUES.md .
2. MELT formerly MemeTrans: https://arxiv.org/abs/2602.13480 ; https://github.com/git-disl/MELT (old git-disl/MemeTrans README redirects). Dataset card https://huggingface.co/datasets/Zinteck/MELT advertises 41,470 launch traces, 122 engineered features, bundle-level evidence, CC BY-NC 4.0; verify current release/terms, intended use, possible source overlap, sample construction and risk-label mechanics. Noncommercial status must be checked before reuse, no commercial redistribution. Keep labels challenger not economic truth; non-graduates coverage unknown until audit.
3. Pumpwatch frozen 44MB snapshot and SQL, part 3. Use small reproducible study first; checksum verification before any claims.
4. Bitquery Pons Launch Outcomes https://www.bitquery.io/datastore/datasets/pons-launch-outcomes ; provider describes every launch plus first 100 buyers and 7-day outcomes, including never-traded. Advertised $250 month/$750 full: no purchase. Schema useful for reproducing internally from existing Pons native collector. https://docs.bitquery.io/docs/blockchain/Solana/Pumpfun/Pump-Fun-API/ and https://sqd.dev/solutions/memecoins/ documented instruction/event filters, indexed transfers, phase and buy/sell attribution. Entitlement and exact access not verified.
5. Research: https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini (34,988 tokens across four chains per paper abstract; published 82.89% of high-return subset showed manipulative indicators; not every high return and not Pons-specific); reproduction material https://zenodo.org/records/17830944 . https://arxiv.org/abs/2609.10246 covers manipulation families; https://doi.org/10.1184/R1/33420628 large data candidate, not acquired. Academic early-stage/wash/creator evidence is useful as risk detection, never a signal to participate in manipulation. All reports only as source claims until verified.

## Scientific framework for Astra/Fable
Freeze eligible opportunity set and actual first-known feature timestamps; full population denominator independent of score. Distinguish unavailable/censored from actual no-trade and no-exit; include abandoned tokens, rejects, missed detection, route failures and fees; zero profits cannot be assumed from absent prices. Train on past completed outcomes only, rolling origin temporal folds with purge/embargo by horizon, cluster bootstrap by deployer/launch episode and day; hold out entire launcher families and chain/venue, separate model development from one final OOS set. Compare B0 cash/no-trade, B1 transparent age/liquidity/volume, B2 existing Alpha scoring version frozen, then ablate each new feature family. Estimate outcome definitions and prereg rare-event power; precision/recall, PR-AUC, Brier/reliability, lift at fixed watch budget, net liquidatable portfolio return, tail risk, adverse selection, time-to-observation and costs; report covariance and concentration. Multiple hypothesis correction / nested tuning; no hindsight exits, no data-derived threshold promotion from one study. Sensitivity to unknown outcomes, fees, route failure and worst-case slippage; resolve differences between upper-bound gross peak and realistic stateful simulation. Model complexity only if robust increment exceeds simpler baseline, across independent episodes with nonzero full exit evidence. R3 framework firewall remains untouched. Use existing #224 pilot criteria and #1512 Strat/S1 adjudication, no auto promotion.

## Hard blockers and controls
Source capture currently has no eligible independent five-gate success in prior readback; not proof of any operational edge. Source accessibility and provider SLAs not established. Public read-only no user wallets or credentials. No external dataset/paid API spending in this audit. Preserve failed research. No new engine/registry/parallel paper ledger. Source claims require independent raw checks. Compare the next actual time-stamped receipts before any scheduling/implementation. Never send restricted data to public model.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/07_MASTER_ASTRA_FABLE_MISSION.md | blob 9eaeed02f50baad51d25c0774392f552134abc84 =====
# MASTER — Alpha Lab Pro global specialist synthesis / Astra + Fable
2026-11-17. Research only. Decision owner Archive #1512 -> Strategist #1157 -> S1 #1156, existing MAL#38 one heavy lane, original #224 / #88 / #194 / #98 / #77 / #228. No current edge claim. Owner requested multiple specialist packages, not a new parallel scheduler or budget increase.

## Goal
Develop evidence-grounded discovery, identity, risk and execution intelligence for Alpha Lab Pro. Test whether prior observable launch history and independent public wallet behavior improve selection over existing baselines, including short-lived price events, while excluding participation in manipulation and never treating privileged-cohort behavior as trade permission. Capture and retain evidence of recurrent wallets and project/launch provenance, even when longer outcomes fail. Separate horizon-specific outcomes and risk from identity and research prioritization. A 100x chart is an extreme historical outcome, not a promised attainable gain.

## Source pins / entrypoint
Part 1 is the exact original Research Lab comment #1512/6958544303. Parts 2–6 are this session's original analysis, linked public docs, code/README blobs and public API probe summaries. Main at initial TypeAI intake Archive 007eb0944025f5f88abce7a5b502b910535d2339, MAL b9037206e9231a64194c0e9955d40d46c2a3ea23, docs branch base d63826121da173dba7ceaaf0c5b8fe46fb2db648. Fresh-read authoritative main, original programs, open PRs and source receipts before any work. Prior Astra report 06_RESEARCH_LAB/astra_program_20261116/results/alpha_lab/ASTRA_ALPHA_LAB_PRO_PAPER_EDGE_RESEARCH.md blob b1f444a7f23a96d70c9aa9e5f27ee686d2cee4fe (already archived, no re-run) prioritizes first-known, exact identity, full-size exit, denominator and accounting. Original MAL#224 already owns serial launcher; no second mission owner. Existing Fable roadmap Round6/7/9 data-gated; not authorized to start a new round without frozen input and specific approval. Existing current canonical source/state controls override this design.
## Rank by current incremental value (not backtest results)
P0: (A) original census latency+continuity and decision clocks #120/#126; external feed comparisons only after ownership. (B) point-in-time prior-deployer history, counts and outcome quality #224, organic graduation vs self-financed, active vs dead, evidence completeness; early-buy projection excludes linked/privileged operators as independent signals. (C) whole-size exit feasibility and transfer-vs-market-cost attribution #98/#88. P1: (D) metadata exact-fingerprints with negative/common-template controls #126/#194/#105; (E) independent wallet recurrence plus holder distribution and longitudinal persistence #88/#101; (F) chain/venue/age/marketcap/class/time conditioned outcome and missed-winner audit #77/#85; P2: (G) UI/companion evidence projection #228; (H) CN regime conditioned efficacy after genuine paper trades exist. No broad report-first handoff; select at most one primary delta per family, and original three active handoff cap.
## Proposed algorithm building blocks (research candidates)
- Identity and provenance: deterministic chain+CA/mint+typed pool and factory/source keys; effective signer/creator/recipient role; immutable first seen metadata/digests; unknown/ambiguous refusal; no danger score compensation.
- Deployer history: hierarchical shrinkage of mature as-of counts, prior genuine activity/graduation ratio, sample size and coverage, historical peak distribution vs liquidatable outcome distribution and persistence, launch cadence/change points, after-cost risk profile. Separate maker activity from repeatable outsider opportunity and from manipulation risk. No individual ranking until validated.
- Relationship/early participation: typed graph with evidence timestamps, negative controls and entity uncertainty; independent participant count/capital, duration and retention normalized by launch phase, size and turnover, classify free distributions separately; coordination evidence may indicate extraction risk/abstention. No strategy to join, signal or profit from coordinated manipulation; no live wallet tracking of suspected actors beyond authorized public forensic evidence.
- Outcome: event-to-observation and data-availability clocks; stateful route simulation for full position, standardized size buckets already owned (including refusal/no-fill/no-exit), costs once, opportunity/cash benchmark and uncertainty. Gross 2x/5x/10x/50x/100x labels descriptive; never conflate price with realizable capital. Competing risk survival models with censoring; logistic / regularized additive baseline before tree or graph models; reserve complex methods for validated incremental lift.
- Product: display identities, relationship evidence without accusation, independent risk and alpha/quality, outcome/cost evidence, missingness, source coverage and timestamps. Source-safe projection only, no new public release, no false real-time claims. Historical case memory separated from live observation. No new live transaction capability.
## Bounded Astra Work question
Can existing Alpha mechanisms be improved using the above three highest-value independent source ideas rather than building new systems? Use all parts plus actual existing code and test receipts, not just reports. Why heavy: temporal/identity/economic provenance cross-layer reconciliation; deterministic public data first. Work ceiling xhigh, API budget $0 unless separately approved under current governance. Freeze exact input manifest and max data/requests; no direct tool available in this thread to invoke a served Astra/Fable model; NOT_DISPATCHED. Existing daily/one-heavy lane and Research Lab controls decide admission. Deliver: (1) overlap matrix of actual code, tests and source state vs each candidate; (2) reproduce top documented source pitfalls with original-owner fixtures, before/after evidence; (3) candidate algorithms with inputs/units/missingness/baselines/formulas and falsifiers; (4) candidate data qualification/availability and rights; (5) preregistered evaluation split/holdout and sample/power justification; (6) small existing-owner implementation packet(s), tests, risk and expected decision value. Select the minimum useful change. No self-scientific promotion or paid invocation from this packet.
## Fable follow-on build/review input
Only after Astra deliverables exist, source-pinned and independently accepted, plus original roadmap/gates and explicit GO: audit causal assumptions, leakage, graph false links, data completeness, execution accounting and failure cases; choose the smallest algorithm improvement with proof. Generate patch draft to existing owner, never new trading engine; no signing, private key, automatic live orders or permission escalation. Include unit/property tests: wrong chain, duplicate pools, migrations, template collisions, program/vault/bridge conflation, API null/stale/429, time-order with same-block events, unknown history, transfer accounting, no-fill/partial/no-route/full exit, fees/decimals, public leak and replay/hindsight guard. Independent review, CI exact head, governed merge and readback, actual prospective outcome required before any validated signal claim. Fable's current availability and served-model proof not checked; do not claim invocation.
## Exit and stop
Every hypothesis gets original owner and #1512 disposition. Retain rejected/negative results; use original case-memory and source registries only if admitted. Stop source research when incremental expected value drops, upstream duplicates or rights/coverage unresolved. If no qualified source or heavy lane available, report exact trigger. Current research stage: intake/source triage only; no dataset acquired, no new backtest, no model dispatched, no change to scanners, rules, data or paper wallets. Public-sourced claims distinguished from hypothesis; timestamps/raw hashes missing for probes, no prospective credit.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/alpha_lab/2026-11-17__global-specialist-dissection/README.md | blob 00ccdf7977a73ef9955141fa6d96d47a80b81070 =====
# Global specialist research package — Alpha Lab Pro, 2026-11-17
Owner-requested collection and synthesis; research-only draft evidence. Original #1512 and existing owners govern. No new queue, workflow, trading permission or paid model call. Part 1 retained from original public issue verbatim; parts 2–6 are source-specific studies; part 7 is curated master mission (NOT_DISPATCHED). No dataset backtest performed; provider claims are not independently validated. Read in order:
- [01_TYPEAI_ORIGINAL.md](01_TYPEAI_ORIGINAL.md)
- [02_DEPLOYER_HISTORY.md](02_DEPLOYER_HISTORY.md)
- [03_LAUNCH_FINGERPRINTS.md](03_LAUNCH_FINGERPRINTS.md)
- [04_WALLET_NETWORKS.md](04_WALLET_NETWORKS.md)
- [05_DISCOVERY_CHAIN_REGIMES.md](05_DISCOVERY_CHAIN_REGIMES.md)
- [06_DATASETS_AND_SCIENCE.md](06_DATASETS_AND_SCIENCE.md)
- [07_MASTER_ASTRA_FABLE_MISSION.md](07_MASTER_ASTRA_FABLE_MISSION.md)
This package does not override current repo contracts or grant release authority. No raw private data or credentials.
===== END SOURCE =====

===== SOURCE 06_RESEARCH_LAB/astra_program_20261116/results/alpha_lab/ASTRA_ALPHA_LAB_PRO_PAPER_EDGE_RESEARCH.md | blob b1f444a7f23a96d70c9aa9e5f27ee686d2cee4fe =====
# Alpha Lab Pro: execution-truth research and paper-wallet architecture

**Supplied source-main:** `82f6cd830fbcd26d77e043da0ad3222abd7cae92`  
**Disposition:** **DESIGN_AND_RESEARCH_ONLY — NOT IMPLEMENTED, NOT PERSISTED, NO TRADING AUTHORITY**

## Executive finding

The supplied evidence supports a disciplined research architecture, but **does not establish a profitable Alpha Lab strategy, verified paper returns, or superiority over a simple executable baseline**.

In particular:

- Matched original v4 **decision → fill → exit → costs** records are absent.
- The site handoff reports **zero verified full exits in its reviewed paired-ledger census**. That is a source assertion about that census—not proof that no exits exist anywhere.
- Historical winners, screenshots, market-cap changes, project quality, wallet labels and graduation outcomes cannot substitute for executable, costed returns.
- Five separate paper wallets can be specified realistically, but they cannot be activated by silently creating the scanner, scorer, ledger, wallet sensor or scheduler that existing contracts prohibit.
- The highest-value next work is **denominator integrity, original first-known clocks, exact identity, full-size exit evidence and deterministic execution accounting**, not another alpha score.

**Current conclusions**

| Question | Finding |
|---|---|
| Did original v4 generate realized profits? | **NOT_EVALUABLE** |
| Did original v4 generate independently verified paper profits? | **NOT_EVALUABLE** |
| Do wallet precursors outperform public price/liquidity information? | **HYPOTHESIS; not demonstrated here** |
| Can project research identify interesting candidates? | Historical examples support investigation, not trading edge |
| Are manual discoveries proven scanner misses? | Not without original eligibility and discovery logs |
| Is launch-origin information potentially useful? | Plausible risk information; profitability remains unproven |
| Can a realizable paper architecture be designed? | Yes, conditionally, through existing owners and approved extensions |
| Is a public, near-live Alpha Lab Pro feed established? | Not by this packet |

### Scope and verification limits

I used only the supplied text. **No tools, execution, repository reads, private access, independent SHA verification or deployment inspection occurred.**

Throughout:

- **SUPPLIED FACT** means explicitly stated in a supplied file.
- **SOURCE ASSERTION** means the file reports an external or operational condition not independently reproduced here.
- **HYPOTHESIS** means a falsifiable research proposition.
- **PROPOSAL** means a future design, not an approved implementation.
- **UNKNOWN** is not zero, false, safe or failed.

Required current cockpit, boundary, registry, skill and private binding files were not supplied. Consequently, this report does not certify current authority, current issue status or implementation readiness. Work requiring unavailable private authority must remain blocked as `PRIVATE_DATA_AUTHORITY_UNAVAILABLE`; the public-only architectural analysis can still proceed.

---

# 1. Exact supplied-source register

These hashes are reproduced from the packet, **not independently recomputed**.

| Ref. | Supplied file | Supplied SHA256 |
|---|---|---|
| **S1** | `AGENTS.md` | `4c2cc641e35e07e49e31d16b6aa960bbf6ceb4bd1ae1eb9fb05b2f53d275093a` |
| **S2** | `04_RESEARCH_LAB/external_specialist_dissection/2026-11-10__ALPHA_LAB_PRO_EXECUTION_TRUTH_SITE_CONSUMER_V1.md` | `950d5073fb6635b023638ab06bf6f8f88e18f054fdfaa945a20b550f5d60620a` |
| **S3** | `06_RESEARCH_LAB/alpha_lab/2026-10-02__wallet-precursor-execution-fidelity-prospective-experiment-v1__prereg.md` | `3315aab2d37da3cfd49fd614537e42dcfa5f40d70de4b5a9efaa54236d077432` |
| **S4** | `06_RESEARCH_LAB/alpha_lab/ALPHA_LAB_PROSPECTIVE_EDGE_EXPERIMENTS_v1.json` | `82fdd3353d6be9d6d8211840aefb421bd1d43623cc08f03394a32e6e946efce5` |
| **S5** | `research/api_agent/meme_alpha/experiments/RH_HISTORICAL_MATCHED_DENOMINATOR_v1.json` | `d8c66eb11e9d3ccf5c0df3c8a14d68a0c2b55fb6c27d522c29064ae4025c9ebf` |
| **S6** | `research/api_agent/meme_alpha/experiments/PONS_V2_LAUNCH_ORIGIN_MATCHED_DENOMINATOR_v1.json` | `ab2ae85ba5be546a9b25d818a7c21da6b474614d6866fb9b251863ab70fc6802` |
| **S7** | `research/api_agent/meme_alpha/MEME_ALPHA_PROSPECTIVE_HARDENING_v1.json` | `9c73abd1becc962fe242aa197e656646872dd924b8820a85ea7d570d09f0936a` |
| **S8** | `06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-16_ASTRA_HIGH_W46W47_ORIGINAL_RESEARCH_UNAUDITED_v1.md` | `981ce1be3655a031810aba7c7f79044ed923b0c608d509ce54fa3bd9f3bce864` |

**Naming caution:** “S4” above is a citation label. It is **not** an assertion about the operational S4 owner mentioned in the request. That owner’s runtime contract is not included.

---

# 2. Source-by-source assessment

## 2.1 S1 — repository governance

### What it establishes

The supplied governance requires:

- Existing owners and current source authority first.
- Private evidence bound to exact commit, path, bytes, SHA256, contract, timestamps, schema and completeness.
- No public copying of restricted values.
- Prospective inputs frozen before outcomes.
- Separate row validity, coverage readiness and promotion.
- No new engine, scoring concept or duplicate forward test without an explicit canonical exception.
- Existing research-to-Codex intake rather than self-declared `CODEX_READY`.
- No new autonomous authority over trading, wallets, payments or recovery.
- Round 3 remains **`PROSPECTIVE_COLLECTION_ONLY`**, with hypothesis testing and outcome scoring **OFF**. [S1]

### Architectural consequence

This report is **not authorization to build a new “scientific scanner.”** Its capabilities should be implemented, if approved, as repairs or bounded extensions to the existing discovery, identity, quote and outcome owners.

Likewise, “five paper strategies” must first be reconciled with the active registry and existing Strategy Arena. They are not five automatically admitted experiments.

The supplied governance contains several conditional release mechanisms. Their existence in this text does not prove their activation prerequisites or current switches. Nothing here claims merge permission.

---

## 2.2 S2 — Exit Truth and site consumer handoff

### What it establishes

The handoff explicitly labels itself conceptual:

- No public schema update.
- No active realtime feed.
- No site release.
- Source/privacy blocks on qualifying token scans and wallets.
- Eight existing Strategy Arena arms remain research-only.
- Zero verified full exits in the reviewed sellability/outcome census.
- Quotes are **estimates**, not executions. [S2]

### Diagnosis

The product architecture is directionally sound because it distinguishes:

1. Spot mark;
2. Sized executable-quote estimate;
3. Controlled simulation;
4. Original historical transaction;
5. Unsupported or unobservable evidence.

However, the product is only as honest as its admission rules. A polished “Exit Reality” card can still mislead if:

- A tiny sell is treated as evidence for a full-position exit;
- A buy route is treated as a sell route;
- A historical route is treated as currently available;
- Pons curve availability is confused with post-graduation DEX availability;
- The browser fetch clock is displayed as source freshness;
- An aggregator response is treated as independent execution proof.

**Required interpretation:** “PASS” must describe a particular test, amount, route and timestamp—not a token’s permanent safety.

The original source owners named in S2 remain relevant: #120 lineage, #194 pool identity, #98 mechanics/quotes, #77 outcomes, #228 site, and #196 privacy/export. Those identifiers belong to the Meme Alpha context described by the source and should not be confused with Archive issue numbers.

---

## 2.3 S3 — wallet precursor and execution fidelity preregistration

### What it establishes

This is a preregistered shadow experiment with:

- Parent #1087;
- Denominator/outcome owner #1340;
- No trading or automatic execution;
- No new scanner, scorer, ledger or scheduler;
- Historical HOOKED seed receiving zero prospective credit;
- A contract-reconstruction hypothesis;
- An explicit execution-fidelity schema. [S3]

### HOOKED: positive control, not performance proof

The screenshot-derived values are not sufficient to reconstruct a trade:

- Approximate first alert cap: $406.8K;
- Later screenshot cap: $5.084M;
- Displayed gain: +1,671.5%;
- 77 buyers;
- 10 saved/identified profiles.

The two approximate cap values imply roughly **12.50× capitalization**, or about **+1,150%**, not +1,671.5%. This does not prove fabrication: the displayed gain may use another price, timestamp, supply definition or reference. It does demonstrate that these fields **cannot safely be combined into a return calculation**.

Neither 77 buyers nor 10 labelled profiles establishes 77 or 10 independent economic actors.

### Robinhood contract: attribution first

The supplied preregistration identifies:

`[PUBLIC_ADDRESS_OMITTED_09]`

as an **executor/strategy contract**, not a smart-money EOA. The alleged 53 episodes and 33 target wallets remain external claims. [S3]

The decisive reconstruction must establish:

- Which public event was observable;
- When it became available to an ordinary observer;
- Whether the contract acted before or after that availability;
- Whether apparent target relationships survive router, bridge, exchange and common-service exclusions;
- Whether costs and exits remain favorable after realistic delay.

If its advantage requires earlier private intent or privileged transaction ordering, it is **not a replicable public-discovery edge**.

### Important boundary

`WALLET_PRECURSOR_EVIDENCE` is observational. It cannot independently authorize BUY/SELL, sizing or execution. The proposed paper designs below do not convert it into production action authority.

---

## 2.4 S4 — prospective edge experiment registration repair

### What it establishes

The contract is `REGISTRATION_REPAIR_RESEARCH_ONLY`, not a completed experiment. It names #1087, #1134 and the existing private ledger root.

Crucially:

- `scorer_path: null`;
- `score_status: SCORE_METHOD_UNFROZEN_NO_SCORING_AUTHORITY`;
- E2 is **`HOLD_NO_SENSOR`**. [S4]

### E1: disclosed address → deployer correspondence

Two additional independent prospective confirmations can support the specific address-correspondence proposition. They cannot establish:

- Profitable entry;
- Sellability;
- General project quality;
- Owner identity;
- A wallet strategy.

Also, `receipt.from`, factory caller, contract creator, beneficiary and project operator can differ. Exact matching must retain those distinctions.

### E3: CA-publication timing

The correct endpoint is a source-bound publication lead/lag relative to a clearly defined T0 and external observer.

Unresolved requirements include:

- Sign convention for `delta_publish`;
- Meaning of T0;
- Whether publication time is exact or interval-censored by polling;
- Original archive coverage of the frozen surface;
- Actual collector and consumer delays.

A first changed capture at 12:05 after an unchanged 12:00 capture means publication occurred in an interval—not necessarily at 12:05.

“Verified-before-public” must not become credit for nonpublic information. The research should distinguish **public first-party availability before broader dissemination** from private access.

### E4: dev-buy OOS lift

The stipulated ≥1.5× fresh OOS lift is a criterion for that registered endpoint. It does not automatically mean ≥1.5× profit or favorable execution economics.

A reproducible launch denominator and genuinely as-of dev-buy measurement are prerequisites. No discovery-sample threshold fitting is admissible.

### Consequence

The requested ranking, simulator and wallet proposals remain **unactivated specifications** until existing governance admits them. E2’s prohibition is not bypassed by renaming a wallet sensor “graph enrichment.”

---

## 2.5 S5 — Robinhood historical matched denominator

### What it establishes

Twelve historical design rows are supplied; all have `framework_prior_match: false`. Five contain token CAs; seven do not. All have zero prospective credit. [S5]

### Source-specific interpretation

| Cases | Proper research role | What cannot be inferred |
|---|---|---|
| Boost Town, MEEP | Visibility-gap leads with asserted product/token features | Timely scanner miss, verified product quality or profitable token |
| QLWY | Identity-complexity control | Bridged token equals new native launch; cross-chain supply can be added indiscriminately |
| OldSchool Finance | Project-memory lead | Directory token label establishes a tradable canonical token |
| RobinFlow, Oasis Protocol, lpTOKEN.fun, Neon Mech Legion | Product/no-token or token-not-established controls | Good product implies investable token |
| Golden Arrow | Prelaunch narrative/control | Fair-mining/no-premine claim proves fair access or eventual launch |
| Margin Hood, BiX Robin | Narrative/presentation controls with CA | Polish, AI language or exact CA is alpha |
| Sheddr | Weak-identity/project-surface control | Discovery-product narrative establishes token identity |

**Critical correction:** twelve `framework_prior_match: false` values do not establish a 100% scanner miss rate. We lack the original search universe, scanner state, timestamps and eligibility rules.

These rows are valuable for investigating **where discovery coverage failed**, but not for scoring recall without those missing records.

No-token controls should remain in project-discovery denominators without being assigned fabricated token returns.

---

## 2.6 S6 — Pons V2 launch-origin denominator

### What it establishes

The source records TAGPAD, DEED and FLYBRAIN as historical seeds, labels the naive standalone hypothesis falsified, and proposes an outcome-blind factory sample. [S6]

That reported falsification is not independently reproduced here, but the refined question is appropriate:

> Does the degree and behavior of privileged launch access add risk information beyond simple public launch characteristics?

### Main temporal trap

Fields measured over `T0…T5M` are **not T0 entry features**.

Similarly:

- First-hour sell-through cannot select an entry at minute five.
- Twenty-four-hour creator behavior cannot classify launch-time skill.
- Later proceeds convergence cannot retroactively establish a known common owner.

Each feature needs its own availability time.

### Main causal trap

Exemption count, template recurrence and deployer frequency may describe launch mechanics without proving malicious intent.

The useful distinction is:

- **Capability:** privileged transfer or trading rights;
- **Exposure:** supply controlled by privileged actors;
- **Behavior:** actual sales/transfers observed by decision time;
- **Outcome:** later economic loss or unsellability.

Those are different objects.

---

## 2.7 S7 — prospective hardening

### What it establishes

This is the strongest supplied denominator discipline:

- Frozen ecosystem intake before token search;
- Unique ecosystem trials as the method-review denominator;
- Artifacts and token matches do not inflate it;
- No-token matches remain counted;
- Matched controls frozen before outcomes;
- Missed-winner audit;
- Minimum 20 matured ecosystem trials before method-review kill criteria. [S7]

### Important distinctions

The contract has at least three legitimate units:

1. **Ecosystem trial** — method-level evidence;
2. **Token match** — asset-level discovery/execution evidence;
3. **Trade episode** — paper-wallet accounting.

They must not be pooled into one apparent sample size.

The missed-winner definition uses:

- Minimum seven-day executable multiple of 2×;
- At least $50,000 liquidity at first eligible observation;
- $1,000 minimum test exit notional.

A small $100 simulated trade does **not** demonstrate the $1,000 missed-winner exit criterion.

Twenty matured trials is a review gate, not a statistical power guarantee. “Unacceptably low recall” still requires a frozen quantitative acceptance rule before confirmatory assessment.

---

## 2.8 S8 — unaudited cross-domain research assessment

### What it establishes

Its Alpha section explicitly identifies missing original decisions, sizes, fills, exits, capacity, costs and matched cohorts, and declares G3/G5 economics not evaluable. [S8]

### Proper use

This is a useful methodological warning, not independent Alpha execution evidence.

Its BTC/ETH forecast analysis cannot:

- Validate an Alpha token strategy;
- Supply Alpha trade costs;
- Repair original wallet chronology;
- Demonstrate that adding CN improves Alpha economics.

Any future Alpha-plus-CN experiment must freeze a separate read-only context treatment and compare it with an identical Alpha baseline. Current CN context is not permission to create a second market-state engine.

---

# 3. Discovery denominator and first-seen architecture

## 3.1 Maintain four linked universes

A single “tokens discovered” counter is insufficient.

| Universe | Unit | Required preservation |
|---|---|---|
| **Ecosystem intake** | Frozen eligible ecosystem trial | Selected, excluded, deferred, no-token, no-launch |
| **Project discovery** | Project or project-version candidate | First public surface, manual additions, rejects, unresolved identity |
| **Launch universe** | Canonical launch/token incarnation | All independently enumerated eligible launches, including unobserved-by-scanner cases |
| **Paper opportunity** | Candidate × strategy decision opportunity | Enter, reject, wait, unavailable, missed due to latency, quote/fill failure |

Link these through existing #1340 row semantics. Do not create an independent denominator engine.

A project without a token belongs in discovery evaluation. It does not belong in a fabricated token-return average.

## 3.2 Preserve distinct clocks

For each material event, retain:

1. `event_chain_time` and block/slot reference;
2. `public_surface_available_at`, if independently establishable;
3. `collector_received_at`;
4. `machine_first_seen_at`;
5. `identity_verified_at`;
6. `decision_posted_at`;
7. `consumer_received_at`, where applicable;
8. `quote_requested_at` / `quote_received_at`;
9. `earliest_simulated_inclusion_at`.

**Never replace machine first-seen with block time or a later reconstructed publication time.**

A historical transaction can prove that an event occurred. It cannot prove that the original scanner knew it then.

A conservative eligible-action clock is:

\[
t_{\text{eligible}}
=
\max(
t_{\text{source available}},
t_{\text{machine received}},
t_{\text{identity verified}},
t_{\text{required features available}}
).
\]

An unknown required clock produces `FIRST_KNOWN_UNVERIFIED`, not an optimistic estimate.

## 3.3 Manual-found miss audit

Every manually supplied candidate should receive:

- Original manual submission receipt;
- Whether the submitter already knew the outcome;
- Whether it was in the frozen scanner universe;
- Whether adequate original source coverage existed;
- Original machine discovery state;
- Original CA-binding state;
- First time it was actually executable;
- A reason-coded comparison.

Recommended miss taxonomy:

| Classification | Meaning |
|---|---|
| `OUT_OF_SCOPE` | Outside frozen universe; coverage limitation, not automatically a scored miss |
| `SOURCE_NOT_COVERED` | Relevant public source absent from existing coverage |
| `COLLECTOR_GAP` | Covered source not captured adequately |
| `SEEN_LATE` | Captured only after the useful window |
| `IDENTITY_UNRESOLVED` | Project seen, correct token not bound |
| `FILTER_REJECTED` | Seen but rejected by frozen selection |
| `QUEUE_LATENCY_MISS` | Valid candidate became unactionable while waiting |
| `NO_EXECUTABLE_ROUTE` | Attractive mark, but no admissible entry |
| `EXIT_CAPACITY_MISS` | Buy possible, required exit size unsupported |
| `RETROSPECTIVE_WINNER_LEAD` | Submitted after success became known |
| `TRUE_TIMELY_DISCOVERY` | Original receipts establish timely discovery and eligibility |

A rejected candidate that later qualifies as a winner still counts against the relevant frozen recall measure. However, a pump that was never sellable at the required size is not an executable winner.

### Prevent the manual sample from becoming another winner list

Use both:

- Systematic outcome-blind sampling of eligible launches/projects;
- A separate missed-winner audit with known selection logic.

Do not estimate population precision from a manually selected winner panel. If sampling probabilities are known, weighted estimates may be possible; otherwise describe the panel rather than generalize it.

## 3.4 Honest denominator reporting

Report separate counts for:

- Complete source windows;
- Partial/truncated windows;
- Unknown coverage;
- Timely discoveries;
- Late discoveries;
- Rejected candidates;
- False bindings;
- No-token and never-launched projects;
- Quote failures;
- Sellability failures;
- Mature outcomes;
- Pending and missing outcomes.

Recall can only be estimated relative to an independently reconstructed, bounded universe. “Recall across all microcaps” is not available from a partial directory or a successful-project list.

---

# 4. Scientific scanner capabilities: what to measure and how to falsify it

These are **capabilities of existing owners**, not authorization for another scanner.

| Domain | Point-in-time construction | Main failure mode | Falsification test |
|---|---|---|---|
| **CA binding** | Chain + exact CA/mint + deployment/program identity + first-party/on-chain linkage | Ticker collision, fake CA, bridge/native confusion | Inject plausible same-name wrong-chain tokens; all must fail binding |
| **Launch timing** | Separate deployment, initial funding, public trading, sell opening, graduation and DEX opening | One ambiguous T0 hides inaccessible launch access | Recompute lead against each relevant public tradability clock |
| **Project skill** | Timestamped shipped product, usage evidence, token economic linkage, verifiable mechanism | Good product but worthless/unnecessary token | Include equally good no-token and failed-token controls |
| **Social/prelaunch** | Archived first-party statements, content hashes, observed publication intervals | Deleted/edited posts and later success backfilled into early state | Outcome-blind surface census, including abandoned projects |
| **Wallet roles** | Versioned role labels and evidence edges | Routers/CEX services counted as coordinated smart money | Remove infrastructure; apparent convergence should survive |
| **Entity independence** | Evidence-weighted common-control hypotheses | Common funder or service treated as proof | Re-run with ambiguous clusters split and merged |
| **Bundle/sniper exposure** | Public transaction order, privileged access, early supply capture | Same-block buys assumed to be a bundle or one actor | Require direct bundle evidence or retain “co-timed/unknown” |
| **Deployer history** | Only launches and outcomes known before decision | Future success/failure contaminates prior reputation | Future-launch injection must be rejected |
| **Liquidity health** | Executable depth, concentration, removal rights, route continuity | TVL or wash volume mistaken for exit capacity | Full-size sells across removal/volatility stress states |
| **Sellability** | Exact-size reverse quote and supported contract semantics | Tiny test sell extrapolated to full exit | Increasing-size quotes and adverse-state fixtures |
| **Taxes/admin risk** | Transfer hooks, blacklist, pause, mint, upgrade, dynamic tax rights | Current low tax treated as permanently low | Admin-state-change scenarios; unsupported behavior fails closed |

## 4.1 Identity specifics

### EVM

Identity should include:

- Chain ID;
- Token address;
- Deployment reference and code hash where relevant;
- Proxy/implementation relationship;
- Decimals and quote-asset identity;
- Factory/pool provenance.

For Uniswap v4, pool identity requires the relevant **PoolManager and PoolKey**, including currencies, fee, tick spacing and hooks. A token address plus “Uniswap v4” is not sufficient.

### Solana

Use:

- Exact mint;
- Token program;
- Decimals;
- Mint/freeze authorities;
- Relevant transfer-fee or transfer-hook extensions;
- Pool/program identity.

Do not map EVM execution assumptions onto Solana because both venues show a USD price.

### Bridged tokens

Preserve origin and destination identities, bridge representation and supply semantics. Do not double-count circulating supply across chains or classify a bridge deployment as a new economic asset without evidence.

## 4.2 Wallet graph: roles before reputation

Useful role classes include:

- Deployer/factory caller;
- Project treasury;
- LP manager;
- Executor contract;
- Router/aggregator;
- Bridge;
- Exchange/service cluster;
- Arbitrage/MEV participant;
- Independent investor candidate;
- Unknown.

Edges must carry:

- Evidence type;
- Chain/time;
- First-known time;
- Confidence;
- Whether they imply common control or only interaction.

**Common funding is evidence, not conclusive identity.** A shared exchange withdrawal source is especially weak.

Wallet “skill” must be measured from an as-of history containing losses, rugs, unsellable positions and skipped/reverted attempts. Current labels cannot be projected backward.

## 4.3 Bundle snipers and privileged access

The research question is not “Are snipers present?” They are common in many launches.

The relevant questions are:

- How much economically independent supply was available to ordinary entrants?
- Did privileged actors receive materially different taxes or timing?
- How concentrated was early ownership after infrastructure filtering?
- Had distribution already started by the proposed public entry?
- Does the observed public-entry outcome survive realistic delay?

No trading system here should reproduce sandwiching, private-intent exploitation or manipulative execution. Such observations may be used to model risk and deny unrealistic public-entry credit.

## 4.4 Microcap project skill versus token speculation

A serious project thesis needs three independently testable links:

1. **The product exists and works.**
2. **The token has a defined economic relationship to that product.**
3. **An outsider can enter and exit at attractive net terms.**

Failure of any link breaks the investment thesis.

A polished product may generate no token demand. A useful token may be overvalued. A cheap token may be unsellable. None of these distinctions is resolved by historical market-cap expansion.

---

# 5. Five independent paper-wallet proposals

## 5.1 Admission and independence

The five designs below are **proposed experimental policies**, not existing approved strategies.

Before activation:

- Reconcile them with the eight existing Strategy Arena arms.
- Reuse an existing compatible arm where possible.
- Otherwise require a separately approved amendment through #1087/#1340/#1134 and the actual active-test owner.
- Do not overwrite existing freezes or present these as original v4.
- Keep scoring OFF where the current contract requires it.
- Exclude Round 3 from outcome scoring.

### Wallet separation

Use five **virtual accounting identities**, not blockchain wallets:

- `PAPER_MOONSHOT`
- `PAPER_SWING`
- `PAPER_MOMENTUM`
- `PAPER_CONSERVATIVE`
- `PAPER_EVENT`

No keys, seed phrases, signing, approvals on-chain or transaction submission.

Each wallet has independent:

- Starting capital;
- Cash and native-gas subledgers;
- Positions;
- Policy version;
- Decisions;
- Costs;
- Drawdown;
- Opportunity-cost benchmark.

No transfers or rescue capital between wallets.

**Separate wallets do not make their outcomes statistically independent.** Shared tokens, deployers, events and market regimes must be clustered.

### Proposed sizing convention

For comparability, the table uses a hypothetical **$10,000 starting accounting value per wallet**. This is a design parameter, not a recommendation or observed balance.

Chain-specific cash and native-gas allocations must be frozen before a run. There is no instantaneous free cross-chain movement.

All numerical thresholds below are **untested candidate parameters**. They must be frozen before OOS collection, not optimized on the supplied winners.

## 5.2 Selection, holding policy and risk budget

| Wallet | Proposed selection | Position/exposure limits | Exit policy at available observations |
|---|---|---|---|
| **1. Asymmetric moonshot** | Public trading age 15 min–24 h; verified circulating cap $100K–$3M; liquidity ≥$50K; exact CA; plausible token economic mechanism; supported full-size entry/reverse quote; no dependence on privileged access | ≤$100 per position; ≤3 concurrent positions; no averaging down | Intended maximum hold 7 days; attempt 50% exit at 2× net liquidation value, 25% at 4×, remainder at time exit or 35% trailing decline; full-loss risk remains possible |
| **2. 1–3 day swing** | Age ≥24 h; cap $1M–$25M; liquidity ≥$250K; positive completed 24 h trend; 5–15% pullback from prior completed 6 h high; no material sellability deterioration | ≤$250 per position; ≤4 positions; no averaging down | Full exit on +30% or −15% net liquidation return; otherwise intended 72 h exit |
| **3. 5–7 day momentum** | Age ≥7 days; cap $5M–$100M; liquidity ≥$1M; positive completed 72 h trend and completed-hour breakout above preceding 72 completed-hour closes; adequate source history | ≤$300 per position; ≤3 positions | At 120 h exit if completed 24 h momentum is non-positive; otherwise intended 168 h exit; earlier −20% loss or 25% trailing-decline trigger |
| **4. Conservative larger-cap** | Age ≥90 days; verified circulating cap ≥$250M; liquidity ≥$10M; supported standard mechanics; adequate 30-day history; completed daily close above prior 30-day moving average; no known material identity/route impairment | ≤$500 per position; ≤4 positions; no leverage | Intended 28-day hold; earlier −12% net liquidation trigger or source-qualified material impairment; no discretionary extension after disappointment |
| **5. Event/catalyst** | First-party, timestamped catalyst publicly scheduled ≥24 h in advance; exact CA already established; age ≥7 days; cap ≥$5M; liquidity ≥$500K; no nonpublic dependency | ≤$100 per position; ≤3 positions | Enter only in frozen window 6–2 h before event; missed window means skip. Exit 24 h after scheduled event, cancellation, −15% loss, or 72 h after entry, whichever trigger first becomes observable |

### Qualifications

- Market cap requires defensible circulating-supply semantics. FDV is not silently substituted.
- A liquidity threshold alone never satisfies executable-depth requirements.
- Stops and profit targets are **instructions to attempt an exit**, not guaranteed fills.
- Partial moonshot exits incur their own gas and route costs.
- “2×” is net liquidation value relative to fully costed entry, not a spot-price or market-cap doubling.
- The momentum breakout excludes the current bar from the historical maximum.
- The event schedule is frozen. A postponed catalyst does not reset the clock automatically.
- Wallet/precursor information remains an observational challenger until separately authorized; it does not independently create a trade instruction.

## 5.3 Execution constraints by wallet

All five use the common execution model in Section 7.

| Wallet | Proposed minimum decision-response delay* | Maximum modeled own-trade impact per side | Additional adverse-move tolerance** | Initial estimated round-trip cost ceiling | Transfer-tax policy |
|---|---:|---:|---:|---:|---|
| Moonshot | 120 s | 2.0% | 1.0% | 8% of entry notional | Known supported taxes only; ≤2% combined buy/sell transfer taxes |
| Swing | 300 s | 1.0% | 0.75% | 4% | ≤1% combined |
| Momentum | 900 s | 0.75% | 0.50% | 3% | ≤0.5% combined |
| Conservative | 1,800 s | 0.25% | 0.25% | 1% | No transfer-tax token |
| Event | 300 s | 1.0% | 0.75% | 4% | ≤1% combined |

\* **Design floors, not measured execution latency.** Actual source, existing workflow, decision, quote and chain delays can be longer and always dominate. These values do not imply a new monitoring cadence.

\** Separate from price impact. The transaction’s `minOut` must be derived from the net quote and frozen tolerance. Do not subtract the same impact twice.

The cost ceiling includes:

- DEX fees;
- Own-trade price impact;
- Expected gas and necessary approvals;
- Chain-specific settlement costs;
- Supported transfer taxes;
- Frozen adverse-selection/MEV stress allowance.

An unknown mandatory cost or route component means **not executable under the primary model**.

Small positions on expensive chains may systematically fail the cost ceiling. That is an honest result, not a reason to omit gas.

## 5.4 Drawdown controls

Proposed wallet-level pause thresholds:

- Moonshot: 8%;
- Swing: 6%;
- Momentum: 8%;
- Conservative: 5%;
- Event: 5%.

A breach freezes new entries and invokes the frozen risk-exit policy for existing positions. It does not erase holdings or guarantee liquidation.

These are **control thresholds, not maximum possible losses**. Gaps, rugs, dynamic taxes, route disappearance and gas costs can produce larger drawdowns.

Position sizing must therefore treat the entire microcap principal as potentially lost. A −15% stop does not justify sizing as though loss were capped at 15%.

## 5.5 Opportunity cost

For every wallet, freeze:

1. **Cash benchmark:** same starting capital, explicit quote-asset risk, no invented yield.
2. **Simple public-market baseline:** identical universe, timing, capacity and costs, without the proposed project/wallet/catalyst feature.
3. **Capital-lockup measure:** return per capital-day and idle-cash fraction.
4. **Rejected-opportunity audit:** outcomes of qualifying rejected candidates, without pretending the wallet could buy them all.

Comparisons must use the same initial capital and concurrency constraints. A fully invested benchmark and a mostly cash moonshot wallet answer different questions; report both total-wallet and deployed-capital results.

---

# 6. Ranking, evidence confidence and decision posting

## 6.1 Do not introduce an unsupported alpha score

The current evidence provides no justified predictive weights, probability calibration or scoring authority. [S1, S4]

For a future approved research specification, prefer:

### First: hard eligibility gates

1. Correct identity;
2. Public-eligible information;
3. Sufficient source completeness;
4. Supported chain/venue;
5. Valid sized buy and reverse-quote model;
6. Acceptable costs/capacity;
7. Strategy-specific eligibility;
8. Available wallet capital.

### Then: deterministic within-strategy ordering

Use the frozen primary feature, followed by:

- Earlier public-eligible time;
- Better admissible execution coverage;
- Canonical token identity as final tie-breaker.

Possible primary features:

- Moonshot: source-backed token-mechanism evidence tier;
- Swing: frozen pullback condition;
- Momentum: normalized completed-window momentum;
- Conservative: executable depth/cost quality;
- Event: catalyst verification tier and proximity within the allowed window.

This is a **proposed research ordering**, not an activated production scorer.

Do not combine missing evidence with positive evidence in a weighted average that allows a strong narrative to compensate for unknown sellability.

## 6.2 Confidence should be a vector

Report separately:

| Dimension | Examples |
|---|---|
| Provenance | Unattested / original receipt / independently reproduced |
| Timing | Unknown first-known / bounded interval / exact original capture |
| Identity | Unresolved / corroborated / deterministic binding |
| Coverage | Gap / partial / full eligible window |
| Execution | Spot-only / sized quote / deterministic simulation / original transaction |
| Statistical support | Anecdotal / exploratory / OOS inconclusive / independently reviewed |

No conversion to “82% chance of success” is justified.

## 6.3 Required posted decision

Before any simulated entry, append an immutable decision containing:

- Existing row and experiment IDs;
- Strategy/wallet ID;
- Frozen policy hash;
- Exact chain/token identity;
- Input cutoff and source hashes;
- Original first-seen and public-eligible times;
- ENTER / REJECT / WAIT / UNAVAILABLE;
- Requested notional and capital reservation;
- Permitted route set;
- Quote expiry and slippage policy;
- Capacity/cost limits;
- Exit, timeout and invalidation rules;
- Maximum attempts and retry policy;
- Decision receipt and posting clock.

A chat statement or file timestamp alone does not prove prospective posting. Use the existing owner’s durable receipt mechanism.

Corrections append new records. They do not overwrite the original decision.

---

# 7. Deterministic event simulator

## 7.1 Integration boundary

The simulator should be an approved extension of the existing execution-fidelity and quote/outcome path—not a new standalone engine, scheduler or trading service.

If existing owners cannot support this without creating prohibited new machinery, stop and seek the required canonical exception.

**No real trades, keys, signing, wallet connection, paid RPC expansion or transaction broadcasts are part of this design.**

## 7.2 Event sequence

The primary sequence is:

```text
SOURCE_CAPTURED
→ CANDIDATE_REGISTERED
→ IDENTITY_BOUND / IDENTITY_UNRESOLVED
→ FEATURES_FROZEN
→ DECISION_POSTED
→ CAPITAL_RESERVED
→ QUOTE_REQUESTED
→ QUOTE_RETURNED / QUOTE_FAILED
→ APPROVAL_SIMULATED_IF_REQUIRED
→ ORDER_READY
→ ELIGIBLE_INCLUSION_POINT
→ FILLED / REVERTED / EXPIRED / NOT_INCLUDED
→ POSITION_OBSERVED
→ EXIT_DECISION_POSTED
→ EXIT_QUOTE
→ EXIT_ATTEMPT
→ CLOSED / PARTIALLY_CLOSED / UNSOLD / OUTCOME_UNKNOWN
```

Rejections, abandoned projects and no-route cases remain first-class terminal or pending states.

### Determinism requirements

A replay is keyed by:

- Input manifest hash;
- Policy/configuration hash;
- Adapter/version hashes;
- Exact source snapshots;
- Explicit scenario ID;
- Deterministic ordering and integer rounding.

Identical inputs must produce identical event and accounting hashes.

Order chain events by block/slot and transaction/log position. Order availability by actual receipt time. A strategy must not see a chain event before its input stream makes that event available.

## 7.3 Latency model

Total delay must include:

\[
L =
L_{\text{capture}}
+
L_{\text{queue}}
+
L_{\text{decision}}
+
L_{\text{quote}}
+
L_{\text{approval}}
+
L_{\text{inclusion}}.
\]

Where receipts exist, use observed delays.

Where they do not:

- Use explicitly hypothetical frozen scenarios;
- Do not describe them as measured service levels;
- Do not use an optimistic zero;
- Do not claim a calibrated fill probability.

The existing scheduler cadence remains unchanged. If its natural observations cannot support a 15-minute opportunity, the appropriate result may be `QUEUE_LATENCY_MISS`.

A stop is assessed only when an existing eligible observation arrives. Never execute at an unseen intrabar stop price.

## 7.4 Chain and venue adapters

| Adapter | Required mechanics | Fail-closed condition |
|---|---|---|
| **EVM constant-product AMM** | Exact reserves, fee, token transfer behavior, router semantics, integer rounding | Missing reserves or unsupported token mechanics |
| **Uniswap v3-style concentrated liquidity** | Current price/tick, initialized ticks, active liquidity, fee tier, tick crossing | TVL-only data or incomplete tick state |
| **Uniswap v4** | Correct chain deployment, PoolManager, PoolKey, hook code/state, dynamic fees, settlement behavior | Unsupported hooks or unknown pool identity |
| **Pons/native curve** | Exact contract version, curve formula, fee schedule, buy/sell phase, graduation rules | Treating curve as generic constant-product pool |
| **Solana DEX/launch venue** | Exact program/version, pool accounts, curve/tick state, token extensions, slot/blockhash rules | EVM approximation or unsupported transfer hook |
| **Multi-hop route** | Every hop, intermediate transfer, approval/settlement requirement and capacity | Any unsupported hop |

For Robinhood Chain 4663, adapter availability must be established from exact deployment and source evidence. A chain ID and a quoted price do not establish Uniswap compatibility.

### Constant-product illustration

For reserve \(x\) of the input asset, reserve \(y\) of output, input \(q\), and pool fee \(f\):

\[
\Delta y=\frac{y(1-f)q}{x+(1-f)q}.
\]

This is valid only for the supported mechanics. Transfer taxes, hooks and concentrated liquidity require their own treatment.

A full-size reverse quote must use the appropriate post-entry or independently observed later state—not simply invert the entry price.

## 7.5 Capacity model

Maximum admissible notional is bounded by the smallest of:

- Wallet position limit;
- Available capital and gas reserve;
- Exact route depth at the impact ceiling;
- Transfer/transaction limits;
- Exit-capacity constraint;
- Venue-specific supported capacity.

Do not use reported daily volume as capacity without wash-trading and independence checks.

Evaluate the S2 size tiers—$50/$100/$250/$500/$1,000—plus each wallet’s full hypothetical position, but only where source coverage permits. Missing tiers remain unknown.

### Cross-wallet capacity

Two views are needed:

1. **Standalone policy comparison:** each wallet is a separate counterfactual.
2. **Joint-capacity stress:** overlapping decisions compete for the same depth.

Never sum five standalone fills and imply they could all execute simultaneously without additional impact.

## 7.6 Fill and failure model

For each attempted transaction, determine:

- Was the quote still valid?
- Was the chain state admissible?
- Was allowance sufficient?
- Was native gas sufficient?
- Was the route still open?
- Did `minOut` remain satisfiable?
- Did token restrictions change?
- Was the transaction included before expiry?

Preserve distinct failures:

- Quote unavailable;
- Unsupported route;
- Approval failure;
- Insufficient gas;
- Slippage revert;
- Out of gas;
- Blockhash/deadline expiry;
- Blacklist/pause;
- Sell-closed phase;
- Pool removed;
- Capacity limit;
- Source state unavailable.

Most atomic swaps are fill-or-revert. Do not invent partial fills unless the route or frozen splitting policy actually permits them.

Retries must be bounded and frozen. Failed on-chain attempts consume modeled gas; a failed off-chain quote request does not automatically incur blockchain gas.

## 7.7 Gas, approvals, taxes and MEV

### EVM

Include where applicable:

- Base fee and priority fee;
- Execution gas;
- L1 data/settlement component for relevant rollups;
- Approval/reset transactions;
- Permit semantics when actually supported;
- Wrapping/unwrapping;
- Reverted-attempt gas.

Track virtual allowances by chain, token and spender. Do not charge approval on every sale if allowance legitimately persists; do not assume it exists initially.

### Solana

Include where applicable:

- Transaction and priority fees;
- Compute limits;
- Account creation;
- Rent deposits and only actually modeled recoveries;
- Writable-account contention and expiry;
- Transfer-fee extensions.

### MEV/adverse selection

Use source-calibrated adverse-selection models where available. Otherwise provide explicitly hypothetical stress scenarios.

Do not label a sandwich cost as “measured” without evidence. Do not simulate an advantage that requires privileged ordering unavailable to the paper policy.

### Avoid double counting

If a route quote is already net of pool fees and transfer taxes, do not subtract them again. Store a decomposition and reconciliation check.

## 7.8 The counterfactual market-impact problem

A crucial limitation:

> Inserting a hypothetical trade changes pool state. Replaying unchanged historical outputs afterward can erase that impact and create fictional execution quality.

Use one of two clearly labelled modes:

1. **Snapshot quote replay:** independent sized estimates at observed states. Suitable for bounded price-taker analysis, not a fully interactive market simulation.
2. **Stateful transaction replay:** replay original transaction inputs against modified state, including changed outcomes and reverts, where sufficient state and transaction semantics exist.

If neither is supportable, report bounded execution sensitivity rather than a precise simulated profit.

Even a technically complete fork replay does not model how other humans or bots would react to the hypothetical trade. That residual must remain explicit.

## 7.9 Reorgs and revisions

Store block/slot identity and finality assumptions. A reorg should:

- Invalidate affected simulated state;
- Restore a deterministic checkpoint;
- Replay the corrected branch;
- Preserve the original observation and correction lineage.

Never silently rewrite the original first-seen record or decision.

---

# 8. Accounting, exits, drawdown and opportunity cost

## 8.1 Distinguish three PnL concepts

| Concept | Meaning |
|---|---|
| **Actual realized PnL** | Matched actual entries/exits and costs |
| **Simulated closed-position PnL** | Completed exits generated by an admitted simulator |
| **Mark/liquidation estimate** | Open inventory valued using a source-qualified quote or stated scenario |

The current packet establishes none of the first two for the proposed wallets.

For a fully closed simulated episode:

\[
\Pi_{\text{sim}}
=
\sum \text{net exit proceeds}
-
\sum \text{entry cash spent}
-
\sum \text{separately accounted costs}.
\]

The accounting definition must prevent fees already included in net proceeds from being subtracted twice.

Quote-asset and native-gas conversions require timestamped conversion sources. USD, USDT, USDG and native assets are not automatically equivalent.

## 8.2 Exit reality

At each exit attempt, re-evaluate:

- Full remaining token quantity;
- Route identity;
- Pool/curve phase;
- Taxes/admin restrictions;
- Gas availability;
- Slippage and impact;
- Quote freshness;
- Inclusion delay;
- Retry policy.

A successful entry never guarantees an exit.

A $50 successful sell does not prove that $1,000—or the complete position—can be sold under the same conditions.

## 8.3 Delisting, rug and missing observation

| Event | Treatment |
|---|---|
| Price feed disappears but DEX route exists | Seek original route evidence; do not set value to zero automatically |
| Confirmed route closure/unsellability | Record an execution failure and economic impairment |
| Proven liquidity removal/rug event | Preserve loss event; do not censor it away |
| No outcome data because collector failed | `OUTCOME_UNKNOWN`; report sensitivity bounds |
| Terminal zero-recovery assumption | Explicit conservative valuation scenario, not an observed zero-price sale |
| Remaining unsold inventory | Not a completed realized exit |

This prevents both optimistic survivorship and unjustified zero-valuations.

## 8.4 Wallet equity and maximum drawdown

Primary economic equity should use **net full-position liquidation estimates**, not last-trade price:

\[
E_t
=
C_t
+
\sum_i V^{\text{net liquidation}}_{i,t}
-
\text{unsettled liabilities}_t.
\]

Then:

\[
DD_t=1-\frac{E_t}{\max_{u\le t}E_u}.
\]

If material liquidation values are unknown, exact drawdown is unknown. Report:

- Verified-observation drawdown;
- Conservative valuation stress;
- Missing-valuation duration and exposure.

Do not fabricate a smooth equity curve through unsupported intervals.

MFE and MAE also need observation cadence and quote-size semantics. Sampled MFE is not a true continuous-time maximum.

---

# 9. Prospective science, independent outcomes and survival analysis

## 9.1 Three evidence lanes

### A. Historical reconstruction

Permitted for:

- Reconstructing source coverage;
- Testing identity;
- Discovering execution-model defects;
- Generating hypotheses.

No prospective alpha credit.

### B. Source-at-discovery replay

Use only original captured information that was available at the replayed decision time.

If original capture is missing, label the exercise **retrospective as-of-chain reconstruction**, not source-at-discovery replay. A later archive query cannot repair machine first-known.

### C. Untouched OOS experiment

Before the period begins, freeze:

- Eligibility and denominator;
- Policy and sizing;
- Feature definitions;
- Entry/exit timing;
- Costs and latency scenarios;
- Benchmarks;
- Outcome horizons;
- Missing-data handling;
- Primary endpoint;
- Dependence unit;
- Minimum meaningful effect;
- Multiplicity and stopping rules.

No threshold tuning after seeing the test outcomes.

## 9.2 Baselines and ablations

For wallet intelligence:

- Champion: public age, cap semantics, liquidity, volume/activity, breadth and momentum;
- Challenger: champion plus admissible as-of wallet/entity features;
- Same decision clock, notional, route model and exit policy.

For project research:

- Price/liquidity baseline;
- Project-only challenger;
- Project plus token-economic-linkage challenger.

For launch-origin research:

- Baseline public launch characteristics;
- Add privileged-access measurements;
- Add strictly prior deployer history.

For catalyst research:

- Matched non-event opportunities;
- Publicly announced catalysts that failed, were delayed or never happened;
- No selection based on later media attention.

Ablations should remove one information family at a time. Otherwise “wallet edge” may actually be liquidity selection or slower entry.

## 9.3 Independent matched outcomes

The outcome owner should reproduce:

- Eligible launch universe;
- Token identities;
- Outcome windows;
- Sized exit states;
- Cost inputs.

Where practical, outcome assembly should be blinded to strategy labels until matching and validity checks are complete.

Controls are selected using only predecision variables:

- Chain/venue;
- Time window;
- Age;
- Cap semantics/bucket;
- Liquidity/depth;
- Source availability.

Do not match on later survival, realized volatility or successful sellability. That would condition away the failures being studied.

## 9.4 Statistical dependence

Cluster by the largest relevant shared cause:

- Ecosystem trial;
- Deployer/entity family;
- Launch batch;
- Catalyst;
- Market episode;
- Overlapping holding period.

Five wallets buying the same token are not five independent discoveries.

Use paired, dependence-aware confidence intervals for incremental effects. With too few independent clusters, report unstable or not-estimable intervals.

Do not multiply sample size by:

- Number of checkpoints;
- Number of quote sizes;
- Number of strategy arms;
- Number of screenshots;
- Number of correlated wallets.

## 9.5 Survival analysis

Useful endpoints include time to:

- First loss of required-size sellability;
- Severe drawdown;
- Confirmed rug/irreversible impairment;
- Graduation;
- First executable 2×;
- Strategy exit.

These are not interchangeable.

Required treatment:

- **Competing risks:** rug, voluntary exit and other terminal events are distinct.
- **Interval censoring:** when failure occurs between observations.
- **Right censoring:** only for genuinely unfinished observation, with assumptions disclosed.
- **Informative missingness:** a disappeared token/feed may be related to failure; do not treat it as benign censoring.
- **Delayed entry:** a strategy starting 15 minutes after launch observes survivors to that time. It cannot claim launch-time survival performance without adjustment.

Never-launched projects belong in a project transition process—candidate → launched / not launched / unresolved—not in a fake token-price series.

## 9.6 Core output measures

Report jointly:

- Timely discovery coverage;
- Missed executable-winner recall;
- Actionable precision;
- False-binding rate;
- Quote and fill success;
- Sellability survival;
- Net simulated return, only after valid simulation exists;
- Full-wallet return;
- Maximum drawdown and severe-loss frequency;
- Capital-days and idle cash;
- Source coverage;
- Cost drag;
- Dependence-adjusted uncertainty;
- Baseline delta.

A strategy with good conditional returns but almost no executable coverage is not automatically useful.

---

# 10. Objective kill, hold and promotion gates

## 10.1 Immediate integrity stops

Stop or invalidate affected evidence for:

- Future information in a decision feature;
- Backdated discovery or posting;
- Wrong chain/CA;
- Denominator substitution;
- Winner-only sampling;
- Silent deletion of rejects or failures;
- Unsupported route presented as executable;
- Missing material costs treated as zero;
- Private information leaking into public output;
- E2 wallet sensor built despite HOLD;
- Round 3 scoring while prohibited.

These are evidence-integrity stops, not optional statistical findings.

## 10.2 Source-contract gates already present

Preserve, rather than replace:

- E1’s frozen maximum window and no outcome-driven extension;
- E3’s ≥30 eligible-row timing review and frozen edge budget;
- E4’s independent denominator and fresh OOS criteria;
- S7’s minimum 20 matured ecosystem trials before its method-review kill assessment. [S4, S7]

Their numerical gates answer specific questions. They are not blanket profitability certification.

## 10.3 Proposed strategy-level review gates

Before OOS start, freeze a minimum meaningful net advantage \(\delta\) against the matched baseline.

At the single planned efficacy review:

- If the upper confidence bound is below \(\delta\), reject the claimed economically meaningful advantage.
- If uncertainty spans materially harmful and beneficial outcomes, classify **INCONCLUSIVE**, not PASS.
- If advantage disappears under measured latency or supported costs, reject realizable-edge claims.
- If results depend on inaccessible/unsellable outliers, reject deployability.
- If a few related entities dominate results, report concentration and require separate validation.
- If public dissemination destroys the lead time, scope the strategy accordingly rather than retain historical credit.

Research safety monitoring may continue during the trial, but repeated efficacy peeking must not become optional stopping.

## 10.4 Promotion requires separate authority

Even a valid positive OOS result does not automatically:

- Change production weights;
- Enable alerts;
- Publish private data;
- Create live wallets;
- Authorize trades;
- Promote an engine;
- Activate a new scheduler.

`VALID_ROW != PROVEN_EDGE` and `COVERAGE_READY != PROMOTION` remain binding. [S4]

---

# 11. Research-to-build roadmap through existing owners

The following are **work-package specifications**, not created tasks, dispatched agents or `CODEX_READY` declarations.

The exact operational S4 contract is absent. Its role must be read from current authority before assigning implementation responsibilities. Do not assume it is the S2 handoff’s “S4” release stage.

| Stage | Existing owner route | Deliverable | Acceptance / stop condition |
|---|---|---|---|
| **0. Authority and baseline census** | #1087; current cockpit; existing S4 route only after verification | Exact current contracts, active tests, owner mapping, original v4 row inventory | Stop on missing authority; explicitly list absent original decisions/fills/exits |
| **1. Denominator and clocks** | #1340; source lineage #120 | Append-only candidate lifecycle, original first-seen receipts, manual-miss taxonomy | Counts reconcile across project/launch/opportunity views; no backdating |
| **2. Identity and launch-origin repair** | Existing Project→CA, #194, #1134 E1/E3/E4 | Exact chain/CA/pool binding; as-of launch/deployer features | Adversarial false-CA and future-feature tests reject correctly |
| **3. Exit mechanics** | #98, then #77 | Private sized buy/sell estimates, phase handling, full-position coverage | SELL-CLOSED, unsupported hooks and missing gas cannot PASS |
| **4. Frozen paper protocols** | #1087/#1340; #1134 only within its admitted scope | Reconciliation of five proposed policies with existing arms; approved prereg amendments if needed | No duplicate ledger/arm; no new sensor; scorer authority explicit |
| **5. Deterministic replay extension** | Existing execution-fidelity/outcome implementation | Supported adapters, accounting, failure model, reproducible receipts | Same inputs → same outputs; unknown state → no fabricated fill |
| **6. OOS collection and independent maturation** | Existing collection/outcome schedules | Frozen inputs, independent outcomes, due-only assessment | Pending remains pending; no result-driven cohort extension |
| **7. Existing-site projection** | #228 with #196 gate and original source owners | Read-only, approved, privacy-safe evidence view | Native deployed bytes and source timestamps verified; no private leakage |

### Code-intake discipline

A research finding becomes a code candidate only after a reproducible bounded defect and current source path are identified.

Because the actual implementation files and intake schema were not supplied, this report does **not** claim a schema-complete Codex candidate or a confirmed code defect. Future intake must follow the existing skill and maturation route.

## 11.1 Required test matrix

Before implementation, freeze positive and adversarial cases:

| Test | Required behavior |
|---|---|
| Feature arrives one block after decision | Excluded from that decision |
| Later wallet reputation supplied | Cannot alter earlier feature state |
| Same symbol, wrong chain/CA | Identity gate rejects |
| Shared router or CEX funder | Does not automatically merge entities |
| Pons sell-closed phase | No sellable label or exit fill |
| v4 hook unsupported | `NOT_SUPPORTED`, not generic AMM approximation |
| Tiny sell succeeds, full sell fails | Full-position coverage fails |
| Entry approval/gas missing | No free fill |
| Slippage revert | No token fill; applicable gas retained |
| Collector outage | Unknown coverage, not zero activity |
| Rug followed by feed disappearance | Failure retained, not benign censoring |
| Re-delivered identical source tick | No duplicate candidate/decision/outcome |
| Two strategies share scarce depth | Joint-capacity stress reflects competition |
| Stop crossed between observations | No fictitious exact-stop execution |
| Private design/value without token-like secret | Privacy gate still rejects public export |

Critical tests must fail when their guard is removed. Test collection alone is not execution evidence.

## 11.2 Growth and idempotency

Use existing immutable history plus a compact active set.

For measured daily new opportunities \(N\), average appended records \(r\), and average bytes \(b\):

\[
\text{incremental history at }d\text{ days}\approx dNrb
\]

for \(d=7,30,90\), adjusted for outcomes and corrections.

Actual \(N,r,b\) are not supplied, so no numerical storage forecast is claimed. The implementation PR must measure them and report:

- Records per run;
- Distinct entities;
- Duplicate ratio;
- Pending backlog;
- 7/30/90-day bytes;
- Retention and consumer path.

Scenario runs should reference shared source snapshots, not duplicate raw evidence into every wallet record.

A clock tick alone must not create new semantic work. Preserve meaningful state transitions without repeatedly redispatching unchanged candidates. [S1]

---

# 12. Existing-site architecture

The site should remain a **read model**, not a trading terminal or independent analytics engine.

## 12.1 Recommended presentation

### Discovery

Show:

- First machine discovery;
- Project/publication time, separately;
- Launch/trading phase;
- Identity status;
- Timely/late/manual-found classification;
- Source coverage.

### Exit Reality

Show:

- Exact tested size;
- Buy and sell separately;
- Route-support status;
- Producer as-of time;
- Quote age;
- PASS/BLOCKED/UNKNOWN for the specific test;
- “Estimate—not execution.”

### Strategy Arena

Keep existing arms and approved mappings. Separate:

- Decision posted;
- Quote obtained;
- Simulated fill;
- Original transaction evidence;
- Exit pending;
- Exit failed;
- Outcome unknown.

Do not display a performance leaderboard while valid matched outcome coverage is absent.

### Proof

Display the complete relevant denominator:

- Selected;
- Rejected;
- Missed;
- No-token;
- Never launched;
- No route;
- Unsellable;
- Mature;
- Pending;
- Missing.

### Trust Desk

Private first:

- Original source receipts;
- Completeness;
- First-known verification;
- Model limitations;
- Cost coverage;
- Quote-size coverage.

Public projection requires the existing #196 allowlist/privacy gate. This report does not authorize exporting token amounts, wallet graphs, provider values or route details.

## 12.2 Freshness

Display separately:

- Source event time;
- Producer capture time;
- Snapshot publication time;
- Browser fetch time.

Client polling is not a new upstream observation. A five-minute configured job is not a five-minute SLA.

Stale or unsupported data should disable actionable-looking controls. No BUY, connect-wallet or signing functions belong in this paper-research surface.

## 12.3 Release truth

“Built,” “released,” “near-live” and “autonomous” require different evidence.

At minimum:

- Exact-head tests;
- Native merge/main readback;
- Approved publication schema;
- Genuine producer output;
- Actual deployed Pages bytes;
- Natural subsequent producer-to-consumer updates.

A green preview or synthetic screenshot proves none of the last three.

---

# 13. Falsifying this architecture’s own assumptions

| Assumption in this proposal | Evidence that would falsify or materially weaken it | Required response |
|---|---|---|
| Better first-seen provenance will reveal usable lead | Existing queue and capture delay consumes all public lead | Stop claiming early-entry edge; evaluate slower horizons only |
| Project quality helps token selection | Matched no-token/good-product controls perform similarly, or token linkage is absent | Separate project intelligence from investment scoring |
| Wallet convergence adds information | Effect disappears after infrastructure filtering or entity-dependence adjustment | Reject wallet-edge claim; do not build E2 sensor |
| Deployer history adds risk value | Apparent effect relies on future launches or one prolific actor | Invalidate leaked rows; narrow or kill hypothesis |
| Privileged-access features help outsiders | They predict graduation but not delayed net returns | Retain risk description only; no profitability claim |
| Exact quotes make simulation realistic | Quotes systematically fail to predict independent historical fills/exits | Recalibrate or downgrade to quote-only evidence |
| Small trades are executable | Gas/taxes consume the entire expected advantage | Skip those chain/size combinations |
| Conservative larger-cap policy is better risk-adjusted | It merely holds cash while a simple matched benchmark dominates | Report opportunity cost; do not use “conservative” as performance proof |
| Five wallets diversify results | Positions share tokens, deployers and market episodes | Report correlated exposure and effective sample size |
| Historical replay approximates market interaction | Own trades materially change later pool behavior | Use stateful replay or explicit bounds; withdraw precise PnL claims |
| Public publication preserves the edge | Disclosure materially accelerates crowding and worsens fills | Treat public-product usefulness and private research edge separately |
| Existing schedules can support all horizons | Event/launch windows repeatedly expire before observation | Mark infeasible; no covert scheduler expansion |

---

# Final recommendation

Prioritize work in this order:

1. **Recover or conclusively inventory the missing original v4 decision→fill→exit→cost evidence.**
2. **Repair first-seen, denominator and CA/phase binding.**
3. **Establish full-position sellability and supported chain-specific execution mechanics.**
4. **Freeze any approved paper-policy amendments before untouched OOS collection.**
5. **Publish only the evidence classes the existing site can truthfully support.**

The five wallets are useful as **separate experimental accounting policies**, not as five demonstrated edges. Their strongest common rule should be:

> **No timely original source, no verified identity, no supported sized route, or no material cost coverage → no executable-alpha credit.**

**Final status:** source-bounded architectural report only. No tools used, no code executed, no tasks persisted, no model dispatched, no wallets created, no trades made, and **no paper profits or strategy superiority asserted**.
===== END SOURCE =====
