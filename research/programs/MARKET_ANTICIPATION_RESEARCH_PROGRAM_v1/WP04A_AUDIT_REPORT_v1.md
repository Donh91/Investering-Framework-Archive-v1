# MAR-WP04A — Owner-Source Candidate Enumeration and Lineage Audit

## Decision

`COMPLETE_FAIL_CLOSED_PARTIAL_ENUMERATION`

WP04A audited all three preregistered WP04 stress chains without reading post-event outcomes. One chain is mechanically enumerable from a rule frozen before this phase; two are blocked because WP04 froze concepts and sensors but not candidate-trigger logic.

## Material finding

The absence of a trigger contract is not treated as zero historical events. Counts for the macro and leverage chains remain `null`, meaning **not legally enumerable under the research contract**. This prevents silent threshold selection after viewing source history.

## Enumerated candidate

One independent rotation-failure cluster is carried forward from WP03:

- event: `MAR_LSP_ROTFAIL_ETHBTC_0300_20260728T150000Z_C01`
- trigger: settled ETH/BTC close at 0.03004
- persistence observation: next settled close 0.03007
- rejection close: 0.02985
- label: `FAILED_PERSISTENCE`
- lineage: `OWNER_PARTIAL`
- missing exact preregistered pre-event checkpoints: -72h, -24h, -4h
- eight later rows remain follow-ups in the same overlap cluster

No post-event return, hit, drawdown, lead-lag statistic or economic label was created.

## Source-family decisions

### Macro

FRED-style owner series are potentially suitable, but a macro event requires a frozen definition of tightening, rate/USD stress, cadence, publication-vintage availability, conjunction order and maximum propagation lag. Until then the chain is `BLOCKED`, not negative.

### Derivatives

Funding, open-interest and taker-flow snapshots exist as source families, but no frozen stress threshold, OI transition rule, spot-displacement rule or propagation lag exists. Enumeration is `BLOCKED` to prevent researcher degrees of freedom.

### Spot and ETH/BTC

The preexisting 0.0300 acceptance/failure rule permits one candidate cluster. Exact checkpoint incompleteness prevents upgrade beyond `OWNER_PARTIAL`.

### Breadth

The prior event lacks a retained point-in-time constituent sidecar and membership hash. That historical breadth join is retroactively irrecoverable. Breadth becomes usable only prospectively after the first replayable sidecar is retained.

## Required next control

Before macro or leverage history is inspected, create and hash a prospective trigger addendum specifying:

1. cadence and settled-row ownership;
2. thresholds or categorical transitions;
3. persistence requirements;
4. conjunction order;
5. maximum propagation lag;
6. publication/retrieval availability handling;
7. overlap-cluster reset logic;
8. null and censoring behavior.

## Governance

Final holdout remains sealed. No economic ranking, parameter search, model-weight change, framework promotion or portfolio effect is permitted by this artifact.
