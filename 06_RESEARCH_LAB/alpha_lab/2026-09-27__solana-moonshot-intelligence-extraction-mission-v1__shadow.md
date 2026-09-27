# Solana Moonshot Intelligence Extraction Mission v1

Date: 2026-09-27  
Owner: existing Meme Alpha / Alpha Lab stack, issue #1087  
Authority: SHADOW_RESEARCH_ONLY  
Scope: learn from mature Solana/Pump.fun tooling and transfer only verified primitives into Robinhood/Pons research.  
Forbidden: parallel scanner, auto-trading authority, retrospective alpha credit, blind score copying, importing third-party private keys/binaries.

## Why this mission exists

Solana/Pump.fun has a longer and denser launch history than Robinhood/Pons. That ecosystem has already paid the cost of learning how to:
- ingest launch events at low latency;
- survive dropped streams and RPC gaps;
- identify graduation/migration state;
- separate real demand from bundles, sniper farms and wash activity;
- reconstruct trader/caller performance;
- track post-graduation survival;
- measure alert latency and execution quality.

The goal is not to reproduce Solana trading. The goal is to extract mature measurement primitives and test them against Pons prospectively.

Chameleon Scope is one benchmark, not the center of the mission.

## Admission rule

A candidate may consume implementation effort only when at least one of these is true:

1. public source code exposes the actual transform/algorithm;
2. public docs specify a deterministic measurement that can be independently reproduced;
3. on-chain/history can validate the claimed behavior;
4. the project publishes a forward ledger or immutable performance evidence;
5. the source supplies a reusable operational primitive, e.g. gap recovery, event parsing or call accounting.

Marketing screenshots alone do not qualify.

Every imported idea receives:
`SOURCE -> CLAIM -> VERIFIED? -> PRIMITIVE -> ROBINHOOD TRANSLATION -> TEST -> KEEP/KILL`.

## Lane A — ingress and completeness

Target:
- sub-block / low-latency event detection;
- deterministic event identity;
- cursor/checkpoint persistence;
- disconnect/gap detection;
- bounded replay/backfill;
- dedupe;
- hot path separated from enrichment.

Priority references:
- `shaurya35/solana-realtime-indexer`
- Chainstack Pump.fun Geyser examples
- QuickNode Yellowstone Pump.fun examples
- Helius Pump AMM gRPC examples
- official/current Pump.fun IDLs, plus `0xfnzero/solana-program-idls`

Primary Robinhood translation:
`Pons factory cursor -> immutable TokenLaunched row -> overlap/backfill -> existing lifecycle`.

This lane is P0 because NYMA proved that superior downstream intelligence is useless if fresh launches are not materialized reliably.

## Lane B — early probability and survival

Target:
- features that become useful before or just after graduation;
- age-conditioned models;
- probability calibration;
- post-graduation sustain probability;
- latency/coverage trade-off.

Priority references:
- `Based-LTD/graduate-oracle`
- Solana memcoin graduation datasets / first-100-block prediction work
- Chameleon post-graduation hold policy

High-value verified ideas from Graduate Oracle:
- age-conditioned feature vectors rather than one universal snapshot;
- calibration, not raw score, as the product;
- forward prediction rows that are timestamped before resolution;
- bot/manipulation flags independent from graduation probability;
- explicit `current_mult` / entry-quality constraint;
- separate post-graduation survival outcome;
- earliness measured as coverage before a price multiplier ceiling.

Do not import its proprietary score or hidden thresholds.

Robinhood tests:
- +0/+5/+10/+20/+30m post-graduation challenger;
- early feature windows before full graduation when Pons data allow;
- executable-return loss versus precision gain at each delay.

## Lane C — manipulation and access topology

Target:
- dev share;
- bundle clusters;
- first buyers/snipers;
- exempt/privileged wallets;
- linked funding sources;
- wallet cycling;
- dust ladders;
- wash/self-flow;
- concentration adjusted for economic entities.

Priority references:
- Chameleon filter inventory;
- Bitquery first-buyer/sniper query patterns;
- GMGN/OKX trench fields;
- Jupiter public token risk fields;
- existing Alpha Lab ASKR/Pons exemption-wallet evidence.

Rule:
an address is not an independent buyer until funding/entity evidence supports independence.

No raw count of "smart wallets", "snipers" or holders may promote alpha by itself.

## Lane D — wallet/caller intelligence

Target:
- point-in-time wallet/caller quality;
- actual cost basis;
- realized vs unrealized PnL;
- first entry versus repeat accumulation;
- lead time versus public propagation;
- hit-rate conditional on entry stage;
- copyability/capacity.

Priority references:
- `gmgnai/gmgn-skills`
- `uerzer/smart-money-tracker` as both idea source and anti-pattern
- Pump.fun callout/leaderboard surfaces
- PumpKit tracker/leaderboard implementation
- Chameleon known-trader UX

Important anti-pattern found:
the open-source `uerzer/smart-money-tracker` assigns a global weighted score from win rate, 7d ROI, volume and recency, and pairs sells to the oldest open position. This is useful as a simple implementation example but is not robust enough for canonical Alpha Lab smart-money authority.

Alpha Lab must preserve:
- economic-entity clustering;
- seeded/dust/service-flow quarantine;
- point-in-time reputation;
- no future-win leakage;
- exact entry/exit reconstruction;
- capacity/slippage.

## Lane E — product/catalyst + token coupling

Solana meme tooling is generally weaker here than Alpha Lab.

Preserve our edge:
- Project -> CA binding;
- first-party source authentication;
- GitHub/repository reality;
- technical product proof;
- catalyst timing;
- `PROJECT_QUALITY != TOKEN_VALUE_CAPTURE`.

Use Solana systems mainly for discovery/microstructure, not as a replacement for project intelligence.

## Lane F — alert accounting and operator UX

Useful Chameleon/PumpKit patterns:
- alert carries frozen signal-time state;
- exact call market cap;
- caller prior record;
- milestone tracking 2x/5x/10x;
- rug/failure update;
- fast Telegram-style delivery.

Alpha Lab keeps richer evidence underneath:
- MFE/MAE;
- executable return;
- slippage;
- liquidity capacity;
- detector/qualification/delivery latency;
- negative denominator.

Simple UX fields are projections, not the scientific ledger.

## Research acceptance protocol

For each proposed primitive:

### 1. Source proof
Freeze repository URL, commit SHA or immutable documentation reference.

### 2. Claim proof
Identify exactly what the source claims.

### 3. Implementation proof
Read the load-bearing code or reproduce the measurement.

### 4. Failure search
Look for:
- leakage;
- survivorship bias;
- retrospective wallet rescoring;
- dropped events;
- hidden denominator;
- raw-address independence assumptions;
- score thresholds without calibration;
- ATH-only outcome claims.

### 5. Robinhood translation
Describe the analogous Pons event/state without pretending chain mechanics are identical.

### 6. Shadow ablation
Test against the existing baseline. No standalone score gets authority.

### 7. Keep/kill
Promote only if prospective evidence adds incremental economic value after latency and execution costs.

## First-wave extraction priorities

### P0 — copy architecture, not score
**shaurya35/solana-realtime-indexer**
- unified live/replay/backfill decode path;
- checkpoint committed atomically with data;
- gap monitor;
- targeted recovery;
- independent verify;
- dead-letter capture;
- raw integer precision.
Translation: directly relevant to current Pons ingress remediation.

### P0 — test methodology
**Based-LTD/graduate-oracle**
- age-conditioned graduation modelling;
- forward immutable predictions;
- calibration;
- manipulation flags separated from probability;
- entry multiplier / earliness validation;
- post-grad sustain research.
Translation: bounded challengers to G2/G3, never model-score import.

### P1 — event/alert plumbing
**nirholas/pumpkit**
- modular launch/graduation/whale/claim monitors;
- event-streaming skills;
- Telegram delivery;
- call tracker / ATH tracker.
Translation: UX and event lifecycle patterns.

### P1 — external challenger workflows
**gmgnai/gmgn-skills**
- structured token risk;
- holder/trader tables;
- smart-money profile;
- risk-warning workflow;
- dev-created-token history.
Translation: feature inventory and external benchmark only. GMGN labels are not ground truth.

### P1 — parser/IDL robustness
**0xfnzero/solana-program-idls + official provider examples**
- versioned launchpad/DEX instruction definitions;
- deterministic parser generation;
- protocol coverage tracking.
Translation: maintain explicit source-contract/event schemas for Pons/future chains.

### P2 — anti-pattern / minimal wallet engine
**uerzer/smart-money-tracker**
- simple PnL ledger and alert plumbing;
- useful for identifying where naive global wallet scores fail.
Translation: regression/anti-pattern tests, not canonical score.

### P2 — basic low-latency monitor
**Kernlog/pump-sniper / Hashdevlol/pumpfun-sniper**
- fast detection and feature inventories.
Translation: compare operational simplicity, do not import arbitrary weighted scores or auto-buy logic.

### P2 — contract/security skill
**trailofbits/skills token-integration-analyzer**
- systematic contract privilege/weird-token review.
Translation: valuable for EVM Project->CA / MansaFi-style technical audit, not moonshot prediction.

## Explicit non-goals

- no copy trading;
- no private-key integration;
- no auto-buy;
- no global "smart wallet score";
- no fixed Solana thresholds transplanted to Pons;
- no paid external API adoption without measured incremental value;
- no feature count as success metric.

## Completion definition

This mission is not complete when many repos have been read.

It is complete when:
1. at least 15 credible external primitives have been adjudicated;
2. the top 3-7 are translated into bounded Robinhood shadow tests;
3. at least one natural prospective Pons cohort produces comparative results;
4. weak ideas are explicitly killed;
5. the resulting production proposal is smaller than the research set.

