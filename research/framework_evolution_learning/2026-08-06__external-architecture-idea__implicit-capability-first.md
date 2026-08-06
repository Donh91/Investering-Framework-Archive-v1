# Framework Evolution Learning

## External architecture idea evaluated

**Date:** 2026-08-06  
**Case:** Prime Agent, persistent agent runtime and proposed Framework Harness  
**Classification:** Durable architecture learning  
**Status:** RATIFIED_AS_GOVERNANCE_LEARNING  
**Authority:** Advisory architecture principle, no market, model-weight or portfolio authority

## Why this record exists

This record is not primarily an archive of Prime Agent. It preserves a reusable lesson about how the framework should evaluate future external architecture ideas, especially ideas presented as a missing engine, runtime, memory layer, planner, swarm, orchestration system or agent framework.

The external idea initially appeared to expose a major architectural gap: the absence of a persistent, model-independent agent harness. A bounded internal candidate was drafted and sent through external red-team review. The review did not validate the need for a new architecture layer. Instead, it found that most proposed capabilities already existed in distributed form across the framework's current execution and governance stack.

The review also identified concrete defects in the existing execution chain. This changed the priority from adding a new layer to repairing and consolidating existing mechanisms.

## Observed development mechanism

The framework demonstrated the following development pattern in practice:

1. An external idea is introduced.
2. Its claimed capability is translated into a bounded internal candidate.
3. Existing repository capabilities are searched for before assuming a gap.
4. The candidate is exposed to adversarial or external review.
5. Concrete defects in the active execution chain take priority over new abstraction.
6. Promotion is blocked when evidence, tests or receipts are missing.
7. Useful principles are retained even when the proposed implementation is rejected or deferred.

This mechanism functioned without a central autonomous superagent. It emerged from the combination of task boundaries, context routing, shadow execution, receipts, ledgers, experiment lifecycle, remediation maturation, handoffs, promotion gates and external falsification.

## Core conclusion

A large external idea can look like missing functionality even when the framework already possesses the same capability implicitly and in distributed form.

The preferred response is therefore not to create a new engine immediately. The framework should first determine whether the capability can be:

- identified in existing components,
- consolidated,
- made deterministic,
- made executable rather than documentation-only,
- given explicit receipts and validation,
- and improved through existing remediation or experiment lanes.

A new architecture layer is justified only when the required capability cannot be expressed or enforced through the existing control plane without harmful coupling or complexity.

## Implicit Capability First Principle

Before proposing or implementing a new engine, manager, runtime, memory system, planner, swarm, harness or orchestration layer, the framework must attempt to prove that the desired capability is not already present across existing components.

The evaluation must answer:

1. Which existing components already perform parts of the capability?
2. Are the apparent gaps caused by missing implementation, weak enforcement, stale wiring, missing rows or poor observability rather than missing architecture?
3. Can the capability be consolidated without adding a new authority surface?
4. Does the proposed layer reduce complexity and failure risk, or mainly rename and duplicate existing functions?
5. Is there production evidence that the new layer solves a real recurring problem?

If the capability already exists implicitly, the default action is:

```text
REPAIR OR CONSOLIDATE EXISTING CAPABILITY
```

not:

```text
CREATE NEW ENGINE
```

## Promotion rule for future external ideas

A new architecture proposal should not advance beyond research or shadow-candidate status unless all of the following are satisfied:

- a capability-overlap map has been produced,
- current implementation defects have been separated from genuine architecture gaps,
- the proposal has a smaller and clearer authority surface than the status quo,
- at least one observed production-shaped failure cannot be solved cleanly through existing mechanisms,
- adversarial tests are defined,
- success and terminal failure can be receipted,
- rollback and kill criteria exist,
- and the proposal does not rely on benchmark hype or documentation-only controls.

## Case-specific conclusion

The Prime Agent case produced a useful but narrower conclusion than the external marketing suggested:

- persistent asynchronous process management may be useful later,
- scalable deep recursive agency was not demonstrated,
- a generic resident agent runtime was not a current first-priority need,
- the framework already had an implicit execution harness,
- the immediate value was found in repairing forecast-unit semantics, idempotency and terminal receipts,
- and the new harness proposal was correctly blocked from promotion without operational evidence.

Prime Agent remains a reference implementation candidate, not a selected platform or dependency.

## Guidance for future agents

When a future external idea appears to solve a major framework weakness:

1. Do not reject it reflexively.
2. Do not adopt its terminology as proof of a missing layer.
3. Map the claimed capability to existing framework components.
4. Search for active defects that may be creating the appearance of an architecture gap.
5. Use external review to falsify both the new idea and the current implementation.
6. Preserve reusable principles, even if the product or architecture proposal is rejected.
7. Prefer fewer engines, stronger contracts, real rows and verifiable receipts.

## Revisit conditions

This conclusion should be revisited if one or more of the following become true:

- repeated cross-run context loss remains unresolved after existing handoff and pointer mechanisms are correctly enforced,
- long-running work repeatedly fails because stateless GitHub execution cannot resume safely,
- bounded specialist workers produce enough real rows to demonstrate a need for stronger runtime isolation,
- multiple runtime providers must be supported through a stable adapter boundary,
- or a persistent runtime demonstrates materially better reliability under the framework's own adversarial tests.

Until then, the framework should treat its current distributed control plane as the primary harness and improve it incrementally through existing learning, remediation and promotion mechanisms.
