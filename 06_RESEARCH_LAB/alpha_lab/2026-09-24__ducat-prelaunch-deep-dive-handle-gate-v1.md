# DUCAT pre-launch deep dive + Handle Gate v1

Date: 2026-09-24
Status: PROSPECTIVE_PRELAUNCH_SPECIAL_TEST
Authority: Alpha Lab research only
Trading authority: NONE
Prospective credit before freeze: 0

## Identity and launch clock

Project: Ducat
Official social: @ducat_money
Official site: https://ducattreasury.com/
Whitepaper: https://ducattreasury.com/paper
Chain: Robinhood Chain
Official announced CA: `0xD0cA71118ca21D674f9018A53026a38A0AB54DbF`
Official announced launch: Friday 2026-09-25 around 09:00 "EST".

Time-zone ambiguity is material:
- 09:00 New York local time in late September would normally map to ~15:00 Europe/Copenhagen;
- literal EST would map to ~16:00 Europe/Copenhagen.
Operational watch window: 14:45-16:15 Europe/Copenhagen until the first authenticated onchain launch event resolves T0.

## Canonical coverage audit

Fresh searches immediately before this packet found no DUCAT/Ducat/exact-CA record in:
- Donh91/Investering-Framework-Archive-v1
- Donh91/secrets
- current public issue search.

Classification:
- FRAMEWORK_VISIBILITY_MISS: CONFIRMED
- PRELAUNCH_AUTOMATION_DISCOVERY_MISS: CONFIRMED_CANONICAL_MISS
- ECONOMIC_ALPHA: UNPROVEN
- RETROSPECTIVE_CREDIT: 0

This is a material miss because the project had an official site, a 61-page whitepaper, repeated pre-launch social explanation, an announced launch date and an exact CA before manual user intake.

## Freshness / identity

Official @ducat_money currently says no token or NFTs are live yet and separately publishes the exact launch CA above.

There are already unrelated/copycat DUCAT/ducat.money Pons pools with DIFFERENT token CAs and very low liquidity/security scores. These are not the official announced asset.

Binding rule:
ONLY exact CA `0xD0cA71118ca21D674f9018A53026a38A0AB54DbF` can enter the official DUCAT gate unless @ducat_money explicitly supersedes it with authenticated correction.

Any same-name DUCAT/ducat.money token with another CA = REJECT / IDENTITY_FAIL.

## Project-age / team risk

Observed public footprint is extremely young:
- official X account joined September 2026;
- ducattreasury.com appears in new-domain records dated 2026-09-17;
- only ~34 official posts and sub-1k follower scale were visible during audit.

No public GitHub organization/repository or independently verified named builder/team identity was reproduced in this packet.

External commentator VirtualBacon spoke positively about the development team based on a mutual contact, but that is social attestation, not identity/security verification.

Classification:
- TEAM_IDENTITY: UNVERIFIED / PSEUDONYMOUS
- DOMAIN_AGE: VERY_YOUNG
- CODE_PUBLICATION: NOT_FOUND
- WHITEPAPER_DEPTH: HIGH
- IMPLEMENTATION_PROOF: PENDING

This combination is not an automatic scam signal, but it demands contract-first rather than narrative-first qualification.

## Protocol model understood from first-party material

### 1. Market, Reference and Reserve are different values
The project explicitly separates:
- MARKET: free-floating, uncapped price;
- REFERENCE: protocol monetary-policy level intended only to move upward;
- RESERVE/BACKING: treasury assets per DUCAT.

Illustrative first-party material shows:
- market $3.00;
- reference $1.00;
- stablecoins $1.30 / DUCAT;
- equities $0.30 / DUCAT;
- total backing $1.60 / DUCAT.

Important:
A $3 market price is NOT economically protected at $3 merely because backing/reference exist.

### 2. Stablecoins alone back the promise
The published mint rule says new DUCAT cannot be created unless stablecoins alone cover the reference on all supply, checked after settlement. Ordinary issuance opens only above 1.20x cover.

Tokenized equities add treasury value/upside but do not back the redemption promise.

### 3. Redemption is conditional, not a hard guaranteed floor
Published material states redemption is open and pays the LOWER of reference or reserve, less 1%, from stablecoins only.

Therefore "Reference only goes up" must not be interpreted as a guaranteed market floor.
If reserve is below reference, redemption can clear below reference.

### 4. Reference ratchet
Reference steps up only after sustained excess reserve proves the higher level can be carried and has no downward path in the contract.

Critical audit requirement:
verify the exact contract authority and algorithm governing this ratchet. A "no downward path" narrative is only meaningful if privileged admin setters/upgrades cannot bypass it.

### 5. Launch sequence creates a temporary economics gap
Official launch communication says:
- token trading goes live first;
- protocol bonds open 1-2 hours later after oracle observation;
- eight-hour epochs then begin;
- first 12 epochs are a four-day bootstrap;
- NFT Pass auctions begin day one.

This is a major Handle Gate fact:
the earliest token market can exist BEFORE the protocol's bond/reserve mechanism has become observable in production.

Early price action must therefore be separated from operational proof.

### 6. NFT Pass layer
Official communication says maximum ~1,000 passes across Founder / Charter / Member tiers, auctioned Dutch-auction style.
Eligibility can come from bonding volume; whitelist can waive the minimum bonding requirement.
Official copy says passes collect at least half of every DUCAT expansion and can be redeemable for tokenized-equity backing.

This creates a second claim on protocol economics and must be modeled before assuming all treasury growth accrues economically to ordinary DUCAT holders.

## Primary protocol risks

1. CONTRACT / ADMIN RISK
Exact token, treasury, bond, redemption, reference-controller, oracle, hook and NFT contracts are not yet reproduced.

2. ORACLE BOOTSTRAP RISK
Bonding opens after only ~1-2 hours of token market history. A thin launch market may make early price/oracle readings manipulable unless the implementation has robust windows/guards.

3. PREMIUM RISK
Market can trade far above reference and reserve. Protocol health does not prevent a large market-price drawdown from an early hype premium.

4. RESERVE QUALITY RISK
Only stablecoins support the promise. Need exact supported stablecoins, haircut rules, issuer/depeg exposure and reserve accounting.

5. REFERENCE IMMUTABILITY RISK
Need to prove no privileged path can lower/overwrite/reference-reset or upgrade the logic.

6. MINT AUTHORITY RISK
Need to prove ordinary 1.20x cover rule cannot be bypassed by owner/admin/emergency/bootstrap mint paths except explicitly disclosed genesis/bootstrap behavior.

7. REDEMPTION EXECUTION RISK
Need to prove DUCAT can actually be redeemed, settlement is permissionless, redemption cannot be paused selectively, and quoted reserve/reference inputs are correct.

8. V4 HOOK / LP RISK
Uniswap v4 hooks add a large smart-contract attack surface. Need hook code, permissions, callbacks, fee logic and external calls.

9. NFT ECONOMIC SENIORITY / DILUTION RISK
Pass holders capture a stated share of expansion and equity backing. Need exact formula and priority relative to DUCAT holders.

10. ANON / VERY-YOUNG TEAM RISK
No independently verified named builder history or public code was reproduced before launch.

11. COPYCAT RISK
Same-name DUCAT pools already exist. Exact-CA authentication is mandatory.

## HANDLE GATE

### STATE R0 - NO ENTRY YET
Current state before official onchain T0.

Remain R0 if ANY is true:
- exact official CA not deployed/readable;
- official source conflicts on CA/chain;
- token source/bytecode unavailable and cannot be safely classified;
- transfer/sell behavior unknown;
- launch pool identity unknown;
- privileged mint/blacklist/freeze/tax behavior unresolved;
- team/treasury destination materially conflicts with published model.

Current pre-launch state: R0.

### STATE R1 - IDENTITY + BASIC SAFETY PASS
Can only occur after exact official CA is live.

Required:
- chain id 4663;
- exact CA match;
- deploy tx/block/time frozen;
- creator/deployer identified;
- bytecode/source or deterministic semantic inspection;
- total supply and mint authority reproduced;
- owner/admin/proxy roles reproduced;
- transfer restrictions / blacklist / pause / taxes reproduced;
- official launch pool bound;
- executable buy AND sell path proven;
- no material honeypot / one-way transfer behavior;
- no conflicting official CA.

If any critical field UNKNOWN -> remain R0.

R1 allows OBSERVE only, not an economic-quality conclusion.

### STATE R2 - EARLY MARKET PROBE ELIGIBLE
Requires R1 plus:
- initial allocations and launchAndBuy/bootstrap allocation known;
- exemptions/privileged-wallet surface known;
- no dominant undisclosed insider/deployer concentration;
- liquidity is executable rather than cosmetic;
- sell simulation / small real-world sellability evidence exists;
- transaction activity not obviously one actor / mechanical wash pattern;
- copycat confusion is resolved.

R2 means the asset is technically eligible for a TINY speculative probe review only.
It does NOT validate the protocol economics.

### STATE R3 - PROTOCOL MECHANICS VERIFIED
Expected no earlier than bonds/oracle activation, roughly T+1-2h.

Requires R2 plus:
- oracle source/window and manipulation guards reproduced;
- bond contract live;
- reserve/stablecoin accounting readable;
- supported stablecoins and haircuts known;
- current reference value readable;
- stablecoin reserve per DUCAT readable;
- ordinary issuance 1.20x cover guard reproduced;
- redemption formula reproduced;
- small redemption or deterministic simulation succeeds;
- no hidden privileged bypass of mint/reference/redemption rules found;
- treasury destinations/custody known;
- v4 hook contract/permissions understood;
- NFT Pass economic claims mapped sufficiently to assess holder dilution/seniority.

R3 is the first point where "treasury-backed DUCAT" is an observed production claim rather than whitepaper-only.

### STATE R4 - QUALIFIED SPECULATIVE ENTRY REVIEW
Requires R3 plus acceptable early market structure:
- holder/buyer breadth materially independent;
- no severe creator/cluster concentration;
- no rapid treasury/deployer extraction;
- liquidity survives early volatility;
- market premium versus reference/reserve is explicitly measured;
- entry does not rely on an obviously extreme transient wick;
- protocol state remains internally consistent across multiple blocks/reads.

R4 means a speculative entry can be evaluated on price/asymmetry.
It still does not mean automatic BUY.

## PRICE / PREMIUM GATE

Always compute before an R4 decision:
- Market / Reference
- Market / stablecoin reserve per DUCAT
- Market / total net backing per DUCAT

Interpretation:
- the larger the premium, the more the position is a growth/reflexivity trade rather than a reserve-floor trade;
- reference monotonicity does not justify paying an unlimited premium;
- a healthy protocol can coexist with a large token drawdown if the market premium compresses.

No fixed universal multiple is promoted from this one case. Freeze actual ratios and compare prospectively.

## Launch-window handling

Because the official account says "around 9am EST", monitor 14:45-16:15 Europe/Copenhagen on 2026-09-25.

Priority sequence:
1. authenticate exact CA;
2. freeze deployment/launch origin;
3. reject copycats;
4. contract/admin/sellability gate;
5. allocation/concentration;
6. early market structure;
7. wait for oracle/bonds;
8. verify reserve/reference/redemption;
9. only then evaluate market premium and entry quality.

Do not let FOMO invert that order.

## Hard invalidators

Immediate NO_TOUCH / R0:
- CA mismatch;
- source conflict;
- undeclared proxy/admin upgrade path with broad powers;
- arbitrary mint;
- blacklist/freeze/transfer trap;
- sell failure;
- hidden tax materially different from disclosed behavior;
- privileged reference/reserve manipulation;
- oracle easily manipulable with no guard;
- treasury assets not verifiably held where claimed;
- redemption not executable as described;
- serious unexplained deployer/related-wallet concentration;
- official communication compromise.

## Prospective evaluation

Freeze from this packet:
- pre-launch visibility;
- exact CA;
- stated launch time;
- whitepaper claims;
- current social propagation;
- absence of prior framework record.

Post-launch horizons:
5m, 15m, 1h, 2h, 4h, 24h, 3d, 7d, 14d, 30d.

At each horizon log:
- Handle Gate state;
- market/reference/reserve ratios;
- liquidity/sellability;
- holders/buyer breadth;
- concentration/clusters;
- deployer/treasury flows;
- oracle/bond/reference/redemption health;
- NFT Pass economics;
- MFE/MAE;
- social propagation;
- whether Alpha Lab intelligence added information before price outcome.

No retrospective credit. No failed horizon deletion.

## Current verdict

ALPHA_LAB_RELEVANCE: VERY_HIGH
PRELAUNCH_DISCOVERABILITY: VERY_HIGH
FRAMEWORK_VISIBILITY_MISS: CONFIRMED
IDENTITY_BINDING: HIGH for official announced CA, deployment pending
TEAM_IDENTITY: UNVERIFIED
WHITEPAPER / ECONOMIC DESIGN: HIGH_INFORMATION
PRODUCTION_IMPLEMENTATION: UNPROVEN
COPYCAT_RISK: HIGH
SMART_CONTRACT_RISK: UNKNOWN
HYPE / PREMIUM_RISK: RISING
CURRENT_HANDLE_GATE: R0_NO_ENTRY_YET
NEXT_GATE: OFFICIAL EXACT-CA DEPLOYMENT + R1 CONTRACT/SELLABILITY AUDIT

The case is valuable precisely because the economic design is interesting enough to create FOMO while production truth is still unavailable.
