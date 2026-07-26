# ADR-FMOS-002 — Adopt FMOS v0.2 architecture

Date: 2026-07-26  
Decision: PROCEED_WITH_CHANGES and ratify the merged audit findings as the design basis for a preservation-first shadow build.

## Inputs

- FMOS v0.1 design package.
- ChatGPT external architecture audit, verdict PROCEED_WITH_CHANGES, 78%.
- Claude/Fable adversarial audit, verdict PROCEED_WITH_CHANGES, 82%.
- DATA PING V7 handover and current GitHub continuity state.

## Ratified changes

1. Knowledge time is mandatory and defines AS_OF.
2. Capture uses write-readback-ACK and explicit idempotency.
3. Privacy screening, secret scan and governed tombstones precede real raw capture.
4. Structured normalization is deterministic code; LLM extraction is A1 sidecar.
5. Schemas are hardened with enums, required guards, typed children and canonical hashing.
6. Evidence atoms are write primitives; Knowledge Objects are semantic projections.
7. Graph edges are separate append-only temporal records.
8. Root ancestry prevents circular/self evidence inflation.
9. Receipt state machine and one-repo system-of-record prevent split brain.
10. Weekly work is decomposed; Master Monday remains unchanged and is enhanced by bundles.
11. GitHub is machine memory and governance substrate, not a magical database or portfolio authority.
12. No existing owner artifact is deleted, reset or silently replaced.

## Non-decision

This ADR does not activate portfolio actions, change market state, alter forecast scores or implement owner adapters.
