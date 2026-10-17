# Temporary missions and five-slot lease protocol
**Status:** PROPOSED; host task operations require actual host action/receipt. GitHub documentation is not a scheduling service.

## Master Audit / permanent S5 replacement, current user override (2026-10-13)

**Current observed host topology:** S1 Supervisor `6a8d34563e988191b8bab0a779cdecac`, S2 Master Monday `6a5515c4a5448191b3f6607fc568927f`, S3 Market Risk `6aae4e2aa6088191aacf5ec5caa6cb6c`, S4 Alpha Outcomes `6acbfb98f548819181e783607e69f58f`, new S5 Project->CA Research Watch `6ace25bde9e081918b3898007bb0f7ac` are the only intended enabled slots. Old S5 `6ab38b90cfe4819193b0d9ccdf4e4e21` disabled. Temporary Master Audit `6acb8ced403081919d5ecc197b186eac` remains DISABLED, PAUSED_BY_OWNER, NOT_DONE. Reconcile actual live host truth on each material run; this document is not an automation control API.

**User-authorized migration:** Disable old S5 first; host readback <=4 enabled; create one successor from an ordinary Chat conversation with a safety-complete SHADOW_ONLY prompt and hourly condition-watch; verify successor enabled, old disabled, Audit disabled and S1–S4 unchanged, <=5 enabled. This operation replaces S5, it does NOT certify an accepted Master Audit terminal handover or GitHub collector execution. No automatic research-to-production/BUY alert permission, no new scanner, no trading.

**CHAT_MODE_PROOF_PENDING:** The current ChatGPT task tool exposes title/prompt/cadence/enabled but no mode/model/Work-credit measurement. Normal Chat creation and a `CHAT ONLY` prompt are intent, not a verified host execution-mode or cost receipt. Never claim zero Work credits until the surface or run receipt explicitly proves it. Do not let the old Audit task's historical instructions toggle old S5 back on; current owner/user instructions and current host truth supersede that stale topology.

**Incomplete Audit:** Existing #1156 is still the sole permanent handover owner. Preserve open audit work, exact source/receipt and scientific gates. Neither this replacement nor enabled state means HANDOFF_VERIFIED. Keep Audit disabled unless expressly authorized by the user after a capacity and overlap check. Its legacy automatic reenable-old-S5 recipe is revoked by this owner override. Do not auto-start a second S5 or use a sixth task.

**Fail-closed reconciliation:** Old S5 reappears as enabled => HOST_STATE_CONFLICT; disable only under fresh user authorization or explicit current host owner mandate, never infer from GitHub text. New S5 missing or disabled => S5_NOT_RUNNING; do not claim monitoring. Work-mode or credit proof unavailable => HOST_EXECUTION_MODE_NOT_EXPOSED. Notifications off => NO_VERIFIED_PUSH. Unavailable or conflicting source => UNKNOWN/CONFLICTED. Route material problems to #1156, not new control planes.

**Historical audit terminal sequence:** Only for a separately user-approved future Audit resumption, complete or independently accept owner handover to #1156, verify exact evidence and host slot topology and stop the temporary Audit task. Do NOT reenable old S5, do NOT create another successor or disturb S1–S4/new S5. New task mutation requires a separate explicit owner decision.

## Future overnight jobs
- Choose a noncritical leasable slot **by explicit user-approved mission**, normally S5 (prelaunch radar) or S4 (research outcomes) depending on urgency; **never S3 risk, S2 Monday or S1 supervisor by default**. Avoid pausing S5 during a known launch window or S4 while a 24h/72h/7d checkpoint is due. If no safe slot, defer or execute in existing Supervisor window instead.
- Prefer repurposing the *same existing task ID* temporarily if safe and restorable, preserving its prior prompt/schedule/timing_mode/notifications/enabled settings as a host-visible verified snapshot and a privacy-safe reference in existing private owner evidence. **Never put private prompts, credentials or wallet details in public GitHub.**
- A temporary task uses a bounded absolute expiry, exact owner/mission, idempotent dedupe and no longer than necessary. For explicit one-off overnight user request, timebox until next morning and perform one terminal handoff before restore.
- When leasing a different task ID under 5/5, disable the chosen donor first and verify free slot before enabling temporary ID. Prefer one ID reused instead of extra create to avoid task quota. No parallel owner or double scanner.
- On terminal or expiry, stop heavy work, leave truthful owner handoff and then restore original task configuration with host readback. Expiry alone is NOT proof of mission success; unfinished work goes to Supervisor with `HANDOFF_PENDING`.
- If self-disable or restore action is unavailable in the execution environment, do not claim automatic restoration; report `HOST_MUTATION_UNAVAILABLE` and stop further dependent activation. A GitHub Action cannot silently mutate ChatGPT host tasks.
- Compare schedule DST in Europe/Copenhagen, guard single-flight host ID and one lease at a time, and never rely on a comment alone to verify state.

## Safety test cases
T1 audit disabled + user-authorized Chat-created S5 replacement enabled: pass HOST_TOPOLOGY_ONLY after host readback; Audit terminal handoff remains NOT_DONE separately.
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
