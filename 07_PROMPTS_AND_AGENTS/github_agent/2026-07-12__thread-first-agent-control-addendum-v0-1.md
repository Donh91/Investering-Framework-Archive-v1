# Thread-First Agent Control Addendum v0.1

**Dato:** 2026-07-12  
**Status:** CANONICAL_OPERATIONAL_ADDENDUM  
**Område:** user interface / agent orchestration / GitHub backend  
**Supersedes:** daily GitHub-Issue queue as the default user-facing control surface

## Decision

The user does not actively operate GitHub. GitHub remains an invisible backend used by ChatGPT for canonical memory, branches, validation, receipts, PRs and backup.

The default user interaction is:

```text
user request in an Investering ChatGPT thread
-> ChatGPT resolves canonical GitHub context
-> relevant existing Skills
-> safe repository work when required
-> result returned in ChatGPT
```

The user is not expected to create GitHub Issues, inspect branches or review PRs as a routine prerequisite.

## Agent Queue Runner status

```yaml
scheduled_agent_queue_runner: RETIRED_AS_DAILY_AUTOMATION
issue_command_bus: AVAILABLE_BUT_DORMANT
issue_creation_required_from_user: NO
control_loop_safety_components_retained: YES
```

Retained components:

- canonical-context routing;
- branch safety;
- deterministic or owner-defined verification;
- maximum-two-iteration bounded correction where applicable;
- run state and receipts;
- no direct main writes without governed merge;
- no self-promotion, threshold mutation or portfolio authority.

## Replacement automation

The released daily automation slot is assigned to `SENSOR_PAIR_DISCOVERY_LAB_V0_1`.

Its user-facing source is the highest-version, most recently used DATA PING project thread containing a complete user-supplied Custom GPT analysis. GitHub stores only durable source-derived handoffs, rows and evaluation state.

## Custom GPT boundary

A scheduled task must not claim to run a Custom GPT. It may only consume an analysis that the user has already posted in an accessible DATA PING thread, or an exact thread-derived handoff.

## Authority

This addendum changes workflow routing only. It creates no market logic, new Skill, live threshold, score, rule promotion or portfolio action.