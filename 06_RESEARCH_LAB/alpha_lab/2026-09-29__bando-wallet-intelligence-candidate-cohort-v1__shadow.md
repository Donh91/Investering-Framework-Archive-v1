# Bando wallet-intelligence candidate cohort v1 — SHADOW

Date: 2026-09-29
Status: SHADOW_RESEARCH / EXTERNAL_CLAIM_INTAKE / FORWARD_FREEZE
Owner: #1087 / #1134 existing Alpha Lab + G3 owners
No new scanner: YES
Trade / copy-trade authority: NONE
Source class: USER_SUPPLIED_X_SCREENSHOTS + PUBLIC WEB / EXPLORER CORROBORATION
Freeze time for future observations: 2026-09-29T19:33:00Z

## Purpose

Turn two public "copy these wallets" lists into a falsifiable wallet-intelligence cohort without importing the copy-trading thesis.

The user supplied two Bando lists:

1. Five Solana / Pump.fun deployer wallets advertised as having high graduation rates.
2. Five Arc wallets advertised as unusually early / "insider" winners.

The framework does NOT accept:
`high historical PnL -> smart wallet -> auto copy trade`.

The existing G3 preregistration asks a narrower question:
does point-in-time, entity-adjusted wallet intelligence add incremental predictive value over G2 capital path / microstructure?

These ten addresses are therefore frozen as external research seeds only.

## Governing distinctions

Never collapse these into one score:

- `DEPLOYER_QUALITY`
- `TRADER_SELECTION_QUALITY`
- `EARLY_INFORMATION_EDGE`
- `RELATIONSHIP / PRIVILEGED_ACCESS`
- `COMMON_CONTROL / ENTITY_CLUSTER`
- `EXIT_QUALITY`
- `FORWARD_REPEATABILITY`

A good deployer can be a poor trader.
A connected wallet can be a poor trader.
A high-PnL wallet can be lucky.
A wallet with one spectacular early buy can have no repeatable edge.

## Lane A — Solana deployer-quality seeds

### A1
Address:
`58Ursk3D3sZt4CrUpuJoWjmY17Xwy8XMHmg4tDhKqDYJ`

Bando claim:
- total launches: 19
- graduated: 19
- graduation rate: 100%
- Pump.fun followers: 315

Independent public profile check:
- Pump.fun profile resolves to `duccius`;
- joined 2026-06-16;
- current profile at review showed **104 Followers / 315 Following**.

Important discrepancy:
Bando's "PF followers: 315" appears to have confused **Following** with **Followers** at the review snapshot.

This is a high-value source-quality warning:
even simple headline fields in external wallet lists must be reproduced before use.

Graduation denominator:
UNVERIFIED in this pass.

Current state:
`DEPLOYER_EDGE = UNASSESSED`
`SOURCE_CLAIM_QUALITY = MIXED`

### A2
Address:
`2E94st2NZnzA943HBceijgkw75gXTTxch39yquMBfeQk`

Bando claim:
- 42 launches
- 28 graduated
- 66.7% graduation
- PF followers 3,667

Independent public profile:
- Pump.fun label `MaxPainMaxGain`;
- verified X account @MaxPainMaxGainX shown by Pump.fun;
- current followers at review: ~3,671.

Follower claim is approximately reproduced.
Launch/graduation counts remain UNVERIFIED here.

Current state:
`PUBLIC_IDENTITY = STRONG`
`DEPLOYER_EDGE = UNASSESSED`

### A3
Address:
`yHCxHBEaJW5tbndqC8JciSThr7U1cqLpdcsvHcx6PRe`

Bando claim:
- 249 launches
- 157 graduated
- 63.1%
- PF followers ~12,700
- "Ansem creator"

Independent public evidence:
- Pump.fun profile resolves to `supermandev`;
- current Pump.fun follower count ~12.7K;
- Solscan visibly marks creator activity associated with the address in current transaction surfaces.

Do not treat the social label "Ansem creator" as fully verified beneficial identity from these sources alone.

Current state:
`CREATOR_ACTIVITY = OBSERVED`
`PUBLIC_IDENTITY_ATTRIBUTION = PARTIAL`
`DEPLOYER_EDGE = UNASSESSED`

### A4
Address:
`ARW9NzhpuBVYaYBZo6fW1P1U6LTNwUY6jfi7XC37Sa97`

Bando claim:
- 71 launches
- 49 graduated
- 69%
- PF followers 479

Independent public evidence:
- Pump.fun profile resolves to `kingpigger`;
- current public search snapshot: ~465 followers;
- Defined.fi search surface independently showed a current 30D trader snapshot around:
  - PnL ~$55.2K
  - volume ~$541K
  - win rate ~32.3%

Interpretation:
Even if the high deployer-graduation claim later reproduces, this illustrates why deployer success and trading win rate are different axes.

Current state:
`DEPLOYER_EDGE = UNASSESSED`
`TRADER_EDGE != DEPLOYER_EDGE`

### A5
Address:
`GeBJSHK4WsGrz2HRvTbqvWGx4JRMpHfJG2ikzrYBDuwR`

Bando claim:
- 137 launches
- 78 graduated
- 56.9%
- PF followers 931

Independent public evidence:
- Pump.fun profile resolves to `adolfdevler`;
- current followers at review: ~941;
- live profile visibly contains both large historical winners and substantial losing / dead positions.

This is useful denominator evidence in principle:
the wallet should not be evaluated from graduated/winning launches only.

Current state:
`DEPLOYER_EDGE = UNASSESSED`
`LOSER_COVERAGE = REQUIRED`

## Lane A test design

The Bando metric "graduation rate" is insufficient.

For every deployer derive, point-in-time where possible:

`launches`
`graduated`
`graduation_rate`
`24h survival after graduation`
`7d survival`
`median post-grad MFE`
`median post-grad MAE`
`median liquidity at graduation`
`rug / dead rate`
`creator self-buy / sell behavior`
`creator fee extraction`
`bundle / funding anomalies`
`repeat project / social quality`
`forward outcomes after freeze`

Primary falsifier:
high graduation rate does NOT improve sellable 5x/10x outcomes versus venue / period baseline after adjusting for launch count and market regime.

No deployer becomes `REPEATABLE_EDGE_CANDIDATE` from graduation rate alone.

---

## Lane B — Arc early-information seeds

External Bando claim set was independently found repeated on public social mirrors, but repetition is not independent evidence.

### B1
Address:
`0x94a376a231a7de1a3b1a83628c27459cd4d5417d`

Claim:
- ~$500 ARGUS
- 6 days before Argus first X post
- PnL ~+$910,100

State:
`CLAIM_ONLY / NEEDS_PRIMARY_RECONSTRUCTION`

Required proof:
- exact buy tx;
- ARGUS token identity;
- buy timestamp;
- historical market cap/liquidity;
- canonical timestamp of first Argus X artifact;
- realized vs unrealized PnL;
- all other new-token entries by this wallet in same period.

### B2
Address:
`0x7bdE9c6e91Ae8cE17CbE642a6342F4f4907Ea7d7`

Claim:
- ~$89 entry
- ~$2.8K market cap
- external post calls it "100% insider"
- PnL ~+$70K

Independent public evidence:
- Arc explorer address exists;
- social mirrors repeat the $89 / ~$2.8K claim.

Critical semantics:
`"100% insider"` is an unsupported evaluative label at this stage.

Required proof:
- what asset the $89 entry actually bought;
- project-publicity frontier at entry time;
- direct deployer/funder/project relationship;
- whether entry was public/sellable;
- broader denominator.

Current relationship state:
`UNKNOWN`, not insider.

### B3
Address:
`0xf950f0da8659c62fb8e0b5462f05f9cacdf56938`

Claim:
- ~$1,200 ARGUS
- ~14 days before mainnet
- PnL ~+$361,100

Independent corroboration is materially stronger here:
- Lookonchain publicly reported the same wallet;
- reported 12.1M ARGUS bought for ~$1,200;
- 1.8M sold for ~$30.9K;
- ~10.1M remained worth ~$332K at the observation;
- total marked value around ~$361K.
- Arcscan confirms wallet activity and current/historical token holdings.

This reproduces the large ARGUS outcome broadly.

Still OPEN:
- "14 days before mainnet" as the correct information-frontier definition;
- whether ARGUS was otherwise discoverable;
- full history / failed entries;
- beneficial-owner relationship.

Current state:
`MATERIAL_WINNER = REPRODUCED_EXTERNAL`
`EARLY_INFORMATION_EDGE = CANDIDATE, NOT PROVEN`

### B4
Address:
`0xC3e22E1e275B4d2535F11f42B8c8354dE1af4535`

Claim:
- ~$2,690 TOLLY
- 17 days before mainnet
- PnL ~+$64K

Public social mirrors repeat the claim.
Current bounded pass did not independently reproduce the full trade / outcome from primary chain history.

Current state:
`CLAIM_ONLY / NEEDS_PRIMARY_RECONSTRUCTION`

### B5
Address:
`0x0413751514b5819bd13A5999174869dbD7adabC6`

Claim:
- ~$272 ARGUS
- before Argus X account was created
- PnL ~+$430K

Independent public evidence:
- Arcscan confirms the wallet exists;
- first Arc transaction: 2026-09-02T17:01:40Z;
- current snapshot showed substantial USDC + token holdings and >200 token positions;
- multiple public posts report the extraordinary ARGUS trade.

This proves the address and active high-value trading footprint, but not yet the information-edge claim.

The phrase "before X account existed" requires a real historical artifact audit:
- account creation / first public post timestamps;
- earlier website/domain/docs;
- onchain token deployment / pool / testnet;
- Discord/Telegram/GitHub;
- project contracts or funding.

Current state:
`EARLY_INFORMATION_EDGE = HIGH_PRIORITY_CANDIDATE`
`PRIVILEGED_ACCESS = UNKNOWN`

## Lane B denominator requirement

The Arc lane is vulnerable to extreme survivor bias.

For each wallet enumerate ALL identifiable early/new-token entries over a frozen period, including:
- dead tokens;
- rugs;
- unchanged / low-return positions;
- transferred/gifted tokens;
- dust;
- copy-trades;
- public-call-following entries.

Required metrics:
- number of independent entries;
- fraction preceding first broad public artifact;
- median lead time;
- success rate conditional on lead time;
- sellable MFE / MAE;
- realized capture;
- capital-weighted return;
- outlier dependence;
- common-funder / project relationship;
- repeat project families.

A wallet with one 300x and 100 failures is not automatically useful.

## Information-frontier model

For Arc early-information research, freeze per token:

`T_contract`
`T_first_pool`
`T_first_website`
`T_domain_registration_if_relevant`
`T_first_X_account_or_first_X_post`
`T_first_GitHub`
`T_first_Telegram/Discord`
`T_testnet/mainnet_announcement`
`T_broad_social_propagation`
`T_wallet_entry`

Candidate lead:
`DELTA_INFO = T_public_frontier - T_wallet_entry`

But a positive DELTA_INFO only becomes evidence if the public frontier is complete enough.
Missing earlier artifacts => UNKNOWN, not insider.

## New challenger: Independent Early-Information Convergence

This is the most promising extract from the Bando lists.

Hypothesis:

> Does a new asset have materially better prospective outcomes when 2+ economically independent wallets with previously frozen early-information evidence enter before broad public propagation, versus one wallet alone and versus G2-only?

Required independence:
- no common funder/controller;
- no direct transfer chain;
- no chronic co-trading pattern that makes events redundant;
- no shared public caller preceding both;
- no router/infra false linkage;
- separate self-initiated buys.

Experimental comparison:
A. G2 only
B. one qualifying early-information wallet
C. >=2 qualifying independent early-information wallets
D. cross-archetype convergence:
   early-information wallet + strong deployer/creator lineage + G2

No numeric signal weight is authorized.

## Negative controls

Preserve:
- all future buys by frozen wallets;
- launches they ignore;
- failed entries;
- entries after public propagation;
- late high-market-cap buys;
- tokens that cannot be sold;
- wallets with historically impressive PnL but no forward edge;
- same-entity convergence;
- public copy-trading cascades after wallet lists become popular.

Important new contamination risk:
Once Bando publishes a wallet list, subsequent trades may attract followers/copy-bots.
Post-publication wallet-following behavior may therefore become endogenous and less predictive.

Add:
`PUBLIC_WALLET_LIST_EXPOSURE_AT`
as a contamination timestamp for future evaluation.

## Initial source-quality learning

The first independent checks already falsified blind ingestion:
- 58Ur... was presented as 315 Pump.fun followers; current Pump.fun profile showed 104 Followers / 315 Following.
- Other follower counts were approximately correct but time-varying.
- PnL claims are often repeated by multiple social accounts that may share the same original source.
- "insider" wording is not evidence.

Therefore all external wallet-list features require source-class and timestamp.

## Promotion gates

A wallet may move from `INSUFFICIENT_SAMPLE` to `REPEATABLE_EDGE_CANDIDATE` only if:
1. broader history including failures is reconstructed;
2. edge survives removal of top outlier;
3. entries are self-initiated and sellable;
4. relationship/privilege axis is separately evaluated;
5. at least one future observation exists after this freeze;
6. source/publication contamination is accounted for.

`REPEATABLE_EDGE_SUPPORTED` requires multiple forward successes across independent events/regimes and matched-control lift.

## Current decisions

ADMIT_ALL_10_AS_RESEARCH_SEEDS = YES
AUTO_COPY_TRADE = NO
AUTO_BUY = NO
PROMOTE_BANDO_PNL = NO
PROMOTE_GRADUATION_RATE = NO
CREATE_PARALLEL_WALLET_SCANNER = NO
ROUTE_TO_EXISTING_G3 = YES
FREEZE_FORWARD_WATCH_FROM_2026_09_29 = YES

Highest-priority forensic targets:
1. B5 `0x041375...` — alleged pre-X ARGUS entry.
2. B3 `0xf950...` — independently corroborated 302x-style ARGUS outcome; denominator needed.
3. B1 `0x94a...` — strongest headline PnL claim, needs primary proof.
4. A1 `58Ur...` — claimed 19/19 deployer record and already surfaced source-field discrepancy.
5. A3 `yHCx...` — very large launch sample and public creator profile.

## Next owner actions after Actions quota recovery

Reuse existing owners only:

1. G3 / #1134:
   create point-in-time candidate rows for these addresses; do not alter the original frozen cohort.
2. Wallet registry:
   create per-address records only as history is reconstructed, with state no higher than INSUFFICIENT_SAMPLE initially.
3. Trenches / birth-tape:
   attach wallet observations to future tokens where self-initiated provenance is verified.
4. Prospective evidence:
   preserve every qualifying and non-qualifying future observation.
5. Outcome owner:
   mature 2x/5x/10x, MAE, sellability and failure outcomes.
6. Entity graph:
   deduplicate common funders/controllers before any convergence evidence is counted.

GitHub Actions quota exhaustion on 2026-09-29 means no attempt should be made to spin new Actions schedules today.
This is a research freeze, not runtime deployment.
