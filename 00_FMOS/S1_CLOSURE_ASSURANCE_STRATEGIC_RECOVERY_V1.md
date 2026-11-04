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

## Permanent per-PR release disposition contract

For every owner-directed release preflight, the EXISTING S1/operator must apply the per-PR input/evidence contract and regression matrix in `00_FMOS/S1_V4_3_DIRECTOR_INTEGRATION.md`, section "2026-11-04 deterministic release dispositions". Use `scripts/governance/s1_release_evidence_classifier_v1.py` for a finite read-only classification of normalized native evidence; use `select_cases_isolated` for independent candidate selection when candidate telemetry may be malformed. Preserve the original strict `select_cases` API for existing strict callers.

Persist a material disposition through the existing #1156 receipt owner, with exact current HEAD/main/policy/source, reason, responsible owner, native evidence references and reactivation trigger. Suppress an unchanged fingerprint. After four genuine material treatments, retain the specific blocked disposition as terminal until a new material trigger; do not count ticks/comments as treatments. Revalidate every binding before merge and read back merge/main/blobs afterward. A local blocked candidate never consumes every independent queue slot.

These are permanent instructions for the existing release process once governed integration completes, not evidence that the saved Chat S1 task has been changed or has executed the new code. `READY_TO_MERGE` is an advisory classification, always with `authorized=false`; only existing authenticated owner authorization and actual platform/domain requirements can permit integration. Native Vault technical `release_permission=false` is immutable and is not itself an independent release assessment. The separate evidence-bound assessment, when genuinely available, belongs to the existing independent recovery authority. No self-attestation or new custodian is introduced.

If the helper cannot execute, report the exact local telemetry/tool limitation and apply the same existing native policy checks to independent candidates through the qualified operator. Do not fabricate an executed-helper receipt, treat unavailable telemetry as PASS, or invent a new global dependency on this module. Required high-impact recovery remains fail-closed for the affected candidate.

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
