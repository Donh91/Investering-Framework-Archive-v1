# External Specialist Capability Snapshot - 2026-10-06

Status: SOURCE_DISCOVERY_SNAPSHOT / NOT_EDGE_EVIDENCE
Canonical queue: README.md
Master issue: #1512

Purpose:
Preserve the current publicly documented specialist capabilities used to rank the master queue. This prevents later agents from repeating discovery work and clearly separates documented capability from live source admission.

## GMGN

Current public material reviewed:
- https://gmgn.ai/blog/how-to-track-smart-money-with-ai-agents/
- https://gmgn.ai/blog/how-to-find-meme-coins-earlier/
- https://gmgn.ai/blog/gmgn-skills-for-ai-agents/

Documented/reported capability:
- separates Smart Money, KOL and Sniper concepts;
- exposes wallet realized/unrealized PnL, ROI, win rate, token breadth, holdings and recent trades through current Skills workflows;
- surfaces smart-money entry/trim/exit behavior;
- exposes token safety/holder context and labels including sniper/insider/bundled wallets;
- combines new-pair discovery, public callouts and wallet tracking.

Research verdict:
HIGH_VALUE_CHALLENGER for S2 Wallet Skill Truth and S7 Attention Conversion.
Do not import Smart Money/insider/bundler labels as truth.


Public source-code audit:
- upstream repository: GMGNAI/gmgn-skills;
- license: MIT;
- current package version observed: gmgn-cli 1.6.6;
- exact public wallet-analysis code separates AUTHENTICITY, CURRENCY, REACHABILITY and SURVIVABILITY;
- portfolio API documentation exposes stats, profits and paginated activity under API-key-only auth;
- the upstream README provides a public testing key for read-only token/market/portfolio commands.

High-value method transfer:
- profit concentration;
- recent-vs-historical skill decay;
- median first-buy->first-sell copy window;
- reachability/latency;
- left-tail survivability;
- self-authored dev-wallet separation;
- unmeasured != pass/fail.

Exact GMGN numeric cutoffs remain external heuristics and are not Framework canon.

Live source-audit state:
S2 Alpha PR #102 is testing whether the public read-only key provides enough indexed portfolio history to act as an OPTIONAL_CHALLENGER for INDEXED_WALLET_PORTFOLIO_V1. The first run proved stats access but triggered the shared-key/IP rate limit before profits/activity could be judged. That is rate-limit evidence, not an endpoint-permission verdict.
## GoPlus

Current public docs reviewed:
- https://docs.gopluslabs.io/docs/getting-started
- https://docs.gopluslabs.io/reference/api-overview
- https://docs.gopluslabs.io/reference/gettransactionsecurityinfousingpost
- https://docs.gopluslabs.io/changelog/token-security-api
- https://docs.gopluslabs.io/reference/response-details-9
- https://docs.gopluslabs.io/reference/supported-dex
- https://docs.gopluslabs.io/reference/supported-main-token

Documented capability:
- Token Security API;
- EVM transaction simulation;
- Solana transaction simulation;
- malicious-address/security surfaces;
- Robinhood Chain 4663 added to Token Security on 2026-07-28;
- Robinhood supported mainstream tokens include WETH, USDE and USDG;
- Robinhood DEX list includes UniswapV2, UniswapV3 and UniswapV4.

Research verdict:
HIGH_VALUE source for S1 Sellability Truth.

Important uncertainty:
documentation reviewed confirms Robinhood Token Security coverage but does not by itself prove every generic EVM transaction-simulation route needed by S1 works on chain 4663.

Live API probe state:
NOT_COMPLETED_FROM_CURRENT_CHAT_TOOLING.
A direct live fetch attempt through the available Firecrawl connector failed because that connector account had insufficient credits. This is a tooling limitation, not source evidence.
Do not mark the source unavailable. Run a bounded source probe through GitHub/approved runtime later.

## Honeypot.is

Current public docs reviewed:
- https://docs.honeypot.is/

Documented capability:
- honeypot checks;
- token tax/gas context;
- pair resource;
- top-holder resource;
- API currently documents no required auth for ordinary use at capture time.

Research verdict:
HIGH_VALUE challenger for S1 where chain coverage is supported.

Documented chain scope:
Honeypot.is currently documents Ethereum, Binance Smart Chain and Base only. Robinhood Chain is not documented as supported and must not be used as Robinhood evidence.

## Arkham

Current public material reviewed:
- https://info.arkm.com/announcements/the-new-arkham-api
- https://info.arkm.com/announcements/arkham-api-upgrade-real-time-intel

Documented capability:
- Intel API for entity labels and fund-flow data;
- address intelligence updates;
- September 2026 upgrade made address-intelligence updates real-time/minutes-level;
- update feed includes deposit-address detection, verified contract labels, token/NFT labels, deployer labels and analyst-curated labels.

Research verdict:
HIGH_VALUE challenger for S3 cluster/entity and S6 distribution egress.
Never treat entity/deposit labels as canonical without raw path corroboration.

## CoinGlass

Current public docs reviewed:
- https://docs.coinglass.com/reference/getting-started-with-your-api
- https://docs.coinglass.com/reference/endpoint-overview
- liquidation map/heatmap endpoints

Documented capability:
- OI;
- funding;
- liquidation events;
- liquidation maps/heatmaps;
- long/short and derivatives flow families;
- spot/order-book expansion in API V4;
- real-time advanced liquidation surfaces.

Important dependency:
advanced liquidation heatmap/map endpoints reviewed are restricted to higher API plans.

Research verdict:
HIGH_VALUE for S5 Derivatives Crowding to Pullback, but dependency/cost must be compared against simpler exchange-native/internal primitives.

## Laevitas

Current public API documentation reviewed:
- https://api.laevitas.ch/swagger/
- https://apiv2.laevitas.ch/swagger

Documented capability includes:
- options OI;
- option volume/flow;
- IV;
- skew;
- GEX;
- term structure;
- forward curve;
- historical options analytics.

Research verdict:
HIGH_VALUE options challenger for S5.
Use to test whether options positioning adds incremental pullback/distribution information beyond spot/perp/OI/funding.

## Tokenomist

Current public surface reviewed:
- https://tokenomist.ai/

Observed capability:
- released percentage;
- upcoming unlock value;
- next-7-day emission;
- release logs;
- API/CLI surface advertised on current site.

Research verdict:
HIGH_VALUE source candidate for existing S8 Unlock Supply Overhang.
No new unlock engine.

## DeFiLlama

Current public protocol/investor surfaces reviewed:
- https://defillama.com/
- https://investors.defillama.com/

Observed capability:
protocol-level TVL, fees, gross protocol revenue and holder/value-capture style fields for supported protocols.

Research verdict:
CONDITIONAL_HIGH_VALUE for S10 Protocol Value Capture on utility/AI/infrastructure tokens.
Low priority for pure memes.

## Bubblemaps / cluster family

Existing internal archive already records Bubblemaps as a high-value cluster/holder-link specialist and preserves historical public cluster claims for PEPE, SHIB and BRETT as research inputs.

Research verdict:
HIGH_VALUE for S3 Entity-Adjusted Cluster/Bundle, but the research objective is reconstruction from raw funding/timing/transfers, not copying a visualization or accepting a cluster as ownership proof.

## Capability vs edge rule

Every item above is only a statement about a provider's documented/observed capability.

It is NOT evidence that:
- the provider predicts returns;
- its labels are calibrated;
- it has lower false-positive rate than Alpha Lab;
- it should become a runtime dependency.

Admission path remains:
`SOURCE_AUDIT -> SEMANTIC_MATCH -> INTERNAL/PROVIDER CHALLENGER -> MATCHED CONTROLS -> FORWARD EVIDENCE -> RETAIN/REJECT`.
