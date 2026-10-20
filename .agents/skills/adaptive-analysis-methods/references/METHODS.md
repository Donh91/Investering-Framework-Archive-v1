# Six bounded analysis methods

Each method is a procedure, not an independent skill, model, agent or execution permission. Choose by the *binding uncertainty* and stop once it is resolved.

| Method | Use when | Required evidence / technique | Exit test |
|---|---|---|---|
| EXPERT_GAP | Brief omits a likely decisive expert question | Identify 1-3 omissions, compare with owner objective, ask only if permission or critical input missing | One falsifiable task refinement; resume task |
| EVIDENCE_RECONSTRUCTION | Claims rely on digests or conflicting chronology | Read original commits, immutable receipts, raw events and timestamps; reconstruct as-of order | Proven chain of custody or explicit UNKNOWN |
| ADVERSARIAL_FALSIFICATION | A claim of edge, correctness or readiness may be false | Baseline, strongest counterexample, negative controls, false-positive/negative costs; defer to existing red-team owner when authorized | Claim survives bounded falsifier or is downgraded |
| CAUSAL_ROOT_CAUSE | Repeated failure or ineffective patch | Reproduce, isolate first divergence, distinguish cause from symptom, verify causal intervention | Regression reproduces before and passes after |
| SCIENTIFIC_EXPERIMENT | A proposed improvement needs evidence | Pre-register hypothesis, prospective split, independent comparator, confounders, censoring, cost | Evaluability gate or defensible inconclusive result |
| MINIMAL_RESOLUTION | Work is stuck in review/PR churn | Identify exact blocker, smallest safe patch, tests, current PR head and owner, readback | Verified closure or precisely bounded blocker |

Selection examples:
- Alpha Lab prospective alpha audit: EVIDENCE_RECONSTRUCTION + SCIENTIFIC_EXPERIMENT.
- Task 2 forecast claims: ADVERSARIAL_FALSIFICATION + EVIDENCE_RECONSTRUCTION.
- Repeated CI/merge defect: CAUSAL_ROOT_CAUSE + MINIMAL_RESOLUTION.
- Clear one-line defect: L0, no method skill.
- Routine market status: L0, no method skill.

Do not turn a method into a new data source, metric, schema, or autonomous workflow.
