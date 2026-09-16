# Skill validator fresh audit receipt

**Recorded:** 2026-09-13  
**Source main:** `8835fc97ddd4e064ee3be44af475241ea2082eb4`  
**Status:** VERIFIED_FINDING / NO_AUTHORITY_CHANGE  
**Owner:** existing skill architecture validator and Codex research intake

## Fresh finding

Current `scripts/agent_skills/validate_skill_architecture.py` still contains two reproduced structural validation defects:

1. The derived routing inventory is checked against a hardcoded `expected_count = 6` instead of reconciling the exact active skill set against canonical registry authority.
2. `allow_implicit_invocation` is compared through `bool(entry.get(...))`, so non-boolean JSON values such as the string `"false"` can be coerced instead of rejected by type.

This receipt intentionally does not import the stale operational state from PR #886. It preserves only the finding that remains true on the bound current-main commit.

## Safety boundary

The correct remediation is validator-only. It must not edit:

- canonical skill registry authority;
- derived routing metadata to make the test pass;
- skill bodies;
- frozen historical baselines;
- workflows, model routing, API budget, market gates or portfolio logic.

The validator should derive/reconcile the expected active inventory from canonical registry semantics and require a real JSON boolean for `allow_implicit_invocation`. A new or retired registered skill must not silently escape set reconciliation.

## Acceptance evidence

Positive controls:

- complete derived inventory matching canonical registered skill rows validates;
- real JSON booleans preserve current side-effect checks.

Negative controls:

- omitted canonical registered skill fails regardless of total count;
- string `"false"`, string `"true"`, integers and null fail boolean validation;
- registry, routing metadata, skill bodies and frozen baselines remain byte-unchanged.

## Authority

This is evidence and intake support only. It does not self-promote a remediation task, change skill authority, qualify runtime behavior, or authorize deployment. Existing Codex maturation and post-fix gates remain authoritative.
