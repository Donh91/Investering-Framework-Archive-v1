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

Status: T2_LOCAL_EXECUTION_PASS / ARTIFACT_PERSISTED_VIA_PR / REMOTE_WORKFLOW_DISPATCH_UNAVAILABLE / METHOD_REVIEW_REQUIRED.
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
Repair PR #1523 merged at `d969e0cd8b548ed4a2e74a0027969a78b7c86a26` after both exact-head checks (Data Architecture Gate and Storage Health Gate) passed. The existing push trigger produced no observed Actions run for that merge at the follow-up check. The available GitHub connection exposes no new workflow-dispatch operation. The exact locally generated registry is therefore persisted through a second isolated PR, without changing its bytes or claim status. #1521 stays OPEN until its required current-main GitHub Actions run is verified. A later workflow run should be an idempotent no-change build if the source remains unchanged. Do not rerun an old failed run: it is bound to the pre-repair commit and cannot verify this fix.

Outstanding agent action: dispatch `.github/workflows/edge001-t2-registry.yml` on fresh main, verify build and guard success, confirm the committed registry hash above, then close the execution issue independently of the unresolved method-review gate. This README's method findings remain binding caution for research follow-up; no blanket inferential PASS is claimed.


## #1526 execution and continued control-repair mission, 2026-10-07

Authority: RESEARCH_ONLY. No Framework-warning data was read or joined. No T3 statistic, action simulation, threshold tuning, policy change or live action was performed.

### Completed, not queued

1. Executed frozen v1.1 generator twice from source head `9929081d0570a6510ce7a0457a5b25dcf54914f9`. Syntax PASS; byte-identical output SHA-256 `b8ffeadecf4a1adf182eac8a5ab163d002af1237c1274cf3e867588977592882`. Source and immutable v1 parent hashes match #1526.
2. Independent audit checks all actual segment-end censored episodes, trough-based/segment-separated family memberships, globally unique IDs including fires and clusters, and cross-asset overlap-only transitive components. Those checks PASS.
3. Two additional control fixtures FAIL on v1.1: unresolved end-of-tape control omitted; BTC10 crossing already present at the P1 fire close can be mislabeled V_REVERSAL. Neither changes an actual classified control on this tape. v1.1 execution is complete, but its unrestricted method gate is FAIL, not T2B_READY.
4. Preserved exact v1.1 output and FAIL audit. Separately froze `T2_OUTCOME_REGISTRY_CONTROL_REPAIR_v1_2.md` at commit `5b6b0dea46e6b7d1a6e2a47fea83062aaeb58a55` before v1.2 execution. Implemented only the two control-boundary repairs in a separate generator.
5. Executed v1.2 twice; byte-identical output SHA-256 `627318638be5901f1aa4c165fa73a1297c496f74e9e751924a826acac6931f2a`. Independent audit PASS. v1, v1.1 generators, frozen contracts and parent v1 bytes remain unchanged.
6. Reconciled v1.1/v1.2: every episode, family, comparator and primary cluster row is identical. Actual control IDs/classifications are identical. Exactly two existing censored controls gain censor_utc/censor_reason metadata. No outcome membership was selected using warnings.
7. Persisted separate machine receipts: `T2_V1_1_EXECUTION_AUDIT_v1.json`, `T2_V1_2_EXECUTION_AUDIT_v1.json`, `T2_V1_1_V1_2_RECONCILIATION_v1.json`. Reusable read-only auditor: `scripts/research/edge001_outcome_registry_audit.py`.

### Reconciliation and evaluation

| Window | Primary BTC10 families, v1 -> repaired | Primary ETH15 families, v1 -> repaired | Primary BTC/ETH clusters | BTC recovered / censored controls |
| --- | --- | --- | ---: | --- |
| ALTSEASON_2020_2021 | 12 -> 11 | 10 -> 10 | 11 | 14 / 2 |
| MODERN_ANALOGUE_2025_2026 | 13 -> 8 | 12 -> 7 | 6 | 1 / 0 |

The older BTC family count is 11 rather than the earlier exploratory trough-only count 7 because v1.1 correctly prohibits merging across continuity segments and retains crossed censored episodes. The earlier diagnostic was not a replacement registry. These cross-asset cluster counts are outcome independence bookkeeping, not eligible typed-warning inferential N or edge evidence.

Evaluation: the repaired outcome mechanics are reproducible and survive the independent audit. This does not solve absent historical typed-warning provenance, the single modern recovered-control power limitation, regime coverage or action economics. Current typed Claim A remains NOT_TESTABLE_AT_PIT and Claim B NOT_TESTABLE_NOW. Modern controls may not be silently pooled to rescue the three-control floor.

Next separate mission after exact main readback: T2B source/provenance preflight, binding input to the v1.2 hash above. Confirm archived typed-owner coverage and first-main-commit knowledge times before any actual signal join. Missing warning coverage must remain UNKNOWN / OWNER_NOT_AVAILABLE, never an invented NO_WARNING performance result. T3 and trading remain closed. #1521 is separate and remains open only for its unverified v1 Actions run; this mission does not close it.

Archive write manifest: isolated explicit task branch; new outcome-only artifacts, read-only auditor, separate control-repair contract/generator and append to existing README. No deletion, workflow, canonical index, frozen v1/v1.1 contract or raw-source change. Backup product: NONE for this run. Main persistence and closure status are recorded in #1526 after CI and readback.


## Continued mission: T2B provenance preflight, 2026-10-07

Completed after #1527 merged and all nine intended files were verified on main at `e42e26ac95d0288331b4e3a0a5ffaa1cb4983fc4`. #1526 is closed as execution/adjudication completed with the v1.1 FAIL preserved and the separate v1.2 repair PASS; this is not a false v1.1 PASS. #1521 remains open and separate.

Receipt: `EDGE-001_TSUNAMI/T2B_PROVENANCE_PREFLIGHT_v1.json`.
Input: immutable T2 v1.2, SHA-256 `627318638be5901f1aa4c165fa73a1297c496f74e9e751924a826acac6931f2a`.
Source inventory: Official Compass immutable daily owner at `9929081d0570a6510ce7a0457a5b25dcf54914f9`.

Work actually performed:
- Read metadata from all 120 archived daily snapshots, binding file SHA-256, Git blob SHA, issued time, contract and policy version. No warning-state performance was inspected.
- Observed issued-time coverage is 2026-09-16T20:37:24Z through 2026-10-06T21:11:52Z. All T2 outcome windows end by 2026-07-31T23:00:00Z.
- Checked the frozen 14d attribution window for every family and the time of every control; recorded unavailable typed provenance for 94 existing family/control IDs without changing membership.
- Recorded six observed policy strata separately; 48 snapshot metadata records have no policy version. No missing version was inferred or pooled.
- No first-main-commit time was inferred from a filename, issue time or file hash. All source issued times are already after every attribution window, so additional commit latency cannot make these rows historically eligible.
- Performed no actual warning-state join, lead statistic, hit rate, circular-shift test, action simulation or promotion.

Verdict: T2B_PREFLIGHT_COMPLETE / PRIMARY_HISTORICAL_TYPED_JOIN_NOT_ADMISSIBLE for this official-source/tape combination. Missing coverage is not NO_WARNING, not a false negative and not evidence that warnings failed. The family/control annotations carry missing primary-typed provenance, not a downgrade of the independently audited price outcomes.

Next admissible routes remain the existing prospective M6 Lane C and separately frozen native-predecessor discovery. Older prose/reconstructions cannot be relabeled current typed states. A predecessor inventory would require native source/field, policy version, exact knowledge time, evidence grade and source hash before any subsequent discovery-only join. This receipt does not claim an exhaustive census of every older predecessor owner or completion of the full T2B join.

Evaluation: the research machinery now has a reproducible repaired outcome tape and an explicit temporal coverage boundary. Generating more historical scores against unavailable current typed warnings would add no valid evidence. Preserve the failed audit, keep the modern single-control power limitation visible, and use prospective collection for the primary typed claim. CLAIM_LEVEL=HYPOTHESIS; LIVE_EXIT_RULE=NONE.
