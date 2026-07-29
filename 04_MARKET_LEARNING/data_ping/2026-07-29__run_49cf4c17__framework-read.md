# DATA PING framework read — run_49cf4c174e254c4ebabb6cf2042109ea

**Snapshot UTC:** 2026-07-29T09:18:00Z  
**Collector status:** PARTIAL, usable for bounded main-framework ingest  
**Predecessor:** `run_b5988607a8f349558a19f78198fdfde2`  
**Primary limitation:** Binance owner/context/final calls failed with GEO_RESTRICTION.

## Framework classification

```yaml
classification: BTC_LED_REPAIR_WITH_IMPROVING_BUT_SUB_GATE_BREADTH_AND_DIRECT_ETHBTC_OWNER_OUTAGE
rotation: NO_ROTATION
ETH_relative_strength: FAILED_PERSISTENCE_REMAINS_ACTIVE_LAST_VALID_OWNER_STATE
selective_large_cap_rotation: NOT_CONFIRMED
broad_alt_rotation: NOT_CONFIRMED
rebuy: LOCKED
new_entry: NOT_ACTIVE
large_caps: WATCH_ONLY
portfolio_action: NONE
canonical_state_change: NONE
```

## Current usable market evidence

```yaml
CoinGecko_BTC: 64378
CoinGecko_ETH: 1916.19
CoinGecko_ETHBTC_derived: 0.0297646712
OKX_BTC: 64419.3
OKX_ETH: 1918.22
BTC_dominance_pct: 56.594852113
ETH_dominance_pct: 10.1243267856
breadth_advance_ratio: 0.4157303371
breadth_advancers: 37
breadth_decliners: 33
breadth_unchanged: 19
breadth_membership_hash: db981da7d5002ac7742419b4bcf7d9c022a5b2ab88165ab971228d587aa6a739
```

BTC and ETH rose approximately 0.9% from the immediately preceding packet. Breadth improved from 37.08% to 41.57%, but remains below the 50% selective and 55% broad rotation gates. BTC dominance also rose. The repair is therefore broader than the previous packet, but still more consistent with BTC-led market improvement than confirmed rotation.

The CoinGecko ETH/BTC ratio is derived diagnostic evidence only. At 0.0297647 it sits below 0.0300, but it cannot score or update the direct gate. The last valid owner adjudication remains the validated first settled close at 0.03007 followed by failed persistence and a live owner value of 0.02982.

## Derivatives boundary

```yaml
OKX_BTC_funding_current: 0.0000386189781703
OKX_ETH_funding_current: -0.0000012355057001
OKX_BTC_OI_usd_change_vs_predecessor_pct: 0.081738
OKX_ETH_OI_usd_change_vs_predecessor_pct: 4.245173
```

OKX ETH open interest expanded while spot prices improved, but Binance funding, OI, taker flow and direct ETH/BTC were unavailable. This is useful as a shadow warning about renewed ETH leverage, not sufficient evidence for a state upgrade.

## Source and gate adjudication

```yaml
Binance_direct_owner: UNAVAILABLE_GEO_RESTRICTION
ETHBTC_direct_gate_score: UNKNOWN
ETHBTC_derived_diagnostic: BELOW_0_0300
previous_valid_owner_state: FIRST_SETTLED_ACCEPTANCE_FAILED_PERSISTENCE
breadth_gate_selective: FAIL
breadth_gate_broad: FAIL
```

Fail-closed rules apply. The direct gate is UNKNOWN for this snapshot. No OKX USD pair or derived ETH/USD divided by BTC/USD ratio may replace Binance spot ETHBTC.

## Prospective evidence adjudication

```yaml
observation_id: OBS-20260729-49cf4c17-BINANCE-OWNER-OUTAGE
policy_family: ROTATION_PERMISSION
new_policy_event: NO
new_A_class_receipt: NO
A_class_increment: 0
A_rows_total: 2
overlap_cluster: ROTATION-2026-W31-ETHBTC-0030-ATTEMPT
reason: SOURCE_OUTAGE_WITHOUT_NEW_DIRECT_GATE_OR_INDEPENDENT_POLICY_DECISION
```

The existing denial remains valid. This packet adds source-resilience and fail-closed evidence but does not create an independent policy event.

## Deep-capture evaluation

```yaml
new_request_required: NO
reason:
  - prior critical settlement gap already resolved
  - current derived diagnostic remains below 0.0300
  - breadth remains below both rotation gates
  - no new Copenhagen settlement boundary is being adjudicated
conditional_retrigger:
  - Binance owner outage persists through next Copenhagen settlement
  - derived or challenger evidence reaches/reclaims 0.0300 while owner remains unavailable
  - breadth crosses 50% and direct gate remains unavailable
```

## Frozen RAW relation

The previously frozen RAW 1–3D and 5–7D forecast remains unchanged. BTC and ETH remain inside its central ranges. The source outage does not justify rewriting the forecast or its `HOLD_AND_DO_NOT_CHASE` translation.
