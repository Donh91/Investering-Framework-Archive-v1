# Native Market Recovery

Evaluates the latest pinned Auto Market State hourly. Two consecutive non-PASS observations are required before a bounded re-run of an already-admitted owner is eligible. Cooldowns prevent retry storms (hourly 2h, live-anchor/breadth/sentiment 4h, stablecoin 12h). Related live-anchor lanes are de-duplicated to one dispatch.

Auth/quota/rate-limit/token/budget conditions suppress retries instead of wasting calls. They remain operational health and are surfaced by Native Handlekompas. Missing market data remains missing; no silent substitution or manual user feeding is required.
