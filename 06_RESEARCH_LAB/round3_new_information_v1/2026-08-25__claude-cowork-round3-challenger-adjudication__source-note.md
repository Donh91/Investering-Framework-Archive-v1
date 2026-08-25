# Claude Cowork Round 3 Challenger Adjudication

**Dato:** 2026-08-25  
**Status:** SOURCE_NOTE / SUPERSEDED_CHALLENGER  
**Område:** Round 3 research lineage and external-review adjudication  
**Primary folder:** `06_RESEARCH_LAB/round3_new_information_v1/`  
**Depends on:** `README.md`, `BLUEPRINT_ACCEPTANCE_RECEIPT.json`, `PRIMARY_HYPOTHESIS_REGISTRY_v1.json`, `CHANGE_CONTROL_v1.json`

## Source identity

```yaml
source_filename: ROUND3_NEW_INFORMATION_DIMENSIONS_BLUEPRINT_2026-08-22.zip
source_sha256: 939e0b324e9542a7ac42d1f6254f6d264d0b846cf8fc02f9146a4249ff2add26
source_claimed_produced_utc: 2026-08-22
source_observed_delivery_utc: 2026-08-25
source_repo_baseline: d707dc33e101227abc2776d62765ee417317058a
source_member_count_claimed: 33
source_integrity_hash_check: PASS
source_portable_qa: FAIL_HARDCODED_CLAUDE_PATH
source_authority: CHALLENGER_SOURCE_CONTEXT_ONLY
```

This uploaded package is not the blueprint accepted by `BLUEPRINT_ACCEPTANCE_RECEIPT.json`. The accepted blueprint has filename `ROUND3_BLUEPRINT_CLAUDE_COWORK_OUTPUT.zip` and SHA-256 `340b9dea7a322626727a3059f47899ad2acfafaa7137fb19fd9b64f3163874ea`.

The challenger package therefore has no authority to replace, reopen or modify the frozen Round 3 contract.

## Durable findings retained

### 1. Availability-first source review

Historical coverage, timestamp semantics, publication lag, retrieval time, unit stability and point-in-time reconstructibility must be resolved before any feature or hypothesis is treated as executable.

This reinforces current source-contract and missingness discipline. It creates no new source and no change to the frozen primary family.

### 2. Funding semantic separation

Realized funding settlements and continuously observed premium-index measures are different information objects. A realized funding value must not be joined into observations before it was actually available.

The current `R3-H02-ETH-FUNDING-BURDEN` contract already preserves this learning by using realized funding events, an explicit availability rule and a prohibition on predicted or next funding.

### 3. Historical liquidation-feed caution

Public liquidation snapshot feeds that emit at most one selected event per symbol per fixed interval are intensity-dependent censored observations and are not complete liquidation-event histories.

This supports excluding such reconstructed histories from confirmatory historical use. It does not prove that every commercial aggregator has identical provenance or censoring.

### 4. Vintage and restatement discipline

Where a source can revise history, research should preserve retrieval vintage, release timestamp, revision amount and the exact information set available at decision time.

ALFRED-style vintages and periodic source-restatement measurement remain useful methodology candidates. They must attach to existing provenance and evidence-registry owners rather than create a new engine or duplicate research lane.

### 5. Reusable power planning

Power and multiplicity simulation before source-value inspection is valuable. Any implementation for current Round 3 must model the actual frozen design:

- paired event-control observations;
- synchronized chronological-block-preserving max-T;
- hypothesis-specific missingness and complete-pair coverage;
- at least 30 complete pairs per prospective block;
- family-wise power at paired concordance 0.67.

The challenger package's independent two-sample AUC simulation is retained only as a design prototype, not as a current threshold or power result.

## Findings not admitted

The following are explicitly rejected from current Round 3:

- replacement of the frozen four-hypothesis family with the challenger's eight-hypothesis historical family;
- execution of the proposed historical D0/D1 programme;
- use of AUC 0.711, 0.624 or approximately 0.60 as current Round 3 decision bars;
- opening or analyzing the proposed 2022-2024 holdout without a separately frozen versioned decision;
- treating failure to reject, or AUC below a fixed value, as automatic scientific falsification;
- treating zero survivors as a strong null without hypothesis-specific coverage and power;
- the claim that prospectively collected observations have zero multiplicity cost;
- use of the proposed positive/negative canary gates as written;
- the broad claim that every third-party liquidation aggregator necessarily inherits the public feed's exact censoring;
- the claim that recently expired Deribit instruments cannot be enumerated through the public API;
- any public storage of restricted provider values;
- any change to Round 3 hypotheses, features, windows, directions, controls, thresholds, multiplicity, analysis authorization or portfolio authority.

## QA and provenance qualification

The package member hashes verify successfully.

However, `CODE/qa_gate.py` and `CODE/build_manifest.py` hardcode:

```text
/home/claude/round3/out/ROUND3_BLUEPRINT
```

The recorded `21/21 PASS` is therefore a non-portable self-check, not an independently rerunnable scientific validation after normal extraction. The power script reproduces its quoted values under its own independent two-sample assumptions, but those assumptions do not match the current frozen paired design.

The package also declares `produced_utc: 2026-08-22` while the delivered ZIP and several members were observed on 2026-08-25. This is preserved as a provenance inconsistency, not interpreted as evidence of misconduct.

## Current operational effect

```yaml
round3_contract_changed: false
primary_hypotheses_changed: false
source_contracts_changed: false
collection_changed: false
analysis_authorized: false
outcome_scoring_authorized: false
historical_holdout_opened: false
new_test_created: false
new_engine_created: false
portfolio_authority_changed: false
```

## Final adjudication

```text
PACKAGE_CLASSIFICATION: SUPERSEDED_CHALLENGER_SOURCE_CONTEXT_ONLY
DURABLE_METHOD_LEARNING: RETAIN_BOUNDED
CURRENT_ROUND3_REPLACEMENT: REJECT
HISTORICAL_EXECUTION: REJECT
CURRENT_CONTRACT_EFFECT: NONE
```
