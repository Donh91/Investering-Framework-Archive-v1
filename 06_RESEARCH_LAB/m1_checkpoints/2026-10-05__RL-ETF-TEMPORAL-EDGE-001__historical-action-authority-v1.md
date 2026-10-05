# M1 Historical Action-Authority Provenance v1

**Mission:** `RL-ETF-TEMPORAL-EDGE-001`  
**Purpose:** Freeze the exact historical action function relevant to the Sep16 A1 episode.  
**Research-only:** yes

## Official Compass binding

Official freeze:
`04_MARKET_LEARNING/handlekompas/official/daily/2026/09/16/CMP-20260916-bf5b03ce2d63.json`

The freeze records:
- issued_at_utc: `2026-09-16T20:37:24Z`
- bound_main_sha: `5b691f66fe5608cd5f5bd8102d5e134003e5171d`
- action_now: `HOLD_DEFENSIVE_WAIT`
- BTC ETF evidence feature: `-450.4m USD`
- WHY: `ETHBTC=0.031550`, `TOP100_BREADTH=0.32`, `ENTRY_SIGNAL=WAIT`

No official daily Compass archive exists for 2026-09-11; the current official daily archive begins on 2026-09-16.

## Exact historical source inspected

Path:
`scripts/data_ping/native_handlekompas.py`

Ref:
`5b691f66fe5608cd5f5bd8102d5e134003e5171d`

Relevant historical `action_context` logic:

```python
healthy = validation != "FAIL" and decision_health == "PASS" and not blockers and _health_ok(auto_state, as_of)
if healthy and entry_state == "GRADUATED_ALTCOIN_TOPUP_ACTIVE":
    now = "GRADUATED_TOPUP_ACTIVE"
elif advance is not None and advance < 0.40:
    now = "HOLD_DEFENSIVE_WAIT"
elif not healthy:
    now = "HOLD_WAIT_DATA_DEGRADED"
elif ratio is not None and ratio > 0.03 and advance is not None and advance >= 0.50:
    now = "PREPARE"
else:
    now = "HOLD_WAIT"
```

The function reads:
- health / blockers
- entry state
- ETH/BTC ratio
- breadth advance ratio

It does not read ETF flow.

Therefore, with all other inputs fixed, deleting the ETF feature from the evidence snapshot cannot change this historical `action_context` output.

## Important limitation

This establishes zero **direct function dependence** of the Sep16 native action on ETF flow.

It does not prove:
- zero indirect upstream influence;
- zero human interpretation effect;
- zero economic opportunity cost of the overall defensive posture;
- zero value of ETF as research context.

Those require separate evidence.
