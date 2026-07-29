# Backtest Master Recovery Report v1

**Dato:** 2026-07-29  
**Status:** `RECOVERED_BASE_BINARY_PLUS_APPEND_ONLY_DELTAS`  
**Program:** `GLOBAL_LIQUIDITY_CAUSAL_CHAIN_RESEARCH_v1`  
**Issue:** #206  
**Authority:** engineering and source recovery only

## Executive result

The ten files uploaded from the prior backtest thread materially resolve the practical master-build gap, but they do not contain the exact previously referenced final binary:

```text
DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip
```

Therefore:

```yaml
G01_UPLOAD_SET_RECONCILED: PARTIAL_RECOVERED_CHAIN_EXACT_FINAL_MISSING
G02_FINAL_MASTER_BYTE_INTEGRITY: BLOCKED
G20_READY_FOR_CONTROLLED_BACKTEST_EXECUTION: NO
```

The upload set does contain a complete earlier Backtest History build plus a documented continuation chain.

## Recovered base

```text
DATA PING BACKTEST HISTORY PACK 20260727T052808Z(1).zip
```

Verified identity:

```yaml
sha256: 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
outer_bytes: 190546648
zip_members: 183
uncompressed_bytes: 209385211
crc_integrity: PASS
internal_checksum_entries: 180
internal_checksum_failures: 0
```

This is not a small phase delta. It contains:

- reconstruction and normalization code;
- validation and test scripts;
- source inventory, coverage, receipts and error evidence;
- raw, normalized and feature data;
- a master daily panel;
- preliminary backtest outputs;
- explicit lookahead and method-break documentation.

### Master daily panel

```yaml
path: features/master/master_daily_panel.csv.gz
rows: 5852
columns: 75
start_date: 2010-07-18
end_date: 2026-07-25
```

The panel includes BTC, ETH, ETH/BTC, ETF-flow features, ETH/BTC gate features, ATR and volatility fields, drawdown, funding, open interest, basis, breadth, dominance, sentiment and reconstructed business-cycle fields.

The base README reports:

- 45 public endpoints probed;
- price data from eight venues;
- 777,567 survivorship-aware universe rows across 623 USDT pairs, including 193 delisted pairs;
- BTC and ETH derivatives history from multiple venues;
- 651 BTC ETF sessions and 513 ETH ETF sessions;
- 1,405,137 CoinMetrics community rows across 838 assets;
- 60 Yahoo macro tickers and 41 OECD series;
- explicit FRED blockage at that phase.

These are package claims preserved for subsequent row-level audit, not automatically promoted owner facts.

## Continuation chain

The other DATA PING packages are preserved as append-only phase packages. The latest compact continuation is:

```text
DATA_PING_BACKTEST_HISTORY_PACK_20260727T114012Z(1).zip
```

Verified identity:

```yaml
sha256: 26df6c5bba68b503ec1744b2ca03b8beecb37ce14abc8f3ced636017b2910521
outer_bytes: 930818
zip_members: 258
uncompressed_bytes: 4103852
crc_integrity: PASS
internal_checksum_entries: 257
internal_checksum_failures: 0
```

It contains later OKX and FRED continuation artifacts, including available annual and monthly aggregates for rates, credit and liquidity series. Those FRED artifacts are latest-vintage aggregate data, not a substitute for ALFRED or archived point-in-time releases.

## TDBC package

```text
TDBC v1 TechDev Business Cycle 2026-07-26(2).zip
```

Verified identity:

```yaml
sha256: e83d3b95e94fba331767feae92bd052ed7f752a1a5305d63621030b293bc5d4c
zip_members: 18
checksums: 17/17_PASS
classification: RECONSTRUCTION_NOT_VENDOR_SERIES
```

TDBC remains a separate business-cycle reconstruction and may not silently replace a vendor series.

## Overlay warning

The recovered base and latest continuation share 17 relative paths. All 17 differ by hash.

A flat extraction or overwrite would destroy phase context. Required layout:

```text
base_052808/
latest_delta_114012/
tdbc_v1/
```

Common files such as README, coverage, receipts and readiness matrices must remain versioned by package namespace.

## Portable recovery bundle

A compact portable bundle was generated from the uploaded files:

```yaml
filename: GLC_BACKTEST_RECOVERY_BUNDLE_20260729.zip
sha256: a38fc62f2b3a2c933528878a10614d46d61dce609b2c9eebc51763e14255c64f
bytes: 2962221
members: 309
```

It contains:

- full upload-set and member-hash manifests;
- base-versus-delta conflict registry;
- the base master daily panel;
- base code and key governance/QA artifacts;
- the full latest compact continuation;
- the full TDBC package;
- recovery decision and final-release reconciliation target.

The binary bundle remains external to GitHub to avoid silently turning a reconstructed candidate into the exact final master.

## What is now resolved

```text
Earlier complete backtest base: RECOVERED
Master daily panel: RECOVERED
Reconstruction code and tests: RECOVERED
Source inventories and receipts: RECOVERED
FRED/OKX continuation chain: RECOVERED
TDBC reconstruction: RECOVERED
Upload hashes and CRC: VERIFIED
Internal checksum failures: ZERO
```

## What remains unresolved

```text
Exact final 183529Z binary: MISSING
Final 514-file byte parity: NOT TESTABLE
Official Nasdaq owner package: MISSING
BEA/FRED interest-payment package: MISSING
CBO vintage archive: MISSING
Treasury maturity/issuance owner package: MISSING
BIS GLI bulk package: MISSING
ALFRED/archived real-time vintages: MISSING
Final source-to-normalized parity: NOT COMPLETE
```

The Yahoo macro collection contains Nasdaq-100 and QQQ challengers, but they do not satisfy the official `NASDAQCOM` owner contract.

## Allowed continuation

This recovery permits:

- source-contract materialization;
- point-in-time schema engineering;
- deterministic rebuild tests against the recovered base;
- source-to-normalized parity work;
- acquisition of missing official macro series;
- synthetic statistics and graph validation.

It does not permit:

- economic testing before G20;
- parameter search;
- final-holdout inspection;
- framework or sensor promotion;
- market-state, gate, rebuy, deployment or portfolio changes.

## Final ruling

The prior blocker `final master binary unavailable` is narrowed to:

```text
EXACT FINAL BINARY UNAVAILABLE,
BUT A COMPLETE EARLIER BASE AND APPEND-ONLY CONTINUATION CHAIN ARE BYTE-RECOVERED.
```

That is sufficient to continue WP01 and WP02 engineering. It is not sufficient to pass G02 or open G20.
