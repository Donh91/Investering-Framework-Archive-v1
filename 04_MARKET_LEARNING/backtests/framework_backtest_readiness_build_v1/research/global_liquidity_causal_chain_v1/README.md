# Global Liquidity Causal Chain Research v1

This program tests the public claims that Bitcoin and Nasdaq closely track global liquidity and that future interest payments can forecast liquidity roughly three years ahead.

It is not designed to prove the claim. It is designed to distinguish:

- shared trend from predictive information;
- liquidity requirement from liquidity actually delivered;
- visual chart resemblance from out-of-sample edge;
- macro regime context from sell or rebuy timing;
- fiscal pressure from the policy reaction that transmits it.

## Current status

Claim freeze and causal architecture are complete. Source acquisition and point-in-time engineering are active. Economic tests remain locked by the repository-wide Backtest Readiness Gate.

The 2026-07-29 upload recovery found a complete earlier Backtest History base and append-only continuation chain. The exact previously referenced `183529Z` final binary is still missing, so exact G02 byte integrity and G20 remain blocked.

Recovery classification:

```text
RECOVERED_BASE_BINARY_PLUS_APPEND_ONLY_DELTAS
```

Recovered base:

```text
DATA PING BACKTEST HISTORY PACK 20260727T052808Z(1).zip
sha256 303d63946fd7696237b8d1a7208fa5aadd877e55aba57d5b51ea17aa46d18c9f
```

It contains the master daily panel, code, tests, raw and normalized data, receipts, source inventories and validation artifacts. It is a source-recovery candidate, not the exact final master.

## Most important derived hypothesis

`LIQUIDITY_DELIVERY_GAP = LIQUIDITY_REQUIREMENT - LIQUIDITY_DELIVERY`

A large positive gap may first imply funding stress, higher term premium, stronger dollar and risk-asset pressure. A later acceleration in delivered liquidity may mark a regime transition. The sign and timing are empirical questions, not assumptions.

## Files

- `CLAIM_FREEZE_v1.json`
- `SOURCE_REGISTRY_v1.json`
- `SOURCE_CONTRACTS_v1.json`
- `ACQUISITION_RECEIPT_v1.json`
- `BACKTEST_MASTER_RECOVERY_MANIFEST_v1.json`
- `BACKTEST_MASTER_RECOVERY_REPORT_v1.md`
- `CAUSAL_DAG_v1.json`
- `PREREGISTERED_ANALYSIS_CONTRACT_v1.md`
- `EXECUTION_STATE_v1.json`
- `AGENT_WORKPACKS_v1.md`
- `PROSPECTIVE_MONITORING_CONTRACT_v1.json`
- `validate_program.py`

## Existing-owner routing

- BT11 Sensor Ablation and Redundancy
- BT15 Defense versus Opportunity Cost
- GRA04 Lead-Lag Network
- GRA07 Contradiction Graph
- Sensor Relationship and Incremental Value Standard

No new active test ID, engine or live signal is created.

## Current next work

1. materialize official Nasdaq, BEA interest-payment, CBO-vintage, Treasury and BIS owner packages;
2. preserve ALFRED or official release vintages;
3. execute source-to-normalized parity against the recovered base under separate base and delta namespaces;
4. reconcile the recovered chain against the reported exact final release if that binary is recovered;
5. keep economic execution and the final holdout closed until G20 passes.

## Authority boundary

Research and engineering only. No market-state, gate, rebuy, deployment or portfolio authority.
