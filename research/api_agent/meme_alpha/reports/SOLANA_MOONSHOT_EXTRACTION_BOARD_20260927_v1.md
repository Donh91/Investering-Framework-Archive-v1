# Solana Moonshot Extraction Board — Wave 1

Date: 2026-09-27  
Owner: #1087  
Mode: SHADOW / RESEARCH ONLY

Scoring here is **research priority**, not token/investment scoring.

| Priority | Source | Verified useful surface | Main risk / caveat | Robinhood/Pons extraction | Decision |
|---|---|---|---|---|---|
| P0 | shaurya35/solana-realtime-indexer | Yellowstone live stream, deep-CPI trade decode, atomic checkpoint+write, gap detection, RPC recovery, replay, independent verification, dead-letter queue, published soak evidence | Solana-specific event transport | Persistent cursor, overlap/backfill, same decode path for live/replay/recovery, independent completeness verifier | EXTRACT NOW |
| P0 | Based-LTD/graduate-oracle | 60k+ curve methodology, age-conditioned features, kNN/GBM calibration, forward prediction ledger, bot flags, earliness validation, post-grad sustain research | core scoring engine closed; project claims need independent performance verification | age-conditioned Pons challenger, calibration, entry-quality ceiling, forward immutable prediction rows | EXTRACT METHODOLOGY |
| P0 | Chameleon Scope | live Pump.fun + Pons terminal claims, hard scam filters, ~20m post-grad survival gate, wallet/caller overlay, 2x/5x/10x tracking | opaque thresholds; no public immutable call ledger found; no public engine repo found | graduation survival ablation, frozen caller snapshot, latency tuple, simple milestone UX | ACTIVE SHADOW CHALLENGER |
| P1 | nirholas/pumpkit | open modular monitors for launches, graduations, whales, fee claims; tracker bot; ATH tracker; event-streaming/indexing skills | bot framework, not demonstrated predictive alpha | lifecycle/event plumbing, callout accounting, health/reconnect patterns | EXTRACT SELECTIVELY |
| P1 | gmgnai/gmgn-skills | open skill workflows for token security, holders/traders, dev history, smart-money profile, risk warnings | upstream GMGN tags/scores are opaque and may contain survivorship/entity errors | workflow/checklist primitives and external challenger features only | EXTRACT WORKFLOWS, NOT SCORES |
| P1 | Chainstack Pump.fun Geyser examples | deterministic Create event listener, migration listeners, explicit production warning about WebSocket loss | provider example, not alpha model | compare ingress transport patterns and event identity | EXTRACT INGESTION PATTERN |
| P1 | QuickNode Yellowstone Pump.fun example | low-latency mint detection with exact mint/slot/signature | provider dependency | minimal detector fixture + latency benchmark pattern | EXTRACT FIXTURE |
| P1 | Helius Pump AMM gRPC docs | live Pump AMM stream examples | provider dependency | stream schema comparison / failover source | BENCHMARK |
| P1 | 0xfnzero/solana-program-idls | versioned PumpFun/PumpSwap/Raydium/Meteora/Orca IDL catalog, MIT | Solana-only | schema/version-drift discipline for launch adapters | EXTRACT GOVERNANCE PATTERN |
| P1 | Bitquery Pump.fun/PumpSwap docs | first-buyer/sniper queries, migration state, historical/realtime datasets, ATH/volume query patterns | paid/API source, query semantics differ by dataset | independent historical challenger, sniper/funder reconstruction ideas | BENCHMARK / OPTIONAL DATA |
| P1 | Pump.fun leaderboard/callout surfaces | current caller/trader performance and callout-reward ecosystem | opaque internal ranking, survivorship/crowding risk | external label challenger, point-in-time caller history | OBSERVE / DO NOT TRUST |
| P2 | uerzer/smart-money-tracker | open trade ledger, wallet PnL, alert queue, leaderboard | naive FIFO-style position handling; global weighted score uses win rate/ROI/volume/recency; no entity clustering | use as anti-pattern and simple alert/accounting reference | DO NOT IMPORT SCORE |
| P2 | Hashdevlol/pumpfun-sniper | feature inventory: creator history, liquidity, holders, socials | arbitrary fixed weights, minimal public validation, tiny repo | feature inventory only | LOW PRIORITY |
| P2 | Kernlog/pump-sniper | Rust + Yellowstone launch monitor, market-cap threshold, reconnect/test mode | trading/sniping logic not relevant; old/simple | operational latency comparison only | LOW PRIORITY |
| P2 | x402agent/solana-clawd Pump.fun skills | explicit Pump/PumpSwap program operations and graduation state | execution skill, not research edge | command/skill ergonomics only | LOW PRIORITY |
| P1 | Trail of Bits token-integration-analyzer skill | systematic owner/upgrade/mint/pause/blocklist/weird-token review | EVM/security oriented, not launch prediction | strengthen Project->CA technical risk audit for Robinhood tokens | EXTRACT INTO SOURCE-AUTH REVIEW |
| P2 | Solana memcoin graduation ML/Kaggle ecosystem | first-100-block graduation prediction framing and public datasets | variable repo quality / possible leakage; old regime | independent feature discovery and negative denominator source | DATASET REVIEW |
| P2 | OKX/Helius trench skill patterns | smart-money, dev reputation, bundle/trench/risk-tag surfaces | service/label opacity | challenger fields and UX, never canonical labels | BENCHMARK |

## Highest-value primitive extractions

### E1 — Completeness before intelligence
Source: `shaurya35/solana-realtime-indexer`

Extract:
- one core decode pipeline for live + replay + backfill;
- stream checkpoint committed atomically with event rows;
- gap detector independent of parser;
- recovery reuses the same parser;
- independent range verification;
- unresolved payload/dead-letter preservation.

Why it matters:
NYMA showed Pons is currently losing value before the intelligence layer. This is the strongest immediate external lesson.

### E2 — Age-conditioned probability
Source: `Based-LTD/graduate-oracle`

Verified published feature frame at age T:
- current virtual liquidity/state;
- liquidity growth;
- log trade count;
- log unique buyers;
- largest-buyer share;
- current price multiplier.

Useful extension fields published independently of score:
- top1/top3 buyer share;
- repeat-buyer rate;
- dust-buy rate;
- unknown/low-history buyer fraction;
- sniper fraction;
- top-buyer history quality;
- sell ratio;
- buys per buyer;
- sybil/fresh-wallet/cycling flags.

Translation:
do not score a Pons launch with one universal state vector. Freeze comparable feature snapshots by age/stage.

### E3 — Earliness is its own objective
Graduate Oracle publicly measures whether signals fire before a multiplier ceiling, not just whether classification is correct.

Translation:
Alpha Lab must score:
- detection accuracy;
- classification accuracy;
- **economic earliness**.

Candidate metric:
`qualified_before_1.5x / 2x / 3x`, with actual executable entry rather than first observed price.

### E4 — Risk and opportunity are separate models
Chameleon + Graduate Oracle both separate manipulation/suspect filters from opportunity/probability.

Translation:
keep:
`INTEGRITY_PASS != ALPHA_PASS`.

MansaFi is the complementary example: safe/normal token code does not establish project legitimacy.

### E5 — Post-graduation survival
Source: Chameleon, Graduate Oracle research, existing Alpha Lab Phoenix/First Distribution work.

Translation:
test 0/5/10/20/30m survival rather than importing a 20m rule.

### E6 — Immutable forward ledger
Source: Graduate Oracle.

Every prediction row must exist before outcome resolution.

Translation:
extend current prospective evidence rather than reconstructing signal state from today's wallet score or final market history.

### E7 — Alert/caller state frozen at signal
Source: Chameleon UX, PumpKit tracker, Alpha Lab governance.

Store:
- prior resolved calls;
- prior 2x/5x rates;
- prior rug rate;
- realized PnL where reconstructable;
- entity identity;
- signal/delivery/executable timestamps.

Never use future wins to improve an old caller.

### E8 — Simple milestones over rich ledger
Source: Chameleon.

Expose 2x/5x/10x for human readability, but preserve MFE/MAE/slippage/capacity underneath.

### E9 — Deep-CPI / settled-event preference
Source: Solana realtime indexer.

It intentionally trusts settled inner event evidence rather than requested outer instruction parameters.

Robinhood translation:
prefer emitted/settled contract event state and actual transfers over transaction intent when classifying launch/trade outcomes.

### E10 — Parser versioning as research integrity
Source: 0xfnzero IDL catalog / provider examples.

Freeze:
- contract/program version;
- event signature/IDL;
- first block valid;
- parser version;
- fixture.

Do not silently reuse an old launch parser after venue contract changes.

### E11 — Wallet-score anti-pattern
Source: uerzer/smart-money-tracker.

Useful because it demonstrates how easy it is to build a plausible but weak score:
`40% win rate + 30% 7d ROI + 15% volume + 15% recency`.

Problems:
- no economic-entity clustering;
- no seeded/dust/service-flow filtering;
- no point-in-time freeze;
- simplistic position matching;
- no copyability/latency/capacity;
- likely survivorship selection.

Use this as a regression example of what Alpha Lab must NOT become.

### E12 — Skill/workflow extraction
Source: `gmgnai/gmgn-skills`, `nirholas/pumpkit/.claude/skills`, Trail of Bits skills.

High-value skill patterns:
- explicit staged workflow rather than one-shot score;
- hard stop before deeper analysis;
- dedicated wallet-profile workflow;
- dedicated active-risk workflow;
- event-streaming and indexing operational skills;
- contract privilege/weird-token checklist.

Translation:
improve existing `meme-alpha-supervisor` behavior, not install overlapping trading skills.

## Wave-1 kills / non-imports

- auto-buy/snipe execution;
- fixed market-cap buy threshold;
- arbitrary feature weights;
- raw follower/social count;
- `smart_wallets >= N` as promotion rule;
- global caller leaderboard without timestamped historical state;
- ATH screenshot as performance proof;
- wallet PnL without cost-basis reconstruction;
- a single-chain graduation threshold transplanted to Pons;
- downloaded binaries/private-key bot kits.

## Next verification queue

1. inspect `solana-realtime-indexer` gap/recover/checkpoint code and translate exact invariants into #1017 Pons ingress acceptance;
2. inspect Graduate Oracle public forward snapshots/research failures for leakage and survivorship controls;
3. inspect PumpKit GraduationMonitor + tracker ATH/call accounting code;
4. inspect GMGN skill's exact security/wallet fields and identify fields already available through our sources;
5. search for open-source bundle/Jito/funder-cluster implementations with reproducible code, not marketing;
6. search for public caller ledgers that preserve deleted/failed calls;
7. test historical Solana graduation datasets for features whose definitions transfer to Pons;
8. keep all cross-chain thresholds in shadow until Pons-local prospective validation.



# Wave 2 — behavioral traces, entity-adjusted concentration and collector integrity

## New P0 source: git-disl/MELT

Public paper/repository:
- 41k+ Solana memecoin launches;
- 200M+ parsed transactions;
- typed swaps, transfers, wash trades and mints;
- bundle traces and same-entity clustering;
- 122 behavioral features;
- chronological train/test split in the public dataset loader;
- source license: CC BY-NC 4.0, so production code must NOT be copied into a commercial system without permission. Methodology and independently reimplemented measurements may be researched.

### E13 — raw-holder concentration is not economic concentration

The public feature generator computes both address-level and cluster-adjusted concentration.

High-value primitives reproduced from source:
- holder Gini;
- raw top1/top5/top10/top20/top50/top100 supply share;
- first-buyer cohorts at top1/top5/top10/top20;
- current holding / initial holding ratios for early buyers;
- sniper windows at 0s / 1s / 5s / 10s;
- dev initial holding / current holding / hold ratio;
- wash ratio;
- transfer ratio;
- buy/sell user counts;
- buy/sell volume and sell-pressure;
- realized and unrealized PnL for early-buyer cohorts.

The strongest primitive is a cluster-adjusted second view:
- bundle-linked accounts are grouped;
- accounts sharing signer evidence are grouped;
- overlapping cluster evidence is unioned with Union-Find;
- holdings are recomputed per economic cluster;
- raw top-N concentration is compared with clustered top-N concentration.

Robinhood translation:
`address_top10_pct` must never be the only concentration field.
Add shadow fields:
- `entity_top1_pct`
- `entity_top5_pct`
- `entity_top10_pct`
- `cluster_total_pct`
- `largest_cluster_pct`
- `raw_vs_entity_top10_delta`
- `early_buyer_retention_ratio`
- `dev_retention_ratio`.

This is particularly relevant to Pons launch exemptions and ASKR-style first-block topology.

### E14 — early-buyer retention is more informative than early-buyer presence alone

MELT tracks how much the earliest buyer cohorts still hold relative to their initial allocation.

Translation:
For Pons, freeze first buyer/exempt cohorts at T0 and observe:
- initial token share;
- share remaining at +1m/+5m/+10m/+20m;
- realized distribution into later independent buyers;
- whether early buyers add, hold, or unload.

This separates:
`early informed accumulation`
from
`privileged launch inventory distributed into followers`.

### E15 — bundle cleanliness is adversarial

Public Solana bundler repositories explicitly advertise launch + multi-wallet buys in one atomic bundle and techniques intended to make wallets appear independent to common analytics surfaces.

Defensive conclusion only:
- a clean Bubblemap-style graph is not proof of independence;
- same-block / same-transaction-family co-firing matters;
- first funding source matters;
- repeated co-firing across launches matters;
- later gather/sell convergence matters;
- address lookup / bundle traces, when observable, are valuable evidence.

Do NOT import, reproduce or operationalize evasion/bundling instructions.

## New P0 research: persistent coordinated cohorts

Recent open research on Pump.fun persistent early-buyer cohorts uses:
- first-buyer-window extraction;
- cross-launch co-occurrence graphs;
- Union-Find / connected-component style cohort formation;
- repeated co-firing across independent launches.

Critical negative result:
raw association between a cohort and later activity can be massively contaminated by the cohort's own purchases. After removing cohort wallets from the measured outcome and matching launches on quality covariates, the apparent effect shrinks sharply.

Alpha Lab translation:
`COHORT_PRESENT` is topology evidence, not alpha.

Every cohort test must:
1. remove the cohort's own volume/buyer count from the outcome;
2. compare against age/stage/launch-quality matched controls;
3. freeze cohort membership before outcome;
4. distinguish repeated co-firing from one-off co-entry;
5. treat common funding as evidence of dependence;
6. measure lead over public/social propagation;
7. test realizable entry after the cohort is observable.

This strengthens the existing rule that wallet convergence is a conditional G3 confirmation layer only.

## New P0 research: collector integrity is part of alpha integrity

Recent Solana research comparing independently configured Pump.fun collectors found very low overlap between collector outputs in some windows. Separate research also shows that off-chain collector terminal labels can fail temporal holdout and may not equal platform-side graduation outcomes.

Translation to Alpha Lab:
a scanner can be statistically sophisticated and still learn the wrong population if its collector misses a class of launches.

Add runtime research health fields:
- `launches_expected_or_reference_count`
- `launches_observed_count`
- `collector_coverage_estimate`
- `cross_collector_jaccard`
- `cursor_head_lag`
- `open_gap_count`
- `oldest_open_gap_age`
- `raw_event_to_canonical_row_rate`
- `unknown_terminal_label_rate`.

Do not convert TIMEOUT / missing observation directly into "failed launch".

## E16 — exact ingestion invariants verified from solana-realtime-indexer source

The implementation confirms the architectural claims:

1. **Atomic progress**  
   Writer commits events, trades and checkpoint inside one database transaction. Cursor cannot truthfully advance beyond committed evidence.

2. **Bounded hot path**  
   Parsed rows enter a bounded queue; a dedicated writer performs batched persistence. This keeps event decoding separate from disk latency.

3. **Independent gap evidence**  
   A slot watermark and datasource disconnect records produce explicit gaps instead of silently reconnecting.

4. **Overlap recovery**  
   Recovery expands each missing range with overlap slots and deduplicates through the existing persistence path.

5. **One decode path**  
   Backfill invokes the same `run_pipeline` used by live ingestion, reducing live/backfill parser drift.

6. **Independent completeness test**  
   `verify-range` reconstructs the expected event identity set for a slot range and compares missing/extra events against persisted rows.

7. **Dead letters instead of disappearance**  
   Failed/timed-out database batches are parked as dead letters with error context.

Pons acceptance should copy these invariants conceptually, not the Solana/Rust implementation.

## E17 — wallet graph discovery is useful; global wallet scoring remains suspect

New source: `0x1nfra/echo-wallet-tracking`.

Useful public primitives:
- graph traversal from successful token -> early buyers -> candidate wallets -> subsequent convergence;
- realized + unrealized PnL separation;
- profit factor;
- median hold duration;
- max drawdown;
- entry speed;
- early-entry frequency;
- exit discipline;
- 7/30/90d windows.

Weak / unvalidated parts:
- hard-coded "smart money" category thresholds;
- global 0-100 score;
- FIFO accounting may diverge from economic intent for complex multi-entry flows;
- validation described against only a small known-wallet set;
- no economic-entity independence in the basic architecture.

Translation:
use graph traversal as a **research lead generator** and preserve metrics separately. Do not collapse them into one canonical wallet score.

## E18 — first-five-minute behavioral risk deserves a Pons challenger

Recent Solana research over millions of tokens reports useful rug discrimination using only the first minutes of trading, with behavioral rather than contract-code features.

Candidate Pons shadow feature families:
- entity-adjusted concentration trajectory;
- early-buyer retention/distribution;
- dev inventory trajectory;
- independent buyer growth;
- wash/self-flow ratio;
- sell pressure;
- liquidity trajectory;
- repeated cohort participation;
- funding-source diversity;
- first-distribution survival.

Keep the target separate from moonshot upside:
`RISK_PROBABILITY != UPSIDE_PROBABILITY`.

## Wave 2 priority changes

| Source / primitive | New priority | Action |
|---|---:|---|
| MELT behavioral trace methodology | P0 | Reimplement compatible measurements, do not copy CC BY-NC source into production |
| solana-realtime-indexer exact ingress invariants | P0 | Route directly into #1017 acceptance |
| persistent coordinated cohort research | P0 | Add decontaminated cohort challenger to existing G3 research |
| collector-overlap / label-integrity research | P0 | Add collector completeness metrics to runtime health |
| Echo wallet graph traversal | P1 | Extract graph discovery and metric decomposition, reject global score |
| public stealth-bundler behavior | P1 defensive | Use only as adversarial threat model for clustering |
| first-5m Solana rug models | P1 | Feature-family challenger, temporal Pons validation required |

## Updated next queue

1. make #1017 Pons ingress acceptance explicitly prove atomic cursor+row persistence, gap capture, overlap recovery and independent range verification;
2. add entity-adjusted concentration and early-buyer-retention fields to the existing shadow feature contract;
3. freeze and replay Pons exemption cohorts using repeated-cofire + funder + distribution evidence;
4. measure collector coverage separately from model quality;
5. build a matched negative denominator before judging any caller/wallet cohort;
6. continue searching open-source caller ledgers, funder graphs and launch-risk datasets;
7. use natural prospective Pons launches to decide which extracted primitives survive.
