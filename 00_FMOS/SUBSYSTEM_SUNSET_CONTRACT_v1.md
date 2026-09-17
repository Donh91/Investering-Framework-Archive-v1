# SUBSYSTEM SUNSET CONTRACT v1

Status: NORMATIVE FOR NEW PERSISTENT SUBSYSTEMS AFTER MERGE
Owner: FMOS architecture governance
Authority: Architecture / complexity governance only
Market authority: NONE
Portfolio authority: NONE
Scientific authority: NONE

## Purpose

Prevent automation-shaped complexity from accumulating without evidence that it changes a useful decision or removes a real operational burden.

This contract does **not** create a new registry, supervisor, dashboard, scheduler or approval service. The required declaration lives inside the new subsystem's existing owner contract or manifest.

## Scope

This contract applies prospectively to a **new persistent subsystem** created after this contract is merged, including a new:

- long-lived agent or specialist role;
- controller, supervisor, router or adjudicator;
- scheduled or continuously event-driven workflow that introduces a new durable responsibility;
- persistent research/learning/memory subsystem;
- durable queue whose lifecycle is not already owned by an existing subsystem.

It does not apply to:

- one-shot migrations or bounded recovery workflows with an explicit end;
- tests, fixtures, transport artifacts or views over already-owned state;
- a small change inside an existing owner that does not create a new durable responsibility;
- existing subsystems solely because this contract was introduced.

An existing subsystem becomes subject to this contract only when a later change materially expands it into a new durable responsibility.

## Required birth declaration

Before a scoped new subsystem can be treated as persistent architecture, its existing owner contract or manifest MUST declare all of the following:

1. `expected_decision_impact`
   - the concrete decision, transition or manual burden the subsystem is expected to change;
   - "improves intelligence" or "adds observability" is insufficient without an observable downstream effect.

2. `evaluation_horizon`
   - the date, observation count or bounded period after which incremental value can be judged;
   - the horizon must be prospective and measurable.

3. `kill_criterion`
   - the condition under which the subsystem is removed, retired, merged into an existing owner or reduced to a non-persistent tool;
   - the criterion must be decidable from evidence available at the evaluation horizon.

4. `existing_owner_overlap`
   - the existing owner(s) that could already perform all or part of the responsibility;
   - if overlap is non-zero, the declaration must explain why extension/merge is insufficient.

5. `complexity_budget`
   - the new persistent moving parts introduced: schedules, queues, state, model calls, credentials, write authorities and maintenance surfaces;
   - `NONE` is valid and preferred when the subsystem is only a deterministic extension of an existing owner.

## Default decision rule

At the evaluation horizon:

- demonstrated incremental decision or operational value -> KEEP or NARROW;
- useful capability but duplicated ownership -> MERGE INTO EXISTING OWNER;
- no demonstrated incremental value and no independent safety requirement -> RETIRE;
- evidence unavailable because the expected consumer was never reached -> fix the consumer edge first, then evaluate once; do not count missing consumption as positive value.

A subsystem MUST NOT survive solely because implementation effort has already been spent.

## Safety exception

A safety, compliance, provenance or fail-closed control may be retained without frequent decision changes when its value is risk containment rather than decision frequency.

The owner must still state:

- the failure class it prevents;
- why an existing control cannot provide equivalent containment;
- the condition that would make the separate subsystem unnecessary.

## Anti-patterns

The following are not valid reasons to create a new persistent subsystem:

- another subsystem exists and needs to be supervised;
- an AI model could perform the task;
- a report would be convenient;
- a queue exists but its executor/consumer is missing;
- a previous subsystem produced information that nobody consumed;
- provider or model diversity by itself.

Fix missing transitions and consumers before creating another owner.

## Minimal example

```yaml
sunset_contract:
  expected_decision_impact: "Reduce unresolved remediation tasks that require manual routing from CODEX_READY to an existing executor."
  evaluation_horizon: "20 eligible tasks or 30 days, whichever occurs first"
  kill_criterion: "Retire if it changes zero eligible task transitions or duplicates an existing owner."
  existing_owner_overlap:
    - "remediation maturation"
  complexity_budget:
    schedules: 0
    queues: 0
    model_calls: 0
    new_write_authority: false
```

The declaration belongs in the subsystem's own existing contract or manifest. Do not create a central sunset database merely to satisfy this contract.

## Success criterion for this governance rule

The rule succeeds when new persistent architecture can answer, at birth:

> What observable value must this component create, by when, and what happens if it does not?

If those questions cannot be answered, the default architectural action is **DO NOT BUILD A NEW SUBSYSTEM**.
