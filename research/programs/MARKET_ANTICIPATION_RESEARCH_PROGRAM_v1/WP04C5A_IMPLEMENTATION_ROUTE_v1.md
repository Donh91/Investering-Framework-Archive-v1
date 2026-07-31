# MAR-WP04C5A implementation route

## Decision

Reuse the existing Data Terminal Phase 1 collector, contracts, receipts, replay gate and artifact workflow as the macro foundation. Do not create a second FRED pipeline.

## Sequence

1. Extend the FRED collector from DGS10 to DGS2, DGS10, DTWEXBGS and VIXCLS while preserving missing-as-UNKNOWN, payload hashes and append-only receipts.
2. Add per-series raw and normalized objects plus raw-to-normalized parity receipts.
3. Run fixture mode, then explicit manual live mode, then download and verify artifact readback.
4. Build separate owner-specific Binance spot and Binance USD-M collectors; do not silently aggregate venues.
5. Build point-in-time Top-100 constituent capture with membership hash, exclusions and ranking method version.
6. Keep all collectors shadow-only until two independent successful artifact readbacks and schema/parity gates pass.

No schedule is activated in C5A. No outcome fields are accessible.
