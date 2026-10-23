# 13 | Hugging Face selective data acquisition, provenance and challenger protocol
**Status:** PILOT_DESIGN_ONLY, awaiting owner approval of Work; public metadata reviewed on 2026-10-22. **Read first:** existing PR #1747 files 01–10, SOURCE_MANIFEST_v1 and SOURCE_MANIFEST_DELTA_v2. These source documents are primary, this file is an execution order, not an alternative source roster.
**Account:** connected `FrameworkCN` was recorded as Free/`is_pro=false` in #1747. Verify at run time. Free Hub search is useful; it is not permission to run paid Jobs or an unlimited always-on hosted agent.

## The overarching question
Which previously unavailable *independently verifiable* first-known market, news or behavioral facts does a particular HF source contribute to an already owned Task 2 hypothesis, and is that contribution **admissible** and **decision-relevant** after comparison with cheaper existing inputs?

An HF dataset published in 2026 and containing 2024 candles gives historical price reconstruction, **not** proof that a forecast issued in 2024 originally used or could actually access that specific 2026 file. It may serve as later truth/outcome source or conservative baseline when timestamp, revision and law allow, but original decision provenance still needs original-era evidence.

## A. Candidate order and hard ceilings
| Priority | Existing HF source | Exact narrow pilot | Admissible initially for | Disqualifier |
|---|---|---|---|---|
| P1-A | `linxy/CryptoCoin` ([HF](https://huggingface.co/datasets/linxy/CryptoCoin)) | one revision-pinned `BTCUSDT/BTCUSDT_1h.parquet` and optionally ETH same schema, inspect 500–2,000 rows across known boundary timestamps | public price cross-check, cheap-control and later outcome tape | dataset viewer zero rows mistaken for missing file; mutable `main` source; future bar close |
| P1-B | `zongowo111/v2-crypto-ohlcv-data` ([HF](https://huggingface.co/datasets/zongowo111/v2-crypto-ohlcv-data)) | one BTC/ETH hour/day file; reconcile actual file tree vs advertised 46 files / 4.82m points vs Hub viewer ~9m | independent price comparison, venue drift and source QA | inconsistent identity, duplicate symbols, unresolved 1m vs 1d intervals |
| P1-C | `Chainticks/stablecoin-flows` ([HF](https://huggingface.co/datasets/Chainticks/stablecoin-flows)) | actual rows in 1–2 date partitions + `_manifest.json`; validate mint/burn/bridge ontology | source QA and confound controls only | manifest event gaps (May14–15 ~20.487h), chain/bridge counting conflicts, conflating transfers with deployment |
| P1-D | `zeroshot/twitter-financial-news-sentiment` ([HF](https://huggingface.co/datasets/zeroshot/twitter-financial-news-sentiment)) | one small licensed original train/test partition | *only* text classification / calibration and label quality | no crypto domain transport proof, leakage, no first-delivery signal |
| P2-A | `aliplayer1/polymarket-crypto-updown` ([HF](https://huggingface.co/datasets/aliplayer1/polymarket-crypto-updown)) | small market and prices partition, **not** 9.31B orderbook records | after-clock market probability / efficient-market baseline | mixed backfills/later resolutions, one-sided/crossed book, no fee/fill basis |
| P2-B | `Chainticks` liquidation ticks (exact ID in PR #1747 07/manifest) | tiny selected venue/day original stream, reconcile 5→800 instrument jump around July12 and venue capping | stress event sourcing/coverage sensitivity | aggregate universe discontinuity; extrapolated market notional |
| P2-C | `edaschau/bitcoin_news` ([HF](https://huggingface.co/datasets/edaschau/bitcoin_news)) and PR #1747 source-clock news candidate | URL and headline family dedup, publisher/retrieval timing conflict | retrospective news QA only | publisher timestamp substituted for first observed source receipt |
| P2-D | `BlockDB/Stablecoin-Transfers-Ethereum-Cryptocurrency-Data` ([HF](https://huggingface.co/datasets/BlockDB/Stablecoin-Transfers-Ethereum-Cryptocurrency-Data)) | tiny projected Parquet partition, only if P1-C fails or adds independent information | bridge and mint/burn attribution quality | 83GB bulk download and blind transfer-as-net-liquidity signal |
| P3 | `Tr4m0ryp/trenches-pumpfun-forward-2026-08` ([HF](https://huggingface.co/datasets/Tr4m0ryp/trenches-pumpfun-forward-2026-08)) | **existing** Alpha Lab ablation code/source-hash review only | Alpha source red-team / negative controls within license | PolyForm Noncommercial, 69.09-hour collector gap, negative token ages, unavailable reach, degenerate target |
| HOLD | `chainoftitle/chain-of-title`, large scraped/historical news, other model/vendor sources | source access/rights proof only | no scientific admission | inaccessible source, rights mismatch, unknown data provenance |

**Important:** A row count or source quality discrepancy does not automatically prove malice, predictive failure or usefulness. Reproduce exact file revision and denominator.

## B. File custody and machine protocol, mandatory for every pilot
Step B1, SEARCH: read canonical owner source inventory and #1747 manifests, deduplicate by exact HF repo ID/file/revision. Search similar public feeds already in GitHub and private restricted owner metadata. Reject repeated projects.
Step B2, PIN: resolve and save immutable HF repository commit SHA. Record exact path, size, SHA-256 content, license card and upstream ownership; file availability verified from actual fetch, not Dataset Viewer counts. A commit-hash string without downloaded blob verification is `SOURCE_METADATA_ONLY`.
Step B3, READ SAFELY: Parquet/Arrow direct projected columns, narrowed date/venue partitions; no `trust_remote_code`, external loader scripts or Space demo execution with GitHub/HF tokens; explicit fetch max bytes, request backoff and CPU/memory caps. Do not mirror large datasets.
Step B4, TIME: three independent clocks `market_event_at`, `provider_first_available_at`, `our_observed_at` plus `archive_revision_at`. For news include original publisher, platform first-seen and story family. **If historic true first-known is unknown, downgrade to retrospective truth tape, not an issued-signal feature.**
Step B5, QA: schema names/dtypes, finite values, granularity, unique symbol/chain/venue identity, UTC normalization, timestamp monotonicity, 1m/1h candle close, weekend gaps, duplicated events, impossible prices, outliers, OHLC inequality, quote/underlying basis, missing and incomplete event count, revisions and delist/survivorship, parent/child token series.
Step B6, CONTAMINATION: feature availability vs forecast issue; label availability vs outcome due, publication and model pretraining cutoff; train-only feature selection, embargo/purged event families and untouched holdout.
Step B7, EVIDENCE: write an immutable public-safe receipt with file meta/hash, limited quality counts and status. Any restricted original provider values or private account/portfolio records remain `Donh91/secrets` with approved private binding. No data movement to public GitHub beyond boundary allowlist.
Step B8, ADMIT / REJECT: owner signs exact reason code and independent review. `T1_FILE_QA` is not `T2_PIT`. Summarize what decision or classification could change; if none, stop.

## C. Candidate model comparisons, optional and last
- **Text duplicate clustering:** start with normalized original URL + stable title hash and simple TF-IDF. Then consider pinned [all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), but only if it improves held-out same-story-family precision/recall over cheap baselines at acceptable cost and lawful license. Goal: less duplicate news, not price prediction.
- **Sentiment:** start dictionary/tiny supervised baseline, then consider [yiyanghkust/finbert-tone](https://huggingface.co/yiyanghkust/finbert-tone) if license and training data allow. [ProsusAI/finbert](https://huggingface.co/ProsusAI/finbert) is noncommercial/share-alike-tagged, HOLD pending rights; headline label accuracy is not action advantage.
- **Time-series:** start persistence/seasonal naive, volatility bands and simple autoregressive controls, then an independently pinned [amazon/chronos-bolt-small](https://huggingface.co/amazon/chronos-bolt-small), Apache-2.0-tagged per existing #1747 card. Its training vintage, release date and historical contamination must be made explicit. A 2026 model cannot be pretended to have been an actual 2023 framework forecast.
- **Deep follow-on:** Chronos-2 or other pretrained forecasting model only if small baselines demonstrate a nontrivial testable deficiency and compute cost is approved. A better RMSE does not imply timing action edge.
- **Alpha:** DO NOT create a new classifier/agent/workflow. Audit existing `research/api_agent/meme_alpha/experiments/trenches_point_in_time_ablation_v1.py` for train/test-aware prefiltering, negative token ages, field-level decision timestamps, source-manifest/revision pinning, split disjointness, and realistic exit labels. Existing Alpha owner decides fixes and legality.

All models use frozen chronological, cross-event embargo, train-only transforms and zero private inference tokens to third-party endpoints unless explicitly approved. Log preprocessing, architecture, seed and runtime SHA. Compare **incremental decision benefit** and false-positive/false-negative tradeoffs, not model-card popularity.

## D. Required HF source card format (owner-safe)
```yaml
source_id: HF-...
hf_repo_id: ...
hf_revision_sha: ...
exact_file_paths: [...]
file_sha256: ...
file_bytes: ...
license_spdx_or_exact_text: ...
license_conflicts: ...
underlying_exchange_chain_venue: ...
publisher_update_time_utc: ...
market_event_start_end_utc: ...
original_first_known_proof: VERIFIED | PARTIAL | UNKNOWN
collector_gap_and_missingness: ...
symbol_and_universe_definition: ...
grain: ...
observed_rows: ...
candidate_total_rows: ...
independent_event_families: ...
known_future_derived_fields: [...]
source_qa_tests: [...]
negative_controls: [...]
framework_owner: ...
allowed_use: SOURCE_QA | AFTER_FACT_TRUTH | PIT_CANDIDATE | REJECTED
admission_tier: T0 | T1 | T2 | T3 | T4
cost_actual_usd: ...
status_reason: ...
```
Do not use `0` for unknown row count, read cost or availability.

## E. Free-tier resource and ROI decision
Use free Hub metadata/card/revision discovery as default. According to official HF reference available on the audit date, free 5-minute request buckets are **1,000 Hub API, 5,000 resolver and 200 page requests** subject to dynamic adjustment; PRO raises them but does not grant free metered Jobs. Cache immutable revisions; obey 429. Free account may have low monthly Inference Providers credit, which is NOT authority to spend beyond it. Paid Jobs require positive compute balance and run charges by minute. On existing evidence, **FREE is sufficient for source discovery, rights review and small manual source QA**. Paid GPU training is not justified before original clock admission.

Any proposed upgrade first produces: target original scientific blocker, free-path alternatives tried, exact compute/data transfer estimate, irreversible/license risks, cost cap, expected outcome, stop-after criterion and explicit owner approval. **No subscription or paid Job launched here.**

## F. Output of the first allowed HF pilot
One pinned small BTC/ETH 1h Parquet source, exact file verification and clock-gap QA, optional second source independent comparator, at least five hostile fixtures, explicit eligible/unknown census and one same-clock price-only comparison *if actually admissible*. Result may be `DATA_SOURCE_REJECTED`. No model training or ETF-era signal score required. It only counts as Task 2 progress if it clears a previously named original R0/R1/R2 obstacle; otherwise mark `EXPLANATORY_SOURCE_QA`.
