# Wazz Robinhood Serial Extraction / Operator Fingerprint Audit v1

Date: 2026-09-27  
Status: SHADOW RESEARCH / HISTORICAL REPRESENTATION / PROSPECTIVE DESIGN INPUT  
Owner: existing Alpha Lab / #1087  
Trade authority: NONE  
Parallel scanner: FORBIDDEN

## Executive conclusion

The WazzCrypto Robinhood-chain thread materially upgrades an existing Alpha Lab research direction.

The repository already had:
- Pons V2 launch-origin freezing;
- PRIVILEGED_LAUNCH_SURFACE from DEED;
- recurring-wallet/deployer graphs;
- matched-denominator work for Pons;
- Blockscout deterministic enrichment;
- birth-tape / anti-hindsight discipline.

The new information suggests a stronger cross-launch unit of analysis:

> operator lineage, not token-by-token rug classification.

The relevant question is no longer only:
"Is this CA suspicious?"

It becomes:
"Does the launch share funding ancestry, wallet cohorts, collectors, launch configuration or proceeds-routing with a historically extractive operator cluster?"

This may create pre-launch or launch-second information value if reproduced prospectively.

## External thread claims, not yet fully reproduced

WazzCrypto publicly claims:
- 53 Robinhood Chain launches linked within roughly two months;
- approximately $18.43M extracted across the linked ring;
- 45/53 linked through proceeds from one launch funding the key used for a later launch;
- several launches linked by reused signer/key addresses or shared collectors;
- many launches concentrated >70% supply into 70-200-wallet bundles;
- repeated fake/relaunch sequences for PINK, CRUMBS and DEED-family launches;
- at least two additional serial-deployer operations outside the main ring.

These are external forensic claims until independently reproduced by Alpha Lab.

## Screenshot-derived high-value observations

The supplied Wazz screenshots report examples including:
- LEGS: ~84% peak concurrent operation supply, 77 wallets, ~1,155.32 ETH extracted;
- CRUMBS: ~86% peak concurrent operation supply, 99 wallets, ~1,135.93 ETH extracted;
- PINK: ~83.84% peak concurrent operation supply, 125 wallets, ~534.23 ETH extracted;
- launch board examples with ~82-86% sniped/operation concentration and extreme later drawdowns;
- cross-launch flow diagrams where proceeds converge into collectors / relays and later fund another launch.

These images are evidence of Wazz's analysis, not independent verification.

## Independent Blockscout reproduction performed 2026-09-27

Chain: Robinhood Chain, 4663.

### CRUMBS
Exact CA: 0x80bAa4b3bfAC6f4978700dF824B1B3d98e889136
- verified PonsV2LauncherToken-family contract;
- launch tx: 0xf49fbbb1469e7b807c88f55f28c23e859c3a445c7b274578899451b9f5b91bf9;
- launch time: 2026-09-08T23:57:56Z;
- launcher/recipient: 0x00607eC8622cf64Cf6735090891d5870a1598Fe4;
- launchAndBuy quoteIn: ~0.053019 ETH;
- initial launcher transfer: ~30M / 1B ~= 3%;
- 15 snipeTaxExemption addresses in decoded calldata.

### DRAFT
Exact CA: 0xfe51aaf6AF1Ec2eB9286e0BdC3c9dc39240cB8F5
- verified PonsV2LauncherToken;
- launch tx: 0xbe401cf36699c1cfbc9d12f5ac1d3958fa765f9003dd316ce9bb6251e81ca31d;
- launch time: 2026-09-10T23:45:04Z;
- launcher/recipient: 0x02b208A186a9567bFE70152D0421558F87Edb6B7;
- launchAndBuy quoteIn: ~0.053019 ETH;
- initial launcher transfer: ~30M / 1B ~= 3%;
- 15 snipeTaxExemption addresses.

### DEED
Exact CA: 0x5E55f18453545d0D4314C5106a2D8Db934298E95
Existing canonical reproduction remains consistent:
- launch time 2026-09-21T23:51:56Z;
- launcher/recipient 0x0052BB21E9CccfcB790913fe3D9bc52cC45d9dD9;
- initial launcher position 2.99%;
- 25 snipeTaxExemptions.

### Critical anti-false-positive note
CRUMBS, DRAFT and DEED expose the same contract creator address:
0x3711ceA4feaDE896C913C68F01Eda97Cb06D1A42.

This MUST NOT be treated as common operator evidence. It is consistent with shared Pons infrastructure/factory mechanics.

Likewise, the common launch path through 0xe33E9E479dF8802cb0866d5d05258bEc4cF62948 is infrastructure, not operator identity by itself.

This confirms why operator fingerprinting must explicitly separate:
PROTOCOL_SHARED vs OPERATOR_SPECIFIC edges.

## New candidate object: OPERATOR LINEAGE GRAPH

Do not create a parallel engine. Extend existing Alpha Lab recurring-wallet/deployer graph semantics.

Candidate node roles:
- launch caller / recipient;
- pre-launch funding key;
- upstream hop / relay;
- bundle signer / authorisation wallet;
- snipe-tax-exempt wallet;
- early acquisition wallet;
- creator-fee recipient;
- collector / proceeds hub;
- bridge/cash-out wallet;
- linked project/social identity;
- token/launch instance.

Candidate edge types:
- DIRECT_FUNDS_BEFORE_LAUNCH;
- PROCEEDS_FUNDS_NEXT_LAUNCH;
- SAME_LAUNCH_CALLER;
- SAME_SIGNER_ADDRESS;
- WALLET_COHORT_OVERLAP;
- EXEMPTION_COHORT_OVERLAP;
- SAME_COLLECTOR;
- PROCEEDS_CONVERGENCE;
- SAME_BATCH_OR_AUTHORIZATION_PATTERN;
- SHARED_SOCIAL_OR_PROJECT_CONTROL_ROOT;
- RELAUNCH_FAMILY;
- INFRASTRUCTURE_ONLY.

Every edge requires timestamp, source and confidence.

## Operator-link confidence

Use evidence classes, not a single opaque score.

CONFIRMED:
- exact same EOA signs/launches multiple cases;
- direct onchain proceeds from known ring fund a later launch key;
- exact same collector receives proceeds across launches.

STRONG:
- high wallet-cohort overlap plus shared funding ancestry;
- repeated pre-launch funding route through the same non-infrastructure relays;
- repeated privileged-wallet set plus proceeds convergence.

WEAK:
- same ticker/theme;
- same launchpad;
- same factory/router;
- similar round-number launch config;
- similar timing alone.

UNKNOWN remains UNKNOWN.

## Dual-axis interpretation

A high extraction-risk launch can still experience a large public price expansion.

Therefore never collapse:
RUG / EXTRACTION RISK
and
TRADEABLE MOMENTUM / REALIZABLE UPSIDE

into one label.

Candidate prospective outputs:
- OPERATOR_LINK_STATE
- EXTRACTION_RISK_STATE
- PRIVILEGED_SUPPLY_STATE
- PUBLIC_BUYER_BREADTH
- FIRST_OPERATOR_SELL_SECONDS
- OPERATOR_SELLTHROUGH_1M / 5M / 15M / 60M
- MFE from first public-eligible quote
- MAE from first public-eligible quote
- bounded-notional sellability/slippage
- REALIZABLE_EXIT_WINDOW

ATH/peak market cap is never sufficient evidence of realizable 10x/20x.

## Why this matters for early discovery

The highest-value potential signal is upstream of CA-level chart behavior:

known extractive proceeds
-> funding hop/key
-> new launch caller/batch
-> launch

If that lineage is visible before or at launch, Alpha Lab can classify the launch regime earlier than ordinary rug scanners that wait for post-launch holder distribution or chart damage.

This is public onchain operator intelligence, not private insider information.

## Prospective hypothesis

Candidate hypothesis:

"Cross-launch operator lineage adds incremental information beyond token-level launch-origin features for predicting extraction risk and the shape/duration of realizable early expansion."

Champion:
existing Alpha Lab + Pons launch-origin + current wallet/deployer features.

Challenger:
Champion + operator-lineage graph.

Primary endpoints:
- severe post-launch drawdown;
- sellability / realizable exit;
- extraction/proceeds convergence;
- time to first coordinated distribution;
- realized 2x/5x/10x under bounded notional and timestamped public eligibility;
- false avoidance of legitimate winners.

Kill if:
- operator links require hindsight;
- infrastructure edges dominate;
- wallet rotation defeats continuity;
- lineage adds no incremental value over simple concentration/bundle metrics;
- apparent large MFE is not realistically sellable;
- false positives materially damage winner recall.

## Next research actions

1. Reproduce Wazz's 53-launch census where possible from exact CAs/events, without importing his final labels as ground truth.
2. Build role-aware graph with explicit infrastructure exclusions.
3. Reproduce at least the DRAFT -> DEED funding-chain example.
4. Test wallet-cohort overlap for LEGS / CRUMBS / PINK / DEED.
5. Freeze historical timing: what would have been known T-60m, T-5m, T0, T+30s, T+2m, T+5m.
6. Measure both avoidance value and realizable upside windows.
7. Keep prospective credit at zero until future rows are frozen before outcomes.

## Framework action

- ADMIT research direction: YES.
- New engine: NO.
- New production threshold: NO.
- Extend recurring-wallet/deployer graph toward operator lineage: YES, SHADOW.
- Add external Wazz ring as historical adversarial dataset: YES.
- Treat scam-linked launches as automatic ENTRY CANDIDATE: NO.
- Study whether known operator behavior creates a repeatable public-onchain execution window: YES, prospectively.
