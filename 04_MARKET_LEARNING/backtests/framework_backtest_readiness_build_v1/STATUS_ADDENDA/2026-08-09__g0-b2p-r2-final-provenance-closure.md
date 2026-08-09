# G0-B2P-R2 final provenance closure

```yaml
experiment_identity: G0-B2-AMENDED-FULL-REDUCED-v1
terminal_verdict: ROTATION_PROVENANCE_UNRECOVERABLE_CLOSE_B2
experiment_status: CLOSED_NON_TESTABLE_PROVENANCE_UNRECOVERABLE
b2_analysis_authorized: false
r3_authorized: false
passive_evidence_class: NON_B2_EVIDENCE
passive_evidence_purpose: HEALTH_ONLY
```

## Bounded provenance finding

R2 completed the final allowed provenance-recovery attempt for the frozen B2 identity.

The contemporaneous Wave 1.2 creation chain proves that `SensorDefinition` contained a `decision_uses` member in code, but the real 32-sensor `SENSOR_ROLE_DEPENDENCY_REGISTRY_v1.json` serialization did not preserve `decision_uses` or `direct_required`. The retained registry therefore cannot prove the exact real-sensor-to-`RotationEvidence` producer mapping.

The Wave 1.2 unit fixture contains a generic toy `BREADTH -> BROAD_ROTATION` dependency. It is not the real 32-sensor registry and is not authoritative provenance for `BREADTH_ABOVE_MA50`.

The exact result package `BACKTEST_WAVE1_2_CONSOLIDATION_20260728.zip` with expected SHA-256 `91a263d93dcee8353c75cba08bd74309e202c74310c34bbab7003015310b32c2` and exact source package `DATA_PING_BACKTEST_HISTORY_PACK_20260727T052808Z.zip` with expected SHA-256 `303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f` were not recovered byte-for-byte from the bounded repositories, retained Actions artifacts, or available file-library search. Wave 1.2 receipts preserve their names/hashes, not their bytes.

Supporting July design/replay material is non-authoritative for this provenance question: proxy bindings were explicitly proposals with nothing selected, and degraded rotation runs marked BTC.D, breadth and deployment as missing. Later narrative cannot repair contemporaneous producer lineage.

## Scientific consequence

At least one load-bearing field remains provenance-unproven and could depend on the Full-only `BREADTH_ABOVE_MA50` sensor. Therefore neither identifying nor non-identifying structural status can be proved for Rotation under the current frozen identity.

The current B2 identity is closed as scientifically non-testable. It must not wait 12-26 weeks for a test that cannot become scientifically valid, and no R3 may be created to rescue it. Any future Full-vs-Reduced research requires a new experiment identity with newly preregistered policy/evaluator provenance.

## Implementation boundary

Only the operational readiness surface is closed. `materialize_blind_dual_run.py` preserves engineering counters but overlays every generated `COVERAGE_LATEST.json` with:

- `b2_coverage_ready = false`;
- `experiment_status = CLOSED_NON_TESTABLE_PROVENANCE_UNRECOVERABLE`;
- `evidence_class = NON_B2_EVIDENCE`;
- `evidence_purpose = HEALTH_ONLY`;
- `b2_analysis_authorized = false`;
- `r3_authorized = false`.

No market rule, threshold, weight, sensor authority, RotationEvidence semantics, REBUY/TRIM evaluator, policy semantics, or queue ordering is changed.

## Explicit non-actions

- Gate 0-B2 was not run.
- No Full-vs-Reduced agreement or divergence was calculated.
- No economic outcome was opened.
- No Deep Research was used.
- No new CFGI credits were used.
- No paid OpenAI API call was made.
- No sensor-to-policy mapping was invented.
