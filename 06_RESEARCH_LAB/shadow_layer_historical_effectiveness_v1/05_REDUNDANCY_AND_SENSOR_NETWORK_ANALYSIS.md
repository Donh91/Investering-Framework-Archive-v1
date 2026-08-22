# Redundancy and Sensor Network Analysis

## Core question

Does the framework possess many independent sensors, or many transformations of a smaller number of underlying information sources?

The archive strongly suggests the latter.

## Latent information families

### Family A - relative capital rotation

Primary observables:

- ETH/BTC
- ETH relative performance
- large-cap alt relative performance

Derived / related concepts:

- EBP
- Early Rotation Pre-Trigger component
- AED
- TPS/DRS components
- F12.5 transmission logic

Risk: counting ETH/BTC rise, ETH outperformance and related TOTAL3 improvement as separate independent confirmations.

### Family B - breadth / participation

Primary observables:

- advance ratio
- breadth survival
- sector participation
- top-N alt participation

Derived / related concepts:

- BSE
- rotation breadth filter
- fake-rotation veto
- DRS
- HDS
- rotation readiness composites

Risk: breadth, TOTAL3 and large-cap participation may be partially dependent views of the same capital broadening process.

### Family C - dominance / concentration

Primary observable:

- BTC dominance path

Derived / related concepts:

- dominance filter
- F12/F12.5 reclaim logic
- fake-rotation filter
- rotation readiness
- hidden deterioration context

Risk: BTC.D level and BTC.D trend/reclaim should not be scored as independent if one is a deterministic transformation of the other.

### Family D - liquidity availability versus deployment

Primary observables:

- stablecoin supply
- SSR
- stablecoin exchange behavior
- DEX/L2/TVL deployment

Derived / related concepts:

- SDE
- DVX
- stablecoin parking/deployment
- Early Rotation Pre-Trigger liquidity component
- DRS

Risk: stablecoin supply, SSR and deployment are not equivalent, but some composites may mix availability and actual usage without enough separation.

### Family E - ETF / institutional absorption

Primary observables:

- BTC/ETH ETF flows
- flow persistence
- issuer concentration

Derived / related concepts:

- EAQ
- AQS
- hidden deterioration
- flow-supported pullback classifier
- BTC-survival divergence classifier

Risk: raw ETF flow and EAQ/AQS may double-count the same flow series unless quality features add measurable incremental information.

### Family F - leverage / volatility structure

Primary observables:

- OI
- funding
- basis
- taker flow
- liquidation volume/clusters
- options gamma/VRP/skew

Derived / related concepts:

- Stress/Flush
- SEI
- leverage fragility
- suppression persistence
- reclaim quality context

Risk: several stress scores may be transformations of the same deleveraging episode.

## High-priority redundancy hypotheses

### H1 - TPS / DRS over-complexity

Historical F12.5 replay material reported that most discrimination appeared to come from BTC.D reclaim, ETH/BTC persistence and breadth survival. This suggests a direct test:

`SIMPLE_3 = BTCD_PATH + ETHBTC_PERSISTENCE + BREADTH_SURVIVAL`

versus

`FULL_ROTATION_SHADOW = all available rotation meta-scores`

If SIMPLE_3 is within a small tolerance of the full stack on false-positive rate, lead-time and missed-opportunity rate, the larger score family should be treated as summarization rather than independent edge.

### H2 - HDS and SPTD overlap

Both describe deterioration hidden beneath stable price. Unless they use independent inputs or materially different lead/lag behavior, they may be the same concept under different names.

### H3 - AQS and EAQ overlap

AQS appears to summarize ETF absorption quality. Test whether the score adds information beyond its raw components: flow persistence, concentration and price absorption.

### H4 - SEI merges multiple already-correlated derivatives signals

Gamma, basis, book thinness and SIM-like reliability inputs may improve robustness, but could also create false confidence through correlated microstructure states.

## Sequence analysis

The archive repeatedly favors sequence over isolated indicators. The most important network structures to test are:

### Rotation sequence

`macro/liquidity improvement -> ETHBTC persistence -> BTC.D deceleration/reclaim behavior -> breadth survival -> broad alt expansion`

Question: which transition adds the most information, and which step merely confirms what is already known?

### Fake rotation sequence

`ETHBTC/large-cap improvement -> weak or failed breadth -> BTC.D remains/reclaims high -> alt deterioration`

Question: is breadth failure the dominant veto, or does BTC.D reclaim materially improve precision?

### ETF-era hidden deterioration sequence

`BTC stable/strong + ETF support -> ETHBTC weakens -> breadth decays -> stablecoin parking / weak deployment -> alt underperformance -> later BTC reaction or continued BTC-only absorption`

Question: how early can portfolio-health deterioration be identified without mistaking healthy BTC concentration for imminent BTC failure?

### Stress / flush sequence

`price stress -> CFGI/fear -> ETF pressure -> liquidation clearance -> OI/funding reset -> reclaim quality -> F1/F2 outcome`

Question: which components improve exhaustion timing and which are merely descriptions after the move?

## Recommended tournament

For every sufficiently covered historical event, compare:

1. single-family baselines
2. best two-family combinations
3. best three-family combinations
4. full shadow composite
5. current-stack state where available

Metrics:

- false-positive rate
- missed-opportunity / false-negative rate
- median lead-time
- regime-conditioned precision
- calibration
- complexity penalty
- source-quality penalty

The winner should not be the most complex model. It should be the simplest model whose incremental information survives negative controls.