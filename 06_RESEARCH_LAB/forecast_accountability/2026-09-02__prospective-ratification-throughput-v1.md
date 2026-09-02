# Prospective Forecast Ratification Throughput v1

Date: 2026-09-02
Status: READY_FOR_MERGE_AFTER_EXTERNAL_RED_TEAM_REMEDIATION
Authority: research / learning only

## Purpose

Close the API-agent owner-ratification throughput gap prospectively without auto-ratification, hindsight, historical rewrites, portfolio authority or a forecasting-skill claim.

This document applies to the `API_AGENT_OWNER_RATIFICATION` forecast family. Separately governed automated experiment forecasts remain a distinct shadow/experimental evidence class.

## Prospective cutover

Hard cutover:

`4057fde279ed0d8eea2df07da10543bda38ee8f8`

Cutover time: `2026-09-02T09:56:53Z`.

Candidates created before this cutover are permanently hindsight-ineligible. Legacy divergent duplicate IDs are retained as archive evidence without choosing a preferred historical variant. Any post-cutover duplicate candidate ID is owner-ineligible and quarantined.

## Owner decision lifecycle

For post-cutover candidates:

1. materialize immutable `FORECAST_CANDIDATE_v1`;
2. process any already-recorded owner decision packet;
3. build an outcome-free `FORECAST_RATIFICATION_QUEUE_v1` for candidates still needing a decision;
4. owner reviews only the queue and candidate record;
5. owner records one `FORECAST_RATIFICATION_PACKET_v2` with `RATIFY` or `REJECT`;
6. processor verifies candidate hash, candidate Git first-add content/time, decision time, packet Git first-add content/time and outcome-blind scope;
7. `REJECT` becomes append-only terminal state;
8. no decision within the SLA becomes `EXPIRED_NO_OWNER_DECISION`;
9. `RATIFY` freezes at owner decision time using a bounded immutable baseline;
10. supported price forecasts receive exact-target-time settlement.

Decision SLA is 60 minutes from candidate creation. Candidate and packet recording tolerances are 15 minutes. Workflow execution time never becomes forecast freeze time.

## Outcome-blind owner surface

Every queue row declares `outcome_data_included=false`.

Every valid owner packet must declare:

- `outcome_blind=true`;
- `decision_basis_scope=[RATIFICATION_QUEUE,CANDIDATE_RECORD]`;
- `outcome_paths_read=[]`;
- `self_promotion_allowed=false`.

The processor has no outcome-root input.

## Terminal integrity

Prospective terminal records are append-only and self-hashed. Candidate, ratification packet and prospective terminal content are bound to Git history so a later content mutation or terminal deletion cannot inherit an earlier valid timestamp and resurrect a rejected/expired candidate.

Terminal dispositions include:

- `LEGACY_PRE_CUTOVER_HINDSIGHT_INELIGIBLE`
- `LEGACY_PRE_CUTOVER_DIVERGENT_DUPLICATE_HINDSIGHT_INELIGIBLE`
- `POST_CUTOVER_CANDIDATE_STRUCTURE_QUARANTINED`
- `EXPIRED_NO_OWNER_DECISION`
- `REJECTED_BY_OWNER`
- `RATIFIED_AND_FROZEN`

Malformed/duplicate IDs are fail-closed per candidate without blocking unrelated candidates or later learning stages.

## Baseline / start-value integrity

Independent Claude/Cowork red-team reproduced a P0 in the pre-remediation branch: baseline selection could search metric history backwards after schema drift and freeze an old price as a new forecast start value while the workflow still returned PASS.

The remediated contract is capture-first:

1. choose the newest immutable archived capture timestamp at or before the owner decision;
2. that capture must be no more than 60 minutes old;
3. the requested metric must resolve in that freshest capture;
4. never search older captures merely because an obsolete metric path used to exist there;
5. conflicting values at the newest timestamp fail closed.

Known supported price wrapper aliases are canonicalised to the declared price family while the authored metric path is retained for provenance. This prevents an alias spelling from silently bypassing exact settlement.

## Exact settlement separation

A ratified supported price forecast freezes with:

- `frozen_at_utc = decision_at_utc`;
- `outcome_due_utc = decision_at_utc + frozen horizon`;
- candidate and ratification hashes;
- baseline evidence hash and observed time;
- `FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1`;
- `FROZEN_AT_RATIFICATION_DECISION_PROSPECTIVE_ONLY`.

Exact forecasts are physically excluded from the legacy Daily Anchor maturation subset.

## Forecast evidence-class boundary

The framework has more than one legitimate forecast producer. Owner ratification is therefore not asserted framework-wide.

The shared evidence-class contract distinguishes:

- `API_AGENT_OWNER_RATIFIED_PROSPECTIVE_v1`
- `AUTOMATED_SCIENTIFIC_EXPERIMENT_SHADOW_v1`
- `LEGACY_OR_UNCLASSIFIED_FORECAST`

Cross-class pooling raises `CROSS_EVIDENCE_CLASS_POOLING_FORBIDDEN`. Legacy/unclassified rows receive no scientific pool compatibility key.

This class key only establishes governance compatibility. It does **not** establish settlement eligibility, independent replication, calibration quality, effective N or forecast skill.

The live repository CI audit checks the API-agent frozen root and the framework-memory automated experiment root for conflicting class provenance. Separately governed PDLT prospective production is already frozen on current main under `PDLT_METHODS_FROZEN_NO_ADMISSIBLE_PROSPECTIVE_RUNTIME`.

## Independent Claude/Cowork red-team closure

Pre-remediation verdict: `BLOCKED_P0 / REMEDIATE_THEN_MERGE`.

Material findings:

- **F-01 P0 — stale baseline fallback:** REMEDIATED with freshest-capture + <=60m fail-closed selection and regression.
- **F-02 P1 — terminal deletion / packet mutation resurrection:** REMEDIATED with Git first-add content binding, terminal self-hash/history guard and regression.
- **F-03 P1 — one malformed/duplicate ID blocks nightly pipeline:** REMEDIATED with per-ID quarantine and non-blocking continuation.
- **F-04 P1 — exact-settlement alias/path drift:** REMEDIATED with supported canonical alias mapping plus authored-path provenance.
- **F-05 P1 — framework-wide owner-ratification claim too broad:** REMEDIATED by explicit family scope plus machine-readable non-poolable evidence classes.

The independent review did not evaluate forecast skill.

## Scientific boundary

This work does not:

- auto-ratify candidates;
- read outcomes during owner review;
- ratify historical backlog;
- rewrite historical forecasts or outcomes;
- alter forecast direction or thresholds;
- change portfolio actions;
- grant canonical/model-weight authority;
- promote replay rows into prospective effective N;
- prove forecast skill.

`FORECAST SKILL = UNPROVEN` remains authoritative until sufficient clean prospective evidence passes separate settlement, replication, independence, calibration and effective-N gates.

## Acceptance status

Final remediation code head before this documentation-only closure commit was:

`4b231cc7e1e9dedca3c2b88563690ce3ea2cf0e7`

It passed all nine relevant PR gates:

1. Forecast Ratification Throughput Gate
2. Forecast Exact Settlement Owner Gate
3. Forecast Settlement Accountability Gate
4. Forecast Outcome Supersession Gate
5. Continuity Learning Gate
6. Full Architecture 1-7 Gate
7. Data Architecture Gate
8. Storage Health Gate
9. Automation Production Health Gate

The Ratification Throughput gate includes behavioral regressions for F-01 through F-05, live forecast evidence-class boundary audit, existing exact-settlement guards, historical replay immutability and production workflow epistemic separation.

Merge still requires a fresh current-main overlap/readback and expected-head binding. No merge is considered complete until main is physically read back after GitHub reports the PR merged.
