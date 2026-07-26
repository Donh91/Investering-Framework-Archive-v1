# US Spot Crypto ETF Flow History — Backtest Pack

**Package:** `US_SPOT_CRYPTO_ETF_FLOW_HISTORY_20260726`  
**Coverage:** BTC 2024-01-11 to 2026-07-24; ETH 2024-07-23 to 2026-07-24  
**Units:** USD millions  
**Status:** STRUCTURE_VALIDATED / A2_EVIDENCE_CANDIDATE  
**Market or portfolio authority:** NONE

## Purpose

Archive the supplied BTC and ETH spot ETF-flow history as full fund-level daily rows and make it directly usable for historical replay and backtest feature construction.

## Contents

- `data/` — fund-level daily rows partitioned by asset and calendar year.
- `scripts/build_etf_flow_features.py` — deterministic long-table, joined-total and trailing-feature builder.
- `scripts/validate_etf_flow_history.py` — fail-closed structural validator.
- `manifest.json` — row counts, coverage, source hashes and timing boundaries.
- `CHECKSUMS.sha256` — committed-file integrity list.

## Validated coverage

| Asset | Sessions | First date | Last date | Duplicate dates | Null cells | Daily row-total failures |
|---|---:|---|---|---:|---:|---:|
| BTC | 651 | 2024-01-11 | 2026-07-24 | 0 | 0 | 0 |
| ETH | 513 | 2024-07-23 | 2026-07-24 | 0 | 0 | 0 |

Each daily `Total` reconciles to the displayed fund columns at one-decimal precision.

## Build and validate

```bash
python scripts/validate_etf_flow_history.py
python scripts/build_etf_flow_features.py
```

Generated outputs are written to `generated/` and are intentionally reproducible rather than authoritative source files.

## Lookahead guard

The source exports contain session dates but no per-row publication timestamps.

Canonical use:

```text
ETF flow dated t is assumed known only after the US session close on t.
```

Same-session trading attribution is prohibited unless publication-time evidence is later added. The default predictive label begins with the next available trading session.

## Backtest use

This pack supports:

- 1, 3, 5, 10 and 20-session flow persistence,
- outflow deterioration versus subsequent downside,
- inflow persistence versus BTC survival,
- BTC versus ETH ETF-flow divergence,
- issuer concentration and fund-level breadth,
- reversal after cumulative inflow or outflow sequences,
- joins to price, ETH/BTC, BTC.D, breadth, derivatives, macro and Forecast Ledger outcomes.

This unlocks the ETF-flow leg. It does not by itself prove a complete multi-sensor framework backtest.
