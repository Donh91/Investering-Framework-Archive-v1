# ChatGPT five-slot automation governance | proposal v1 (2026-10-12)

**Status:** PROPOSED_DOC_ONLY until independently reviewed, merged and exact main bytes read back. This is a declarative operating guide, not a new scheduler, host API, GitHub Actions workflow, or authority to change a task. Canonical `AGENTS.md`, `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md`, private/public policy, and current owner records take precedence.

## Purpose
Five scarce ChatGPT automation slots should contain **five complementary user-facing jobs**, not five scanners, supervisors or redundant research engines. GitHub Actions remains deterministic runtime; ChatGPT automations read, route, synthesize and notify when delivery is actually possible. GitHub files may change independently from host automation state; neither proves the other.

## Permanent topology after temporary Master Audit handback
| Slot | ChatGPT task | Host ID | Domain and operating contract | Mode |
|---|---|---|---|---|
| S1 | Daglig Supervisor + Alpha Meta-Governor | `6a8d34563e988191b8bab0a779cdecac` | [supervisor](SUPERVISOR.md); current #1156, PR #1575 runbook after merge | PERMANENT / 07:45,14:45,22:45 |
| S2 | Ugentlig Master Monday + CN | `6a5515c4a5448191b3f6607fc568927f` | [weekly](MASTER_MONDAY.md) | PERMANENT / Monday 10:00 |
| S3 | Market Risk -> Portfolio Action | `6aae4e2aa6088191aacf5ec5caa6cb6c` | [risk](MARKET_RISK.md) | PERMANENT / hourly silent condition watch |
| S4 | Alpha Lab - Outcome Learning | `6acbfb98f548819181e783607e69f58f` | [outcomes](ALPHA_OUTCOMES.md), MAL PR #143 runbook after merge | PERMANENT / daily 22:15 |
| S5 | Project->CA Research Watch (Alpha Alerts gated) | `6ab38b90cfe4819193b0d9ccdf4e4e21` | [early-alpha](PROJECT_CA.md) | PERMANENT SUCCESSOR / hourly silent research condition watch; **currently disabled; Project→CA alerts forbidden under SHADOW_ONLY** |
| TEMP | Master Audit - Timevis mission | `6acb8ced403081919d5ecc197b186eac` | [temporary](TEMPORARY_MISSIONS.md) | ACTIVE LEASE of S5; must close and disable before S5 is enabled |

**Current truth:** host automation list/peek and actual GitHub main, not this table. If host schedule, enabled, notifications or prompt differ from this proposed plan, report DRIFT. Do not mutate automatically based on this document alone. Do not infer available task slots by counting files or stale task entries.

## Bootstrap contract for every active ChatGPT task
Keep an independent, short, *safety-complete* host prompt with:
1. Task identity + exact host ID and immutable purpose; current allowed schedule, output, notify policy.
2. Resolve fresh canonical GitHub main + AGENTS, then this README and exact role file; reject draft branch as production policy. Prefer latest accepted current owner contract if a doc is stale.
3. Fail-closed safety: no trades, no secret exposure, no invented Work/CI/notifications, no self-merge, no canonical market truth changes, no duplicate scanner/writer, no additional paid spend.
4. On missing/404/stale/conflicting doc: **keep last-known safe host behavior**, classify `RUNBOOK_UNAVAILABLE` or `RUNBOOK_DRIFT`, no broadening; escalate to supervisor only if material. Never halt essential risk alert solely because a non-authoritative README cannot be fetched: use the host prompt's unchanged canonical-read-only behavior.
5. If GitHub docs updated but host task not updated, **do not silently treat new capabilities or schedules as live**. Apply only compatible research detail; changes in task owner, schedule, authority, notification, cost or risk require explicit authorized host mutation plus independent readback.
6. On host prompt update but GitHub doc not merged: operate on explicit safe inline instructions, mark `DOC_PENDING`, no claim of completed GitHub adoption.
7. A GitHub comment or issue is never host-automation enable/disable evidence. Read host state after every task mutation.
8. Notification enabled != delivered. For user-critical risk alerts, if host notifications are off, record `DELIVERY_NOT_VERIFIED` and surface the setting problem without claiming a push.

## Reconciliation / failure matrix
| Event | Safe response |
|---|---|
| GitHub inaccessible or 404 | Stay on original task's safety-complete host instructions; `RUNBOOK_UNAVAILABLE`; no unauthorized expansion. |
| GitHub PR open but not merged | `DOC_PENDING`; do not adopt as authoritative. |
| GitHub main newer than host prompt | `RUNBOOK_DRIFT`; read role and current owners, apply only non-authority-bearing interpretation. Owner/schedule changes require verified host update. |
| Host task enabled but GitHub says retired | Host is actual active scheduler. Do not assume it stopped; alert supervisor and obtain explicit approved host change. |
| Host task disabled but GitHub says enabled | No runtime! Report `HOST_DISABLED`; do not claim monitoring. |
| Host task count 5/5 | Never create another. Use governed slot lease, or wait. |
| Source stale / missing | No new BUY/SELL/phase promotion; source-specific UNKNOWN. |
| Alert recipient notifications off | Cannot claim push; report `NOTIFICATION_DELIVERY_UNVERIFIED`. |
| Host task mutation succeeds, readback fails | `HOST_STATE_UNKNOWN`; no subsequent dependent activation. |
| Concurrent handovers | Single-flight lease ID + latest host state check; never overwrite an active newer mission. |

## Capacity and reporting
At most five simultaneously enabled tasks. No routine new tasks. Every task's cheap delta-first run uses existing GitHub Actions/source receipts. Quiet/no-change = silent. Do not promise background completion without a real scheduled task and host receipt. Risk task is an exceptional decision-delivery consumer, not a substitute market engine. Alpha discovery and alpha outcomes are distinct producer/measurement consumers; never count user-submitted token as machine first-seen.

## Acceptance checklist
- Governed documentation PR reviewed and merged, main-byte readback verified.
- Existing host tasks have safety-complete bootstraps, correct IDs, schedules and domain boundaries; notification settings checked.
- Master Audit terminal handover is verifiably received by #1156; exact audit task disabled; successor S5 enabled only if slot free and host/governance acceptance gates pass. Before enabling, harden successor host prompt to match #1087 SHADOW_ONLY / NO_USER_ALERTS; do not treat host activation as production bridge activation. A pending documentation PR is NOT a reason to keep a completed hourly audit alive: existing successor host prompt remains the safe fallback, with DOC_PENDING and no new README-derived authority.
- At least one normal natural run and GitHub/source readback for successor, with no false live-alert claim.
- Future temporary lease is rehearsed with host readback and restoration, no overlap and no lost permanent instructions.
