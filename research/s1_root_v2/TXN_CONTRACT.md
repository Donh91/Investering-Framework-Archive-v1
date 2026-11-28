# S1 merge transaction contract (txn.py)

Maturity: `PATCH_DRAFT` + `REPRODUCED` in simulation only. Nothing here is implemented in the
Archive. `txn.py` is an executable specification of TICK F6/F7 and EVIDENCE_BINDINGS B3/B5 for
ONE lane merge; qualification (F1-F5, T1-T3, H1) is out of scope and is the caller's input.

## 1. Binding and key

`key = sha256("S1_TXN_KEY_v1\nrepo_id=<int>\npr=<int>\nhead=<40>\nbase_main=<40>\nloop_blob=<40>\n")`

Labelled, newline-terminated, fixed order; ints must be positive `int` (not bool), SHAs exactly
40 lowercase hex. The `S1_LANE_MERGE_INTENT_v1` carries `key:` next to its existing fields
(`pr / head / main / repo_id / loop`). An intent is **authentic** only if its author is `Donh91`,
`created_at == updated_at`, and the key recomputes from its own fields. A non-authentic intent
authorises nothing and blocks nothing.

**One merge attempt per key, ever.** A key that appears in any authentic intent, open or
settled, is spent (`NOOP key_spent`). A new attempt needs a new binding (new head, new main or
new loop blob).

## 2. Actions of `plan_step(observed_state, oldest_open_intent_or_None)`

| Action | Native effect | When |
|---|---|---|
| `NOOP(reason)` | none | nothing to do, not allowed, or wait |
| `READBACK(need)` | one read: `pr`, `commit`, `on_main`, `rule_suite`, `head_blobs`, `pr_comments` | evidence missing |
| `POST_INTENT` | post intent on #1156, then re-read #1156 | no open intent, lane not halted, key unspent, PR open at the candidate head |
| `MERGE(sha=intent head, squash)` | one merge call | only in the run that posted the intent, only if that intent is the first authentic one with its key, lane not halted, within `DEADLINE_S` (300 s) of the intent, and no merge call was made yet |
| `POST_RECEIPTS(receipt)` | one post | own success response + OWN readback; origin `S1_RUN` |
| `RECONCILE_OWN(receipt)` | one post | a later run proves OWN natively; origin `UNKNOWN`, `reconciled: True` |
| `RECONCILE_FOREIGN` | `S1_OP_DONE_v1 result: FOREIGN` | merged, but provably not this operation |
| `ABANDON(reason)` | `S1_OP_DONE_v1 result: ABSENT` | `not_merged`, `HEAD_CHANGED`, `DUPLICATE`, `lane_halted`, `deadline` |
| `HALT_UNKNOWN` | `S1_LANE_HALTED` (`readback` or `reconcile_readback`) | merged and neither OWN nor FOREIGN is provable |

`ABANDON` is one action more than the eight named in the task: "not merged" is neither foreign
nor unknown and needs its own settlement.

After any merge call that did not return success (405, 409, timeout, unreadable response) the
run ends `NOOP MERGE_REFUSED(<status>)` with **no retry and no other write** (F6). The intent
stays OPEN and only a later run's native read settles it.

## 3. Classification of an observed merge (`classify`)

Checked in this order; the first match wins.

| Observation | Class |
|---|---|
| PR not merged, head == intent head | ABSENT `not_merged` |
| PR not merged, head != intent head | ABSENT `HEAD_CHANGED` (never re-bound) |
| `merged_by` != `Donh91` | FOREIGN `other_actor` |
| PR head != intent head | FOREIGN `other_head` |
| `merged_at` < intent `created_at` | FOREIGN `before_intent` |
| `merged_at` > intent `created_at` + 900 s | FOREIGN `after_window` |
| merge commit does not have exactly one parent | FOREIGN `not_squash` |
| `merged_at` == intent `created_at` (1 s resolution) | UNKNOWN |
| subject does not end `(#<pr>)` | UNKNOWN |
| merge commit not ancestor of / equal to main | UNKNOWN |
| rule-suite result is not `pass` | UNKNOWN |
| changed blobs != blobs at the intent head (or empty) | UNKNOWN |
| any field malformed or unreadable inside a successful read | UNKNOWN |
| all of the above pass | OWN |
| OWN, reconciling run, and an `OWNER_MERGE_NOTE_v1` for the PR is on #1156 | UNKNOWN `owner_marker` |
| OWN/ABSENT/FOREIGN contradicting this run's own success response | UNKNOWN |

`Donh91` matching is a **necessary** filter only. It never produces OWN. UNKNOWN always halts and
is never reported as a merge.

A native call that *fails* (transport error) is not a classification: the run ends `NOOP
native_error`, writes nothing, and the intent stays OPEN (B3: "stays OPEN and is skipped").

## 4. Receipts and their order

1. `S1_ITEM_v1 state: MERGED` on the PR
2. `S1_CLOSURE_v1` on the PR (consumer closure, B5; a distinct step)
3. `S1_LANE_MERGE_v1` on #1156 (merge evidence; **the commit record, posted last**)

Each cites `intent`, `key`, `merge`. The ledger receipt adds `main_before` (the merge commit's
parent), `base_drift` (parent != intent main), `merge_execution_origin` and `reconciled`.

**Deviation from F7**, which says ledger receipt first. With F7's order the intent is closed
before the PR receipts exist, so a crash there leaves no OPEN intent and RECONCILE never
completes them (B5 repairs a missing closure lazily; nothing repairs a missing
`S1_ITEM_v1 MERGED`). Posting the ledger receipt last makes "intent OPEN" equal "transaction
incomplete", so one mechanism recovers every partial state at no extra cost per tick. Keeping
F7's order instead costs one extra PR-comment read on every tick, forever.

## 5. Recovery table (every row is a test)

| Interrupted after | Durable state | Next run (>= 60 min later) |
|---|---|---|
| nothing / PR read | none | fresh transaction |
| intent post (response lost or crash) | OPEN intent, no merge | `ABANDON not_merged`; key spent |
| intent post, head pushed | OPEN intent | `ABANDON HEAD_CHANGED` |
| merge call, response lost, merge landed | OPEN intent, PR merged | readback, `RECONCILE_OWN` x3, origin UNKNOWN |
| merge call failed / refused | OPEN intent, PR open | `ABANDON not_merged` |
| merge ok, crash before/during readback | OPEN intent, PR merged | readback, `RECONCILE_OWN` x3 |
| 1 or 2 PR receipts posted | OPEN intent | reads PR comments, posts only the missing ones |
| ledger receipt posted | closed | `NOOP key_spent` |
| any point, then a foreign merge (other head, 2 parents, other login, outside window) | OPEN intent | `RECONCILE_FOREIGN`, no merge receipt, no halt |
| any point, merge unprovable | OPEN intent | `HALT_UNKNOWN` |
| second concurrent run sees the intent | - | `NOOP intent_young` |
| two runs both post an intent | two intents, same key | lower comment id merges; the other `ABANDON DUPLICATE` |

## 6. Call budget (measured by `txn_sim.measure_call_counts`, asserted in the tests)

| Path | Calls | Sequence |
|---|---|---|
| ordinary merge | **12** | ledger, PR, post intent, ledger, merge, PR, commit, compare, rule-suite, post x3 |
| NOOP head changed / PR not open | 2 | ledger, PR |
| NOOP lane halted / intent young / key spent | 1 | ledger |
| reconcile OWN | 10 | ledger, PR, commit, compare, rule-suite, PR files, PR comments, post x3 |
| reconcile ABSENT / FOREIGN (other head, time) | 3 | ledger, PR, post |

The `<= ~8` target for an ordinary merge is **not met**: 12 = 7 reads + 5 writes, and the 5
writes (intent, merge, three receipts) are mandated. Honest ways down: fuse commit + ancestry
into one `compare(intent main...main)` when it shows exactly one commit (11); fold
`S1_ITEM_v1 MERGED` and `S1_CLOSURE_v1` into one PR comment (10); drop the rule-suite read if
C10's "no rule bypass" is given another native source (9). Dropping the pre-intent PR read or
the intent re-read would remove a safety property, so they are not offered.

## 7. Residual risks (not provable natively)

1. **Shared identity.** S1 and the owner are both `Donh91`. An owner squash of the intent's
   exact head inside the 15-minute window, after the intent, is indistinguishable from S1's own
   merge whose response was lost. B3 case (i) calls it "the operation"; the kernel reconciles it
   with origin `UNKNOWN`, never `S1_RUN`. Only `OWNER_MERGE_NOTE_v1` (a proposed, optional
   marker) turns it into a halt, and a marker posted after the reconciling run read #1156 is
   missed. `S1_RUN` rests solely on the merging run's own success response.
2. **No atomic intent+merge.** GitHub has no compare-and-set on comments and no base-conditional
   merge. Two concurrent runs are separated by the intent re-read (lowest comment id wins),
   which assumes the comment list is read-your-writes consistent and ids are monotonic. The
   native backstop is that a PR merges once and `sha=` pins the head.
3. **Settle delay is a time assumption.** A reconciler settles an intent after 60 minutes. A run
   that is still alive then, or a merge call that lands more than 60 minutes after it was sent,
   could merge after its intent was settled ABSENT. `DEADLINE_S` bounds when the call is sent,
   not when GitHub applies it.
4. **Main can move between the intent and the merge.** The squash lands on whatever main is
   then. The receipt records `base_drift`; the kernel does not re-run T3 on that drift.
5. **Ledger completeness.** `key_spent`, OPEN detection and the lane halt all assume the whole
   relevant ledger was read. A paged or truncated read of #1156 weakens all three.
6. **Same-second ambiguity.** `created_at` and `merged_at` have 1 s resolution; equality halts.
7. **Duplicate receipts.** Two runs reconciling the same old intent concurrently can each post
   the same receipt (never a second merge, never conflicting outcomes). Comments have no
   conditional create.
8. **Two-parent result of S1's own call.** Cannot occur with `merge_method=squash`; if it did and
   the run died, B3 case (ii) files it FOREIGN without a halt. The run that saw its own success
   response halts instead.
9. **Bypass evidence.** The model reads one `rule_suite` result per merge commit. Which native
   API S1 really uses for "no rule bypass" is not stated in C10/F7.
10. **Simulation only.** The fake GitHub is linearizable and never returns stale reads; the real
    one does not promise that.

## 8. Verification

`python3 -m unittest tests.governance.test_s1_root_v2_txn` (28 tests) from the `files/` root;
`python3 tests/governance/mutants_txn.py` (30 mutants, all must be killed). The fault sweep
runs 17,148 scenarios: every crash point x every foreign event at every position, lost and
failed responses on every call, double crashes, five tampered merges, all 5,018 interleavings of
a duplicate tick, and 4,956 bounded interleavings of concurrent reconcilers. No external
repository was modified.
