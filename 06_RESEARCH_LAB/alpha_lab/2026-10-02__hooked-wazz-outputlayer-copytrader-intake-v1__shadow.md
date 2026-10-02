# Alpha Lab Intake — HOOKED / Wazz Wallet Intel + Robinhood Copy-Trader Contract v1

Date: 2026-10-02
Status: SHADOW RESEARCH / NEW PROSPECTIVE LEADS
Owner: existing Alpha Lab / Meme Alpha Supervisor / #1087
Trade authority: NONE
Automatic execution: NO
New scanner owner: NO

## Why this intake exists

Owner supplied fresh screenshots for Alpha Lab review containing two materially useful live cases:

1. Solana token HOOKED, surfaced by Wazz's wallet-intelligence tooling.
2. Robinhood Chain address/contract 0x53a42d2d0fdd60bf8f833fb94841349095a74024, surfaced by Outputlayer as an apparent predictive/copy-trading strategy running at scale.

These are not new architecture concepts. They are fresh cases that should be routed into the existing wallet/entity-memory, signal-capacity, operator-risk and prospective outcome owners.

## Case A — HOOKED / Wazz positive winner case

Exact Solana mint:
C1mBfBoDkwWfd6uTFZp62ARHLjeVp3bDpCDMfMZtPngE

Owner-supplied Wazz screenshot reports:
- first alert market cap: ~$406.8K;
- latest saved cap in the screenshot: ~$5.084M;
- displayed price gain since first alert: +1,671.5%;
- 77 buyers at the alert object;
- 10 saved/identified holder profiles visible;
- visible holder labels include Meteora, Aurelius, smol_intern, 0xdetweiler, bulgugi, Iri0o, BTCwolf, EpicLocrianDesk and UnevenAlikeCrab;
- identity checks were still incomplete in the screenshot.

Independent public-source checks:
- Hooked's official site identifies the same mint as $HOOKED.
- Hooked docs describe the project as a Solana Token-2022 transfer-hook launchpad using Meteora bonding-curve mechanics.
- Public market sources on 2026-10-01 independently observed the same mint at multi-million-dollar valuation after its 2026-09-28 launch, corroborating that a large post-alert expansion actually occurred.
- Public holder/risk sources disagree materially on holder counts and concentration depending on timestamp/methodology, so these fields must remain point-in-time and source-scoped.

Alpha Lab interpretation:
This is a valuable POSITIVE CONTROL for Wazz-style wallet/entity intelligence.

The research question is not:
"Did HOOKED pump?"

It is:
"At the frozen first-alert timestamp, did the holder/entity composition add incremental predictive value beyond simple price/volume/liquidity/launch-age features?"

Required replay:
- freeze Wazz first-alert timestamp and cap;
- reconstruct what holder identities were knowable then, not later;
- separate protocol/infrastructure accounts from economic actors;
- measure independent buyer breadth;
- measure liquidity/sellability at first alert;
- compute MFE/MAE from first public executable quote;
- record time to 2x/5x/10x and first major drawdown;
- compare against matched Meteora/DBC launches with similar age, cap, volume and liquidity that did not become major winners;
- test whether named-wallet overlap or wallet quality added incremental information beyond generic momentum.

Do not award alpha credit from retrospective labels or current wallet reputation.

## Case B — Robinhood Chain predictive/copy-trading contract

Exact address:
0x53a42d2d0fdd60bf8f833fb94841349095a74024

Owner-supplied Outputlayer screenshot reports an external retrospective analysis:
- 53 "real episodes";
- 45 green;
- ~$63.3K bought;
- ~$21.3K realized profit;
- median episode approximately +$154 / +15%;
- mean approximately +$402 / +25%;
- p10 about -$30;
- p90 about +$889;
- worst about -$336;
- best about +$3,208;
- top 10 episodes reportedly contributed ~73% of profit;
- max drawdown reported as ~$336;
- 4-6 open positions / roughly $4K-$8K at risk;
- screenshot states the strategy targets 33 FOMO whale wallets with a fixed ticket per wallet.

Treat all performance statistics above as EXTERNAL CLAIMS until independently reconstructed.

Independent Blockscout verification performed in this bounded pass before the Blockscout session became unavailable:
- chain: Robinhood Chain, chain ID 4663;
- 0x53a4...4024 is a CONTRACT, not a normal EOA;
- contract is unverified at observation time;
- first transaction timestamp: 2026-09-29T13:20:44Z;
- creator: 0x2841A9258cdf9F222D337a83FeB33cBd1E441891;
- native balance observed: ~6.4521 ETH;
- USDG balance observed: ~18,385.444613 USDG;
- additional small token holdings observed;
- live token transfers on 2026-10-02 included TANK and ZKSTR;
- recent execution touched 0x8366a39CC670B4001A1121B8F6A443A643e40951, independently identifiable as Robinhood Chain's Uniswap v4 PoolManager, so that address is infrastructure and must not be treated as operator identity.

This materially strengthens the case as a live strategy-contract research object rather than a social-media anecdote.

Alpha Lab interpretation:
This case belongs in WALLET / STRATEGY INTELLIGENCE, not token scoring.

Priority research questions:
1. Can Outputlayer's 53 episodes be reconstructed mechanically from chain data?
2. What exactly constitutes an "episode" and a "green" outcome?
3. Are profits measured mark-to-market or realized after all exits?
4. What is the denominator, including skipped/missed/reverted attempts?
5. Is the apparent edge concentrated in a small number of target wallets?
6. Does the contract buy after target intent becomes public or exploit pre-fill information?
7. What latency/block-index advantage is required?
8. Can the behavior be detected prospectively without copying unsafe or potentially manipulative execution?
9. What fraction of returns survives gas, failed transactions, slippage and realistic bounded notional?
10. Does the strategy remain positive out of sample after the public disclosure itself?

Research output should separate:
- TARGET_WALLET_SIGNAL_QUALITY;
- EXECUTION_EDGE;
- ROUTE/MEV_TOXICITY;
- REALIZED_PNL;
- CAPACITY/DECAY;
- PUBLIC_ELIGIBILITY.

## Framework fit

This intake strengthens existing 2026-09-27 Wazz / Outputlayer research rather than creating a new scanner.

Relevant existing architecture:
- persistent point-in-time wallet/entity memory;
- ADDRESS -> ENTITY_CLUSTER semantics;
- explicit infrastructure false-positive exclusions;
- dual-axis risk vs realizable alpha;
- prospective frozen outcome rows;
- no retroactive label improvement.

## Priority

P1 — Robinhood contract 0x53a4...4024:
High research value because the address is live, exact, independently verified as a contract and potentially provides dozens of reconstructable episodes.

P1 — HOOKED:
High learning value as a positive winner/control for Wazz-style wallet intelligence, especially because the first-alert level is available from the supplied screenshot.

Neither case receives automatic BUY/SELL authority.

## Next bounded actions

1. Reconstruct HOOKED's first-alert birth/holder tape and matched controls.
2. Reconstruct the 0x53a4...4024 episode ledger from 2026-09-29 onward.
3. Identify target-wallet cohort only from public evidence and point-in-time data.
4. Attribute routers/pools/relays as INFRASTRUCTURE before any wallet/entity inference.
5. Freeze outcome rows and test forward rather than accepting the external performance summary.
6. Reuse existing Alpha Lab owners, no duplicate scanner or scheduler.
