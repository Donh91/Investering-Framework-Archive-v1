# S1 vNext, reviewer and release acceptance matrix

**Use existing Claude v2 as the only implementation baseline.** This document describes tests before any authority change. Reviewers must NOT count their own work as independent review, and all test evidence must be reproducible on the exact native PR HEAD.

## A. Immediate PR #2190

| Gate | Required reproducible proof | Negative that must fail | Owner |
|---|---|---|---|
| Fork provenance | workflow_run admitted only when `head_repository.full_name` equals exact parent repo | fork `main`, missing `head_repository`, renamed/uppercased repo, wrong branch | Codex original PR branch |
| Health ordering | last actual scheduled production failure does not get masked by later skipped workflow_run | two fake fork failures ahead of success | Codex + detached reviewer |
| Source chain | updated health tree -> lane switch blob -> contract blob -> BOOTSTRAP 3b | old bootstrap token, stale tree, changed base | Codex, owner release |
| Native CI | full suite and all actual job steps on 40-hex head | green workflow with skipped full-suite test | GitHub Actions native |
| Review | detached exact-head reviewer, no blocking threads | old-head APPROVE, same-author review | Claude while available, alternative qualified in-house reviewer if approved |
| Release | non-force reviewed owner-present squash, main/commit/blobs | S1 unilateral HIGH_IMPACT merge | Owner |

The existing #2190 remains unmerged until all gates pass. An unchanged reply to Codex is not a code patch. Don't race the writer.

## B. v2 direct comparison

| Threat | Existing Claude v2 mechanism | Independent challenger | Required acceptance |
|---|---|---|---|
| Stale pins after #2189/#2190 | v2_0 12-file package and v2_0_github 10-file staged package | compare every original base blob at current main | 0 stale base blobs in final source package, C1b drift suite |
| False reviewer independence | `REVIEW_ADMISSION.md` allows S1 specialist receipt | do not call S1's own re-derivation detached | all admitted code reviews from distinct qualified identity/context and source; negative author tests |
| Forced close of useful work | `STEWARD_STATES.md` park/age counters, two strong-looking signals | never close on time/counter/comment alone | objective native duplicate/supersession proof or owner-present; rollback positive |
| Missing API path | v1.6.9 C7 workflow-scoped GitHub runs | tool-compatible repo-wide pagination adapter | exact path/event/main, last 26h, negative fork/PR/incomplete page |
| Isolation coverage | `S1_WORKFLOW_ISOLATION_V1.json` lower-bound imported-code set | dynamic import/shell/call-chain red team, fail closed on unknown | fresh detached R4 and hosted CI on current source including last `parents[k]` fix |
| Codex authored PR | Codex cannot review own head | fresh independently qualified ChatGPT review if governance proves real separation, else owner | no fake S1 specialist semantic independence |
| Branch update and new CI | native update branch or git data + readback | stale HEAD/merge from main and multiple writers | never lose newer main bytes, exact post-update current-head review |
| GitHub write timeout | intent and reconcile | operation-key dedupe + native results | replay yields exactly one actual action |
| Scheduler delay | generated hourly task | track native scheduled/started/completed | no code decision treats schedule as a completed run |
| Owner UX | status lines and optional daily summary | in-run verified owner decision card | exact SHA, blockers, one action, no extra task required |
| False completion | review/merge/progress counts | native same-run attribution and natural consumer | separate merge and consumer outcome classes |
| Efficiency | 2-source rolling discovery + 3 deep cases | frozen v1.6.9/v2 baseline cost | fewer duplicate reads/owner touches, no blind PR/comment inflation |

## C. 109-test reference harness

- 82 adverse guard tests and 27 finite planner tests passed under Python standard library locally.
- Each function returns `authorized=False` by construction. A model or PR cannot treat passing these tests as permission to mutate GitHub.
- These tests are *research tests*, not current native hosted framework CI. Claude may reuse/correct them only after integrating against actual current policy with new tests, independent review and source blob derivation.
- The next necessary checks are actual GitHub Actions full suite, F3 ruleset census, branch protection, review-thread closure, original code/output readback, and live observed S1 scheduled runs. Those remain `NOT_PROVEN` by this package.

## D. In-house-only operational standard

- No Claude subscription or response is ever mandatory for normal S1 existence, diagnosis, prioritization, safe code-test work, or clearly owner-present HIGH_IMPACT decisions.
- Every merge needs at least the independent review actually required by the **current** AGENTS and enforced platform. Codex review on a non-Codex-authored head may qualify when the native bot receipt is complete; Codex's own code cannot be approved by the same Codex bot merely with a second comment.
- Independent internal ChatGPT reviewer path is **proposed**, not automatically admitted. To qualify it, first prove separate execution context, original code authorship exclusion, uneditable native run report, exact HEAD, source-pinned tests and reviewer independence under a reviewed AGENTS change. No second scheduled S1 task is allowed.
- If independent reviewer cannot be proven, S1 MUST surface a precise owner card. Owner approval cannot waive any mandatory native independent CI, security or protection rule.
- A clear manual owner review/merge in ChatGPT + native GitHub connector is a valid **in-house** fallback once eligible. No external Claude account is needed for this route.

## E. Hostile scenario replay

1. False fork-main RED or false fork-main success.
2. Stale Code review after update-branch.
3. A fork PR with missing repository identity.
4. A workflow SUCCESS with skipped privacy/full suite.
5. User- or bot-authored S1_ITEM counters force `CLOSED_NOISE`.
6. Owner card generated while review still REQUEST_CHANGES.
7. Codex authored the patch and Codex's own review claims no findings.
8. S1 authored patch and its specialist rubric says APPROVE.
9. Claude disabled for seven days, Codex available for other non-Code-authored work.
10. API 403, 429, mixed page count, branch HEAD changed between preflight and write.
11. S1 last_result points to an older successful tick while latest scheduled run has failed.
12. Merge accepted on GitHub but receipt lost, then next S1 tick tries again.
13. Test suite executes, but produced public site is different from reviewed output.
14. Proposed closure merely due to the 3-park limit.
15. User approves HEAD A, CI restarts and PR head changes to B.
16. Sol paid request returns timeout after payment claim, response ID unknown.
17. Native Vault release receipt expired, no source/recovery separation.
18. Model-generated summary counts owner-interactive merges as unattended S1.
19. SOURCE_UNVERIFIED bootstrap still tries to post a GitHub comment.
20. Monday 09:30-10:30 output card accidentally emits a write.

## F. Review verdicts and promotion kill rule

Every finding must be labeled `PROVEN`, `NOT_PROVEN`, `HYPOTHESIS`, `CONFLICTING` or `TOOL_CANNOT_READ`, with exact source objects and timestamps. Each test proposal needs a reference baseline, adversarial input, expected output, false-positive cost, false-negative cost, exact code path and new full-head CI requirement. A reviewer returns `APPROVE`, `REQUEST_CHANGES`, or `ABSTAIN`. `APPROVE` by itself is not merge authorization.

Hard kill criteria: any false READY, unauthorized closure, loss of newer main bytes, self review counted as independent, ability to alter credential/write-token jobs from PR without review, source/recovery bypass, source/market first-known leak, double-paid Sol POST, unreviewed owner/policy patch, or a second active S1.
