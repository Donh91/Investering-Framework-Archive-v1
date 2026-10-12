# Shadow Compass v2 scoring contract v3 (proposed)

Status: DRAFT / REVIEW_REQUIRED.
Contract ID: `SHADOW_COMPASS_V2_SCORING_v3`.

Retain frozen forecast and Auto Market State binding, existing 12h/72h/168h horizons, direction tolerances, baseline semantics, and research-only authority.

The shared hourly loader must use candle close `timestamp_utc + 1h` for outcome alignment. `source_window_end_utc` is a batch/collection boundary, not a candle-close or proven first-knowledge timestamp. Reject malformed clocks and unavailable future collection windows; require a completed endpoint within the existing ±1h tolerance or remain pending.

Newly matured outcomes must carry v3 and distinguish candle open, candle close, and batch end. Historical v1/v2 forecasts and outcomes remain immutable and require separately reviewed reconciliation before comparisons or claims of edge. No automatic promotion, trading action, model-weight or threshold change.

Official companion: `04_MARKET_LEARNING/handlekompas/SCORING_CONTRACT_v3.md`.
