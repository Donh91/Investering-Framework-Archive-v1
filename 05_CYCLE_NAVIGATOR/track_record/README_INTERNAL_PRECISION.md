# Cycle Navigator internal precision ledgers

- `CN_INTERNAL_PARAMETER_LEDGER.jsonl`: append-only matured parameter outcomes, one row per frozen claim/parameter.
- `CN_INTERNAL_PRECISION_LEDGER.jsonl`: compact weekly summary rows.

Rules are defined by `../protocols/2026-09-14__internal-precision-accountability-contract-v1.md`.

These ledgers are internal accountability/calibration surfaces only and do not grant market, portfolio, threshold, model-weight, or promotion authority.

## Precision Learning Supervisor

Settled weekly rows are consumed by `05_CYCLE_NAVIGATOR/internal_learning/STATE.json` through the internal-only Precision Learning Supervisor. It monitors family weakness every settlement and performs a deeper review after each four new successful settlements. Internal learning is additive-only and cannot alter the established public SITE/X precision surface.
