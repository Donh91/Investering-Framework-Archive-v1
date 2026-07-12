# Open Questions Register — Sensor Audit v1 Addendum

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Område:** unresolved evidence gaps / next actions  
**Primary folder:** `01_CORE_FRAMEWORK/governance/`  
**Depends on:** `01_CORE_FRAMEWORK/governance/2026-07-10__open-questions-register-v1-2__canonical.md`

## Updated questions

### OQ-PULLBACK — reproducible role and evaluation

```yaml
status: OPEN_NEEDS_FORWARD_ROWS
question: Does C2 retain timing value in prospectively frozen pullback events when A is urgency and D is confirmation/veto?
new_evidence: C-family beat frequency-matched timing placebo historically; A did not; D was late
next_action: instrument C2 and denominator/attribution fields in existing Pullback Edge rows
owner: GOVERNANCE_RESEARCH_LAB
```

### OQ-ROTATION — multi-axis survival value

```yaml
status: OPEN_DATA_DEPENDENT
question: Does ETHBTC plus frozen-universe breadth, BTC.D survival, deployment/activity and flow reduce fake rotation enough to justify delay?
resolved_blockers:
  - BTC_D_HISTORY
  - STABLECOIN_DEPLOYMENT_HISTORY
remaining_primary_blocker:
  - FROZEN_UNIVERSE_ALTCOIN_BREADTH
owner: RESEARCH_LAB
```

### OQ-B1-REPRO — 21 versus 22 B1 fires

```yaml
status: OPEN_MEDIUM
question: Which exact warm-up, eligibility or date-boundary rule explains the frozen 21-fire series versus direct 22-fire recomputation?
additional_date: 2025-03-04
next_action: independent source-backed reproduction without threshold changes
owner: RESEARCH_LAB_TRUTH_LAYER
```

### OQ-STABLE-LATENCY — operational availability

```yaml
status: OPEN_FORWARD_ONLY
question: Can any stablecoin activity context survive actual source latency and revision handling prospectively?
historical_finding: one additional delay day changed strategy return from +17.54% to -4.98%
next_action: log source and operational availability timestamps; no standalone strategy test promotion
owner: DATA_PING_RESEARCH_LAB
```
