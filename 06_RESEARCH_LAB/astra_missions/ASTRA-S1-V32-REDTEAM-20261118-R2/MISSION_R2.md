# ASTRA GPT-6.2 RED-TEAM MISSION: S1 v3.2 (tick brief hardening)

- mission_id: ASTRA-S1-V32-REDTEAM-20261118-R2
- requested_by: owner (Donh91), 2026-11-18. Budget and price are pre-approved by the owner for ONE run.
- prepared_by: Claude (setup session). Maturity: TEST_DESIGN. No external repository modified.
- model: Astra on GPT-6.2 at the highest reasoning setting available. One-shot, no tools, no network.
- input: `BUNDLE_R2.md` in this folder (round 2: the fixed final candidate). It is self-contained; do not fetch anything.

## 1. Role
You are an adversarial security and correctness auditor. Your job is to break S1 v3.2 before it ships. Assume a capable attacker, and assume GitHub misbehaves (late crons, throttled APIs, partial pages). Be concrete: every finding needs a reproducible scenario. Do not praise, and do not restate the design.

## 2. System under test (short)
- **S1** is an hourly ChatGPT scheduled task (small tool budget) that supervises the public repository `Donh91/Investering-Framework-Archive-v1`. It can comment, request reviews and squash-merge PRs through a "reviewed-merge lane" (AGENTS.md §0.2e). It must never merge HIGH_IMPACT or owner-gated work, and never trade, move money or publish private data.
- Its saved task text is `00_FMOS/S1/BOOTSTRAP.txt`. The bootstrap pins `RUNTIME_CONTRACT.json` by blob SHA (step 3b). The contract pins `ACTION_LOOP.md`, `TICK.md`, the rubric files and the lane switch.
- **v3.1** added `.github/workflows/s1-tick-brief.yml` and `scripts/governance/s1_tick_brief_v1.py`. GitHub precomputes a JSON "tick brief" into the body of one issue labelled `s1-tick-brief`. S1 verifies it (author, run re-read, freshness ≤ 45 minutes, drift against current main), re-reads the chosen candidate natively, and acts.
- **v3.2** changes the following:
  - A: the brief is built against a pinned main SHA M0.
  - B: exact endings (BRIEF_INCOMPLETE and similar).
  - C: merge-base and behind count from git objects, not REST compare.
  - D: `claude_slots`. S1 reads private Bridge #173 once per tick for exact-head Claude CLAUDE_REVIEW_v1 APPROVE receipts. PROMOTE is permissive, because F4 re-verifies. SUPPRESSING a review request requires full visible admissibility.
  - E: an owner branch-update repair route.
  - F: freshness fallback through `workflow_run` and `push` triggers on main, gated by a cheap `due` job with a run-history check.
  - G: an API budget. One cron at :18, at most 300 calls per build, attempts counted, and on rate limit one bounded retry followed by BRIEF_INCOMPLETE.

## 2b. Round 2
A previous offline audit (GPT-6) reported A1-A23 (see §0b of BUNDLE_R2). For EACH of A1-A23, state FIXED / PARTIAL / NOT_FIXED / NOT_APPLICABLE with file:line evidence from BUNDLE_R2. Then attack anew. New findings use ids N1, N2, ...

## 3. Attack these specifically
1. **Brief forgery, replay and staleness.** Can anyone (another workflow with `issues:write`, a PR author, a fork, a bot) make S1 accept a forged, old, replayed or edited brief, or act on a brief that does not describe the current main? Attack the issue-author check, the run re-read, the edit window, the 45-minute freshness and the M0-to-current-main drift rule (T3).
2. **Merge without full gates.** Find any path in TICK.md or ACTION_LOOP.md where S1 merges without natively re-verifying all of these:
   - the exact head;
   - required CI on that head (privacy-scan enforce, execution-truth, full test);
   - an admissible review;
   - lane eligibility (no governance, workflow, secret-run, custody or privacy-boundary path);
   - rulesets and halts.
3. **Receipt abuse (D).** Three people or agents post as the same GitHub account Donh91: Claude, Grok's connector and S1. Can an unsolicited, edited, PROACTIVE, wrong-head or binding-less receipt promote a merge or suppress a review request so that a PR livelocks? Can a REQUEST_CHANGES be hidden?
4. **Workflow security.**
   - `workflow_run` and `push` trigger scope;
   - forks;
   - script injection through `${{ }}` or environment variables;
   - token persistence (`tree:0` fetch with `http.extraheader`, `GIT_CONFIG_*`);
   - artifact or cache poisoning;
   - the PyYAML hash pin;
   - least privilege per job.
5. **Liveness and cost.**
   - Show any scenario that causes repeated builds over 1 per hour, or that exceeds the 300-call cap. Retries, pagination and the shared repo-wide GITHUB_TOKEN limit of 1,000 requests per hour are all in scope.
   - Show any scenario where S1 never acts again: a permanent NOOP or livelock.
   - The schedule-outage case is real. On 2026-11-18, GitHub fired no crons for this repository for about 4 hours, while App-token bot pushes kept happening.
6. **Workflow-isolation derivation.** Can a PR add code that runs in a secret-using job and still be classified lane-eligible? Consider the derivation at the PR head unioned with main, drift between B.main and M, dynamic imports, and new files in non-test directories.
7. **Endings and fail-closed.** Every unread or ambiguous state must end in one of the allowed NOOPs, with no write. Find a fail-open path.
8. **Pins.** Any way to change S1's behaviour without changing a pinned blob, for example a rubric read only "where TICK.md names it", or an unpinned file that TICK.md or ACTION_LOOP.md defers to?

## 4. Known and accepted (do not re-report unless you show they are worse)
- Same-account forgery: anyone with write access can post as Donh91. This is accepted. Defences are exact-head binding and native re-verification.
- If the cap is hit before the PR loop, publishing fails and S1 later returns BRIEF_STALE. This fails closed.
- At most about 45 minutes of drift between M0 and the tick, mitigated by T3.
- Depth cap: more than 15 open non-draft PRs gives BRIEF_INCOMPLETE(depth_cap).
- The final candidate adds a `push: main` trigger through the same `due` gate (brief older than 55 minutes, no cron run in the last 50 minutes, no build in the last 60 minutes). Attack its cost and safety.

## 5. Output format (strict)
```
ASTRA_REDTEAM_REPORT_v1
mission_id: ASTRA-S1-V32-REDTEAM-20261118-R2
input_sha256: <copy the value the launcher states; do not compute it>
verdict: SHIP | FIX_FIRST | BLOCK
provenance: <exact model id, reasoning effort, and platform as shown to you>
round1_status: <A1..A23 each: FIXED|PARTIAL|NOT_FIXED|NOT_APPLICABLE + evidence>
summary: <=5 lines
findings:
- id: A1
  severity: P0|P1|P2|P3
  area: forgery|merge-gate|receipt|workflow-sec|liveness|cost|isolation|fail-open|pins
  file_line: <path:line from BUNDLE>
  scenario: <step-by-step, concrete>
  impact: <what goes wrong>
  minimal_fix: <smallest change>
  test: <the test that would catch it>
rejected_suspicions: <what you checked and found safe, one line each>
open_questions: <only what blocks a verdict>
```
Severity scale:
- **P0:** an unsafe write or merge, or a secret or privacy leak.
- **P1:** a gate can be bypassed, or there is reliable non-liveness or a budget breach.
- **P2:** a real defect with a bounded impact.
- **P3:** polish.

SHIP means no P0, P1 or P2.

## 6. Rules for the run
- Only use the bundle. Mark any claim you cannot verify from it as OPEN.
- No browsing and no code execution against real systems.
- Do not produce exploit code against GitHub. Describe scenarios only.
