# Project -> CA Intelligence Bridge - Deep Research Result v1

**Dato:** 2026-09-20  
**Status:** SHADOW_ONLY / READY_FOR_SHADOW_BUILD  
**Område:** Alpha Lab / Meme Alpha / Project-first discovery  
**Primary folder:** `06_RESEARCH_LAB/alpha_lab/`  
**Depends on:** `PROJECT_CA_INTELLIGENCE_BRIDGE_DEEP_RESEARCH_MISSION_v1.md`  
**Owner:** issue #1087  
**Frozen research base:** `684ea9703148d1c0bcef7ff65fec93c1ed489d00`  
**Authority:** RESEARCH_ONLY / NO_TRADE / NO_PRODUCTION_PROMOTION / NO_MODEL_WEIGHT_CHANGE / NO_ALERT_AUTHORITY  
**Codex used:** NO

## Executive verdict

**READY_FOR_SHADOW_BUILD**

The research supports a bounded Project -> CA bridge, but only as a child capability inside the existing Meme Alpha Supervisor / Prospective Evidence / Moonshot lifecycle.

The surviving mechanism is not "Jev finds good tokens". It is:

```text
public project surfaces
-> deterministic normalization and source authentication
-> persistent project memory
-> material-change detection
-> exact project -> CA binding
-> existing Alpha Lab identity / origin / sellability / liquidity gates
-> bounded Deep Dive
-> prospective outcome measurement
```

The strongest finding is that the current gap is primarily a **project-memory and project-to-CA join gap**, not a missing token scanner. NET is the clearest historical illustration, SAFIX is the clearest identity-conflict warning, and DARK is a useful semantic/falsifiability case. None receives prospective performance credit.

Jev can be tested as a narrow semantic triage layer, but it must not become a truth layer, identity resolver, arithmetic engine, date comparator, threshold authority or evidence-dropper. Variant C is intentionally designed to test whether deterministic material-change detection captures most or all of B's value without Jev.

No production activation follows from this verdict.

## 1. Frozen proposition

> A persistent project-first discovery and project-to-CA bridge can improve early recall and lead time for high-information Robinhood Chain projects relative to the existing Alpha Lab champion, without materially increasing false links, Deep-Dive load, unsafe retention loss or research cost.

This proposition is falsifiable prospectively.

## 2. Existing-owner and redundancy check

The proposal **REFINES_EXISTING_OWNER**.

It must reuse:

- issue `#1087` as canonical Alpha Lab owner;
- `.agents/skills/meme-alpha-supervisor/SKILL.md` as operational research supervisor;
- `.agents/skills/prospective-evidence-ledger/SKILL.md` as evidence discipline;
- `.agents/skills/research-lab-red-team/SKILL.md` as falsification owner;
- `research/api_agent/meme_alpha/MEME_ALPHA_RUNTIME_POLICY_v1.json`;
- `research/api_agent/meme_alpha/MEME_ALPHA_PROSPECTIVE_HARDENING_v1.json`;
- `research/api_agent/meme_alpha/MEME_ALPHA_ROBINHOOD_PONS_V2_SHADOW_ADAPTER_v1.json`;
- `research/api_agent/meme_alpha/MOONSHOT_SENTINEL_CONTRACT_v1.json`;
- `research/api_agent/meme_alpha/ALPHA_LAB_LIFECYCLE_ENGINE_v1.json`;
- `.agents/skills/typesafe-ai/SKILL.md`, currently `INSTALLED_EXPERIMENTAL_SHADOW_ONLY`.

It must **not** create another scanner, signal engine, learning ledger, trading engine, user-alert system or competing owner.

## 3. Evidence table

Evidence was evaluated for early discovery, timestampability, reproducibility, access/cost, identity reliability and appropriate role.

| ID | Surface | Earliest useful role | Timestampability / reproducibility | Access / cost | Reliability for truth | Allowed role | Main failure mode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E01 | Robinhood Chain official docs / ecosystem pages | project discovery, chain primitives, canonical network data | strong for current docs, changes must be snapshotted | public/free | HIGH for Robinhood-owned facts, not third-party project safety | seed + chain truth | curated and often late |
| E02 | Robinhood public RPC / provider RPC | deployments, logs, bytecode, token state | block timestamp and hash, highly reproducible | public endpoint is rate-limited; keyed providers optional | VERY HIGH for onchain facts | deterministic truth | weak project ownership semantics |
| E03 | Blockscout explorer/API | contract verification, logs, transfers, token metadata | block/tx anchored | public/free tier plus paid options | HIGH for chain state | deterministic enrichment / verification | explorer labels can be incomplete |
| E04 | Pons V1/V2 factory events | exact token launch discovery | exact block/log/event | RPC cost only | VERY HIGH for Pons launch occurrence | launch truth | does not prove token belongs to a project |
| E05 | Pons token metadata/social fields | launch-time candidate linkage | onchain when stored in token/factory state | RPC cost only | MEDIUM | CA candidate linkage only | self-asserted links, spoofable |
| E06 | GitHub public repositories, commits and releases | prelaunch project discovery, artifact shipping, explicit chain integration | commit/release SHA and time | public API/search; rate limits apply | MEDIUM-HIGH for artifact existence, LOW for project ownership by itself | discovery + change detection | repo spam, forks, copied README, adversarial text |
| E07 | npm/PyPI/package registries | shipping signal and project maturity | publish version/time | generally public/free | MEDIUM | discovery corroboration | package squatting / empty packages |
| E08 | first-party website/docs | product/mechanic semantics, published CA candidate | must snapshot observed_at and content hash | public/free | MEDIUM until source authenticated | semantic evidence | mutable, self-serving, stale or contradictory |
| E09 | official project socials | early announcement / CA candidate | post timestamp if retrievable | public/API availability varies | LOW-MEDIUM | candidate evidence only | spoofing, deletions, API/ranking constraints |
| E10 | Robinhood/Open House/buildathon directories | very early project universe | event/list timestamp can be frozen | public/free where available | MEDIUM for participation, LOW for token identity | denominator + discovery | many projects never launch tokens |
| E11 | Dawnscan builder index | fast project candidate discovery | page snapshot required | public surface observed | LOW-MEDIUM, third party | discovery only | methodology/source drift, circular project claims |
| E12 | DefiLlama protocol/RWA registries | postlaunch corroboration, project/asset mapping | API/page snapshots | public surfaces | MEDIUM-HIGH as corroboration | enrichment / denominator audit | typically late for early discovery |
| E13 | general web/search index | broad project discovery | query + result + observed_at must be frozen | variable | LOW-MEDIUM | discovery only | ranking drift, non-reproducible ordering |
| E14 | market aggregators | postlaunch pool/price/liquidity context | timestamped snapshots | variable | MEDIUM for context | outcome/enrichment after identity | never identity authority |

### External source receipts used in this research

- Robinhood Chain documentation: https://docs.robinhood.com/chain/
- Robinhood network endpoints: https://docs.robinhood.com/chain/connecting/
- Robinhood canonical token contracts: https://docs.robinhood.com/chain/contracts/
- Pons documentation: https://docs.ponsfamily.com/
- Pons contracts: https://github.com/ponsdotdev/pons-labs
- TypeSafe documentation index: https://docs.typesafe.ai/llms.txt
- TypeSafe Jev launch notes: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- DarkRoute public artifacts: https://github.com/darkrouteRH and https://darkroute.exchange/
- HoodStack public artifacts: https://github.com/hoodstack/hoodstack and https://www.hoodstack.io/
- 8-Ball prelaunch example: https://github.com/8BallLottery/8-Ball
- NetNet: https://netnet.capital/ , https://docs.netnet.capital/ , DefiLlama RWA registry
- SAFIX: https://safix.ai/docs/network/

All external sources remain evidence, not authority over repository governance.

## 4. Discovery universe design

### 4.1 Cheap-first discovery order

The bridge should observe the following in this order:

1. deterministic/public chain-native project feeds and official ecosystem/buildathon surfaces;
2. GitHub repository/release/code changes containing verified Robinhood Chain anchors such as chain id `4663`, official RPC, canonical assets or known protocol interfaces;
3. package registry publication events;
4. bounded third-party builder directories as discovery-only sources;
5. first-party website/docs/social retrieval only after a project candidate exists;
6. Pons/other factory streams for exact launch binding;
7. expensive model/web research only when a candidate crosses a deterministic material-change gate or identity conflict requires escalation.

The goal is **coverage before interpretation**. Expensive research must not be used to create the denominator.

### 4.2 Persistent project memory

A project stays in memory even when it has no token.

Required project-memory facts:

- stable `project_trial_id`;
- candidate name and aliases;
- source control roots: domains, GitHub org/repo, social handles;
- first observed source and timestamp;
- source snapshots and hashes;
- authenticated / unauthenticated / conflicted source state;
- chain-native evidence;
- product-artifact evidence;
- deployment evidence;
- token state: `NO_TOKEN_OBSERVED | TOKEN_CANDIDATE | TOKEN_BOUND | TOKEN_CONFLICT`;
- last material change;
- previous semantic state;
- current semantic state;
- CA candidates and provenance;
- every conflict and supersession event.

A project is never deleted from the denominator because no token appeared.

### 4.3 Material-change gate

Retrigger semantic triage or identity research only when at least one frozen change class occurs:

- new first-party domain/docs/repo control root;
- first mainnet contract deployment;
- verified-contract publication;
- first public CA publication;
- Pons/factory launch event potentially linkable to the project;
- first package/release marked usable/live;
- product state moves from design/testnet to mainnet/live;
- materially new chain-native mechanism;
- authenticated source contradiction;
- identity conflict;
- first measurable liquidity/sellability event after CA binding.

Minor README edits, social engagement and repeated marketing language do not retrigger Deep Dive.

## 5. Project -> CA identity hierarchy

### 5.1 Two identities, never one

Project identity and token identity are separate objects.

```text
PROJECT
  -> zero, one or many TOKEN_BINDINGS
TOKEN
  -> exact chain_id + exact contract address
```

Ticker/name/logo are never identity keys.

### 5.2 Token truth hierarchy

Highest to lowest authority:

1. **onchain factory/deployment event plus verified bytecode/state** for exact chain + CA;
2. **authenticated project-controlled onchain binding** linking project control to that CA;
3. **authenticated project first-party CA publication**, then independently verified onchain;
4. **verified explorer / registry mapping** as corroboration;
5. **third-party protocol registry** as corroboration;
6. **social post / search result / market aggregator** as candidate only.

Pons `TokenLaunched` proves a Pons launch. It does not, by itself, prove that a token belongs to NetNet, SAFIX, DARK or any other named project.

### 5.3 Binding states

```text
UNBOUND
CANDIDATE_BINDING
BOUND_HIGH
CONFLICTED
SUPERSEDED_WITH_PROOF
REVOKED
```

Only `BOUND_HIGH` may enter existing Alpha Lab token verification as the project-linked CA.

### 5.4 Binding requirements

`BOUND_HIGH` requires:

- exact chain id;
- exact CA verified onchain;
- provenance from an authenticated project source OR deterministic project-controlled onchain relation;
- no unresolved material conflict;
- source observed_at and available_at;
- evidence hash;
- clear relationship type: `OFFICIAL_TOKEN | LEGACY_TOKEN | TEST_TOKEN | BRIDGED_REPRESENTATION | OTHER`;
- if a relaunch/migration is claimed, explicit continuity proof.

### 5.5 Conflict policy

Any of the following forces `CONFLICTED`:

- two current CAs claimed for one token role with no explicit relationship;
- same ticker/name at multiple addresses;
- first-party surfaces disagree;
- project website and repository disagree on launch state;
- candidate CA is only a reply, copycat or aggregator listing;
- deployer linkage contradicts project-controlled evidence;
- purported migration lacks a source + onchain continuity trail.

Conflict semantics:

- keep all candidates;
- never overwrite the earlier CA;
- never infer migration;
- never infer "latest = official";
- preserve historical bindings;
- escalate only the conflict, not the whole project;
- missing resolution remains UNKNOWN / CONFLICTED, never negative.

SAFIX is the canonical design case: the earlier Pons SAFIX address and the current SFX/USDG address must remain separate until a proved continuity relation exists.

### 5.6 Mutable-source protection

HoodStack demonstrates why page state must be timestamped. Its current public GitHub README simultaneously contains an HSTACK CA and older text stating no token has launched, while its current website states HSTACK is live. The bridge must preserve these as timestamped, contradictory observations, not silently choose the most recent-looking prose.

## 6. Anti-overfit denominator

### 6.1 Primary denominator

The denominator is the **unique eligible project trial**, not token artifacts, not Deep-Dive rows and not known winners.

Eligibility must be frozen before outcome knowledge.

A trial is eligible if it appeared through a preregistered discovery source and contained enough Robinhood-chain relevance to satisfy deterministic intake rules at observation time.

### 6.2 Required negative / control classes

Every prospective window must preserve all classes:

| Class | Description | Why required |
| --- | --- | --- |
| N1 | serious chain-native project, no token during observation window | prevents "good project = token" assumption |
| N2 | serious project that launches late | tests project memory and delayed CA join |
| N3 | token launch with strong-looking product narrative but poor/failed outcome | tests semantic overconfidence |
| N4 | social/hype project with weak product evidence | tests noise suppression |
| N5 | duplicate-name / ticker / relaunch / migration conflict | tests false-link safety |
| N6 | copycat/fork/sibling project with similar keywords | tests keyword overfit |
| N7 | token-first launch with little project substance | tests whether project-first misses token-native winners |
| N8 | rug, unsellable, liquidity-collapse or economically non-exitable launch | safety denominator |
| N9 | source-spoof / compromised / adversarial project surface | model and authentication stress |
| N10 | neutral random eligible projects from the same discovery source and week | prevents curated negatives |

### 6.3 Historical design/falsification examples

These are **not** performance rows:

- **NET**: confirmed historical visibility miss in repository evidence; primary failure class `PROJECT_TO_CA_JOIN_GAP`.
- **SAFIX/SFX**: project-first candidate with material CA identity conflict.
- **DARK**: useful semantic case because some product surfaces were live while multiple roadmap/contracts were explicitly not deployed/audited.
- **TAGPAD**: existing negative case where narrative/low MC did not override sell pressure and outcome collapsed.
- **HoodStack**: mutable/contradictory project state, useful for timestamp and conflict handling.
- **8-Ball**: serious project surface explicitly stating its token had not launched, a clean no-token denominator example.

### 6.4 Matching dimensions

When a token-bound candidate is compared with controls, match on fields knowable at selection time:

- chain/ecosystem;
- discovery week;
- source family;
- project maturity bucket;
- product archetype;
- token state at discovery;
- if already launched: token age bucket, liquidity bucket and MC/FDV availability, preserving UNKNOWN;
- source authentication state.

Never select a replacement control after seeing outcome merely because the original control is inconvenient.

### 6.5 Pons base-rate handling

Broad Pons launch/graduation counts currently present elsewhere in the framework remain **external claims until independently reproduced**. They may motivate a denominator audit, but cannot be used as a hard base rate in this experiment until the same exact factory versions, block interval, event definition and graduation definition are reproduced.

## 7. A/B/C architecture freeze

### Variant A - deterministic project-first baseline

```text
Discovery sources
-> deterministic normalization
-> source/control-root authentication
-> persistent project memory
-> deterministic material-change gate
-> deterministic project -> CA hierarchy
-> existing Alpha Lab verification
-> existing bounded Deep Dive
```

No Jev.

### Variant B - A + narrow Jev semantic triage

Same universe, same snapshots, same project memory, same CA truth layer and same hard gates as A.

Jev sees only a bounded, sanitized semantic state after deterministic preprocessing. It may add reusable semantic features. It may **not** drop evidence, resolve identity, compare dates, calculate metrics, change thresholds, issue alerts or promote a token.

Low confidence means retain/escalate, never DROP.

Pinned model for the experiment: `jev-1.13.0`.

### Variant C - adversarial deterministic delta architecture

C is frozen specifically to challenge the assumption that Jev adds value.

```text
same discovery universe as A/B
-> same authentication and project memory
-> material transition graph
-> deterministic evidence-family delta
-> rarity / novelty measured from contemporaneous source universe
-> exact CA join
-> existing Alpha Lab verification
```

C prioritizes only hard state transitions:

- no token -> public CA;
- design -> verifiable deployed mainnet surface;
- unverified code -> verified deployed contract;
- no working surface -> independently observable live use;
- no chain-specific mechanism -> new chain-native primitive;
- stable state -> authenticated contradiction/conflict.

It does not interpret whether a project "sounds good".

**Reason for C:** if B does not materially outperform C, Jev is unnecessary complexity.

### External-adversary note

The mission includes a Claude red-team packet. No Claude runtime was available in this execution environment, and no external-model opinion is fabricated. The packet's required adversarial function is preserved by freezing C before prospective scoring and by the falsification matrix below. A future independent Claude run may critique the frozen A/B/C package, but cannot rewrite historical observations or thresholds after outcomes.

## 8. Jev decision: KEEP / CHANGE / KILL

TypeSafe's current docs support narrow typed semantic decisions and explicitly advise that code retain deterministic logic. The vendor also documents jagged edges for `jev-1.13`, including arithmetic/counting, date comparison, large irrelevant state, indirection and adversarial content. Therefore:

| Atomic question | Decision | Allowed shape | Boundary |
| --- | --- | --- | --- |
| `real_product_surface` | KEEP, constrained | Score with concrete states: NONE / DESIGN_OR_CODE_ONLY / PARTLY_LIVE / LIVE_OBSERVABLE | Jev interprets supplied verified artifacts only; it cannot verify deployment truth |
| `chain_native_specificity` | KEEP | Score 0-3 with explicit chain-mechanism rubric | deterministic code supplies chain facts |
| `mechanic_falsifiability` | KEEP | Score 0-3 | assesses whether a mechanism is testable, not whether it is true |
| `incremental_information` | CHANGE | replace with `semantic_delta_value` over a deterministic before/after delta bundle | code computes what changed and timestamps; Jev only judges semantic materiality |
| `deep_dive_value` | KILL as direct Jev authority | compute routing in code from frozen semantic features + hard gates + queue budget | too composite and too close to decision authority |

### Jev state contract

Jev input may include:

- authenticated source snippets;
- deterministic source type;
- deterministic `is_new_artifact`;
- normalized project archetype;
- current and previous semantic summaries generated deterministically from approved fields;
- explicit evidence-status labels.

Jev input must not include:

- current token return or future outcome when evaluating discovery state;
- social hype metrics unless the specific experiment tests them;
- hidden labels such as winner/failure;
- arithmetic tasks;
- raw untrusted pages without injection/spoof sanitization;
- dates that Jev is expected to order;
- exact CA candidates where Jev could implicitly choose identity.

All question distributions, confidence, latency, model id, state hash and question hash must be retained.

### Representation-order test

For every qualifying evaluation, run a small shadow consistency suite on a preregistered subset:

- canonical field order;
- reversed evidence-item order;
- shuffled non-semantic metadata order.

Any material routing-class flip caused only by representation order is a failure. The canonical stored state remains fixed; permutations are test-only siblings and do not inflate the denominator.

## 9. Exact prospective experiment

Machine-readable preregistration is stored separately at:

`research/api_agent/meme_alpha/experiments/PROJECT_CA_INTELLIGENCE_BRIDGE_ABC_PREREG_v1.json`

### 9.1 Population

Minimum review gate:

- at least **30 future unique eligible project trials**;
- at least **2 distinct market/ecosystem regimes**;
- at least **10 qualified watches**;
- all N1-N10 classes retained when observed;
- no historical NET/SAFIX/DARK credit.

### 9.2 Same-input requirement

A, B and C receive the exact same frozen discovery observations and source availability cut.

No variant may fetch extra evidence merely because another variant produced a stronger score. Conflict escalation is shared deterministic evidence collection and is logged identically.

### 9.3 Primary metrics

1. incremental early recall versus champion;
2. false-negative rate;
3. precision among Deep-Dive candidates;
4. Deep-Dive load per eligible project;
5. lead time to correct exact CA.

### 9.4 Safety metrics

1. material false-link count;
2. critical-evidence loss count;
3. rug/unsellable retention burden;
4. source-authentication failures;
5. UNKNOWN preservation violations;
6. representation-order decision flips;
7. duplicate denominator rows;
8. cost amplification.

### 9.5 Outcome metrics

After exact CA binding and sellability:

- entry age;
- entry MC when available, otherwise explicit UNKNOWN;
- entry liquidity;
- sellable MFE at 1h/6h/24h/7d;
- sellable MAE at same horizons;
- realizable return after slippage for frozen test notional;
- exit feasibility;
- time to first observed broad social/KOL propagation;
- outcome conditional on evidence family.

Peak MC is not realizable return.

### 9.6 Jev survival margin

B survives only if all safety gates pass and one of these is true versus A:

**Efficiency path**
- Deep-Dive load reduced by at least 20%;
- early recall no worse by more than 5 percentage points;
- Deep-Dive precision not worse;
- no material lead-time loss.

**Recall path**
- early recall improves by at least 10 percentage points;
- Deep-Dive load <= 1.10x A;
- Deep-Dive precision no worse by more than 5 percentage points;
- median lead time is not worse.

In addition, B must show incremental value versus C on at least one primary metric that is larger than ordinary run-to-run noise under the frozen repeated-evaluation harness. If C captures the gain within the preregistered margin, Jev is killed or removed from this bridge.

### 9.7 Architecture-level success margin

Project-first survives only if the best safe challenger A/B/C:

- finds at least two prospectively qualified opportunities that the champion missed or found materially later;
- has zero material false project-to-CA links;
- has zero critical evidence losses;
- does not increase Deep-Dive load above 1.25x champion without a compensating precision or early-recall gain;
- preserves all eligible denominator rows.

This is a shadow-research success criterion, not a trading claim.

## 10. Prospective schema

Each unique project trial lives in the existing Prospective Evidence discipline.

Required top-level fields:

```json
{
  "project_trial_id": "EE-NNN-ECOSYSTEM-YYYYMMDD",
  "method_version": "...",
  "frozen_at_utc": "...",
  "eligibility_manifest_sha256": "...",
  "discovery": {},
  "project_identity": {},
  "source_observations": [],
  "project_memory_before": {},
  "material_delta": {},
  "variants": {
    "A": {},
    "B": {},
    "C": {}
  },
  "ca_bindings": [],
  "existing_alpha_lab_handoff": {},
  "deep_dive": {},
  "outcome": {},
  "missed_winner_audit": {},
  "lineage": {},
  "authority": {}
}
```

### Required source observation fields

```text
source_id
source_family
url_or_onchain_locator
control_root_id
observed_at_utc
available_at_utc
published_at_utc_or_unknown
content_sha256
authentication_state
raw_fact_class
is_material_change
conflict_state
```

### Variant B fields

```text
model_id
model_version
state_sha256
question_set_sha256
question_id
answer
probability_distribution
confidence_if_supported
latency_ms
service_error
representation_order_id
```

### CA binding fields

```text
chain_id
token_ca
relationship_type
binding_state
binding_provenance
first_candidate_at_utc
bound_high_at_utc
conflict_ids
onchain_verification
project_control_binding
supersedes_binding_id_or_null
```

### Lifecycle

Use existing high-level trial lifecycle:

```text
DISCOVERY_OPEN
-> DISCOVERY_COMPLETE
-> OUTCOME_MATURING
-> OUTCOME_MATURED
or INVALIDATED
```

Within `DISCOVERY_OPEN`, use bridge sub-state:

```text
RAW_DISCOVERY
NORMALIZED
PROJECT_CLUSTERED
SOURCE_AUTHENTICATED_OR_BOUNDED
MATERIAL_DELTA_EVALUATED
CA_UNBOUND
CA_CANDIDATE
CA_BOUND_HIGH
CA_CONFLICTED
ALPHA_LAB_HANDOFF
DEEP_DIVE_OR_RETAINED_WATCH
```

Sub-states do not create new denominator units.

## 11. Falsification matrix

| Attack / falsifier | Expected safe behavior | Kill / failure condition |
| --- | --- | --- |
| NET-like project is visible but no CA yet | retained in project memory | dropped because no token exists |
| SAFIX-like same-name two-CA conflict | CONFLICTED, both retained | silent selection of one CA |
| DARK-like mixed live/not-live roadmap | semantic fields distinguish actual shipped evidence from plans | roadmap language scored as deployed truth |
| TAGPAD-like strong narrative + poor outcome | retained as negative | removed from denominator |
| 8-Ball-like serious project, no token | retained N1 | excluded because no CA |
| HoodStack-like contradictory mutable sources | timestamped conflict | latest page silently overwrites history |
| copied README / fork | control-root clustering and duplicate suppression | duplicate project trials |
| social account spoof | candidate only | CA bound from social alone |
| prompt injection inside README/docs | sanitize/quarantine and low-confidence retain | model instruction changes routing/authority |
| missing MC/liquidity | UNKNOWN | zero/default invented |
| later-success backfill | original frozen discovery remains immutable | post-outcome facts rewrite discovery |
| Pons token with copied project name | no project binding without provenance | name/ticker join |
| bridge/migration claim | explicit continuity proof required | inferred continuity |
| Jev high confidence conflicts with deterministic truth | deterministic truth wins | model overrides truth |
| Jev low confidence | retain/escalate | evidence DROP |
| representation order permutation | materially same routing | decision-class flip above allowed tolerance |
| source outage | source-health failure, no negative inference | project downgraded as bad |
| high launch volume regime | bounded project memory + queue budgets | Deep Dive flood |
| low launch regime | no forced positives | synthetic alerts for quota |
| C matches B | remove Jev from bridge | Jev kept for architectural preference |
| champion matches challengers | kill bridge | project-first retained without measurable divergence |

## 12. Implementation delta, ranked

No implementation is executed by this research result.

| Rank | Delta | Value | Effort | Risk | Recommendation |
| --- | --- | --- | --- | --- | --- |
| 1 | Add project-memory child schema to existing prospective row format | VERY HIGH | LOW-MED | LOW | BUILD IN SHADOW |
| 2 | Add deterministic project->CA binding state machine and conflict retention | VERY HIGH | MED | LOW-MED | BUILD IN SHADOW |
| 3 | Add cheap-first discovery adapters for official ecosystem/GitHub/buildathon/package surfaces | HIGH | MED | MED | BUILD BOUNDED |
| 4 | Add material-change trigger so repeated project noise does not invoke models/DD | HIGH | MED | LOW | BUILD |
| 5 | Add A/B/C shadow comparator and exact same-input receipts | HIGH | MED | LOW | BUILD |
| 6 | Add narrow Jev semantic feature extraction per frozen questions | MEDIUM, unproven | LOW-MED | MED | SHADOW ONLY |
| 7 | Add denominator completeness and no-token/failed-project audit | VERY HIGH | MED | LOW | BUILD |
| 8 | Add source-conflict and adversarial-text fixtures | HIGH | LOW | LOW | BUILD |
| 9 | Expand to more chains | UNKNOWN | HIGH | HIGH | NOT NOW |
| 10 | User alerts / buy labels / automated promotion | OUT OF SCOPE | HIGH | HIGH | FORBIDDEN |

## 13. Explicit NOT implement list

Do not implement:

- a new "Project Alpha" scanner engine;
- another standalone ledger;
- project-name or ticker joins;
- Jev arithmetic/date/CA/sellability decisions;
- Jev-generated BUY/SELL or alert labels;
- any automatic evidence DROP from low confidence;
- automatic production promotion;
- automatic model weight changes;
- retrospective winner-trained thresholds;
- NET/SAFIX/DARK as success rows;
- a Pons base rate taken from external counts without reproduction;
- social engagement as independent project truth;
- Deep Dive on every project discovery;
- a new scheduler if the existing Meme Alpha runtime can own the cadence;
- private-source leakage into public control plane;
- Codex dependency for research.

## 14. Strongest supporting case

The strongest support is not NET's later valuation. It is the combination of:

1. the repository's confirmed historical `PROJECT_TO_CA_JOIN_GAP`;
2. the existence of timestampable project surfaces before or around launch;
3. deterministic launch/contract infrastructure on Robinhood Chain;
4. a persistent no-token project universe that the current token-first flow does not naturally retain.

The mechanism is therefore plausible independently of the winner outcome.

## 15. Strongest falsification case

The strongest falsifier is that C may capture nearly all useful value.

Persistent project memory + deterministic material-change detection + exact CA binding may be sufficient. If so, Jev adds cost, variance and an adversarial-text attack surface without increasing recall, lead time or Deep-Dive efficiency.

A second strong falsifier is that project-first discovery may mostly surface serious projects that never produce economically useful, sellable token opportunities. N1/N2/N3 denominator rows will expose this.

## 16. False-positive and false-negative costs

### False positive

A bad project-to-CA link is high cost because it can contaminate wallet attribution, lifecycle outcomes and later learning. Therefore false-link tolerance is effectively zero for `BOUND_HIGH`.

Deep-Dive false positives are lower cost but must be bounded by load/cost caps.

### False negative

Dropping a project before CA publication can destroy the entire point of the bridge. Therefore project memory is persistent and low model confidence cannot delete evidence.

The system may deprioritize immediate research, but must retain the project and retrigger on material change.

## 17. Authority boundary

May change after a later reviewed shadow implementation:

- research discovery coverage;
- project-memory research fields;
- semantic research features;
- exact CA candidate/binding research state;
- Deep-Dive research queue prioritization within existing caps;
- prospective evidence rows.

May not change:

- portfolio;
- BUY/SELL;
- user alerts;
- live market state;
- Cycle Navigator;
- Master Monday;
- production signal weights;
- canonical framework doctrine;
- automated trade execution;
- evidence truth from model output;
- repository governance.

## 18. Validation against mission kill criteria

Current research result:

- deterministic-only solution has **not** yet been shown to match within margin -> prospective A/B/C required;
- critical evidence is explicitly retained -> PASS by design;
- Jev representation-order dependency is explicitly tested -> prospective gate;
- injection/spoof cannot gain truth authority -> PASS by design, prospective stress still required;
- material false link is a hard kill -> PASS by design;
- failed/similar denominator included -> PASS;
- NET/SAFIX/DARK advantage alone cannot pass -> PASS;
- held-out future population required -> PASS;
- Deep-Dive load is a primary metric and cap -> PASS.

## 19. Final Research Lab verdict

**Primary red-team classification:** FORWARD_TEST_CANDIDATE  
**Mission verdict:** **READY_FOR_SHADOW_BUILD**

Confidence in architecture: **HIGH**  
Confidence that project-first will produce measurable prospective alpha: **UNPROVEN**  
Confidence that Jev adds incremental value over deterministic C: **LOW-MEDIUM / UNPROVEN**

The bridge is worth building in shadow because the root gap is concrete and the experiment can cleanly kill itself. It is not ready for production, trading, user alerts or rule promotion.
