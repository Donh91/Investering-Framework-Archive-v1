# Round 3 source-license and storage boundary

Status: `PRIVATE_DATA_PLANE_BOUND_COLLECTION_HOLD_TERMS_AND_PROVENANCE`

The canonical framework repository is public. Round 3 primary sources include provider market data whose current provider terms may restrict redistribution, publication, commercial use, retention or onward availability.

Therefore this programme applies a conservative fail-closed boundary:

1. Raw provider payloads and normalized provider-derived market values are not committed to the public framework repository.
2. Public GitHub may contain collector code, schemas, contracts, hashes, row counts, timestamp ranges, gap/completeness metrics and provider-value-free health receipts.
3. `Donh91/secrets` is the identified restricted data plane. Collection may be scheduled only for a source explicitly activated by its private source binding, complete applicable-terms evidence and a separately reviewed current activation record.
4. A provider terms receipt must state the exact source contract, relevant terms/document version or access agreement, collection purpose, allowed retention, whether internal/private derived storage is permitted, and whether any public aggregate health metadata is permitted.
5. If rights are ambiguous, the source remains `PROSPECTIVE_ONLY_BLOCKED_TERMS` rather than being silently collected.
6. Paid historical acquisition remains separately governed and is not authorized by this freeze.

The earlier freeze-time statement that no private repository was available is superseded for current routing. The later historical activation receipt and canary remain immutable historical evidence, but they do not describe current authorization. Current collection is paused because the applicable account entity/region, intended-use attestation, retention/derived-processing scope, provider-value-free public aggregate permission and change-control owner are not yet completely evidenced. SC06 additionally requires a persistent runtime and private object/blob storage.

The current private health report distinguishes integrity from analysis eligibility. Eleven existing captures are integrity-valid, but all eleven remain analysis-ineligible because the legacy capture envelope lacks the required schema-v2 collector commit, mapping version and run binding. They are preserved, not backfilled or rewritten. Reactivation requires a separate reviewed pull request, and the first new capture must pass the schema-v2 health gate before any analysis linkage.

Cross-repository bindings and value-free public receipts follow `00_ARCHIVE_CONTROL/CROSS_REPO_DATA_BOUNDARY.md`. Credentials never belong in either repository as ordinary files.

This is a storage/governance decision, not a market finding, and cannot be used to alter the four frozen hypotheses or their statistical thresholds.
