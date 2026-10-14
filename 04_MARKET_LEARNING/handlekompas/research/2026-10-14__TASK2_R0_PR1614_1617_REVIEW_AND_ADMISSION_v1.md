# Task 2 · R0 consolidation review and independent-approval gate

**Date:** 2026-10-14. **Class:** `RESEARCH_ONLY_SOURCE_OBJECT_INTEGRITY`. **Branch baseline:** exact original source control-plane main `fe24da3e1d49ab325c007d9b432fc058ff06669a` (refresh before final merge). **Canonical:** `04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_FULL_STACK_NO_HINDSIGHT_AUDIT_WORK_HANDOFF_v1.md`.

## Why consolidation is necessary

- [PR #1614](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1614) is an older **dirty/conflicted** proposal: source census plus a different pinned comparison receipt and dated restricted-metadata research summary. The comparison receipt describes `17` families/`37` refs/`36` paths; the existing `2026-10-14__TASK2_R0_PUBLIC_SOURCE_DRIFT_RECEIPT_v1.json` on main already covers exact `36/36` source paths at its own separately pinned revision. These are two **different historical exact targets**, not two inconsistent proofs.
- [PR #1617](https://github.com/Donh91/Investering-Framework-Archive-v1/pull/1617) is also now dirty; its improved versioned verifier checks original **per-source SHA/type** (not merely top-level root trees), exact immutable target tree, ancestry, namespace/path syntax, shared-path SHA conflicts. It includes a bounded synthetic Git negative-control test suite. User requested a coherent Task 2 without overlapping tools.
- This PR reuses **exact Git blobs** from #1617, not silently rewritten code: `task2_r0_git_object_reconcile_v1_1.mjs` blob `f1fb6331173820a539ecfa688fcc7a4fda264767` and `task2_r0_git_object_reconcile_v1_1.test.mjs` blob `c8c133cb3fd8d463ffc001f418bf539fbf9cf753`. Both have been independently GitHub read back after writing on this new clean branch.
- The old #1614 dated restricted-source metadata (private health 1,043 reported files, 11 legacy capture gaps) remains viewable in that PR until owner decides whether to separately archive a **refreshed** value-free private health receipt. No raw or restricted provider records are transferred. A count from a dated health snapshot does **not** certify individual source first-known.

## Executable verification

On a checked-out repo with **both original historical commits** accessible, run:

```bash
node 04_MARKET_LEARNING/handlekompas/research/2026-10-14__task2_r0_git_object_reconcile_v1_1.test.mjs
node 04_MARKET_LEARNING/handlekompas/research/2026-10-14__task2_r0_git_object_reconcile_v1_1.mjs \
  --inventory 04_MARKET_LEARNING/handlekompas/research/2026-10-13__TASK2_R0_PINNED_PUBLIC_SOURCE_INVENTORY_v1.json \
  --head 05f9daba3a8648c1d7c744fa5665b1014c968639 \
  --expected-tree 8a632948eb8515c023196271a2299259cb8bc607 \
  --repo-dir .
```

The exact historical comparison pins above are **previously archived research inputs**, not values inferred from moving `HEAD`. Do not rewrite original receipt if a newer comparison changes. The reconciler returns exit `0` only when all source paths exist with the original type; `2` on a verified drift with missing/type-mismatch; `1` for invalid or unverifiable arguments/objects. `CHANGED` is source-object drift, not data correctness or market predictive skill. Run the standalone test suite again in CI or an isolated reviewer environment; this discussion is **not** an independent CI-run receipt.

A locally isolated, functionally matching mirror of the proposed Git-object checks was independently re-implemented and executed (Node 22 / Git 2.47) with **10/10 synthetic regression tests PASS** for original SHAs/types, deleted paths, head tree, moving references, ancestry, conflicting refs and unsafe paths. Since the standalone source copied here was not programmatically materialized into that isolated fixture from GitHub bytes, **do not misstate that mirror as proof the exact committed test blob executed in CI**. Exact source-object-copy verification and bounded mirror-test verification are distinct.

## Scientific status and closure policy

**R0 public Git objects:** prior source-drift receipt exists, new verifier under code review. **R1 actual original first-known:** still BLOCKED. **Historical R2–R7 simulations from this work:** `0`. **Independent market family count:** unverified. **Private source values:** not read or published. **Live models/signals/actions:** unchanged.

This addendum is an R0 **execution utility**, not a new canonical source owner, workflow, scheduler or automatic model optimizer. Existing Codex review invocation on old PR #1617 was previously quota-blocked. The 10 local mirror tests and basic GitHub CI do not substitute for an **independent code/source review** if required by the existing research-to-code governance. Request the existing Supervisor or independent reviewer to inspect the exact new head, verify reproducibility and merge only after its own code/data-boundary gates. Then mark old #1614/#1617 superseded **only when no unique evidence is lost**. Do not force-merge either dirty PR.

**Priority after R0 code review:** R1 provider first-known and original issuance/outcome receipts, followed by cheap matched price/volatility baselines; CFGI pre/post 2026-07-08 vendor scoring eras must not be silently pooled. None of the 2025 1h CFGI rows retrieved retrospectively in Aug 2026 is automatically an authenticated 2025 tradable source.
