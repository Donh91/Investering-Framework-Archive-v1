# RHX402 launch pre-outcome audit v1

Date: 2026-09-27
Observed window: approximately T+20m to T+30m after declared 2026-09-27T14:00:00Z launch
Status: MANUAL INTAKE / PRE-OUTCOME SNAPSHOT / DEEP-DIVE CANDIDATE
Owner: #1087 / Meme Alpha Supervisor
Prospective autonomous discovery credit: 0
Trade authority: NONE

## User-supplied launch evidence

User supplied contemporaneous X screenshots from @rhx402agent showing:
- "$RHX402 is live on pons";
- exact CA: 0xc1069E44531183913006ff0d9A1803f1af717B6A;
- project site: rhx402.xyz;
- public code link: github.com/rhx402/rhx402;
- framing: "x402 for AI agents on Robinhood Chain. The rail was live before the token, and now it is open source."

The screenshot shows the post approximately 22 minutes old at ~16:23 CEST.

## Canonical repository freshness check

Fresh search of Donh91/Investering-Framework-Archive-v1 before this intake:
- exact CA: no prior match;
- RHX402: no prior match.

This is therefore a new manual Alpha Lab case.

## First-party project/code evidence

Public repository:
https://github.com/rhx402/rhx402

Repository metadata at intake:
- created: 2026-09-25T07:40:43Z;
- public TypeScript repository;
- MIT license;
- two visible commits at intake;
- initial implementation commit dated 2026-09-25;
- launch-day CA/config commit dated 2026-09-27T14:21:09Z;
- no GitHub Actions workflow present in the current tree;
- 0 stars / 0 forks at this very early observation.

README states:
- the payment rail settles USDG on Robinhood Chain chain id 4663;
- first x402 payment allegedly settled on 2026-09-25;
- RHX402 token launched on Pons on 2026-09-27;
- the token is explicitly NOT required for payments/settlement or software use.

The exact CA is embedded in the launch-day repository config and Pons launch link.

## Code-quality / product observations

The repository is materially more than a landing page.

Visible implementation includes:
- buyer rail;
- spend-policy engine;
- SQLite ledger and signed receipts;
- seller middleware;
- USDG facilitator;
- MCP server / CLI;
- paid API;
- unit tests for facilitator guard, spend policy and receipts;
- a full local-fork E2E script using Robinhood Chain mainnet state.

Security-minded implementation details visible in source include:
- fail-closed policy checks;
- exact network/asset/scheme checks;
- signed seller registration;
- per-payment / per-seller / daily caps;
- gas-reserve guard;
- wallet keys outside model context;
- EIP-3009 gasless buyer authorization;
- offline signed-receipt verification.

The code therefore supports a real technical/product thesis rather than pure token marketing.

## Important provenance / novelty correction

The README explicitly says the architecture is taken from CRA AGENT / giupy997/arcagentx402 (MIT) and rebuilt for Robinhood Chain.

Therefore:
- "working product" is stronger than vaporware;
- "novel protocol invented from scratch" is NOT supported;
- value lies in Robinhood-specific integration, USDG/facilitator/MCP implementation and execution, not originality of the base x402 architecture.

The upstream CRA repository itself is also extremely young (created 2026-09-14 at intake).

## Critical token-value-capture separation

The strongest current caveat is explicit in the project's own README:

> payments and settlement are in USDG, and no part of this software requires holding RHX402.

Therefore PROJECT QUALITY and TOKEN ECONOMIC QUALITY must be separated.

At this observation:
- PRODUCT_SIGNAL: MATERIAL / technically coherent;
- TOKEN_UTILITY: NONE_VERIFIED;
- TOKEN_VALUE_CAPTURE: NONE_VERIFIED;
- token demand can currently be narrative/speculative even if the rail is legitimate.

Do not infer token value capture from product usage.

## Narrative / catalyst quality

The launch has a coherent Robinhood-native narrative stack:
- AI agents;
- x402 agent payments;
- MCP;
- USDG;
- Robinhood Chain;
- working/open-source code;
- Pons launch.

This is materially better narrative-product coherence than a generic AI ticker.

However, narrative coherence does not solve token-value capture or launch-distribution risk.

## Data gaps at intake

The bounded interactive pass could not independently freeze current market/pool metrics or decoded Pons launch-origin fields.

Keep UNKNOWN:
- canonical pool;
- live MC/FDV;
- liquidity;
- volume / unique buyers-sellers;
- sellability / bounded-notional slippage;
- launch caller / recipient;
- initial launcher buy percentage;
- snipe-tax exemption count;
- exemption wallet behavior;
- top-holder adjusted concentration;
- operator-lineage match;
- creator fee / proceeds path;
- first coordinated distribution timing;
- execution-toxicity state.

These must not be inferred from the project repository.

## Preliminary Alpha Lab classification

DATA INTEGRITY: PARTIAL
EXACT_CA: FIRST-PARTY-CORROBORATED, onchain launch-origin enrichment pending
PROJECT / PRODUCT SIGNAL: STRONGER_THAN_TYPICAL_FRESH_PONS
CODE EVIDENCE: MATERIAL
NOVELTY: MODERATE; base architecture adapted from MIT upstream
TOKEN UTILITY / VALUE CAPTURE: WEAK / NONE VERIFIED
NARRATIVE COHERENCE: HIGH
OPERATOR / EXTRACTION RISK: UNKNOWN
REALIZABLE ADVERSARIAL ALPHA: UNKNOWN
EXECUTION TOXICITY: UNKNOWN

Current state:
DEEP_DIVE / WATCH, not automatic ENTRY CANDIDATE.

## Upgrade conditions

Upgrade research conviction if:
- exact Pons launch origin is clean relative to matched denominator;
- adjusted privileged/linked supply is low or non-distributing;
- independent buyer breadth expands;
- liquidity survives and bounded exits are feasible;
- product payment usage continues after launch;
- seller/API adoption appears beyond self-generated demo traffic;
- operator-lineage scan finds no material extractive continuity;
- token gains a credible value-capture mechanism without degrading the product.

## Downgrade / reject conditions

Downgrade sharply if:
- launch-origin shows large coordinated bundle/exemption concentration with early sell-through;
- proceeds/funding connect to known extraction operator;
- liquidity or sellability deteriorates;
- public demand is mostly linked wallets;
- payment rail activity is only self-test/demo activity;
- token marketing implies utility not present in code;
- execution toxicity materially impairs entry/exit.

## Research value

This is a particularly useful Alpha Lab case because it tests a common failure mode:

REAL PRODUCT != GOOD TOKEN.

It should be retained even if the token later fails, because the product-before-token and explicit zero-token-dependency facts were knowable at launch.
