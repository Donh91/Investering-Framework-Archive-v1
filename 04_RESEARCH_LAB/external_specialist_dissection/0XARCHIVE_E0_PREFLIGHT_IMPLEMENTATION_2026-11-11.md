# 0xArchive E0 metadata source preflight (2026-11-11)

Status: SHADOW_ONLY / NO_PROVIDER_DATA / NO_PAID_SPEND / NO_SOURCE_AUTHORITY.
Owner: existing Archive S5 #1514 and HRE #1596. Related source audit: Archive PR #2085; original external specialist queue #1512.
Files: `scripts/research/oxarchive_e0_source_preflight_v1.py` and `tests/research/test_oxarchive_e0_source_preflight_v1.py`.

## Scope

This zero-dependency Python preflight validates **only a research source receipt's declared metadata**, not the vendor record bytes, access, market truth or strategy performance. It never authenticates with 0xArchive, connects wallets, checks raw trades, modifies files, sends HTTP, dispatches a paid model, publishes source data, or changes the Compass and Alpha Lab production path. It is NOT a backtest engine or a new source collector.

Its output deliberately states:
- `SCHEMA_ONLY_PASS` when syntactic, temporal, source identity, legal-state and private metadata constraints are internally consistent;
- `HOLD` with stable error codes if something is missing, malformed or contradictory;
- **all real-world proof flags false in either case**, including `external_source_authenticated`, `raw_dataset_bytes_verified`, `first_known_proof_independently_verified`, `trading_edge_proven`, `production_admitted`, `publication_authorized`.

Even an E0 `SCHEMA_ONLY_PASS` does **not** establish that the public metadata reflects original historical availability. Independent authenticated source and historical publication receipts must be inspected under the existing data-plane authorization.

## Entrypoint and tests

From the repository root:

```bash
python -m py_compile scripts/research/oxarchive_e0_source_preflight_v1.py tests/research/test_oxarchive_e0_source_preflight_v1.py
python -m unittest tests.research.test_oxarchive_e0_source_preflight_v1 -v
python scripts/research/oxarchive_e0_source_preflight_v1.py /path/to/restricted/metadata-only-receipt.json
```

The CLI prints **only stable error codes and safe status fields**. Do not give it the raw vendor payload. It rejects symlinks, directories, pipes and files larger than 256 KiB. Input JSON is allowlisted; unknown fields are rejected rather than included in output.

The test fixture is entirely synthetic. No real provider request or vendor data is included in this change.

## Claimed receipt shape

Required `OXARCHIVE_E0_SOURCE_RECEIPT_V1` fields are exactly those in `inspect()` and the synthetic fixture in the unit test. Important constraints:
- `decision_cutoff_utc` and source clocks are full UTC-Z instants, not date labels or exchange-local clocks.
- Each receipt binds `family + market_id + datatype + API version`, never plain BTC alone. Supported families include Hyperliquid core/Spot/HIP3/HIP4 and both Lighter deployments.
- `window_start <= event_max < window_end <= decision_cutoff`, and both source first-known and provider available timestamps must lie between the event and the cutoff. A later retrieval is *allowed* but cannot establish first-known.
- `availability_evidence=IMMUTABLE_PRIOR_PUBLICATION_RECEIPT` is required as a **declaration only**. Another layer must independently validate that immutable prior proof, not merely trust the string.
- `quality_state=COMPLETE_WINDOW`, zero gaps, finalized rows, nonzero row count, schema digest and private dataset binding metadata are required. An accepted shape cannot waive independent gap, clock or file-hash audits.
- `rights_state=INTERNAL_RESEARCH_RIGHTS_REVIEWED` is a caller declaration. Before real use, first retrieve and verify the binding 0xArchive Data License and Terms against intended outputs. Provider's developer data-rights summary is NOT the controlling contract.
- Private binding references `Donh91/secrets`, SHA-1 Git commit ID, SHA-256 data hash, byte count and private path. Data bytes stay restricted; API keys stay only in approved runtime secret storage.

## Scientific-method transfer and nonduplication

**Study ledger:** 0xbt's trial ledger counts recorded attempts but resets via a newly created study. We should compare existing internal trial accounting with an externally anchored, append-only **global** attempt registry before accepting any deflated-Sharpe claims. Do not copy its plugin into a privileged executor.

**New source-code audit, pinned upstream commit 3ff0c834:** In `skills/backtest/engine/crates/py/python/oxarchive_backtest/study.py`, `Study.trials()` includes the *first* run with each `result_hash` and skips other `kind=trial` rows with the same result. Thus `len(Study.trials())` is distinct result hashes, not an exhaustive attempt count; `deflated_sharpe()` receives this deduplicated list. Multiple parameter configurations or selected windows with identical result paths can be collapsed. Do not equate this value with every exploratory attempt or with the statistically **effective independent** trial count. A robust Research Lab design should preserve all three separately: `attempt_count_all`, `distinct_outcome_hashes`, and `effective_independent_trial_count` (estimated using preregistered correlation/multiplicity rules). Source code also states that a study not initialized means nothing is recorded or sealed. This is a source-level observation, NOT an executed exploit or validated numeric bias. Test synthetic duplicate-result, reset/new-study, direct-Parquet and immutable global tip behaviors before any method import.

**Holdout:** 0xbt docs say directly reading underlying Parquet bypasses the study seal. Our eventual holdout must be protected by independent storage permissions and one-use release, not merely a Python API convention. This metadata preflight is deliberately NOT a holdout enforcement module.

**Reproducibility:** test source commit + dataset byte hash + strategy source hash + parameters + fee model + source available-at + universe/version; a 16-hex result hash is not a substitute for dataset-level byte attestation.

**Clock perturbation:** treat 0xbt's phase perturbation as an independent negative-control candidate. Compare existing HRE chronological/episode-clock controls first and implement only a demonstrably missing primitive.

**Reality Lab:** use existing HRE and price-control cost sensitivity code; `0xbt` uses 1-minute Hyperliquid core perp bars, with orderbook columns always null and default 2 bps fallback slippage. Thus it is NOT an already-realistic L3/L4 execution simulator.

**Alpha Lab:** preserve existing `Meme-Alpha-Lab/scripts/exit_quote_quality_v1.py` and paper wallet's prospective frozen decisions, size/capacity and fee/gas/sellability/no-fill semantics. Do not infer DEX-microcap realizable exits from Hyperliquid perps. Any cross-system transfer should be *scientific controls*, not external composite scores.

## Terminal criteria

1. E0 code and synthetic regression CI at exact HEAD green, independent review, governed merge, main readback.
2. Real provider E0 only after separate free-key access and data-rights proof; required quality routes include `/v1/capabilities`, `/v1/data-quality/coverage/{exchange}/{symbol}`, freshness, incidents and symbol-specific pagination. These have not been queried with authenticated access.
3. E1-E4 tests are later, under existing original issues. Prospective frozen outcomes and value-over-native-source controls are required before promoting anything.
4. On no legal access or no source-specific first-known, the honest state is `SOURCE_ACCESS_UNVERIFIED` or `SOURCE_CLOCK_UNKNOWN`, not PASS/READY. Preserve adverse/negative research outcomes.

No new workflow, scheduler, agent, cost, source authority, market threshold, trading permission or default skill installation is authorized by this document.
