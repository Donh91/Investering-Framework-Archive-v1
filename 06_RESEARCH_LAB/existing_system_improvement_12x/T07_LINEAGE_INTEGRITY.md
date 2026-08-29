# T07 - Forecast-to-Outcome Lineage Integrity

**State:** FINDING_FROZEN
**Existing owner:** T10 `ARCHIVE_LINEAGE_INTEGRITY`

## Current evidence

T10 already defines the required chain:

`forecast_id -> source_master_monday -> ratification_receipt -> CN_handoff -> verified_actual -> score_row`.

The canonical Open Questions Register still carries `OQ-W28-LINEAGE` as `OPEN_CRITICAL` because the ratified W28 Master Monday source is not accessible. Governance explicitly says to locate the real source or create an explicit source-backed ratification receipt; until then W28 remains unscored.

## Frozen finding

`FORWARD_LINEAGE_COMPLETENESS_OBSERVABILITY_NEEDS_HARDENING`

The W28 historical hole is not authorization to reconstruct or guess lineage. The improvement target is forward prevention and visibility.

## Required improvement

Materialize a deterministic read-only T10 lineage completeness report over official eligible forecasts that records, per forecast:

- exact forecast path/hash;
- frozen source package/path/hash;
- ratification receipt/path/hash;
- CN/public handoff where applicable;
- verified actual/outcome path/hash;
- score/calibration path/hash where score semantics exist;
- current completeness state;
- exact missing link(s);
- whether the row is therefore score-eligible, unscored, pending or censored.

W28 must remain explicitly `UNSCORED_LINEAGE_GAP` unless the genuine ratified source is independently recovered. No substitute document, similarity match or later narrative may close it.

## Acceptance

Positive: every current official scored row has a mechanically traversable chain or is flagged with the exact missing edge; report totals reconcile to official score/outcome owners.

Negative: no historical source is fabricated, no mutable latest pointer substitutes for a frozen source, and a missing lineage edge can never be hidden by an available outcome.

## Completion target

Forward official scored rows: 100% complete lineage. Historical irreparable rows may remain explicitly excluded without blocking honest forward calibration.
