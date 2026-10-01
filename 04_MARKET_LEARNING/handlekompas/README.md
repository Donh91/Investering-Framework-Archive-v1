# Native Handlekompas

`NATIVE_HANDLEKOMPAS_v1` is a concise, source-call-free readback of the pinned `AUTO_MARKET_STATE_PACKET_v1`.

It emits `NOW`, `PREPARE`, `TOPUP_GATE`, `RISK_DOWN`, `WHY`, `DATA_HEALTH` and `BUDGET_HEALTH`. It binds the source packet SHA and source snapshot commit SHA.

Authority is non-binding: no portfolio execution, canonical-state mutation, threshold/model-weight change, owner switch, proxy promotion or historical rewrite.

Provider quota/rate-limit/token/budget/auth failures are operational health, never market evidence. Exact monthly spend is explicitly unknown unless a bound account-level budget status is supplied. Manual Custom-GPT Data Ping is diagnostic/fallback only; normal predecessor continuity is GitHub-native.


## Direction vs action

Market direction and action permission are separate surfaces.

- `market_direction.directional_state` is descriptive and may be `BULLISH`, `BEARISH`, `NEUTRAL`, `MIXED`, `UNCHANGED_NO_NEW_OBSERVATION` or `UNAVAILABLE`.
- `UNCHANGED_NO_NEW_OBSERVATION` means the owner repeated the same completed price observation; it is a data-time state, not evidence that the market itself is neutral.
- `market_direction.regime` remains descriptive market state; it never mirrors `action.NOW`.
- `action.NOW` remains governed independently and does not inherit direction as execution authority.
- A bearish direction may still map to `HOLD_WAIT`; a bullish direction may still map to `HOLD_WAIT`.
- `NEXT_12H.expected_direction` is derived from descriptive market direction, while `NEXT_12H.action_posture` remains constrained by the governed action layer.

This prevents a descriptive forecast from silently granting BUY/SELL authority.
