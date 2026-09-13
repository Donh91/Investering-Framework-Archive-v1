# AT-SRC-0010 — Maran Robinhood Tool Stack + 7D Wallet Leaderboard Audit

**Captured:** 2026-09-12  
**Status:** `EXTERNAL_RESEARCH_LEAD / TOOL_RADAR / DATA_QUALITY_FINDING`  
**Authority:** `RESEARCH_ONLY / SHADOW_ONLY`  
**Primary workstream:** Memes v3 / Alpha Lab  
**No trade authority:** true

## Source A — Maran tool stack

Primary source supplied by the owner:

`https://x.com/themaran/status/2098343345810772387?s=46&t=SUBrcpc4yI4ppaXpURK03g`

Deterministic X Snowflake timestamp:

`2026-09-11T09:30:13.632Z`

The externally indexed post groups Robinhood/FOMO research tools into a practical workflow:

- **live tape:** `rhtrenches.com`, `fomopulse.app`;
- **research / consensus:** `fomoradar.online`;
- **second-screen / alerts:** FOMO live-feed side panel, tracking bot and leaderboard feed;
- **Robinhood Chain / unlabeled-wallet discovery:** `hoodfi.io`, `stalkchain.com`, `hoodwatch.io`, `hoodstalk.ai`, `robinhoodradar.com`;
- **other niche tools:** `fomoetf.app`, `fomosapiens.xyz`, and a FOMO websocket project.

The source's workflow advice is directionally useful: observe tape first, verify the print, then investigate the wallet/entity behind it rather than installing every tool or trusting one dashboard.

This source is a **discovery radar**, not a canonical provider list. Every provider must be separately evaluated for provenance, terms, latency, survivorship, address-role errors, pricing methodology and incremental value over existing framework sources.

## Open-source benchmark — FomoPulse

Public repository:

`https://github.com/itsnex1s/fomopulse-robinhood-chain-tape`

The repository describes a read-only Robinhood Chain tape reconstructed from public chain data, with roughly one-second live fill visibility and endpoints for tape, traders, bags and discovery.

Research-relevant design ideas include:

- public-RPC-first reconstruction rather than trusting social labels;
- explicit receipt retention and deterministic rebuild/replay;
- excluding pools below a minimum depth from meaningful pricing;
- separating identical multi-wallet token sprays / handouts from paid acquisitions;
- average-cost / round-trip bookkeeping based on observed fills;
- keeping raw chain-derived metrics independent from optional social handles / avatars;
- treating discovery as "who bought" rather than "token is safe".

These ideas are compatible with existing Alpha Lab principles and should be used as an architecture/implementation benchmark, not copied blindly. Any code reuse requires normal license, dependency and security review. Logged-in third-party session credentials are not authorized by this source note.

## Source B — 7D realized-PnL wallet leaderboard claim

A second owner-supplied social post claimed that the five most profitable Robinhood Chain traders over the prior seven days were specific addresses with approximately +$87K to +$135K realized PnL and advised followers to wait for those wallets to buy something new.

A current Hoodfi chain page exposes the same ranking as a 7D realized-PnL leaderboard attributed to Dune-derived analytics, making Hoodfi / Dune the likely upstream data family for the claim.

**The list must not be imported as a smart-wallet watchlist without role resolution.**

## Critical finding — leaderboard contamination

Cross-token holder inspection found a high-confidence contamination pattern in at least three of the five addresses supplied in the social leaderboard:

- the same address appears as an extremely large holder / inventory address across multiple unrelated Pons-family launches;
- the repeated balance pattern is approximately three-quarters of supply across different tokens;
- this behavior is much more consistent with launchpad curve / protocol inventory / settlement / service infrastructure than with an ordinary discretionary trader.

Therefore a generic wallet-PnL query can manufacture very large apparent "realized trader PnL" when protocol/service addresses are treated as traders.

This is a load-bearing Alpha Lab lesson:

> `ENTITY / ADDRESS ROLE > REPORTED WALLET PNL`

The exact competitive addresses and per-address classifications remain restricted in `Donh91/secrets`.

## Mandatory ADDRESS_ROLE_GATE

Before any leaderboard, KOL list, Nansen-style label, scanner ranking or social claim can put an address into `WATCH`, classify the address role from chain-native evidence.

Minimum role vocabulary:

- `EOA_TRADER`
- `SMART_ACCOUNT_TRADER`
- `PROTOCOL_SERVICE`
- `CURVE_OR_LAUNCHPAD_INVENTORY`
- `ROUTER`
- `POOL_OR_LP_INFRASTRUCTURE`
- `FEE_COLLECTOR`
- `DEPLOYER_OR_CREATOR_INFRASTRUCTURE`
- `BRIDGE_OR_SETTLEMENT`
- `UNKNOWN`

Rules:

1. `UNKNOWN` cannot be promoted to wallet-alpha watch status.
2. Service / inventory / pool / router / fee-collector activity cannot count as discretionary trading PnL.
3. Passive receipts, dust, sprays, airdrops and inventory transfers remain excluded from intentional acquisition.
4. Realized PnL must be reproducible from eligible intentional fills, route and executable pricing where possible.
5. Entity clustering precedes independence assumptions.
6. Outlier ablation is mandatory: a wallet whose score is dominated by one exceptional token is not automatically repeatably skilled.
7. Conditional skill is evaluated by context, venue, token age and entry state, not by one global PnL rank.
8. Public visibility / follower capital is evaluated after skill, because a historically good wallet may lose expectancy once widely tracked.

## Wallet-PnL sanitization sequence

Canonical research sequence for wallet-leaderboard candidates:

`ADDRESS ROLE`
→ `INTENTIONAL SWAP FILTER`
→ `SERVICE / INVENTORY EXCLUSION`
→ `ECONOMIC ENTITY CLUSTERING`
→ `REALIZED PNL REPRODUCTION`
→ `OUTLIER ABLATION`
→ `CONDITIONAL SKILL`
→ `PUBLIC VISIBILITY / CAPACITY`
→ `PROSPECTIVE WATCH`

A source-reported leaderboard rank is only a discovery prior.

## Initial adjudication

- **Maran tool map:** high-value external discovery / tooling radar. Particularly valuable for finding complementary Robinhood Chain observability and open-source implementation ideas.
- **FomoPulse:** high-value architecture / code benchmark for deterministic chain-tape reconstruction, receipt replay, dust/handout separation and wallet-flow bookkeeping.
- **Hoodfi chain page:** useful external benchmark and source-discovery surface, but its wallet-PnL ranking requires service-address sanitization before use.
- **Top-5 wallet post:** valuable mainly as a data-quality stress test. It demonstrates why reported profit is not enough to identify a trader.

## Framework effect

This note does not create a new engine, scheduler, provider dependency, paid subscription or trade path.

It strengthens existing Memes v3 / Alpha Lab wallet research by adding an explicit address-role gate before PnL-based qualification. Existing conditional-wallet, entity-graph, visibility/capacity and prospective outcome rules remain authoritative.
