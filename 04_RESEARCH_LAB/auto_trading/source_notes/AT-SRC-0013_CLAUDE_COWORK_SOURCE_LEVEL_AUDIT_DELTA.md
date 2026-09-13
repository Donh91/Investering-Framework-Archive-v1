# AT-SRC-0013 — Claude Cowork source-level audit delta

Date: 2026-09-12
Status: `RESEARCH_QUEUED / SECONDARY_REPORT_WITH_PRIMARY_SOURCE_TARGETS`
Authority: `NONE / RESEARCH_ONLY / NO_EXECUTION`
Owner: `04_RESEARCH_LAB/auto_trading/`
Follow-up issue: `#885`

## Why this note exists

Archive the incremental findings reported by the independent Claude Cowork audit after its source-level review, while preserving the framework rule that external summaries are discovery/evidence leads rather than automatic canonical truth.

The report's most important architectural claim is independently confirmed on current main: the repository already has a substantial scientific experiment lifecycle, while AUTO_TRADING's 22 hypotheses remain in a Markdown theory ledger. The correct next move is therefore to connect strategy/factor research to the existing owner, not create a parallel research machine.

## Independently confirmed against current main

### Existing experiment owner

`scripts/experiments/experiment_lifecycle.py` currently contains:
- SHA-256-based candidate identity;
- `write_new()` immutability semantics;
- typed component operators;
- deterministic placebo direction;
- explicit authority blocks with no portfolio/canonical authority;
- candidate/observation/forecast/outcome/receipt lifecycle machinery.

Current `KINDS` is exactly:

`SENSOR_COMBINATION, FORECAST_TEST, SEQUENCE_TEST, DATA_QUALITY_TEST`

There is no explicit strategy/factor kind.

`scripts/experiments/experiment_lifecycle_scientific_admission.py` currently contains:
- semantic fingerprints and deduplication;
- `QUALIFIED_FOR_FORWARD_TEST`;
- `no_retroactive_rescore`;
- baseline/negative-control/adversarial-check plans;
- research-only authority ceilings.

`04_RESEARCH_LAB/auto_trading/THEORY_LEDGER.md` contains AT-HYP-0001 through AT-HYP-0022. The ledger itself does not record a completed strategy test.

## High-value external findings requiring reproduction

### Vibe-Trading

Claude corrected an earlier classification after source-level inspection and reports that HKUDS/Vibe-Trading contains unusually strong correctness engineering, including a poison-the-future look-ahead gate, AST purity checks, same-universe random control and inherited provenance rules.

Decision: `BORROW_PRINCIPLE / BENCHMARK_CANDIDATE`, subject to exact source/license verification and local planted-defect reproduction. Do not import the framework wholesale.

### AlphaForgeBench

Claude reports Appendix C shows very low reproducibility for repeated temperature-0 LLM trading-action runs on identical BTC data, including action agreement around 0.36–0.48 and 95.7% step-level disagreement, with materially divergent return outcomes.

Decision: `PRIMARY_SOURCE_REPRODUCTION_REQUIRED` before exact numbers become framework evidence. Directionally this strengthens AT-HYP-0004/0008: LLMs should preferentially propose/compile deterministic research objects rather than sit in the per-bar action loop.

### Fine-grained multi-agent paper

Claude reports an ablation where removing four of five specialist agents improves Sharpe and only the technical agent appears incrementally useful; the useful abstraction is reportedly pre-computed technical indicators rather than raw long price context.

Decision: `PRIMARY_SOURCE_REPRODUCTION_REQUIRED`. If verified, treat as quantitative support for Minimum Sufficient Intelligence and cheap deterministic preprocessing before expensive reasoning, not as evidence to add specialist agents.

### ai-hedge-fund

Claude reports the repository now includes real PIT/look-ahead controls, including filing-time rather than period-end semantics.

Decision: re-audit current source before borrowing. This is directly relevant to US alternative-data timing contracts.

### Veles

Primary source was inaccessible behind sign-in / blocked social source. No substantive finding is adopted.

Classification: `SCREENED / PRIMARY_SOURCE_INACCESSIBLE`.

## Data correction

Claude reports that restricted storage contains an approximately 851,882-row hourly panel and a 432-position MAEVE ledger. These counts must be verified against current `Donh91/secrets` before use. Restricted bytes must remain private; public research may expose only safe manifests, hashes, contracts and aggregate results.

## Binding research decision

Do not implement a naked enum addition merely because `KINDS` lacks `STRATEGY_TEST`. That would widen admission without proving the schema can truthfully represent strategy/factor experiments.

The smallest safe change is:
1. inspect current owner and tests;
2. define the minimum strategy/factor schema extension, or prove an existing kind is sufficient;
3. preserve immutable identity, falsifier, PIT lineage, placebo/baseline, semantic deduplication and authority=false;
4. validate mechanical leakage detection against planted defects;
5. move one existing AUTO_TRADING hypothesis into a real reproducible artifact;
6. bind monotonic proposal-time trial accounting before broad Astra search.

## Priority experiments

### E1 — mechanical leakage gate

Right-truncation invariance, left-truncation/warm-up convergence and planted future-leak fixtures. The detector must demonstrate that it catches known defects before it is trusted on real factors.

### E3 — AT-HYP-0019 deterministic factor test

Compare raw feature level, rolling percentile, z-score, distance from rolling extrema and velocity conditional on normalization where data supports it. No LLM in the bar loop. Use PIT construction, deterministic controls and immutable results.

### E2 — factor/compiler vs direct action policy

Compare deterministic baseline, AI-compiled deterministic rule/factor and unconstrained per-bar LLM action policy. Blind evaluation context mechanically. Repeated-run reproducibility is a primary endpoint independent of return.

## Guardrails

- no live trading;
- no signer or credentials;
- no automatic promotion;
- no new regime engine;
- no new execution engine before evidence requires one;
- historical success may falsify/rank/stress-test but cannot alone create execution authority;
- social claims and external summaries remain discovery until reproduced;
- failed and abandoned attempts must remain visible in trial accounting.

## Operational handoff

GitHub issue `#885` is the executable research mission. It requires fresh-main verification, smallest-owner extension, planted leakage tests, one real immutable hypothesis artifact, trial accounting before broad search, focused CI and post-merge main readback.

## Bottom line

The valuable delta is not another trading framework. It is the realization that the repository's existing scientific lifecycle is already close to the required research machine. The next marginal work should connect AUTO_TRADING hypotheses to that owner and produce falsifiable evidence.