# OTA24 QA incident: lineage and settlement wording

## Findings

1. Raw-row hashes were newly supplied for all three H7 row-5 instruments.
2. `response_sha256` remains absent.
3. Retrieval time is non-exact (`17:29:01.6xxZ`).
4. Matching closes do not prove byte-identical full rows against the original retrieval.
5. The phrase “rejected on close twice” overstates the evidence because the 2026-07-27 session was still in progress.
6. The 2026-07-26 high was exactly 0.03000, a touch rather than an intraday print above the threshold.

## Corrective labels

```yaml
H7_row5_lineage: PARTIAL_LINEAGE_PASS
2026_07_26: INTRADAY_TOUCH_SETTLED_CLOSE_BELOW
2026_07_27: INTRADAY_BREAK_IN_PROGRESS_CURRENTLY_BELOW
canonical_harm: NONE
```

This is a terminology and audit-completeness correction. It does not change the existing experiment score or framework state.