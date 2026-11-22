S1 STEWARD STATES v2.0 (rubric of 00_FMOS/S1/ACTION_LOOP.md rule 6; pinned by rubric_blobs in 00_FMOS/S1/RUNTIME_CONTRACT.json; AGENTS.md section 0.2f)

PURPOSE
Every unfinished piece of work has exactly one state, visible on GitHub, with a budget. When a budget runs out S1 gives the item a disposition in that same run. "Waiting" is never allowed indefinitely, and no item loops: every path through this file ends in MERGED, OWNER_APPROVAL, PARKED, PARKED_OWNER_DECISION, CLOSED_NOISE or RESEARCH_HANDOFF, and PARKED itself ends after at most three parks. TIME AND BUDGET NEVER CLOSE: an exhausted budget, a revisit without news, a cap or a silent route only parks an item, hands it to research or escalates it to the owner (PARKED_OWNER_DECISION); only CONTENT signals can close (CLOSED_NOISE).

WORK ITEMS
- One work item per subject. Keys: pr:<n> (an open PR, drafts included), issue:<n> (an open issue with no disposition and no activity for 14 days or more), pkg:<queue comment id> (a Bridge CLAUDE_FIX_QUEUE_v1, CLAUDE_FINDING_v1 or Grok report on #173), handoff:<comment id> (a Strategist or Research Lab item addressed to S1), todo:<path>#<first 8 of sha256 of the line> (an OPEN or TODO entry in 00_FMOS/*OPEN_WORK* or a roadmap file).
- v3 keys: closure:<PR> (a lane merge whose consumer closure became UNVERIFIED, EVIDENCE_BINDINGS.md B5; kind FIX, risk as the merged PR) and edge:<stream_id> (a research stream of EDGE_LEDGER.md; kind RESEARCH).
- NOT WORK ITEMS: the control issues #1156, #1157, #1512, #1593 and any issue that ACTION_LOOP.md or AGENTS.md names as a ledger or receipt channel. S1 never parks or closes them.
- DEDUP: a new candidate whose subject is already an item (same PR; an issue that a PR closes or links; a package already opened as a PR; a todo that an item cites) joins that item and is never a second item.
- Kind, set at TRIAGED and only ever raised: FIX (repairs a defect or test), TEST, DOCS, RESEARCH (a research or method question), DIRECTION (a new research program, removal of a feature, a change of priorities or roadmap, a new producer or consumer). Unclear reads as DIRECTION.
- Risk class, set at TRIAGED: per REVIEW_ADMISSION.md RISK CLASS.
- FORGERY RESISTANCE: every agent can post as Donh91, so S1 never lowers anything a comment says. For each item S1 uses: risk = the highest of every S1_ITEM_v1 risk in its history and a fresh path-based classification at the current head; kind = the highest of its history and a fresh classification (order FIX < TEST < DOCS < RESEARCH < DIRECTION); attempt, park_count, triage_cycles and repair_cycles = the highest value among the item's RECEIPT-BACKED S1_ITEM_v1 comments only: a comment is receipt-backed when its id is listed under receipts= in the S1_OPEN_WORK_INDEX_v1 of a later S1_HEARTBEAT_v1 on #1156 (author Donh91, unedited, this task id, the same contract=<8>); until then S1 uses the newest receipt-backed value, and every other comment's counters are ignored. This filters stray and stale comments, not a determined forger: every agent posts as Donh91 and no native run receipt exists for this task. RESIDUAL: a forged counter or heartbeat can at most move an item to PARKED_OWNER_DECISION, which stays open and is listed as decide<n>. A newest S1_ITEM_v1 whose state is not a successor that this file allows from the previous state is ignored. A forged S1_ITEM_v1 can therefore never cause a merge or a close: at most it moves an item to PARKED or PARKED_OWNER_DECISION, which stays open and listed for the owner.

STATES
DISCOVERED -> TRIAGED -> (PLAN <-> STRATEGIST) -> BUILD -> TEST -> REVIEW -> one of MERGED | OWNER_APPROVAL | PARKED | PARKED_OWNER_DECISION | CLOSED_NOISE | RESEARCH_HANDOFF.
- PLAN and STRATEGIST are used for DIRECTION and RESEARCH items; FIX, TEST and DOCS go TRIAGED -> BUILD (or straight to TEST when the head already exists).
- An existing PR with a head is at least TEST; a green head waiting for review is REVIEW.
- OWNER_APPROVAL is any OWNER_GATED item that is not MERGED: S1 lists it, the owner acts.
- PARKED_OWNER_DECISION: an item whose time or budget is exhausted, or that S1 may not close unattended. It stays open (never closed, never converted to draft by this state), gets the label s1:owner-decision, is listed as decide<n> on the FIRST LINE and in the daily summary, and S1 spends no further budget on it. New information (as in PARKED) returns it to TRIAGED, subject to the LIFETIME CAP; the owner's own close or keep ends it.
- A PARKED item returns to TRIAGED at its revisit date. A RESEARCH_HANDOFF returns to TRIAGED when answered, or at its budget.

STATE ON GITHUB, NEVER IN A CHAT
- The state of an item is its newest authentic S1_ITEM_v1 comment: on the PR or issue itself, and on #1156 for pkg, handoff and todo items. Authentic means author Donh91, created_at equals updated_at, and a contract=<8> line (any contract; a newer contract does not drop the state).
- S1_ITEM_v1 format, one field per line: S1_ITEM_v1 / item: <key> / state: <STATE> / kind: <KIND> / risk: <class> / attempt: <n> / park_count: <n> / due: <YYYY-MM-DD, UTC> / reason: <one line> / signals: <comma list or -> / links: <ids or -> / next: <the next ladder step> / contract=<8>.
- Labels mirror the comment when S1 can set them: s1:state/<state lower-case>, s1:attempt/<n>, s1:due/<YYYY-MM-DD>, s1:parked. The comment wins when they disagree; S1 repairs labels when it can.
- A daily roll-up is the S1_OPEN_WORK_INDEX_v1 section of the heartbeat on #1156.

BUDGETS (machine-readable; tests/governance/test_s1_steward_scenarios_v2.py reads this block)
```json
{"contract": "S1_STEWARD_BUDGETS_v1",
 "dwell_days": {"DISCOVERED": 1, "TRIAGED": 2, "PLAN": 3, "STRATEGIST": 3, "BUILD": 5, "TEST": 5, "REVIEW": 3, "RESEARCH_HANDOFF": 14},
 "max_attempts": {"DISCOVERED": 2, "TRIAGED": 3, "PLAN": 3, "BUILD": 3, "TEST": 3, "REVIEW": 2},
 "max_triage_cycles": 6,
 "max_repair_cycles": 4,
 "codex_silent_hours": 24,
 "park_revisit_max_days": 30,
 "max_parks": 3,
 "same_noop_runs": 3,
 "max_active_research_handoffs": 3,
 "max_transitions_per_run": 5,
 "close_noise_min_signals": 2}
```
- due = the date of entering the state + dwell_days. A transition into the same state (a new attempt) sets a new due date and attempt+1. Leaving a state resets attempt to 0.
- An item is OVERDUE when today (UTC) is after due, or attempt exceeds max_attempts for its state, or the same NOOP reason at the same head appeared same_noop_runs runs in a row.
- LIFETIME CAP: every entry into TRIAGED (from PARKED, RESEARCH_HANDOFF, a Strategist answer or new information) adds 1 to triage_cycles. An item that would enter TRIAGED with triage_cycles already at max_triage_cycles is PARKED_OWNER_DECISION instead, with reason cycle_cap. So no item cycles forever, however often new information or answers arrive.
- REPAIR CAP: every entry into BUILD or TEST from REVIEW (a repair, a branch update, a Codex address) adds 1 to repair_cycles, which never resets. An item that would enter BUILD or TEST with repair_cycles already at max_repair_cycles is PARKED_OWNER_DECISION instead, with reason repair_cap. So REVIEW and TEST cannot alternate forever.
- Budgets never pause: an outage of Codex, the Strategist, Claude or the owner does not stop the clock.

FORCED DISPOSITION TABLE (rule 6(a); first matching row wins; record the row id in reason)
- F1 The item is WAITING_ONLY_FOR_OWNER (ACTION_LOOP.md OWNER APPROVAL): OWNER_APPROVAL, with no budget; it stays in the STATUS LINES until the owner acts or the head changes. Any other OWNER_GATED item is listed as HIGH_IMPACT BLOCKED and follows the rows below like every other item, so it cannot sit open forever either.
- F2 REVIEW overdue and attempt below max_attempts.REVIEW: REVIEW again (re-request Codex once more, then S1_REVIEW_REQUEST_v1, then the specialist receipt where REVIEW_ADMISSION.md allows it).
- F3 REVIEW overdue at max attempts, or BUILD or TEST overdue, or attempts exhausted: PARKED (reason review_budget, repair_budget or test_budget).
- F4 STRATEGIST overdue (no answer): kind DIRECTION is PARKED (reason strategist_silent; a DIRECTION item never merges without CONCUR); kind RESEARCH is RESEARCH_HANDOFF when fewer than max_active_research_handoffs are ACTIVE, else PARKED.
- F5 RESEARCH_HANDOFF overdue (no answer): PARKED (reason handoff_silent). The handoff stops counting as ACTIVE.
- F6 DISCOVERED, TRIAGED or PLAN overdue: TRIAGED again (attempt+1) if new information exists and the attempt limit is not reached, else PARKED (reason triage_budget).
- F7 A PARKED item at its revisit date: see PARKED.
- Rows F2 to F7 never close an item: time and budget only park, hand off or escalate.
- Never NOOP an OVERDUE item: when no row can be carried out because a tool is missing, write the S1_ITEM_v1 with the disposition anyway and use the TOOL FALLBACKS.

PARKED
- OWNER_GATED items are never converted to draft and never closed by S1: S1 parks them by comment and label only, they stay on the SECOND LINE, and where this file would close one S1 instead adds decide<n> to the FIRST LINE (the owner closes or keeps it).
- S1 converts a PR to draft, adds the label s1:parked, and writes the S1_ITEM_v1 with state PARKED, the reason, park_count+1 and a revisit date at most park_revisit_max_days ahead (due = revisit).
- At the revisit date S1 re-evaluates. New information (a new commit, a new review, a new linked answer, a main change to a file the item touches, or a new owner or Strategist comment) returns it to TRIAGED.
- With no new information: park_count 1 -> park again (park_count 2) and send one S1_STRATEGIST_CONSULT_v1 asking CLOSE or KEEP; park_count 2 -> CLOSED_NOISE when CLOSED_NOISE below allows it, otherwise park a final time (park_count 3); park_count 3 -> CLOSED_NOISE when CLOSED_NOISE below allows it, otherwise PARKED_OWNER_DECISION (reason stale_final_park). So no item is parked more than max_parks times.
- park_count never resets while the item stays open. An item that would be parked again with park_count already at max_parks becomes PARKED_OWNER_DECISION instead (reason park_limit). An item that anyone other than S1 reopens starts again with park_count 0.
- A Strategist KEEP answer returns the item to TRIAGED with park_count unchanged.

CLOSED_NOISE (duplicate, outdated premise, LARP, no owner link, superseded)
- Only CONTENT signals count, each named in signals with a link to a native GitHub object: duplicate (another open or merged PR, linked, that changes the same paths; subject similarity alone is never duplicate), superseded (main at M already holds every changed blob of the item, or a later PR or package states it supersedes the item, with its link; it counts once), premise_falsified (a path and blob on main whose data contradicts the item's stated premise), strategist_concur (a CONCUR to CLOSE answer on #1157 under STRATEGIST CONSULT), reviewer_concur (a Codex review or a CLAUDE_REVIEW_v1 that names duplicate, superseded or premise_falsified for this item). Time and budget facts (stale_parked, stale_final_park, park_limit, cycle_cap, repair_cap, no_owner_link, any overdue or silence) are reasons, never close signals; duplicate and no_owner_link alone never close.
- S1 closes unattended only when ALL hold: at least close_noise_min_signals distinct content signals; at least one is OBJECTIVE (duplicate, superseded or premise_falsified, verified by S1 from native reads in this run); at least one is INDEPENDENT of S1 (strategist_concur, reviewer_concur, or superseded where main at M holds every changed blob; a comment that says close is never a signal: the owner closes items himself); the item's risk is LOW or MEDIUM; it is not OWNER_GATED. Otherwise it is PARKED_OWNER_DECISION (reason close_needs_owner).
- HIGH, HIGH_IMPACT, EXTREME, unclear and OWNER_GATED items are never closed by S1.
- S1 closes the PR or issue with one comment: CLOSED_NOISE, the signals with links, "Reopen to resume; nothing was deleted." S1 never deletes a branch, a file or data, so a close is always reversible.
- Every PARKED_OWNER_DECISION item is listed in the daily summary under "venter på din beslutning" with its reason, so the owner can close or keep it.

RESEARCH_HANDOFF
- S1 posts one S1_RESEARCH_HANDOFF_v1 on #1512 (or on the domain owner's issue when the item names one): item, the concrete question, the success criterion, links, due. At most max_active_research_handoffs S1 handoffs are ACTIVE (posted, unanswered, not overdue); at the limit the item is PARKED with reason handoff_capacity.

STRATEGIST CONSULT
- S1 posts one S1_STRATEGIST_CONSULT_v1 on #1157: item, the question (Is this direction defensible? CLOSE or KEEP? Priority?), the evidence links, and the answer format: verdict: CONCUR | OBJECT | CLOSE | KEEP, plus one reason line, citing the consult comment id.
- An answer counts when it is a later comment on #1157 (for a handoff: on #1512 or the named owner issue) by Donh91 or a framework bot, unedited (created_at equals updated_at), that cites the consult or handoff id and has a verdict line. Answers are behavioural evidence, not authority; they never replace a review or an owner decision.

V3 PROGRESS ORDER (rule 6(b)): before the order that ACTION_LOOP.md rule 6(b) gives, S1 first does the due weekly EDGE LEDGER step (EDGE_LEDGER.md E5) and then the due CONSUMER CLOSURE checks (EVIDENCE_BINDINGS.md B5). Each is cheap and bounded by its own per-run limit, and each counts as S1_ITEM_v1-style transitions inside the same limit of max_transitions_per_run.

DISCOVERY (rule 6(b); cheap, a few sources per run, rolling)
- Sources in rolling order, at most 2 per run, resuming after the source named in the newest S1_OPEN_WORK_INDEX_v1 cursor: open PRs including drafts, oldest first; open issues with no activity for 14 days or more; Bridge #173 CLAUDE_FIX_QUEUE_v1 (s1_package: v1), CLAUDE_FINDING_v1 and Grok reports; 00_FMOS/*OPEN_WORK* and roadmap OPEN or TODO entries; the newest Strategist (#1157) and Research Lab (#1512) items addressed to S1.
- FRESH AUTOMATION HEALTH INCIDENT (early intake, existing Archive owner only): during rule 6(b), BEFORE the rotating sources, S1 may inspect at most ONE open original Archive issue whose title is exactly `AUTOMATION HEALTH RED`, even when its age is under 14 days. This is the existing `.github/workflows/automation-production-health.yml` alert owner, not a new monitor. Verify the issue is in Donh91/Investering-Framework-Archive-v1, currently open, and linked to the CURRENT main blob of `research/architecture_health/LATEST_AUTOMATION_HEALTH.json`. Verify that report's `red_count` is a positive integer, `status` is RED, and its source run is an authentic completed native main scheduled health run; the GitHub run itself can conclude SUCCESS because the health observer reports a RED fleet without failing. If a source run/issue/report binding is unavailable, do NOT infer RED or pass: record SOURCE_UNVERIFIED as a discovery-block reason and fall through to ordinary sources. At most one additional work item and a bounded original-source read, never a second monitoring schedule.
- The fresh health issue uses the SAME `issue:<n>` key and the ordinary FIX state machine; consult its newest receipt-backed S1_ITEM_v1 BEFORE writing, and do not re-create a discovered item on a later tick. A GREEN/AMBER fleet snapshot does NOT prove that an earlier source or downstream consumer recovered, and an archived FLEET_HEALTH_ONLY receipt is NOT an individual source/consumer completion; require the original consumer's natural production evidence under EVIDENCE_BINDINGS B5. Critical security/privacy/data-integrity risk remains OWNER_GATED. An incident item confers NO new ability to create a code PR, cross the private/public boundary, merge HIGH_IMPACT, waive review, increase API spending, or declare first-known/edge. Use only existing rule 2/5/6 actions and the ordinary risk/lease/review budgets. Cross-repo Alpha/secrets issues remain with their original owners; no key collision across repositories is permitted.
- A discovered item gets one S1_ITEM_v1 (state DISCOVERED) and is triaged within its budget.
- S1_OPEN_WORK_INDEX_v1, once per Copenhagen day inside the heartbeat: counts per state, the 10 most overdue items with key, state and due, the ACTIVE handoffs, ops=<OPEN intents, oldest id> (EVIDENCE_BINDINGS.md B3), closures=<observing>/<verified>/<unverified> with the UNVERIFIED PRs (B5), edge=<stream>:<newest decision> for every stream or edge=ABSENT (EDGE_LEDGER.md), receipts=<key>:<comment id> for every S1_ITEM_v1 this task posted since the previous heartbeat, and cursor=<next source>. It is a comment, never a new file on main.

BRANCH UPDATE (rule 2(c); never main, never force, never a conflict resolution)
- Route 1, preferred: when your tools can send PUT API/pulls/<n>/update-branch, send it with expected_head_sha = H. GitHub performs a real merge and refuses on a conflict.
- Route 2, git data API, only when ALL hold: the PR is not OWNER_GATED, H7 does not apply, every changed file of the PR has status added, modified or removed (no rename), the complete list has at most 100 files, and compare_commits <merge base of H and M>...M shows that main changed NONE of the PR's files (paths and previous paths). Then a merge has no conflict and its tree is exactly: the tree of M with each PR path set to its blob and mode at H (sha null for a removed path). Steps: read the tree of H for the mode and blob of every PR path; create_tree with base_tree = the tree of M and one entry per PR path; create_commit with that tree, parents [H, M] and a message ending with S1-Authored-By: 6ae5fd466b48819187abc224ec0f1c5f; update_ref heads/<branch> to the new commit with force false.
- If main changed any PR file, neither route applies: that is a conflict, handled by rule 2(d) ("@codex address"), never by overwriting.
- Readback for both routes: the branch head is the new commit and its parents are exactly [H, M]; compare_commits M...<new head> lists exactly the PR paths; every PR path's blob at the new head equals its blob at H; and every path that main changed since the merge base still has its blob at M; and compare_commits <merge base of H and M>...M still lists none of the PR paths (a shared path is a conflict, so the overlay would have lost main's change). Any mismatch: post one S1_ITEM_v1 (state TEST, reason branch_update_readback) and do nothing more.
- CONTENT-NEUTRAL: a branch-update commit that passed this readback adds no content of S1's own, so it does not make the head S1_AUTHORED (REVIEW_ADMISSION.md); the new head still needs a new exact-head review, and its new CI runs replace the missing ones. Branch updates count against max_attempts.TEST.
- Neither route possible (no tool, a failed precondition): no update; the item's budget forces a disposition.

DRAFTS
- A draft PR is a work item under the same budgets. When its author route has been silent for 14 days (no commit, no comment by the author route): if its required CI is green on H, it has no unresolved P0/P1 and it is not OWNER_GATED, S1 marks it ready for review (state REVIEW); otherwise the FORCED DISPOSITION TABLE applies to it like to any other item. No draft-to-ready tool: comment only, and the budget forces a disposition.

TOOL FALLBACKS
- No label tool: comment only. No draft-conversion tool: PARKED by comment and label only, and S1 then skips the PR as if it were a draft. No close tool: write the S1_ITEM_v1 with state CLOSED_NOISE and add the item to OWNER APPROVAL REQUIRED as close<n> (the owner presses Close). Discovery, budgets and dispositions never wait for a tool.
