# Cowork Readiness Protocol

This file freezes the final pre-Cowork launch requirements for the Historical Altseason Pullback Laboratory. It changes no market rule, threshold, weight, event label, portfolio policy or analytical outcome definition.

Cowork research is authorized only after all of the following are materially true on the final bundle:

1. `RESEARCH_READINESS_MANIFEST.json` exists and `readiness_verdict == PASS`.
2. Free-stage provenance confirms `BINANCE_VISION_ARCHIVE_FIRST_TRANSPORT_v1`, archive-first true, deterministic timestamp reordering true, and analysis semantics unchanged.
3. Time-integrity audit is PASS with strict timestamp lags, no cross-window lag bridging and no positional-row-as-hour substitution.
4. Objective episode catalogue and matched continuation controls exist and are non-empty.
5. Exact-hour free event paths exist with explicit missingness.
6. CFGI billing is PASS, expected and actual usage remain within the frozen hard cap, and the minimum credit reserve is preserved.
7. CFGI exact-relative-hour paths and field-level coverage exist. No silent nearest-hour fallback or invented history is permitted.
8. The final Cowork input manifest inventories every bundled file with SHA-256.
9. Both `COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md` and `COWORK_OPUS5_RESEARCH_PROTOCOL_ADDENDUM.md` are present in the bundle and mandatory.
10. The addendum's hypothesis provenance, effective-sample-size/power, multiplicity, placebo, parameter-stability and top-candidate destruction requirements are binding.
11. Historical conclusions remain capped at `FORWARD_TEST`; no automatic production promotion is authorized.
12. If any requirement fails, bundle generation must fail closed or clearly emit a blocked/incomplete state. It must never silently downgrade the scientific contract.

## Final preflight principle

A large number of hourly observations must never be mistaken for a large number of independent events. Episode-level evidence, robustness, controls, temporal directionality and prospective support determine confidence.

## Authority

RESEARCH ONLY. No live execution. No market-state mutation. No automatic rule changes.