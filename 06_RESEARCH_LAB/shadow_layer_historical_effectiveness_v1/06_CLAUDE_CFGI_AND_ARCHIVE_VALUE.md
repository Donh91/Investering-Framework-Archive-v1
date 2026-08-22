# Claude, CFGI and Historical Archive Value

## Why this material matters

A substantial part of the framework's historical research cost has already been paid. Old Claude research packages, DATA PING packets and related archived materials contain observations from sources that may be expensive, rate-limited, ephemeral or inconvenient to reacquire.

The correct policy is therefore:

> Reuse preserved point-in-time evidence before buying or reconstructing the same history again.

## What can be reused as evidence

### High-value reusable data

- CFGI GLOBAL/BTC/ETH observations with source timestamps
- ETF flow rows and settled-session references
- BTC/ETH/ETHBTC values
- BTC dominance values where provider identity is known
- breadth snapshots with universe/membership metadata
- OI/funding/taker-flow observations
- liquidation and stress observations
- stablecoin deployment/history rows where source identity is preserved
- source hashes, retrieval times and normalized payload hashes

These can support historical event reconstruction when the observation existed before the outcome.

## What cannot be treated as raw evidence

Claude or prior-model conclusions such as:

- `rotation confirmed`
- `high reliability`
- `this sensor works`
- `historically 75% failure`
- `this is the best predictor`

are research hypotheses unless accompanied by reproducible rows.

## CFGI specifically

CFGI appears in the framework from the early Tier-1 Shadow architecture and remains important as a sentiment/stress input. Later DATA PING packets preserve separate GLOBAL, BTC and ETH scores with timestamps and normalized-payload hashes, proving that high-quality point-in-time capture exists for at least part of the archive.

However, July research-design material explicitly recorded a missing complete historical CFGI archive for some replay work. Therefore:

- do not assume continuity,
- mine the existing packets first,
- create a timestamp inventory,
- only request external recovery for uncovered windows that matter to a concrete hypothesis.

## Highest-value Claude research findings to preserve

### A. Framework asymmetry / false negatives

Research Lab correctly identified that the framework measured false positives more aggressively than false negatives. This led to Cumulative FNP / opportunity-cost accounting.

Value: high governance relevance.

### B. F12.5 replay

The replay claimed earlier detection in 2020 and 2021 and highlighted BTC.D reclaim as a potentially dominant component. The exact numeric claims require independent reproduction before becoming facts, but the replay is highly valuable for hypothesis prioritization and redundancy testing.

Value: high research lead, medium evidentiary authority.

### C. ETF-era two-layer model

The split between BTC absorption and ecosystem transmission appears across multiple independent archive strands and explains observed market behavior better than the older `BTC strength -> altseason` assumption.

Value: high conceptual robustness.

### D. Stablecoin parking versus deployment

This is a major improvement over older supply-based liquidity interpretation.

Value: high, but implementation quality depends on actual deployment data.

### E. Hidden deterioration

The archive repeatedly warns that stable BTC price can mask weakening breadth, ETH/BTC and deployment.

Value: high as risk-classification hypothesis.

## Efficient recovery order

When a historical test needs a missing field:

1. Search repository-native machine rows.
2. Search DATA PING archives.
3. Search Claude / Research Lab packages.
4. Search archived Fable / OTA material.
5. Search project File Library source documents if available to the reviewing environment.
6. Only then use external historical recovery.

## Deep Research rule

External Deep Research is justified only for a bounded missing-data question, for example:

`Recover the exact historical stablecoin deployment proxy for these 12 preregistered timestamps using source-native data available at those dates.`

It is not justified as a substitute for reading the repo.

## Data preservation recommendation

Future expensive-source observations should always persist:

- source name
- exact scope
- source timestamp
- retrieval timestamp
- normalized value
- normalized payload hash
- units
- source-version identifier
- missing/stale status

That converts expensive one-time calls into durable research capital.