# Alpha Lab Shadow Proof v1 - import audit

Owner: #1087
Date: 2026-09-19
Status: TEST-ONLY, prospective evidence required.

## Source review

Claude Round-2 supplied `alpha_lab_shadow_v1.py`. It compiles cleanly, but MUST NOT be imported as production or credited as prospective proof without corrections.

### Accepted mechanisms

- explicit production User-Agent;
- factory + topic0 structural gate;
- persistent SQLite/WAL;
- `PRIMARY KEY(tx, log_index)` dedup;
- overlapping authority cursor with safe-head lag;
- simulated outage/backfill comparison;
- receipt.from collection;
- own-clock latency discipline;
- independent event-set comparison after capture.

### Blocking defects before evidence credit

1. **SHADOW-04 is retrospective as written.**
   `cmd_identity` reads the current head, backscans old blocks, selects the last N launches, then resolves them at `latest`. It does not freeze a spec before unknown future launches and therefore cannot satisfy the project's prospective-evidence rule.

2. **Historical-state leakage.**
   Symbol/name are queried at `latest`, not captured at first sight. This can differ from T0 and cannot support first-seen identity claims.

3. **Single-provider safe head.**
   `safe_head` takes three samples from one RPC. The Round-2 design requires multiple independent providers before an authority cursor can claim provider diversity.

4. **Cursor starts at current head.**
   Capture has no durable resume from a prior persisted cursor. It overwrites the cursor at startup, so restart-survival is not actually proven by this version.

5. **No raw receipt/T0 state persistence in capture.**
   The schema has `receipt_from` but capture does not fetch/store the receipt. Ephemeral T0 proof is therefore not implemented.

6. **No executable VERIFIED identity gate.**
   The harness measures attributes but does not prove zero false VERIFIED accepts because VERIFIED_CA is not implemented.

7. **No pre-registration artifact.**
   Spec hash, frozen assertion text, start time and future start block must be written before each credited run.

8. **Ground truth is not independent transport.**
   Re-querying the same RPC after the run is useful consistency evidence, but not independent-provider ground truth.

## Required corrected SHADOW-04

Before start:
- freeze `spec_sha256`, code SHA, chain, factory/topic0, provider set, future start block and exact assertions;
- start only from blocks/events not yet observed by the harness;
- capture raw log + receipt + first-seen metadata immediately;
- resolve ticker/name only as descriptive fields;
- record topic3 and receipt.from divergence/reuse without turning either into VERIFIED identity;
- use at least two transports/providers for event-set comparison;
- finish at >=1000 future launches;
- any run whose start block existed before freeze is RETROSPECTIVE and cannot satisfy a gate.

## SHADOW-07

Do not infer Δ_publish from arbitrary token websites after launch.

A credited row requires a first-party project surface frozen before T0, with CA absent/COMING_SOON at freeze. Poll the frozen surface prospectively and record:
- T0 canonical launch;
- Tpublish_first_seen on the frozen first-party surface;
- Δ_publish;
- Text from an independent external observer when available.

Rows discovered only after T0 are ineligible.

Kill question:
If verified first-party publication systematically occurs after the useful external-edge budget, stop optimizing VERIFIED-before-public launch detection and re-scope to candidate-grade or upstream provenance research.

## Evidence labels

`EXTERNAL_REVIEW_MEASURED`: Claude's Round-2 measurements.
`LOCAL_REPRODUCED`: reproduced independently by our machinery.
`PROSPECTIVE_PASS`: pre-registered future run passed.
`RETROSPECTIVE`: useful research only, never gate credit.
`NOT_RUN`: never PASS.

No capital or autonomous execution is authorized by this harness.
