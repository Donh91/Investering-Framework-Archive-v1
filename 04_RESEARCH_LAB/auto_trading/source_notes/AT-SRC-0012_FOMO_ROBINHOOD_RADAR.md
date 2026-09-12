# AT-SRC-0012 — FOMO Robinhood Radar

Date captured: 2026-09-12
Source type: Open-source repository + linked X post
Repository: https://github.com/cvxv666/fomo-robinhood-radar
Author: cvxv666 / @antpalkin
Status: RESEARCH_QUEUED
Evidence class: CODE-VERIFIED ARCHITECTURE + MAINTAINER PERFORMANCE CLAIMS REQUIRING REPRODUCTION
Primary operational fit: Alpha Lab / memes / Robinhood Chain
Secondary fit: AUTO_TRADING upstream feature research
Authority: READ-ONLY / RESEARCH ONLY / NO EXECUTION

## Executive assessment

This is substantially more interesting than a typical AI-trading social post because the repository contains a real, test-covered data pipeline rather than only prompts or screenshots.

The strongest transferable value is not its LLM score. It is the combination of:

- profile -> real-wallet resolution;
- low-cost on-chain fill collection;
- receipt-level provenance to determine whether a fill was actually the tracked wallet's trade;
- dust/direct-push/seeded-token defenses against manipulated smart-money feeds;
- reconstructed wallet books from fills plus live balance reads;
- burst detection based on trusted-wallet first-entry acceleration;
- explicit exit monitoring;
- point-in-time score history and out-of-sample calibration attempts;
- fail-soft source architecture;
- a CLI/API/SKILL layer suitable for future agent tooling.

This makes the project a high-value source for Alpha Lab wallet intelligence and a useful candidate component/benchmark for future Astra research.

It must NOT be treated as proof of predictive alpha yet.

## Verified repository facts

As inspected on 2026-09-12:

- repository is public, MIT licensed and Python-based;
- repository was created 2026-09-11, so it is extremely new;
- README documents live site, Telegram bot and HTTP API;
- pipeline modules include `resolve`, `provenance`, `analyze`, `calibrate`, `hot`, `backfill`, `holdings`, collection and health tooling;
- tests exist for analysis, API, calibration, hot/burst logic, provenance, RPC, resolution and other modules;
- `SKILL.md` exposes a structured research-agent interface over the dataset;
- no trading/execution engine is required for the core research pipeline.

## Strongest architectural finding: provenance before signal

`pipeline/provenance.py` directly addresses a failure mode highly relevant to our Alpha Lab work:

A token can appear to have been bought by trusted wallets even when an outside actor paid for the swap and named those wallets as recipients.

The repository distinguishes:

- `direct`: transaction sent directly to the router, not a normal wallet-originated app trade;
- `dust`: abnormally small buy relative to an absolute threshold and the wallet's own typical size;
- `trade`: remaining flow that passes the provenance rules.

It also marks tokens as `seeded` when pushed/dust/direct buys hit multiple trusted wallets and outnumber genuine trades.

This is a materially useful anti-manipulation pattern for any future smart-money/memecoin pipeline.

TRANSFERABLE PRINCIPLE:

`wallet received token` != `wallet intentionally bought token`

Every wallet-flow signal should preserve transaction provenance and test adversarial attribution before entering a ranking model.

## Wallet resolution

The project documents an inference process that resolves a fomo profile to the likely execution wallet by comparing token/trade timing across quiet windows.

The README reports 101 agreements and zero disagreements against later verified wallets.

Treat this as a MAINTAINER CLAIM until reproduced from the relevant fixtures/live data.

The underlying design is nevertheless useful:

- use multiple independent behavioral observations;
- weight low-background-noise windows more heavily;
- preserve conflicts rather than overwriting inferred identity when a later source disagrees.

## Free/on-chain collection design

The default Robinhood Chain path uses batched `eth_getLogs` plus batched transaction receipts rather than one request per wallet.

The README reports roughly 30 free requests for a full pass over about 302 wallets and reports 209/209 agreement on token/side against a separate trenches tape in one comparison window.

Again, treat the exact accuracy numbers as MAINTAINER CLAIMS until reproduced.

Architecturally, the batched topic-filter approach is high-value because it suggests a low-cost prospective Shadow feed for Robinhood-chain wallet research without buying duplicated data.

## Trader scoring: useful structure, not trusted truth

`pipeline/score.py` uses a compact per-wallet context and an LLM to produce:

- score 0–100;
- active/watch/dropped state;
- style tags;
- red flags;
- short reasoning;
- confidence.

Important: the current repository code uses Anthropic model identifiers (`claude-haiku-4-5`, `claude-sonnet-4-6`) or manual export/import to any LLM. The X post's wording that every trader receives a "GPT-6 Astra score" is therefore NOT a faithful description of the currently inspected default code path.

The score also weights fomo-reported PnL, including open/unrealized positions, as the primary signal. This can be useful for memecoin books where winners remain open, but it creates important risks:

- mark-to-market dependence;
- one-hit / extreme-winner distortion;
- survivorship;
- platform-specific PnL semantics;
- possible dependence between score features and later evaluation if not timestamped strictly.

The score should be treated as one feature family, not as a truth label.

## Out-of-sample calibration: unusually positive sign

`pipeline/calibrate.py` explicitly acknowledges that a numerical score is meaningless unless tested prospectively.

It stores score history and evaluates only positions opened after a wallet's earliest verdict. This prevents the most obvious circular test where the historical PnL used to create the score is also used to claim that the score predicted performance.

The code also explicitly states known limitations, including small samples and uncorrected survivorship.

This is significantly better research hygiene than most social-media "smart money" systems.

TRANSFERABLE PRINCIPLE:

A wallet/trader score must be evaluated only on actions observable after the frozen score was assigned.

## Critical issue: burst backtest can run with look-ahead-contaminated wallet scores

`pipeline/hot.py` is one of the most interesting modules and one of the most important caveats.

The burst rule uses first buys inside a sliding window and weights wallets by `(score/100)^2`.

The module offers score lookup modes:

- `strict`: score actually in force at the historical timestamp;
- `first`: earliest recorded verdict;
- `current`: today's score replayed over the historical tape.

The code itself correctly documents that `current` reads the answer first.

However, the `backtest()` function currently defaults to `mode="current"`.

Therefore social claims such as burst hit-rate / "39% go 2x" must NOT be accepted as clean out-of-sample evidence unless the exact reported statistic is reproduced under `strict` point-in-time scoring, with provenance filtering, launch/liquidity filters and frozen outcome definitions.

This is the single most important research caveat found in the source review.

## FLYBRAIN claim

The code comments document FLYBRAIN as a real motivating example and describe an early burst before pool open / before the later run.

The X post claims a 20:18 alert, pool open at 20:51 and later 27x performance.

This is useful as a case study, not statistical evidence.

Before using it as evidence, reconstruct:

1. exact chain timestamps;
2. first buys and wallet identities;
3. score version in force at that time;
4. transaction provenance;
5. pool opening definition;
6. price source and executable liquidity;
7. whether the alert existed prospectively rather than being reconstructed after the run.

## Why this fits Alpha Lab especially well

The repository directly implements several ideas already central to the meme / Alpha Lab direction:

- contract/token identity rather than ticker-only matching;
- wallet quality rather than raw wallet count;
- first-entry timing;
- buyer acceleration;
- reconstructed wallet behavior;
- anti-wash / anti-seeding attribution;
- liquidity-aware filtering;
- exit feed;
- prospective outcome labeling.

Its natural role is therefore upstream evidence generation for Alpha Lab, not autonomous trading execution.

## Relationship to Nansen and existing data

Do not clone this system blindly if Nansen, current BlockHorizon/on-chain archives, existing Robinhood-chain research or other data owners already provide the same fields.

The highest-value differential appears to be:

1. Robinhood/fomo-specific identity resolution;
2. transaction-receipt provenance against planted smart-money buys;
3. extremely low-cost batched raw-chain collection;
4. burst/exit logic designed around wallet cohorts;
5. the source code itself as a benchmark for Alpha Lab pipeline design.

Future audit should compare these against Nansen labels and existing wallet-cluster tooling.

## Candidate research hypotheses

### FRR-H1 — Receipt provenance materially improves smart-money precision

Signals built from raw token receipts/transfers will have materially more false-positive wallet buys than signals requiring provenance classification.

### FRR-H2 — Point-in-time wallet quality improves burst precision

A burst weighted by wallet scores actually observable at alert time will outperform unweighted unique-wallet count after controlling for liquidity and token age.

### FRR-H3 — Current-score replay materially overstates historical burst edge

`current` score mode will outperform `strict` mode in historical replay because it leaks later trader quality into earlier periods.

### FRR-H4 — First-entry acceleration adds value beyond static holder count

Rapid arrival of independently strong wallets should provide more information than the same wallet set accumulated slowly.

### FRR-H5 — Exit-cohort behavior contains earlier failure information

When a high-quality cohort starts distributing, exit acceleration may improve risk/invalidations even if it has weak standalone directional alpha.

## Required Astra/Cowork follow-up

Priority: HIGH for Alpha Lab; MEDIUM-HIGH for Auto Trading architecture.

1. Reproduce repository tests in a sandbox.
2. Inspect the exact data model and timestamp semantics.
3. Reproduce the 101/101 wallet-resolution comparison if fixtures or source data allow.
4. Reproduce the 209/209 RPC-vs-trenches comparison.
5. Re-run burst backtests under `strict`, `first` and `current` score modes.
6. Measure the inflation caused by `current` mode.
7. Reconstruct FLYBRAIN prospectively from raw timestamps if possible.
8. Measure planted/dust/direct false-positive rate independently.
9. Compare wallet scoring with simple deterministic baselines and Nansen labels.
10. Compare weighted conviction against unique-wallet count, dollars bought, first-entry acceleration and random/high-PnL baselines.
11. Add liquidity, slippage and sellability outcomes before calling any burst tradable.
12. Preserve all evaluations as point-in-time Shadow research.

## Do not adopt yet

Do not:

- treat `score >= 70` as a canonical smart-money definition;
- treat the social burst hit-rate as verified;
- use current wallet scores in historical backtests;
- copy execution/trading behavior from the public site/bot;
- create a parallel wallet engine if existing Alpha Lab owners can absorb the useful methods;
- assume FOMO PnL is an unbiased truth label;
- give the LLM any trading authority.

## Classification

Repository classification: `BORROW_PRINCIPLE + BENCHMARK_CANDIDATE`, with selected modules potentially becoming `POTENTIAL_COMPONENT` after reproduction.

Framework status: `RESEARCH_QUEUED`.

Recommended owner if operationalized: existing Alpha Lab / meme research owner.

Auto Trading role: upstream feature/provenance research only.

No live execution authority.