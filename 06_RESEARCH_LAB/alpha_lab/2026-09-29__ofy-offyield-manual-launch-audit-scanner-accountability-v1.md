# OFY / OffYield manual launch audit + scanner accountability v1

Date: 2026-09-29
Status: MANUAL_INTAKE / PROSPECTIVE-LATE-LAUNCH SNAPSHOT / SHADOW
Owner: #1087 / existing Alpha Lab owners
Project: OffYield
Official X: @offyield
Official site: https://www.offyield.com/
Official CA: 0xfd1a35778d9798f13c6fb97d29c07a5ce3f7fb5e
Chain: Robinhood Chain / 4663
Trade authority: NONE
Automatic scanner credit: ZERO

## 1. Why this case matters

User manually surfaced the official $OFY launch approximately ~1h after on-chain T0.

Fresh canonical searches of:
- Donh91/Investering-Framework-Archive-v1
- Donh91/secrets

found no prior match for:
- OffYield
- exact CA
- meaningful OFY project record

Therefore this is a new manual Alpha Lab intake.

This case is especially important because:
1. OffYield had public pre-launch project signals for days before T0;
2. fake/copycat OFY launches existed before the official token;
3. the official launch occurred while GitHub Actions included minutes were exhausted;
4. the official token repriced aggressively immediately after launch.

Scanner attribution must separate PRE-LAUNCH DISCOVERY COVERAGE from T0 RUNTIME AVAILABILITY.

## 2. Project -> CA identity — STRONG / VERIFIED

User supplied a screenshot from verified @offyield showing:
- "$OFY is live";
- CA `0xfd1a35778d9798f13c6fb97d29c07a5ce3f7fb5e`.

Fresh first-party site read shows the same CA on the OffYield homepage.

Pons launch calldata embeds:
- project name: "OffYield Neobank"
- symbol: OFY
- description matching official project
- X: https://x.com/offyield
- Telegram: https://t.me/offyield

Therefore:
`PROJECT_CA_BINDING = STRONG / VERIFIED`.

This is particularly valuable because OffYield publicly warned before launch that fake tokens were circulating and that only the CA posted from @offyield should be trusted.

## 3. Product is materially real, but product != token

Official site/docs describe a live non-custodial Robinhood Chain product:
- users deposit USDG;
- funds are supplied into a lending market;
- principal and spendable yield are separated;
- spending draws only from accrued yield;
- principal withdrawal is user-controlled;
- fail-closed behavior is documented;
- prepaid card purchase is available through CryptoRefills;
- product is early access with capped deposits.

Current docs say the underlying yield source is the Steakhouse USDG vault on Morpho.

Critical token-value-capture separation:
the docs explicitly state:

- users' deposits and interest do NOT touch $OFY;
- the core yield/spend product does not require OFY.

Current token utility observed:
- project says OFY holders receive 5% USDG cashback on prepaid-card purchases;
- cashback is separately funded.

Therefore:
- PRODUCT_SIGNAL = MATERIAL
- CORE_TOKEN_DEPENDENCY = NONE
- TOKEN_UTILITY = CASHBACK
- TOKEN_VALUE_CAPTURE = LIMITED / NOT YET PROVEN DURABLE

This is structurally similar to the RHX402 lesson:
`REAL PRODUCT != NECESSARILY STRONG TOKEN ECONOMICS`.

## 4. Security / legitimacy evidence

Independent Shieldify public audit portfolio lists:
- OffYield - Robinhood
- review ID 160
- August 2026
- "Yield-Bearing Stablecoin Vault (Spendable-Yield Card Product)"

This corroborates that a real security review exists.

Do not upgrade this to:
- bug-free;
- insured;
- token-safe;
- Pons launch-safe.

The audit concerns the product/vault code, not necessarily the economic quality of the OFY token launch.

The project also claims OffYield LLC is registered in Wyoming, filing 2026-002059669.
This snapshot preserves the claim; company-record verification is separate.

## 5. Exact launch origin — VERIFIED

Blockscout:
- token contract: verified `PonsV2LauncherToken`
- first transaction / launch:
  2026-09-29T18:08:13Z
- launch tx:
  `0x31e24b0dfa47ba4e7935b1f04b0331ce045950b5f9a2dc933e01700ebe957433`
- launch caller / recipient:
  `0xfF4336362d25F962B8a5F674bF73eD0Caaf079a1`
- total supply: 1,000,000,000 OFY
- pairToken in launchAndBuy: native ETH
- quoteIn: 0.036 ETH
- snipeTaxExemptions: NONE
- initial OFY to launch caller:
  ~20.3624659M OFY = ~2.036% supply

At 18:13:03Z, ~4m50s after launch, the launch caller transferred the exact ~20.3624659M OFY initial position to:
`0x000...dEaD`.

Therefore:
- INITIAL_CREATOR_BUY ≈ 2.04%
- INITIAL_CREATOR_POSITION_BURNED = YES
- SNIPE_TAX_EXEMPTIONS = 0

These are positive anti-rug launch-origin observations.

They do NOT clear post-launch coordinated accumulation.

## 6. Launcher provenance

Launcher wallet:
`0xfF4336362d25F962B8a5F674bF73eD0Caaf079a1`

First observed Robinhood Chain transaction:
2026-09-29T15:16:11Z

Funding:
`0x88D25C861938a91AF4ad57aD964a8fCc6c6351d3`
-> launcher
0.05046 ETH
at 15:16:11Z

Launch occurs ~2h52m later.

Funder:
- active on Robinhood Chain since 2026-07-13;
- no current canonical match in the known Alpha Lab / Wazz operator registry from bounded GitHub search.

Interpretation:
- launcher itself is fresh;
- upstream funder is not fresh;
- UNKNOWN whether this is project treasury/operator funding, service funding or unrelated infrastructure.

No cabal conclusion from this edge alone.

## 7. Live market snapshot

Fresh Dexscreener API snapshot after user surfaced the launch:

Primary OFY/ETH pool:
`0x67e59e2543e5ba24129c476a966def72503a1dda3b09626f609ca8e621183c36`

Pool created:
2026-09-29T18:08:31Z, ~18s after on-chain launch.

Observed:
- price ~ $0.001195
- market cap / FDV ~ $1.17M
- liquidity ~ $105K
- volume ~ $2.55M
- 24h / since-launch buys ~7,536
- sells ~6,996
- price change ~ +1831%
- holder count from Blockscout ~2,660+

Additional OFY/USDG and OFY/ETH pools were also created soon after launch.

Primary USDG pool snapshot:
- price ~ $0.001210
- liquidity ~ $50K
- volume ~ $259K

Interpretation:
- SELLABILITY = OBSERVED
- PUBLIC TRADING = VERY ACTIVE
- LIQUIDITY = MATERIAL FOR FRESH PONS TOKEN
- HEADLINE EXPANSION = EXTREME
- ORGANIC_INDEPENDENT_DEMAND = NOT PROVEN FROM TX COUNT ALONE

High transaction / holder counts may include bots, EIP-7702 wallets, arbitrage and sybil activity.

## 8. Holder topology

Fresh Blockscout top-holder snapshot contains major system addresses:

- PonsV2MemeHook ~8.45%
- PonsV2LaunchLocker ~8.16%
- PoolManager ~5.36%
- burn address ~2.04%

These must NOT be treated as ordinary whale concentration.

Largest observed non-system holder:
~1.62% supply.

Approximate top-10 non-system holdings in the visible snapshot are around ~10% combined.

Many top addresses are EIP-7702 delegated accounts.

Current interpretation:
- no obvious single external 20-80% whale dominates the visible holder table;
- distribution appears materially broader than BYTE's most dangerous patterns;
- economic independence remains UNKNOWN;
- EIP-7702 / automation means raw wallet count is not enough.

Required next step:
`early buyer graph -> funding ancestry -> timing/amount/gas similarity -> beneficial inventory lineage`.

## 9. Fake-launch / identity lesson

Before official launch, OffYield publicly warned:
- fake OFY branding/tokens existed;
- the only real CA would be posted by @offyield.

Public search surfaces show multiple pre-existing tokens/pools using OffYield/OFY branding and different CAs.

This validates a core Project->CA rule:

`TICKER / BRAND MATCH != PROJECT IDENTITY`

The authoritative binding here is:
authenticated project surface + exact CA + matching first-party site + matching launch calldata.

This should be retained as a positive identity-resolution case.

## 10. Scanner accountability

Fresh canonical search found no OFY / OffYield / exact-CA row in either control plane or secrets plane.

Therefore:
`AUTOMATIC_DISCOVERY = NOT EVIDENCED`
`AUTOMATIC_ALERT_CREDIT = ZERO`

Important causal split:

### A. Pre-launch discovery
OffYield publicly signaled the upcoming OFY launch before 2026-09-29:
- project said token launch was coming;
- fake-launch warning explicitly said official CA would later come from @offyield;
- audit/mainnet/token launch were publicly discussed.

This occurred BEFORE the 2026-09-29 Actions quota exhaustion.

Therefore a complete Project-first discovery system cannot attribute the entire miss to today's GitHub Actions outage.

Potential class:
`PRELAUNCH_PROJECT_DISCOVERY_MISS`.

### B. T0/runtime monitoring
Official T0 occurred at 18:08:13Z on 2026-09-29.

GitHub Actions included minutes were already exhausted at 3000/3000 with a $0 hard stop on the same date.

Therefore absence of Moonshot/Phoenix scheduled runtime evidence around T0 must be classified:
`RUNTIME_OBSERVABILITY_IMPAIRED_BY_ACTIONS_QUOTA`

Do NOT score this T0 absence as scanner-code failure.

Correct attribution requires two independent rows:
1. project-source coverage before launch;
2. runtime availability at exact launch.

## 11. Alpha interpretation at manual observation time

This is NOT an early-entry call at the frozen manual observation.

By the time the user surfaced it:
- the main pool had already expanded roughly +18x on Dexscreener's since-launch price-change metric;
- market cap was already around $1.17M;
- liquidity around $105K;
- millions in volume had traded.

Therefore:
- PRE-LAUNCH PROJECT ALPHA = potentially missed
- T0 / early-market alpha = retrospective/open, must be reconstructed
- CURRENT EARLY ASYMMETRY = materially consumed
- PRODUCT QUALITY = better than typical fresh Pons launch
- TOKEN VALUE CAPTURE = materially weaker than product quality
- RUG SIGNAL = no classic launch-origin rug evidence observed so far
- COHORT / OPERATOR RISK = still OPEN

Do not confuse:
`LEGIT PROJECT`
with
`GOOD ENTRY AT ANY PRICE`.

## 12. High-value learning

1. **Project-first discovery matters.**
   OFY was discoverable as a project before its CA existed.

2. **Fake copycats make exact CA provenance essential.**
   A brand/ticker scanner alone would have failed badly.

3. **Product legitimacy and token economics must remain separate.**
   OffYield may have a real audited product while OFY remains mainly an incentive/marketing token.

4. **Clean launch calldata does not end cohort analysis.**
   0 exemptions + creator burn are positive, but not sufficient.

5. **System-holder normalization is mandatory.**
   Pons hook, locker, PoolManager and burn addresses must be excluded or role-classified before concentration scoring.

6. **EIP-7702 wallet counts are not independent-user counts.**

7. **Scanner attribution must separate discovery from runtime.**
   Actions quota can explain T0 collection failure but cannot explain missing a project that publicly announced itself days earlier.

## 13. Required next research

A. Freeze project-publicity timeline:
- first launch announcement;
- fake-token warning;
- audit publication;
- exact official CA post;
- T0.

B. Reconstruct earliest economically viable public entry:
- Pons curve / pool prices;
- liquidity;
- sellability;
- slippage;
- market cap;
- MFE/MAE.

C. Early-wallet cohort audit:
- first 25-50 meaningful buyers;
- fresh-wallet age;
- common funders;
- synchronized buy/retry patterns;
- EIP-7702 implementation clustering;
- later descendant inventory.

D. Token economic audit:
- exact cashback qualification threshold;
- cashback funding source / budget;
- OFY demand sink;
- emissions / fee capture / buyback / governance, if any;
- whether product adoption creates durable OFY demand.

E. Scanner postmortem:
- why OffYield did not enter the prelaunch project watchlist before Actions quota exhaustion;
- separately document launch-day runtime hard stop.

## Current state

PROJECT / PRODUCT SIGNAL: STRONGER_THAN_TYPICAL_PONS
PROJECT_CA_BINDING: VERIFIED
SECURITY REVIEW EXISTENCE: VERIFIED
CORE_PRODUCT_DEPENDENCY_ON_OFY: NONE
TOKEN_UTILITY: LIMITED / CASHBACK
TOKEN_VALUE_CAPTURE: OPEN / WEAKLY ESTABLISHED
LAUNCH PRIVILEGE: LOW IN OBSERVED CALLDATA
CREATOR INITIAL BUY: ~2.04%, BURNED
SNIPE EXEMPTIONS: 0
PUBLIC DEMAND: VERY STRONG
CLASSIC RUG SIGNAL: NOT OBSERVED
COHORT / OPERATOR RISK: OPEN
EARLY ALPHA AT MANUAL OBSERVATION: LARGELY CONSUMED
AUTOMATIC SCANNER CREDIT: ZERO
PRELAUNCH DISCOVERY MISS: LIKELY / REQUIRES OWNER RECONSTRUCTION
T0 RUNTIME MISS: CONFOUNDED BY ACTIONS QUOTA HARD STOP

No trade recommendation is created by this file.
