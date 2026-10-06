# High-Value Edge Research

Status: ACTIVE_RESEARCH_PROGRAM
Authority: RESEARCH_ONLY / ZERO_LIVE_TRADING_AUTHORITY
Created: 2026-10-06

Canonical home for the Framework highest-value attempts to prove or kill economically meaningful edge.

An Edge package is a falsification program with frozen claims, point-in-time provenance, simple baselines, economic accounting, independent episode counting, negative controls and prospective confirmation.

## Claim ladder

1. HYPOTHESIS
2. HISTORICAL_CANDIDATE_EDGE
3. ROBUST_HISTORICAL_EDGE
4. PROSPECTIVELY_SUPPORTED_EDGE
5. DOCUMENTED_FRAMEWORK_EDGE

DOCUMENTED_FRAMEWORK_EDGE requires point-in-time admissibility, superiority to frozen simple baselines on the same clock, positive economics after costs and false exits, appropriate independent episode/regime robustness, no unresolved material leakage, prospective out-of-sample support, and independent adversarial review.

No single backtest, hit rate, AI verdict or impressive episode can grant the label.

## Information edge versus action edge

Every package separates INFORMATION EDGE from ACTION EDGE. A failed action mapping does not automatically disprove an information edge. A useful warning does not automatically justify SELL.

## Active package

EDGE-001_TSUNAMI_EARLY_WARNING_AND_SURVIVAL

Question: Can the Framework detect deterioration early enough to provide economically useful protection without systematically exiting the good pumps?

This is the only ACTIVE package at creation.

## Candidate registry, not active claims

Future packages require separate preregistration:
- ROTATION_TRANSMISSION_EDGE
- CYCLE_RANGE_EDGE
- ETF_INCREMENTAL_EDGE
- ALPHA_DISCOVERY_EDGE
- REENTRY_EDGE
- FALSE_NEGATIVE_PERMISSION_EDGE, BLOCKED until legitimate owner semantics exist.

Listing is not evidence and creates no implementation or live authority.

## Governance

- One canonical package owner per edge question.
- Reuse M1-M7, HCEL, Compass, CN and Research Genome evidence. Do not duplicate owners.
- Preserve negative and method-invalid results.
- No threshold tuning after outcome inspection.
- Same clock, cost and data rules for Framework and comparators.
- Count independent episode families, not repeated alerts.
- Reconstructed or event-time-proxy evidence remains visibly weaker than PIT evidence.
- Claude Bridge is an adversarial reviewer, not a second policy designer.
- Live market or portfolio behavior requires separate governance outside this directory.


## Execution and adversarial evaluation, #1521, 2026-10-06

Status: T2_LOCAL_EXECUTION_PASS / REMOTE_WORKFLOW_PENDING_VERIFICATION / METHOD_REVIEW_REQUIRED.
Authority: RESEARCH_ONLY. CLAIM_LEVEL=HYPOTHESIS. WARNING_IS_SELL=FALSE. LIVE_EXIT_RULE=NONE.

This is an execution receipt and method review, not a new research owner or evidence of warning/trading skill. Issue: [#1521](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1521). Exact source checkout: `9320d4f6977de93f1a5b01473b5058c53685e730`.

### Work actually performed

- Reproduced the unmodified generator failure: `py_compile` passed but full execution raised `NameError: SRC is not defined`. A literal backslash-n inside the comment had commented out the source assignment. Previous Actions run [37533959148](https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/37533959148) passed syntax and failed the build step.
- Restored only the physical newline before SRC. No thresholds, family rules, price tape, comparator semantics or frozen contracts changed. Repair commit: `5e009c9cd55e38fe30d341cb029b59e4a3b4599e`. Isolated branch: `agent/task-20261006-edge001-t2`.
- Executed the complete T2 generator twice after repair, on the exact archived compressed source. Both runs returned PASS and produced byte-identical JSON.
- Verified source SHA-256, artifact SHA-256, primary BTCUSDT/10 cell, `framework_warning_data_joined=false`, positive prices, unique timestamps, exact hourly cadence within continuity segments, episode timestamp ordering and grid-crossing consistency.
- Additional completed work from the research list: T1C price-tape/source binding and continuity audit; T1A/T1B outcome-only adverse/control census; T2 method/independence audit. These are bounded completed checks, not claims that all T1 provenance work or T2B is complete.
- Executed five synthetic causal/control checks: P1 rearming only after peak regain, no premature rearming, segment reset, valid V reversal, and rejection after a 10% crossing. All passed.
- Reproduced censored-episode loss at segment boundaries and quantified its occurrence on the actual tape.
- No warning join, T2B annotation, T3 score, p-value, action simulation, paid model call or live action was performed. Other candidate Edge packages were not activated.

Compressed source SHA-256: `f3adc5716343c3a6e7dca812f4ca2d607abb5dd37495a7fa268ab41e5e889bd8`.
Expected generated registry SHA-256: `c8f8aa30502b909f016787161a661b2183f8ceef61c820cea00c53c5b70f71db`.
Target: `EDGE-001_TSUNAMI/T2_OUTCOME_ONLY_EPISODE_REGISTRY_v1.json`.

### Outcome-only census

Counts below are generator output, not independent inferential N or Framework hits.

| Window | Asset | Eligible hourly rows | Continuity segments | P1 / P2 fires | Families by grid | BTC V controls |
| --- | --- | ---: | ---: | --- | --- | ---: |
| ALTSEASON_2020_2021 | BTCUSDT | 11,659 | 10 | 29 / 51 | 10%: 12; 15%: 8; 20%: 6 | 14 |
| ALTSEASON_2020_2021 | ETHUSDT | 11,659 | 10 | 40 / 59 | 15%: 10; 20%: 6; 30%: 2 | N/A |
| MODERN_ANALOGUE_2025_2026 | BTCUSDT | 13,847 | 1 | 7 / 7 | 10%: 13; 15%: 5; 20%: 3 | 1 |
| MODERN_ANALOGUE_2025_2026 | ETHUSDT | 13,847 | 1 | 5 / 8 | 15%: 12; 20%: 7; 30%: 3 | N/A |

### Evaluation for the next agent

Verdict: the execution repair is necessary and reproducible. The frozen registry is useful as an auditable baseline, but it is not yet inferentially admissible.

1. **Family-rule mismatch, material.** `families()` compares successive peak times. The charter groups overlapping peak-to-trough windows or peaks within 14d of the prior family trough. An outcome-only diagnostic application of the charter gives BTC/10 family counts 7 versus generator 12 for 2020/21, and 8 versus 13 for 2025/26. These diagnostics were not substituted into the registry. Resolve exact M6/charter ownership before a separately versioned repair; never overwrite v1 or select a rule based on warning results.
2. **Gap censoring, material.** When a threshold-crossed episode has not rebounded before a continuity segment changes, `episodes()` drops it instead of preserving a censored record. On the older tape this loses BTC episodes at 10/15/20 grids: 3/3/1, and ETH episodes at 15/20/30 grids: 2/2/2. These grid counts overlap and must not be summed as independent events. The modern tape has no such boundary losses. Preserve exclusions/censoring in a new approved version; do not bridge missing prices.
3. **Join identifiers need explicit namespacing.** Family IDs such as F01 repeat across window/asset/grid; individual episodes and V controls have no explicit stable IDs. Before T2B, freeze composite IDs using source hash, window, asset, grid, timestamps and continuity segment, without changing membership.
4. **Control power is limited.** The modern primary tape contains only one V-reversal control, below the repair's three-independent-control-cluster floor. The three-control floor is not met by that count. Do not silently pool regimes or substitute recovered-warning controls without exact lineage.
5. **No historical typed edge proof.** PRE_T2_METHOD_REPAIR keeps current typed Claim A NOT_TESTABLE_AT_PIT and Claim B NOT_TESTABLE_NOW. A larger outcome census does not create missing historical typed warnings. Prospective M6 Lane C remains the proof route.
6. **Cross-asset independence remains unresolved.** Per-asset family counts cannot be added as inferential N. Adjudicate overlaps before scoring.

Recommended order: verify remote T2 execution and exact main artifact -> freeze/adjudicate the method discrepancies and stable-ID plan -> versioned outcome-only repair if approved by the existing owner -> T2B provenance annotation only -> native predecessor discovery where admissible -> prospective M6 confirmation. T3 typed historical edge-proof and live action remain closed.

Row/technical acceptance: PASS locally.
Coverage/inferential readiness: NOT_READY.
Edge/promotion status: NO_CHANGE.
Write manifest: one generator newline repair plus append to this existing README; no frozen-contract, workflow, registry-policy, index or source-data changes.
Backup product for this run: NONE; no new Vault snapshot verified.
Remote run/merge completion must be recorded in the #1521 issue thread after exact-head readback; the local PASS above must not be mistaken for a remote Actions PASS.
