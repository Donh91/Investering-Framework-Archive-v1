# GCBLO Full Experiment Artifact Scope

**Status:** RESEARCH_ARTIFACT_BUNDLE  
**Source ZIP SHA-256:** `054d2ef1a49bf03fb22d295a6aca8d165c7ad28c1095db4e7baceab2e770f791`  
**Source PDF SHA-256:** `7291f4e50b8907ccf5da22d41239eeb32c4f27b3231734399d11604f8bfb7edb`

## Directly archived in GitHub

```text
REPORT.md
PACKAGE_FILE_MANIFEST.csv
code/engine.py
code/outcomes.py
code/ablate.py
data/receipts.json
data/kraken_time.json
results/grid_pass.csv
results/sharpe_dist.json
```

These files preserve the method, state machine, outcome tests, ablations, source lineage, blocked lanes, execution clock, zero-pass result and unselected strategy summary.

## Hash-anchored but not duplicated

The large public-source payloads and the full `grid_all.csv` remain identified by exact size and SHA-256 in `PACKAGE_FILE_MANIFEST.csv` and by source URL and retrieval receipt in `data/receipts.json`.

They are not duplicated in this GitHub folder because:

1. the repository already preserves the exact source-package ZIP hash;
2. the raw series are public-source extracts rather than proprietary framework truth;
3. the supplied release has an unresolved cross-environment parity difference;
4. copying large rows into the canonical research archive before PATCH1 would risk treating one disputed output release as authoritative;
5. the narrow PATCH1 must regenerate and freeze the authoritative rows, hashes and dependency environment.

This is an archive-scope decision, not deletion or rejection of the source material.

## Recovery order

```text
1. Read REPORT.md.
2. Verify the original ZIP against its SHA-256 when available.
3. Read PACKAGE_FILE_MANIFEST.csv and data/receipts.json.
4. Recover public inputs using the frozen source URLs and receipt conventions.
5. Run code/engine.py, code/outcomes.py and code/ablate.py in the PATCH1-frozen environment.
6. Compare against PATCH1 reference hashes, never against narrative numbers alone.
```

## Authority boundary

```text
RESEARCH PRESERVATION: YES
RAW SOURCE AUTHORITY: RECEIPT-BOUND
PACKAGED RESULT AUTHORITY: PENDING PATCH1
CANONICAL MARKET STATE: NO
LIVE GCBLO WEIGHT: ZERO
REBUY OR PORTFOLIO ACTION: NO
```
