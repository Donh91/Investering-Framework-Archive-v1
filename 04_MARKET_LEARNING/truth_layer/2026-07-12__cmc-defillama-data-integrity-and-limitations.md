# CMC + DeFiLlama Data Integrity and Limitations

**Date:** 2026-07-12

## Integrity PASS

- CMC BTC.D ZIP readable and internally hash-valid.
- 1,287 raw/normalized BTC.D rows match.
- No interpolation, backdating or proxy insertion.
- One source gap, 2023-01-05, preserved as missing.
- DeFiLlama artifact readable.
- 12/12 raw endpoint files present and checksum-valid.
- 5,532 normalized stablecoin rows; 922 matched rows per entity.
- No TVL substitution.
- No velocity label.
- Individually supplied JSON files match the corresponding artifact copies where provided.

## Source-convention boundary

`CMC_DIRECT_SOURCE_CONVENTION` is not TradingView `CRYPTOCAP:BTC.D`. Cross-provider absolute levels must not be spliced or compared without a declared convention change.

## M1 source conflict

The M1 PDF claims 151 warning fires while the supplied row CSV contains 81. The 81-row CSV is the reproducible source used for A/C/D clustering. Exact regeneration of the PDF aggregate requires the original generator or daily signal matrix.

## Small-n and pseudo-replication

M4 has three real-labeled gate rows, but they belong to one real episode.

```text
REAL EPISODES: 1
FAKE EPISODES: 4
UNRESOLVED EPISODES: 1
```

No inferential or promotion claim is justified.

## Stablecoin semantics

- supply is liquidity availability, not deployment;
- DEX volume is activity, not capital direction;
- DEX/supply is an activity proxy, not velocity;
- six-entity coverage is broad but not the entire market;
- provider history and tracked protocols may be revised.

## Horizon semantics

The June–July 2026 M4 episode remains unresolved. No outcome is backfilled.

## Authority boundary

No market call, portfolio action, threshold promotion or rule ratification was performed.
