# OSINKO Alpha Lab audit - historical visibility miss + live watch v1

Date: 2026-09-24
Status: HISTORICAL_RECONSTRUCTION + LIVE_WATCH
Authority: Alpha Lab research only
Trading authority: NONE
Prospective credit for pre-2026-09-24 outcome: 0

## Identity

Project: Osinko
Token: OSINKO
Chain: Robinhood Chain
Exact CA: `0x8cd57b19033a90b753d73dbc122367a4a52b8586`

Current first-party Project→CA binding: HIGH.
Basis: osinko.app publishes the exact CA in the product/site footer and identifies it as $OSINKO.

Pons launch origin: PENDING deterministic reconstruction.
Reason: the exact CA currently has Pons V2 market surfaces, but current pool age is not token age and must not be substituted for the original launch event.

## First-party publication evidence supplied during audit

User supplied a screenshot of the verified @UseOsinko X account showing:
- post text: "$OSINKO is live."
- exact CA above;
- displayed timestamp: 20:46 on 2026-09-08.

Treat this as point-in-time first-party CA-publication evidence, but the screenshot itself is not persisted in this repository. Exact X-post URL / immutable external capture remains to be bound if obtainable.

This establishes at minimum that the project publicly bound itself to this CA by 2026-09-08. It does NOT by itself establish the onchain token creation time, Pons factory generation or launch transaction.

## Product surface observed 2026-09-24

The current first-party Osinko site describes and exposes an interactive Robinhood Chain product around tokenized stocks and dividends. Publicly observable functions include:
- deposit stock tokens;
- early dividend payout using a USDG pool;
- per-second dividend streaming;
- dividend reinvestment;
- borrowing against deposited stock;
- splitting a stock into share/principal and dividend/yield-like tokens;
- an AI-agent/MCP interaction surface where actions return unsigned calldata and require wallet signing;
- Chainlink-based stock pricing with a stated stale-price fail-close rule.

This is materially different from ticker-only/meme-only packaging. The correct Alpha Lab representation is PROJECT_FIRST_PRODUCT_SURFACE, not generic narrative quality.

First-party site:
https://www.osinko.app/

## Product/adoption claims requiring independent reproduction

First-party/social surfaces have claimed:
- a live TVL/dividend tracker;
- first end-to-end user payouts on mainnet;
- current stock deposits / USDG dividend backing;
- collateral/borrow parameters and dividend-backed loan mechanics.

These remain CLAIMS until independently reproduced from exact contracts / transactions. Do not convert product copy, demo values or social posts into TVL/adoption truth.

Important distinction:
the site's large sample portfolio/demo is not protocol TVL.

## Market snapshot during audit

GeckoTerminal exact-CA market surfaces on 2026-09-24 showed multiple pools for the same token.

A current Uniswap V3 Robinhood pool snapshot showed approximately:
- price: $0.0001441;
- market cap: ~$144k;
- FDV: ~$148k;
- liquidity: ~$23.4k;
- holders: 399;
- 24h volume: ~$42k;
- 24h transactions: 409;
- contract marked verified on that market surface, no honeypot indicated, no proxy found.

Another same-CA Pons V2 surface exists and has materially different pool age/market observations. Therefore:
- token age MUST NOT be inferred from any one pool age;
- market cap/liquidity must be pool/timestamp sourced;
- total executable liquidity and canonical launch lineage remain to be reconstructed.

Market source:
https://www.geckoterminal.com/robinhood/pools/0x2ba20864c16fa5f83c3af6d9ea0a6cdb09b3af9a

## Framework audit result

Fresh code/archive search on 2026-09-24 found no exact-CA or OSINKO/Osinko record in:
- Donh91/Investering-Framework-Archive-v1
- Donh91/secrets

Classification:
- FRAMEWORK_VISIBILITY_MISS: CONFIRMED for the public project/token before this manual intake.
- T0_QUALIFICATION_MISS: UNKNOWN until historical point-in-time reconstruction.
- ECONOMIC_ALPHA_MISS: UNPROVEN.
- PROJECT_TO_CA_CURRENT_BINDING: HIGH.
- PONS_ORIGIN: PENDING.
- SELLABILITY/LIQUIDITY: PRESENT ON CURRENT DEX SURFACES, historical state pending.
- PROSPECTIVE_CREDIT_BEFORE_INTAKE: 0.

This is a false-negative / visibility-gap case for Alpha Lab research, not a retroactive winner.

## Why this case is high-value for Alpha Lab

OSINKO tests a feature family the current Project→CA/prelaunch lane explicitly cares about:

1. project/product surface appears substantive relative to Pons noise;
2. exact first-party CA binding exists;
3. the project is actively shipping product features after launch;
4. the token remained small enough for a long observation window;
5. current product narrative maps tightly to Robinhood Chain's tokenized-stock primitive;
6. social footprint is still relatively small, making propagation timing measurable;
7. the case can test whether "builder persistence + functioning product + chain-native primitive" adds information beyond launch traction alone.

The learning target is NOT "working product = buy".
The learning target is whether a bounded, reproducible combination of pre/post-launch project evidence predicts qualification, survival, liquidity quality or later repricing better than matched Pons controls.

## Critical risks / unresolved items

- Original token creation tx/block/time not yet reproduced.
- Exact Pons factory/version/origin not yet reproduced.
- Creator/deployer and initial allocation/access-fairness not yet reconstructed.
- Holder concentration beyond pool addresses not yet reproduced.
- Product smart-contract addresses/code/audit status not independently mapped here.
- No independent security audit of Osinko protocol contracts has been established in this packet.
- First-party adoption/TVL/payout claims need chain reproduction.
- Multiple pools make naive age/liquidity/price interpretation unsafe.
- Social/caller exposure can contaminate later price action; propagation timestamps must be frozen.
- Current market outcome is already partially known, so all historical learning is E1 representation only.

## Required reconstruction

Reconstruct point-in-time state at:
- pre-CA / earliest project visibility;
- first authenticated CA publication;
- token launch T0;
- ~$25k MC if observable;
- ~$50k MC;
- ~$100k MC;
- ~$250k MC;
- current observation.

At each checkpoint preserve only then-observable evidence:
- project/product surface;
- source age/health;
- exact CA binding;
- launch tx/factory;
- creator/deployer;
- initial buy / privileged access / exemptions;
- supply and MC-vs-FDV;
- liquidity and sellability;
- buyer breadth/concentration;
- transfer-vs-buy provenance;
- product contracts and real usage;
- social/caller propagation;
- wallet convergence;
- material product/catalyst updates.

Unreproducible checkpoint = UNKNOWN. No interpolation.

## Matched-control requirement

Compare OSINKO against failed/ordinary Pons projects with similar:
- age;
- initial market cap;
- tokenized-stock/RWA/DeFi narrative;
- apparent product polish;
- social size;
- liquidity;
- launch regime.

Specifically test whether these survive matched controls:
- product existed before token;
- functioning interactive app;
- active post-launch shipping;
- exact first-party CA continuity;
- onchain usage rather than demo content;
- chain-native stock/dividend primitive;
- low social footprint before later market attention.

## Live-watch role from 2026-09-24 forward

From this intake onward the exact CA may generate genuine prospective observations.

Freeze future material changes before outcome:
- verified protocol TVL/user growth;
- new product modules;
- independently verified onchain usage;
- liquidity/sellability changes;
- holder/buyer breadth;
- meaningful wallet/caller convergence;
- broad social propagation;
- exact market-cap milestones;
- drawdown / survival.

Historical outcome before this intake receives zero prospective credit.

## Current verdict

ALPHA_LAB_RELEVANCE: HIGH
CASE_ROLE: CONFIRMED_VISIBILITY_MISS + HISTORICAL_RECONSTRUCTION + LIVE_FORWARD_WATCH
MOONSHOT_QUALITY: NOT YET PROVEN
CURRENT_ACTION: DEEP_DIVE_WATCH
EDGE_STATUS: UNPROVEN

The important question is whether Alpha Lab should have discovered and qualified Osinko materially earlier from project-first evidence, not whether OSINKO later goes up.
