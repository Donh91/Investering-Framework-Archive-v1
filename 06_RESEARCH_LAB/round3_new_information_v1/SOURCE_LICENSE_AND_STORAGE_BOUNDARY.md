# Round 3 source-license and storage boundary

Status: `PRE_COLLECTION_GOVERNANCE_GATE`

The canonical framework repository is public. Round 3 primary sources include provider market data whose current provider terms may restrict redistribution, publication, commercial use, retention or onward availability.

Therefore this programme applies a conservative fail-closed boundary:

1. Raw provider payloads and normalized provider-derived market values are not committed to the public framework repository.
2. Public GitHub may contain collector code, schemas, contracts, hashes, row counts, timestamp ranges, gap/completeness metrics and provider-value-free health receipts.
3. Collection cannot be scheduled until a private storage destination is identified and a provider-specific terms/retention receipt is recorded.
4. A provider terms receipt must state the exact source contract, relevant terms/document version or access agreement, collection purpose, allowed retention, whether internal/private derived storage is permitted, and whether any public aggregate health metadata is permitted.
5. If rights are ambiguous, the source remains `PROSPECTIVE_ONLY_BLOCKED_TERMS` rather than being silently collected.
6. Paid historical acquisition remains separately governed and is not authorized by this freeze.

At freeze time, the accessible GitHub repositories under the linked account were checked and no suitable private repository was available. No raw Round 3 collection is activated by this PR.

This is a storage/governance decision, not a market finding, and cannot be used to alter the four frozen hypotheses or their statistical thresholds.