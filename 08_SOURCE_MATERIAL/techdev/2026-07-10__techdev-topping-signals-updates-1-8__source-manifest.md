# TechDev Topping Signals Updates #1–#8 — Source Manifest

**Import date:** 2026-07-10  
**Status:** SOURCE_MANIFEST / PARTIAL_SEQUENCE_MISSING_5  
**Scope:** Historical 2024 TechDev topping-signal snapshots  
**Related extraction:** `06_RESEARCH_LAB/forward_tests/2026-07-10__techdev-topping-signals-updates-1-8__historical-extraction-v0-1.md`

## Source rule

- These files are historical evidence, not current operational doctrine.
- One uploaded PDF anchors each available update.
- Update #5 is missing and must not be reconstructed from surrounding updates.
- No performance scoring is performed in this import.
- Mechanical readings and TechDev's discretionary interpretation must remain separate.

## Imported updates

| Update | Date | Selected uploaded artifact | SHA-256 | Import status |
|---:|---|---|---|---|
| #1 | 2024-01-22 | `TechDev Newsletter - Topping Signals Update #1.pdf` | `941336816d2e9d65d1418f97fc62157c1dc7e17c2d87f7f83b81014b34d856f0` | SOURCE_BACKED_IMPORTED |
| #2 | 2024-02-04 | `TechDev Newsletter - Topping Signals Update #2.pdf` | `6f00694dc40bcc662b6dec2617d7bb176eca0ee79fa5429d1cf2ab14e84fbdf4` | SOURCE_BACKED_IMPORTED |
| #3 | 2024-02-19 | `TechDev Newsletter - Topping Signals Update #3.pdf` | `1202064addf9119ad7d897ef2e6ba1665e2e2a0772927c3f40efe5c8dc6a35b6` | SOURCE_BACKED_IMPORTED |
| #4 | 2024-03-03 | `TechDev Newsletter - Topping Signals Update #4.pdf` | `46dba29a9b562b8163132000ce84ca711a9c1f2d9adf32d4dfd531db8befab40` | SOURCE_BACKED_IMPORTED |
| #5 | DATA_MISSING | DATA_MISSING | DATA_MISSING | SOURCE_MISSING |
| #6 | 2024-03-31 | `TechDev Newsletter - Topping Signals Update #6.pdf` | `fe03c5317d9b1ccb1f05979f7981ff2c83afc7a33bf46449c1f290b8d496c6a9` | SOURCE_BACKED_IMPORTED |
| #7 | 2024-04-14 | `TechDev Newsletter - Topping Signals Update #7.pdf` | `d8cd8c288e7c788e8be18f421e01057d6cd8f97b0c98671aa63097baf8338e58` | SOURCE_BACKED_IMPORTED |
| #8 | 2024-05-20 | `TechDev Newsletter - Topping Signals Update #8.pdf` | `66bf769d0a46c3e45c371e15f43c81976c0ece7da6eb4ffce2b6281a3ebbb669` | SOURCE_BACKED_IMPORTED |

## Coverage

```yaml
updates_expected: 8
updates_imported: 7
updates_missing: [5]
historical_snapshot_rows: 7
signals_per_snapshot: 4
scoring_performed: NO
current_operational_authority: NONE
```

## Indicator-origin sources referenced by TechDev but not imported

```yaml
TOP_GAUGE_DEFINITION:
  referenced_source: Market Update Issue #35 Part 2
  status: SOURCE_MISSING

TETHER_DOMINANCE_RSI_BB_WIDTH_PI_CROSS_DEFINITIONS:
  referenced_source: Market Update Issue #26 Part 1
  status: SOURCE_MISSING

INTERMEDIATE_MARKET_CONTEXT:
  referenced_source: Market Update Issue #42
  date: 2024-03-23
  title: Parabolic Market Leg May Be Around the Corner
  status: SOURCE_MISSING
```

These source gaps should remain explicit before any historical performance or trigger-quality scoring.
