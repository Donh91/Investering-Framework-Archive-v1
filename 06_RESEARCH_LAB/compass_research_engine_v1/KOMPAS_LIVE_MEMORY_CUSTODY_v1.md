# Kompas Scientific Evolution / live memory custody increment

Original owners #1596 / #1516 / #1827; CRE and existing Challenger A/B remain owners. Owner authorized this increment 2026-11-25. No duplicate forecast engine or scheduler. This PR is offline capture mechanics only; no collection activation, outcome scoring, private data, Round 3 access, promotion or official forecast authority.

Input: exact public data/kompas-live.json bytes from an independently acquired public publication. Verify producer seal (same Python canonical JSON encoding), source authority and clock ordering; retain exact bytes, SHA-256, unavailable/partial statuses, caller-reported observation. Atomic no-replace local storage; duplicate exact packet is idempotent, same clock divergent bytes conflict. No claim that local storage is independently immutable against administrators, no trusted first-known clock, full census or source authenticity from self-seal alone. Do not pass private data or commit captured packets to the public control plane without domain review. This is a candidate for an existing governed archive writer, not a second writer.

Next gated increment: bind independent first-observed publication receipt and full expected-hour census (including missing, partial and unavailable), agree retention and owner; wire into an existing approved delivery lane only after review. Then preregister a future cohort, fixed target UTC, matching source and baseline; use existing Task2/CRE scoring and independent cluster denominators, interval coverage and paired errors, never retrospective enrollment. UI consumes admitted read-only scores only. No Round 3 analyses.

Acceptance: synthetic tests for wrong seal/authority/clock, missing statuses, conflict, idempotency, corruption and unavailable preservation. Native CI and exact-head independent review required. No production release claimed.

Scope correction: keep offline custody code, tests and contract together inside the existing CRE shadow boundary. The native CRE scope guard remains unchanged. This is not the production CN writer.

Local custody limits: observer_reported_at_utc is not tamper-evident in local storage. First write wins, not earliest claimed observation; a divergent same-clock packet is rejected but its bytes are not retained by v1. Do not infer a complete conflict census or first-known time from this archive. No tilted cohort scoring without ROUND3_GOVERNED_ACTIVATION and the existing scientific admission gates. Conflict retention and an authenticated publication receipt remain separate gated work.
