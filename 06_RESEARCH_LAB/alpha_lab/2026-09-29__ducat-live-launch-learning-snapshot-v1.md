# DUCAT live launch learning snapshot v1

Date: 2026-09-29
Status: PROSPECTIVE LIVE / POST-T0 LEARNING SNAPSHOT
Owner: #1087 / existing Alpha Lab owners
Project: Ducat
Official CA: 0xD0cA71118ca21D674f9018A53026a38A0AB54DbF
Chain: Robinhood Chain / 4663
Trade authority: NONE
Automatic alert credit: ZERO until reconstructed from actual runtime evidence

## Purpose

Freeze what was actually observable after DUCAT launched, preserve what Alpha Lab got right and wrong, and prevent later hindsight from rewriting the case.

This file does not replace the pre-launch snapshot:
`2026-09-29__ducat-launch-day-supersession-snapshot-v1.md`

It is the next point-in-time row.

## 1. Launch identity and timing — VERIFIED

Fresh Blockscout read shows the exact pre-announced CA is now deployed and verified:

`0xD0cA71118ca21D674f9018A53026a38A0AB54DbF`

- contract name: DucatToken
- token symbol: DUCAT
- decimals: 18
- proxy: none observed
- first on-chain transaction timestamp: 2026-09-29T13:08:54Z
- creation transaction: `0x954059e2d621a6e28db7c795d538aae9247e1c967e8fe6dab76af359915a2933`
- contract is verified on Blockscout
- @ducat_money posted "Ducat is now live" at 2026-09-29T13:09:24Z

Therefore:
- EXACT_CA_BINDING = VERIFIED
- PROJECT_TO_CA = VERIFIED
- LAUNCH_T0 = 2026-09-29T13:08:54Z on-chain
- FIRST_PARTY_LIVE_CONFIRMATION ≈ T0 + 30s

The previously announced 13:00 UTC launch time was approximate. Do not rewrite it retrospectively.

## 2. Genesis transaction — VERIFIED structure

Creation/settlement transaction shows:

- 100,000 USDG transferred into the genesis settlement path;
- 33,333.333333333333333300 DUCAT minted in the settlement transaction;
- 10,000 DUCAT minted in the same launch flow;
- 1 DUCAT additional mint observed in the same transaction;
- Uniswap v4 position NFT minted during launch setup.

This is consistent in broad shape with the published design:
- genesis cap 100,000 USDG;
- genesis sale price 3 USDG;
- 30% of raise to pool / 70% to treasury;
- Uniswap v4 market created at launch.

Do not infer exact treasury allocation accounting solely from the three mint events; preserve transaction-level accounting for a dedicated reconciliation.

## 3. Live market snapshot

Fresh DEX Screener snapshot around 2026-09-29 ~16:05Z:

- DUCAT/USDG Uniswap v4 pair:
  `0xc3fc1d3d70d94772c6f6b3491af14bbc11b5f75ae2bd66b63890bd89ee830b19`
- price ≈ $53.02
- liquidity ≈ $252K
- FDV / displayed market cap ≈ $2.2M
- volume since launch ≈ $969K
- traders ≈ 1,936
- buys / sells ≈ 3,523 / 2,333
- buy / sell volume ≈ $535K / $434K
- buyers / sellers ≈ 1,888 / 614
- live sell transactions observed

Therefore:
- EXECUTION = LIVE
- SELLABILITY = OBSERVED
- PUBLIC_DEMAND = STRONG
- CLASSIC immediate honeypot / no-sell failure = NOT SUPPORTED by observed market activity

This does NOT clear all contract/control risk.

## 4. Headline launch expansion — large, but do not over-credit

Genesis reference sale price was $3 per DUCAT.

Observed market price ≈ $53 implies a headline ratio of roughly:

`53 / 3 ≈ 17.7x`

This is useful as market-expansion evidence, but NOT yet a realizable scanner return.

Reasons:
- genesis buyers were placed into pDUCAT, not necessarily unrestricted spot DUCAT;
- opening tax began extremely high and decayed over time;
- actual earliest public executable entry price is not yet reconstructed;
- pDUCAT withdrawal/exit mechanics matter for genesis participants;
- MFE must be measured from the first eligible prospective alert timestamp, not from the ceremonial $3 sale.

Therefore:
- HEADLINE_MARKET_EXPANSION = VERY_STRONG
- REALIZABLE_ALPHA_MULTIPLE = OPEN
- AUTOMATIC_SCANNER_CREDIT = ZERO pending reconstruction

## 5. Tax conflict resolved by current first-party material

The pre-launch 2% vs 3% source conflict is now superseded by current first-party Ducat 101:

- launch tax: 90% both sides initially;
- halves every 4 minutes;
- reaches 2% within the first hour;
- standing swap tax: 2% buy + 2% sell;
- tax is taken in USDG on the Uniswap v4 pool.

Therefore:
- LAUNCH_TAX_PARAMETER = RESOLVED_CURRENT_FIRST_PARTY
- CURRENT_STANDING_SWAP_TAX = 2% BUY / 2% SELL

Historical pre-launch conflict remains preserved as a valid source-conflict event.

## 6. Holder topology — raw concentration is misleading

Fresh Blockscout holder read:

- total DUCAT supply ≈ 43,894.7185 DUCAT
- `ProtectedDucat` contract holds ≈ 35,108.14 DUCAT
- this is ≈ 79.98% of total supply
- `PoolManager` holds ≈ 2,505.47 DUCAT ≈ 5.71%

A naïve concentration scanner could misclassify the ~80% ProtectedDucat balance as a whale/operator concentration.

But `ProtectedDucat` is the protocol staking vault.

Therefore:
`PROTOCOL_CUSTODY != BENEFICIAL_OWNER_CONCENTRATION`

This is a direct framework lesson:
holder concentration must be entity-role aware before becoming rug/cabal evidence.

## 7. pDUCAT / genesis cohort

Fresh pDUCAT read:

- pDUCAT contract: `0x102a9CE100075b4D59291ec85B4ebAc072b456dC`
- name: ProtectedDucat / token: Protected DUCAT
- active DUCAT in vault ≈ 35,108 DUCAT
- pDUCAT total supply ≈ 34,905
- pDUCAT holder count ≈ 115

Top pDUCAT holder snapshot contains:
- one external address around 1.50% of pDUCAT supply;
- many genesis accounts around 333.333 pDUCAT each, ≈0.955% each.

Current interpretation:
- raw genesis distribution appears materially broader than BYTE's observed concentrated pre-positioned inventory;
- no single obvious external genesis whale dominates the pDUCAT holder table;
- however 115 holder addresses are NOT evidence of 115 independent economic actors.

Required next test:
`funding ancestry -> fresh-wallet age -> common funder -> batch timing -> gas fingerprint -> beneficial ownership / control clusters`

State:
- RAW_GENESIS_BREADTH = POSITIVE
- ECONOMIC_INDEPENDENCE = UNKNOWN
- CABAL / COMMON_CONTROL = NOT CLEARED

## 8. Protocol is producing live state

Fresh first-party app snapshot after bonds opened:

- Epoch 1 / bootstrap active
- market TWAP ≈ $58.01
- Reference = $1.00
- backing cover ≈ 1.73x
- stable backing / DUCAT ≈ $1.73
- DUCAT supply ≈ 43,895
- treasury display ≈ $460,397
- USDG ≈ $76,826
- tax vault ≈ $180,292
- protocol-owned liquidity ≈ $203,279
- active in pDUCAT vault ≈ 35,108 DUCAT
- bonds ≈ 105.37 DUCAT bonded so far
- first NFT Pass auction + protocol bonding announced live at ~16:02Z

This is stronger than pure launch marketing:
the protocol exposes measurable treasury, bonding, staking and policy state.

But first-party app state is still an application representation.
Critical values should be reconciled to contracts before being treated as independent truth.

## 9. Key risk changed after launch

Pre-launch primary concern:
- deployment
- hook/tax correctness
- sellability
- genesis allocation
- privileged access / cabal

Post-launch primary concern is increasingly:
`VALUATION_PREMIUM_VS_BACKING`

Observed:
- spot ≈ $53
- first-party market TWAP ≈ $58
- Reference = $1
- stable backing / DUCAT ≈ $1.73

So current spot is roughly:
- ~30x stable backing per token;
- >50x current Reference.

This does NOT mean price must converge to backing.
DUCAT has additional reflexive mechanisms:
- bond demand;
- prints;
- tax capture;
- pass economics;
- reference ratchet;
- protocol-owned liquidity.

But "reserve-backed" must NOT be interpreted as downside protection near the current market price.

Framework state:
- PROTOCOL_OPERATIONALITY = MATERIAL / LIVE
- RESERVE_BACKING = MATERIAL
- CURRENT_MARKET_PREMIUM = EXTREME
- RUG_RISK != VALUATION_RISK

Keep these risk families separate.

## 10. BYTE comparison

BYTE taught:
- early-wallet address balances are insufficient;
- inventory can migrate to descendants before sell;
- paid catalyst + apparent source-wallet holding can coexist with hidden economic distribution;
- early buyer != insider;
- beneficial inventory lineage matters.

DUCAT currently differs:
- exact project/CA binding was public before launch;
- launch mechanics were documented;
- verified contract and explicit protocol roles exist;
- live sellability is observed;
- genesis inventory is largely represented through the ProtectedDucat vault;
- raw pDUCAT holder distribution is broader.

Do not overfit:
DUCAT can still contain coordinated genesis participants or later coordinated distribution.
Use the same beneficial-inventory logic prospectively.

## 11. Scanner / alert accountability — important miss candidate

Fresh GitHub read:
- no DUCAT / exact-CA runtime record was found in `Donh91/secrets`;
- no TIME_SENSITIVE_ALPHA_REVIEW record was found for DUCAT;
- issue #110 remains open for Moonshot scheduler/liveness;
- private-repo checkout repair merged on 2026-09-28, but issue explicitly remains fail-closed pending post-repair liveness proof.

Therefore:
DUCAT must NOT receive automatic scanner credit merely because it was manually known pre-launch.

Current label:
`MANUAL_PRELAUNCH_KNOWN / AUTOMATIC_ALERT_NOT_PROVEN`

Potentially important failure:
A pre-announced exact CA, launch time, official project surface and later >10x market expansion existed, yet no automatic Alpha alert is currently evidenced.

Do NOT yet conclude scheduler failure caused the miss.
Required reconstruction must separate:
1. scanner never woke;
2. scanner woke but source did not surface DUCAT;
3. DUCAT was observed but rejected;
4. execution/tax gate correctly held it out;
5. candidate became eligible only after most repricing;
6. notification bridge failed after valid candidate formation.

This causal classification is more valuable than calling the case a simple scanner miss.

## 12. Required retrospective-without-hindsight reconstruction

Freeze and reconstruct:

`T_project_known`
-> `T_CA_published`
-> `T_deploy = 13:08:54Z`
-> `T_market_open`
-> `T_tax_decay checkpoints`
-> `T_first public sellable entry`
-> `T_scanner_observation`
-> `T_candidate formation`
-> `T_alert eligibility`
-> `T_alert delivery or miss`
-> realizable MFE / MAE

At each checkpoint preserve:
- price / MC / liquidity;
- tax;
- actual round-trip execution;
- holder breadth;
- genesis-cohort topology;
- independent wallet evidence;
- public visibility;
- project/catalyst evidence;
- critical unknowns.

Do not use current $53 price to justify an earlier alert.

## 13. Prospective tests from here

### Test A — genesis economic independence
Determine whether the ~115 pDUCAT addresses are independent or linked.

### Test B — privileged execution
Determine whether any genesis / related wallet had materially different tax, routing or execution rights.

### Test C — beneficial inventory lineage
Track pDUCAT withdrawals / DUCAT descendants and later exits at cluster level.

### Test D — valuation regime
Track:
`market price / Reference / stable backing / total backing / tax vault / POL / bond demand`
through bootstrap.

### Test E — first print
At 2026-09-30T00:00Z verify:
- print executes;
- amount;
- recipients;
- pDUCAT accounting;
- pass accounting;
- backing and supply effects;
- whether published formulas reconcile.

### Test F — scanner accountability
Reconstruct exact automatic discovery and notification path with zero hindsight.

## 14. Alpha Lab learning extraction

Promote as research principles, NOT live thresholds:

1. **Protocol custody is not holder concentration.**
   Entity-role classification is mandatory before concentration scoring.

2. **A public exact CA + scheduled launch is a high-value prospective test asset.**
   Missing such cases is measurable discovery/reliability failure, not anecdote.

3. **Tax decay creates an execution clock.**
   Alpha quality must be measured from the first economically viable public entry, not T0 or genesis price.

4. **Reserve-backed does not mean market-backed.**
   Separate contract redemption/backing floor from speculative market premium.

5. **Positive and negative cases need equal rigor.**
   BYTE is a negative economic-outcome lesson; DUCAT is currently a positive launch-expansion case. Neither should be rewritten to fit the framework.

6. **Manual knowledge is not scanner credit.**
   Prospective credit requires actual runtime evidence and timestamped alert eligibility.

7. **The best Alpha Lab case is not the biggest multiple.**
   It is the case where discovery, execution, risk, alert timing and later outcome can all be reproduced.

## Current state

- PROJECT / CA: VERIFIED
- LIVE MARKET: VERIFIED
- SELLABILITY: OBSERVED
- PROTOCOL STATE: LIVE / MATERIAL
- CLASSIC RUG SIGNAL: NOT OBSERVED
- GENESIS COMMON CONTROL: UNKNOWN
- ECONOMIC INVENTORY LINEAGE: OPEN
- VALUATION RISK: HIGH
- MARKET EXPANSION FROM $3 GENESIS REFERENCE: VERY STRONG
- REALIZABLE PUBLIC ALPHA: OPEN
- AUTOMATIC ALPHA ALERT CREDIT: ZERO / NOT PROVEN
- CASE VALUE TO ALPHA LAB: VERY HIGH

Next highest-information event:
`first-print verification + scanner reconstruction + genesis wallet graph`.
