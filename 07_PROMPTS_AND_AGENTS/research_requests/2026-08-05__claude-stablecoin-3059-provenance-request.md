# Claude Provenance Request — Stablecoin USD 305.9B

```yaml
request_id: TRR-CIRCLE-ARC-PROVENANCE-20260805-02
priority: P1_NARROW_SOURCE_PROVENANCE
parent_request: TRR-CIRCLE-ARC-20260805-01
trigger_validation: DP-STABLECOIN-VALIDATION-20260805-01
scope: ORIGINAL_305_9B_OBSERVATION_ONLY
framework_effect: NOT_ASSESSED_BY_RESEARCH_AGENT
canonical_effect: NONE
portfolio_effect: NONE
```

## Copy-ready prompt

```text
TARGETED PROVENANCE RECOVERY — TRR-CIRCLE-ARC-20260805-01 / STABLECOIN USD 305.9B

REQUEST ID
TRR-CIRCLE-ARC-PROVENANCE-20260805-02

PURPOSE
Recover or explicitly retract the exact source lineage behind your prior claim:

"Total stablecoin supply = USD 305.9B on 2026-08-05."

A separate DATA PING validation found DefiLlama's rendered public stablecoin market cap at USD 300.384B and identified the leading explanation as:

- totalCirculating.peggedUSD = nominal USD-pegged circulating supply;
- totalCirculatingUSD.peggedUSD = price-adjusted USD market value.

This explanation is structurally plausible but remains unproven because your original 305.9B raw source record was not preserved in the material returned to ChatGPT.

ROLE
Act only as Source-Provenance Recovery + Source-QA.
Do not broaden into stablecoin market research, Circle analysis, market interpretation, regime classification or portfolio advice.
Do not replace the original observation with a newly fetched value without clearly labeling it as a new observation.

REQUIRED ORIGINAL-RUN PROVENANCE
For the exact USD 305.9B value, provide:
1. exact endpoint URL;
2. exact query arguments;
3. HTTP retrieval timestamp UTC;
4. source/data timestamp UTC;
5. exact JSON field path;
6. raw terminal row or minimal raw source excerpt containing the value;
7. whether the field was `totalCirculating.peggedUSD`, `totalCirculatingUSD.peggedUSD`, or a locally computed sum;
8. exact peg-type universe;
9. asset membership or membership hash;
10. treatment of non-USD pegs;
11. treatment of bridged, canonical and third-party representations;
12. duplicate-removal rule;
13. price basis and off-peg treatment;
14. exact aggregation code or formula;
15. raw payload SHA-256;
16. transformed-result SHA-256, separately labeled if present;
17. whether the value was fetched once or reproduced twice.

MANDATORY FIELD-PATH TEST
Explicitly answer:

A. Was 305.9B read from `totalCirculating.peggedUSD`?
B. Was 305.9B read from `totalCirculatingUSD.peggedUSD`?
C. Was 305.9B computed by summing assets or chains?
D. Were all peg types or USD pegs only included?
E. Were chain balances summed in a way that could double-count bridged representations?

REPRODUCTION
Attempt two fresh reproductions of the original method, preserving both raw payload hashes and terminal rows.

- If both reproduce the original field definition within normal source-update tolerance, label `PROVENANCE_RECOVERED`.
- If the current endpoint differs because the source updated, show that the method and field path are still the same and label `METHOD_RECOVERED_VALUE_MOVED`.
- If the original raw lineage cannot be recovered, label `SOURCE_PROVENANCE_LOST`.
- If you determine the 305.9B value used the wrong field or universe, explicitly issue a correction or retraction. Do not preserve the number by approximation.

REQUIRED OUTPUT
1. One-line verdict.
2. Original-run provenance matrix.
3. Raw excerpt and hashes.
4. Exact field-path determination.
5. Peg-universe and duplicate audit.
6. Two-run reproduction table.
7. Correction/retraction statement if needed.
8. Main-thread reconciliation package.

MAIN-THREAD RECONCILIATION PACKAGE
Provide:
- item_id
- original_claim
- provenance_status
- exact_endpoint
- exact_arguments
- field_path
- source_timestamp
- retrieval_timestamp
- raw_value
- unit
- peg_universe
- duplicate_rule
- price_basis
- aggregation_formula
- raw_payload_sha256
- reproduction_1
- reproduction_2
- correction_or_retraction
- unresolved_dependencies
- canonical_effect_claimed: NONE
- portfolio_effect_claimed: NONE
- requires_main_thread_crosscheck: YES

FAIL-CLOSED RULE
If any of endpoint, field path, universe, timestamp or raw hash cannot be recovered, do not label the 305.9B value verified. Return `SOURCE_PROVENANCE_LOST` and recommend that ChatGPT retain the value in quarantine.

STOP CONDITION
Stop when the original 305.9B lineage is recovered or explicitly declared lost/retracted. Do not conduct wider research.
```
