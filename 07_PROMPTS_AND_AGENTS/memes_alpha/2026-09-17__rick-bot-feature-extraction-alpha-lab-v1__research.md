# Rick Bot Feature Extraction for Alpha Lab v1

Status: RESEARCH / BUILD CANDIDATE
Date: 2026-09-17
Purpose: Extract public product patterns from Rick (@RickBurpBot) that can improve Alpha Lab token audits without copying proprietary code, private data, branding, or bypassing access controls.

## Executive finding

Rick is valuable less because of any single metric and more because it compresses many expensive research branches into one low-latency token card. Alpha Lab should copy the product pattern, not the product: deterministic first-pass triage, clickable drill-down, wallet/deployer provenance, comparable-token/PVP context, and outcome tracking.

Publicly documented Rick capabilities relevant to Alpha Lab include:
- token scans with price/FDV/liquidity/volume/age and holder context
- T10/T20 and top-200 holder statistics
- notable/known holders, whales, KOL/smart-money/insider-style labels
- wallet stats and labels across multiple horizons
- deployer history and prior launches
- bundle/sniper/insider/deployer indicators where supported
- PVP/similar-token matching
- OG/copycat ticker lookup
- top traders
- group first-scan and ATH/outcome statistics
- first-scan FDV, current performance, median gain and 2x/5x hit-rate style group analytics
- community thesis/comments with FDV-at-comment context
- social/lore/community discovery and deleted-post context
- Arc support by contract address

## Screenshot-derived UX pattern

The supplied Arc scan demonstrates an effective compact hierarchy:
TOKEN / CHAIN / VENUE
price
FDV now -> recent peak/time window
liquidity and liquidity multiple
volume + age
short-horizon flow / buy-sell activity
top-holder percentages
holder count + average wallet age
fresh-wallet percentages
PVP/comparable historical matches
CA
one-tap drill-down links
caller/first-scan outcome context

This is valuable because the card exposes both opportunity and failure modes before the analyst opens ten separate tools.

## Alpha Lab extraction: FAST AUDIT CARD

Build/reuse existing owners to produce one deterministic pre-analysis object:

ALPHA_FAST_AUDIT_V1
- ca
- chain
- canonical_pool
- quote_asset
- observed_at
- price
- fdv
- market_cap
- supply_basis
- liquidity_usd
- liquidity_to_fdv
- volume_5m / 1h / 24h
- buys_sells and unique traders where available
- age
- peak_fdv_since_first_seen and elapsed time
- drawdown_from_peak
- holder_count
- top5 / top10 / top20 concentration
- adjusted_free_float_concentration after classifying LP/contracts/protocol/CEX where feasible
- wallet_age_distribution
- fresh_wallet_1d / 7d share
- notable_holder_count
- recurring_alpha_wallet_count
- insider/deployer/linked-funder flags
- deployer prior-launch count and outcomes
- bundle/synchronized-entry suspicion with confidence, never binary truth without evidence
- top-trader accumulation/distribution state
- comparable/PVP tokens and historical outcome summaries
- ticker originality/copycat risk
- social/community velocity and provenance
- data_conflicts[]
- missing_fields[]
- evidence_quality

The object must obey the standing DATA INTEGRITY order. Missing values remain UNKNOWN, never zero or synthetic substitutes.

## High-value Alpha Lab ideas

### 1. Wallet Pattern Compression
Instead of merely listing top holders, summarize economic meaning:
SYSTEM/LP, TEAM/DEV, MIGRATION, CEX, KNOWN/KOL, RECURRING_ALPHA, FRESH, ORDINARY_EOA, UNKNOWN.
Then compute adjusted concentration and whether high-information wallets are accumulating, holding or distributing.

### 2. Deployer Reputation Graph
For deployer and linked funding wallets, preserve previous launches, peak multiples, rugs/dead launches, migration behavior, supply extraction and repeated counterparties. Do not equate correlation with identity.

### 3. PVP / Analog Engine
For a fresh token, retrieve same-chain/same-launchpad analogs using features available at the frozen observation time: age, starting FDV, liquidity/FDV, volume velocity, holder growth, concentration, fresh-wallet mix, narrative/ticker similarity and launch mechanics. Historical outcomes are labels, never inputs from the future.

Output should answer: What happened to genuinely comparable launches after the same age? Avoid survivorship bias by retaining dead launches and failures.

### 4. First-Seen Outcome Ledger
Every CA gets immutable first-seen state. Track 1h, 6h, 24h, 3d, 7d and later horizons as appropriate:
- max FDV/MC
- max drawdown
- liquidity survival
- exitability
- time to 2x/5x/10x
- failure/rug/dead classification where defensible
This directly supports Alpha Lab's anti-hindsight learning mandate.

### 5. Source / Caller Calibration
When a Telegram/X source introduces a token, freeze source, timestamp and baseline. Over time calculate source-specific hit rates and failure rates by chain/regime/market-cap bucket. Never treat popularity as edge by itself.

### 6. One-tap drill-down
Fast card first, expensive research only on demand or when triggers fire:
DATA INTEGRITY -> HOLDER/WALLET -> DEV -> PVP/ANALOG -> SOCIAL/LORE -> TECH -> FULL ALPHA AUDIT.
This is the main latency lesson from Rick.

## Triggered research depth

Escalate automatically when one or more high-information conditions appear:
- unusual adjusted concentration
- recurring alpha wallets before broad social discovery
- linked wallets across multiple successful launches
- rapid liquidity growth without matching holder breadth
- fresh-wallet surge
- deployer with unusually strong or poor history
- distribution by early wallets into rising volume
- PVP analogs with unusually skewed historical outcomes
- material source conflicts

Do not spend full research budget on every CA.

## Proposed compact user output

ALPHA QUICKSCAN
DATA: PASS / CONFLICT / INCOMPLETE
MC/FDV | LIQ | VOL | AGE
HOLDERS: concentration + adjusted concentration
WALLETS: ACCUMULATING / MIXED / DISTRIBUTING / UNKNOWN
DEV: CLEAN / MIXED / RISK / UNKNOWN
ANALOGS: favorable / mixed / adverse / insufficient sample
SOCIAL: organic / concentrated / accelerating / weak / unknown
RISK FLAGS: max 3
MOON SIGNAL: HIGH / MEDIUM / LOW / INSUFFICIENT
ACTION: IGNORE / WATCH / DEEP DIVE / ENTRY CANDIDATE
NEXT INVALIDATION / UPGRADE CONDITION

This is a triage surface, not a replacement for the standing full analysis order.

## Guardrails

- Never scrape or reverse engineer private/proprietary internals when public behavior is sufficient.
- Do not copy Rick branding, proprietary datasets or inaccessible algorithms.
- Reimplement ideas from public documentation and observable outputs using our own data provenance.
- No wallet label is treated as fact without provenance/confidence.
- Bundles, insiders and coordinated-wallet classifications are probabilistic and can false-positive.
- Exact CA/chain/pool verification precedes ticker/social matching.
- Performance claims require timestamped baseline and outcome evidence.
- Dead tokens/failures remain in analog and source-performance datasets.
- No portfolio execution authority is created by this research note.

## Build recommendation

Priority 1: FAST AUDIT CARD + immutable first-seen snapshot.
Priority 2: holder/wallet classification and adjusted concentration.
Priority 3: deployer history + recurring-wallet graph.
Priority 4: PVP/analog outcome engine.
Priority 5: source/caller calibration and compact mobile rendering.

Before adding new services, audit existing Alpha Lab/Moonshot scanner owners and reuse them. This must not create a parallel scanner or forecast engine.

## Success criteria

A useful implementation should reduce time from CA receipt to trustworthy first-pass classification while improving, not weakening, data integrity. Measure:
- median time-to-quickscan
- percent of scans with exact pool verified
- percent with adjusted holder concentration
- wallet/deployer coverage
- false data-conflict resolution rate
- 1h/24h/7d outcome coverage
- calibration of HIGH/MEDIUM/LOW moon signals
- incremental predictive value versus simple MC/liquidity/volume baselines

If the richer system does not outperform the simple baseline out-of-sample, retire or simplify the extra features.
