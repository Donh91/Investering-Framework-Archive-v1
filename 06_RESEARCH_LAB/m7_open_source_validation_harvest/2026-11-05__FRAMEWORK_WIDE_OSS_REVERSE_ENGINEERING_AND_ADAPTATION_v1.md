# Framework-wide open-source reverse engineering and adaptation | 2026-11-05

**Scope:** All relevant investment framework archives, NOT News Intelligence alone. **Status:** P0/P1 method-source research, no live installation or authority change.

Machine-readable source inventory: 04_RESEARCH_LAB/external_specialist_dissection/2026-11-05__CROSS_FRAMEWORK_OSS_SOURCE_SNAPSHOT_v1.json

**Canonical owners:** Existing Research Lab #1512 / Strategist #1157 / S1 #1156. Reuse 04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json. No additional agent, scheduler, source subscription, research queue, trading authority or separate writer.

## Existing systems and overlap

The project already includes research mission RL-OPEN-SOURCE-VALIDATION-HARVEST-007 (2026-10-06), a specialist method queue, Research Genome, backtest_engine/statistics.py with purged walk-forward and bootstrap, the M6 Event Outcome Contract, Task 2 PIT source gates, experimental independent replay, the Alpha microstructure/Wallet Lab and the Supervisor/Strategist governance chain. The October harvest already implemented M6 outcome and causal F3 work. Its remaining forward observational gates MUST NOT be rebranded as new missing methods.

Five connected relevant repositories checked directly:
- Archive-v1: PUBLIC canonical source, forecasts, M6, data, Research Lab, Supervisor, Strategist and GitHub Actions.
- Eksperimenter-framework-: PUBLIC, noncanonical request-hash verified independent experiment and execution receipts.
- Meme-Alpha-Lab: PRIVATE repository but PUBLIC-SAFE evidence only, Scout, microcap, Wallet Alpha, Narrative, Microstructure, paper execution.
- Investering-AI-Audit-Bridge: PRIVATE, noncanonical independent reports, never direct production source/merge.
- CycleNavigator-scores: PUBLIC verification mirror, with currently provisional historic timestamp proof, not proof of economic Edge.

Donh91/secrets is the **restricted data plane** and is NOT read or copied into this public research mission. Vault is outside operational source exploration.

## Eight source-to-owning-lane workstreams

### P0 1. Autonomous closure and system reliability
**Candidates:** Temporal MIT, Prefect Apache-2.0, OpenTelemetry Apache-2.0, LangGraph MIT. **Owner:** existing S1 #1156, Strategist #1157 and framework learning supervisor.

Reverse-engineer finite-state workflows, retry idempotence, deadline/timeout, checkpoint and trace-receipt patterns. DO NOT install a substitute orchestrator. Existing GitHub Actions remain writers; S1 remains sole Chat Supervisor. Build a deterministic replay of at least these real failure classes: stale HOLD, unchanged blocker, changing HEAD, Codex quota exhaustion, CI fail then fix, previously paid Sol mission, qualified merge/main-readback, postrelease consumer failure. One issue should end in actual merged/verified, superseded-closed or bounded terminal blocked state, not repeat comments. Every action binds original issue+PR+SHA+attempt+executor+receipt+time. Require new source evidence to repeat an attempted repair. Keep destructive source/recovery authority separated. **Kill:** no measurable reduction in unclosed items or duplicate work.

### P0 2. Compass, Cycle Navigator, rotation, macro and pullback
**Candidates:** River BSD-3-Clause ADWIN / ruptures BSD-2-Clause PELT / Qlib MIT. **Owners:** existing Official Compass, Task 2, M6, CN Score mirror.

Compare a causal online regime/drift shadow challenger against current Compass 12h/24h/72h/168h, CN frozen Monday range and M6 pullback 3/5-4/5 episodes, including abstention, missed events and false warnings. Negative control: applying full-sample retrospective PELT to an earlier period would use future data, so only expanding/rolling as-of predictions count; freeze each signal when first published. Measure incremental false-negative detection and cost relative to existing 14-day audit, price/momentum/no-change baselines. Do not alter thresholds, BUY/SELL or historical forecasts. **Kill:** fails PIT or loses against incumbent after costs and uncertainty.

### P0 3. Task 2, real Edge and reproducible backtests
**Candidates:** QuantConnect LEAN Apache-2.0 / Qlib MIT, compare existing native backtest_engine; Zipline and QuantStats only if distinct value. **Owners:** Task 2 + public Experiment Execution Plane.

LEAN fill/event clocks are a falsifier for assumed fills and trade capacity; Qlib handlers are a source/feature lineage challenger. Existing code already has walk-forward, purge/embargo, confidence intervals and grouped outcome methods, so do not reinvent them. Run one-shot reproducible experiment keyed to same decision clock, original feature retrieval time, non-overlapping observations, realistic spread/fees/fills, alternative no-trade/control decision, loser-inclusive denominator, and immature outcome handling. Compare at most one primitive each experiment. **Kill:** unverified PIT, overfit, near-zero realizable edge or insufficient samples.

### P0 4. Alpha Lab, microcaps and actual exit quality
**Candidates:** CCXT MIT normalized exchange data / Hummingbot Apache-2.0 paper execution. **Owners:** existing Meme Alpha microstructure, wallet qualification, public source registry, paper ledger and on-chain owner.

Study order book depth, spread, tax, gas, liquidity, partial fills, slippage, venue, transfer and bridge delays, impact of notional size. Match DEX route simulations to source-verified chainId+contract; preserve existing GoPlus/Honeypot negative-route tests, Pons public decoder and Robinhood first-cohort evidence. Do not deploy live bots or place orders. Distinguish paper returns, executable returns and hard drawdowns. Include losing launches and tokens never alerted; measure false SAFE and false UNSAFE and 1-3-day swing utility. **Kill:** cannot obtain same-time executable evidence or edge disappears after friction.

### P1 5. On-chain temporal truth
**Candidate:** Graph Node Apache-2.0; existing Blockscout/raw RPC remain default. **Owners:** existing Alpha chain / source / forensics. Extract log indexing, chain-reorg invalidation, per-block finality and exact contract/tx/log identity from the event ingestion path. No expensive full self-hosted indexer until a known current owner bug justifies it. **Kill:** same evidence already available from the existing raw chain pipeline.

### P1 6. News / narrative / market information
**Candidates:** AIHOT MIT / Horizon MIT / xnews Apache-2.0 / Trafilatura Apache-2.0. **Owner:** News Intelligence #1888 and merged #1900 source challenger; Alpha #218 read-only. This lane has ALREADY BEEN INTAKED and MUST NOT start again. Continue unmonitored event-family source coverage and natural producer->Director->consumer evidence; no duplicate "new agent". Source-independent fact vs syndicated article, as-of clock and exact contract binding matter; B0/B1/B2 NEWSFT prospective >=50 before claims of economic impact.

### P1 7. Data health, source drift and research governance
**Candidate:** Evidently Apache-2.0; Qlib feature provenance. **Owner:** existing Data Architecture/Source QA and Framework Learning. Detect *semantic* missingness/failed parser/freshness, distribution/regime shifts and unstable feature definitions, not just HTTP success. Compare with existing source clocks and health state; no new dashboard or noisy notifications unless it catches a verified prior miss. **Kill:** adds alerts without a better decision or repair.

### P1 8. Research Genome and tail-risk learning
**Candidates:** QuantStats Apache-2.0, Optuna MIT; FinRL MIT methodology foil only. **Owner:** Research Lab #1512 and existing experiment lifecycle. Borrow risk and trial-accountability tests, NOT an off-the-shelf "AI strategy". Freeze all proposed variants, unchanged objective, evaluation window, joint costs and held-out controls. Tune only after prospective data has enough admissible N and PIT pass. Compare drawdown/CVaR, M6 MAE/MFE, warning opportunity cost, capacity and false-negative loss. Preserve all failed variants; no score inferred from cherry-picked top backtest.

## Candidate source provenance and code reuse

The accompanying JSON records 18 pinned GitHub HEAD SHAs, GitHub license metadata, candidate source file, existing owner overlap and the smallest proposed method/test. Repository MIT/Apache/BSD code permission does not confer publisher news rights, model weight licenses, APIs, RPC access or dataset redistribution. Copyleft or source-available repositories require separate legal review and are NOT auto-copied. Verify version/dependency/license again before vendoring.

Priority is not repo stars or apparent AI sophistication. Select distinct information, reproducibility, decision value, transferability, operational simplicity, license/data rights and independent refutation. An open-source agent can be studied as a recipe without being installed or connected to our repositories.

## Permanent execution and learning process

1. Source PINNED -> existing-owner OVERLAP -> frozen falsifiable claim.
2. First-party/public independent reproduction -> baseline and source receipt.
3. Negative controls + simulated counterexamples + no-lookahead tests.
4. Existing Research Lab #1512 -> Strategist #1157 adjudication. One actionable delta per primitive, with accepted/rejected/blocked trigger.
5. Existing S1 #1156 routes exactly one accepted heavy task to original domain owner and authorizes only qualified bounded PR, within active PR cap. Never create competing supervisor.
6. Independent CI/review -> qualified merge -> exact main/consumer readback. A comment, queue entry, API packet or green CI alone is not completion.
7. Prospective matched effect evaluation -> RETAIN / MODIFY / KILL. Negative findings retained permanently with source and reason.

**First four actual candidate coding missions, in priority order:** (a) S1 finite-state replay anti-loop checks, (b) Task 2 event-time/fill realism falsifier on existing native engine and Experiments Plane, (c) causal regime drift challenger for Compass/M6, (d) Alpha paper-exit capacity with CCXT/Hummingbot mechanics. Each requires overlap check before code. No parallel full-agent deployments, no new paid API missions, no promotion of live forecasts or market thresholds.

## Non-claims

This is a breadth-first live-repo and public OSS source triage, not a claim that every historical artifact was read or every algorithm reproduced. Source code and four of the upstream paths were inspected, other items remain candidate method references. The new source inventory is reproducible, but individual domain features have NOT been implemented or empirically proven. No private secrets, trading, new API credentials, scheduled tasks or external code execution are introduced.
