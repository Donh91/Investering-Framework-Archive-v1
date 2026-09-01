# OnChainMind / Public Data Source Admission v1

Status: `SHADOW_RESEARCH_COMPLETE / NO_MARKET_AUTHORITY`

This folder is the bounded source-admission result produced from the 2026-09-01 OnChainMind deep dive and subsequent public-upstream research.

## Final decisions

- **OnChainMind** remains discovery/context only. No automated scraping and no raw archive.
- **Coin Metrics Community** is approved as the preferred long-history reproducible baseline. Evidence runs must bind an immutable Git commit SHA.
- **BGeometrics standard on-chain series** are approved only for transient research. Raw payloads are not persisted in the public repository.
- **MVRV** failed the bounded incremental predictive-value replay. It remains valuation/stress context only.
- **Broad on-chain metric mining** is killed. No 200-metric fishing expedition.
- **URPD** is the strongest differentiated candidate and is approved only as a prospective Stress & Structure observation. Recent date-parameterized requests work, but the payload does not attest its own snapshot day and long historical retention is not verified.
- **Polymarket** openly documents research access, but durable raw storage/redistribution remains unresolved for this archive. The parser stays offline-only.
- **DefiLlama** reuses the existing owner. No duplicate adapter.
- **BGeometrics Regime Score** is rejected as a new vote because it recombines signal families already owned by the framework.
- **Self-hosted historical URPD** is deferred because it requires materially heavier UTXO/indexer and price-at-last-move lineage.

## Files

- `SOURCE_CONTRACTS_v0_1.json` - current provider and authority contracts.
- `PRIORITY_AND_KILL_MATRIX_v0_1.json` - executed PASS/KILL/DEFER disposition matrix.
- `REPLAY_OUTCOME_2026-09-01.json` - derived replay results, no provider raw data.
- `URPD_PROSPECTIVE_OBSERVATION_CONTRACT_v0_1.json` - shadow-only URPD lineage and feature contract.
- `RESEARCH_EXPERIMENT_SPEC_v0_1.md` - replay design and remaining falsification work.

Research-only code:

- `scripts/research_sources/coinmetrics_community_probe.py`
- `scripts/research_sources/bgeometrics_research_probe.py`
- `scripts/research_sources/urpd_topology_probe.py`
- `scripts/research_sources/polymarket_expectations_parser.py`
- `scripts/research_sources/onchain_incremental_value_replay.py`
- `scripts/research_sources/validate_research_source_receipt.py`

## Authority ceiling

Nothing in this package may directly:

- change a live gate or threshold,
- change portfolio state,
- become a new independent confirmation vote,
- bypass existing derivatives/source ownership,
- or masquerade as prospective evidence.

The architectural rule is: **copy less, bind better**.
