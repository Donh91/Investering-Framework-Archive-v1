# Framework-wide conclusion continuity contract — 2026-10-12

Status: PROPOSED OWNER INTEGRATION; NOT YET DEPLOYED.
Scope: all existing Archive, Meme-Alpha-Lab, Research Lab, Cycle Navigator, Compass, Edge, Auto Trading, Audit Bridge and supervisor-owned workflows.
Principle: The user should not have to remember to forward findings, conclusions or follow-up tasks between framework components.

## Mandatory terminal handoff
Every completed, failed, inconclusive or blocked run emits a source-addressed `FRAMEWORK_CONCLUSION_HANDOFF_V1` record with:
- `source_repo`, `source_run_id`, `source_commit_sha`, `source_evidence_paths`, `owner_issue`, `conclusion_status` (`PASS|FAIL|INCONCLUSIVE|DATA_BLOCKED|CANCELLED`), `conclusion`, `falsifiers`, `confidence_limits`, `lessons`, `downstream_consumers`, `next_action`, `next_action_owner`, `next_action_gate`, `needs_user_decision`, `authority_scope`, `budget_impact`, `dedupe_key`.
- Conclusion may be `NO_ACTION_JUSTIFIED`, with rationale. Missing evidence remains UNKNOWN.
- Never invent a downstream success; handoff is `PENDING` until the owner acknowledges it.

## Existing-owner lifecycle
`RUN_FINISHED -> CONCLUSION_FROZEN -> ROUTED_TO_OWNER -> OWNER_ACKNOWLEDGED -> ACTION_COMPLETED_OR_EXPLICITLY_BLOCKED -> VERIFIED -> CLOSED`.
Existing supervisor reconciles on its already scheduled/event-driven turn; no new schedule or duplicate scanner. A missing acknowledgement becomes `HANDOFF_STALLED` and is surfaced through existing supervisor health reporting, not silently dropped. A rerun with the same immutable dedupe key cannot create duplicate tasks. A new material source hash may reopen a previously closed conclusion.

## Routing
- Alpha Lab and Project→CA -> #1087 / #1340 / existing S1-S9 / #1339.
- Research/API experiments -> #1476 / #1512 and relevant scientific owner; one heavy lane, budget caps intact.
- Cycle Navigator / Compass / Master Monday -> existing canonical site/data owners; preserve frozen forecasts and release gates.
- Auto Trading -> existing research and #1557 denominator gate; never infer trading authorization.
- GitHub reliability/security, CI, backups, governance -> existing Supervisor and relevant issue owner.
- Cross-repo handoffs must link source and destination issue and evidence hash, not copy mutable claims as independent proof.

## Verification and anti-loop
1. Confirm source run and exact version exists; ignore unverified narrative.
2. Check dedupe, already-owned active PR/issue, downstream readiness and precedence; route to one existing owner.
3. Require an acknowledgement receipt and a next action or explicit reason not to act.
4. Confirm the action actually happened (commit, test, run, measured outcome), rather than marking a comment or PR draft as execution.
5. Record result and learnings, then create a new handoff only on a material state change; max one heavy research lane.
6. Reconcile stalled handoffs on existing supervisor cadence. Report concise exceptions to the user only when their decision, missing permissions, safety or money is required.

## Boundaries
No additional automation, no extra API spend, no Work-credit dependency, no autonomous trades, no silent production merges, no lowering source/prospective evidence gates, no claim of implementation until owner integration and tests verify end-to-end.
Existing workflow owners must implement idempotent consumption, state transitions, stall reporting, and tests in their own code. First acceptance fixture: Alpha R1 DATA_BLOCKED receipt from PR #1585 must be acknowledged by #1340, assigned to S1 for exact pool/source/route proof, and tracked to either a verified result or explicit block without user prompting.

## Acceptance test
Simulate PASS, FAIL, DATA_BLOCKED, duplicate replay, stale source, cross-repo owner unavailable, action completed, and no-action-justified. Confirm each gets exactly one appropriate owner disposition, no API call without budget gate, and no trading authority. Until verified, status remains PROPOSED, not ACTIVE.
