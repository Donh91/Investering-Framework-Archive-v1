# Sensor Survival, Timing, Placebo & Regime Audit v1

**Dato:** 2026-07-12  
**Status:** CANONICAL  
**Evidence class:** CANONICAL_RESEARCH_EVIDENCE  
**Område:** sensor survival / timing / placebo / regime transportability  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `01_CORE_FRAMEWORK/governance/`, `04_MARKET_LEARNING/full_backtests/`, `06_RESEARCH_LAB/forward_tests/`  
**Depends on:** `04_MARKET_LEARNING/full_backtests/2026-07-12__full-sensor-simulation-backtest-v1__canonical.md`, `01_CORE_FRAMEWORK/governance/2026-07-12__btc-d-and-stablecoin-role-freeze-v1__canonical.md`  
**Package SHA-256:** `2c8f09873c117d9e10ab269e7a147e363475f0e87258052ca0aae8bdb971febb`  
**Package integrity:** `35 files / ZIP PASS / 34 internal checksums PASS`

## Frozen propositions

1. A sensor survives only if it adds role-specific decision value beyond simpler baselines and redundant sensors.
2. Measured timing must match the claimed role: urgency, warning, confirmation, veto or post-event context.
3. A claimed edge must survive frequency-matched, shifted and latency-aware placebos.
4. A useful sensor must transport across periods or be explicitly labelled regime-specific.

## Verdict

```text
STRONGEST SURVIVOR TO EXPAND: C-family, especially C2, as LEAN WARNING
STRONGEST DEMOTION: A3 to QUARANTINE / ZERO EXECUTION WEIGHT
CLEANEST ROLE FREEZE: D-family as CONFIRMATION/VETO, not prediction
BTC.D B1 EARLY WARNING: NOT_SUPPORTED / ZERO WEIGHT
STABLECOIN STANDALONE PREDICTOR: NOT_SUPPORTED / ZERO WEIGHT
STABLECOIN AVAILABILITY AND ACTIVITY CONTEXT: RETAIN WITH REDUNDANCY COMPRESSION
HIGHEST DATA EXPANSION PRIORITY: frozen-universe altcoin breadth
RULE PROMOTION: NONE
```

## Sensor survival

### A family

A retains urgency value but not precision authority. At a 30-day event window, A hit nine events, while frequency-matched random dates also had median nine. The observed alignment was not distinguishable from signal-density placebo.

A3 is quarantined. Removing A3 improved the historical trim-edge comparison by 24.4 percentage points and reduced false alarms, while wave recall fell from 9/9 to 7/9. This supports zero execution weight and forward observation, not historical deletion.

### C family

C is the strongest surviving warning family. At the 30-day event window, C hit nine events versus random median six; exploratory p approximately 0.006. The timing advantage remained stronger than random at 14, 21, 30 and 45 days. C2 is the principal expansion candidate, but only for forward row collection.

### D family

D is clean but late. Median lead was 0.5 day to C5 and four days to C12, with no false-alarm dates in the evaluated set. D is therefore confirmation/veto, not an independent early-warning vote.

## Timing atlas

```text
A family: 5d to C5 / 9.5d to C12 -> URGENCY
C family: 2d to C5 / 8d to C12 -> LEAN WARNING
D family: 0.5d to C5 / 4d to C12 -> CONFIRMATION/VETO
BTC.D B1: positive BTC follow-through building over 10–21d -> POST-STRESS/REBOUND CONTEXT
EXPANDING_DEPLOYMENT: median episode 2d -> SHORT-LIVED CONTEXT
JOINT_TRANSMISSION_STATE: median episode 1d -> FRAGILE SHADOW STATE
```

## Placebo and leakage findings

- M1 contains ten events, while the prior M2 performance denominator used nine evaluable events. Including PW01 changes 4/4 Storm recall to 4/5. Future reporting must expose total, eligible, excluded and exclusion reason.
- Six rule/date signals were assigned to two overlapping events. Future scoring must use non-overlapping windows or one-to-one attribution.
- Direct B1 recomputation produced 22 fires, while the frozen canonical package contains 21. The additional date is 2025-03-04. This remains a reproducibility discrepancy; the frozen historical result is not rewritten.
- Expanding-deployment strategy return changed from +17.54% to -4.98% after one additional operational-delay day. This rejects production robustness.
- 89/108 nearby transmission configurations were positive in-sample, but only 3/108 were positive in both train and 2026 test; those survivors barely traded.

## Regime transportability and decay

- EXPANDING_DEPLOYMENT had negative median ETH/BTC returns at 7, 14 and 30 days in the pooled weekly sample.
- Its 14-day relative median was negative in Downtrend, Transition and Uptrend.
- Rolling 26-week median advantage was positive in only 11.1% of eligible windows; last positive window was 2025-12-22.
- BTC.D B1 transported as positive BTC survival/rebound context, not as early downside warning.
- C family transported best among M1 warning roles, but the sample remains one-cycle and too small for authority promotion.

## Stablecoin axis compression

Weekly DEX-volume change and DEX/supply-ratio change had Spearman correlation near 0.998. They are one activity family, not two independent confirmations.

Retained axes:

```text
stablecoin supply change -> LIQUIDITY AVAILABILITY
one normalized DEX activity measure -> REALIZED ACTIVITY
chain-positive share -> DISTRIBUTIONAL SHADOW CONFIRMATION
```

## Machine consequence

### Expand evidence production

```text
C2 forward warning rows
frozen-universe altcoin breadth
TechDev category-specific outcome calibration
```

### Retain with narrow roles

```text
A1/A2 = urgency only
C1/C2 = lean warning
D2/D3 and price structure = confirmation/veto
BTC.D = rotation survival/reclaim context
stablecoin supply = liquidity availability
one normalized activity proxy = realized activity
chain activity breadth = shadow confirmation
ATR = range/volatility infrastructure
```

### Demote or compress

```text
A3 = quarantine / zero execution weight
BTC.D B1 early warning = zero
stablecoin deployment standalone = zero
DEX change + DEX/supply ratio = one activity axis
EMA50 = merge into price structure context
DAYS_BELOW_GATE = retire as redundant with BASE_DEPTH
SIG_A = reject
SIG_B = shadow only
```

## Evidence and authority boundary

The audit is retrospective research evidence. It modifies evidence classifications, role boundaries, blocker states and forward instrumentation. It creates no market call, portfolio action, live threshold change, new engine, new test, new score or automatic promotion.

## Machine-readable archive

Primary data root:

```text
06_RESEARCH_LAB/audit_summaries/sensor_survival_v1/
```

The complete external package is identified by SHA-256 above. Binary charts are not duplicated through the text-only connector; their identities remain in the package manifest and checksums.
