# NOIR / NoirPay Alpha Lab live false-negative audit v1

Date: 2026-09-24
Status: LIVE_FALSE_NEGATIVE_AUDIT + FORWARD_WATCH
Authority: Alpha Lab research only
Trading authority: NONE

## Identity

Project: NoirPay
Token: NOIR
Chain: Robinhood Chain
Chain id: 4663
Exact CA: `0xA5F832390447b050955D7b734a9A2fA861B4d3AB`

Current first-party Project→CA binding: HIGH.
Basis: official NoirPay docs publish the exact CA as the only $NOIR contract and identify Robinhood Chain as chain 4663.

First-party token documentation also states:
- fixed supply: 1,000,000,000 NOIR;
- 18 decimals;
- standard ERC-20;
- no owner function;
- Pons launchpad / ETH bonding-curve venue;
- 2% creator fee on curve trades;
- no staking or emissions;
- token utility limited to tiers/fee discounts plus discretionary revenue-funded buybacks.

These are project claims until independently reproduced where relevant.

## Manual intake trigger

The user supplied a fresh X screenshot on 2026-09-24 showing an external caller describing a small NOIR position around "60K FDV" and linking the exact CA plus noirpay.app.

The screenshot is USER_SUPPLIED_SOCIAL_CONTEXT.
The caller explicitly stated they had not completed enough DD. Therefore caller enthusiasm is not accepted as verification of project claims or economic quality.

## Fresh framework coverage check

Immediately before this packet, fresh searches of:
- Donh91/Investering-Framework-Archive-v1
- Donh91/secrets
- current public issue search

returned no exact CA, NOIR or NoirPay record.

Classification at intake:
- CANONICAL_PRELAUNCH_FREEZE: ABSENT
- CANONICAL_TOKEN_FIRST_SEEN: ABSENT
- FRAMEWORK_VISIBILITY_MISS: CONFIRMED
- AUTOMATION_PRELAUNCH_DISCOVERY_MISS: CONFIRMED_CANONICAL_MISS, subject only to later discovery of a noncanonical run receipt
- ECONOMIC_ALPHA_MISS: UNPROVEN
- PROSPECTIVE_CREDIT_BEFORE_MANUAL_INTAKE: 0

This classification matters because the Project→CA Autonomous Supervisor had already been upgraded to search for pre-launch Pons/Robinhood projects and had run after that upgrade before this manual intake.

## Why the miss is material

NOIR was not an invisible one-block launch.

Public surfaces existed before the 2026-09-24 manual intake and before the current public launch propagation:
- official documentation with project thesis and exact CA;
- official GitHub organization and three public repositories;
- public third-party Telegram propagation dated 2026-09-22 with website, docs, dApp, GitHub and social links;
- first-party token docs state on-chain token verification on 2026-09-21;
- current official docs say the product itself remains pre-launch while $NOIR is live.

This is exactly the source family the pre-launch Project→CA lane was intended to observe.

## Important clock separation

Do not collapse these into one "launch time":

1. PROJECT_VISIBILITY_T0 - earliest reproducible public project surface.
2. TOKEN_CONTRACT_T0 - contract creation/deployment.
3. FIRST_PARTY_CA_PUBLICATION_T0 - first authenticated project publication of exact CA.
4. PONS_ECONOMIC_LAUNCH_T0 - first executable Pons market/curve event.
5. BROAD_PROPAGATION_T0 - first material external caller/community propagation.

Current evidence suggests the exact token contract existed before the later "live now on Pons" social propagation. The exact timestamps require deterministic chain/social reconstruction.

## Product reality vs marketing

The strongest correction from DD is that NoirPay is NOT yet a live full neobank.

Official docs explicitly state:
- NoirPay is pre-launch;
- product contracts are not live on Robinhood Chain mainnet yet;
- a dApp preview exists;
- $NOIR is live;
- shielded account, private yield routing, viewing keys, card, payroll and business API are future/product-design surfaces.

Therefore:
- "self-custodial privacy neobank" = product thesis/design;
- live mainnet neobank usage = NOT ESTABLISHED;
- card/yield/payroll/compliance claims = DESIGN/PRELAUNCH unless separately reproduced.

This prevents the exact failure mode "professional site + feature copy = shipped product".

## Public code evidence

Official GitHub organization: `noirpayapp`
Public repositories observed at intake:
- `noirpayapp/stealth-handles`
- `noirpayapp/viewing-keys`
- `noirpayapp/payroll-router`

This is stronger than a no-code marketing page. The repositories contain implementation and test surfaces for stealth addresses, viewing/disclosure tooling and a payroll/payment router.

However code presence is not deployment/adoption.

### Claim-link feature

The `stealth-handles` README implements the same basic mechanism described in the user-supplied X post:
- one-time address;
- private key in URL fragment;
- recipient sweeps funds;
- sender retains the key and can reclaim an unclaimed link.

This means the feature has public implementation evidence.

But the same repository states:
- "Not audited. Use at your own risk."

So feature-code evidence is PRESENT; production-security evidence is NOT.

### Viewing-key specification mismatch

This is a material product-integrity finding.

Marketing/docs describe scoped/date-limited/revocable viewing access.

The current `viewing-keys` README says the v1 viewing key:
- reveals every incoming payment from the first note onward;
- has no cryptographic date range;
- has no expiry;
- is "revoked" only by rotating to new account keys;
- time-limited access is instead implemented as a sealed statement snapshot/link.

Classification:
`SPEC_IMPLEMENTATION_MISMATCH`

This is not evidence of fraud. It is evidence that current implementation semantics are narrower/different than some higher-level product copy.

### Payroll router

The public payroll router is a thin ownerless forwarder according to its README and includes Foundry/SDK implementation surfaces.

The repository also states "Not audited."

Again:
`PUBLIC_CODE_PRESENT != MAINNET_PRODUCT_LIVE != SECURITY_AUDITED`.

## Current market context at intake

A fresh public market snapshot around the audit showed NOIR around the low-hundreds-of-thousands market-cap range, with tens of thousands of dollars of liquidity, hundreds of holders and substantial same-day trading activity.

A current GMGN snapshot around the audit showed approximately:
- market cap: ~$147k;
- liquidity: ~$36.8k;
- holders: ~498;
- 24h volume: ~$254.7k;
- token creation: 2026-09-21 15:45:20 as reported by that surface;
- pool creation: 2026-09-22 04:22:43;
- top-10 concentration: ~22.7%;
- dev balance shown as 0% at that snapshot.

These are market-provider observations, not canonical chain truth. Reproduce before scoring.

The user's external-caller screenshot claimed entry near 60K FDV. That exact entry level is not accepted as verified until the corresponding market timestamp is reproduced.

## Alpha Lab interpretation

### Positive evidence families

1. PROJECT_FIRST_SURFACE
   - coherent project thesis before broad current propagation.

2. EXACT_PROJECT_TO_CA_BINDING
   - official docs publish one exact CA.

3. PUBLIC_CODE
   - three project repositories with code/test surfaces.

4. CHAIN_NATIVE_FIT
   - privacy + USDG + tokenized-stock use case is specifically designed around Robinhood Chain.

5. PRELAUNCH_DISCOVERABILITY
   - public docs/GitHub/Telegram existed before current manual intake.

6. EARLY_MARKET_ACTIVITY
   - current market surfaces show nontrivial liquidity, holders and transaction volume.

### Negative / uncertainty families

1. PRODUCT_PRELAUNCH
   - core product contracts are not live on mainnet according to NoirPay itself.

2. SECURITY_UNPROVEN
   - public repositories explicitly state not audited.

3. SPEC_IMPLEMENTATION_MISMATCH
   - viewing-key implementation does not match some scoped/expiring key language at the primitive level.

4. VERY_YOUNG_PROJECT_SURFACE
   - public GitHub/project footprint is extremely recent.

5. MARKET_EXTREME_VOLATILITY
   - early token price/market-cap path has already moved violently; current entry convexity cannot be inferred from the original low-FDV thesis.

6. ACCESS_FAIRNESS_UNKNOWN
   - launchAndBuy, initial allocation, exemption arrays, deployer history, sniper/bundler provenance and transfer-vs-buy structure remain unreproduced.

7. REAL_USAGE_UNKNOWN
   - no independently reproduced protocol TVL, card activity, payroll users, yield deposits or business revenue.

## Current Alpha Lab verdict

ALPHA_LAB_RELEVANCE: HIGH
PROJECT_TO_CA_BINDING: HIGH
PRELAUNCH_DISCOVERABILITY: HIGH
FRAMEWORK_VISIBILITY_MISS: CONFIRMED
AUTOMATION_DISCOVERY_MISS: CONFIRMED_CANONICAL_MISS
PRODUCT_SUBSTANCE: MEDIUM_HIGH_AS_PRELAUNCH_CODE_AND_DESIGN
PRODUCT_LIVE_STATUS: PRELAUNCH
SECURITY_STATUS: UNAUDITED / UNKNOWN
MARKET_SIGNAL: QUALIFIED_DEEP_DIVE_WATCH
MOONSHOT_EDGE: UNPROVEN
TRADING_AUTHORITY: NONE

This case should not be learned as "privacy neobank + GitHub = winner".
It should be learned as a coverage failure: a project with multiple public prelaunch surfaces, exact CA, code and an explicit Pons path existed before manual discovery and was not frozen by the Project→CA lane.

## Required deterministic next work

Reconstruct:
- earliest public project timestamp;
- exact first-party CA publication timestamp;
- token creation tx/block/time;
- exact Pons economic launch tx/block/time;
- Pons factory/version;
- creator/deployer funding history;
- initial buy / allocation / exemption/access-fairness surface;
- supply and MC-vs-FDV semantics;
- liquidity/sellability through launch;
- holder/buyer breadth;
- transfers vs purchases;
- sniper/bundler/related-wallet clusters;
- product contract deployment status;
- any actual mainnet usage;
- caller/source propagation timeline;
- market checkpoints around $25k / $50k / $100k / $250k where reproducible.

## Automation learning

The fix should target coverage, not NOIR-specific keywords.

Pre-launch scans should explicitly include:
- new Robinhood Chain project docs containing PRE-LAUNCH / LAUNCHING SOON / PONS / token contract language;
- newly created project GitHub orgs/repos linked from first-party docs;
- exact CA appearing in docs before broad launch propagation;
- external ecosystem posts linking a project bundle (web + docs + GitHub + X) before launch.

Candidate qualification still requires the existing freshness/identity gate. No keyword alone promotes a project.

## Forward treatment

From this manual intake timestamp onward, NOIR is eligible for genuine LIVE_FORWARD_WATCH observations.

Freeze future changes prospectively:
- exact origin/access-fairness reconstruction;
- product contract deployment;
- code/audit changes;
- real usage/adoption;
- liquidity/sellability;
- holder/buyer breadth;
- wallet convergence;
- social propagation;
- Phoenix-like compression/re-entry if later applicable;
- realized outcomes.

No pre-intake event earns prospective alpha credit.
