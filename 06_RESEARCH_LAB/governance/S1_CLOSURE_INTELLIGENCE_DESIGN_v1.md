# S1 Closure Intelligence design v1

Status: CI-0 documentation design. Runtime implementation and promotion require their respective separate reviews.

Provenance: CLOSURE_INTELLIGENCE_ADDENDUM_v1.md, §§4–5, Bridge claude/log, Git blob `d37a6760f5475402a0764d7b23e5cd11f58f5834`, content SHA-256 `aa98feddd95adf53cdcac9da07c201faacf814514a5fb68ad6a89788fa75aaf6`. Original owners: Archive #1156 and #1157. The source sections below are reproduced byte-for-byte.

## 4. (d) The state machine and evidence schema

**States** (one per canonical item, keyed by `item_id = <repo>#<n>`, or `finding:<issue>/<comment>`):

`DISCOVERED → TRIAGED → ASSIGNED → PATCHED → REVIEW_REQUESTED → REVIEWED → RELEASE_READY → MERGED → SERVED_VERIFIED → OUTCOME_CHECKED → CLOSED`

**HOLD states** (sticky until their evidence changes):

`SOURCE_UNKNOWN | SCIENCE_HOLD | CI_FAILED | REVIEW_BLOCKED | OWNER_GATED | DEADLINE_MISSED | SUPERSEDED | STALE_REVIEW`

**Transition rules**, each derived only from native GitHub facts the producer reads:
- **PATCHED:** a PR exists with a head SHA.
- **REVIEW_REQUESTED:** an S1_REVIEW_REQUEST_v1 (Bridge) or an `@codex review` comment exists for **this head**.
- **REVIEWED:** an admissible receipt for **this head** exists:
  - a Claude CLAUDE_REVIEW_v1 APPROVE (rules as in TICK F4); or
  - Codex "no major issues", plus a codex-review-state with commit_sha equal to the head, and no unresolved P0/P1.
  - A Codex `COMMENTED` with findings is **REVIEW_BLOCKED**, not REVIEWED.
  - Self-review never counts: the author is checked against the reviewer.
- **STALE_REVIEW:** the head moved after a REVIEWED. The state goes back to PATCHED, and the old receipt is void (as today).
- **RELEASE_READY:** REVIEWED, every required job success at this head, no open owner gate, and, for science items, `source_asof_evidence` complete. Otherwise SOURCE_UNKNOWN or SCIENCE_HOLD, **even if CI is green**.
- **MERGED:** merged_at is set and the squash commit's blobs equal the reviewed head. **A merge is never CLOSED.**
- **SERVED_VERIFIED:** a receipt with `served_sha256` equal to the built artifact, for items with a consumer (site, API, scheduled output). Items with no consumer skip to OUTCOME_CHECKED, and the registry says so.
- **OUTCOME_CHECKED:** for science items, the lawful cohort matured and N is reported. Otherwise it stays OUTCOME_PENDING.
- **DEADLINE_MISSED:** `now > due_at` and the state is before RELEASE_READY. This is a sticky HOLD with a `next_action` from the registry, for example "move to W49".

**Record fields**, from the owner's list:

```
item_id, owner, product, risk_class, priority, due_at, blocking_dependency,
source_main_sha, pr_head_sha, review_actor, reviewed_head, ci_required, ci_results,
source_asof_evidence, owner_attestation, served_readback, outcome_window, rollback,
state, hold_reason, last_action, next_action, idempotency_key
```

Every assertion carries an evidence id: a comment id, run id or blob. `idempotency_key = sha256(item_id|head|finding)` prevents duplicate requests, and is already enforced by S1's one-request-per-head rule.

## 5. The replay test matrix (CI-1 acceptance, in the W1 harness)

| fixture | expected |
|---|---|
| head moved after APPROVE | STALE_REVIEW, then PATCHED; no READY |
| a required job missing or failed | CI_FAILED |
| CI green, but science source first-known missing | SOURCE_UNKNOWN (never READY) |
| unresolved P0/P1 thread | REVIEW_BLOCKED |
| Codex COMMENTED with findings | REVIEW_BLOCKED |
| Codex reviewing Codex-authored code | REVIEW_BLOCKED (self-review) |
| owner gate open | OWNER_GATED |
| `due_at` passed (RISK-02 W48) | DEADLINE_MISSED, with next_action from the registry |
| merged but no served readback | MERGED (not CLOSED) |
| superseded PR | SUPERSEDED |
| adversarial: forged receipt / edited comment / wrong head | never READY |

**Metrics:**
- 0 false READY across all fixtures;
- 24 shadow briefs agree with manual adjudication before CI-3.

