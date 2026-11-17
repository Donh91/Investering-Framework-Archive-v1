# Supervisor vNext — adversarial architecture review

**Scope:** original #1156; existing S1 task `6ae5fd466b48819187abc224ec0f1c5f`; supplied source-main identifier `82f6cd830fbcd26d77e043da0ad3222abd7cae92`.

**Disposition: DESIGN REVIEW ONLY — NOT ADOPTION-READY.**

I examined only the supplied text. **No tools were invoked, hashes recomputed, repositories inspected, tests executed, reviews requested, or production changes made.** The supplied SHA-256 values identify the evidence packet; they are not independently validated checksums here. This response is adversarial analysis, **not an authenticated detached-review receipt, native GitHub approval, owner consent, or an Astra/API execution claim**.

**The original Claude review of the final integrated proposal remains required before adoption.** The supplied Claude adjudication does not review this recommendation or a final implementation. [V, Verdict; D, §10]

## Executive determination

The safest coherent direction is **an incremental, source-bound steward inside the existing S1 task**, not a replacement supervisor:

1. retain GitHub/main as policy authority;
2. make planning and classification explicitly non-authorizing;
3. authenticate evidence separately from evaluating it;
4. use one designated original-branch writer;
5. separate independent technical review from release authority;
6. reconcile uncertain mutations before attempting another;
7. distinguish merge verification, natural consumer verification, and attributable S1 closure;
8. make Claude optional **only after** a governed reviewer-admission change—not by ignoring today’s Claude-specific lane. [A, §§0.2a–e; O, Remediation and Codex; D, §§1–3, 7]

The principal risks are not insufficient intelligence. They are **identity ambiguity, policy/implementation divergence, incomplete dependency boundaries, non-atomic mutations, and evidence that can be asserted more easily than authenticated**. The supplied code explicitly acknowledges that its classifications do not authenticate callers; current lane policy also acknowledges shared-account review-authentication risk. [C, module and classifier docstrings; A, §0.2e(d)]

**Do not apply the frozen Claude v2 package byte-for-byte.** Its supplied adjudication reports four stale base pins at its own comparison snapshot, accepts the forged-counter and self-review objections, and leaves D4–D8 unverified. That is sufficient to reject blind application, but not sufficient to establish the state of today’s repository. [V, D1–D8]

---

# 1. Evidence register and limits

Citations below use these aliases. Each alias resolves to the **full supplied SHA-256**, not a Git blob SHA.

| Alias | Supplied file | SHA-256 |
|---|---|---|
| **A** | `AGENTS.md` | `4c2cc641e35e07e49e31d16b6aa960bbf6ceb4bd1ae1eb9fb05b2f53d275093a` |
| **L** | `00_FMOS/S1/ACTION_LOOP.md` | `88e94f521b911dad5858e19b7f89e29eaa7636227f25eb95e045a4496f2a62c2` |
| **R** | `00_FMOS/S1/RUNTIME_CONTRACT.json` | `e685d4431e6b02a200f3cbf7c4129a76665c129980ef7cd9c6e7a25a94547dec` |
| **W** | `00_FMOS/S1/REVIEWED_MERGE_LANE.json` | `1aad6b39619c734baecbb9f11da3c54c17861c5d6215bc633809fd556f0b16b9` |
| **J** | `00_FMOS/S1_REQUIRED_PR_JOBS_POLICY_V1.json` | `f38b978b858e4333544b967fce75ea3a2ea3ca09d78df6b92a5e5f38deee4f81` |
| **N** | `00_FMOS/S1_NATIVE_RULE_CENSUS_AND_RELEASE_RECIPE_V1.md` | `e6eec56bae8f9e1a8bc10cd670e87bc8f9c453601b65793292193a92d6179655` |
| **O** | `00_FMOS/AUTOMATION_ORCHESTRATION_ARCHITECTURE_v2.md` | `decaf94323966324a9d48ba54117ec984f7b49b8eabab5d5b3528f185044c8f5` |
| **C** | `scripts/governance/s1_release_evidence_classifier_v1.py` | `32966a3ff3654b5e5d558afc42e1b656c8c7322cd1b99027b73974dd5f0e36ee` |
| **D** | `.../sources/S1_DRAFT.md` | `15cb7e6a6f84407394781f5953b6e7ee47359efc4561d540108c3a6107adcd2d` |
| **V** | `.../sources/CLAUDE_V2.md` | `8f1d9dce1988347e6162754983aedcba1e2545bda93beb37d48c1246a693b007` |

### Evidence classes used here

- **TEXT-VERIFIED:** directly visible in a supplied policy or design.
- **CODE-VISIBLE:** implementation logic visible in supplied source; execution not verified.
- **REPORTED:** another supplied artifact reports a historical inspection or result.
- **MISSING:** necessary original/native evidence was not supplied.
- **PROPOSED:** this review’s design recommendation; not effective policy.

This distinction is required because written governance, queue readiness, CI, native merge, and production consumption establish different facts. [A, §§2, 0.2a; O, Observer versus observed status; C, `classify_release_evidence`]

### Critical missing evidence

The packet does **not** contain:

- original #2194 content, exact source path/blob, comments, or design implementation;
- the complete Claude v2 source package, `STEWARD_STATES.md`, `REVIEW_ADMISSION.md`, build report, or final integrated head;
- the original independent D1–D8 review—only its adjudication and overlapping draft discussion;
- `BOOTSTRAP.txt`, live saved-task text, or authenticated task-run history;
- a tree listing binding the supplied files to the claimed source-main commit;
- the operational cockpit, current #1156/#173/#1593 records, original PRs, or native rules;
- workflow YAML, actual import closures, dependency lockfiles, required-job logs, scanner source, runtime tests, or standing-policy implementation;
- canonical recovery-policy bytes, live custody evidence, restore-drill evidence, or consumer readbacks. [A, preflight and §§0.2c–e; R; J; L, HIGH EVIDENCE; D, §§5–10; V, Sources]

**Consequence:** an actual current operational graph cannot honestly be certified from this packet. The graph below is a **source-grounded declared graph with explicit unverified runtime edges**, not a live inventory. #2194 remains **NOT ADJUDICATED AS AN ORIGINAL SOURCE**. [A, §8; D, §1; V, artifact metadata]

---

# 2. Authority, status, schedule, software and native-tool graph

## 2.1 Authority graph

```text
Canonical safety / public-private boundaries
    │  referenced; full underlying owners missing
    ▼
Current-main AGENTS.md
    ├── §0.2a owner-specific release / stronger safety constraints
    ├── §0.2b original-PR repair and learning route
    ├── §0.2c bounded LOW policy
    │      └── required-jobs manifest: lane_state = SHADOW
    ├── §0.2d runtime-source contract
    │      └── saved task → BOOTSTRAP → RUNTIME_CONTRACT → ACTION_LOOP
    └── §0.2e reviewed-merge lane
           └── switch says ON, conditional on pins/halt/health/all gates

Advisory evidence, NOT authority:
    Bridge scoreboard / review comments / model reports
    release classifier / supplied booleans / receipt summaries

Native enforcement and factual evidence:
    GitHub rules + PR/head + workflow/job/step execution + merge/readback

Natural completion:
    producer → persisted output → receiver → final consumer
```

This hierarchy is supported by the supplied policies. **The manifest’s `SHADOW` and reviewed-lane switch’s `ON` are not, by themselves, contradictory:** §0.2e expressly limits the former to §0.2c. Neither value proves that either lane is currently usable. [A, §§0.2c–e; J, `lane_state`; W; L, AUTHORITY]

The older architecture’s broad automated-merge restriction must not silently erase the later, explicitly scoped §0.2e exception. Conversely, §0.2e must not be interpreted as permission for excluded governance, custody, workflow, payment, or privacy changes. Ambiguity should narrow action, not broaden it. [O, Owner-authorized single-account integration; A, §0.2e Precedence and exclusions]

## 2.2 Current versus proposed status

| Component | What the packet establishes | What it does not establish |
|---|---|---|
| ACTION_LOOP v1.6.9 | Detailed current-design instruction text | Saved task actually loads and follows it |
| Runtime contract | Names task, bootstrap version and full Git object pins | Those objects exist at claimed main or match supplied bytes |
| Reviewed lane | Switch text says `ON`, max batch 3 | Live pins, halt state, native rules, health, owner activation provenance |
| LOW/RP1 lane | Manifest says `SHADOW`, no review waivers | Any permission to use RP1 |
| Classifier | Read-only Python logic, `authorized:false` | Native evidence authentication or hosted execution |
| Privacy scanner | Referenced in policy, manifest and current checklist | Its implementation, completeness or current execution |
| Claude v2 | Design adjudication, reported defects | Complete implementation or production qualification |
| S1 draft | Research architecture proposal | Adopted reviewer route, state machine or scheduler capability |
| #2194 | Requested by the user as a design source | Original contents or current status |
| S1 closure performance | Required measurement semantics | Any verified closure count or prospective outcome |

All runtime cells remain **MISSING** rather than inferred from filenames, prose or status labels. [A, §§0.2c–e, 2; L; R; W; J; C; D; V]

A particular version trap is important: the early §0.2c text says the scanner was “NOT BUILT at proposal time,” while later policy and manifest reference it. Neither statement alone establishes present implementation. The scanner source and native run are still required. [A, §0.2c privacy gate and §0.2e(b); J, `required_job_executed_paths`]

## 2.3 Declared schedule graph

| Declared activity | Schedule | Dependency meaning |
|---|---|---|
| Automation Production Health | 05:30 / 17:30 Copenhagen | Produces fleet evidence |
| Remediation Maturation Controller | 05:45 / 17:45 | Consumes evidence; sole `CODEX_READY` maturation authority |
| Operations Dashboard | 06:00 / 18:00 | Combines health and remediation |
| Existing S1 | Hourly at :45 Copenhagen | Bounded original-PR action |
| S1 heartbeat | First direct scheduled tick at/after 08:45 each local day | Observability, not another scheduler |
| Monday prohibition | 09:30–10:30 Copenhagen | Strict read-only |
| Vault | Own schedule only | S1 may not dispatch, rerun or pass inputs |

The :45 S1 ticks overlap nominally with remediation at 05:45/17:45. That is a potential freshness/concurrency boundary, **not proof of an actual collision**. Cron order does not prove upstream finality. [O, Daily observability order; L, schedule, H1, H4, HEARTBEAT]

**Proposed:** recheck the Monday window immediately before every mutation, not just at run start. A delayed or long-running tick must not cross into a prohibited interval and continue writing. Heartbeat and incident comments are writes too; read-only precedence must remain explicit. Use timezone-aware Copenhagen time, retaining UTC timestamps and the platform’s actual scheduling timestamps when available. [Basis: L, H1 and HEARTBEAT; D, §§0, 7]

## 2.4 Software-dependency graph: established lower bound

```text
ACTION_LOOP
 ├─ reads AGENTS / runtime contract / lane switch / manifest
 ├─ reads Bridge STATUS and #173 review evidence
 ├─ reads native PR, CI, rules, comments and git objects
 ├─ for HIGH: references s1_vault_watchdog_v1.py::valid_seal
 └─ invokes existing connector mutations

s1_release_evidence_classifier_v1.py
 ├─ Python standard library:
 │    ast, re, hashlib, json, datetime, urllib.parse
 ├─ conditional local import:
 │    scripts.governance.s1_general_release_evidence_v1::classify
 ├─ consumes caller-supplied job/review/recovery/source records
 └─ emits advisory JSON; no writer or provider call in supplied source

Required-job policy
 ├─ data-architecture-gate.yml / gate
 ├─ storage-health-gate.yml / storage-health
 ├─ claimed derived required_job_executed_paths
 └─ s1_standing_policy_v1.py --check validates derivation

Reviewed lane additionally requires
 └─ automation-production-health-gate.yml / test
       ├─ full-suite step
       └─ execution-truth step
```

The local import, workflow files, derivation code and referenced tests are **not supplied**. Consequently, the manifest is a declared dependency inventory, not independently reconstructed transitive closure. The third reviewed-lane job also needs its own complete execution dependency accounting; the two-job LOW manifest alone is insufficient to establish that closure. [C, imports and `s1_general_preflight_required`; J; A, §0.2e(c); L, C4, HIGH EVIDENCE]

## 2.5 Native-tool graph and capability boundaries

| Purpose | Named native interface | Required distinction |
|---|---|---|
| Resolve policy/source | branch, contents, git/tree reads | Git object identity versus supplied SHA-256 |
| Discover originals | PR list, PR details, paginated changed files | Complete repository-qualified identity, not PR number alone |
| Authenticate review | issue comments, review threads, native reviews, Bridge blob | Advisory report versus native approval |
| Establish CI | workflow runs → jobs → steps/logs | Correct repository/event/code SHA and actual execution |
| Establish rules | branch/protection + exhaustive ruleset lists/details | Disabled/evaluate/active; optional endpoint failure is not empty rules |
| Merge | native squash API with expected head | HEAD condition does not atomically bind main, comments or rules |
| Verify outcome | PR merge + commit/tree/ancestry + native rule evidence | HTTP success is not full readback |
| Attribute S1 | native task-run record | GitHub account identity is not scheduled-task identity |
| Prove completion | domain-native producer/receiver/consumer evidence | CI and observer success are not consumer success |

These interfaces are **named by the source**, not demonstrated as available in this session. In particular, the draft reports a C7 endpoint allowlist failure, while ACTION_LOOP instructs generic REST fetches; neither proves actual current connector capabilities. [L, C2–C10 and HEARTBEAT; N, §1; D, §§5, 7]

---

# 3. Comparative adjudication

## 3.1 Baseline, Claude v2 and independent critique

| Dimension | v1.6.9 / supplied current policy | Claude v2 as described | Adversarial disposition |
|---|---|---|---|
| Authority | Main-rooted runtime and conditional lane | Stacked package with reported stale pins | Rebuild from fresh main; never transplant frozen authority |
| Review | Claude-specific exact-head lane; acknowledged behavioural identity | S1 specialist receipt could satisfy independence | Specialist = preflight only; replace only through governed admission |
| Closure | Strong merge-readback rules, limited long-lived reconciliation | Time/budget “noise” signals and counters | No count/age-driven original closure |
| Concurrency | H7 heuristic; optimistic HEAD checks | One-writer intent | Intent/comment is not a lock |
| Recovery | App receipt, native evidence, separation; bootstrap fallback | Proposed evolution | Preserve independent recovery, tighten availability proof |
| CI | Three reviewed-lane jobs; selected step execution | Isolation work, reported remaining dependency defects | Verify trusted gate code and untrusted-code isolation separately |
| Liveness | One task, heartbeat, bounded candidates with ambiguity | Daily-summary and loop-control changes | Keep one task; resolve budgets explicitly |
| Completion | Merge receipt distinct from production readback | Steward closed-loop states | Require causal consumer and run-origin evidence |

The Claude adjudication directly accepts D1–D3 and explicitly does **not** independently verify D4–D8. The draft’s account of an import fix, roughly 58 write jobs and review status is also **reported evidence**, not a source-audited inventory here. [L; A, §0.2e; D, §§5–7, 10; V, D1–D8]

## 3.2 D1–D8: requirements that survive this review

- **D1 — stale pins:** accepted. However, the reported comparison was against `b3706fa5`, not a proven tree at the supplied source-main. Do not call the current packet internally stale merely because its values differ from an earlier report. [V, D1; R; W]
- **D2 — counters and closure:** accepted and strengthened. Even authenticated time/budget counters do not prove duplicate, supersession or falsification; they may justify parking, not closing. Objective evidence still requires an authorized closer. [V, D2; D, §2]
- **D3 — self-review:** accepted. The proposed LOW sampling exception is not adopted here: a 1-in-5 audit cannot retrospectively create independence for the other four releases. Any review waiver must be explicit policy, accurately named, and evaluated as a waiver. [V, D3; A, §§0.2c–e]
- **D4 — write-token custody:** accepted, unverified. A “non-secret” writer remains privileged; token provenance and transitive execution matter more than a literal `secrets.` search. [V, D4; D, §6; A, §0.2e exclusions 3 and 10]
- **D5 — one scheduler:** accepted. Integrate summaries into the existing tick; no new task or workflow. [V, D5; L, HEARTBEAT; D, §0]
- **D6 — budgets:** accepted. Limits cannot justify incomplete pagination being treated as complete. [V, D6; L, H6; N, §1]
- **D7 — partial failure:** accepted, but “write intent first” is insufficient: intent creation can itself time out, and shared-account intent text cannot authenticate execution. [V, D7; L, C9 and RECONCILE; D, §7]
- **D8 — lateness:** accepted. Record native clocks; absent platform history means unknown liveness, not a fabricated execution count. [V, D8; L, HEARTBEAT; D, §7]

---

# 4. Concrete technical findings

## 4.1 Unsafe pins and source transitions

**Finding:** source pins are necessary but not self-authenticating. A switch containing expected Git SHAs does not prove that current main has those objects, that the saved bootstrap matches, or that the owner authorized the transition. Updating all pins to match an unsafe tree can produce internal consistency without legitimate authority. [R; W; A, §§0.2d–e]

**Proposed correction:**

- verify full commit/tree/blob identities from one immutable source snapshot;
- distinguish `pin_consistent`, `source_reachable`, `activation_authorized`, and `runtime_consumed`;
- keep old and new contract identities in transition evidence;
- never update pins merely to clear a failing lane;
- require the final integrated policy/runtime/switch/tests to be reviewed together;
- do not drop unfinished operations when the contract changes. [Basis: A, §§0.2a, 0.2d–e; L, RECONCILE; V, D1]

The current reconcile rule expressly discards older-contract intents. That accepted gap is unsafe as a general recovery architecture: upgrading instructions must not erase responsibility for an earlier uncertain mutation. [L, RECONCILE]

## 4.2 Shared-account identity does not prove independence or S1 execution

The current review lane requires an unedited owner-account comment plus a Bridge report, request linkage and exact head. Those checks improve binding, but the policy expressly acknowledges that multiple agents can post as the same owner. A report blob proves **content identity**, not who independently reasoned about it. [A, §0.2e(d); L, C5]

The same problem affects re-enable provenance: “merged by Donh91 but not S1” cannot be inferred from the GitHub login alone where the principals share that identity. It needs separately authenticated interactive/run provenance. [A, §0.2e Lane state 3 and accepted residual risk; D, §§1, 3]

**Proposed correction:** represent separately:

```text
technical_authorship_independence
review_execution_provenance
native_GitHub_review_state
owner_authorization
scheduled_task_origin
```

A missing value cannot be filled by another field. If current tools cannot authenticate a required dimension, retain a bounded HOLD; do not invent a reviewer account or “independent specialist.” [Basis: A, §§0.2a–e; C, authentication disclaimers; D, §3]

## 4.3 Source-visible classifier drift

The supplied classifier is responsibly labelled advisory, but several paths no longer mirror the newer policy:

- `_claude_review_is_valid` accepts `SELF_AUTHORED_DESIGN` for LOW.
- Required jobs are selected by `name`, not consistently by workflow-path/job-ID identity.
- `active_writer_lease` must be exactly `False`; it cannot express the approved RP1 meaning of `null`.
- `source_science_gate` must be `PASS`; it cannot express approved, scoped non-applicability.
- HIGH recovery freshness is capped at 86,400 seconds, while ACTION_LOOP describes a 30-hour recovery receipt window.
- HIGH owner evidence is structurally checked through booleans and a comment URL; that does not prove interactive owner presence.
- The changed-test census contains legacy compatibility paths that do not require the modern complete-census evidence.
- Merge blob representation requires SHA-valued entries and does not clearly represent verified absence for a deleted path. [C, `_claude_review_is_valid`, `_changed_test_execution_issue`, `classify_pr_disposition`; A, §0.2c D4/D5 and §0.2e; L, HIGH EVIDENCE]

These are **not demonstrated autonomous exploits**: the classifier returns `authorized:false` and delegates authentication to its caller. They are nevertheless dangerous if a future adapter treats `READY_TO_MERGE` as a permission token or fabricates inputs to satisfy old logic. [C, classifier docstrings and return paths; A, §0.2c activation prerequisites]

**Proposed correction:** version admission semantics explicitly; fail on incompatible policy versions; remove review-name ambiguity; represent deletions/modes; keep legacy analysis separate from new release qualification. Never “fix” incompatibility by substituting `false` for unknown lease state or `PASS` for non-applicability. [Basis: C; A, §0.2c F8/F9/F10; J]

## 4.4 Checklist inconsistencies are specification defects

Four source-visible ambiguities deserve immediate repair:

1. **C1 says H1 and H7 “do not apply.”** Read literally, this conflicts with the mandatory Monday and foreign-writer stops. The stricter rule must prevail, but the checklist should say “neither stop is triggered,” not use waiver-like wording.
2. **H6 says three deep candidates, with a batch parenthesis allowing `max_merges_per_tick + 2`—up to five.**
3. **Rule 2(c) instructs branch updates; C2 says S1 has no branch-update tool.**
4. **“One write” describes a logical batch that includes multiple intents, merges and receipts, while heartbeat is excluded.** It is not one atomic mutation. [L, H1, H6, H7, rule 2, C1, C2, C9–C11, HEARTBEAT]

**Proposed correction:** define one logical work action, its permitted mutation substeps, a separate small observability budget, and an explicit capability map. No available branch-update tool means delegation to the existing authorized writer or owner—not an invented operation. [Basis: L; D, §§1, 5, 7]

## 4.5 Reconciliation can misattribute or abandon a merge

The current intent filter uses owner-account authorship, unedited text, an eight-character contract, timing, PR head and one-parent squash shape. It does not establish that scheduled S1 performed the merge. An owner-interactive squash in the permitted interval can match those characteristics. [L, RECONCILE and C9–C10; A, §0.2c Receipts; N, R12]

Additional gaps:

- intents younger than 60 minutes are not reconciled;
- intents older than 24 hours are dropped;
- contract changes drop older intents;
- missing evidence may be recorded as unavailable in a reconstructed merge receipt;
- no task-run linkage is required by that intent filter. [L, RECONCILE]

**Proposed correction:** native merge verification may be recovered without claiming S1 attribution. Use separate results:

```text
MERGE_NATIVE_VERIFIED
MERGE_ACTOR_ORIGIN_UNKNOWN
S1_SCHEDULED_ORIGIN_VERIFIED
POST_FIX_OBSERVATION
```

Unresolved operations survive upgrades and elapsed time. Missing receipt data remains a material evidence gap; it must not be counted as complete closure. [Basis: A, §0.2c Receipts and kill rules; L, RECEIPTS; D, §§1–2, 7]

## 4.6 Native CI success can conceal unexecuted safety work

The current policy correctly requires specific successful jobs and two executed test steps. However, its general acceptance of other `NEUTRAL`/`SKIPPED` checks cannot replace independently establishing **all applicable native and domain-required work**. A combined status or matching job display name is insufficient. [A, §0.2e(c); L, C4; J, qualification; N, R09/R24]

A privacy log line also proves little unless the scanner implementation, workflow identity, event, checked-out code, step execution and log origin are bound. PR code could potentially print the same line; whether present workflow isolation prevents that is **MISSING evidence**. The review-based fallback must authenticate the underlying run, not merely repeat its ID. [A, §0.2e(b); L, C3; D, §6]

**Proposed correction:** separate:

- trusted policy evaluator;
- isolated execution of candidate code/tests;
- source-bound execution results;
- native collector that authenticates those results.

Do not prohibit all imports of PR code: testing necessarily executes candidate code. Prohibit **authority-deciding gate logic** from being replaced by the candidate, and prohibit untrusted execution from inheriting write credentials or secrets. [Basis: V, D4; D, §6; J, qualification]

## 4.7 Workflow execution closure is broader than imports

The supplied policy excludes secret-using code and added repository-write capabilities. That is valuable but insufficient as a complete capability boundary: changing data, configuration or a helper argument can redirect an existing writer without adding a new `git push` or API call. [A, §0.2e exclusions 3 and 10; D, §6]

**Proposed dependency analysis must cover:**

- Python imports, package initializers, `sys.path`, dynamic loaders and plug-ins;
- shell sourcing, subprocesses, executable scripts and generated commands;
- reusable workflows and local/composite actions;
- configuration, templates and files interpreted as commands or publication inputs;
- checkout credentials, `github.token`, environment tokens and persisted git credentials;
- hooks, git configuration, symlinks, path traversal and checkout/ref selection;
- artifact/cache transfer from untrusted to privileged jobs;
- public-output rendering and private-data provenance. [Basis: D, §6; A, §0.2e; V, D4]

Static discovery is a lower bound. Unresolved execution edges should produce **UNKNOWN / LANE_EXCLUDED**, not an empty dependency set. The reported “roughly 58” jobs must be reconstructed from actual workflows before it is used as an inventory. [D, §6; V, D4]

## 4.8 Health workflow success is not healthy production

§0.2e checks recent successful execution of the scheduled health observer. The orchestration architecture expressly permits that observer to succeed after publishing a RED fleet report. Therefore, the current condition is an **observer-liveness gate**, not proof that the fleet or affected consumer is green. [A, §0.2e Lane state 4; O, Observer versus observed status]

**Proposed correction:** preserve observer liveness, and separately evaluate the affected domain’s current report/output. Do not require the entire unrelated fleet to be green, and do not misname successful RED publication as production recovery. [Basis: O; A, §0.2a postmerge requirements]

## 4.9 Recovery evidence and source-write authority must remain separate

Recovery receipt freshness, valid seals, restoration evidence, source ancestry and independent custody are distinct requirements. The supplied watchdog implementation and receipts are absent. The source-specific separation attestation also lapses under stated conditions; its comment IDs cannot prove those conditions remain unchanged. [L, HIGH EVIDENCE; A, permanent invariant]

The initial Claude fallback must not persist merely because the App’s first receipt was not found in an incomplete comment search. Likewise, read access to Vault is not generally equivalent to destructive authority, but the current S1 attestation explicitly treats such access as a lapse trigger and must be obeyed. [L, HIGH EVIDENCE; A, permanent invariant]

**Proposed correction:** verify recovery through permitted value-free evidence and independently maintained custody facts. Never obtain Vault access, dispatch a recovery workflow, or change credentials to make a source release possible. Unknown separation remains fatal for affected high-impact actions. [Basis: A, §§0, 6; L, H4 and HIGH EVIDENCE]

---

# 5. Recommended in-house steward architecture

## 5.1 Roles, without another agent service

**PROPOSED:** implement the following as bounded responsibilities of the existing S1/operator and existing source modules—not new schedulers, workflows, identities or queues. [Basis: A, §§0.2b–e; O, queue continuity and remediation; D, §§0–3]

| Role | Preferred existing participant | Constraint |
|---|---|---|
| Source resolver | Existing S1 | Current-main authority first |
| Advisory planner | Existing S1 + pure deterministic reducers | Always non-authorizing |
| Code writer | Existing Codex route by default | One original branch, bounded task, no parallel writer |
| Technical reviewer | Qualified existing nonauthor Codex route, or separately qualified detached reviewer | Authenticated nonauthorship/context; no self-review |
| Integrator | Existing authorized S1 lane or owner-interactive integrator | Current policy and native rules |
| Consumer verifier | Existing domain owner, S1 evidence collector | Natural causal evidence |
| Adoption critic | Original Claude reviewer | Required for this design’s final adoption |

Prefer coordinator-only S1 over routinely alternating author/reviewer/integrator roles. If an existing authorized direct-repair path is retained, authorship must disqualify S1 from claiming independent review of that head. [Basis: O, intelligent orchestration; L, rule 2/H2; D, §3]

### Claude optionality: exact boundary

- **Today:** the supplied §0.2e lane requires admissible `CLAUDE_REVIEW_v1`; Codex commentary cannot silently substitute.
- **Future:** a reviewed governance change may admit an authenticated nonauthor in-house reviewer route.
- **Unavailable independent reviewer:** continue discovery, permitted repair, testing and evidence gathering; block release requiring that review.
- **Owner consent:** cannot erase a concrete P0/P1 or fabricate independence.
- **Adoption:** original Claude review remains mandatory for this proposal even if runtime Claude later becomes optional. [A, §§0.2a–e; L, C5; D, §3; V, D3 and Smallest next step]

## 5.2 Pure decisions versus authenticated adapters

```text
Native read adapter
    → immutable source/evidence snapshot
    → pure advisory reducer
    → proposed action + exact missing gates
    → independent authorization evaluation
    → capability-constrained native mutation
    → native readback
    → later natural consumer observation
```

The reducer should never accept a caller’s `authorized:true` as sufficient. Native adapters establish provenance; policy evaluation establishes applicability; native platform rules constrain the mutation. No one layer can impersonate the others. [Basis: C, classifier disclaimers; A, §§0.2c–e; D, §1]

**Recommended initial scope:** one original work item and one logical mutation action per tick; no merge batching during qualification. Preserve a maximum of three deeply inspected candidates, with exhaustive required reads for whichever candidate proceeds. This reduces recovery and attribution complexity; it is a proposed restriction, not a claim about current limits. [Basis: L, H6/C11; V, D6–D7]

Tool and wall-clock budgets should be fixed before the pilot using observed connector costs. Exhausting a budget yields `EVIDENCE_BUDGET_EXHAUSTED`, never a completed census or a review waiver. [Basis: V, D6; N, §1; D, §9]

---

# 6. Exact source, branch, head and action contract

The following is a **proposed logical contract**, to be incorporated into existing owned receipts/records where appropriate. It is not a new canonical store or a ready-to-submit schema. [Basis: D, §1; O, queue continuity]

```yaml
work_identity:
  owner_issue: 1156
  original_repo_id: <native immutable repository identity>
  original_repo_full_name: Donh91/Investering-Framework-Archive-v1
  original_issue_or_pr: <number>
  original_pr_node_id: <native identity>
  source_design:
    issue: 2194
    evidence_status: MISSING_UNTIL_NATIVE_SOURCE_SUPPLIED

execution_origin:
  task_id: 6ae5fd466b48819187abc224ec0f1c5f
  task_run_id: <native value or UNKNOWN>
  trigger_kind: DIRECT_SCHEDULED | RUN_NOW | OWNER_INTERACTIVE | UNKNOWN
  scheduled_for: <native timestamp or UNKNOWN>
  started_at: <native timestamp or UNKNOWN>
  provenance_reference: <independently readable source or UNKNOWN>

source_snapshot:
  main_commit: <full SHA>
  agents_blob: <full Git blob SHA>
  bootstrap_blob: <full Git blob SHA>
  runtime_contract_blob: <full Git blob SHA>
  action_loop_blob: <full Git blob SHA>
  lane_switch_blob: <full Git blob SHA>
  job_manifest_blob: <full Git blob SHA>
  recipe_blob: <full Git blob SHA when applicable>
  dependency_graph_digest: <SHA-256 of authenticated graph>
  rule_snapshot_digest: <SHA-256 plus underlying native sources>

branch_binding:
  base_repo_id: <native identity>
  base_ref: main
  head_repo_id: <native identity; may differ for a fork>
  head_ref: <explicit exact ref>
  expected_head: <full 40-character SHA>
  branch_exists: <authenticated>
  default_or_backup_branch: false
  designated_writer: <existing admitted principal or UNKNOWN>
  exclusive_lease: <native evidence or UNKNOWN>

action:
  kind: REPAIR | REQUEST_REVIEW | MERGE | RECONCILE | OWNER_CARD
  allowed_paths_and_operations: <exact bounded set>
  expected_before_state: <native state fingerprint>
  intended_change_digest: <patch/action payload hash>
  operation_key: <SHA-256 of canonical immutable action identity>
  mutation_substeps: <ordered bounded list>
  planner_authorized: false

evidence:
  complete_diff_digest: <paths, rename sources, statuses, modes, content bindings>
  review_request: <native source and exact head>
  review_execution: <nonauthorship and provenance>
  required_job_tuples: <workflow path, job identity, run attempt, execution SHA>
  recovery_and_separation: <applicable native evidence or NOT_APPLICABLE_BY_POLICY>
  consumer_contract: <existing domain owner and required natural readback>
```

### Binding rules

1. **Repository identity precedes branch name.** `main` in a fork is not Archive main. PR `#2190` without repository identity is ambiguous. Mutations target the actual `head.repo` and explicit `head.ref`, or stop if unauthorized. [Basis: D, §§7, 10–11; A, §6]
2. **Use full hashes internally.** Eight-character values are display abbreviations, not durable operation identity or adequate cross-version reconciliation keys. [Basis: R; L, RECONCILE/RECEIPTS; D, §1]
3. **An operation key is not a lock.** It deduplicates intended work but cannot prove no other actor wrote or merged. [Basis: D, §7; A, §0.2c D4]
4. **A branch writer is separate from main writers.** H7’s recent-commit heuristic is not proof of exclusive ownership; `framework-main-writer` does not, from the supplied text, establish a lock shared with ChatGPT connectors. [Basis: L, H7; O, Acceptance]
5. **Expected HEAD is not expected main.** A native merge’s head condition does not atomically freeze policy, rules, review comments or base branch. Report the residual race rather than claiming an atomic authorization transaction. [Basis: A, §§0.2a and 0.2c F3; N, Race and bypass]
6. **For code, qualify the integration context.** Exact-head review alone may miss semantic interaction with changed main. Documentation reuse can follow the narrowly governed disjointness rule; code should receive renewed review/testing against current integration context. [Basis: A, §0.2c D3; J, `review_reuse`; L, C1b/C2]
7. **Readback includes tree semantics.** Verify additions/modifications, deletion absence, rename source/destination, file modes and symlink/gitlink treatment—not only positive blob SHA equality. Unknown or unsupported object types stop the affected release. [Basis: A, complete-diff gate; C, merge blob validation; D, §2]

### Multi-file writes

**PROPOSED:** prefer an existing tool path that creates a single commit from the expected parent and performs a non-force, conflict-detecting ref update. Do not represent a series of per-file Contents API writes as atomic. A blob-SHA precondition is not a whole-branch transaction; a non-force ref update is not automatically a general compare-and-swap lease. If available tooling cannot safely implement the bounded change, delegate to the existing admitted writer or stop. [Basis: A, §6; D, §§1, 7; V, D7]

---

# 7. State machine and safe re-admission

## 7.1 Work lifecycle

**PROPOSED:**

```text
DISCOVERED
  → TRIAGED
  → BUILD_AUTHORIZED
  → BUILD_IN_PROGRESS
  → TEST_EVIDENCE_PENDING
  → REVIEW_PENDING
  → QUALIFIED_FOR_NATIVE_RECHECK
  → MUTATION_INTENT
  → MUTATION_OUTCOME_UNKNOWN | MERGED_NATIVE
  → MAIN_READBACK_VERIFIED
  → POST_FIX_OBSERVATION
  → CLOSED_VERIFIED
```

Side states:

```text
BLOCKED_WITH_TRIGGER
PARKED_OPEN
OWNER_ACTION_REQUIRED
RESEARCH_ONLY
SUPERSEDED_PROVEN
REJECTED_WITH_EVIDENCE
HALTED
```

`QUALIFIED_FOR_NATIVE_RECHECK` is deliberately not an authorization token. `CLOSED_VERIFIED` is an evidence disposition, not an automatic GitHub issue-close command. [Basis: C, advisory disposition; D, §2; O, queue continuity]

## 7.2 Required transition evidence

| Transition | Minimum causal evidence |
|---|---|
| Discover → triage | Original identity, authoritative owner, dedupe and risk |
| Triage → build | Reproducer, bounded paths, tests specified before fix, permitted writer |
| Build → test | Actual branch/head and complete intended diff |
| Test → review | Correct PR-event execution, privacy, positive and adversarial tests |
| Review → qualification | Genuine exact-head nonauthor review, complete findings disposition |
| Qualification → mutation | Fresh source, rules, CI, review, writer and applicable recovery gates |
| Mutation → readback | Native outcome, exact merge/tree/ancestry and no bypass |
| Readback → observation | Registered existing consumer contract and expected natural trigger |
| Observation → verified closure | Natural causal output consumed successfully, independent evidence check |

These bridge requirements follow the source’s distinction between readiness, execution, merge and actual consumption. [A, §§0.2a, 4a; O, Remediation and Codex; D, §2]

## 7.3 Ambiguous writes

On timeout or broken connection after any mutation:

1. enter `MUTATION_OUTCOME_UNKNOWN`;
2. do not infer failure from the missing response;
3. query native state using the immutable operation binding;
4. if the effect exists, verify it and finish evidence publication;
5. if the effect is definitely absent, re-qualify before another attempt;
6. if uncertainty persists, stop that mutation and preserve the unresolved operation.

This applies to code writes, review requests, merge intents, merges and receipts—not only merge calls. A 405/409 remains STOP under current policy. [Basis: L, C9; D, §§1, 7; V, D7]

## 7.4 Safe re-admission triggers

| Blocker | Valid re-admission trigger | Invalid trigger |
|---|---|---|
| Stale head/review | New head fully tested and independently reviewed | Old approval copied forward |
| Reviewer quota | Actual qualified review becomes available | Thirty minutes elapsed |
| Unknown writer | Authenticated handoff/release and fresh head | Comment claiming “lease=false” |
| Missing native CI | Correct job/steps finish and are authenticated | Green dispatch or combined status |
| Source/pin drift | Governed source restored/adopted and freshly resolved | Replacing expected pin with observed value |
| Recovery expiry | New admissible independent evidence | Editing receipt time |
| Ambiguous mutation | Native outcome established | Missing receipt |
| Privacy unknown | Complete approved provenance/scan evidence | No token-like string found |
| Lane halt | Existing owner-controlled re-enable path satisfied | Agent comment saying cleared |
| No eligible work | New eligible original or material evidence | Clock tick alone |

A material fingerprint should include review content/revision, required execution evidence, source bindings and causal blockers. It should exclude irrelevant observation-clock churn—but **not erase security-relevant edits**. [Basis: C, `finish/material_value`; A, §0.2c D7–D9; D, §§1, 7]

## 7.5 Reviewer quota and starvation

Review requests should deduplicate by repository, original PR, exact head, requested scope and request provenance. An unresolved request is not an unlimited retry license. Codex silence, quota exhaustion or Claude unavailability is an explicit dependency state; no paid fallback or automatic model switch is authorized. [Basis: L, rule 3; O, Codex event finality; D, §§3, 8, 11]

The current “ANSWER first” rule can potentially consume repeated ticks with new requests. **Proposed:** keep responses bounded and deduplicated, and measure answer-induced delay; any priority change must be reviewed rather than silently overriding the ladder. [Basis: L, ROLE and LADDER; V, D6]

---

# 8. Actual S1-owned closure and consumer proof

A merge made by `Donh91` is not necessarily a scheduled S1 merge. A correctly shaped intent is not run provenance. An external repair coordinated by S1 is not S1-authored code. These distinctions must survive into evaluation. [A, §0.2c Receipts; N, R12; L, HEARTBEAT; D, §§2, 9]

**PROPOSED attribution fields:**

```text
discovered_by
triaged_by
code_authored_by
reviewed_by
merge_executed_by
merge_execution_origin
consumer_verified_by
closure_adjudicated_by
```

Credit separate outcomes:

- **S1-coordinated work:** attributable coordination, irrespective of who merged.
- **S1-scheduled merge:** authenticated task-run origin plus native merge.
- **S1-owned verified closure:** attributable scheduled action and full original-work/consumer completion under a frozen definition.
- **Owner-assisted closure:** explicit owner interaction contributed to release.
- **Origin unknown:** native outcome exists, scheduled attribution absent.

No field should be inferred solely from the shared account. [Basis: A, §0.2c Receipts; D, §§2, 9; C, authentication disclaimers]

### Consumer chain

For each consequential producer/consumer change, require:

```text
approved code/source
 → natural producer run
 → exact persisted object and source identity
 → manifest/index inclusion
 → receiver acceptance
 → final consumer output/readback
 → retention/growth evidence
```

The contract must identify the existing owner at every edge. A successful observer publishing RED is not receiver acceptance; a site build is not necessarily deployed-site consumption; a source file on main is not proof the saved S1 task loaded it. [A, §4a; O, Observer versus observed status; D, §§2, 7]

For producer incidents covered by §4a, retain the stronger conditions: unrelated-PR CI, replay counts, no lost evidence, independent review and 72-hour stable growth. For documentation without a production consumer, predefine the legitimate documentation/runtime acceptance evidence; do not invent a market or website consumer. [A, §4a(7); D, §2]

---

# 9. Fifteen ranked fixes

All are **proposed patches or qualification work in existing owners**, not authorization to implement now.

| Rank | Priority | Fix and implementation target | Dependency / acceptance |
|---:|---|---|---|
| **1** | P0 | **Freeze authentic source and resolve stale-pin transitions.** Rebuild final package from current main; bind bootstrap/runtime/switch/policy/tests. | Original source/PR evidence and original Claude final review. No blind v2 apply. [R; W; V, D1] |
| **2** | P0 | **Remove self-review admission.** Specialist output becomes preflight only; reject self-authored/mixed-author review unless a genuinely nonauthor reviewer is proven. | Governed reviewer schema/admission; negative identity tests. [C, `_claude_review_is_valid`; V, D3] |
| **3** | P0 | **Eliminate forged/time-driven closure.** Ignore unverified counters for authority; park valuable originals open. | Objective native evidence plus explicit closure policy/authorized closer. [V, D2; D, §2] |
| **4** | P0 | **Authenticate full original/fork identity.** Bind repository IDs, PR identity, head repository/ref and expected head before writes. | Exact #2190 evidence is missing; repair only on authenticated original. [D, §§7, 10–11] |
| **5** | P0 | **Isolate release-gate evaluation from candidate code.** Authenticate trusted workflow/evaluator source and sandbox untrusted tests without write secrets. | Actual workflow/source closure; hosted negative controls. [A, §0.2e; V, D4] |
| **6** | P0 | **Derive privileged execution closure.** Include imports, configs, shell, reusable actions, checkout credentials and artifact transfer. | UNKNOWN means excluded; reported job counts independently reconstructed. [D, §6; J] |
| **7** | P0 | **Durable ambiguous-write reconciliation.** Cover every mutation; survive contract upgrades and >24-hour gaps. | Native outcome reconstruction; no blind retries or false attribution. [L, RECONCILE/C9; V, D7] |
| **8** | P0 | **Strengthen recovery/custody verification.** Preserve technical receipt versus release assessment separation; no Vault capability expansion. | Actual seal implementation, native recovery and current separation evidence. [L, HIGH EVIDENCE; A, invariant] |
| **9** | P1 | **Unify native CI identity/execution truth.** Workflow path + job identity + attempt + checked-out SHA + substantive execution. | Skipped/masked/wrong-event cases fail; changed-test guards proven. [J; C; N, R07/R09/R24] |
| **10** | P1 | **Resolve checklist contradictions.** C1 wording, 3-versus-5 budget, branch-update capability and logical-versus-physical writes. | Source tests against exact instruction contract; no policy weakening. [L, H6, rule 2, C1/C2/C9] |
| **11** | P1 | **Make rule and health adapters complete.** Exhaustive two-pass pagination; exact health workflow/event/repo; separate observer and fleet status. | Tool compatibility demonstrated without endpoint-based permission inference. [N, §1; O; D, §5] |
| **12** | P1 | **Define one-writer handoff.** Codex default writer; S1 does not race outstanding address requests or infer leases. | Fresh original head and explicit handoff; no force update. [L, H7; D, §§1, 3] |
| **13** | P1 | **Bind task-run provenance and heartbeat.** Distinguish direct scheduled, run-now, owner-interactive and unknown. | Native history if available; otherwise no scheduled-closure credit. [L, HEARTBEAT; D, §7] |
| **14** | P1 | **Make consumer closure first-class.** Per-original causal producer/receiver/consumer contract and completion receipt. | Genuine natural observation, applicable growth/retention proof. [A, §4a; O; D, §2] |
| **15** | P2 | **Adopt bounded in-house reviewer routing and prospective evaluation.** Claude optional only after policy admission; quota HOLD stays honest. | Fixes 1–14, original Claude review, hosted qualification and owner-controlled rollout. [D, §§3, 9–10; V, Verdict] |

**Sequencing:** fix authority and evidence foundations before widening autonomy. Dependency-isolation work and mutation recovery are prerequisites to increased merge throughput; throughput tuning is not the first task. [Basis: V, Smallest next step; D, §10]

---

# 10. Adversarial negative tests and fault injections

These are **specified tests, not executed results**. They should be incorporated into existing tests and native PR jobs through separately reviewed changes—no new workflow or production fault injection is authorized here. [A, §0.2a; D, §§10–12; V, D4/D7]

## 10.1 Negative acceptance matrix

| ID | Adversarial input | Required outcome |
|---|---|---|
| N01 | Branch copy of AGENTS/recipe is weaker than main | Main authority only; candidate rejected |
| N02 | All pins updated consistently but no valid activation evidence | Consistency does not activate policy |
| N03 | Forged `S1_ITEM` with maximum park count | No close, no authority-bearing counter |
| N04 | Authentic age/cycle-cap signals only | `PARKED_OPEN`, not closed |
| N05 | Codex authored part of H and supplies its “review” | Not independent |
| N06 | S1 emits specialist review of its own repair | Preflight only |
| N07 | Forged App name or owner PAT comment | No reviewer/owner-presence authentication |
| N08 | Review H=A; branch now B | Review invalidated |
| N09 | Exact-head adverse review arrives after earlier approval | Release blocked |
| N10 | Review edited/deleted or newer review hidden on another page | Fresh full census; HOLD on incompleteness |
| N11 | Same PR number/head-ref in a fork | No write to wrong repository |
| N12 | Files list omits rename source or count mismatches | No classification/admission |
| N13 | Deletion, chmod, symlink or gitlink not representable | Explicit handling or HOLD |
| N14 | Required job skipped; workflow still green | CI not proven |
| N15 | Test collected but not executed; `continue-on-error` masks failure | CI not proven |
| N16 | Correct display name, wrong workflow/job identity | Reject evidence |
| N17 | Correct workflow, wrong repository/event/checkout SHA | Reject evidence |
| N18 | Candidate prints privacy-success marker | Cannot satisfy trusted scan evidence |
| N19 | Secret-free writer reads implicit checkout token | Privileged execution classified/excluded |
| N20 | Dynamic import, shell source or config redirects existing writer | UNKNOWN/excluded unless closure proven |
| N21 | Rules API short-page cap hides active final rule | Continue to explicit empty page |
| N22 | Rules change between census and merge | Requalify; bypass post-readback halts |
| N23 | Health observer SUCCESS with fleet RED | Observer live; affected-domain status separately evaluated |
| N24 | Vault receipt expired, edited, wrong App or mismatched source tree | HIGH evidence blocked |
| N25 | Owner approves stale head | No release on new head |
| N26 | Owner merges inside S1 intent timing window | Native merge may verify; not S1-owned credit |
| N27 | Forged `ticks_24h=24` with no native history | UNKNOWN; no fabricated liveness |
| N28 | Merge green, receiver stale or Pages not updated | `POST_FIX_OBSERVATION` |
| N29 | Review quota exhausted for a week | Continue permissible work; no fake review/paid fallback |
| N30 | Monday boundary occurs mid-tick | No subsequent mutation |

The matrix directly tests the supplied policies’ head, rule, privacy, recovery and provenance requirements and the draft/adjudication’s identified failure cases. [A, §§0.2a–e, 4a, 6; N, R01–R31; D, §11; V, D1–D8]

## 10.2 Fault-injection matrix

| Injection boundary | Expected recovery |
|---|---|
| Intent post accepted; response lost | Read existing intent; no blind repost |
| First of several file writes accepted; process dies | Partial state detected; no ready/review reuse |
| Commit created; branch update outcome unknown | Inspect ref and commit ancestry before another write |
| Merge accepted; response times out | Query PR/merge; never retry merge blindly |
| Merge succeeds; receipt publication fails | Recover receipt without re-merging or inventing origin |
| Contract upgrades before reconciliation | Old operation remains recoverable under its original binding |
| Native logs expire before receipt recovery | Evidence unavailable; no complete closure credit |
| API 429/403/allowlist 400 mid-pagination | Partial census; affected action blocked |
| Unrelated main writes repeatedly advance base | Bounded requalification; no head rebinding or waived review |
| Scheduler delayed; result pointer remains old | Native timestamps distinguish late run from stale output |
| Halt posted between qualification and action | Fresh halt read blocks if observed; residual race disclosed |
| Consumer publishes stale source ID after new code | No production verification |
| Token custody changes after attestation | Separation invalidated; affected high-impact action stops |
| Unknown accepted paid request in historical evidence | Liability UNKNOWN; no retry or zero-cost assumption |

These are simulations/fixtures or explicitly authorized test-environment injections only. The paid-call case is a state-handling test, not permission to make a paid call. [Basis: L, C9/HIGH EVIDENCE; D, §§7, 11–12; O, API-agent semantics]

## 10.3 Mutation-sensitive proof

For each critical guard, deliberately remove or invert it in an isolated test mutant:

- head equality;
- repository equality;
- complete file-count check;
- independent-review check;
- executed-step requirement;
- privacy-source authentication;
- active-rule compliance;
- recovery separation;
- readback before closure;
- task-run provenance before scheduled credit.

**Acceptance:** the corresponding negative fixture must fail because of the removed guard—not because an unrelated setup check failed first. Run the unmodified positive fixture through the same path. This prevents a suite that is “green” only because it never reaches the safety decision. [Basis: A, §0.2a; O, quality amendment; D, §§1, 10]

---

# 11. Prospective 7-day / 28-day evaluation

## 11.1 Pre-registration and comparators

**PROPOSED:** freeze the evaluation definitions before observing pilot outcomes.

- Baseline: supplied v1.6.9 contract, supplemented only by authenticated native historical data.
- Candidate: exact integrated vNext head and policy blobs.
- Claude v2: comparator only once its actual implementation and effective policy are available. The adjudication text is not an executable comparator.
- #2194: comparator/design input only after its original source is supplied and bound.
- Counterfactual replay: research-only, same frozen snapshots, no production mutations.
- Prospective results: actual native task/PR/consumer events only. [Basis: D, §§9–10; V, Verdict; A, prospective evidence discipline]

Do not pool owner-assisted releases with unattended S1 releases. Do not select only easy completed PRs after observing outcomes. Include all qualified originals under the frozen eligibility rule, recording risk, review availability, tool capability and consumer readiness. [Basis: D, §9; A, §0.2c evaluation]

## 11.2 Primary measures

| Measure | Definition |
|---|---|
| Verified original closures | Distinct original work items meeting frozen code/main/consumer criteria |
| S1-scheduled closure yield | Verified S1-origin closures / genuinely eligible originals with adequate run provenance |
| Owner burden | Material owner interactions per verified closure; denominator zero ⇒ undefined |
| False READY | Qualified/released action missing a required gate, including attribution/privacy/rule defects |
| False HOLD | Independent retrospective adjudication shows all required gates were actually available at decision time |
| Repair-to-consumer time | Native first eligible repair state to natural consumer verification |
| Review pressure | Requests, completions, stale-head rerequests and quota blocks |
| Evidence completeness | Required authenticated fields present / required fields, with material omissions separately fatal |
| Cost | Actual attributable paid cost and resource observations; unknown liability separate |
| Liveness | Native scheduled/started/completed timestamps and missing-history coverage |

A completely enumerated queue with no eligible originals has denominator **0** and `NO_POSITIVE_TRIAL`; an incompletely observed queue has denominator **UNKNOWN**. Neither is a successful autonomy demonstration. [Basis: L, HEARTBEAT; D, §§2, 9; A, §0.2c rollout]

## 11.3 First seven days

1. At least 24 hours shadow, preserving existing policy and no new autonomy.
2. Audit every candidate decision in the small pilot.
3. Establish one genuine eligible original; do not manufacture work to obtain a positive trial.
4. If separately approved for release, require native exact-head execution and actual unprompted scheduled provenance.
5. Retain mandatory independent review.
6. Record all blocked cases and evidence acquisition failures.
7. Require zero confirmed false READY, privacy/custody breaches, unauthorized spends or improper closures.
8. Treat incomplete consumer observation as pending at day 7, not success or failure fabricated to meet a deadline. [Basis: A, §0.2c rollout/kill rules; D, §§9–10]

## 11.4 Twenty-eight days

Compare risk-conditioned cohorts and report:

- verified closures and pending originals;
- owner-assisted versus scheduled outcomes;
- cycle-time distribution, including censored unfinished work;
- false READY/HOLD adjudications;
- downstream regressions and reverts;
- quota/tool bottlenecks;
- producer growth and retention where applicable;
- actual cost and unknown billing;
- provenance coverage. [Basis: D, §9; A, §4a; O, completion semantics]

**Promotion is an owner-controlled decision, not a metric-triggered automatic action.** No positive trial means adoption remains unproven. Zero observed failures in a tiny cohort is weak evidence: analytically, zero failures in five independent trials still permits an approximately **45% one-sided 95% upper failure bound**. That is a statistical illustration, not an observed test result. [Basis: A, §0.2c kill rules; D, §9]

---

# 12. Rollback, emergency stop and safe restart

## 12.1 Emergency stop

**PROPOSED operational response, subject to existing authority:**

- stop further lane mutations on confirmed false READY, head violation, privacy miss, bypass, unexplained readback mismatch, custody uncertainty or material receipt corruption;
- preserve the native evidence and unresolved operation state;
- use the existing #1156 halt mechanism when writing is permitted and evidence is established;
- if strict read-only or source verification prevents posting, stop locally and emit the blocked-state result—do not violate the prohibition to announce compliance;
- do not touch Vault, credentials, rulesets, schedules or task identity. [Basis: A, §0.2c kill rules and §0.2e halt triggers; L, H1/H4/H5]

A posted halt is an important coordination control, **not a revocation of shared-account credentials**. This residual limitation must be acknowledged. Only the human owner may perform any independently authorized credential/ruleset intervention; this review requests none. [Basis: A, §0.2e shared-account residual risk; A, §6]

## 12.2 Rollback

- Revert through the existing original PR/native governance path.
- Preserve history; no force-push, destructive rewrite or backup manipulation.
- Restore a coherent approved set of policy/runtime/switch pins—not one file in isolation.
- Keep the lane halted while consistency, review and readback are unresolved.
- Verify the rollback’s natural consumer outcome; reverting code is not proof that damaged data has recovered.
- Treat data repair as a separate bounded task under its original source owner; recovery remains independent. [Basis: A, §§0.2c kill rules, 6; D, §§7, 10–12]

## 12.3 Restart

Require:

1. identified root cause;
2. reproducing negative test;
3. guard-removal test sensitivity;
4. exact integrated patch review;
5. applicable recovery/separation evidence;
6. original Claude review for this adoption;
7. owner-present activation through the existing governed source path;
8. fresh source/native-rule/readback evidence;
9. renewed shadow observation where the failure invalidated earlier qualification.

Do not clear a halt because the same shared account posted “fixed,” because a counter reset, or because the next observer run succeeded. [Basis: A, §0.2e re-enable; V, Smallest next step; O, Observer versus observed status]

---

# 13. Rejected alternatives and challenge to this recommendation

## 13.1 Rejected alternatives

| Alternative | Why rejected |
|---|---|
| Deploy Claude v2 unchanged | Reported stale bases, self-review and closure defects remain disqualifying. [V, D1–D3] |
| Build a separate “v3 supervisor” | Adds authority/coordination surface before existing lane is qualified. [D, §§0, 10; O, queue continuity] |
| Treat S1 specialist output as independent | Same principal/rubric is preflight, not detached review. [V, D3] |
| Make Claude optional immediately | Contradicts current Claude-specific §0.2e gate. [A, §0.2e(d)] |
| Use owner PAT comments as consent | Native metadata cannot prove human presence. [A, §0.2c owner-authenticity gate] |
| Trust supplied classifier booleans | The code expressly does not authenticate them. [C] |
| Auto-close on age, budget or park counts | These facts do not prove original work is noise. [V, D2] |
| Treat comment intents as locks/exactly-once execution | Shared identity and partial failures defeat that claim. [D, §§1, 7; L, RECONCILE] |
| Scan only literal secret/token strings | Misses implicit credentials, private design and transitive execution. [D, §6; A, §0.2c privacy gate] |
| Regard green CI as closure | Main, natural producer and consumer evidence remain distinct. [A, §§0.2a, 4a; O] |
| Solve races with more double-reads | Reduces exposure but cannot make mutable review/rule state atomic. [A, §0.2a; N, Race and bypass] |
| Add paid fallback loops or trading authority | Outside scope and prohibited by current hard stops. [L, H3; D, §§0, 8] |

## 13.2 Strongest objections to my recommendation

### Objection A: “This is too much machinery for a one-owner repository.”

Valid. A large event schema and dependency graph could become a second governance system. The response is **not** another database, registry or executor: add only the minimum fields to existing owner receipts and pure validators, and begin with one original per tick. If this still costs more owner effort than it saves, retain a simpler coordinator with owner-directed integration. [Basis: O, queue continuity; D, §§1, 9–10]

### Objection B: “You may make in-house independence impossible.”

Also valid. The supplied packet does not prove an independently authenticated internal ChatGPT reviewer route, and Codex cannot independently review its own authored head under the proposed rule. Therefore “Claude optional” is a capability target, **not a promise of uninterrupted unattended merging**. A genuine reviewer gap must remain visible. [Basis: D, §3; V, D3; A, §0.2e(d)]

### Objection C: “Static dependency closure can never be complete.”

Correct for unrestricted dynamic execution. That is why unresolved edges must be excluded and privileged execution must be narrowed. The goal is not a falsely perfect static graph; it is a bounded trusted gate plus isolated untrusted computation and explicit unknowns. Some changes may remain owner-only indefinitely. [Basis: D, §6; V, D4]

### Objection D: “Existing connectors cannot provide atomic locks or task provenance.”

That may be true; current capability evidence is missing. Do not invent them. Use honest optimistic concurrency where policy allows it, with narrowly bounded actions and reconciliation. If scheduled provenance is unavailable, report native merges without claiming S1-owned scheduled closure. [Basis: A, §0.2c D4; L, HEARTBEAT; D, §7]

### Objection E: “Conservative holds may erase throughput gains.”

Possible. Measure false HOLD and owner burden alongside safety. Fix unjustified capability assumptions, incomplete adapters and redundant rereads—but do not convert missing native evidence into PASS to improve velocity. [Basis: N, optional capability fallback; V, D6; D, §9]

### Objection F: “Why not leave v1.6.9 unchanged?”

That is preferable to unsafe adoption. However, the supplied text already exposes reconcile attribution gaps, instruction ambiguities and classifier-policy drift. The smallest justified intervention is a sequence of independently reviewed repairs to the existing system, not a wholesale replacement or immediate expansion of autonomy. [Basis: L, RECONCILE/C1/H6; C; V, Verdict]

---

# Final recommendation

**Retain the existing S1 identity, schedule, original #1156 ownership and GitHub-rooted authority. Do not deploy the frozen Claude v2 package or claim #2194 has been reviewed.**

First obtain the missing original sources and native evidence; resolve source/pin transitions, self-review, forged closure, workflow isolation and ambiguous-write recovery. Then qualify a small in-house steward increment with mandatory independent review, authentic task-run attribution and natural consumer proof. Claude may become optional for routine operation only through a separately reviewed policy change; **the original Claude review of the final integrated adoption package remains required**. [A, §§0.2a–e; D, §§3, 10–12; V, Verdict]

**Current result:** `RESEARCH_ONLY / NOT_PERSISTED / NO_PRODUCTION_CHANGE / ADOPTION_UNPROVEN`. No owner consent, hosted test success, independent approval, scheduled S1 closure or production verification is claimed. [A, §8; C, advisory contract; D, §§2, 9–12]