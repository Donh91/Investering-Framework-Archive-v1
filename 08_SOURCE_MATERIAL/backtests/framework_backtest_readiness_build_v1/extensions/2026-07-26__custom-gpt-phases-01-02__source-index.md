# BACKTEST BUILD source index — Custom GPT phases 01 and 02

**Collection status:** `ACTIVE`  
**Test execution:** `LOCKED`

## Supplied artifacts

| Uploaded artifact | Bytes | SHA-256 | Role |
|---|---:|---|---|
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T214318Z(1).zip` | 541,080 | `4f5ff5e52574106bf158bab3bb24ff70af00355051233edbf7a3e08e5cdba852` | intermediate cumulative package |
| `DATA_PING_BACKTEST_HISTORY_PACK_20260726T220615Z.zip` | 1,143,790 | `82bd9761d31125e73404109a0f1af5f443c1e219f513da724d3787e84bc2e2a6` | latest cumulative package candidate |

The latest package contains the 21:43 package as an embedded predecessor with exact hash parity. It also contains the previously supplied 20:56 and extraction-parts packages.

## Materialization policy during active collection

Successive packages are cumulative and include predecessor ZIPs. To avoid repository bloat and repeated byte storage while more packages are explicitly expected:

```yaml
hash_and_lineage_archive: ACTIVE
logical_audit_archive: ACTIVE
intermediate_raw_zip_materialization: DEFERRED
latest_final_cumulative_zip_materialization: REQUIRED_AT_COLLECTION_BATCH_CLOSE
```

No source identity is lost: package names, byte counts, SHA-256 values, embedded-predecessor relationships and independent validation results are preserved here and in the extension audit.

## Accepted evidence

- Phase 01 direct OKX swap daily rows: 2025-06-22 through 2026-04-17.
- Phase 02 direct OKX swap daily rows: 2024-08-26 through 2025-06-21.
- Combined direct daily BTC and ETH swap coverage is continuous from 2024-08-26 through 2026-04-17.
- ETH/BTC rows are a separate derived series and have no direct-pair gate authority.

## Authority boundary

These sources expand the readiness archive only. They do not authorize tests, market interpretation, portfolio action, forecast scoring, rule promotion or canonical-state changes.
