# Historical Sensor Provenance & Validation Methods — 2026-08-21

Status: RESEARCH_ONLY_NON_CANONICAL

Purpose: preserve newly recovered historical provenance and strengthen the validation protocol for legacy shadow sensors without changing live market rules, thresholds, weights, portfolio execution, Master Monday logic, Cycle Navigator logic, or current sensor semantics.

## 1. Newly recovered provenance facts

### Early Rotation Pre-Trigger v1.1
Historical user archive material dated 2026-04-21 contains an explicit v1.1 definition:
- Stablecoin alt inflow 3D > +3%
- Large-cap alt volume share 3D > +4%
- ETH/BTC < 0.032
- BTC dominance > 56

The same source explicitly classifies the Pre-Trigger as an early-window/shadow signal, not a buy signal or standalone deployment authority.

A second archive document from 2026-04-21 describes the signal as a window signal rather than an event signal, identifies low sample size and survivorship-bias risk, and requires later confirmation by ETH/BTC, BTC dominance and breadth.

### Rotation Engine v2
Historical archive material dated 2026-04-22 documents:
- Pre-Trigger as an early warning only
- Rotation Readiness Score components
- breadth and dominance filters
- Macro Delay Window
- Fake Rotation Type 3 as Pre-Trigger + brief ETH/BTC improvement + high BTC.D + weak breadth
- execution only after broader confirmation

The archived claim that Type 3 had a 55–75% failure rate is a historical model claim only. It is not validated evidence and must be challenged independently.

### Later precedence change
Later DATA PING V3 archive material states that newer operational patches supersede older engine assumptions where they directly clarify the same area. In particular, because BTC dominance sources conflicted, fixed BTC.D levels were downgraded to directional interpretation until source reconciliation.

Therefore historical validation MUST version sensor semantics by date. The April v1.1 definition may be tested as the April historical definition where contemporaneous evidence exists. It must not be silently combined with the later ETF-era directional BTC.D interpretation.

## 2. Required version-boundary rule

For every reconstructed observation store:
- sensor_version
- definition_valid_from_utc
- definition_valid_to_utc where known
- definition_source_name
- definition_source_timestamp
- exact_threshold_semantics
- later_supersession_or_clarification

Do not evaluate a historical event with a later definition unless the test is explicitly labelled a modern counterfactual and kept separate from historical-framework evaluation.

## 3. Anti-overfitting methods to add to the research interpretation layer

The independent validation stage should explicitly account for multiple testing and backtest overfitting.

Relevant literature:
- Bailey & López de Prado, "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting, and Non-Normality", Journal of Portfolio Management, 2014, DOI 10.3905/jpm.2014.40.5.094.
- Bailey, Borwein, López de Prado & Zhu, "The Probability of Backtest Overfitting", Journal of Computational Finance, 2016/2017, DOI 10.21314/JCF.2016.322.
- Arian, Norouzi Mobarekeh & Seco, "Backtest overfitting in the machine learning era: A comparison of out-of-sample testing methods in a synthetic controlled environment", Knowledge-Based Systems 305 (2024) 112477, DOI 10.1016/j.knosys.2024.112477.

Implications for this framework:
1. Count materially distinct hypotheses / sensor variants tested. Do not report only the best-performing recovered sensor.
2. Do not choose outcome horizon post hoc. Predeclare or report the full horizon panel (6h, 12h, 24h, 48h, 72h, 7d, 14d, 30d where supported).
3. Where sample size permits, use leakage-aware time splits. Purge observations whose outcome windows overlap a test period and use an embargo where feature persistence can leak information.
4. Report results across chronological/regime partitions, not only pooled history.
5. For strategy-like return outputs, consider Deflated Sharpe Ratio / Probability of Backtest Overfitting only when their assumptions and sample size are appropriate. Do not force them onto categorical sensor outcomes.
6. For categorical sensors, prefer transparent event rates, matched non-trigger controls, calibration, false-positive rate, precision/recall where meaningful, and exact confidence intervals with small-sample caution.
7. Treat repeated variants, thresholds and horizons as a family of tests. Apparent significance must be interpreted under multiple-testing pressure.

## 4. Negative controls and baseline ladder

Every complex legacy sensor should be compared against the simplest available baselines over identical timestamps:
- ETH/BTC only
- BTC dominance direction only
- breadth only
- stablecoin/liquidity component only
- ETF flow component only where relevant
- current-stack signal available over the same period
- matched non-trigger periods
- timestamp-shift placebo where economically sensible

A complex sensor deserves future research attention only if it adds incremental information beyond its own components or creates a materially useful veto/filter with acceptable false-positive behaviour.

## 5. Priority implications

### Early Rotation Pre-Trigger
Highest-priority provenance candidate because an explicit dated definition exists. Historical testing must preserve the April thresholds exactly and separately test the later directional-BTC.D interpretation as a different version.

### Fake Rotation Type 3
Test primarily as a veto/filter. Do not inherit the archived 55–75% failure-rate claim as truth.

### ETF-era divergence classifiers
Separate BTC outcome from alt/ecosystem outcome. BTC survival and ecosystem deterioration are distinct dependent variables.

### ODM
Evaluate whether forecast errors are horizon-mismatch rather than signal failure, but prohibit selecting the best maturation horizon after outcomes are known.

### CCE
Build an explicit component-dependence map before counting multiple confirmations as independent evidence.

### SRE / FAE
Require clean timestamped forecast and outcome provenance before attribution. Otherwise mark bounded sections UNTESTABLE.

### RRS / RWE
Do not validate composite/adaptive weighting until component validity and dependence are established. RWE remains blocked from runtime.

## 6. Scientific stop rules

Use UNTESTABLE when:
- exact historical semantics cannot be recovered,
- required contemporaneous inputs are missing,
- only later prose exists,
- a proxy would materially change the meaning of the original sensor,
- source membership/provenance is unknowable,
- outcome and observation timestamps cannot be separated without leakage.

Prefer a small exact sample over a large synthetic sample.

## 7. Source-boundary note

The recovered user-archive documents establish historical framework claims and definitions. They do not by themselves validate predictive performance. External academic literature is used only to strengthen methodology, not to retroactively validate any framework sensor.
