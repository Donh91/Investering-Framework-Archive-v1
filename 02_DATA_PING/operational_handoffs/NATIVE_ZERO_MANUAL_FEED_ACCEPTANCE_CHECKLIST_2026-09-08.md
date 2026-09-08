# Acceptance checklist — Native zero-manual-feed graduation

Issue: #822
Branch: feat/native-handlekompas-zero-manual-feed-20260908

- [ ] Native Handlekompas contract implemented and deterministic.
- [ ] Generated from latest pinned AUTO_MARKET_STATE/owner evidence, never chat state.
- [ ] Data-health section distinguishes market weakness from machinery degradation.
- [ ] Repeated stale-pointer/readback failures have bounded self-repair/recovery semantics.
- [ ] Ledger/receipt failures fail closed and are never reconstructed after the fact.
- [ ] CFGI/provider auth/quota/rate-limit/token/budget failures are machine-classified where observable.
- [ ] Budget-health output is present even when exact spend is unavailable; UNKNOWN is explicit.
- [ ] Master Monday can surface persistent provider/budget degradation.
- [ ] Existing portfolio authority and thresholds unchanged.
- [ ] Custom GPT Data Ping no longer required for predecessor continuity.
- [ ] Focused tests added.
- [ ] PR CI PASS.
- [ ] Merge to main.
- [ ] Main readback verifies Handlekompas + zero-manual-feed handoff.
