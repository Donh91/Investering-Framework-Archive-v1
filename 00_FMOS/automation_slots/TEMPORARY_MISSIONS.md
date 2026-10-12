# Temporary missions and five-slot lease protocol
**Status:** PROPOSED; host task operations require actual host action/receipt. GitHub documentation is not a scheduling service.

## Master Audit currently leases S5
Temporary task ID `6acb8ced403081919d5ecc197b186eac`; permanent successor ID `6ab38b90cfe4819193b0d9ccdf4e4e21`. Audit is **not** permanent. It must finish or hand off unique verified work to permanent Supervisor #1156, with owner acceptance/next gates and no orphaned due P0. Do not confuse a green PR with terminal completion.

**Atomic-ish two-phase handback (host API is NOT atomic):**
1. Fresh-read host state, current GitHub main/governance, audit mission owner, #1156, exact active count and successor readiness. Confirm there is exactly one valid active audit and successor is disabled; any conflict => STOP / HOST_STATE_CONFLICT.
2. Prepare one durable, privacy-safe terminal handover to existing #1156, dedupe by mission ID+evidence fingerprint; verify comment/readback. Record verified completed vs delegated open gates, owner, source heads, and explicit noncompletion caveats.
3. Mark mission `HANDOFF_VERIFIED` only if #1156 has acknowledged/accepted the remaining responsibility in current evidence; posting a comment alone does not prove owner execution. If owner acceptance cannot be proven, classify `HANDOFF_PENDING`, continue temporary mission until a legitimate terminal contract is met.
4. **Disable the temporary task first**, using exact host ID and host update. **Read host state back**; must show audit disabled, and <=4 active tasks. If disable or readback fails, STOP: never enable successor, report `LEASE_RELEASE_UNVERIFIED`.
5. Enable the **preexisting disabled** Project->CA task after its host prompt is verified explicitly SHADOW_ONLY/NO_USER_ALERTS under #1087 and current owner governance is revalidated and host count allows it. A documentation PR not yet merged is DOC_PENDING, not a terminal handover blocker: use existing host prompt ONLY; do not adopt draft runbook authority. Read host state back; ensure five or fewer enabled, correct ID/schedule/notify policy and audit disabled. If enable fails, preserve the free slot and escalate; do not blindly re-enable audit or disable other permanent tasks.
6. On first due successor run, verify a real read-only producer receipt, correct source bindings and absence of unauthorized Project→CA user alerts; notification capability may be tested separately only for independently authorized alert products. Only then `SUCCESSOR_ACTIVE_VERIFIED`. Final user report must distinguish task enabled from operational source/delivery proof.

**Rollback:** If a post-activation P0 defect is discovered, fail closed on alert promotion and return to current owner; do not auto-reenable Master Audit. The Supervisor continues permanent coverage. If audit handoff fails before step 4, do not disable. If audit disabled and successor cannot be enabled, leave vacancy intentionally with `HANDOVER_BLOCKED`, and notify user; no speculative extra task.

## Future overnight jobs
- Choose a noncritical leasable slot **by explicit user-approved mission**, normally S5 (prelaunch radar) or S4 (research outcomes) depending on urgency; **never S3 risk, S2 Monday or S1 supervisor by default**. Avoid pausing S5 during a known launch window or S4 while a 24h/72h/7d checkpoint is due. If no safe slot, defer or execute in existing Supervisor window instead.
- Prefer repurposing the *same existing task ID* temporarily if safe and restorable, preserving its prior prompt/schedule/timing_mode/notifications/enabled settings as a host-visible verified snapshot and a privacy-safe reference in existing private owner evidence. **Never put private prompts, credentials or wallet details in public GitHub.**
- A temporary task uses a bounded absolute expiry, exact owner/mission, idempotent dedupe and no longer than necessary. For explicit one-off overnight user request, timebox until next morning and perform one terminal handoff before restore.
- When leasing a different task ID under 5/5, disable the chosen donor first and verify free slot before enabling temporary ID. Prefer one ID reused instead of extra create to avoid task quota. No parallel owner or double scanner.
- On terminal or expiry, stop heavy work, leave truthful owner handoff and then restore original task configuration with host readback. Expiry alone is NOT proof of mission success; unfinished work goes to Supervisor with `HANDOFF_PENDING`.
- If self-disable or restore action is unavailable in the execution environment, do not claim automatic restoration; report `HOST_MUTATION_UNAVAILABLE` and stop further dependent activation. A GitHub Action cannot silently mutate ChatGPT host tasks.
- Compare schedule DST in Europe/Copenhagen, guard single-flight host ID and one lease at a time, and never rely on a comment alone to verify state.

## Safety test cases
T1 audit disabled + successor enabled: pass only host readback + accepted owner handoff.
T2 GitHub docs pending: do not adopt or claim deployed.
T3 disable failed: no successor enable.
T4 successor enable failed: free slot + owner escalation, no blind retry loop.
T5 5/5 active: do not create/enable sixth.
T6 24h Alpha outcome due: don't borrow S4.
T7 risk warning pending: don't borrow S3.
T8 stale/unreadable host state: no mutation.
T9 notifications off: no claimed delivered push.
T10 temporary expiry with unfinished mission: handoff to Supervisor, not fake DONE.
T11 GitHub runbook/host prompt mismatch: fail closed on authority; report drift.
T12 simultaneous different missions: reject second lease unless first terminal verified.
