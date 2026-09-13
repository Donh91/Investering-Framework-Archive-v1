# AT-SRC-0012 - FOMO Robinhood Radar / wallet-behaviour intelligence

Date captured: 2026-09-12
Status: VERY HIGH PRIORITY RESEARCH_QUEUED
Evidence class: OPEN-SOURCE IMPLEMENTATION + LIVE READ-ONLY PRODUCT + UNVERIFIED PERFORMANCE CLAIMS

## Sources

- X post by `@antpalkin` / `cvxv666`
- https://github.com/cvxv666/fomo-robinhood-radar
- https://fomoradar.app

License: MIT in the inspected repository.

## Executive verdict

This is materially more interesting than the X marketing language suggests, but for a different reason.

The public code is not literally a 'neural copy of every winning trader'. The inspected implementation is better described as:

`identity resolution -> on-chain tape -> receipt/provenance filtering -> wallet book reconstruction -> LLM trader scoring -> weighted cohort/conviction signals -> post-verdict calibration`

That is a legitimate and unusually relevant research architecture for Alpha Lab / Robinhood Chain.

The strongest part is not the LLM. The strongest part is the provenance pipeline that tries to establish WHO actually traded, WHAT was actually their trade, and whether subsequent behavior can be evaluated point-in-time.

## High-value technical findings

### 1. Wallet resolver

`pipeline/resolve.py` infers the execution wallet behind a Fomo profile from repeated token/time co-occurrence windows. Quiet windows receive more weight than crowded ones, and the result must separate from the runner-up by hits/ratio.

The repository reports 101/101 agreements against later available verified-wallet labels. This is a project claim and should be independently replayed before adoption.

### 2. Fill provenance / anti-seeding logic

`pipeline/provenance.py` explicitly addresses a serious smart-wallet failure mode: tokens can be routed to a famous wallet without that wallet initiating the trade.

The code distinguishes:

- `direct` - external transaction sent to the router, not the tracked wallet's action;
- `dust` - amount too small relative to an absolute floor / wallet's normal size;
- `trade` - remaining qualified flow.

It also quarantines tokens where multiple trusted wallets receive pushed/dust flows that outnumber real buys.

This is highly transferable to our wallet-cluster and meme research because naive token-transfer attribution can manufacture fake smart-money consensus.

### 3. Cost-basis / book reconstruction

The pipeline reconstructs a wallet's positions from observed buys/sells and separately checks live holdings with on-chain balance reads. It explicitly excludes cases where pre-observation entry cost is unknowable rather than inventing cost basis.

### 4. LLM scoring is bounded but remains subjective

The current public `score.py` uses a structured Claude prompt by default, with manual export/import for other LLMs. It ranks traders from Fomo PnL, on-chain behavior, open positions, hold times, early entries and red flags.

Important discrepancy with the X language:

The post says the judge is GPT-6 Astra, while the current public default code inspected calls Anthropic models. The architecture is model-substitutable; the repo does not establish that Astra is the canonical scorer.

Also, the prompt explicitly treats Fomo PnL including open/unrealized positions as the primary signal. This can create selection and mark-to-market bias if used naively.

### 5. Calibration is stronger than expected

`pipeline/calibrate.py` explicitly asks whether the score predicts anything AFTER the score was assigned.

It:

- freezes each wallet's first verdict;
- counts only positions opened after that verdict;
- reports realized and marked outcomes separately;
- includes sample counts and score age;
- states that survivorship is not corrected;
- states that no market benchmark is yet present.

This is exactly the kind of temporal discipline our Research Lab wants.

### 6. Test coverage

The repository contains dedicated tests for analysis, API, bot, calibration, DB, Fomo API, hot/signal logic, parsers, provenance, receiver, resolver and RPC behavior.

Presence of tests is not proof of alpha, but materially increases engineering/reproducibility quality compared with most social trading projects.

## Why this matters specifically to Investering / Alpha Lab

This is directly relevant to existing Robinhood Chain / meme research such as TENDIEMAN and wallet-cluster accumulation work.

Potentially reusable upstream capabilities:

- entity/wallet resolution;
- transaction provenance;
- seeded/dust consensus suppression;
- normalized wallet ledger and cost-basis reconstruction;
- scored-wallet cohort aggregation;
- entry/burst and exit-flow observations;
- point-in-time calibration after the score.

The right role is READ-ONLY EVIDENCE / FEATURE GENERATION.

It must not become direct copy-trading authority.

## Major unresolved risks

1. Survivorship bias: winners are selected from leaderboards / active known wallets.
2. Score circularity: historical PnL informs the score and may dominate qualitative scoring.
3. Market benchmark missing from current calibration.
4. Regime dependence: a wallet good in one meme regime may fail immediately in another.
5. Capacity / price impact: copying multiple wallets may enter materially later at worse liquidity.
6. Latency / ordering: an alert can be point-in-time correct and still be economically untradeable.
7. Correlated wallets / social clusters can look like independent confirmations.
8. Manipulators can adapt once filters are public.
9. Open-position mark-to-market can exaggerate repeatability.
10. The claimed `39% go 2x`, $19.5M, 27x examples and similar X performance statements are discovery claims only until independently reproduced from frozen data.

## Framework classification

- identity resolver: `POTENTIAL_COMPONENT`
- provenance / anti-seeding logic: `POTENTIAL_COMPONENT - VERY HIGH VALUE`
- tape / normalized wallet ledger: `POTENTIAL_COMPONENT`
- LLM wallet scoring: `BENCHMARK / ABLATION REQUIRED`
- burst/entry signal: `FROZEN-FORWARD RESEARCH`
- exit feed: `FROZEN-FORWARD RESEARCH`
- direct neural-copy / auto-copy execution: `REJECT FOR NOW`

## Required next step

Run the dedicated `FOMO_RADAR_RESEARCH_QUEUE.md` before any code is imported or connected to capital.