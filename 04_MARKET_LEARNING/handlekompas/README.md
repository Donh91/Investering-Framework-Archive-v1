# Native Handlekompas

`NATIVE_HANDLEKOMPAS_v1` is a concise, source-call-free readback of the pinned `AUTO_MARKET_STATE_PACKET_v1`.

It emits `NOW`, `PREPARE`, `TOPUP_GATE`, `RISK_DOWN`, `WHY`, `DATA_HEALTH` and `BUDGET_HEALTH`. It binds the source packet SHA and source snapshot commit SHA.

Authority is non-binding: no portfolio execution, canonical-state mutation, threshold/model-weight change, owner switch, proxy promotion or historical rewrite.

Provider quota/rate-limit/token/budget/auth failures are operational health, never market evidence. Exact monthly spend is explicitly unknown unless a bound account-level budget status is supplied. Manual Custom-GPT Data Ping is diagnostic/fallback only; normal predecessor continuity is GitHub-native.
