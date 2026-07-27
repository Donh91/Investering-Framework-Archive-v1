# CHATGPT × CLAUDE DUAL-MODEL REPLICATION PROTOCOL v1

```yaml
protocol_id: DUAL_MODEL_REPLICATION_PROTOCOL_v1
status: FROZEN_BEFORE_RESULTS
models:
  lead_architect: GPT_5_6_THINKING
  independent_replication: CLAUDE_OPUS_5_MAX
result_sharing_before_submission: FORBIDDEN
```

## 1. Objective

Two capable models must independently implement and evaluate the same preregistered contracts. The purpose is not to vote. The purpose is to expose hidden assumptions, implementation drift, data-selection differences and interpretation bias.

## 2. Common immutable input bundle

Both models receive the same:

- Backtest Architecture Constitution;
- owner dataset registry;
- readiness gate;
- test matrix;
- graph-analysis specification;
- exact package filenames, byte counts and SHA-256 hashes;
- source and method registries;
- temporal and settlement contracts;
- frozen random seeds where applicable;
- artifact naming contract.

Neither model may substitute a source without recording a formal deviation.

## 3. Blindness rules

Before independent submission:

- ChatGPT may not see Claude's code, results or conclusion;
- Claude may not see ChatGPT's code, results or conclusion;
- neither may receive an executive summary produced by the other;
- both may see the same archived source audits and preregistration documents;
- both must treat package preliminary results as quarantined evidence, not truth.

## 4. Required execution order

1. Verify input identities.
2. Evaluate readiness gates independently.
3. Run engineering tests only.
4. Report every failed readiness gate.
5. Stop before economic tests unless all required gates pass.
6. Freeze test implementation hashes.
7. Execute the approved test sequence.
8. Run robustness and negative controls.
9. Build graph artifacts.
10. Produce a signed result manifest and conclusion package.

## 5. Required result package

Each model returns:

```text
MODEL_RESULT_PACKAGE/
  MANIFEST.json
  README.md
  input_hashes.json
  readiness_gate_results.json
  code/
  tests/
  logs/
  engineering_results/
  economic_results/
  graph_results/
  robustness_results/
  rejected_runs/
  conclusion.md
  CHECKSUMS.sha256
```

`rejected_runs/` is mandatory. Failed or contradictory runs must not disappear.

## 6. Machine result contract

Every test result contains:

- `test_id`;
- `implementation_id`;
- `code_hash`;
- owner dataset IDs and hashes;
- training, validation and holdout intervals;
- primary endpoint;
- sample count;
- independent episode count;
- missingness count;
- effect estimate;
- uncertainty interval;
- negative-control result;
- robustness status;
- multiple-testing family and adjusted status;
- conclusion class;
- deviations from preregistration;
- model interpretation separated from computed result.

## 7. Comparison protocol

After both packages are frozen, an adjudication run compares them in this order:

### A. Input parity

Did both use the same bytes and owner datasets?

### B. Sample parity

Did both generate the same eligible event timestamps and sample counts?

### C. Feature parity

Do row-level features match within declared tolerance?

### D. Outcome parity

Do forward labels, MFE, MAE and survival outcomes match?

### E. Statistical parity

Do point estimates and uncertainty differ only within expected numeric tolerance?

### F. Interpretation parity

Do both assign the same evidence class and promotion recommendation?

## 8. Difference taxonomy

Every disagreement receives exactly one primary class:

- `INPUT_IDENTITY_DIFFERENCE`;
- `OWNER_SELECTION_DIFFERENCE`;
- `TIME_ALIGNMENT_DIFFERENCE`;
- `EVENT_DEFINITION_DIFFERENCE`;
- `IMPLEMENTATION_BUG`;
- `NUMERIC_TOLERANCE`;
- `STATISTICAL_METHOD_DIFFERENCE`;
- `MISSING_DATA_POLICY_DIFFERENCE`;
- `INTERPRETATION_DIFFERENCE`;
- `UNRESOLVED`.

A disagreement cannot be resolved by averaging the results.

## 9. Resolution rules

- Byte or row parity disputes are resolved by direct artifact inspection.
- Temporal disputes are resolved by the frozen point-in-time contract.
- Owner disputes are resolved by the frozen owner registry.
- Statistical-method disputes require both methods to be reported and a preregistered adjudication rule.
- Interpretation disputes remain visible even if numerical results agree.
- Any unresolved load-bearing difference blocks promotion.

## 10. Independence scorecard

The adjudicator records:

- input parity;
- eligible-event parity;
- row-level feature parity;
- result parity;
- robustness parity;
- conclusion parity;
- number and severity of deviations;
- whether either model copied or depended on the other's implementation.

Final labels:

- `INDEPENDENT_REPLICATION_PASS`;
- `REPLICATION_PASS_WITH_NON_MATERIAL_DIFFERENCES`;
- `REPLICATION_CONFLICT_MATERIAL`;
- `REPLICATION_INVALID_INPUT_MISMATCH`;
- `REPLICATION_BLOCKED`.

## 11. Promotion boundary

Even `INDEPENDENT_REPLICATION_PASS` does not automatically change the framework. It only permits the result to enter governance review.

No portfolio action, threshold change, sensor promotion or state change is authorized by this protocol.
