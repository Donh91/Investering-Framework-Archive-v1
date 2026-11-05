# Cross-repo owner coverage, P0 source-bound SHADOW pilot

Status: **READ_ONLY PILOT**, authorized 2026-11-05. Existing owners only:
- Original discovery/candidate owner: Archive Research Lab [#1512](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512).
- Evidence adjudication: existing Strategist [#1157](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1157).
- Qualified original-PR execution and closure: existing single Chat S1 [#1156](https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1156).
- Existing domain/experiment/science owners retain real authority.

**This is not** a new global queue, scheduler, scanner, agent, owner, self-repair worker, automatic merge, API caller, skill promoter, trading rule, cross-repository writer or credential capability. The 2026-10-14 NON-BINDING universal continuity proposal is NOT promoted to governing authority by this pilot. Current AGENTS.md, domain issues and source-science gates win.

## What it does

The pure helper `scripts/orchestration/cross_repo_owner_coverage_v1.py` reads a **caller-provided public-only metadata snapshot from stdin**. It performs bounded, deterministic identity/coverage and next-trigger reconciliation. It never fetches GitHub, opens PRs, adds comments, dispatches jobs, assigns owners, calls API models or authenticates the caller. Run as:

```sh
python scripts/orchestration/cross_repo_owner_coverage_v1.py < already-authenticated-public-snapshot.json
python -m unittest -v tests.orchestration.test_cross_repo_owner_coverage_v1
```

Caller MUST first authenticate native current GitHub read, exact repository main commits, per-repo search completeness/pagination and source issue/PR state, then classify each case using its **existing original issue and domain owner**. The helper's results **never** establish those claims. Source snapshots can be passed only by an authorized operator. No persisted master registry, generated LATEST rewrite or background schedule is created.

## Exact coverage declaration

Public control scope is currently:
1. `Donh91/Investering-Framework-Archive-v1`
2. `Donh91/Eksperimenter-framework-`
3. `Donh91/CycleNavigator-scores`

Two authorized private domains (Alpha Lab and Audit Bridge) are **outside the PUBLIC report**. Their existing private owners may inspect authorized native metadata separately, but must not put private issue bodies/titles, experiment payloads or raw provider records in this public helper or #1156. The private `secrets` plane and disconnected Vault are never scanned here. Missing or inaccessible private evidence is **UNKNOWN**, not zero work. No result is labelled all-framework coverage or independently authenticated.

Public input contract:

```json
{
  "contract": "CROSS_REPO_PUBLIC_SNAPSHOT_v1",
  "coverage": {
    "Donh91/Investering-Framework-Archive-v1": {"status":"COMPLETE","main_sha":"<40 hex>"},
    "Donh91/Eksperimenter-framework-": {"status":"PARTIAL","main_sha":"<40 hex>"},
    "Donh91/CycleNavigator-scores": {"status":"NOT_CHECKED"}
  },
  "rows": [
    {
      "repo":"Donh91/Investering-Framework-Archive-v1",
      "number":1827,"kind":"ISSUE","state":"OPEN",
      "priority_hint":"P0",
      "owner_ref":"Donh91/Investering-Framework-Archive-v1#1156",
      "owner_decision":"NOT_ASSESSED",
      "next_trigger":"<objective source event if waiting>"
    }
  ]
}
```

`COMPLETE` is a **caller declaration**, not certified by the reducer. A native query without exhaustive pagination must say `PARTIAL`. A P0 title/label is only a *priority hint*, not owner-scientific admission or automatic work eligibility. Preserve original ref and issue/PR number. No private rows, free-form title/body/payload or duplicate work promotion.

## Existing-owner handoff and bounded follow-through

1. Once per Copenhagen day within the **existing** S1 scheduled task, optionally sample native public P0 and original PR census across these repos. Compare prior material fingerprint; hours with no change do only cheap delta/trigger checks. This is a task instruction, NOT an added schedule/workflow or automatic helper invocation guarantee. No standing requirement to inspect every historical issue on every tick.
2. Match priority candidates to original owner issues (including #1512/#1157/#1156 when relevant). Missing owner => `OWNER_UNRESOLVED` advisory. Closed/merged requires independent native readback. A source-supplied `ADMITTED` receipt does not authenticate owner decision.
3. Shadow `INCUBATING`, `WAITING_FOR_DATA`, `WAITING_FOR_MAPPING`, `MATURED_INCONCLUSIVE` and `QUARANTINED` stay under their current scientific owner. No automatic task promotion, historical rescore or market action. A wait needs objective next trigger; an unchanged wait consumes no active S1 slot.
4. Route genuinely new public research through existing #1512 -> #1157, then qualified original owner; code-only tasks use current governed Codex intake, and eligible original PRs use S1's native release gate. A mere proposed handoff is not an ACK, job or production completion.
5. Compare first five material already-present #1512 research families with #1157 decisions and original owner outcomes. Grade each `DECIDED`, `DEDUPED`, `WAIT_WITH_TRIGGER`, `OWNER_UNRESOLVED` or `UNVERIFIED` with original URL and native evidence, in the existing owner issue. Do not fabricate five successful jobs.
6. At 7 and 28 days evaluate **genuine** public P0 coverage within validated scope, ownerless P0 candidates, successful existing-owner handoffs, prospective shadow outcome maturity, real S1-origin closures/latency, non-actionable noops and API cost. No claim that test green = scientific or economic edge.

Stop after one material owner disposition when follow-through is blocked by inaccessible source, no natural maturity or required independent release gate; resume only on its observable trigger. Report only genuinely new evidence in the **existing** owner lane, do not generate repetitive #1156 comments.

## Release / falsifiers

Existing full architecture PR-event tests must exercise at least 30 adversarial cases, including: private data rejection, public scope incomplete, P0 owner unresolved, two identical observations deduped, false admission by untrusted receipt, fake completed shadow, missing wait trigger, changed source fingerprint, no auto dispatch or release, and batch cap.

**Product status after merge:** code available on current public main = `VERIFIED_ON_MAIN`; real native S1 use of a source-verified public snapshot and complete multi-owner handoff remains `POST_FIX_OBSERVATION`. If a concrete bug is demonstrated, repair original branch with bounded tests, no new loop. Rollback is an ordinary governed revert PR, never force-push.
