# FRED Classic Targeted Series Production Upgrade

**Dato:** 2026-07-05  
**Status:** CANONICAL  
**Område:** Macro Shadow Layer, FRED, Master Monday, backtest integrity  
**Primary folder:** 04_MARKET_LEARNING/macro_shadow/  
**Related folders:** 02_DATA_PING/source_qa/, 03_WEEKLY_OPERATIONS/master_monday/, 06_RESEARCH_LAB/forward_tests/  
**Supersedes:** Prior FRED bulk probe status BACKTEST_READY_PARTIAL  
**Depends on:** DATA PING V4 Sensor Discipline Doctrine, Archive Map & Routing Rules

---

## 1. Executive conclusion

FRED Classic v1.2 targeted-series access is now production-ready as a Macro Shadow Layer input.

This does not change crypto market state.

It does change FRED's framework status from:

```text
BACKTEST_READY_PARTIAL
```

to:

```text
BACKTEST_READY_FULL
```

Based on the custom GPT run:

```text
FRED_CLASSIC_V1_2_FULL_DEMONSTRATION
DATE: 2026-07-05
SOURCE: FRED Classic v1.2 PASS
Observations: 43/43 PASS
Metadata: 5/5 PASS
Vintage/backtest: 8/8 PASS
Mode: TARGETED_SERIES_ONLY
Bulk v2 used: false
Crypto sources used: false
```

Canonical verdict:

```text
FRED Classic Targeted Series = production macro context
FRED Bulk Release = discovery only
FRED Macro = weekly / Master Monday input
FRED Macro ≠ daily crypto trigger
```

---

## 2. What changed

Earlier FRED testing showed that FRED access and release-level bulk discovery worked, but production use was limited because first cursor pages were not target-ready.

The new run confirms that exact targeted series retrieval now works across the framework's required macro categories.

This upgrades FRED from infrastructure experiment to production macro-shadow input.

---

## 3. Data coverage confirmed

The run successfully accessed:

```text
Rates / curve
Real rates
Inflation expectations
Credit spreads
VIX / financial conditions
Fed balance sheet / liquidity proxies
Policy / funding rates
Dollar / FX
Slow macro calibration
Vintage / point-in-time dates
Metadata
```

---

## 4. Macro shadow digest from 2026-07-05 run

```text
rates_pressure: UP
real_rate_pressure: UP
inflation_expectations: SLIGHTLY_UP
credit_stress: LOWER_OVER_5OBS
vol_stress: LOWER_OVER_5OBS
liquidity_proxy: MIXED
policy_funding: STABLE
dollar_pressure: SLIGHTLY_FIRMER
slow_macro: MONTHLY_QUARTERLY_CALIBRATION_ONLY
```

Framework read:

```text
MACRO_SHADOW:
Mixed / cautious-neutral

Macro impact:
No clean tailwind
No acute stress
```

---

## 5. Current FRED category reads

### 5.1 Rates and curve

Key series:

```text
DGS3MO
DGS2
DGS10
DGS30
T10Y2Y
```

Run read:

```text
Nominal rates higher across 2Y / 10Y / 30Y.
10Y-2Y spread positive and wider over last 5 valid observations.
```

Framework interpretation:

```text
Rates pressure: UP
Curve: positive / modestly wider
Crypto impact: macro tailwind not clean
```

---

### 5.2 Real rates and inflation expectations

Key series:

```text
DFII10
T10YIE
T5YIE
T5YIFR
```

Run read:

```text
Real-rate pressure higher.
Breakeven inflation measures slightly higher.
```

Framework interpretation:

```text
Real-rate pressure: UP
Inflation expectations: SLIGHTLY_UP
Crypto impact: mixed, not a clean risk-on tailwind
```

---

### 5.3 Credit stress

Key series:

```text
BAMLC0A0CM
BAMLH0A0HYM2
BAMLH0A1HYBB
BAMLH0A2HYB
BAMLH0A3HYC
```

Run read:

```text
Credit spreads lower across IG / HY / BB / B / CCC over last 5 valid observations.
```

Framework interpretation:

```text
Credit stress: LOWER
Risk stress: easing
Crypto impact: supportive context, not sufficient for rotation
```

---

### 5.4 Volatility and financial conditions

Key series:

```text
VIXCLS
NFCI
ANFCI
```

Run read:

```text
Volatility lower.
Financial conditions measures remain negative.
```

Framework interpretation:

```text
Vol stress: LOWER
Financial conditions: still easy / loose by index level
Crypto impact: supportive context, but not deployment proof
```

---

### 5.5 Liquidity and Fed balance sheet

Key series:

```text
WALCL
WRESBAL
WTREGEN
RRPONTSYD
M2SL
```

Run read:

```text
Liquidity proxies mixed.
Fed balance sheet slightly lower WoW.
Reserve balances higher WoW but lower vs 5 observations.
RRP low.
M2 higher on monthly cadence.
```

Framework interpretation:

```text
Liquidity proxy: MIXED
Crypto impact: not a clean tailwind, not acute stress
```

---

### 5.6 Policy and funding

Key series:

```text
DFF
SOFR
EFFR
OBFR
IORB
```

Run read:

```text
Policy / funding rates broadly stable.
```

Framework interpretation:

```text
Policy/funding: STABLE
Crypto impact: neutral context
```

---

### 5.7 Dollar / FX

Key series:

```text
DTWEXBGS
DEXUSEU
DEXJPUS
DEXCHUS
DEXUSUK
```

Run read:

```text
Broad dollar index slightly firmer over last 5 valid observations.
```

Framework interpretation:

```text
Dollar pressure: SLIGHTLY_FIRMER
Crypto impact: mild dampener, not decisive
```

---

### 5.8 Slow macro calibration

Key series:

```text
CPIAUCSL
CPILFESL
PCEPI
PCEPILFE
UNRATE
PAYEMS
ICSA
INDPRO
RSAFS
GDP
GDPC1
```

Run read:

```text
Slow macro is usable for weekly / Master Monday calibration, not daily trigger.
```

Framework interpretation:

```text
Slow macro: MONTHLY / QUARTERLY ONLY
Use for: macro regime context, not daily signals
```

---

## 6. Vintage and backtest support

The most important upgrade is not the current macro read.

The most important upgrade is that vintage / point-in-time support works.

Confirmed vintage support for:

```text
DGS10
T10Y2Y
BAMLH0A0HYM2
VIXCLS
WALCL
RRPONTSYD
CPIAUCSL
GDP
```

Canonical learning:

```text
Vintage endpoint works for point-in-time / backtest control.
Backtest leakage risk can now be reduced.
```

This matters for Research Lab, historical replay and Master Monday calibration because the framework can test what would have been knowable at the time.

---

## 7. Boundary conditions

FRED data must not determine:

```text
market_state
recovery
rotation
rebuy
deployment
official_row
FNP_PATH
```

The run itself correctly marked:

```text
market_state: NOT_DETERMINED
recovery: NOT_DETERMINED
rotation: NOT_DETERMINED
rebuy: NOT_DETERMINED
deployment: NOT_DETERMINED
official_row: NOT_DETERMINED
FNP_PATH: NOT_DETERMINED
```

Canonical rule:

```text
Macro context can condition confidence.
It cannot unlock crypto execution gates by itself.
```

---

## 8. Integration with framework

### Daily DATA PING

Use only compact status if exact targeted FRED series are available.

Example:

```text
FRED_MACRO_STATUS: TARGET_SERIES_PASS / BACKTEST_READY_FULL
MACRO_SHADOW: Mixed / cautious-neutral
```

Do not let FRED expand daily DATA PING noise.

---

### Weekly RAW

Use FRED as context for:

```text
macro pressure
real-rate pressure
credit stress
volatility stress
liquidity conditions
dollar pressure
```

Do not use it as a standalone directional forecast.

---

### Master Monday

Master Monday should include FRED in the macro calibration block.

Preferred output:

```text
MACRO_SHADOW:
Risk-on / Neutral / Risk-reduced

RATES_PRESSURE:
Up / Flat / Down

REAL_RATE_PRESSURE:
Up / Flat / Down

CREDIT_STRESS:
Low / Rising / High

VOL_STRESS:
Low / Medium / High

LIQUIDITY_PROXY:
Expanding / Mixed / Contracting

DOLLAR_PRESSURE:
Rising / Flat / Falling

FRAMEWORK_IMPACT:
Supportive / Neutral / Dampening
```

---

### Research Lab

Use FRED for:

```text
historical replay
point-in-time macro context
macro gate audit
FNP and false negative review
opportunity-cost analysis
```

But do not let Research Lab treat FRED macro as proof of crypto rotation.

---

## 9. Current crypto-state effect

This FRED run does not change the current crypto framework state.

As of the surrounding July 5 DATA PING context:

```text
Recovery-attempt: ACTIVE
Recovery-attempt quality: FRAGILE
Rotation: NO
Rebuy: LOCKED
```

FRED modifies only macro confidence context:

```text
Macro does not block recovery attempt by itself.
But rates / real rates / dollar are not clean tailwinds.
Credit / VIX / conditions are supportive.
Liquidity is mixed.
Therefore macro context is mixed, not decisive.
```

---

## 10. Operational rule going forward

```text
FRED Classic Targeted Series = production macro shadow input.
FRED Bulk = discovery only.
FRED Vintage = backtest integrity layer.
FRED Daily = compact context only.
FRED Weekly = Master Monday calibration.
FRED never equals rebuy / rotation / deployment confirmation.
```

---

## 11. Final conclusion

FRED is now a reliable macro-shadow infrastructure layer for the framework.

It improves:

```text
macro calibration
Research Lab replay
Master Monday context
backtest integrity
point-in-time control
```

It does not improve by itself:

```text
crypto execution timing
rebuy permission
rotation confirmation
altseason confirmation
portfolio action
```

Final status:

```text
FRED_MACRO_STATUS: BACKTEST_READY_FULL
Framework role: Production macro context
Decision role: Context only
```