# Round 3 source-license and storage boundary

Status: `PRIVATE_DATA_PLANE_BOUND_PARTIAL_COLLECTION_ACTIVE`

The canonical framework repository is public. Round 3 primary sources include provider market data whose current provider terms may restrict redistribution, publication, commercial use, retention or onward availability.

Therefore this programme applies a conservative fail-closed boundary:

1. Raw provider payloads and normalized provider-derived market values are not committed to the public framework repository.
2. Public GitHub may contain collector code, schemas, contracts, hashes, row counts, timestamp ranges, gap/completeness metrics and provider-value-free health receipts.
3. `Donh91/secrets` is the identified restricted data plane. Collection may be scheduled only for a source explicitly activated by its private source binding, terms boundary and activation record.
4. A provider terms receipt must state the exact source contract, relevant terms/document version or access agreement, collection purpose, allowed retention, whether internal/private derived storage is permitted, and whether any public aggregate health metadata is permitted.
5. If rights are ambiguous, the source remains `PROSPECTIVE_ONLY_BLOCKED_TERMS` rather than being silently collected.
6. Paid historical acquisition remains separately governed and is not authorized by this freeze.

The earlier freeze-time statement that no private repository was available is superseded for current routing. SC01, SC03 and SC14 private prospective collection are active. SC06 remains canary-only until a persistent runtime and private object/blob storage are explicitly authorized and commissioned.

Cross-repository bindings and value-free public receipts follow `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`. Credentials never belong in either repository as ordinary files.

This is a storage/governance decision, not a market finding, and cannot be used to alter the four frozen hypotheses or their statistical thresholds.
