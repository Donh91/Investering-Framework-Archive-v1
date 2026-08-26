# Exit Ladder Owner Block and Cowork Adjudication

**Date:** 2026-08-26

**Status:** RESEARCH_AUDIT_RECEIPT

**Scope:** capital preservation / cycle-top research / Exit Ladder accountability

**Primary owner updated:** `04_MARKET_LEARNING/shadow_protocols/2026-07-11__s4-hybrid-zero-weight-shadow-logging-protocol-v0-1__canonical.md`

**Authority:** RESEARCH_ONLY / ZERO_MARKET_AND_PORTFOLIO_AUTHORITY

## Source binding

```yaml
source_package: THE_LAST_20_PERCENT_RESULT_LAST_20_PERCENT_CAPITAL_PRESERVATION_V1_20260826.zip
source_package_sha256: ec837d2046ccbf1265e98f59fa87b47a0a92bc511a79a3de369e803bfad81189
source_bound_control_commit: 0f77dd408dcee4f54b9d77e73fe87f96159b8e0c
source_authority: RESEARCH_ONLY_NON_CANONICAL
source_github_writes: 0
source_paid_calls: 0
```

The source ZIP checksum matched. All 82 package checksums passed and its QA
gate passed 37 of 37 checks. An offline rerun reproduced the classifications
and headline tables. One byte-level difference remained in
`results/F2_pareto_frontier.csv`: the local pandas version retained additional
floating-point digits in one derived column, with a maximum numeric difference
of 0.00004 and no Pareto-classification change. The package is therefore
semantically reproducible, but its claim of byte-identical results across any
recent pandas version is too strong.

## Findings retained

1. A dedicated historical crypto cycle-top predictor is not robustly
   identifiable from three completed independent macro cycles. This is a
   research ceiling, not proof that any specific exit rule works or fails.
2. The Exit Ladder CSV has zero valid rows and its E0-E7 transition conditions,
   native producer and lifecycle are not defined at the owner.
3. The Three-Horizon Action Compass exposes Lane-3 distribution and exit
   vocabulary, but it is explicitly an output contract and supplies no native
   E0-E7 evaluation.
4. The tested three-input confluence candidate was almost entirely redundant
   with the one-input price-trend classification. This supports simplification,
   not a new rule.
5. Fixed amplitude thresholds and named historical top callers remain
   unsuitable for live authority. The current evidence permits historical
   context or a reference challenger only.

## Claims not retained

### Random matched-duration result

The supplied A5 null is not duration matched. Random blocks may overlap, so
the realized defensive duration is shorter than the target. For the 200-day
trend state the mean shortfall was about 2.7 to 3.3 percent of cycle days. For
the staged ladder it was about 16.4 to 17.4 percent. The staged ladder also
uses partial exposures, while A5 replaces every matched day with zero exposure.

A stricter circular-shift timing null preserved the observed defensive days,
episode pattern and exposure intensity. Under that check, the 200-day trend
state beat 89.2%, 68.5% and 59.0% of shifted timings across H1-H3, not 95.5%,
61.1% and 47.6%. The claim that it beat random timing in only one of three
cycles is therefore not robust. The staged ladder beat 62.2%, 56.8% and 33.4%,
so the claim that it was worse than random in all three cycles is also false
under the stricter null.

No positive edge claim follows from the replacement check. Effective n remains
three and the timing-null choice is itself a modelling decision.

### Proposed percentile survivor

The package evaluated fixed Mayer thresholds, not a trailing Mayer percentile.
No code or result file tests the proposed percentile transform. It is an
unexecuted challenger suggested after observing fixed-threshold decay, not a
surviving measured signal.

### Protective-exit attribution

The reported protective-exit date is selected using the later realized trough:
the earliest transition after which mean exposure through that trough is at
most 0.35. Policy equity and maximum-drawdown paths remain causal, but the
selected exit date, top capture and lead-time narrative are retrospective
attributions. They cannot be treated as a real-time trigger result.

### Warning confidence interval

The warning-quality interval resamples 180-day blocks as exchangeable across
the full series. The same package documents strong amplitude decay and a
post-ETF structural break. The interval is descriptive under a stationarity
assumption that the evidence itself challenges. It does not validate the
proposed percentile warning.

### Loss-weight binding

The proposed `lambda >= 0.23` uses the midpoint pair 15% and 70% plus one
chosen utility family. The user's stated 10-20% versus 60-80% ranges do not
identify that point, and LF001 explicitly records a directional preference,
not a numeric utility weight. LF001 remains `NEEDS_GOVERNANCE_BINDING`.

### Existing-owner integration

The proposed four-state shortcut cannot be merged as written:

- mapping E0 directly to E4, E5 or E6 violates the owner's no-skip rule;
- the current 19-column CSV has one `outcome_window` and one `outcome`, while
  the proposal requires 30, 90 and 180 day outcomes from one emission;
- Exit Ladder has no registered active-test lifecycle or validator;
- FNP requires actual frozen decision divergence, not a warning label alone;
- T6 is an alt-rotation survival owner and does not own general BTC exit
  evidence.

## Decision

```yaml
research_verdict: MODIFY_EXISTING_OWNER
historical_top_predictor: NO_GO_HISTORICAL_IDENTIFIABILITY
row_program_as_proposed: REJECT
loss_contract_as_proposed: REJECT
percentile_warning_as_survivor: REJECT_UNEXECUTED
exit_ladder_status: OWNER_BLOCKED
new_engine: false
new_test: false
new_threshold: false
rows_added: 0
market_state_change: false
portfolio_action: false
```

The only implemented change is a documented blocked state in the existing Exit
Ladder owner. This prevents pseudo-rows and preserves the useful part of the
research: the framework still has an exit-accountability gap, but the supplied
shortcut does not validly close it.
