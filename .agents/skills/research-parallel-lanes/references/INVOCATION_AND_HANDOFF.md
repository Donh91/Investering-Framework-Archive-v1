# Research Parallel Lanes, use in another chat and exact handoff

## Minimal owner invocation, Danish

> Kør **Research Parallel Lanes v1** fra `Donh91/Investering-Framework-Archive-v1/.agents/skills/research-parallel-lanes/SKILL.md` på **Task 2, issue #1596**. Arbejd i **6 uafhængige forskningsspor** fra samme tråd. Læs først eksisterende arkiver, resultater og ejere, fastfrys kilder, del kun reelt uafhængigt arbejde mellem eksisterende GitHub Actions-jobs eller autoriserede agenter, verificer resultaterne og lav fælles syntese. Genbrug Supervisor og Research Lab, ingen nye automations, ingen opdigtet parallel agentaktivitet, ingen real trading. Fuld mandat inden for gældende sikkerheds-, budget- og releasekrav.

## Tiny invocation, English

> **Use Research Parallel Lanes v1** for existing owner [issue/PR]. Run [N] independent falsifiable research tracks in the same thread, prefer verified concurrent read-only GitHub jobs where useful, existing authorized AI lanes only if actually callable, consolidate exact artifacts and scientific conclusions into the original owner. No new scheduler or trading authority.

## Practical modes

| Mode | Actually parallel? | AI agents? | Verification |
|---|---|---|---|
| Concurrent read-only tool calls inside one chat | Maybe, when underlying calls are truly concurrent | **No** | Source/tool IDs and readbacks |
| Two+ independent GitHub Actions jobs | Yes when start/end intervals overlap | **No** | Run ID, each job ID/started/completed/conclusion and artifact |
| Existing Research Lab/Strategist/Sol/Codex agents | Only if separately authorized agent runtime dispatch occurred | **Yes, conditional** | Native agent attempt, model, scope, cost and actual result receipts |
| Ten narrative headings in a chat | No execution proved | **No** | `PLANNED` only |

GitHub jobs can execute independently even though one chat is the coordinating place for the user to follow research and synthesis. A conversation alone cannot sustain autonomous future work after the present turn unless an existing authorized scheduled task or execution runner actually owns that work.

## Compact mission packet

```yaml
original_issue: <existing owner issue>
objective: <one evidence-backed decision question>
source_snapshot_sha: <40hex code/source binding>
first_known_and_eligibility: ORIGINAL_PIT | POSTHOC_TRUTH | UNKNOWN
lane_count: 2..10
max_concurrent_jobs: 2..4 by default
execution_mode: CHAT_TOOLS | GITHUB_ACTIONS_JOBS | AUTHORIZED_AI_RUNTIME | MIXED
lanes:
  - id: L01
    question: <different testable claim>
    baseline: <simple incumbent>
    falsifier: <what result disproves candidate>
    source_and_clock: <exact frozen source + availability time>
    executor: <actual available mode>
    prereqs: []
    run_receipt: NOT_YET_EXECUTED
    output: <original owner research path>
completion:
  required_lanes_finished: UNKNOWN
  artifact_receipts_verified: UNKNOWN
  source_QA: UNKNOWN
  prediction_edge: UNPROVEN
  economic_edge: UNPROVEN
  production_admission: NOT_REQUESTED
```

No generic `SUCCESS` can combine incompatible statuses. Source availability, completed experiment, predictive edge and investor utility are distinct gates.

## Task 2 six-track starting decomposition (suggestion, not issued execution)

A useful real Task 2 example: original Compass forecast PIT-source baseline; lead-time/pullback stress with false positives; source-integrity and event time/clock QA; cross-venue independence; wallet/altseason nontransfer controls; blinded or prospective post-maturity evaluation. Some are dependent, so the source-clock validation must precede model comparison; remaining independent tests may execute simultaneously. Another thread should recheck current #1596 and #387 to avoid duplicating already-merged #1988/#1989.

## Lane-level handoff and user-facing synthesis

For each lane, report `PLANNED | RUNNING | COMPLETE_VERIFIED | FAILED_EVIDENCED | BLOCKED | NOT_EXECUTED`, exact SHA, source digest, original time scope, what was actually run, job/agent ID, raw logs/artifact ID (or exact missing evidence), positive/negative finding, false-alarm/edge/cost caveat, owner action and stop condition.

At the end: **(a)** what genuinely ran simultaneously, **(b)** useful new evidence even if negative, **(c)** incomplete/blocked tracks and exact repair owner, **(d)** release/merged/main readback independently verified, **(e)** what the user can now safely conclude. Do not call multiple branches "agents" or claim that a green workflow proves future autonomous work.
