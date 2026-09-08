# Native Handlekompas implementation note

This feature intentionally sits on top of `AUTO_MARKET_STATE_PACKET_v1` rather than duplicating source acquisition.

The old manual Custom-GPT Data Ping is therefore not reimplemented source-by-source. Native owners remain responsible for acquisition and provenance, Auto Market State remains the normalized pinned aggregate, and Handlekompas is only the concise readback/action-context layer.

Failure handling:
- Pointer hash mismatch -> fail closed.
- Degraded owner lanes -> visible in DATA_HEALTH.
- Provider quota/rate-limit/token/budget signals -> visible in BUDGET_HEALTH and provider health.
- Exact monthly spend unavailable -> explicit UNKNOWN, never fabricated.
- Proxy breadth cannot self-promote to canonical confirmation.
- No portfolio execution or threshold mutation.
