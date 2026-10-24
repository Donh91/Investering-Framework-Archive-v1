# Source document red-team | HF native file inspection delta 2026-10-22

**Authority:** provider-authored dataset README/DATASHEET/MANIFEST/file listing, checked through HF connected filesystem, not an independent reproduction of entire underlying Parquet content. This is an **additive corrective audit** following the preliminary Hub viewer source census. No download/execution, account-billed compute, forecast, production or portfolio changes.

## HIGH: HF-005 pump.fun sample is not a clean general-market edge corpus
**Dataset:** https://huggingface.co/datasets/Tr4m0ryp/trenches-pumpfun-forward-2026-08
**Direct source files:** README.md; DATASHEET.md; MANIFEST.json. Source authors' disclosures:
- **License:** precisely `polyform-noncommercial-1.0.0`, attribution/no resale; not merely 'other'. Intended production/commercial deployment and derivative usage require explicit legal/terms assessment. This is a *licensed study*, not universally reusable commercial signal input.
- **Period:** 2026-08-06T22:40:47Z to 2026-08-13T01:07:50Z across 146.45 elapsed hours, but just **75.27 observed hours**. Gap 69.09 hours, followed by 2.09 hours; not random coverage. Stratify pre_gap/post_gap and reject claims of continuous collection.
- **Population selection:** vendor-curated near-progressing token feed. Chain-completion label 960/84,584 pump.fun mints, **1.135%** in-sample; historical other venue population claims **0.198%**. These are different populations; never market-wide extrapolate the enriched base rate.
- **Labels:** `path_completed` 960 true vs live `graduated` 880 true; 80 false negatives and 0 false positives reported relative to chain reading. Outcome `y_theta_70` is **false on every row**, because source curve-path pulling has 0% coverage for this population; `path_status=error:not_pulled`. NEVER train on/score `y_theta_70` or conflate absence of progress with negative outcome.
- **Join impossible for trades:** `curve_paths.jsonl.gz` and `launch_windows.jsonl.gz` cover earlier populations and have **zero mint overlap** with the observed 85,442-mint capture. No trade-path pathwise return/exit outcome may be inferred by joining them.
- **Other venues unlabelled:** 858 of 85,442 token mints cover ray_launchpad, meteora_dbc, sugar with no curve completion label; no mixing venue denominator.
- **Social reach is late:** 0 of 85,442 mints have `reach_derivable_at_decision=true`; corrected read time median reported **20.52 s** after its stamped time for 56,593 reach blocks. All `reach_*` must be barred from first-sighting decision model.
- **Clock bug:** 1,225 mints (1.4337%) have negative observed token age, minimum **-27.6723 s**; suggested conservative age bound is `seen_at + 27.68 seconds`, subject to owner verification.
- **Target proxies leak by construction:** progress/market cap/liquidity/vendor curve proxy variables can trivially predict completion if already near graduation. Follow the author's full 21-name banned-feature list; no reward for tautological predictors.
- **File integrity corner case:** repaired multi-member `launch_windows.jsonl.gz` recovered **999** records; authors say plain gzip reader reads only **130** silently. Validate compressed file against pinned MANIFEST SHA and count. Also note DATASHEET describes license and captures publisher-provenance, not our independent verification.

**Audit decision:** `LICENSING_RESTRICTED__PIT_HARDENING_RESEARCH_ONLY`. High scientific educational value as a source of *counterexamples and explicit leakage tests*. Not a direct input to commercial Alpha Lab signals or claimed positive alpha without fresh legal, chain, timestamp, population and actual independent holdout validation.

## HIGH: HF-001 source counts/revisions conflict internally
**Dataset:** https://huggingface.co/datasets/zongowo111/v2-crypto-ohlcv-data
- Hub viewer displays ~9.0M Parquet rows/~425.3 MB across converted dataset.
- Provider `README.md`, generated 2025-12-30, says **4,819,964 data points**, 46 files, 23 symbols and 15m/1h bars, 110.57MB.
- `fetch_report.json` documents 23 symbols × 2 timeframes, 46 successful fetches on 2025-12-30.
- Live file listing for `klines/BTCUSDT/` also has **BTC_1d.parquet** and **BTC_1m.parquet**, alongside 15m/1h, meaning stored repository surface is not fully described by README's two timeframes. The plain Parquet viewer's 12-column schema omits market symbol because it is encoded in the file path, so merged dataset cannot be joined safely on timestamp without reconstructing original path/symbol/timeframe.

**Audit decision:** `P1_WITH_FILE_LEVEL_REVISION_CENSUS`; cannot represent advertised global row count as a consistent published fixed historical file cohort, and no R1 source admission.

## MEDIUM: HF-002 Hub viewer says zero rows, but direct files exist
**Dataset:** https://huggingface.co/datasets/linxy/CryptoCoin
- HF `dataset_structure` exposed no viewer config rows, but `hf_fs ls` confirms per-symbol directory `BTCUSDT/` with 10 per-symbol intervals, from 5m to 1d.
- `BTCUSDT/BTCUSDT_1h.parquet` exists, ~9,050,531 bytes; README shows 364 symbol names, per-symbol Parquet and daily updates (2026-10-22 00:48:34 UTC).
- Therefore classify **viewer-unindexed, not source absent**. This may be a better narrowly addressed date/venue pilot than giant merged viewer datasets, subject to SHA and first-known evidence.

**Audit decision:** `P1_TARGETED_FILE_PILOT`, but no status as accepted production bars, no independent provider custody.

## MEDIUM: HF-004 orderbook/live and historical scans must be separated
**Dataset:** https://huggingface.co/datasets/aliplayer1/polymarket-crypto-updown
- README documents a **historical Gamma/CLOB scan and on-chain backfill every 6h** plus **live 24/7 WebSocket** capture; consolidated uploads every 3 hours. One dataset therefore contains rows with distinct original accessibility and collection provenance.
- For predictions and CLOB snapshots, `ts_ms` on a late backfill is NOT evidence a live observer could have acted then. `ticks.source` differentiates `onchain` and `websocket`, but source-specific first-retrieval still requires proof.
- `markets.resolution = -1` and `fee_rate_bps = -1` are unknown, not false or zero-fee. Hub sample shows both.
- Amount of data (~9.3 billion orderbook rows) argues for metadata/partition projection, not full download.

**Audit decision:** `RESEARCH_CANDIDATE_SMALL_SPLIT_WITH_SOURCE_STRATIFICATION`.

## MEDIUM: HF-007 historical Chain of Title unresolved access
**Source:** https://huggingface.co/datasets/chainoftitle/chain-of-title. Native HF filesystem `stat` returned exists=false, while search-engine-indexed public page still describes the CC0 dataset/DOI and 2026-09-08 frozen deposit; direct web open was unauthorized at this check. Neither independently proves deletion nor current downloadable access. Existing framework's frozen CC0/archive source-boundary must stand. Status `SOURCE_ACCESS_ANOMALY__NEEDS_AUTHORIZED_RECHECK`. Do not bypass access controls or conflate licensed live API.

## Delta evidence grade and reporting requirement
All source-statistics above are **author-documented claims checked against actual source files/metadata**, not recalculated from entire source tables. This still materially changes which experiments are safe to propose. Next Task 2 run must record tested exact file revisions, SHA-256 and refusal/acceptance receipts, and the first-known gate before R2. Research outcomes and operational source availability are distinct.
