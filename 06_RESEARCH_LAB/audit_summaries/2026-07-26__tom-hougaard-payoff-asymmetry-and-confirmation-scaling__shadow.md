# Tom Hougaard Payoff Asymmetry and Confirmation Scaling Audit

**Dato:** 2026-07-26  
**Status:** SHADOW_ONLY / SELECTIVE_ACCEPT  
**Område:** decision quality / payoff distribution / deployment discipline  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `08_SOURCE_MATERIAL/external_methods/`, `06_RESEARCH_LAB/forward_tests/`, `05_CYCLE_NAVIGATOR/`  
**Depends on:** Continuous Forward Evidence Accumulation v1, Active Test Registry, FRLP v0.1

## Executive verdict

```yaml
research_relevance: HIGH_FOR_L1_AND_BOUNDED_L2
intradaday_method_relevance: LOW
new_signal: NO
new_test: NO
new_engine: NO
current_rebuy_change: NO
current_deployment_change: NO
portfolio_action: NO
```

The durable contribution is not a trading setup. It is a decision-quality reminder:

```text
A system may be right frequently and still destroy value when losses,
missed upside or false restraint dominate the payoff distribution.
```

A second bounded contribution is:

```text
After permission exists, scaling should respond to confirmed survival
of the winning state rather than to the emotional desire to realise a small gain.
```

That principle is not permission to unlock, chase price or import intraday pyramiding.

## L1 - Payoff asymmetry over hit rate

### Decision

```yaml
verdict: ACCEPT_AS_ALREADY_OPERATIONALISED_METHOD_LEARNING
new_schema_required: NO
new_metric_engine_required: NO
```

The FXCM result supports the general proposition that hit rate alone is insufficient. It does not independently validate any Cycle Navigator model.

The framework already implements the correct response through:

- Winkler alongside Jaccard and containment in FRLP;
- adjustment alpha versus simple baselines;
- MFE and MAE;
- maximum drawdown;
- drawdown avoided;
- missed upside;
- opportunity cost;
- false-permission cost;
- unit-matched outcome distributions.

The operational protocol explicitly states that hit rate or lift alone is insufficient and requires these distribution fields for matured rows.

Therefore Claude's R2 does not justify another field family or duplicate owner.

Required enforcement:

```text
A summary may not declare success from containment, Jaccard, hit rate,
correct-state share or signal survival alone when the corresponding
payoff and opportunity-cost distribution is unavailable.
```

## L2 - Add to winners and confirmed deployment

### Decision

```yaml
verdict: RETAIN_AS_CONDITIONAL_POST_PERMISSION_DESIGN_PRINCIPLE
current_activation: NO
owner_routing: [FNP_CUMULATIVE, ROTATION_SURVIVAL_FORWARD]
new_test: NO
```

The useful translation is not Hougaard's position sizing or intraday pyramiding.

The bounded translation is:

```text
Once an existing governance gate grants permission,
additional deployment may be evaluated against confirmation survival,
not against first-touch excitement or fear of losing an open gain.
```

A future confirmation ladder must be frozen before use and must specify:

```text
permission prerequisite
eligible asset tier
confirmation state
settled hold requirement
maximum tranche count
maximum aggregate exposure
invalidation state
cooldown or re-entry rule
benchmark action
missed-upside cost
false-confirmation cost
MAE and drawdown limit
```

It must compete against:

```text
single deployment at first permission
WAIT
existing permission schedule
simple equal tranches
```

No ladder may be activated while rebuy remains locked or before the governing Stage-1 decision exists.

## L3 - Good loser, weak winner

### Decision

```yaml
verdict: ACCEPT_AS_AUDIT_INTERPRETATION_ONLY
```

The phrase is a useful compression of a known asymmetry:

- the framework has demonstrated value in avoiding or limiting some stress periods;
- the framework still needs enough prospective rows to measure missed and undersized participation during valid recovery or rotation states.

This does not prove that the framework is systematically a poor winner. That conclusion remains conditional on T2, T5 and deployment-survival rows.

Accepted wording:

```text
Winner-capture and false-restraint costs remain under-measured relative to damage limitation.
```

Rejected wording:

```text
The framework is already proven to be a poor winner.
```

## L4 - Price action and breach taxonomy

### Direct import

```yaml
intradaday_breakout_method: REJECT
cfd_stop_microstructure: REJECT
breakeven_snap_as_weekly_rule: REJECT
raw_intraday_break_as_confirmation: REJECT
```

Reasons:

- wrong time resolution;
- different venue and leverage structure;
- crypto trades continuously through weekends;
- intraday stop clusters do not map mechanically to weekly state;
- live versus settled governance already forbids first-touch promotion.

### Bounded research candidate

```yaml
candidate: LIQUIDITY_SWEEP_VS_STRUCTURAL_BREACH_ANNOTATION
status: APPROVED_SHADOW_SUBANALYSIS_NOT_NEW_TEST
owner: FRLP_V0_1
```

Existing M5 or FRLP breach observations may be annotated, without rewriting original rows, as:

```text
LIQUIDITY_SWEEP:
range edge breached intraperiod but reclaimed by the frozen settled-close rule

STRUCTURAL_BREACH:
range edge breached and remained outside at the frozen settlement point

UNRESOLVED:
source granularity or week convention cannot determine the class
```

The annotation may test whether:

- Jaccard overstates failure when a wick is quickly reclaimed;
- containment and breach-day counts hide path quality;
- sweep frequency differs by volatility or event regime;
- structural breaches carry materially worse MAE or follow-through.

Constraints:

```text
no retrospective range modification
no relabelling of the original forecast
no deletion of breach days
no portfolio authority
no new test ID
all annotation rules frozen before reading outcomes beyond the breach day
```

## L5 - Process and journalling

### Decision

```yaml
verdict: REDUNDANT_WITH_EXISTING_GOVERNANCE
```

Scenario preparation, falsifiers, journal discipline and sufficient-row requirements are already encoded in repository governance and forward evidence protocols.

No additional process layer is warranted.

## What is explicitly not imported

```text
self-reported P&L records
competition and marketing claims as proof of edge
GBP 3,500 per point risk culture
high leverage as a route to performance
intradaday CFD setup details
celebrity or top-1-percent framing
course or social-media authority
sub-40-percent hit-rate or 4-to-1 payoff claims without primary ledger evidence
```

The framework may import a ratio discipline without importing stake size.

## Permanent learning retained

```text
1. Correct classification frequency is subordinate to payoff distribution.
2. Missed upside and false restraint are losses, but not equivalent to realised drawdown.
3. Scaling after permission is a separate decision from granting permission.
4. Confirmation-based scaling must be prospectively frozen and benchmarked.
5. Intraperiod sweeps and settled structural breaches should not be conflated.
6. High leverage and public performance claims receive no evidentiary shortcut.
```

## Operational disposition of Claude candidates

```yaml
R1_sweep_vs_structural:
  decision: ACCEPT_BOUNDED_SHADOW_SUBANALYSIS
  new_test: false
  original_rows_rewritten: false

R2_captured_vs_foregone_fields:
  decision: ALREADY_IMPLEMENTED
  schema_change: false

R3_post_unlock_confirmation_ladder:
  decision: QUEUE_AS_CONDITIONAL_DESIGN_ONLY
  activation: false
  prerequisite: GOVERNING_PERMISSION_AND_PREREGISTERED_RULES
```

## Authority boundary

```text
SOURCE ARCHIVE: YES
SHADOW LEARNING: YES
BOUNDED RETROSPECTIVE ANNOTATION: YES
NEW ACTIVE TEST: NO
NEW ENGINE: NO
NEW SENSOR: NO
CURRENT REBUY CHANGE: NO
CURRENT DEPLOYMENT CHANGE: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
PORTFOLIO ACTION: NO
```
