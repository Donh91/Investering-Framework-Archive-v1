# Bend 2 x Task 2: outcome-integrity proof candidate

Date: 2026-10-19.
Status: **SHADOW_ONLY / BEND_PROOF_NOT_EXECUTED / NO_PRODUCTION_AUTHORITY**.

## Evidence, owner and boundaries

Approved one-off, no-cost research pilot within the **existing** AI stack intake PR #1583, Task 2 #1557/#1596 and Supervisor #1156. It is not a replacement for #1675, current Python property/mutation tests or the existing Codex queue. No new workflows, schedule, model router, credentials, external service, source data, API cost, portfolio action or automatic merge.

- Source: https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1675
- Inspected #1675 HEAD: `700c50e336750726e5d08a2fc77b173652df28cd`. This is a *moving PR*: re-read before any later decisions.
- Relevant inspected #1675 blobs: `scripts/experiments/experiment_lifecycle.py` = `46afeb620d3839a36138c5e1a89adc2d1b9b28f0`; `sensor_relationship_compression.py` = `87010a4a43563f7147d5eb25862dfd2b66420436`.
- Upstream: https://github.com/bendlang/bend ; https://github.com/bendlang/bend/blob/main/guide/GUIDE.md ; syntax example (unofficial): https://bend2.dev/learn/types-as-specifications/
- Backplane: https://github.com/i2cjak/Backplane is an electronics workspace. **Process inspiration only**, not an install/integration candidate.

## Frozen falsifiable claim

Can a Bend 2 `LAWS.bend` + `PROOF.bend` pair prevent a specific abstract error: counting censored/unknown/unbound/unscoreable outcomes as scientifically scoreable, or interpreting any counter as independently validated prospective skill?

`job.bend` models exactly six pre-classified outcome states. Only `BoundMaturedHit` and `BoundMaturedMiss` are scoreable. The seven laws require other states to remain unscoreable and counters not to self-promote scientific validity.

**Crucial trust-boundary limitation:** `BoundMaturedHit` presumes the original frozen forecast/settlement receipt has *already* been checked elsewhere. This toy model does **not** verify actual Python, evidence bytes, source authenticity, settlement prices, timestamps or the mapping from raw outcomes to constructors. A misclassified source can satisfy all laws. Proofs cannot establish investment alpha or independent forecast skill.

## How to verify when a trusted Bend runtime is available

From this directory:

```bash
bend PROOF.bend --verdict
```

Required positive: exact known Bend build, exit 0 and `ALL PROOFS CHECK`. The small BendTT verdict kernel is stronger than the default checker, but parser/translation and source-to-model correspondence remain unproven boundaries.

Negative controls (in disposable copies, **without changing LAWS.bend or PROOF.bend**):
1. Set `case Censored{}: True{}` in `job.bend`. `censored_never_scoreable` must fail.
2. Change `independently_validated_by_counter` to return `True{}`. `no_counter_based_independent_validation` must fail.

Keep byte hashes of the frozen LAWS/proofs, exact compiler commit, stdout/stderr, exit codes, and record observed coverage. A law edited to accommodate a mutant invalidates the test.

**2026-10-19 execution truth:** Bend and Bun are absent in the current sandbox; its host cannot resolve the upstream GitHub domain. Neither Bend proof positive nor its negative controls have been run. **DO NOT claim a mathematical proof.** Do not use upstream `curl | sh` inside framework CI or production; require separate pinned-toolchain/supply-chain assessment before introducing any such runtime.

## Supporting portable sanity tests (executed, NOT a formal proof)

```bash
python -m unittest -v test_shadow_model.py
```

Isolated local Python 3.13.5: **4/4 PASS**, 162 cross-product abstract input combinations, a counter safety check and a mutant example. The Python fixture is a *reduced, separately authored model*, not a production-test receipt and not a parity test of the #1675 source. No claim is made that GitHub Actions executed these tests.

## Evidence standard and next decision

1. Obtain a pinned, trusted Bend binary; verify positive `--verdict` AND both frozen-law mutation failures.
2. Independent review must map each Bend constructor to the exact-current #1675 Python branch/receipt integrity conditions. Demand evidence that all relevant paths are covered.
3. Run a measured baseline comparison with existing Python property and mutation tests. Count *unique failure classes detected* and development/runtime cost. If no marginal benefit, retire Bend.
4. Preserve `AGENTS.md`, repository and recovery safety, public/private boundary, Task 2 frozen research limitations and CI/release rules. No production promotion without separate approval.

Decision now: **HOLD_BEND_VERDICT_UNVERIFIED**. Backplane: **DO_NOT_INSTALL**. Only existing domain owners may advance the study; do not create another owner, supervisor, scheduler or queue.
