# FRESH RESEARCH THREAD — HISTORICAL SHADOW SENSOR VALIDATION v1

Act as an independent principal investigator and adversarial research-methodologist.

## Input
First audit the current GitHub repository `Donh91/Investering-Framework-Archive-v1` and read the full Codex/reconstruction package under:
`06_RESEARCH_LAB/historical_sensor_recovery_v1/validation_v1/`

Also read:
- `04_MARKET_LEARNING/shadow_registry/LEGACY_RECOVERY_QUEUE.json`
- `06_RESEARCH_LAB/historical_sensor_recovery_v1/RECOVERED_LEGACY_SENSOR_DEFINITIONS_2026-08-21.json`
- `06_RESEARCH_LAB/historical_sensor_recovery_v1/HISTORICAL_SHADOW_SENSOR_VALIDATION_MASTER_HANDOFF_v1.md`

GitHub is authoritative for current state. The reconstruction package is evidence, not a verdict.

## Mission
Determine whether recovered legacy shadow sensors contain historically observable incremental information that merits prospective forward testing, or whether they are redundant, noisy, regime-specific, or untestable.

Do NOT promote sensors. Do NOT change canonical rules, thresholds, weights, market semantics, portfolio execution, Master Monday logic or Cycle Navigator logic.

## Adversarial questions
For every testable sensor ask:
1. Was its definition known before the evaluated outcome?
2. Can its state be reconstructed without hindsight?
3. Does it add information beyond simpler components such as ETHBTC, BTC dominance, breadth, ETF flows, liquidity and derivatives?
4. Is apparent performance driven by a few famous episodes?
5. Does the result survive negative controls and matched non-trigger periods?
6. Is it robust to reasonable outcome horizons without choosing the best horizon after seeing results?
7. Does the sensor duplicate another current or recovered sensor?
8. Is usefulness regime-specific?
9. What failure modes are visible?
10. What prospective test would falsify the hypothesis?

## Special focus
### Early Rotation Pre-Trigger
Test lead time versus false positives and incremental value beyond its own components. Never treat the archived threshold set as newly validated merely because it fits history.

### Fake Rotation Type 3
Test as a veto/filter. Explicitly challenge the archived claimed 55-75% failure-rate range. That range is an archived model claim, not established evidence.

### ETF-era classifiers
Test whether ETF absorption genuinely creates a useful distinction between BTC survival and broader alt deterioration. Separate BTC outcome from portfolio/alt outcome.

### ODM
Evaluate whether errors previously classified as bad signals are better explained by maturation-horizon mismatch. Avoid selecting the best horizon post hoc.

### CCE
Map shared inputs, transformations and common latent drivers. Estimate where multiple confirmations are effectively the same information and therefore should not increase confidence independently.

### SRE / FAE
Assess whether available historical outcome/forecast ledgers are sufficiently clean for attribution. If not, mark bounded parts UNTESTABLE rather than reconstructing intent.

### RRS / RWE
Do not validate composites/adaptive weighting until component validity and dependence are established. RWE remains runtime-blocked.

## Required verdict vocabulary
Use only:
- KEEP
- WATCH
- REDUNDANT
- NOISE
- REGIME_SPECIFIC
- UNTESTABLE
- PROSPECTIVE_TEST_JUSTIFIED

`PROSPECTIVE_TEST_JUSTIFIED` means only that a separate forward test is scientifically warranted. It is not canonical promotion.

## Required outputs
Produce:
1. Executive conclusion.
2. Sensor-by-sensor evidence table.
3. Provenance/leakage audit.
4. Lead-lag findings.
5. False-positive and negative-control findings.
6. Redundancy/dependence map.
7. Regime-specific findings.
8. Data-quality sensitivity analysis.
9. Ranked prospective-test queue.
10. Explicit list of sensors/components that should be retired from further research because they are redundant/noise/untestable.
11. Concrete recommendations for Shadow Registry weekly calibration, without changing canonical authority.
12. A machine-readable JSON verdict block suitable for GitHub archival.

## Scientific discipline
Prefer `UNTESTABLE` over invented data. Prefer `REDUNDANT` over keeping complexity for its own sake. A sensor must beat or complement simpler baselines to justify future attention.

Historical fit is hypothesis-generation only. Any material live-framework change requires separate prospective evidence and separate approval/governance.
