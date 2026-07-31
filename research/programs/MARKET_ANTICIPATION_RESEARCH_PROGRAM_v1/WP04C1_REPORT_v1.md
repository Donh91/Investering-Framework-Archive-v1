# MAR-WP04C1 — Owner Data Materialization and Hash Registry

## Decision

`COMPLETE_FAIL_CLOSED_PARTIAL_MATERIALIZATION`

The existing Backtest Owner Dataset Registry v1 was located and cross-walked to the frozen WP04B trigger contract. It materially improves dataset identity and package-root lineage, but it remains `DRAFT_FROZEN_PENDING_FINAL_MASTER_BYTE_AUDIT`.

## Material finding

The declared final master `DATA_PING_BACKTEST_HISTORY_PACK_FINAL_20260727T183529Z.zip` still has no repository-visible bytes, byte size or SHA-256. The Claude megapack has a package-root SHA-256, but the WP04C-required member files are not repository-resident and do not have independently available member-level hashes or source-to-normalized parity receipts.

Accordingly:

- package roots are securely referenced where hashes exist;
- required datasets are formally mapped to WP04B sensors;
- no dataset is promoted to replayable owner status;
- historical event enumeration remains locked;
- event counts remain unknown, not zero.

## Unblocking package

The materialization request now specifies the exact artifacts, member files, hashes, schemas, timestamp fields, duplicate policy, settlement replay and parity receipts required to resume WP04C.

## Governance

No trigger change, event enumeration, outcome inspection, forward return, hit rate, drawdown, ranking, framework promotion, portfolio effect or final-holdout access occurred.
