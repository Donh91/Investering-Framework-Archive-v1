# Test diagnosis and bounded remediation · 2026-11-06

PR #1963 original GitHub API Agent Gateway Gate run #42217506193 failed exactly one source-specific existing unittest: `tests.api_agent.test_research_lab_sol_max_owner_gate.ResearchLabMaxOwnerGateTests.test_new_single_active_queue_and_old_unknown_quarantine`.

Cause: the original unittest asserted hardcoded previous one-shot S1 MAX mission ID `S1-ELITE-REPAIR-TRIAGE-SOL61-MAX-20261106B` must remain the only `ACTIVE_RELEASED` mission forever. This contradicts existing `SHARED_SOL_MAX_CROSS_THREAD_RUNBOOK_V1` and the native queue's intended one-successor-per-call policy, even when old B has a verified original completed and one-way no-retry HOLD.

Minimal fix: replace ID-specific active pointer assertion with EXACTLY ONE active mission, equality with `queue.active_mission`, `new_paid_attempts_authorized=true`, max effort and packet owner/authority binding. Preserve the historic uncertain runs' no-repost checks, and explicitly reject reactivation of original B when an independent newer mission is active. Do not change production dispatch code, security/funding gates, queue reader or old paid receipts. Existing #1814 and #1823 changed-file sets do not include this test path.

Acceptance: previously failed native test and full API gateway workflow PASS on exact new HEAD, plus Data Architecture/Storage/Continuity; all prior owner consent, packet identity, single-use, unknown bill and no-Astra negative tests remain intact. A green test alone is not permission for paid POST; require qualified PR merge/main readback and separately authenticated owner trigger. No provider call from test.
