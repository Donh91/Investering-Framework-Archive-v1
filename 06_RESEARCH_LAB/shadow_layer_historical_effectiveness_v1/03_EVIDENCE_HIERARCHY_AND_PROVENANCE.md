# Evidence Hierarchy and Provenance Audit

## Why this file exists

The archive contains both data and interpretation. Historical validation fails if those are mixed.

A statement such as `CFGI BTC = 59 at timestamp T` is a data observation if source identity and timestamp are preserved. A statement such as `CFGI confirms rotation` is an interpretation and must be evaluated separately.

## Evidence classes

### Class A - repository-native contemporaneous machine evidence

Examples:

- DATA PING machine summaries with source timestamps and normalized values
- current breadth forward snapshots
- ETF settled rows with source hashes
- entry-signal events/outcomes
- settled ETH/BTC observations
- current OI/funding/taker-flow capture

Use: eligible for direct historical measurement when identity is stable.

### Class B - repository-native immutable research / forward rows

Examples:

- frozen forward-test rows
- historical research-lab artifacts with explicit preregistration or frozen timestamps
- F12/F12.5 replay artifacts where definition and event dates are preserved

Use: evidence, but leakage and retrospective-definition risk must be checked.

### Class C - archived DATA PING / Claude / research packages with point-in-time data

Examples:

- historical CFGI values captured in packets
- ETF flow observations
- BTC dominance and ETH/BTC values
- stress/flush observations containing liquidation, OI/funding and flow context

Use: valuable evidence cache. Extract data separately from commentary.

### Class D - retrospective replay / synthesis

Examples:

- historical replay summaries stating that F12.5 was earlier in 2020/2021
- cycle lead-time tables
- old sensor hit-rate syntheses

Use: hypothesis-supporting evidence, not final edge proof.

### Class E - narrative claim

Examples:

- `100% success rate in observed cycles`
- `55-75% fake rotation failure rate`
- `75-85% microcap failure rate`

Use: research lead only unless event rows and definitions are recoverable.

## High-value evidence already preserved

### CFGI

The project has current machine packets that preserve separate GLOBAL, BTC and ETH CFGI values with timestamps and payload hashes. Older architecture documents also show that CFGI BTC/ETH was intentionally collected as Tier-1 / sentiment context. This makes historical CFGI data worth mining from archived DATA PING and Claude packets before purchasing or reacquiring external history.

Important limitation: several July test-design artifacts explicitly noted that a complete historical CFGI archive was not frozen at that time. Therefore availability is episodic, not assumed continuous.

### ETF flows

ETF evidence is stronger than many other shadow inputs because settled Farside-style data was repeatedly captured and later became a dedicated owner surface. ETF-flow level is therefore usable as an input, but the research conclusion is that flow *quality, persistence and transmission* matter more than a positive daily print.

### Breadth

Current breadth-forward material is timestamped and membership-aware. Earlier breadth concepts varied and sometimes used broad proxies. Historical cross-period comparison must preserve source/version boundaries.

### ETH/BTC

Direct and derived ETH/BTC appear frequently in DATA PING. Current data distinguishes direct pair observations and settled persistence. Older documents used very different heuristic thresholds, so historical values can be reused but old threshold semantics must not be silently imported.

### BTC dominance

BTC.D is highly important but provenance is more fragile than the concept suggests. Different denominators and providers can materially change levels. Historical analysis should prefer path features such as reclaim, lower-high, acceleration and persistence after the source convention is fixed.

### Derivatives and liquidation

Current capture of OI/funding/taker-flow is strong. Historical continuity is weaker. Stress/flush episodes provide useful event-level evidence, but broad hit-rate claims are not yet justified.

## Provenance findings by major historical claim

| Claim | Provenance verdict | Treatment |
|---|---|---|
| Shadow v1-v8 hit-rate table | explicitly described as synthesis, not statistical backtest | hypothesis only |
| Early Rotation Pre-Trigger very high historical success | low n + survivorship caveat + incomplete event-state provenance | do not quote as edge |
| Fake Rotation Type 3 55-75% failure | independent recovery did not reproduce | reject as established fact |
| Microcap 75-85% failure after pumps | narrative historical claim without recovered event table | unverified |
| F12.5 earlier by ~5 weeks 2020 and ~4-5 weeks 2021 | structured retrospective replay, Tier-1 caveats remain | supportive, not final proof |
| BTC.D 10-day reclaim strongest F12.5 component | retrospective component attribution | high-value redundancy hypothesis |
| Entry Signal Ledger positive 24h event | repository-native forward outcome | valid observation, n=1 matured 24h |
| Stress/Flush June sequence | contemporaneous DATA PING interpretation with multiple observed inputs | valid case study, not population estimate |

## Leakage red-team rules

Any future extraction from this archive must check:

- definition date versus outcome date
- whether a threshold was chosen after the episode
- whether a famous historical date was implicitly used to define the window
- whether later ETF-era terminology was projected backward
- whether a source changed provider or denominator
- whether a missing value was replaced by a proxy after outcomes were visible
- whether a composite contains multiple transformations of the same underlying variable
- whether the outcome horizon was selected because it looked favorable

## Scientific consequence

The archive is rich enough to support a serious information-value review, but not rich enough to treat every named sensor as historically scored. The correct unit of confidence is often the **information family**, not the sensor label.