# EXTERNAL ALPHA DISCOVERY & REVERSE ENGINEERING

Status: STANDING RESEARCH LANE / RESEARCH ONLY
Owner issue: #937
Scientific lifecycle owner: #885
Generic method: `../EXTERNAL_STRATEGY_REVERSE_ENGINEERING_PROTOCOL_v1.md`

## Mission

Continuously turn externally observable traders, bots, wallet cohorts and automated strategies into falsifiable research objects.

The lane exists to answer one question:

> Can the Framework isolate the part of an external strategy's apparent edge that is real, observable, copyable, scalable and transferable without importing the external bot wholesale?

The target is not source-code cloning. The target is revealed-policy reconstruction and independently validated transfer learning.

## Canonical chain

`DISCOVER -> VERIFY_IDENTITY -> VERIFY_TRACK_RECORD -> RECONSTRUCT_ACTIONS -> RECONSTRUCT_OPPORTUNITY_SET -> SOURCE_ALPHA -> OBSERVABLE_ALPHA -> COPYABLE_ALPHA -> SCALABLE_ALPHA -> TRANSFER_COMPONENT`

No stage may silently imply the next stage.

In particular:

- profitable source != observable signal;
- observable signal != copyable expectancy;
- copyable expectancy != scalable expectancy;
- behavioral similarity != recovered proprietary internals;
- attractive component != permission to trade capital.

## Standing artifacts

- `EXTERNAL_ALPHA_REGISTRY.json` - canonical machine-readable candidate registry.
- `CANDIDATE_INTAKE_SCHEMA.json` - minimum evidence contract for new candidates.
- `DISCOVERY_POLICY.md` - autonomous discovery/admission policy.
- `CROSS_STRATEGY_META_LEARNING_CONTRACT.md` - gate for learning across independently adjudicated strategies.
- `../../../../scripts/experiments/external_alpha_registry.py` - deterministic validator/scorer/gating logic.
- `../../../../tests/experiments/test_external_alpha_registry.py` - fail-closed tests.

Case-specific research remains in its existing owner files. This lane does not duplicate Edge, MAEVE, FOMO Radar or STAMPEDE research queues.

## Stable candidate states

### Admission decision

- `REJECT` - evidence value is too low or structurally unverifiable.
- `WATCH` - potentially interesting, but evidence is insufficient for expensive reverse engineering.
- `RESEARCH_QUEUE` - evidence justifies bounded forensic work.
- `REVERSE_ENGINEER` - evidence density is high enough for behavioral reconstruction.

### Promotion state

- `RESEARCH_ONLY`
- `SOURCE_ALPHA_PENDING`
- `SOURCE_ALPHA_VERIFIED`
- `SOURCE_EDGE_NOT_COPYABLE`
- `COPYABLE_ALPHA_VERIFIED`
- `SCALABLE_ALPHA_VERIFIED`
- `TRANSFER_CANDIDATE`
- `TRANSFERRED_COMPONENT`
- `KILLED`

Admission score is not a trading score. It estimates whether spending research effort on the external system is justified.

## Admission dimensions

The deterministic scorer rewards:

1. exact identity / source resolution;
2. independently reconstructable track record;
3. inclusion of losers / failed actions;
4. point-in-time timestamps;
5. action-ledger coverage;
6. reconstructable opportunity set / no-trade controls;
7. executable price / cost / latency evidence;
8. known version boundaries;
9. explicit falsifiers;
10. plausible reusable transfer value.

Hard caps apply to marketing-only evidence, selective winner feeds, ambiguous identity and other conditions that make apparent performance scientifically weak.

Scores decide admission depth only. Source/copy/scale promotion must come from the #885 experiment lifecycle and immutable result artifacts.

## Initial reference cases

### EXT-ALPHA-0001 - EdgeOnchain / Oddy

Role: prediction-market reference case.

Current value: unusually clean venue mechanics and public API/on-chain structure make it a strong methodological laboratory for separating source alpha from follower/copy alpha.

Current blocker: canonical Polymarket execution identity must still be primary-verified before the ledger is admitted.

Case owner: #922.

### EXT-ALPHA-0002 - MAEVE / CFGI

Role: primary crypto-AI behavioral reconstruction case.

The archived-era recovery already contains 432 parent positions and 1,073 fills, exceeding the standing Astra heavy-modeling row-count trigger. This does NOT mean arbitrary model fitting is allowed. The current bottleneck is leakage-clean feature alignment, matched no-trade controls, opportunity-set reconstruction and chronological validation.

MAEVE is the highest-value candidate for future transfer learning into the Framework because it is directly adjacent to CFGI, multi-timeframe crypto signals, DCA, exit logic, sizing and short-horizon market behavior.

### EXT-ALPHA-0003 - FOMO Radar

Role: wallet identity, provenance and cohort-quality case.

Highest-value candidate primitives include identity resolution, anti-seeding / dust provenance, normalized wallet ledgers and frozen post-score calibration. Direct copytrading remains unadmitted.

### EXT-ALPHA-0004 - STAMPEDE

Role: wallet rotation / herd-acceleration case.

Highest-value candidate primitives include same-wallet sell->buy sequence evidence, distinct-wallet breadth, acceleration and outcome journaling. It is jointly researched with FOMO Radar under #908 but retained as a separate candidate so marginal value can be ablated.

## New candidate routing

Every new user-supplied or autonomously discovered bot/strategy starts as a registry candidate, not a new engine.

Default prior: `REJECT` until evidence earns deeper work.

New candidates should be deduplicated against:

- existing registry entries;
- existing Auto Trading source notes;
- existing strategy families / owners;
- prior killed or abandoned candidates.

A new X post about an already-registered system updates evidence on that candidate. It does not create a duplicate case.

## Transfer contract

The Framework may never transfer an external strategy by name or reputation alone.

Transferable objects are the smallest falsifiable primitives that survive ablation, for example:

- feature family;
- selection/no-trade gate;
- sizing rule;
- timing rule;
- exit rule;
- DCA rule;
- provenance transform;
- regime gate;
- execution / maker-taker rule;
- latency / capacity model;
- risk veto.

Before transfer, the primitive must:

1. have an explicit causal/mechanical hypothesis;
2. beat the relevant existing Framework baseline under common clock/cost assumptions;
3. survive chronological/OOS or frozen-forward testing;
4. have a clear owner and rollback/kill rule;
5. preserve negative trials in accounting;
6. remain research-only until normal promotion governance grants additional authority.

## Cross-strategy learning

Do not mine patterns across mostly unverified bots.

The meta-learning gate is intentionally locked until:

- at least 5 candidates are independently adjudicated to source-alpha stage;
- at least 3 have a settled source-alpha ruling;
- at least 2 have a settled copyability ruling.

Once unlocked, recurrent primitives may be studied across cases, but candidate identity must remain visible so correlated strategies or duplicated code do not masquerade as independent evidence.

## Autonomy boundary

Agents may autonomously:

- search public sources;
- create/update registry candidates;
- deduplicate;
- collect read-only evidence;
- propose bounded experiments;
- run research-only replay / shadow tests under existing authority;
- downgrade/kill weak candidates;
- nominate a primitive for #885 testing.

Agents may not autonomously:

- sign transactions;
- deposit capital;
- copytrade;
- connect private wallets/keys;
- convert promotional claims into verified evidence;
- promote a component directly into live execution;
- silently alter failed-trial history.

## Research-budget rule

Optimize for expected information gain, not number of candidates.

Prefer one candidate with a reconstructable 1,000-row point-in-time ledger over 100 viral bots with screenshots.

Research depth should stop as soon as a hard falsifier is hit.

## Definition of success

The standing lane succeeds when a newly discovered external strategy can be routed consistently from discovery to either rejection or a reproducible research artifact, and when any component transferred into the Framework has stronger independent evidence than the external project's own marketing narrative.