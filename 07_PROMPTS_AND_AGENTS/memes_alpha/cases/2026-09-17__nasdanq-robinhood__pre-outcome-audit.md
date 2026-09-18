# Alpha Lab — NASDANQ Robinhood pre-outcome audit

Status: FROZEN PRE-OUTCOME RESEARCH SNAPSHOT
Observed: 2026-09-17 ~23:20 Europe/Copenhagen
Source/caller: user-supplied Telegram screenshot from Crypto Gods Lounge; independently cross-checked against exact-CA web/on-chain sources
Token: NASDANQ
Chain: Robinhood Chain, chainId 4663
Exact CA: `0x51fb76be80ab6daaa345d818f4e06441816b4fea`
Canonical observed legacy pool: NASDANQ/WETH Uniswap v3 `0xdb1b57704d5122058ff925c1e765c17b21d065ec`
Launchpad lineage: Pons V1 / `PonsLauncherToken`

## Same-run action snapshot

The user's ~23:20 Telegram bot screenshot is the freshest exact-CA observation available in this run and therefore outranks lagged web/index snapshots for present-tense market state. It showed approximately:
- price: `$0.00116000`
- market cap: `$1.16M`
- liquidity: `$132.7K` (~11% of MC)
- 24h change: `+46.32%`
- 24h volume: `$100.6K`
- buys / sells by count: `331 / 580`
- total supply: `1.000B`
- burned: `0.0%`
- holders: `4,515`
- displayed top-10 share: `24.1%`
- pair/token age: ~44d
- launch MC shown: `$1.41M`
- historical ATH MC shown: `$4.67M`
- bot: no honeypot flag; max-transaction / max-wallet warning shown

Historical web readbacks during this audit contained materially different price/MC values because of crawl/cache timing. They are retained only as chronology/context, not substituted for the same-run screenshot.

## Data integrity / contract semantics

Exact CA is independently mapped to NASDANQ on Robinhood Chain by multiple sources, including Gate Alpha listing, RH-scan/Blockscout-family explorers, Pump and market scanners. The observed strongest legacy route is the Uniswap v3 NASDANQ/WETH pool above.

The token is a verified `PonsLauncherToken` implementation. Public Pons V1 source documentation establishes that max-wallet and cumulative max-buy restrictions are temporary launch-window anti-snipe controls applying to pool-to-user buys. After `restrictionEndBlock`, the token behaves as a plain ERC-20; sells are not subject to those launch-window limits and there is no configurable transfer tax in the standard implementation. Therefore the Telegram bot's generic `Max Transaction | Max Wallet` warning must NOT be interpreted as a currently active 44-day-old restriction without address-specific live state proving otherwise.

Go+ and Quick Intel were shown by DexScreener as `No issues`, with the usual warning that automated audits are not definitive.

## Historical provenance / lore

Independent 2017 evidence from The Verge confirms that a 12-person Reddit team led by Brandon Wink and Ron Vaisman was building NASDANQ as a working fictional meme-stock market arising from r/MemeEconomy. The Verge described NASDANQ by name and quoted Wink directly. Know Your Meme also records NASDANQ's 2016/2017 history and closed beta.

This means the core `2016 Meme Economy -> NASDANQ meme exchange` provenance is real and predates the 2026 token by about a decade. It is unusually strong meme-lore compared with a narrative invented at token launch.

Current social/project surfaces identify Brandon Wink / `@DanqDev` as the returning former NASDANQ creator and bind him to this exact CA. That current identity link is strongly supported by the project's own surfaces and the long-lived social account, but it is still treated separately from the independently verified 2017 historical provenance.

The stronger historical claim that NASDAQ formally caused the original NASDANQ shutdown is currently supported primarily by Wink/project/community retrospective statements. This audit did not locate the original cease-and-desist/legal document, so `NASDAQ SHUTDOWN / C&D` remains `CLAIMED_NOT_PRIMARY_DOCUMENT_VERIFIED`, not canonical fact.

## Current catalyst

The current project/developer is publicly pursuing Pons V2 migration. Recent developer/project posts state an intention to pair NASDANQ with a QQQ stock-token asset and add stock airdrops around the migration. However, the developer also states that the migration application is still awaiting Pons response and that exact migration mechanics were not yet known to him.

Therefore:
- `PONS_V2_MIGRATION_INTENT = VERIFIED_FIRST_PARTY`
- `QQQ_PAIR_AND_STOCK_AIRDROP_PLAN = VERIFIED_PROJECT_CLAIM`
- `MIGRATION_APPROVED / LIVE = NOT VERIFIED`
- `EXACT_MIGRATION_MECHANICS = UNKNOWN`

A separate GeckoTerminal NASDANQ/QQQ pool exists with a different token contract and negligible liquidity. It must NOT be confused with this exact CA or used as proof that this token's migration is live.

## Market-structure observations

At the user screenshot baseline, liquidity/MC was ~11.4%, a comparatively usable ratio for a ~$1M meme microcap, though still thin in absolute terms. The token was about 75% below its displayed `$4.67M` ATH while rallying ~46% in 24h. Current MC was also below the screenshot's displayed `$1.41M` launch MC.

Historical source snapshots suggest holder count rose from roughly 3.7K around six days earlier to 4.5K now, while one third-party top-10 snapshot had been ~27.4% versus the screenshot's 24.1%. Because holder classification and LP/system-address treatment may differ by source, treat this only as a directional hypothesis of widening distribution until normalized exact-holder data is reconstructed.

The current Telegram call is not first discovery. SWARM reports public calls beginning ~39 days ago, with 13 tracked callers and a very large best-call multiple from the earliest floor. This is a mature/recycled narrative, not undiscovered alpha.

## Alpha thesis

Positive:
- real, independently documented 2016/2017 internet-culture provenance;
- original NASDANQ creator Brandon Wink is credibly associated with the current project/exact CA through project/social evidence;
- narrative is unusually chain-native: meme stock history + Robinhood stock-token chain + proposed QQQ pairing;
- active builder/project surfaces rather than an abandoned pure ticker;
- ~4.5K holders and ~11% liquidity/MC at the live screenshot baseline are non-trivial for the valuation;
- ~75% below prior ATH creates meaningful convexity if a verified V2/QQQ catalyst re-rates the token;
- standard Pons V1 contract pattern reduces some classic mutable-owner/tax/honeypot concerns.

Negative / falsifiers:
- 44-day-old asset with many prior callers: discovery edge is largely gone;
- same-run rally already ~46%, so Telegram call may be late relative to the current impulse;
- sell count materially exceeds buy count at screenshot time, although count alone does not establish net dollar flow;
- migration is not yet approved/complete and exact holder mechanics remain unknown;
- QQQ pairing / stock-airdrop implementation is currently a project plan, not independently proven deployed utility;
- original Nasdaq cease-and-desist story lacks primary-document verification in this pass;
- lore/provenance can support attention but does not itself create token cash flow or intrinsic floor;
- prior ATH proves reflexivity/volatility, not future recoverability;
- current wallet clusters, deployer-related holdings, LP control, top-holder identities/cost basis and migration snapshot risks require deeper reconstruction.

## Pre-outcome Alpha state

`DEEP DIVE / CATALYST WATCH — ENTRY ONLY ON LIVE RECONFIRMATION, NOT BLIND CHASE`

Interpretation: this is a materially better meme thesis than a generic Robinhood-chain pump because the lore is real, old, verifiable and unusually well matched to the chain's tokenized-stock narrative. The potential V2 + QQQ loop is a legitimate catalyst if Pons actually approves and deploys it. But it is not undiscovered alpha and the current Telegram share follows a +46% 24h move, so timing quality is not yet proven.

Upgrade conditions:
1. Pons independently confirms/executes migration for this exact CA / canonical successor mapping.
2. Exact QQQ pairing and stock-airdrop mechanics become verifiable on-chain, with no token-identity ambiguity.
3. Holder/deployer/LP forensics show no dangerous coordinated concentration and distribution continues to broaden.
4. Liquidity persists or improves through/after catalyst without volume being dominated by self-churn.
5. Same-run market state shows constructive absorption after the current impulse rather than immediate social-call exhaustion.

Downgrade / kill conditions:
1. migration stalls, is rejected, or requires a risky/unfavorable token replacement;
2. QQQ/airdrop claim cannot be independently reconciled with Pons/on-chain implementation;
3. creator/team-linked wallets or LP structure create material exit-control risk;
4. holder growth is explained mainly by sybil splitting/dust;
5. current rally retraces with collapsing liquidity/participation after the Telegram/KOL push.

## Highest-information next work

- exact wallet/deployer/LP map and top-holder normalization excluding pools/system addresses;
- first-buyer and recurring-alpha-wallet reconstruction;
- Pons V2 migration status watcher, exact successor/identity mapping and snapshot mechanics;
- QQQ-pair and stock-airdrop implementation proof when available;
- 24h / 3d / 7d outcome learning against this immutable ~23:20 baseline.

## Sources
- User-provided Telegram screenshots, 2026-09-17 ~23:20 Europe/Copenhagen.
- DexScreener exact CA/pair: `https://dexscreener.com/robinhood/0xdb1b57704d5122058ff925c1e765c17b21d065ec`
- The Verge (2017): `https://www.theverge.com/2017/1/10/14223264/meme-economy-reddit-stock-market`
- Know Your Meme: `https://knowyourmeme.com/memes/meme-economy`
- Current project: `https://danq.site/`
- Legacy/current project surface: `https://nasdanqonrh.com/`
- Pons V1 design/source evidence: `https://github.com/blockfile/pons-launcher/blob/main/docs/superpowers/specs/2026-07-25-pons-launcher-design.md`
- Gate Alpha exact-CA listing: `https://www.gate.com/pt-br/announcements/article/101018`
- RH-scan exact token: `https://rh-scan.com/token/0x51fb76be80ab6daaa345d818f4e06441816b4fea`

No portfolio execution authority is created by this research record.