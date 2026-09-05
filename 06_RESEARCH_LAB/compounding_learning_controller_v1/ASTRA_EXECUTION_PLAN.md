# Astra Execution Plan — Compounding Learning Controller v1

**Execution state now:** `PAUSED_BY_OWNER_UNTIL_ASTRA`  
**This document authorizes planning only, not implementation before Astra review is explicitly started.**

## Mission

Build the smallest correct autonomous learning controller that compounds framework knowledge over time by converting mature prospective evidence into:

- durable learning;
- calibrated uncertainty;
- explicit contradiction tracking;
- a ranked next-best prospective test;
- a backlog of unresolved questions.

Do this without adding a second adjudication engine or weakening scientific/governance boundaries.

---

## Phase 0 — Fresh-state audit

Before coding, Astra must establish then-current truth.

1. Read current `main` SHA and recent architecture-changing PRs.
2. Read all files in this folder.
3. Audit current:
   - Experiment Lifecycle;
   - Scientific Admission;
   - Unified Experimental Adjudication;
   - learning/outcome memory;
   - research orchestration and handoff manifests;
   - automation/architecture health;
   - repository safety and backup governance.
4. Compare old exploratory branch `agent/task-20260904-compounding-learning-v1` to current main.
5. Produce a salvage table:
   - `KEEP`;
   - `ADAPT`;
   - `DROP`;
   - `NEW_REQUIRED`.
6. Confirm that no newer owner already implements the same responsibility.

**Gate:** no implementation until architecture overlap is understood.

---

## Phase 1 — Freeze responsibility and interfaces

Create or refine a minimal contract defining:

- upstream authoritative inputs;
- immutable identifiers/hashes;
- material-change definition;
- learning-state schema;
- learning-event schema;
- next-best-test proposal schema;
- backlog schema;
- allowed/forbidden authority;
- no-op/idempotency behavior.

Critical boundary:

`Unified Adjudication = WHAT DOES THE EVIDENCE SAY?`

`Compounding Learning = WHAT DID WE LEARN, WHAT IS UNCERTAIN, WHAT SHOULD WE TEST NEXT?`

**Gate:** architecture review must prove no duplicated adjudication logic.

---

## Phase 2 — Build deterministic core

Preferred implementation shape:

- one small controller module under the existing research/experiment or research-learning code ownership chosen by Astra;
- pure/deterministic transformation functions where possible;
- thin I/O wrapper;
- explicit schema versioning;
- append-only event persistence;
- deterministic semantic deduplication;
- conservative missing-input handling;
- zero automatic promotion.

Core functions should include equivalents of:

1. `collect_material_adjudicated_evidence()`
2. `derive_learning_delta()`
3. `update_learning_state()`
4. `enumerate_unresolved_questions()`
5. `generate_candidate_tests()`
6. `rank_tests_for_information_value()`
7. `select_bounded_next_best_test()`
8. `emit_learning_event_and_backlog()`

Do not couple ranking to a specific frontier model. A model may later assist proposal generation, but the contract and persisted evidence surface must remain model-independent.

---

## Phase 3 — Scientific anti-self-deception tests

Astra must add adversarial fixtures covering at least:

- supportive result followed by a required disconfirming test candidate;
- negative result that should weaken but not erase a hypothesis;
- inconclusive result that should preserve uncertainty;
- duplicate semantic experiment variant;
- regime-specific support that must not generalize globally;
- missing outcome / technical failure that must not become market evidence;
- repeated no-op run with no new mature evidence;
- new evidence that is immaterial and should not emit a learning event;
- outcome-peeking attempt;
- proposal attempting to bypass Scientific Admission;
- proposal attempting threshold/weight/canonical change;
- contradictory evidence from multiple experiment families;
- high-information simple test outranking a complex weakly incremental test.

**Gate:** tests must demonstrate that the controller can learn from failure without becoming a self-confirming optimizer.

---

## Phase 4 — Integrate after Unified Adjudication

Preferred operational pattern:

1. Unified Experimental Adjudication finishes and persists current output.
2. Controller reads that persisted output plus bound evidence references.
3. Controller checks whether material new adjudicated evidence exists since prior controller state.
4. If no: deterministic `NO_MATERIAL_LEARNING_DELTA` and no unnecessary write churn.
5. If yes: persist learning event, latest learning state, ranked backlog and bounded next-best-test proposal.
6. Any new experiment proposal enters the existing Scientific Admission route.

Astra should decide whether this is best implemented as:

- a dependent step in the existing weekly adjudication workflow; or
- a separate workflow triggered after successful adjudication.

Default preference: **reuse existing ownership and cadence unless separation materially improves safety/observability.**

---

## Phase 5 — Discoverability and future-agent routing

The implementation is incomplete until future agents can find and understand it.

Astra should minimally add/update the correct existing owners so that:

- architecture guides explain where the controller sits;
- agent routing points to the controller when a task concerns experiment learning, next-test selection or autonomous research improvement;
- the downstream framework handoff manifest exposes latest controller state;
- architecture health checks detect missing/disconnected controller outputs;
- CI path filters include controller code/contracts/tests;
- no duplicate canonical owner is created.

A future audit should be able to answer quickly:

> “Where does the framework convert experimental outcomes into cumulative learning and select the next best prospective test?”

with one obvious path.

---

## Phase 6 — Runtime and autonomy hardening

Before activation:

- deterministic dry run against current repository data;
- verify no retrospective rows are created;
- verify no existing frozen evidence is modified;
- verify no market rule/weight/portfolio effect;
- verify proposal count is bounded;
- verify repeated execution is idempotent;
- verify malformed/missing upstream input fails closed;
- verify git write behavior follows current main-writer concurrency rules;
- verify repository safety / backup requirements for workflow changes;
- verify exact-head PR merge and post-merge readback.

Optional model-assisted proposal generation must fail safely to a deterministic/no-proposal state if unavailable.

---

## Phase 7 — Acceptance criteria

The build is accepted only if all are true:

### Architecture
- no parallel experiment engine;
- no duplicate adjudicator;
- explicit post-adjudication placement;
- new proposals route back through Scientific Admission.

### Scientific integrity
- immutable prospective evidence preserved;
- no hindsight-created evidence;
- contradictions preserved;
- failures produce learning rather than silent deletion;
- next tests are selected for uncertainty/information value, not narrative appeal.

### Autonomy
- can maintain learning state automatically after mature evidence appears;
- can autonomously rank and propose the next test;
- can no-op safely when nothing material changed;
- cannot autonomously promote research into canonical market/portfolio authority.

### Compounding
- every material learning event is traceable to evidence;
- previous learning states remain recoverable;
- test-selection quality can itself be audited over time;
- future controllers/models can compare whether selected tests actually reduced uncertainty.

### Operations
- tests/CI pass;
- workflow order and concurrency are safe;
- main readback verified after merge;
- discoverability/handoff surfaces updated;
- backup/Vault obligations handled under then-current governance.

---

## Phase 8 — Second-order learning (recommended after v1 is stable)

Do **not** overbuild this into v1, but design schemas so Astra can later add meta-learning about the controller itself.

Future questions:

- Which proposed tests actually reduced uncertainty fastest?
- Which test families repeatedly produced redundant evidence?
- Which regimes are under-tested?
- Does the controller systematically over-prioritize fast feedback over high-value slow feedback?
- Are simple tests outperforming complex tests in information gained per unit cost?
- Does evidence that changes framework decisions differ from evidence that merely improves descriptive knowledge?

This is where compounding can become genuinely recursive:

`learn about market -> learn how to test market -> learn which testing strategy learns best`

But v1 must first make the first loop correct, auditable and safe.

---

## Owner restart instruction

When Astra is available, the owner can simply instruct:

> **“Kør Compounding Learning Controller Astra-planen i `06_RESEARCH_LAB/compounding_learning_controller_v1/` fra fresh current main. Audit først, byg derefter autonomt gennem PR/CI/merge/readback, og stop hvis governance eller videnskabelig integritet kræver det.”**
