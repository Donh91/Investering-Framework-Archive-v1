# S1 Release Control · Agent-first consumer contract v1

**Authority:** ADVISORY READ-ONLY DERIVATIVE, not a source of truth, prompt replacement, scheduler, release permission, queue owner, formal reviewer or agent identity. Original S1 #1156 retains owner authority. Canonical AGENTS.md and source-specific source, governance, billing, recovery and permission contracts always take precedence.

## Precise entrypoints

- Source metadata: `node tools/s1-release-control/agent-context-v1.mjs --stdout`, contract `S1_AGENT_OPERATIONS_CONTEXT_v1`.
- **Prioritized agent brief:** `node tools/s1-release-control/agent-brief-v1.mjs --stdout`, contract `S1_AGENT_OPERATIONS_BRIEF_v1`, checked by `schemas/agent-brief-v1.schema.json` and negative tests. This is a bounded summary of original-source hints, not a new canonical queue.
- Public GitHub PR projection: `node tools/s1-release-control/projection-v1.mjs --stdout`, contract `S1_RELEASE_PROJECTION_v1`.
- Shared human/machine fail-closed rules: `tools/s1-release-control/release-core.js`.
- Positive, negative, mutation and source-bound tests: `test-static.mjs`, `test-projection-v1.mjs`, `test-agent-context-v1.mjs`.
- To verify an exported brief, run `node tools/s1-release-control/verify-agent-brief-v1.mjs ARTIFACT.json EXACT_PR_HEAD_SHA`. Its bounded, deterministic proof checks source SHA bindings, original read-only controls and a maximum 90-minute observation age. `ADVISORY_SOURCE_IDENTITIES_VERIFIED` **does not** mean current main was reread or that any original action is authorized. Tests deliberately reject a historical artifact replay, future timestamp, stale review-style claim and false S1/Grok authority.
- These scripts execute only on an existing authorized runtime when called, with no cron, additional supervisor, new credential, paid API or model dispatch. They use **anonymous public GET**. A local run is not evidence of unattended S1 operation.

## Strict read and decision sequence

1. Confirm current canonical `AGENTS.md`, public/restricted boundary, original S1 mission and current source authority.
2. Run `agent-context-v1.mjs` when a public system overview is necessary. Inspect `main_preflight_sha`, `main_final_sha`, every source blob SHA, source digest, status, clock and `partial`. Any unknown or invalidation stays UNOBSERVED.
3. Use the read-only agent brief to locate original owner and original SHA-bound source, then read `LATEST_CODEX_READY_TASKS.json` as the **sole original READY authority** if Codex work is relevant. Execution-state is observability only. The packet's small `task_refs` are bounded pointers, not new work orders or permissions.
4. Run `projection-v1.mjs` only where current public PR evidence improves a specific original decision. Even `ci_observation.status=PROVEN` means **some exact-head PR-associated runs are successful**, not required-check completeness, review authority, independence, billing, restore or merge permission. Unknown and partial sources forbid PASS.
5. Select up to three legitimate original PRs for the existing S1 tick, subject to existing policies and original owner contracts. Preserve Monday 09:30–10:30 Europe/Copenhagen READ-ONLY. Do not promote queue_plan to a job queue.
6. Re-read native HEAD, main, real platform rules and exact mandatory CI/reviews. HIGH_IMPACT remains blocked without independent source-bound recovery/custody, actual separate release assessment and destructive-authority separation. The cockpit never signs off.
7. Credit actual completion only after native original merge and current main readback, then separately required natural Pages/producer/consumer result. A manual owner-directed merge is INTERACTIVE_OWNER, not DIRECT_SCHEDULED S1.

## Actor-specific value

**S1:** Use exact source gaps and original Codex/repair pointers to avoid rediscovery; distinguish true external blocker from eligible independent safe work. No second S1 task. For duplicate/stale entries, match original signatures, not title guesses. Record verified action on #1156 and original owner, never mutate generated LATEST pointers.

**Strategist:** Correlate `operations.original_required_actions` and `remediation.summary` with original source SHA paths. Recommend a root-cause repair with measurable downstream unlock. Do not invent a signal, merge disposition or a new authoritative queue.

**Codex:** Treat `codex_ready.summary.task_refs` as browsing hints only, not task dispatch. Resolve each exact original candidate and its fresh preflight command, allowed-change scope and forbidden changes in canonical intake. Never self-declare READY, run paid models from the website or bypass a PR review gate.

**Grok Bridge:** Independently audit the public source and code at exact PR HEAD, and use Bridge's **existing restricted advisory owner** for its own reports. A public projection must keep Bridge private details `UNOBSERVED` until an authenticated original Bridge receipt is available. Grok feedback is advisory, not `APPROVED` in GitHub, not release authority and not a second reviewer identity.

**Research Lab:** Apply falsifiers and source/clock quality checks to any release projection claim. The 8-track Research Parallel Lanes source ledger is an evidence coordination artifact, not evidence of eight agents or live AI workloads.

## Negative contract

Disallow: synthetic evidence; `UNKNOWN` upgraded to `PROVEN`; stale main/head/review/check; incomplete pagination treated as complete; hidden private source fetch; recovery on a different release; billing override; automatic model expenditure; self-approval; direct main writes; new GitHub identity; duplicate S1 scheduler; false natural S1 closure; Cycle Navigator Pages coupling.

Do not use the cockpit as a public proxy for private `Donh91/secrets`, Bridge or Alpha Lab data. Public records may expose only previously authorized public metadata. The canonical restricted-plane routing remains unmodified.

## Verification and source identity

All positive local tests and actual Actions runs must be tied to the **current** PR exact HEAD. A passing run for an earlier HEAD is historical. The existing original PR #1996 remains the code owner; the original S1 issue #1156 remains the workflow owner. GitHub read-only PR comments/Bridge advisory notices are discovery aids, not native execution receipts.

A separate public Pages repository is required for a genuinely distinct GitHub Pages product URL. None is asserted as created or deployed until actual native repo/main/Pages/CDN readback. S1 browser tests operate on standalone `tools/s1-release-control` without invoking CN.
