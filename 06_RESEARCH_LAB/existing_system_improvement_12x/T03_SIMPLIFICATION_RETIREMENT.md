# T03 - Experiment / Sensor Simplification and Retirement Review

**State:** FINDING_FROZEN
**Existing owners:** Experiment Lifecycle; Sensor Relationship / Incremental Value Standard

## Current evidence

Current Experiment Registry contains 153 candidates, including 79 `INCUBATING` and 32 `MATURED_INCONCLUSIVE`.

The registry shows repeated forecast families whose titles differ mainly by source-path namespace aliases, for example variants of BTC or ETH mark-price paths such as:

- `market_metrics.derivatives...`
- `latest_capture.market_metrics.derivatives...`
- `market.derivatives...`
- `latest_capture.derivatives...`

Multiple candidates can therefore represent substantially the same target/direction while retaining separate lifecycle identities. This is historically understandable because path contracts evolved, but it increases context volume and risks treating namespace duplication as hypothesis diversity.

The lifecycle also sets `automatic_age_expiry: false`; retirement therefore requires explicit evidence-based review rather than automatic deletion.

## Frozen finding

`EXPERIMENT_SEMANTIC_DUPLICATION_AND_INCONCLUSIVE_COMPRESSION_REVIEW_MISSING`

The problem is not that 153 candidates are automatically too many. The problem is that the existing operational surface does not provide a deterministic simplification view answering:

- which candidates are semantic/path aliases of one another;
- which matured-inconclusive candidates share the same underlying family;
- which incubating candidates have many observations but no valid forecast/outcome path;
- which candidates are waiting for an already-known mapping/data dependency;
- which supported/not-supported candidates supersede weaker variants;
- which candidates have no plausible decision-consumer path even if they mature.

## Required improvement

Create a read-only simplification review that clusters existing candidates using existing canonical path normalization and lifecycle metadata. It may recommend only:

`KEEP / MERGE_REVIEW / RETIRE_REVIEW / WAIT_FOR_DATA / WAIT_FOR_MAPPING / NEEDS_MORE_OUTCOMES`.

It must not automatically retire, merge, promote, change a weight or suppress future evidence production.

### Minimum clustering dimensions

- normalized target metric path;
- target direction and horizon;
- candidate kind;
- normalized component paths for sensor combinations;
- lifecycle state;
- matured outcome count;
- observation count;
- known producer/namespace provenance.

### Strong flags

- multiple active candidate IDs collapsing to the same normalized target/direction/horizon family;
- `MATURED_INCONCLUSIVE` families with repeated aliases and no incremental decision distinction;
- high-observation `INCUBATING` candidates with zero frozen forecasts/outcomes;
- dead mapping/data dependencies that already have a newer equivalent owner.

## Acceptance

Positive: report is deterministic and every cluster links back to exact candidate IDs.

Negative: no candidate file or historical row is deleted/rewritten; no automatic retirement, promotion or weight change; distinct hypotheses sharing one metric must not be collapsed merely because their path is equal.

## Review gate

Only framework governance may ratify a `MERGE_REVIEW` or `RETIRE_REVIEW`. The tool is evidence compression, not an authority layer.
