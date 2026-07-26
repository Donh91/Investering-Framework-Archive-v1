# Garden Finance incident — framework assessment

**Assessment date:** 2026-07-26  
**Evidence class:** `X_NATIVE_SOURCE_DISCOVERY + ON_CHAIN_CORROBORATION`  
**Status:** `SECURITY_EVENT_WATCH / NON_SYSTEMIC_AT_PRESENT / NO_CANONICAL_MARKET_STATE_CHANGE`

## Executive assessment

Garden Finance has a credible, material protocol-security incident with an official service-pause signal and independent exploit corroboration.

The current evidence does not establish:

- a final loss amount;
- a final exploit vector;
- broader stablecoin impairment;
- contagion to major bridge or exchange infrastructure;
- a market-wide liquidity event.

The early approximately `$450,000 USDT` estimate appears likely to be a partial first observation because a later independent investigator estimate is approximately `$10.8M+` across multiple chains. Both remain non-final pending a Garden postmortem and reconciled on-chain accounting.

## Framework classification

```yaml
incident_id: SEC-GARDEN-2026-07-26
protocol: Garden Finance
category: PROTOCOL_SECURITY_BRIDGE_HTLC
incident_confidence: HIGH
loss_size_confidence: LOW
root_cause_confidence: LOW
multi_chain_scope: PROBABLE
service_disruption: CONFIRMED_BY_SUPPLIED_OFFICIAL_POST
systemic_risk: NOT_DEMONSTRATED
market_state_effect: NONE
portfolio_state_effect: NONE
```

## Portfolio relevance

No Garden Finance token, position or direct protocol exposure is present in the currently tracked portfolio holdings.

Therefore:

```yaml
portfolio_action: NONE
rebuy_change: NONE
new_entry_change: NONE
rotation_change: NONE
large_caps_change: NONE
```

Operational safety remains separate from portfolio allocation: Garden app and contracts should not be used while the protocol is investigating and until remediation and reopening are independently confirmed.

## DATA PING and shadow-layer handling

This incident should not become a normal price, breadth, ETF or macro sensor.

It belongs in a bounded security-event shadow layer with these fields:

```yaml
protocol_outage: true
exploit_claim: true
loss_estimate_status: CONFLICTED_AND_EVOLVING
stablecoin_asset_involved: USDT
chains_reported: [Ethereum, Base, Arbitrum, BSC]
contagion_evidence: none_confirmed
major_market_dislocation: none_confirmed
```

Permitted effects:

- add protocol-security context;
- raise bridge/HTLC implementation-risk awareness;
- preserve source and estimate evolution;
- monitor for stablecoin, chain-liquidity or integration contagion.

Forbidden effects without further evidence:

- classify the whole market as risk-off;
- change rotation or recovery state;
- change portfolio permissions;
- treat the incident estimate as final;
- infer that HTLCs as a general primitive are broken;
- infer that Bitcoin, Ethereum, Base, Arbitrum or BSC core infrastructure was exploited.

## Grok-source value assessment

This is an appropriate use of Grok's retained role:

`X_NATIVE_SOURCE_DISCOVERY`

The run found an official protocol response and an early security-provider alert before conventional sources had fully indexed the event.

The run also demonstrates why Grok must remain a discovery layer rather than final adjudicator:

- the first numeric estimate was probably incomplete;
- the official post confirmed investigation and outage, not final cause or loss;
- later independent evidence materially changed the likely scale;
- source reconciliation was required before framework use.

## Watch conditions

Escalate the incident only if one or more of the following appear:

1. Garden confirms user losses or insolvency risk.
2. A major wallet, exchange or aggregator reports direct exposure.
3. USDT or another stablecoin shows material freeze, depeg or liquidity effects linked to the incident.
4. The exploit vector is shown to affect widely reused contracts or forks.
5. Attacker flows create measurable chain or market-liquidity stress.
6. The final loss materially exceeds current estimates or remains actively draining.

## Current decision

```yaml
security_event_watch: ACTIVE
canonical_state_change: NONE
framework_classification_change: NONE
portfolio_action: NONE
next_required_input: OFFICIAL_POSTMORTEM_OR_RECONCILED_ON_CHAIN_UPDATE
```
