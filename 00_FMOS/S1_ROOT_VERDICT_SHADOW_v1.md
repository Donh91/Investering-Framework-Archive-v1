# S1 ROOT — shadow decision envelope (draft, not a cutover)

Objective: public brief computes deterministic evidence, S1 decides. Existing V1 remains authoritative. This adds a bounded enum-only shadow envelope to the existing producer and no scheduler, permission, credential, policy, saved prompt or production mutation.

## Required review before activation

The public job cannot read the independent private review source or establish its own completed publication. A digest is integrity, not a signature. Bind the served object to the exact repository, trusted bot, successful workflow run and attempt, pinned contract and fresh main. A future public review protocol must originate independently in an authorized public channel; never copy private data or weaken veto rules. Until approved, the private review and all live gates remain mandatory. The current owner-present and HIGH/HIGH_IMPACT exclusions remain unchanged. A conservative NONE is intentional.

| Failure mode | Response |
|---|---|
| stale run, invalid author, edited publication, future timestamp | NONE, no write |
| main or head changed, unknown mergeability, new commit | NONE, do not rebind |
| missing CI tuple, newer job, privacy or gate drift | NONE |
| private exact-head approval or newest veto unreadable | NONE |
| open intent, active halt, owner gate, unclear risk | NONE |
| uncertain action response | do not retry, reconcile from native evidence |
| post-merge blobs or ancestry mismatch | existing halt protocol |
| budget insufficient for mandatory readback | do not start mutation |

## Call budget and trust boundary

Target: at most six orchestration invocations (main, brief+run authentication, live gate bundle, one logical operation, native readback, final receipt). Count underlying native calls separately. The existing intent, merge and three receipts already cost five writes; the old protocol cannot satisfy six *native* calls with all mandatory reads. Do not represent grouping as native call reduction. Do not activate a merge path until a reviewed transactional/receipt design preserves the existing guarantees and has a proven budget. GitHub merge SHA protects the PR head, not the main SHA or simultaneous veto changes; use existing rulesets and fail closed on observable drift. An exact-main-only shadow is conservative and may lower yield; measure before altering drift policy.

## Probe, no writes

No new scheduler and no saved-task edits. Proposed owner-approved diagnostic-only run after review: one orchestration call executes bootstrap and T1–T3 in sequence, records before/after each native call, elapsed monotonic time, exact UTF-8 result bytes, error class/status, and count; emits bounded summary and END marker. Repeat with fixed result sizes and count ladders 1, 2, 4, 6, 8 to distinguish call count from result volume; inject delay separately. If host kills the call before END, mark stop reason UNKNOWN, never infer a cap from absence. Compare scheduled host with interactive replay on the same immutable inputs. Do not use live write actions, and do not replace the saved task before owner approval.

## Rollback

No active consumer changes. Discard draft or revert this additive producer change; no runtime cutover or scheduler change. Before any eventual merge, re-chain all affected lane tree pins, contract and bootstrap in reviewed order. Before activation require exact-head independent approval, tests of authentication, mutable veto/halts, concurrent main/head movement, uncertain merge and readback plus natural scheduled shadow acceptance. Existing acceptance remains intact.
