# S1 vNext | Autonomous Steward, in-house-first, adversarial design and code

**Status:** REVIEW_CANDIDATE / RESEARCH_ONLY / NOT DEPLOYED. Owner requested 16 November 2026. No active S1 task, source governance, protected branch, review lane, model routing, payment limit or trading authority is modified by this package.

## Authoritative snapshots (read again before any write)

- Sole current Chat S1 task: `6ae5fd466b48819187abc224ec0f1c5f`, existing hourly `:45` Europe/Copenhagen, Monday 09:30-10:30 strictly read-only.
- Archive observed main at preparation: `584d18a7870fa0d45c99a7fd3f75356edf203f30` (16 Nov 2026 17:31:28 UTC). Active `00_FMOS/S1/ACTION_LOOP.md` Git blob `b4649725eaf972fd559bdbd91803f029185eb6cd`, contract Git blob `4ef1bee7d045b4b09b0d8f745c21c856d2704d7e`. Re-fetch exact main and AGENTS before implementation.
- Existing Claude v2 source, **not to duplicate**: Bridge `claude/log`, `reports/claude/automated/2026/11/CLAUDE-S1-V2-BUILD-20261116T0716Z/README.md` Git blob `ebec773a4e510f16fbe7801abbcb077cbee92595`; recipe Git blob `30089f5e6332708a31b07682d0338dd6549758cf`. Existing packages `v2_0/` and `v2_0_github/` remain PATCH_DRAFT, not activated. R1, R2 and R3 all requested changes; final post-R3 correction has not received a detached R4 review.
- Urgent PR #2190 code-repair owner path remains separate; Claude and Codex both found the fork-main health gap at HEAD `8992c5a105e244d4840e5a4e62f67e60ee39e6c2`. An in-place Codex instruction was filed, but no corrected HEAD was proven at snapshot.
- GitHub instructions/lane, source/recovery separation, live CI and reviewer requirements are binding. No plan or package is a release authorization.

## Files

1. `DESIGN.md` - full S1 vNext architecture, capability/role matrix, error model, owner approvals, migration, rollback, acceptance criteria and research falsifiers.
2. `SOL_MAX_MISSION.md` - prepared public-only Sol 6.1 MAX evaluation, with safety controls and an explicit paid-dispatch blocker.
3. `SOL_MAX_PACKET.json` - machine-readable mission and provenance, state `PREPARED_NOT_DISPATCHED`, no job or response ID.
4. `REVIEW_MATRIX.md` - priority ordered red-team and implementation contract for Codex, in-house ChatGPT reviewer and optional Claude.
5. `reference/s1_steward_guard_reference.py` - pure, side-effect-free threat guards.
6. `reference/s1_steward_planner_reference.py` - pure, side-effect-free finite state/action planner and owner-decision cards.
7. `reference/test_s1_steward_guard_reference.py` and `reference/test_s1_steward_planner_reference.py` - offline adversarial tests.

## Reproduce without paid API or GitHub credentials

```bash
cd reference
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v \
  test_s1_steward_guard_reference.py test_s1_steward_planner_reference.py
```

All advisory code is deterministic and Python standard-library only. **Passing these tests does not establish hosted PR CI, real GitHub adoption, agent independence, dispatch availability, live accuracy or closure.**

## Hard precedence

1. Fix the live #2190 P2 on the original PR, rerun native exact-head tests, get an independent exact-head review and obey owner-only release/contract paste.
2. Ask Claude to review this proposal against **its own existing v2**; reconcile ACCEPT/REJECT/DEFER in that package, not a competing framework owner.
3. Run a safe v2 shadow comparison on real independent current-source fixtures. No automatic merge/close/owner decision from this code.
4. Only after reviewed v2 production rollout and a prospective cohort, consider measured v3 enhancements and appropriate owner actions.
5. Sol 6.1 MAX may help criticize the design, but it cannot run until its **existing source registry and historical payment liability** pass the current native paid gate. User willingness to pay is recorded; no implied bypass.

**North star:** more independently verified original closures and natural consumer outcomes, fewer owner interventions and fewer wasted/tardy ticks, with zero false READY, unauthorized review, leaked secret, illegitimate close or merged code.
