# Cycle Navigator internal precision ledgers

- `CN_INTERNAL_PARAMETER_LEDGER.jsonl`: append-only matured parameter outcomes, one row per frozen claim/parameter.
- `CN_INTERNAL_PRECISION_LEDGER.jsonl`: compact weekly summary rows.

Rules are defined by `../protocols/2026-09-14__internal-precision-accountability-contract-v1.md`.

These ledgers are internal accountability/calibration surfaces only and do not grant market, portfolio, threshold, model-weight, or promotion authority.
