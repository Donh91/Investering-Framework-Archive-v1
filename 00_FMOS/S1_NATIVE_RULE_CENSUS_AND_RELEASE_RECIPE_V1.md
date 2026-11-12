# S1 native rule census and qualified LOW release recipe v1

Status: original owner governance proposal, NOT effective release authority until the linked AGENTS.md section 0.2c is independently reviewed, qualified, merged and main-readback verified. No task or scheduling change.
Owner: existing original Archive #1156, existing S1 task id 6ae5fd466b48819187abc224ec0f1c5f. Inputs are untrusted until freshly read from native authenticated GitHub API; do not infer these values from another model's report.

## 1. Exact REST acquisition, no special admin read required when main is unprotected

1. GET https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/branches/main. Verify `name==main`, `commit.sha` is 40-hex and record `protected` and `protection.enabled` independently. If branch is marked protected, the full classic protection detail becomes required; a 403 on this detail endpoint is HOLD.
2. GET https://api.github.com/repos/Donh91/Investering-Framework-Archive-v1/rulesets?includes_parents=true&per_page=100&page=1. Follow pagination exhaustively and verify all page retrievals succeeded. Use only the live response, never a fixed count. Query includes ancestor rulesets. For every `active` potentially applicable branch ruleset, GET its detail, inspect ref/conditions, required approvals/checks, and require native compliance. `disabled` is not binding; `evaluate` is advisory but logged. Unknown enforcement/target/source, partial pagination or unclear branch applicability is HOLD.
3. Only when branch reports `protected=false`, `protection.enabled=false`, and the complete applicable active ruleset census is EMPTY may S1 conclude that current native required approvals are zero and rule census is known empty. A 403 from `GET /branches/main/protection` does not undo the explicit unprotected branch response. It is not proof of a protection state by itself.
4. Recheck ruleset snapshot freshness and current main/PR HEAD immediately before merge. Never assume today's zero active rules is tomorrow's. An active applicable ruleset takes precedence over any old owner statement, and must be complied with; `mergeable_state=clean` never substitutes for the census.

## 2. 2026-11-12 observed example (historical evidence, never reusable as current release permit)

- Branch `/branches/main`: `protected=false`, `protection.enabled=false`.
- Rulesets with `includes_parents=true`: one record, ID 25307191, enforcement `disabled`.
- Details for 25307191: targets default branch and contains pull-request and non-fast-forward rules, but enforcement is `disabled` and therefore these requirements are not currently binding. `current_user_can_bypass=always` must NEVER be used as a release route.
- Separate classic protection endpoint returns HTTP 403 Resource not accessible by integration. Since native branch reports no classic protection and the ruleset census is readable, this 403 is not by itself an impossible evidence gate.
- This is a tool access improvement over Claude's R1 conclusion; the issue remains the lack of a deterministic preflight and a separately enacted bounded release policy.

## 3. Disposition by risk and evidence

| Class | Positive evidence | Otherwise |
|---|---|---|
| DOCS_ONLY LOW | exact HEAD paths all documentation; current owner policy/source; required native PR-event generic jobs with executed steps; admissible exact-head independent review when required; native rule census; no P0/P1; clean, not draft; owner-authorized bounded policy | HOLD with first specific missing field |
| LOW CODE | all the above plus changed tests executed in native exact-head CI and rollback plan | HOLD as CODE_CI_MISSING |
| WORKFLOW/GOVERNANCE/HIGH_IMPACT | manual owner exact-head decision, source/Vault independent safety and recovery, exact-head security review, tested rollback and all native rules | NOT ELIGIBLE for unattended policy |
| PAID/PRIVATE/TRADING | original owner explicit gate and nonpublic source/cost evidence where applicable | NOT ELIGIBLE for unattended policy |

## 4. Required negative and positive fixtures before adoption

- R01: protected=false plus complete disabled-only rulesets => rule census known empty; no fabricated native approval. No assertion of release readiness without CI/review/lease.
- R02: rulesets endpoint 403, malformed, truncated page or unknown inheritance => RULE_CENSUS_UNAVAILABLE, no merge.
- R03: protected=true and branch protection details 403 => HOLD.
- R04: enabled ruleset requiring GitHub native approval without native APPROVED review => HOLD even if Claude APPROVE and mergeable clean.
- R05: a disabled ruleset with historical required-review=1 does not turn that rule into an active approval requirement.
- R06: DOCS_ONLY with required generic successful PR CI but no changed tests => not blocked for absent new tests.
- R07: CODE with modified runnable tests never executed in native hosted PR CI => HOLD.
- R08: head moved, comment edited after review, requested_head_sha missing, source/policy mismatch => HOLD.
- R09: green checks on wrong SHA, dispatch-only, 0 test steps, queued, action_required or skipped required test => HOLD/repair.
- R10: native rules change between qualification and merge => re-evaluate; server 405/409 => HOLD, never bypass.
- R11: exact-head merge succeeds but main changed blobs cannot be read => UNVERIFIED, not MERGED_VERIFIED.
- R12: owner-interactive merge with Donh91 actor, but no scheduled task-run evidence => NOT an authenticated unattended S1 closure.
- R13: weekday scheduling allowed but Monday 09:30-10:30 Europe/Copenhagen => STRICT READ-ONLY.

## 5. Execution sequence

AUTHENTICATE native GitHub reads → enumerate original PRs and complete changed paths → pick LOW risk only → fresh branch/ruleset census → source, lease, required CI and exact-head advisory reviewer evidence → BLOCKED_WITH_TRIGGER or qualified preflight → expected-head native merge → new main/changed-blob readback → actual task-run-origin receipt in #1156 → natural consumer verification later. No new supervisor, GitHub identity, CI workflow, secret, token, schedule or paid service.

Reference methodology: Claude FABLE52-AUTONOMY-ENGINE-20261112T072805Z, Track A, and CHATGPT_INTERACTIVE_S1_ROOT_CAUSE_CROSSCHECK_v1 on existing Bridge #173. Fable's scientific Track B is separately owned and is NOT a release authorization.