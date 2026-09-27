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

