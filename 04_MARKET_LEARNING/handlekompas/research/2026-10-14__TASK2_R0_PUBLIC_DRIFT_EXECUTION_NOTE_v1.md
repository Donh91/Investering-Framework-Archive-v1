# Task 2 — First concrete R0 public-source execution (2026-10-14)

**Stage:** `R0_PUBLIC_GIT_OBJECT_DELTA_COMPLETE__R1_PIT_NOT_ADMITTED`. **Research-only:** no market rule, no action, no automated promotion.

## Exact scope and source

- Frozen initial R0 source inventory: `2026-10-13__TASK2_R0_PINNED_PUBLIC_SOURCE_INVENTORY_v1.json`, initial **main `aea463dc9c5a57fab0e7ef1aa5fc63791158d524`**, initial Git tree **`391aa4154451d1ec49fe3e59db107f21ca1b437f`**.
- Revalidated as-of comparison **main `46c7a167b1d328c9f6a13451d74941a09ceb644b`**, Git root tree **`e347702c38faa3655235af4e75bbad58138cd21a`**, obtained from exact Git commit object, not current moving HEAD.
- [Machine receipt](2026-10-14__TASK2_R0_GIT_SOURCE_DELTA_RECEIPT_v1.json): **17 families / 37 source references / 36 distinct source paths; 16 changed Git objects, 20 unchanged, 0 unresolved, 0 missing**. Strategic/Forward Path shares one underlying directory path and is counted once.
- Real GitHub verification used pinned `git/trees` recursively in 5 untruncated top-level subtrees (03_DAILY_CAPTURE_LOGS 9,770 entries; 04_MARKET_LEARNING 6,745; 05_CYCLE_NAVIGATOR 309; 06_RESEARCH_LAB 637; 07_PROMPTS_AND_AGENTS 323). The `research/` recursive response was **truncated after 53,911 entries**, so four research source blobs were verified **individually** by exact `fetch_file(..., ref=46c7...)`. Do not misreport the truncated tree as fully covered.
- 16 changed objects span capture logs (6 directory trees), Official/Shadow Compass (3), intraday direction outputs (2), pullback summary (1), Action Compass/EDGE/M6 memory (4). **Changed means different Git objects**, not that data worsened, matured, was on time or had a new predictive signal. The unchanged sources are an object-level status at two commits, not a completeness attestation for individual raw events.

## Reproducibility

Repository-local, standalone offline verifier: [`2026-10-14__task2_r0_git_object_census_v1.mjs`](2026-10-14__task2_r0_git_object_census_v1.mjs). It reads the pinned original source inventory, rejects wrong baseline/root tree, duplicate SHA conflicts and path traversal, independently resolves each directory tree/blob with Git plumbing for **both exact pinned SHAs**, and prints deterministic JSON. No API tokens or paid sources needed.

```bash
node 04_MARKET_LEARNING/handlekompas/research/2026-10-14__task2_r0_git_object_census_v1.mjs --self-test
node 04_MARKET_LEARNING/handlekompas/research/2026-10-14__task2_r0_git_object_census_v1.mjs \
  --inventory 04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_R0_PINNED_PUBLIC_SOURCE_INVENTORY_v1.json \
  --baseline aea463dc9c5a57fab0e7ef1aa5fc63791158d524 \
  --current 46c7a167b1d328c9f6a13451d74941a09ceb644b
```

The reproduction checkout must contain both Git commits (fetch explicit object history if not). The independent 7-scenario synthetic Git fixture was exercised locally on a prototype of the verifier during this preparation; **CI/exact committed script self-test and a full local-clone re-run must still be checked before calling the reproducible execution fully independently reviewed**. The receipt itself was collected from actual pinned GitHub object readbacks, not synthesized fixture data.

## Admission and next sequence (strict)

1. **R1 must link actual immutable source objects to provider-first-known and original issuance receipts.** Git commits alone are not provider first-knowledge evidence; retrospective price joins cannot convert censored original outcomes into valid PIT labels.
2. Preserve all **1,140** original Task 1.5 forecast×asset×horizon slots and enumerate missing/censored/abstentions on the original frozen ledger. The prior Task 1.5 cohort includes **824** retrospective spot joins, of which 500 originally censored, 314 originally matured and 10 without original receipt; **all 316 other slots remain part of the original denominator and need explicit census**.
3. Reconcile current M6 typed warnings with independent prospective adverse families; do not backcast native predecessor warnings. Current public gate remains `R1_LIVE_PIT_BLOCKED` and `R2_R7_NOT_EXECUTED`.
4. **First eligible historical test after R1 admission:** frozen CN weekly range/volatility mechanical baseline **on the same originally issued weeks**, or an admitted price-only directional baseline versus the original Compass. Record independent cohort N, widths/coverage, abstentions, missingness, matched original forecasts and holdout. Do not use a 2026 exposed discovery period as unseen data.
5. No new scheduler, API spending, parallel R1 engine, routine Claude Bridge reads or portfolio execution. Private data remains in `Donh91/secrets`, bound through its authorized private evidence receipts only.

## Precise outcome

**Success:** full 36-path public Git-object status at one exact new commit and machine-readable source drift audit. **Not claimed:** completion of private R0, historical first-known/PIT evidence, independent shock-family denominator, R2–R7 performance tests, predictive edge, economic action edge or production readiness. Keep the current gate's BLOCKED values unchanged unless the existing canonical owner later authorizes promotion.
