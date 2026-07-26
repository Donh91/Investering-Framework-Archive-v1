# Custom GPT historical backtest packs - independent audit

**Audit date:** 2026-07-26  
**Status:** `HASH_AND_LOGICAL_ARCHIVE_COMPLETE / RAW_ZIP_GITHUB_COPY_PENDING / DATA_MOSTLY_SOUND / REPRODUCIBILITY_REPAIRS_REQUIRED / SYNTHESIS_DEFERRED`  
**Authority:** Evidence, QA and backtest-design input only. No market call, forecast score, portfolio action or canonical-state change.

## 1. Executive decision

The two packages should be audited and their identity preserved immediately. There is no benefit in waiting for Claude before preserving hashes, inventory, lineage and findings.

The final combined backtest design, test priority and any canonical admission decision should wait for Claude's forthcoming package so all evidence can be reconciled once rather than ratified piecemeal.

```yaml
archive_now: YES
run_economic_backtests_now: NO
ratify_final_test_matrix_now: NO
wait_for_claude_for_final_synthesis: YES
```

### GitHub materialization boundary

The uploaded ZIP files were read directly and independently hashed. Their exact hashes, sizes, internal inventories and audit results are now preserved in GitHub.

The available GitHub contents route in this execution context does not accept a mounted local ZIP path as a repository binary file. Therefore the raw ZIP byte streams themselves are not claimed to be present in the repository. No base64 surrogate or corrupted pseudo-binary representation was created.

## 2. Large history pack

Artifact:

`DATA_PING_BACKTEST_HISTORY_PACK_20260726T205621Z.zip`

### Verified structure

- 70 files;
- 549,093 uncompressed bytes;
- package-reported 2,013 rectangular/event rows;
- 69 non-manifest checksum entries independently verified with zero mismatch;
- OHLC row invariants pass for the packaged BTC and ETH direct source tables;
- raw-to-normalized row reconciliation passes for the OKX index pages;
- ETF fund totals reconcile for all ten W30 fund-level rows;
- no weekend ETF zero rows were created;
- breadth is correctly fail-closed as forward-only;
- venue and market-type boundaries are preserved.

### Actual usable coverage

- BTC and ETH OKX perpetual-swap 1H: 166 rows each, W30 only;
- BTC and ETH OKX index-proxy 1D: 98 rows each, 2026-04-18 to 2026-07-24;
- derived ETH/BTC index proxy: 98 rows, not direct;
- ETF fund-level flows: five W30 sessions per asset inside this package;
- derivatives: four current snapshot rows, not historical series;
- breadth: two forward snapshots;
- framework extracts: three partial records;
- macro, CFGI, stablecoin and TVL: limited subsets or snapshots.

The package is therefore valuable as a deterministic integration fixture and partial historical evidence package. It is not a broad multi-cycle backtest database.

## 3. Extraction-parts package

Artifact:

`FRAMEWORK_BACKTEST_EXTRACTION_PARTS_TO_20260726T204022Z(2).zip`

### Verified structure

- 16 files;
- 134,765 uncompressed bytes;
- 98 normalized rows for each of parts 01, 02 and 03;
- actual coverage 2026-04-18 to 2026-07-24;
- all three parts correctly labelled `PARTIAL_WITH_EXPLICIT_GAPS`;
- direct Binance requests failed by geo restriction;
- OKX index candles remain proxy evidence, not relabelled as spot;
- ETH/BTC remains derived, not direct;
- continuation manifest preserves pagination state.

### Relationship to the large pack

Five substantive source/data files are byte-identical to copies in the large history pack. The package should therefore be retained for lineage and continuation control, not counted as five additional datasets or extra sample coverage.

## 4. QA findings requiring repair

### Q1 - self-referential manifest inconsistency

The large pack's internal `manifest.json` lists itself as:

```yaml
claimed_bytes: 1419
actual_bytes: 13948
claimed_sha256: 0b2378a2a487dfeff9831558d26cc0926b3827aa2f4d0502a857068733ec526d
actual_sha256: a5c79625bb684be2dbd66d98708ced235d3bc0b1e5633d967723f820f689fd82
```

The separate `CHECKSUMS.sha256` correctly excludes the manifest and all 69 listed non-manifest files pass. This is a manifest-construction defect, not evidence that payload files changed.

The extraction-parts package has the same class of issue:

- its package manifest has a stale self-entry;
- its manifest also records a checksum-file hash that does not match the final checksum file;
- the checksum file's 15 ordinary entries independently pass.

Required repair pattern:

- never require a file to contain its own final hash;
- exclude manifest and checksum ledger from self-hashing, or use a detached outer receipt;
- generate payload checksums first, manifest second and detached package receipt last.

### Q2 - validation script overclaims its scope

`validate_package.py` describes itself as checksum and OHLC validation but only iterates over CSV files and tests OHLC invariants. It does not validate package checksums.

Required repair:

- either rename it to `validate_csv_ohlc.py`, or implement actual checksum, row-count, timestamp and manifest validation.

### Q3 - rebuild script is not replay-safe

`rebuild_features.py` rewrites the derived hourly ETH/BTC file with a reduced six-column schema. The archived target contains eighteen columns including venue, settlement, timestamps, method identity and high/low semantics.

Running the supplied rebuild script would therefore destroy schema parity and metadata.

Required repair:

- produce output to a temporary path;
- reconstruct the full locked schema;
- compare row count, column order and hash against the expected fixture;
- promote only after parity passes.

### Q4 - duplicate report uses incomplete keys

`duplicates.csv` flags repeated timestamps in multi-entity tables, including:

- BTC and ETH derivatives at the same snapshot;
- several FRED series on the same date;
- several chains or pools at the same snapshot.

These are not necessarily duplicate observations. The correct uniqueness keys are composite, for example:

- derivatives: `snapshot_utc + asset + venue + contract`;
- macro: `date + series`;
- stablecoins/TVL: `snapshot_utc + chain`;
- DEX: `snapshot_utc + address`.

Required repair:

- replace timestamp-only duplicate tests with dataset-specific primary keys.

### Q5 - readiness language is too generous for economic inference

BT01, BT02 and BT09 are labelled `READY_WITH_RESTRICTIONS`, but this package contains only five ETF sessions and one weekend-to-Monday candidate window.

They are ready as:

`PIPELINE_SMOKE_TEST / GOLDEN_FIXTURE`

They are not ready for:

- edge estimation;
- significance testing;
- parameter selection;
- portfolio-rule promotion.

The full ETF archive already present in GitHub, with 651 BTC sessions and 513 ETH sessions, should be the owner dataset for actual ETF backtests. The five-session rows here should be used as a W30 parity fixture.

## 5. Backtest value now available

### Ready now as engineering tests

1. Rebuild and exactly reproduce the W30 hourly, daily, volatility, drawdown and ETF feature files.
2. Verify that ETF information is not admitted before session close.
3. Verify that weekend ETF rows are absent rather than zero-filled.
4. Verify venue and market-type separation.
5. Verify that derived ETH/BTC cannot satisfy a direct-pair gate.
6. Test restart/continuation behavior from the parts 01-03 continuation manifest.

### Ready after joining existing GitHub ETF history

1. ETF flow persistence;
2. ETF reversal after streaks;
3. BTC versus ETH ETF-flow divergence;
4. weekend crypto movement versus next completed ETF session;
5. issuer concentration and flow breadth.

### Still blocked for real historical testing

- H7 and direct ETH/BTC transmission;
- 0.0300/0.0275 direct-pair gate statistics;
- historical funding/OI confirmation;
- breadth-confirmed rotation before archive start;
- TechDev business-cycle turns;
- last-flush/rebuy-delay with complete decision-time lineage;
- full state-machine replay.

## 6. Recommended handling when Claude arrives

Do not rebuild or merge the packages blindly.

Claude's material should be evaluated against this audit using four buckets:

1. `NEW_NON_DUPLICATE_DATA`;
2. `REPAIR_OR_VALIDATION_LOGIC`;
3. `TEST_DESIGN_OR_HYPOTHESIS`;
4. `DUPLICATE_OR_LOWER_AUTHORITY`.

After that, create one consolidated backtest work package with:

- an owner-source registry;
- a deduplication map;
- repaired detached manifests;
- replay-safe builders;
- golden-fixture tests based on W30;
- long-history economic tests only where sample and point-in-time lineage are adequate.

## 7. Framework decision

```yaml
hash_and_logical_archive: ACCEPTED
raw_zip_github_copy: PENDING_CONNECTOR_CAPABILITY
large_pack_payload_integrity: PASS_WITH_MANIFEST_SELF_REFERENCE_DEFECT
parts_pack_payload_integrity: PASS_WITH_MANIFEST_SELF_REFERENCE_DEFECT
canonical_backtest_dataset: NOT_YET
historical_edge_claim: NONE
framework_state_change: NONE
portfolio_action: NONE
next_gate: INGEST_AND_COMPARE_CLAUDE_PACKAGE
```
