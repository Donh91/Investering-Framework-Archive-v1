# Wazz Wallet Intel + Atarashi Robinhood MEV — Expanded Audit v1

Date: 2026-09-27
Status: SHADOW RESEARCH / ARCHITECTURE INPUT
Owner: #1087 / Meme Alpha Supervisor
Portfolio/trading authority: NONE
Parallel scanner: FORBIDDEN

## Why this audit exists

This packet expands the earlier Wazz serial-extraction/operator-lineage audit with two additional public research threads:

1. WazzCrypto — automated onchain alerting/trading tool using wallet-label DB, holder profiling, accumulation/reduction state, security scans and social confirmation.
2. Atarashi + Outputlayer — Robinhood Chain sandwich / protected-order-flow observations, rotating attacker keys, receiving contracts and router surfaces.

The purpose is not to copy external tools or accept social claims as truth.
The purpose is to identify architecture primitives that can be independently reproduced and prospectively tested inside the existing Alpha Lab owners.

## Source-derived findings

### Wazz wallet-intelligence thread

Public thread:
- https://x.com/WazzCrypto/status/2103553062866768036
- related wallet DB thread: https://x.com/WazzCrypto/status/2102098428234801596
- earlier rug-wallet investigation post: https://x.com/WazzCrypto/status/2093073884941582383

Wazz describes:
- an onchain intel / wallet-label database;
- automated alerting/trading experiments on top of that DB;
- full holder profiling for identified wallets;
- accumulation vs reduction state;
- social/influence metadata;
- high-PnL wallet filtering;
- security scans aggregated from multiple providers;
- labels created from prior rug investigations by tracing fund flows and linked profiles.

Framework interpretation:
The valuable primitive is persistent entity memory across tokens.
A token scan should query what is already known about economic actors, not rebuild wallet context from scratch each time.

Do not copy:
- opaque wallet quality scores;
- retrospective high-PnL labels without point-in-time history;
- social influence as a positive alpha primitive;
- provider security verdicts as ground truth.

### Atarashi / Outputlayer thread

Public thread:
- https://x.com/atarashi/status/2103913524757983682
- operator-key detail: https://x.com/outputlayer/status/2103923311310991726
- related orderflow comment: https://x.com/sw0rdmann/status/2103937873741557823

Atarashi alleges that a subset of Robinhood Chain sandwich bots repeatedly sandwich Relay-origin victims and hypothesizes that at least one Relay solver may be leaking private intent data.

This is an allegation / research hypothesis, not established fact.

Atarashi listed five addresses for a six-day search period:
- 0x44c0ba0b734d4b7705fcd07ddae9fbbc078d74dd
- 0x38b3f8125bbbd45b56d0c3a535b90181d7dd3880
- 0x2a23c6d2522f07d230abf9c7a96d703520fd222b
- 0x18e0efe5be1cbb4e060c26f7f16f276be4dbc38c
- 0x9d61ad5c82586ae118af38e1cc68c8d1ad50771a

Outputlayer further described three operator clusters and explicitly noted key rotation, including one cluster using the Robinhood Uniswap Universal Router.

## Independent verification performed

### Operator 1 receiving contract

External claim:
receiving contract
0x68a04a63fd1d8eabf167ef48ed0a0ef06c2374d9

Blockscout Robinhood Chain (4663) independently confirms:
- address is a contract;
- first transaction / creation timestamp: 2026-09-24T08:58:45Z;
- creation tx: 0xc5b962b721f903b5271b7f4bd33f2fd88d56350e2b0a275b8e46b2ad817bbab7;
- creator address:
  0x44c0Ba0b734d4b7705fCd07DDAe9fbBc078D74Dd

This directly reproduces one important graph edge from the external thread:
one of the listed Operator-1 keys created the listed receiving contract.

It does NOT independently prove the sandwich classification or Relay leakage allegation.

### Operator 3 contract

External claim:
0x2da9222a2b26dac27213cb8d27e92ae6c580a463

Blockscout confirms:
- contract exists on Robinhood Chain;
- first transaction timestamp: 2026-09-11T07:53:46Z;
- unverified contract at observation time;
- creator:
  0xc35b2C29c209CaB9adE3BF3C0812ccE4eB11C0B8

The claimed association with
0x18e0efe5be1cbb4e060c26f7f16f276be4dbc38c
was not independently reproduced in this bounded pass.

### Universal Router false-positive protection

Outputlayer names:
0x8876789976decbfcbbbe364623c63652db8c0904

Official Uniswap deployment data identifies this as Robinhood Chain's Universal Router.

Therefore:
- the router address is shared protocol infrastructure;
- touching the router is NOT operator identity;
- only the rotating sender/key behavior around it can be candidate operator evidence.

This is directly analogous to the Pons factory false-positive problem already found in the Wazz launch-ring audit.

## External research context

A September 2026 paper, "No Place to Hide: An Analysis on Protected Order Flow Sandwich Attacks", studies protected-order-flow sandwich attacks across six other chains.

Relevant architecture learning:
- protected/private order flow can still be exposed;
- attack legs can be wide or cross-block rather than tight;
- persistent attacker clustering is necessary to separate attacks from ordinary high-frequency two-way trading;
- exposure can occur at several layers, including OFAs, applications, RPCs and validators.

The paper does NOT study Robinhood Chain and therefore does not verify Atarashi's specific claim.
It only establishes that protected-order-flow exposure is a plausible class of failure that deserves measurement rather than dismissal.

## Architecture consequence

Alpha Lab needs three independent axes.

### Axis A — OPERATOR / EXTRACTION RISK

Question:
Is this launch economically connected to a previously extractive or coordinated operator cluster?

Examples:
- proceeds fund next launch key;
- same non-infrastructure signer;
- same collector;
- repeated privileged-wallet cohort;
- relaunch family with linked economic control;
- concentrated bundled supply;
- creator-fee/proceeds convergence.

Output must never be inferred from same launchpad/factory/router alone.

### Axis B — REALIZABLE ADVERSARIAL ALPHA

Question:
Even if extraction risk is high, is there a measurable public, sellable expansion window before coordinated distribution dominates?

Required separation:
high extraction risk != zero MFE
and
high MFE != realizable alpha.

Measure:
- first public-eligible timestamp;
- independent buyer breadth excluding linked operator entities;
- de-manipulated net demand;
- liquidity and bounded-notional exit capacity;
- operator inventory / sell-through;
- time to first coordinated distribution;
- realizable MFE after slippage;
- MAE;
- time to 2x/5x/10x when sellable;
- window closure condition.

No ATH-only credit.

### Axis C — EXECUTION TOXICITY / MEV

Question:
Can the candidate be entered/exited without abnormal adverse execution risk from sandwich / orderflow exposure?

Candidate evidence:
- persistent known attacker entity near target pool;
- sandwich-density around the same execution route;
- route/provider association where reproducible;
- active rotating key cluster;
- abnormal execution shortfall;
- victim-pattern correlation;
- route-specific degradation.

This axis can only reduce execution confidence or close a research alpha window.
It may not create a positive alpha signal.

## Persistent wallet/entity memory

Wazz's strongest architecture lesson is stateful memory.

Existing Alpha Lab wallet/cabal research should evolve toward a persistent economic-entity graph where labels are versioned evidence, not permanent truth.

Node examples:
- EOA;
- contract;
- token;
- pool;
- launch instance;
- project;
- operator cluster;
- collector;
- router / protocol infrastructure;
- external social identity.

Role examples:
- LAUNCH_CALLER
- FUNDING_KEY
- BUNDLE_SIGNER
- SNIPE_EXEMPT
- EARLY_BUYER
- DISTRIBUTOR
- COLLECTOR
- CREATOR_FEE_RECIPIENT
- HIGH_PNL_CANDIDATE
- MEV_ATTACKER_CANDIDATE
- INFRASTRUCTURE

Every role/edge requires:
- observed_at;
- first_seen;
- source;
- evidence ref;
- confidence state;
- point-in-time validity;
- supersession / expiry;
- infrastructure flag.

No wallet label may retroactively improve an earlier signal.

## Rotating-key lesson

Atarashi/Outputlayer materially strengthens a design requirement:
address watchlists alone are insufficient.

An operator can rotate keys every hours while preserving:
- recipient contracts;
- routers;
- selectors;
- funding ancestry;
- timing pattern;
- destination collectors;
- behavioral structure.

Therefore the model must support:
ADDRESS -> ENTITY_CLUSTER

without claiming real-world identity.

## Guardrails

- "insider" is descriptive shorthand only when evidence is stated.
- Public onchain intelligence is not private insider information.
- No use of MEV observations to front-run or sandwich third parties.
- MEV research is defensive execution-risk measurement.
- External labels are leads until independently reproduced.
- Same factory/router/bridge is never operator identity by itself.
- UNKNOWN != 0.
- No automatic trading authority.
- No parallel scanner.
- No production thresholds from this audit.

## Final decision

ADMIT_WAZZ_WALLET_MEMORY_PATTERN = YES
ADMIT_OPERATOR_LINEAGE = YES_SHADOW
ADMIT_DUAL_RISK_ALPHA_AXES = YES_SHADOW
ADMIT_EXECUTION_TOXICITY_AXIS = YES_SHADOW
ADMIT_ATARASHI_KEYS_AS_EXTERNAL_RESEARCH_SEEDS = YES_POINT_IN_TIME_ONLY
CLAIM_RELAY_SOLVER_LEAK = UNVERIFIED_HYPOTHESIS
AUTOMATIC_EXECUTION = NO
