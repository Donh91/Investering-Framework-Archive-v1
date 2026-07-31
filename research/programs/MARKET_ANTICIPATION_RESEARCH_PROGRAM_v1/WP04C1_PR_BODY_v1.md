# MAR-WP04C1 PR summary

Completes owner-data materialization and hash-registry control under parent #209 and WP04C #249.

- Locates and anchors Backtest Owner Dataset Registry v1 at commit `2755175baa4d5cb55f4be990e5265c9486723c78`.
- Creates package-root hash registry and dataset-to-WP04B sensor crosswalk.
- Defines exact artifact-intake, member-hash, schema, timestamp, duplicate, settlement and parity requirements.
- Promotes zero datasets because final-master bytes and member-level hashes remain unavailable.
- Keeps event enumeration, outcomes and final holdout sealed.

Decision: `COMPLETE_FAIL_CLOSED_PARTIAL_MATERIALIZATION`.
