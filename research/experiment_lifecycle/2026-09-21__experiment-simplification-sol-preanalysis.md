# Experiment Simplification Review - Sol Pre-analysis 2026-09-21

Status: READ_ONLY_PREANALYSIS
Owner: existing Experiment Lifecycle / T03
Authority: evidence compression only, no merge/retire/promotion/weight authority

## Fresh-main correction

The original T03 finding was frozen when the registry had 153 candidates. Fresh main now reports **366 candidates** at `2026-09-20T23:23:49Z`.

Current lifecycle counts:
- INCUBATING 272
- MATURED_INCONCLUSIVE 32
- MATURED_SUPPORTED 13
- MATURED_NOT_SUPPORTED 6
- WAITING_FOR_MAPPING 24
- WAITING_FOR_DATA 7
- TARGET_UNIT_QUARANTINED 8
- WAITING_FOR_MATURITY 2
- PROPOSED 2

Admission surface:
- QUALIFIED_FOR_FORWARD_TEST 184
- SEMANTIC_DUPLICATE_KEEP_SHADOW 173
- TARGET_UNIT_QUARANTINED 8
- WAITING_FOR_MAPPING 1

## Deterministic evidence already visible

There are **39 semantic_fingerprint groups with more than one row**. This is direct registry evidence that compression review is materially more important now than when T03 was created.

Largest exact-fingerprint families include:
- `a4d539...7605b`: 24 WAITING_FOR_MAPPING rows across legacy sensor-pair titles.
- `db632e...fcc17`: 18 BTC mark-price DOWN rows spanning `derivatives`, `market_metrics.derivatives`, `latest_capture.derivatives`, `latest_capture.market_metrics.derivatives`, and `market.derivatives` namespace forms.
- `6f6f98...ba1f`: 17 BTC mark-price DOWN rows.
- `393008...36fb2`: 15 BTC mark-price DOWN rows, including INCUBATING and MATURED_NOT_SUPPORTED states.
- `d15407...26da5`: 13 ETH mark-price DOWN rows.
- `d478d8...5362cf`: 12 BTC mark-price DOWN rows.
- `f99fd8...f4e10`: 10 ETH mark-price DOWN rows.
- `18607b...7fda`: 9 ETH mark-price DOWN rows.
- `1a7adb...f28b`: 9 BTC mark-price DOWN rows, including INCUBATING and MATURED_SUPPORTED states.
- `fe8ccd...0d745`: 8 ETH mark-price DOWN rows, including INCUBATING and MATURED_SUPPORTED states.

Fresh main also contains **233 candidates with >=20 observations and zero matured outcomes**. This is a triage flag only, not a retirement verdict.

## Important implementation correction

The reusable helper should use the registry's existing `semantic_fingerprint` as the first exact grouping key before attempting any path-alias normalization. A matching fingerprint is stronger evidence than title similarity.

However, identical fingerprints can span distinct displayed titles and even different lifecycle states. Therefore the helper must not auto-merge. It should emit review clusters with exact candidate IDs and preserve:
- candidate kind
- lifecycle state
- scientific admission status
- observation count
- matured outcome count
- title/path provenance
- fingerprint
- forecast IDs / outcome availability

Path normalization should be a second diagnostic layer used to expose namespace aliases, not an identity override.

## Recommended deterministic review labels

- KEEP - no material duplication flag or distinct decision hypothesis is documented
- MERGE_REVIEW - exact fingerprint or canonical alias family suggests redundant identities, governance decision required
- RETIRE_REVIEW - only when a weaker/superseded variant has explicit evidence and no unique consumer path, governance decision required
- WAIT_FOR_DATA - preserve current dependency state
- WAIT_FOR_MAPPING - preserve current dependency state
- NEEDS_MORE_OUTCOMES - high observation volume but insufficient matured outcomes

No label changes lifecycle state.

## Priority fixtures for Codex

1. Exact fingerprint duplicate fixture - `db632e...fcc17`, all 18 IDs must remain individually traceable.
2. Same fingerprint, mixed lifecycle fixture - `393008...36fb2`, must not erase MATURED_NOT_SUPPORTED evidence.
3. Same fingerprint, supported sibling fixture - `1a7adb...f28b` and `fe8ccd...0d745`, supported evidence must not auto-retire siblings.
4. Legacy mapping fixture - `a4d539...7605b`, WAITING_FOR_MAPPING must not become RETIRE_REVIEW merely because fingerprint is shared.
5. High-observation zero-outcome fixture - flag NEEDS_MORE_OUTCOMES or existing dependency state, never infer failure from missing outcomes.
6. Distinct hypotheses sharing a metric/path fixture - must remain separate unless fingerprint/contract evidence supports a review relationship.

## Codex work remaining

Codex does **not** need to rediscover the problem or invent clustering semantics. Remaining work is mechanical:
1. implement a read-only helper over `LATEST_EXPERIMENT_REGISTRY.json`;
2. emit deterministic cluster JSON/readout using the frozen labels;
3. add the six fixtures above plus no-mutation tests;
4. prove no candidate/history/weight/state mutation.

This pre-analysis does not mark the candidate resolved. The reusable deterministic helper and tests are still required by the existing T03 acceptance gate.
