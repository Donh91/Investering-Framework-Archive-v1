# EDGEONCHAIN FORENSIC RESEARCH QUEUE

Status: RESEARCH_ONLY / HIGH PRIORITY
Date: 2026-09-13
Issue owner: `#922`
Lifecycle owner: `#885`
Candidate role: prediction-market alpha source, copyability benchmark and future automated-vault strategy family

## Core boundary

Do not buy `$EDGE`, deposit into Edge vaults, connect signing keys, copytrade, or grant live betting / portfolio authority from this research.

The research target is the evidence chain:

`prediction quality -> source execution -> delayed copyability -> vault economics/security`

Social performance claims are discovery evidence only.

## Current source-audit findings

### Official model description

Edge documentation describes Oddy as an in-house probability engine that:

- ingests sports, market and contextual data;
- estimates outcome probabilities;
- compares model probability with market-implied probability;
- considers only positive expected-value selections;
- ranks selections by expected value / risk;
- sizes positions under embedded risk rules;
- executes on-chain through prediction-market protocols.

Primary references:

- `https://edgeonchain.gitbook.io/docs/overview/meet-oddy`
- `https://edgeonchain.gitbook.io/docs/overview/our-edge`
- `https://edgeonchain.gitbook.io/docs/overview/our-background`

These pages describe intended architecture. They are not independent evidence that the claimed predictive edge exists.

### Public Polymarket footprint

A public Polymarket profile exists for `@EdgeOnchain`:

- `https://polymarket.com/profile/%40EdgeOnchain`

An indexed historical snapshot showed 147 predictions and a largest win of about `$1,755`, but the snapshot is stale and cannot validate current social claims.

Polymarket exposes public data surfaces suitable for primary reconstruction once the canonical proxy-wallet address is frozen:

- user activity;
- user trades;
- current positions;
- closed positions;
- accounting snapshot ZIP (`positions.csv`, `equity.csv`);
- public profile search.

Canonical API documentation:

- `https://docs.polymarket.com/market-data/overview`
- `https://docs.polymarket.com/api-reference/core/get-user-activity`
- `https://docs.polymarket.com/api-reference/core/get-trades-for-a-user-or-markets`
- `https://docs.polymarket.com/api-reference/core/get-closed-positions-for-a-user`
- `https://docs.polymarket.com/api-reference/misc/download-an-accounting-snapshot-zip-of-csvs`

### Material performance-documentation inconsistency

Official vault pages currently describe approximately:

- Conservative: `3.5% weekly`, based on 14,750 backtest bets;
- Balanced: `5.8% weekly`, based on 6,200 backtest bets;
- Aggressive: `9.2% weekly`, based on 8,350 backtest bets.

The general vault page also shows a one-year table compounding these percentages weekly.

However, the vault-specific 36-month tables produce balances consistent with compounding the same percentages approximately once per **month**, while the surrounding text calls them **weekly ROI**.

References:

- `https://edgeonchain.gitbook.io/docs/the-vaults/how-it-works`
- `https://edgeonchain.gitbook.io/docs/the-vaults/conservative-vault`
- `https://edgeonchain.gitbook.io/docs/the-vaults/balanced-vault`
- `https://edgeonchain.gitbook.io/docs/the-vaults/aggressive-vault`

Ruling:

`DOCUMENTATION_INCONSISTENCY / PERFORMANCE_EVIDENCE_NOT_ADMISSIBLE`

Do not use the headline backtest ROI as evidence until the raw bet set, cadence, sizing and calculation method are independently reproduced.

### Vault engineering disclosure

A recent public Edge development update describes a rebuilt Polygon ERC-4626 vault design with:

- `Ownable2Step`;
- `Pausable`;
- reentrancy protection;
- a dedicated betting wallet;
- maximum 50% of vault assets deployed at one time;
- capital-return accounting;
- explicit `recordCapitalLoss` handling.

The same update says testing found two important defects before deployment, including a missing loss-accounting function that would otherwise have overstated vault value.

The update also acknowledges that an earlier dashboard P&L pipeline had problems with losing-bet settlement and duplicate counting before being rebuilt.

Research consequence:

Historical dashboard P&L cannot be accepted as canonical truth without independent transaction-level reconciliation.

### Current autonomy state must be verified, not inferred

The official GitBook describes fully autonomous selection/execution and future automated vault operation. A recent engineering update, however, described remaining work around independent audit, betting-wallet hardening and settlement automation before public launch.

Therefore current status is:

`AUTONOMY_CLAIM_REQUIRES_CURRENT_PRIMARY_VERIFICATION`

Do not silently merge roadmap/intended-state language with deployed-state evidence.

### Identity / KYC / audit

Edge's team page links an Assure DeFi listing:

- `https://projects.assuredefi.com/project/edgeonchain`

The Assure page independently confirms an Edgeonchain listing, while explicitly warning that KYC does not establish project safety or legitimacy.

Hashlock has publicly acknowledged supporting Edge ahead of launch. No final public Hashlock report was independently located in the initial search pass.

Ruling:

- KYC listing: `VERIFIED_LISTING / NOT_SECURITY_EVIDENCE`
- Hashlock involvement: `SUPPORTED_BY_PUBLIC_ACKNOWLEDGEMENT`
- final audit findings: `NOT_YET_VERIFIED`

## Claims ledger - discovery only

The following claims remain unverified unless primary bet-level evidence proves them:

- follower challenge around `$1,000 -> $85,000/$93,000`;
- 25 consecutive wins;
- 38 wins from 39;
- 40x+ follower performance;
- exact `2.5%` fee on profitable bets;
- fully autonomous end-to-end vault settlement today.

The follower challenge is especially important to separate from Edge source performance because promotional posts describe additional follower parlaying. A follower's compounding/parlay result is not automatically the AI model's return.

## P0 - Identity and source freeze

Resolve with primary evidence:

1. canonical Polymarket proxy wallet(s);
2. any Overtime / other execution wallets;
3. Polygon vault contract addresses;
4. dedicated betting wallet address;
5. verified vault source / bytecode;
6. dashboard and Dune identifiers;
7. final Hashlock report and remediation state;
8. exact fee implementation;
9. `$EDGE` token contract: `0x8f3aa4cA9fC915ffa3f18fE9914b8292De25db82`.

Fail closed on ambiguous identity.

## P0 - Immutable source ledger

For every retrievable Edge bet freeze:

- proxy wallet;
- tx hash;
- condition / asset ID;
- event and outcome;
- entry timestamp;
- executed price;
- stake / USDC amount;
- settlement;
- realized P&L;
- single / parlay / correlated-event cluster;
- source and retrieval timestamp.

Retain all losses, unresolved markets and cancelled cases.

## P0 - Historical claim reconciliation

Reconstruct separately:

1. Oddy / Edge source account;
2. `$1k -> $85k/$93k` third-party follower challenge;
3. streak claims;
4. official backtest pools.

Decompose return into:

- prediction selection;
- sizing;
- compounding;
- parlay leverage;
- correlation;
- follower modifications.

Any unreconciled headline remains `UNVERIFIED`.

## P1 - Prediction-alpha test

Singles are the primary statistical unit. Parlays remain a separate analysis.

Measure:

- realized ROI / expectancy;
- hit rate by entry-probability bucket;
- model probability vs market-implied probability when model probability is published;
- calibration;
- Brier / log loss where admissible;
- post-signal market movement;
- drawdown / tail loss;
- sport / market-type segmentation.

Controls:

1. market implied probability;
2. matched odds / sport / time controls;
3. naive favorite strategy;
4. equal stake;
5. simple fixed-fractional sizing;
6. matched random picks.

Use event/day dependence-aware resampling. Repeated bets on the same match are not independent evidence.

## P1 - Copyability / latency decay

For each public signal compare:

- source fill;
- first independently observable timestamp;
- +30 seconds;
- +1 minute;
- +5 minutes.

Use contemporaneous price/orderbook and realistic fill assumptions.

Measure:

- expected return after delay;
- adverse repricing;
- available depth;
- slippage / fees;
- missed fills;
- capacity.

Required classification:

`SOURCE_EDGE_AND_COPYABLE / SOURCE_EDGE_NOT_COPYABLE / NO_VERIFIED_SOURCE_EDGE`

## P1 - Vault security and economics

Before any vault promotion verify:

- ERC-4626 accounting;
- `totalAssets` while capital is deployed;
- loss recording;
- 50% deployment cap;
- withdrawal / redeem behavior;
- owner/admin powers;
- pause and recovery powers;
- betting-wallet permissions;
- proxy / upgradeability state;
- settlement automation vs manual authority;
- final security audit;
- exact fee rate and fee base;
- fee economics across mixed win/loss sequences.

A fee on every winning bet is not equivalent to a high-water-mark fee on net new profit.

## P2 - Frozen prospective test

Historical evidence may qualify this source for frozen forward shadow only.

Pre-register signal definition, timestamp rule, sizing, latency and cost model before collection.

Target before any promotion beyond research:

- >=100 settled independent single-market observations;
- >=8 elapsed weeks;
- immutable signals before event start;
- no retrospective edits;
- all losses/unresolved cases preserved;
- positive post-cost expectancy under a realistic copy delay;
- dependence-aware uncertainty assessment.

Parlays do not inflate the independent observation count.

## Success condition

A positive outcome requires all of the following, not one headline P&L chart:

1. primary ledger reconciles;
2. source edge survives market baselines;
3. copy edge survives realistic delay/costs;
4. vault accounting/security is independently acceptable;
5. frozen prospective results survive #885 governance.

## Kill / downgrade criteria

Kill or materially reduce priority if:

- wallet identity cannot be resolved;
- losing bets or settlements are materially incomplete;
- historical claims need selective exclusions;
- alpha disappears after market-implied / matched-odds controls;
- source alpha is not realistically copyable;
- performance is mainly parlay leverage / sizing rather than prediction quality;
- vault accounting or audit findings remain unresolved;
- fee mechanics erase user expectancy.

## Framework relationship

`#885` remains the scientific experiment owner.

Use its anti-leakage, immutable-artifact, no-retroactive-rescore and monotonic trial-accounting rules. Do not create a second experiment engine and do not grant execution authority from this queue.
