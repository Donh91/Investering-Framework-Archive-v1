# Historical Effectiveness Findings

## 1. Rotation family

### ETH/BTC persistence

The archive repeatedly converges on the same correction: one-day ETH/BTC strength is too weak. The useful concept is persistence, higher-lows / sustained relative strength and survival through pullbacks.

Historical usefulness type: `EARLY_WARNING + CONFIRMATION`

Evidence strength: medium-high as an information family, lower for any single historical threshold.

Verdict: `KEEP`.

### Breadth survival

Breadth is one of the most consistent false-rotation filters in the archive. It is especially valuable for distinguishing selective large-cap participation from genuine broad expansion.

Historical usefulness type: `VETO + REGIME_CLASSIFIER`.

Evidence strength: medium-high conceptually; source definitions vary over time.

Verdict: `KEEP`.

### BTC dominance

BTC.D is useful when treated as path and persistence information rather than one immutable level. Historical replay research suggests reclaim behavior may have more discrimination than large composite scores.

Historical usefulness type: `VETO + REGIME_CLASSIFIER`.

Evidence strength: medium, with source/denominator caveat.

Verdict: `KEEP` with version freeze.

### Early Rotation Pre-Trigger

This is a plausible early-warning composite, but the historical archive does not provide a clean enough event table for its distinctive inputs to establish incremental edge. Its old high-reliability wording must be downgraded.

Historical usefulness type: intended `EARLY_WARNING`.

Verdict: `PROSPECTIVE_TEST_JUSTIFIED`, not historically validated.

### Fake Rotation Type 3

The conceptual pattern remains useful: flows/relative strength without breadth can fail. The historical numeric failure-rate claim is not reproduced.

Historical usefulness type: `VETO`.

Verdict: `WATCH`; retire the old percentage claim.

## 2. ETF-era absorption and transmission

### ETF flows alone

Positive ETF flows are not a reliable broad-risk signal. The archive correctly evolved from raw flow direction toward flow quality, persistence, concentration and whether liquidity transmits beyond BTC.

Historical usefulness type: `CONTEXT`, not standalone predictor.

Verdict: raw ETF inflow as bullish confirmation = `REDUNDANT/WEAK`; ETF flow quality = `KEEP`.

### Hidden deterioration under stable BTC

This is one of the strongest ETF-era research concepts. BTC can remain supported while ETH/BTC, breadth and alt participation deteriorate. The idea is repeated across Claude, DATA PING and the current legacy recovery hypotheses.

Historical usefulness type: `RISK_DETERIORATION + REGIME_CLASSIFIER`.

Verdict: `KEEP` as information family; individual HDS/SPTD formulas require evaluator validation.

### Stablecoin supply versus deployment

The archive correctly learned that stablecoin growth is not equivalent to risk deployment. Parking versus deployment is more informative than supply growth alone.

Historical usefulness type: `REGIME_CLASSIFIER`.

Verdict: stablecoin supply alone = `REDUNDANT/WEAK`; deployment behavior = `KEEP/WATCH` depending data quality.

## 3. Stress / flush family

A June case study is especially informative. The contemporaneous read separated:

- CFGI as early stress signal,
- ETF flows as structural pressure,
- liquidation clusters as depth/timing,
- funding/OI as acceleration mechanism,
- ETH/BTC as evidence that the flush did not become rotation.

The lesson is not that any one input predicted the bottom. The lesson is functional decomposition.

Historical usefulness type:

- CFGI: stress context
- ETF: structural flow context
- liquidation clusters: timing/depth
- funding/OI: leverage mechanism
- reclaim quality: post-flush confirmation

Verdict: `KEEP` as diagnostic stack; insufficient n for a hit-rate claim.

## 4. Macro family

Copper/Gold, M2 and macro delay concepts are useful as context, but early Shadow v1-v8 lead-time bands were explicitly synthesized rather than statistically backtested.

Historical usefulness type: `REGIME_CONTEXT`.

Verdict: `REGIME_SPECIFIC/WATCH`; do not use old lead-time bands as empirical constants.

## 5. Adaptive-learning family

### CCE

Confidence compression / dependence control becomes more important as the number of named sensors increases. Multiple views of ETH/BTC, breadth, TOTAL3 and deployment can look like independent confirmations while sharing one latent driver.

Verdict: `KEEP` as anti-double-counting method.

### ODM

Outcome delay is a valid methodological concern. Some signals may naturally manifest on different horizons. However, this cannot be used to rescue failed historical predictions by selecting a favorable horizon after the fact.

Verdict: `KEEP` as fixed-horizon maturation control.

### SRE / FAE

Attribution is valuable only when contemporaneous input identity is clean. Much historical material is not clean enough for full sensor-level attribution.

Verdict: `KEEP CONCEPT`, historical sensor attribution often `UNTESTABLE`.

### RWE

Regime weighting is the highest overfitting-risk layer because it can transform retrospective patterns directly into live influence.

Verdict: `BLOCKED_FROM_RUNTIME` on historical evidence alone.

### FNP / Cumulative False Negative Ledger

This is one of the highest-value governance findings. Historical research suggests confirmation delay can accumulate across multiple gates. FNP makes late-but-correct behavior visible.

Verdict: `KEEP`, high-priority learning control.

## 6. Current Entry Signal Ledger

The current repository-native performance summary has two activation events, but only one matured 24h event and no matured 7d/14d/30d sample. That one 24h event showed positive BTC and ETH returns, but it cannot support a reliability estimate.

Verdict: `WATCH`.

## 7. Most important falsifications

The review rejects or downgrades these old ideas as established facts:

- Fake Rotation Type 3 55-75% historical failure rate.
- Early Rotation Pre-Trigger near-perfect historical reliability.
- Microcap 75-85% failure-rate claim without event rows.
- Fixed old BTC.D / ETHBTC thresholds as timeless laws.
- Stablecoin growth alone as bullish liquidity evidence.
- ETF inflows alone as broad ecosystem health.
- Multiple correlated confirmations as automatically higher confidence.

## 8. Most important surviving hypotheses

The research that remains most worth testing is simple:

1. Does ETH/BTC persistence add lead-time before breadth confirmation?
2. Does BTC.D reclaim materially improve fake-rotation filtering?
3. Does breadth survival explain most of the difference between selective pumps and real rotation?
4. Does ETF-flow quality plus transmission state detect hidden deterioration earlier than BTC price?
5. Do liquidation/OI/funding/reclaim variables improve pullback timing without becoming bottom-pickers?
6. Can a <=3 information-family model match the larger shadow stack?
7. How much opportunity cost is created by adding confirmations that do not reduce false positives materially?