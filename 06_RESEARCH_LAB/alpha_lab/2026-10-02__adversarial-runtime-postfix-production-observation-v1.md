# Alpha Lab adversarial runtime — post-fix production-shaped observation v1

Date: 2026-10-02
Status: POST_FIX_RUNTIME_ROUTE_PASS / SCIENTIFIC_COUNTING_GATE_OPEN
Owner: existing Alpha Lab / #1087 / existing Codex research execution owners
Authority: OBSERVATION_ONLY
Trade authority: NONE
New scanner/runtime: NONE

## Scope

This receipt adjudicates the production-shaped observation sequence after the already-approved adversarial runtime wiring:

`codex-research-alpha-adversarial-runtime-wiring-v1`

It does not promote an adversarial-alpha signal or first-pump strategy.

## 1. Runtime wiring is live in the existing private Meme Alpha runtime

Public control-plane implementation:
- PR #1411 merged.
- candidate is no longer CODEX_READY; current lifecycle is POST_FIX_OBSERVATION.

Private implementation:
- Donh91/secrets PR #171 merged.
- existing Meme Alpha Background Research runtime recognizes:
  - `ADVERSARIAL_MAINTENANCE`
  - `ADVERSARIAL_REPLAY`
- no parallel scheduler/scanner/ledger/trading authority was created.

## 2. PONSCUPINE stale-action regression — parent replay

Private production-shaped evidence:
- run `36879914092`
- bounded replay completion preserved at:
  `private_research/memes_alpha/research_leads/2026/10/01/2026-10-01T145000Z__ponscupine-adversarial-replay-v2-completion.json`

Observed behavior:
- historical market/action context was not reused as current authority;
- same-run evidence did not prove current price / market cap / sellability;
- output remained DEGRADED / fail-closed;
- no user alert or trading authority;
- independent child replay was created.

State:
`PARENT_STALE_ACTION_REPLAY = PASS_FAIL_CLOSED`.

## 3. Neighbor regression

Private run:
`36881054034`

Task:
`2026-10-01T150500Z__ponscupine-stale-action-language-neighbor-v1.json`

Observed:
- same exact CA was hydrated;
- current DEX snapshot supplied liquidity/transaction context but did not establish current price, market cap or executable sellability;
- historical `ENTRY_CANDIDATE` label remained historical-only;
- output stayed DEGRADED/UNKNOWN;
- `adversarial_role_active = true`;
- no trade/user-alert authority.

State:
`NEIGHBOR_STALE_ACTION_REGRESSION = PASS_FAIL_CLOSED`.

## 4. Post-fix observation discovered two real runtime defects

### A. Adversarial child starvation

Production observation showed old generic P0 child backlog could tie on the same priority score and win by lexical path ordering ahead of the required adversarial independent replay.

This was a runtime/queue defect, not a market-rule defect.

Fix:
- Donh91/secrets PR #187
- merge `f43f59b4418ac2469e8e79473ee3d9f7d610d3e0`
- Private Data Plane Gate: PASS

Fix semantics:
- frozen priority score remains authoritative;
- only exact child-score ties prefer `ADVERSARIAL_REPLAY` over generic research;
- a lower-priority adversarial child still cannot outrank a higher-priority generic child.

Post-fix run `36974761258` selected the intended adversarial child, proving the starvation fix in production shape.

### B. Child exact-identity propagation

That selected child then exposed a second defect:
generated children did not preserve safe exact asset identity, producing `identity_count = 0` and blocking a genuine independent replay.

Fix:
- Donh91/secrets PR #188
- merge `366f880c38b359f9f5e8998935de33ed6a2beb4d`
- Private Data Plane Gate: PASS

Safe propagation is limited to:
- `chain`
- `chain_id`
- `token_ca`

Parent conclusions, historical action labels and thesis state are NOT inherited.

## 5. Exact-CA independent child retest

Final bounded existing-runtime run:
`36975445000`

Selected child:
`private_research/memes_alpha/runtime/child_queue/2026/10/02/16c52a9a790b147411b4.json`

Observed:
- `runtime_task_type = ADVERSARIAL_REPLAY`
- `adversarial_role_active = true`
- exact CA preserved:
  `0x860412a94963ef92561e79b2f91073e194670125`
- chain ID 4663 preserved;
- Stage0 `identity_count = 1`;
- network-enabled same-run DEX observation succeeded;
- liquidity and transaction activity were observed;
- current price / market cap / executable sellability were not established by the serialized Stage0 evidence;
- output remained DEGRADED;
- no actionable state, user alert or trade authority was created;
- depth-2 replay created no further children.

Therefore:

`AUTONOMOUS_ROUTE = PASS`

`EXACT_IDENTITY_REPLAY = PASS`

`FAIL_CLOSED_ON_INSUFFICIENT_CURRENT_ACTION_EVIDENCE = PASS`

`PARALLEL_RUNTIME_CREATED = NO`

## 6. What is NOT claimed as closed

The final independent child requested a four-case synthetic missingness matrix:
- price missing;
- market cap missing;
- sellability missing;
- all three missing.

The production-shaped exact-CA run demonstrated the all-relevant-fields-insufficient fail-closed behavior, but did not materialize four separate decision/log fixtures.

Therefore:

`FULL_MISSINGNESS_MATRIX = PENDING / NON_BLOCKING_FOR_RUNTIME_ROUTE_PROOF`

This must not be rewritten as complete.

## 7. Claude / adversarial-alpha research adjudication

Claude's latest adversarial research is accepted as:

`CONTINUE_SHADOW`

Key accepted lesson:
the base-rate problem is severe. Broad Pons features such as relaunch frequency, quote asset and generic fresh-wallet behavior can produce unusably many false positives at launch-volume scale.

Therefore first-pump policy optimization remains downstream of an interpretable qualification denominator.

Do not optimize exits on selected historical winners before the counting gate is interpretable.

## 8. 88-launch counting gate remains open

The frozen outcome-blind interval currently contains 88 exact launch rows.

Canonical pre-enrichment receipt still reports:
- `qualification_unknown_rows = 88`
- Stage1 `INCOMPLETE_SOURCE_EVIDENCE`

The deterministic qualification-enrichment implementation is merged:
- candidate `codex-research-adversarial-operator-qualification-enrichment-v1`
- merge `a6e39dfd103ea76b09c397ef0c4aa38ff5b97d32`
- lifecycle `POST_FIX_OBSERVATION`

But no post-fix enriched 88-row manifest/counting receipt is canonical yet.

Therefore:
`88_ROW_ENRICHMENT_EXECUTION = PENDING`

`COUNTING_GATE_INTERPRETABLE = NO`

`FIRST_PUMP_POLICY_PROMOTION = BLOCKED`

This is the highest-value remaining observation task.

## 9. Next exact step

Run the already-merged deterministic executor against:

Manifest:
`research/api_agent/meme_alpha/reports/2026-10-01__adversarial-counting-bounded-interval-manifest-v1.json`

Seed registry:
`research/api_agent/meme_alpha/experiments/ROBINHOOD_ADVERSARY_SEED_REGISTRY_20260927_v1.json`

Executor:
`scripts/research/memes_alpha/adversarial_operator_enrichment.py`

Required output:
- enriched immutable 88-row shadow manifest;
- fresh counting output from unchanged counting thresholds;
- source-health / UNKNOWN distribution;
- Stage1 gate;
- no outcome fields.

Do not create a new workflow merely to run this observation.

## Current state

ADVERSARIAL_RUNTIME_WIRING: LIVE
PARENT_STALE_ACTION_REPLAY: PASS
NEIGHBOR_REGRESSION: PASS
CHILD_STARVATION_DEFECT: FIXED + CI PASS + PRODUCTION-SHAPED SELECTION PASS
CHILD_IDENTITY_PROPAGATION_DEFECT: FIXED + CI PASS
EXACT_CA_INDEPENDENT_ROUTE: PASS
FAIL_CLOSED_SEMANTICS: PASS
AUTOMATIC_TRADING: NONE
FULL_MISSINGNESS_MATRIX: PENDING
CLAUDE_ADVERSARIAL_RESEARCH: CONTINUE_SHADOW
88_ROW_QUALIFICATION_ENRICHMENT: PENDING POST_FIX OBSERVATION
FIRST_PUMP_ALPHA_CLAIM: NOT ALLOWED
