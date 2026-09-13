# NANSEN MCP RESEARCH QUEUE

Status: `RESEARCH_ONLY`
Owner: Investering Framework Research Lab
Source anchor: `source_notes/AT-SRC-0008_NANSEN_MCP_ONCHAIN_INTELLIGENCE.md`
Authority: `NONE_BY_ITSELF`

## Purpose

Evaluate Nansen as a read-only onchain intelligence provider for Alpha Lab and future Astra-era automated research without duplicating existing data, silently increasing recurring spend, or creating execution authority.

## P0 — Duplicate-coverage audit

Before any paid or recurring Nansen use:

1. inventory existing onchain/wallet/holder/DEX-flow data in the public and restricted research planes;
2. define the exact Nansen fields needed by each hypothesis;
3. map every desired field to one of:
   - `EXISTING_EXACT`
   - `EXISTING_APPROXIMATE`
   - `DERIVABLE_FREE`
   - `NANSEN_LABEL_ADVANTAGE`
   - `NANSEN_HISTORY_ADVANTAGE`
   - `PAID_GAP`
   - `NOT_NEEDED`
4. document endpoint credit cost and rate limits at retrieval time;
5. refuse broad historical backfill until a frozen experiment requires it.

Primary objective: maximize incremental information per paid API credit.

## P0 — Read-only capability proof

Run a minimal read-only proof against representative tasks only after credentials are available through governed secrets handling.

Candidate proof tasks:

- profile a known wallet and compare labels/PnL against public explorer evidence;
- query Smart Money netflow for a liquid token and compare with free/public flow proxies;
- inspect top holders / holder-type segmentation;
- inspect DEX trades for a known event window;
- retrieve token-screening output for a controlled universe.

Record:

- endpoint/tool;
- query parameters;
- response schema;
- retrieval timestamp;
- credits consumed;
- unique fields returned;
- overlap with existing archive;
- latency;
- any unavailable chain/asset limitation.

No transaction preparation, signing, execution or wallet authority is part of this proof.

## P1 — Alpha Lab / meme research ablation

Test whether Nansen-specific labels improve the existing meme/early-token research process.

Candidate feature families:

- labeled-wallet count and change;
- wallet-quality weighted buyer acceleration;
- smart-money netflow;
- holder concentration by labeled segment;
- repeat-buyer quality;
- entity-linked exchange inflow/outflow;
- wallet PnL quality;
- buyer/seller composition around discovery time.

Required comparison:

1. current Alpha Lab features without Nansen;
2. equivalent raw/free onchain features;
3. Nansen labels/features added;
4. Nansen labels/features only.

Measure whether Nansen adds incremental information rather than merely prettier labeling.

The owner-approved experiment contract is now:

`NANSEN_ALPHA_LAB_ABLATION_V1.md`

Its exact competitive cohort is bound privately under:

`Donh91/secrets:private_research/memes_alpha/provider_benchmarks/nansen/2026/09/11/benchmark_manifest_v1.json`

## P1 — Point-in-time label audit

Critical research question: can historical Nansen labels be reconstructed as they were observable at the decision timestamp?

If not, current labels applied to old trades must be marked `RETROSPECTIVE_LABEL_RISK` and excluded from clean causal backtests unless a defensible point-in-time proxy exists.

This matters especially for:

- Smart Money labels based on trailing PnL;
- wallet ranking windows;
- entity attribution discovered after the event;
- labels that are revised or promoted later.

## P1 — Smart Money conditionality

Do not assume Smart Money accumulation is bullish.

Test conditional performance by:

- liquidity tier;
- market-cap tier;
- token age;
- regime/state from existing Framework owners;
- broad-risk-on vs stress;
- concentration vs breadth of participating wallets;
- accumulation duration;
- realized vs unrealized historical wallet quality;
- subsequent liquidity and holder-growth confirmation.

Negative-control windows are required.

## P2 — Astra tool-routing benchmark

Once Astra/Agents API execution infrastructure is qualified, compare two research lanes on the same frozen tasks:

A. Astra with existing free/open data only.
B. Astra with Nansen MCP available as an optional tool.

Measure:

- answer correctness;
- verified evidence found;
- unresolved gaps;
- tool calls;
- token cost;
- Nansen credit cost;
- latency;
- marginal conclusion change;
- false-confidence rate.

Nansen should be called only when expected information gain justifies provider cost.

## P2 — Historical backtest purchase gate

Historical Nansen data may be purchased only when all are true:

1. hypothesis is frozen;
2. free/current archive cannot answer it;
3. endpoint history is sufficient for the target period;
4. point-in-time semantics are understood;
5. expected credit cost is documented;
6. licensing/storage rules are documented;
7. baseline and falsification tests are pre-registered;
8. a maximum acquisition budget is set.

## Promotion criteria

Nansen may become a recurring research data lane only if it demonstrates at least one of:

- unique labels/features unavailable from existing sources;
- materially higher accuracy/coverage than free derivation;
- substantial research-time savings per dollar/credit;
- stable incremental out-of-sample value in a governed feature study.

Provider convenience alone is not sufficient.

## Kill / downgrade criteria

Downgrade or stop the lane if:

- most useful fields are already available or cheaply derivable;
- label leakage cannot be controlled for historical research;
- endpoint costs scale poorly relative to information gain;
- chain coverage excludes priority universes;
- provider schema/labels drift without reproducible versioning;
- Nansen features fail incremental ablation after costs.

## Recommended current state

`RESEARCH_QUEUED / NO PAID BACKFILL / READ_ONLY_ONLY`

The immediate next step is now frozen as a duplicate-coverage + point-in-time + Alpha Lab ablation benchmark. Codex may build the deterministic read-only harness when the existing Memes v3 baseline is operational. A recurring Shadow adapter is explicitly deferred until the benchmark proves incremental value.
