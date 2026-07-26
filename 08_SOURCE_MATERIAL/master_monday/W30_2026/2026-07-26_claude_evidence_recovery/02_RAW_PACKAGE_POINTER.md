# W30 Raw Package Pointer

## Original package

```yaml
zip_filename: CN W30 MASTER MONDAY EVIDENCE RECOVERY 2026-07-26.zip
zip_bytes: 1676211
zip_member_count: 109
zip_sha256: 9353f2fcefb9aaf38d8102dd3a4ec538fba302352178e883e1bcf0cdc6472ad8
pdf_filename: W30 MASTER MONDAY EVIDENCE RECOVERY.pdf
pdf_bytes: 156817
pdf_sha256: 23b0f7f9b8aa7dc0612b2f757744f934f1246dd16ea81670e0f54c06ed5cdae3
attachment_context: Investering project conversation, 2026-07-26
binary_materialized_in_repository: false
binary_materialization_status: PARTIAL_CONNECTOR_LIMITATION
```

## Important package members

```text
W30_MASTER_MONDAY_EVIDENCE_RECOVERY.md
cn_raw_bridge.json
receipts.json
data/forecast_maturity_ledger_W30.csv
data/source_qa_matrix.csv
data/delta_vs_dp_snapshot.csv
data/breadth_membership.csv
data/etf_flows_last10_farside.csv
data/settled_closes_btc.csv
data/settled_closes_eth.csv
data/settled_closes_ethbtc.csv
data/computed_core.json
data/computed_aux.json
raw/manifest.psv
raw/run_anchor.txt
```

The remaining raw members include source payloads from Binance, Kraken, Coinbase, Bitstamp, OKX, CoinGecko, Farside, DeFiLlama, FRED, Yahoo and failed/fallback endpoints.

## Retrieval rule

A future process retrieving the original attachment must:

1. verify exact filename and byte count;
2. compute SHA-256 before extraction;
3. require exact match with the hashes above;
4. extract into a new immutable evidence directory;
5. retain the original ZIP unchanged;
6. compare `receipts.json` and `raw/manifest.psv` against extracted member hashes;
7. never treat the package as canonical framework state.

## Missing binary duplication

The repository connector available during this ingest accepted UTF-8 text writes but did not expose a direct binary upload parameter. The package is therefore represented by:

- cryptographic package identity;
- routed logical evidence summaries;
- source inventory;
- QA and receipt log;
- conflict registry;
- governance receipt.

This is intentionally recorded as a limitation rather than falsely claiming that the binary ZIP and PDF were uploaded to GitHub.