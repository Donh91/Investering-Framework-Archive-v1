# Native Handlekompas

`LATEST.json` is the machine-readable pointer for the latest concise market-state readback.

Source authority remains the pinned `AUTO_MARKET_STATE_PACKET_v1` and its underlying owner evidence. Handlekompas is non-binding and cannot execute trades, change canonical state, mutate market thresholds, or change model weights.

Expected human readback fields:
- `NOW`
- `PREPARE`
- `TOPUP_GATE`
- `RISK_DOWN`
- `WHY`
- `DATA_HEALTH`
- `BUDGET_HEALTH`

`BUDGET_HEALTH` must never invent exact account spend. Provider quota/token/budget exhaustion is surfaced when observable; otherwise exact spend remains explicitly unknown until a bound account-level cost ledger exists.

Manual Custom-GPT Data Ping is diagnostic/fallback only. GitHub-native owner state is the operating predecessor chain.
