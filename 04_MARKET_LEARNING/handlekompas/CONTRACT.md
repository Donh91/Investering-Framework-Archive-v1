# NATIVE_HANDLEKOMPAS_v1

Handlekompas is a concise, non-binding projection of `AUTO_MARKET_STATE_PACKET_v1` for human readback. It cannot introduce evidence absent from the source packet and cannot promote proxy evidence.

Required fields: source binding, NOW, PREPARE, TOPUP_GATE, RISK_DOWN, WHY, DATA_HEALTH, BUDGET_HEALTH, authority, SHA-256.

Hash binding: the emitted packet records the source Auto Market State packet SHA and exact source snapshot commit SHA. The pointer records the emitted Handlekompas SHA and source packet SHA.
