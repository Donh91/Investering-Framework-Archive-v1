# S1 Closure Assurance v1.0 + Strategic Opportunity Recovery

Status: DRAFT / GOVERNED REVIEW. Original owner: Archive #1156. This document and its schema are **non-executable**, do not alter S1's saved task, schedule, existing writer, authority, or any production routing.

## Existing source-first authority

Follow AGENTS.md, the operational cockpit read order, 00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md, current main, exact original owner issue/PR, receipts and platform rules. This contract is an *overlay* for the existing LATEST_REMEDIATION_QUEUE, LATEST_HANDOFF, CODEX_READY, incident and Strategist/Research Lab surfaces, **not** a new competing queue or writer. Private source evidence stays in its restricted plane. No automatic market promotion, trade, payment, Grok call, release, new scheduler or Vault recovery authority.

## Identity and deduplication

Key each case by (original repository, original issue/PR or approved proposal ID, original source fingerprint). Store one authoritative existing-owner URL. Match old proposals by hypothesis and source lineage, not titles alone. Current source evidence wins over historical notes. Existing Strategist LATEST proposals have dispatch_allowed=false; preserve advisory-only semantics and route via #1157/#1512 and their original domain owners.

## Lifecycle

DISCOVERED -> ACTIONABLE -> IN_PROGRESS -> VERIFICATION -> CLOSED_VERIFIED.
Research may enter READY_FOR_TEST -> IN_VALIDATION -> ADOPTED_VERIFIED or REJECTED_WITH_EVIDENCE.
A BLOCKED_WITH_TRIGGER is a *nonterminal monitored state*, requiring named trigger owner and falsifiable reactivation condition. PROCESS_STALLED requires evidence of repeated no-progress and a different bounded strategy, not another duplicate comment. SUPERSEDED_VERIFIED needs exact replacement proof. A closed PR is not proof that the original runtime defect is fixed.

Each material receipt must satisfy `schemas/S1_CLOSURE_ASSURANCE_V1.schema.json`. Schema checks are structural only; independent original SHA, source clocks, GitHub CI job steps, policy and consumer readback remain mandatory.

## S1 selection and fairness

At each **existing** S1 tick: cheap deltas for existing owners; select up to 3 actionable original candidates. Active P0 safety/recovery first, then independent ready fixes, then Strategist/Research Lab bounded falsification when capacity permits. A static external HOLD cannot monopolize all slots. Do not interpret a changed issue timestamp, a review comment, a Codex-ready label, or green observer workflow as engineering progress. Prefer verified code/tests/release/readback or concrete owner reactivation. No duplicate PR or competing HEAD writer.

A case with two failed *identical* repair attempts and no new evidence becomes PROCESS_STALLED, with explicit root-cause/falsifier and different next step. This is not a time-based permission to bypass release gates. No automatic retry storm.

## Evidence and closure

Record original issue, owner, fingerprint, last material action time, proof refs, next action, acceptance test and trigger. Genuine closure is a verified main merge + natural consumer/production proof, a documented scientific rejection, or verified supersession. External blockers remain visible and rechecked on trigger. Every claim is based on exact current receipts, not a narrative issue comment.

## Safe rollout

1. Audit current queue, Strategist proposals and existing S1 receipt patterns, dedupe without rewriting original data.
2. Validate positive and adversarial negative examples, including blocked-without-trigger, closure-without-proof, Strategist promotion authority, stale/duplicate evidence, and missing owner.
3. Obtain independent current-head review and CI. Only then consider an existing-owner implementation that consumes the receipt without introducing a second writer.
4. Pilot on Archive #1156, Alpha #120/#194/#77, CN/SITE and Vault access-blocked case. Never access Vault without authorized private credentials.
5. Observe seven natural days; measure unowned P0/P1, untriggered HOLD, qualified closures, time since material progress and proposal decisions. No fabricated success metric.

## Rollback

Before any subsequent production integration, record original main/HEAD/config blob SHAs, existing cadence, original queue and latest receipts. Release one bounded change at a time, with reviewed revert PR and natural post-change verification. A draft schema alone has no runtime effect.
