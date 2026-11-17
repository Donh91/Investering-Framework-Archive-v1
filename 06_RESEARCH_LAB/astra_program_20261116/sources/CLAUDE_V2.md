# S1 v2 Autonomous Steward: independent adjudication of the D1–D8 design review (pre-implementation)

```yaml
artifact_id: CLAUDE-S1-V2-DESIGN-ADJUDICATION
author_agent: Claude, scheduled Bridge auditor (session_0174j3zyStcb322SRX1EXPAV), lane a
request: "#173 6922436951 OWNER_DIRECTED_S1_V2_INDEPENDENT_DESIGN_REVIEW_v1 (+ coordination 6922244260)"
artifact_type: METHOD/DESIGN REVIEW (advisory); no source PR, no code
independence: DETACHED from the v2 package author (another Claude session built CLAUDE-S1-V2-BUILD-20261116T0716Z)
sources: claude/log v2_0/files (STEWARD_STATES.md bc67670c, REVIEW_ADMISSION.md 47b42ef5, blobs.txt); Archive main b3706fa5
round3_firewall: not touched
external_framework_repositories_modified: false
local_state: SUBMITTED
```

## Verdict

**The v2_0 package is not ready to promote, as the proposal says.** I accept D1, D2 and D3 as **binding v2 requirements**; all three are verified below. I accept D4–D8 as requirements but have **not independently verified** them in this run. Order of work: track A (#2190) first, then rebuild v2 on fresh main.

## D1: base pins stale; health endpoint compatibility. **VERIFIED and ACCEPT.**

`v2_0/blobs.txt`, compared with main `b3706fa5`:

| file | base pinned in v2_0 | main today | state |
|---|---|---|---|
| ACTION_LOOP.md | `b4649725` | `b4649725` | match |
| AGENTS.md | `8516afbb` | `8516afbb` | match |
| test_s1_runtime_contract_v1.py | `f0439c78` | `f0439c78` | match |
| **BOOTSTRAP.txt** | `f36b3c7b` | `b4d76de0` | **stale** |
| **REVIEWED_MERGE_LANE.json** | `53cf8620` | `5cde5904` | **stale** |
| **RUNTIME_CONTRACT.json** | `84c01363` | `4ef1bee7` | **stale** |
| **test_s1_reviewed_merge_lane_v1.py** | `0d08dc87` | `74e8e07b` | **stale** |

So 4 of the 7 base pins are stale. The byte-exact v2_0 must **not** be applied, and v2_0_github is stacked on it. Once #2190 merges, the contract changes again.

**Requirement:** rebuild v2 from fresh main **after** #2190. Keep a 26 h health-freshness gate. Read it through a tool-compatible endpoint, `/actions/runs?event=schedule&branch=main` filtered by workflow path. Add negative tests for runs from pull requests, dispatches and forks, and report `TOOL_CANNOT_READ` honestly instead of waiving the check.

## D2: unattended CLOSED_NOISE on time and budget signals. **VERIFIED and ACCEPT (HIGH).**

`STEWARD_STATES.md` creates three problems:

1. **Close signals.** Closing needs at least `close_noise_min_signals = 2`, with at least one STRONG signal. STRONG includes **`stale_final_park`, `park_limit` and `cycle_cap`**. These are budget or time facts, not evidence that the original item is noise.
2. **Counters can be forged.** `park_count` and the other counters are "the highest value in its history", and the file's own forgery note says that **a forged S1_ITEM_v1 "can only speed up a disposition"**. One forged comment carrying `park_count: 3` therefore reaches CLOSED_NOISE early.
3. **Visibility.** Reversibility ("Reopen to resume") and the daily-summary line soften this, but a valuable original can still be closed silently.

**Requirements:**
- An unattended close needs **at least one objective, natively verifiable signal**: duplicate, superseded or premise_falsified, each linked to a native object.
- Time and budget signals alone lead to **PARKED_OWNER_DECISION** (open, labelled), never to a close.
- Never auto-close **HIGH or HIGH_IMPACT** items.
- Read counters only from S1-authored items whose contract and run id are present in a native run receipt. A plain comment by `Donh91` is not enough.

**Tests:**
- a forged comment with `park_count: 3` must not close;
- an item with only `stale_final_park` and `park_limit` must not close;
- a HIGH item must never close;
- a missing Strategist answer must lead to PARKED.

## D3: the "specialist" review is not independent. **VERIFIED and ACCEPT, with an owner decision for LOW.**

`REVIEW_ADMISSION.md` (iii) admits `S1_SPECIALIST_REVIEW_v1`. It is **written by S1 and re-derived by the same S1 merge principal**, for risk classes LOW and MEDIUM, and for HIGH when the head is CODEX_AUTHORED. The file also says "Claude is never required".

A rubric re-derived by the merging agent is a preflight check, not an independent review.

- It conflicts with the 2026-11-09 owner decision: the independent-review gate needs a different reviewer.
- It conflicts with clarification 6873422813: a self-authored-design APPROVE cannot alone satisfy that gate.

**Requirements:**
- MEDIUM, HIGH and HIGH_IMPACT need **Codex App authenticated** on a head Codex did not author, or a **detached Claude exact-head receipt**. Otherwise HOLD.
- The specialist receipt may be **preflight only**, never counted as independent.
- LOW (documentation or tests only) may use the specialist path **only if the owner explicitly decides so**, with a prospective audit sample (for example, 1 in 5 LOW merges also get a detached review).

**Tests:** author spoofing, mixed authorship, forged App identity, a receipt for an old head, and a native CHANGES_REQUESTED.

## D4–D8: ACCEPT as requirements, NOT independently verified this run

- **D4, write-token custody.** Census the roughly 58 non-secret write jobs, and do not widen the lane until hosted isolation is proven. R4 must be a fresh detached review on the **final integrated head**, and gate checks must not import scripts from the PR's own source.
- **D5, no second scheduler.** Fold DAILY_SUMMARY into the existing hourly S1 as an idempotent once-a-day section. A separate task needs an explicit owner yes.
- **D6, cost and loop control.** Use a changed-fingerprint scan, limit to 3 material cases per run, and set a fixed tool-call budget. Every NOOP states its exact reason. Resolve the "3" vs "max_merges_per_tick + 2" ambiguity in writing.
- **D7, partial failure.** Write an intent before every mutation, read back the exact head afterwards, and dedupe on retry. Test each partial-failure case listed in the proposal.
- **D8, scheduler lateness.** Record `scheduled_for`, `started_at` and `run_id`. Alert on an SLA breach, not on lateness alone.

## Smallest next step

1. Codex fixes #2190; I review the new head.
2. The v2 author rebases v2 on post-#2190 main and implements D1–D3 as written above.
3. Fresh detached R4 on the integrated head, with hosted CI and mutation runs.

No v2 promotion before step 3.

No external repository was modified.
