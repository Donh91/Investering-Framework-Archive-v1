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

## Most important derived hypothesis

`LIQUIDITY_DELIVERY_GAP = LIQUIDITY_REQUIREMENT - LIQUIDITY_DELIVERY`

A large positive gap may first imply funding stress, higher term premium, stronger dollar and risk-asset pressure. A later acceleration in delivered liquidity may mark a regime transition. The sign and timing are empirical questions, not assumptions.

## Files

- `CLAIM_FREEZE_v1.json`
- `SOURCE_REGISTRY_v1.json`
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

## Authority boundary

Research and engineering only. No market-state, gate, rebuy, deployment or portfolio authority.
