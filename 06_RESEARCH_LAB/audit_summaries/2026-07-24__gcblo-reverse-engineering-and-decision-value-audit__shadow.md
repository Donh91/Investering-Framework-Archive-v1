# GCBLO Reverse Engineering and Decision-Value Audit

**Dato:** 2026-07-24  
**Status:** SHADOW_ONLY  
**Område:** global liquidity / Bitcoin macro regime / sell and rebuy timing  
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/`  
**Related folders:** `04_MARKET_LEARNING/macro_shadow/`, `08_SOURCE_MATERIAL/screenshots/`, `07_PROMPTS_AND_AGENTS/claude/`  
**Depends on:** Sensor Relationship & Incremental Value Standard, Active Test Registry, source note for the GCBLO X corpus  
**Supersedes:** none  

## Research Lab verdict

```yaml
primary_verdict: SHADOW_OBSERVATION
research_action: OFFLINE_REPLICATION_AND_INCREMENTAL_VALUE_CHALLENGER
new_test: NO
new_engine: NO
current_reentry_signal: NO
current_sell_signal: NO
market_state_change: NO
gate_change: NO
rebuy_change: NO
portfolio_action: NO
```

The GCBLO concept is economically plausible as a slow macro-liquidity regime proxy. The presented screenshots do not establish that the exact oscillator, its +86 and -80 thresholds, or its halving-conditioned interpretation provide robust sell and rebuy timing.

The correct research question is not whether the chart looks historically aligned. It is whether a reproducible, real-time-vintage version adds out-of-sample decision value after the framework already knows business-cycle state, global M2, price trend, volatility, ETF flow, derivatives positioning and current decision locks.

## Frozen proposition

```text
A weekly oscillator built from changes in major central-bank balance sheets,
TGA and RRP can improve Bitcoin cycle-risk and re-entry decisions beyond
simple macro, trend and existing framework baselines.
```

This proposition has two separate decision targets:

```text
TOP-RISK TARGET:
Does it reduce future major drawdown at an acceptable missed-upside cost?

RE-ENTRY TARGET:
Does it improve future risk-adjusted return and reduce premature-entry drawdown
relative to WAIT and price-confirmed entry?
```

Top and re-entry performance must not be blended into one accuracy score.

## Likely reverse-engineered architecture

Based on the source description, the closest transparent candidate family is:

```text
x_FED(t) = Federal Reserve total assets
x_ECB(t) = ECB total assets
x_BOJ(t) = BOJ total assets
x_TGA(t) = Treasury General Account
x_RRP(t) = Overnight Reverse Repo Facility
```

For each component `i`:

```text
d_i(t) = change_k(x_i(t))
z_i(t) = [d_i(t) - rolling_mean_L(d_i)] / rolling_std_L(d_i)
```

Candidate composite:

```text
C(t) =
  w_FED * z_FED(t)
+ w_ECB * z_ECB(t)
+ w_BOJ * z_BOJ(t)
- w_TGA * z_TGA(t)
- w_RRP * z_RRP(t)
```

Candidate smoothing and bound:

```text
S(t) = EMA_E[C(t)]
GCBLO_candidate(t) = A * (2 / pi) * atan(lambda * S(t))
```

Unknown parameters:

```text
k       = difference or rate-of-change horizon
L       = z-score lookback
w_i     = component weights
E       = EMA length
lambda  = arctangent compression scale
A       = output amplitude
```

This family is a reconstruction hypothesis, not the original formula.

## Strongest supporting case

1. Central-bank operations and government cash accounts can change bank-reserve supply and money-market conditions. New York Fed documentation states that repos temporarily increase reserve balances and reverse repos temporarily reduce them. This validates the directional sign of RRP as one reserve-drain component, though not a universal risk-asset transmission rule.

2. Bitcoin and crypto flows are influenced by global financial conditions. ECB research finds that crypto momentum and volatility, plus volatility and liquidity in global financial markets, matter for Bitcoin trading. BIS research also identifies global funding conditions as important drivers of native crypto flows.

3. A slow, smoothed macro regime indicator may provide useful context for:

```text
risk-budget reduction
macro deterioration watch
post-stress recovery context
false-negative opportunity-cost review
```

4. The October 2025 observation is directionally interesting. Bitcoin did establish an all-time high near USD 126,000 on October 6, 2025, and the source's October 7 screenshot is close in time. This is a valid case for investigation, but one event is not calibration evidence.

5. The concept overlaps constructively with existing TechDev research. TechDev has repeatedly treated global liquidity as regime-dependent, with stronger relevance near business-cycle troughs, and has used an approximately 11-week lead as a timing hypothesis. That makes GCBLO suitable as a challenger against existing liquidity families rather than an isolated new doctrine.

## Strongest falsification case

### 1. Global liquidity is not one observable quantity

BIS defines global liquidity as the ease of financing in global markets and states that no single indicator provides the full picture. BIS factor research identifies at least global monetary policy, global credit supply and global credit demand as separate common drivers. IMF surveillance likewise includes price and quantity variables, bank leverage, interest rates, risk attitudes and cross-border flows.

A central-bank-balance-sheet oscillator is therefore a partial proxy, not global liquidity itself.

### 2. Mixed data frequencies create synthetic timing

Likely inputs update at different frequencies:

```text
WALCL: weekly, Wednesday level
TGA: weekly level or weekly average depending on series choice
RRP: daily
ECB assets: weekly
BOJ assets: monthly, end of period
```

Forward-filling monthly BOJ data into weekly rows produces artificial steps and stale information. Weekly aggregation of daily RRP can change results depending on last, mean, maximum or release-aligned sampling.

### 3. Currency and scale treatment are unresolved

Fed and US drains are in USD, ECB assets are in EUR, and BOJ assets are in JPY. Z-scoring each change makes dimensions comparable statistically, but it does not make the economic impulse equally important. Equal weighting can overstate a small standardized move in one jurisdiction and understate a large globally transmitted move elsewhere.

A USD-converted stock model and a component-normalized flow model are different hypotheses and must be tested separately.

### 4. PBoC omission is material

The visible construction includes Fed, ECB and BOJ but not the People's Bank of China. This is difficult to reconcile with broader global-liquidity research and with TechDev's own use of Chinese credit and CN10Y proxies. The omission may be due to data quality, but that must be explicit and tested through ablation rather than assumed harmless.

### 5. First difference plus z-score plus EMA plus arctangent is highly parameter-sensitive

Each transformation adds freedom:

```text
difference horizon
normalization window
component weights
smoothing length
bounding scale
thresholds
```

The arctangent transform is monotonic. It mainly compresses extremes and changes the visual scale. Values such as +86 and -80 have no inherent economic meaning unless fixed before outcome testing and shown to be stable under parameter perturbation.

### 6. The visible oscillator is heavily saturated

The historical line spends long periods near its upper and lower bounds. This can be useful for coarse regime classification, but it reduces timing resolution. A threshold can look precise on a chart while the underlying information was available across a wide range of weeks.

### 7. The effective historical sample is tiny

The halving-conditioned narrative has roughly three completed modern post-halving cycles before the current cycle. Claims such as 'every time' therefore rest on a very small number of independent macro episodes. Daily or weekly bars inside each cycle do not create independent cycle-level samples.

### 8. Historical-vintage and repaint risk are unresolved

Current FRED history is not the same as information available on each historical date. Revisions, publication delays, forward-filled values and TradingView data handling can move historical crossings. A credible timing test requires as-of data vintages or a frozen release-calendar reconstruction.

The October 7 post is promising evidence only if:

```text
all source values were available by that timestamp
the exact formula and settings were frozen
no later data revision moved the threshold cross
historical labels were generated mechanically
```

### 9. Visual labels may be retrospective

The charts show labels for cycle tops, exits and re-entries. Without a machine-readable signal log, it is not known whether each label existed in real time, was added later, or reflects discretionary interpretation.

### 10. The re-entry claim may confuse macro bottom with executable entry

A liquidity inflection can occur before price acceptance, during continued deleveraging or before a final price low. Macro improvement may support the medium-term expected return while still allowing substantial short-term MAE.

Therefore:

```text
GCBLO > -80 is not equivalent to executable rebuy permission.
```

## Evidence classification

```yaml
indicator_existence: PUBLICLY_CROSS_REFERENCED
conceptual_mechanics: PLAUSIBLE
exact_formula: MISSING
exact_settings: MISSING
as_of_historical_series: MISSING
threshold_calibration: MISSING
ex_ante_signal_log: MISSING
independent_cycle_sample: VERY_SMALL
october_2025_case: ANECDOTAL_BUT_RESEARCH_WORTHY
july_2026_reentry_case: UNMATURED_SOURCE_CLAIM
current_framework_weight: ZERO_INCREMENTAL_WEIGHT
```

## Current interpretation of the July 2026 reading

The reading near -78.37 should be classified as:

```text
MACRO_LIQUIDITY_REENTRY_HYPOTHESIS
NOT_EXECUTION_PERMISSION
```

Its strongest defensible meaning is:

```text
The candidate oscillator may be transitioning out of an extreme restrictive state.
This raises the priority of monitoring confirmation and the cost of remaining fully locked.
```

It does not establish:

```text
the final BTC price low
the end of the pullback event
an immediate buy window
altcoin permission
rotation confirmation
portfolio deployment authority
```

## Research architecture

No new named engine or active test is created. Research is an offline challenger under the Sensor Relationship & Incremental Value Standard and must route decision outcomes to existing owners.

### Phase 0: exact-source recovery

Acquire where possible:

- TradingView script access or author-provided Pine code;
- settings export;
- machine-readable oscillator export;
- exact series IDs;
- exact component weights;
- threshold and lookback derivation;
- dated historical signal log.

If these are unavailable, label all outputs:

```text
RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GCBLO
```

### Phase 1: faithful candidate-family reconstruction

Test a predeclared grid without using Bitcoin outcome performance to choose the formula:

```text
change horizon k: 1, 4, 13, 26 and 52 weeks
z-score lookback L: 26, 52, 104 and 156 weeks
EMA length E: 4, 8, 13, 26 and 52 weeks
weights:
  equal
  inverse-volatility
  USD-stock-share
  GDP-share
FX treatment:
  native-unit z-score
  USD conversion before change
TGA sampling:
  Wednesday level
  weekly average
RRP sampling:
  Wednesday
  weekly mean
  weekly end
```

The objective in this phase is visual and mechanical reconstruction, not BTC optimisation.

### Phase 2: no-repaint and release-lag audit

Build two data sets:

```text
CURRENT_VINTAGE:
latest revised history, descriptive only

REAL_TIME_VINTAGE:
values and publication dates available at each decision timestamp
```

Required fields:

```text
observation_date
release_timestamp
available_to_model_timestamp
source_vintage
revision_flag
forward_fill_age_days
component_staleness_days
```

A historical cross that disappears or shifts materially under real-time vintages is not timing evidence.

### Phase 3: component ablation and specification survival

Run:

```text
Fed only
Fed - TGA - RRP
Fed + ECB + BOJ
Fed + ECB + BOJ + PBoC
full central-bank USD stock
normalized component flow
GCBLO candidate without arctangent
GCBLO candidate without halving condition
```

Determine whether the supposed value comes from:

```text
one component
normalization
smoothing
the threshold
halving conditioning
or broad liquidity itself
```

### Phase 4: top-risk decision utility

Candidate event:

```text
post-halving upper-state exit
or decline through a predeclared upper threshold
```

Evaluate 4, 8, 12 and 26-week horizons.

Required metrics:

```text
future peak-to-trough drawdown
lead time to local and macro peak
false-top rate
maximum upside after warning
upside foregone by exit
maximum drawdown avoided
time out of market
re-entry delay
utility versus hold
utility versus simple price-trend exit
```

### Phase 5: re-entry decision utility

Candidate event:

```text
lower-state recovery through a predeclared threshold
```

Compare:

```text
immediate candidate entry
WAIT
price-confirmed entry
liquidity plus price confirmation
liquidity plus transmission plus price confirmation
```

Required horizons:

```text
4 weeks
12 weeks
26 weeks
52 weeks
```

Required metrics:

```text
end return
MFE
MAE
maximum drawdown
false re-entry rate
missed upside
opportunity cost
time to confirmation
time to final low
```

### Phase 6: incremental-value audit

Baselines:

```text
halving clock only
BTC 200-day trend
BTC 200-week trend
BTC drawdown from 60-day and all-time high
Fed net liquidity only
USD-converted global central-bank assets
Global M2 with frozen 11-week lead hypothesis
TechDev CN10Y / DXY / high-yield-spread family
existing framework macro state
existing framework macro plus price and flow confirmation
```

Questions:

```text
Does GCBLO improve out-of-sample probability or decision utility?
Does it merely repackage the same liquidity factor?
Does its value survive after business-cycle state is known?
Does it add value only near troughs or only after tops?
Does it improve sell and rebuy differently?
```

Mandatory methods:

```text
expanding walk-forward
leave-one-cycle-out
block bootstrap
parameter perturbation
multiple-testing family maximum
nonlinear dependency diagnostic
regime and volatility splits
matched observational units
```

### Phase 7: prospective current-cycle shadow row

Freeze the July 24, 2026 source claim as an external claim, not a framework prediction.

Track from the timestamped source:

```text
4W, 12W, 26W and 52W return
MFE and MAE
new-low occurrence
time to final low if later identifiable
price-confirmation date
transmission-confirmation date
cost of immediate entry versus confirmed entry and WAIT
```

Route matured decision-cost evidence to existing owners where eligible:

```text
T2 GATE_BTC_PARTIAL_FT_1
T4 PULLBACK_EDGE_20260708_01_OUTCOMES
T5 FNP_CUMULATIVE
```

Do not manufacture a prospective framework row retrospectively. The external source claim remains separate from a framework decision row unless a qualifying frozen framework divergence exists.

## Proposed improved model family

The useful inspiration is not another single oscillator. It is a three-stage Liquidity Transition challenger:

### Layer 1: liquidity impulse

```text
major central-bank assets
TGA
RRP
bank reserves
PBoC or China-credit proxy
FX-normalized global M2 or CB assets
```

### Layer 2: transmission

```text
DXY
real yields
high-yield spreads
repo and funding stress
stablecoin supply
ETF flows
BTC basis, funding and OI quality
```

### Layer 3: price acceptance

```text
weekly and daily trend
breakout or reclaim persistence
volatility expansion after compression
spot-flow confirmation
breadth and ETH/BTC only for separate alt permission
```

Decision logic to test:

```text
LIQUIDITY TURN ONLY:
WATCH

LIQUIDITY + TRANSMISSION:
MACRO CONFIRMATION CANDIDATE

LIQUIDITY + TRANSMISSION + PRICE ACCEPTANCE:
ELIGIBLE FOR EXISTING GOVERNANCE REVIEW
```

This preserves the potential macro lead while avoiding the claim that one slow oscillator identifies an executable bottom.

## False-positive and false-negative costs

### False positive: premature sell

```text
missed upside
premature tax realisation
unnecessary time out of market
failed re-entry discipline
```

### False negative: late sell

```text
avoidable drawdown
loss of deployable capital
higher psychological and execution stress
```

### False positive: premature re-entry

```text
large MAE
capital tied before final flush
inability to exploit later confirmation
```

### False negative: delayed re-entry

```text
missed upside
higher re-entry price
continued full lock during improving regime
```

A model is useful only if the full cost distribution improves, not merely the count of historically correct labels.

## Falsifier, promotion and kill criteria

```yaml
falsifier:
  - no out-of-sample improvement over simple macro and price baselines
  - historical threshold crossings move materially under real-time vintages
  - performance disappears after excluding one completed cycle
  - value disappears after controlling for business-cycle and price state
  - threshold result fails reasonable parameter perturbation
promotion_condition:
  - reproducible formula and data lineage
  - frozen real-time-vintage implementation
  - measurable incremental decision value
  - acceptable missed-upside and MAE trade-off
  - regime stability or explicit bounded regime condition
  - sufficient prospective rows under existing governance
kill_condition:
  - primarily a repainting or revised-data artefact
  - redundant with an existing simpler liquidity sensor
  - requires unstable threshold or lead optimisation
  - no benefit after complexity and delay cost
observation_window:
  historical: 2011_to_2026_with_leave_one_cycle_out
  prospective: current_cycle_plus_future_valid_rows
minimum_valid_rows:
  no_cycle_level_promotion_from_three_completed_cycles
baseline:
  simple_macro_plus_price_confirmation
owner:
  SENSOR_RELATIONSHIP_STANDARD_AND_EXISTING_T2_T4_T5
```

## Final bounded conclusion

```text
GCBLO deserves reproduction.
GCBLO does not yet deserve belief as a sell/rebuy oracle.

The October 2025 warning is a valuable case study.
The July 2026 re-entry call is a valuable prospective claim.
Neither changes framework action today.

The durable opportunity is to test whether a liquidity-turn feature improves
existing confirmation and opportunity-cost logic, not to replace it.
```

## Primary external references

- TradingView community listing for `Global Central Banks Liquidity Oscillator (W) (Adjustable)`
- New York Fed, Repo and Reverse Repo Agreements
- BIS, Understanding Global Liquidity
- BIS, Global Liquidity Indicators: Background and Interpretation
- IMF, Global Liquidity: Issues for Surveillance
- ECB Working Paper 2868, Global and Local Drivers of Bitcoin Trading vis-a-vis Fiat Currencies
- BIS Working Paper 1265, DeFiying Gravity? Cross-Border Bitcoin, Ether and Stablecoin Flows
- FRED series pages for WALCL, WTREGEN, RRPONTSYD, ECBASSETSW and JPNASSETS

## Framework authority boundary

```text
NEW TEST: NO
NEW ENGINE: NO
NEW SENSOR WEIGHT: NO
CURRENT REENTRY: NO
CURRENT SELL: NO
MARKET STATE CHANGE: NO
GATE CHANGE: NO
REBUY CHANGE: NO
DEPLOYMENT CHANGE: NO
PORTFOLIO ACTION: NO
```
