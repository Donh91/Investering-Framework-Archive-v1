# Project -> CA Intelligence Bridge - Shadow Build Implementation Contract v1

Status: CODEX_READY / SHADOW_ONLY
Owner: #1087
Research authority: PR #1180 / PROJECT_CA_INTELLIGENCE_BRIDGE_ABC_PREREG_v1
Design supervisor: GPT-5.6 Sol High
Code executor: CODEX_ONLY
Independent review: required after every code-write packet
Production activation: forbidden

## Non-negotiable invariants

- Do not change the frozen A/B/C experiment, survival margins, denominator, metrics or kill criteria.
- Reuse existing Meme Alpha runtime, prospective evidence, lifecycle and owner. No parallel scanner, ledger, scheduler or learning engine.
- Project identity and token identity remain separate.
- Ticker/name/logo never establish identity.
- BOUND_HIGH requires exact chain + exact CA + authenticated project source or deterministic project-controlled onchain relation + no unresolved material conflict + timestamps + evidence hash + relationship type.
- Missing/conflicted evidence is UNKNOWN/CONFLICTED, never silently negative.
- Jev has no truth, identity, provenance, arithmetic, date, market, sellability, BUY/SELL, DROP or promotion authority.
- NET/SAFIX/DARK remain design/regression cases with zero prospective credit.
- All eligible projects, rejects and zero-result days remain in the denominator.
- No user alerts, portfolio actions, production weights or automatic promotion.

## Packet sequence

### P1 - Project Memory substrate
Goal: create the smallest child schema/adapter needed to persist a unique eligible project trial before a token exists.

Required fields include project_trial_id, method_version, frozen_at_utc, eligibility_manifest_sha256, discovery, project_identity, source_observations, project_memory_before, material_delta, token state, CA candidates, lineage and authority.

Token states: NO_TOKEN_OBSERVED, TOKEN_CANDIDATE, TOKEN_BOUND, TOKEN_CONFLICT.

Acceptance:
- same project observations deterministically resolve to the same trial lineage without outcome data;
- no-token projects persist;
- aliases do not become identity proof;
- source snapshots preserve observed_at/available_at/hash;
- historical state is append-only or explicitly superseded, never silently rewritten.

Regression: 8-Ball no-token case; HoodStack contradictory mutable-source case.

### P2 - Project -> exact CA binding state machine
States: UNBOUND, CANDIDATE_BINDING, BOUND_HIGH, CONFLICTED, SUPERSEDED_WITH_PROOF, REVOKED.

Acceptance:
- exact chain_id + exact contract address is token primary key;
- same ticker/name at multiple addresses cannot auto-bind;
- unresolved conflict cannot reach BOUND_HIGH;
- migration/relaunch requires explicit continuity proof;
- earlier binding remains preserved when superseded;
- Pons TokenLaunched alone proves launch, not project ownership.

Regression: SAFIX/SFX identity conflict must remain CONFLICTED until continuity is proved.

Hard stop: any test path capable of material false Project->CA binding.

### P3 - Deterministic material-change detector
Only frozen material transitions retrigger semantic/identity work.

Allowed classes include new authenticated control root, first mainnet deployment, verified-contract publication, first public CA, linkable factory event, usable/live package or release, design/testnet -> mainnet/live, materially new chain-native mechanism, authenticated contradiction, identity conflict, first sellability/liquidity after binding.

Acceptance:
- minor README edits, repeated marketing and engagement do not retrigger Deep Dive;
- transition receipt contains before hash, after hash, class, timestamps and evidence refs;
- source outage cannot be interpreted as negative project evidence.

### P4 - A/B/C exact-input shadow comparator
Champion remains unchanged.
A = deterministic project-first.
B = A + bounded Jev features.
C = deterministic material-transition/evidence-family delta challenger.

Acceptance:
- A/B/C consume the same frozen eligible project universe and same point-in-time source state;
- variant outputs cannot mutate shared input;
- outcome fields unavailable until maturity;
- permutation siblings never increase denominator;
- exact receipts allow replay and variant comparison;
- counters start at zero after activation.

### P5 - Narrow Jev adapter
Only:
- real_product_surface
- chain_native_specificity
- mechanic_falsifiability
- semantic_delta_value, after deterministic before/after freeze

Kill direct Jev deep_dive_value authority.

Acceptance:
- pinned jev-1.13.0 for experiment;
- canonical state order;
- log model/version/state hash/question hash/distribution/confidence/latency/errors/order id;
- low confidence RETAIN_OR_ESCALATE_NEVER_DROP;
- representation-order suite;
- malformed/service failure fails closed;
- deterministic truth always wins conflict.

### P6 - Prospective denominator + outcome wiring
Preserve N1-N10 and zero-result days.
Minimum review remains 30 future eligible projects, >=2 regimes, >=10 qualified watches.

Acceptance:
- no historical NET/SAFIX/DARK credit;
- denominator unit UNIQUE_ELIGIBLE_PROJECT_TRIAL;
- rejected/no-token/failed projects remain;
- sellable MFE/MAE and realizable outcomes join only after frozen observation;
- false-negative audit includes champion and all variants;
- hard kills automatically surface as research stop state, never production promotion.

## Verification per packet

Every code packet must provide:
1. exact files changed;
2. focused deterministic tests;
3. regression tests for named design cases where applicable;
4. proof no frozen experiment semantics changed;
5. proof no production/trade/alert authority added;
6. fresh-main comparison;
7. independent read-only review after code write;
8. canonical receipt under #1087.

No packet may silently fix another packet's semantics.

## Merge discipline

One packet at a time. Do not begin the next packet until the prior packet has:
- tests green;
- independent review;
- fresh-main readback;
- no unresolved material review finding.

If a packet reveals a flaw in the frozen research design, STOP and route back to Sol supervisor. Do not repair the preregistration through implementation code.

## Activation

Completion of P1-P6 means SHADOW_RUNTIME_READY only.
Prospective counters remain 0 until an explicit reviewed shadow activation receipt.
Production remains forbidden.
