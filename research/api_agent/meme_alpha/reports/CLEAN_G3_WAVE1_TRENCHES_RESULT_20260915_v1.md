# CLEAN G3 Wave 1 - Trenches forward-capture result

Date: 2026-09-15  
Status: RESEARCH COMPLETE FOR THIS SUBTEST / NO LIVE PROMOTION  
Workflow run: https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/35017455708  
Artifact: `meme-alpha-trenches-point-in-time-v1`, run artifact ID `10416620785`

## Question

Does a source-captured smart-wallet-like field add incremental value above a point-in-time G2 feature set in an independent August 2026 Pump.fun forward capture?

This is **not** the final clean-G3 economic-return test. The released field is `smart_degen_count`, not a reconstructed AS-OF wallet-quality ledger, and the outcome is `path_completed`, a lifecycle completion label rather than sellable 5x/10x return.

## Data and point-in-time hygiene

- 85,442 first-sighting feature rows.
- 84,584 rows joined to lifecycle labels.
- Published forward split used directly: 50,812 train and 30,059 test rows in the analysis after source filters.
- 525 train and 399 test `path_completed=true` events.
- Test base rate: 1.3274%.
- Reach/X feature family excluded from model inputs.
- `reach_derivable_at_decision=true`: 0 / 85,442 rows.
- 56,593 finite reach read lags had median 20.519s, p95 35.491s, min 15.604s, max 96.578s after the recorded derivability stamp.
- 1,225 rows had negative source age at first sighting, minimum -27.672s. This confirms that observer time and claimed launch age cannot be treated as perfect truth without conservative bounds.
- Curve-progress and market-cap/vault progress proxies were excluded because they can mechanically encode the lifecycle label.

Source-byte SHA-256 pins used by the successful run:

- `features.parquet`: `6abcbaaf85c6da76bcce847bb72893a5aef92f71d043d60267db0618174d8142`
- `labels.parquet`: `65f421fb589cbaf1bf626006f37486a26d2ac219f022f96bcb9690e30c68ecb9`
- `split.json`: `9991b4162c9669e74c48444c34d77b2b5a0daa5545733791743413121c22d68a`

## Forward-test result

| Arm | AP | ROC-AUC | Top 1% precision | Top 1% lift | Top 5% precision | Top 5% lift | Top 5% recall |
|---|---:|---:|---:|---:|---:|---:|---:|
| G2 only | **0.2344** | **0.9130** | **33.00%** | **24.86x** | **16.98%** | **12.79x** | **63.91%** |
| Source-captured G3 only | 0.0696 | 0.6325 | 21.00% | 15.82x | 7.99% | 6.02x | 30.08% |
| G2 + source-captured G3 | 0.2302 | 0.9100 | 32.33% | 24.36x | 16.91% | 12.74x | 63.66% |

## Verdict

`smart_degen_count` contains some lifecycle information by itself, but **did not add incremental value to G2 in this forward split**. Adding it slightly reduced AP, ROC-AUC, top-1% precision, top-5% precision and top-5% recall relative to G2 alone.

This independently supports the current architecture:

1. G2 capital-path / launch microstructure remains the primary early layer.
2. A vendor/source `smart wallet` count is not automatically incremental alpha.
3. The clean-G3 hypothesis remains open because this test did not contain reconstructed point-in-time wallet quality, economic-entity adjustment or sellable return outcomes.
4. Clean G3 must therefore be tested prospectively from actual current-token native buy events plus a separately matured AS-OF prior-wallet ledger.

## Relation to the Ian test

The Ian June cohort and this independent August capture now agree on the important negative conclusion: **raw/source-captured smart-wallet annotations should not be promoted merely because they sound informed.** In Ian, source-captured G3 did not improve the 2x G2 model and only produced a sparse 5x interaction worth further investigation. In Trenches, `smart_degen_count` did not improve G2 for lifecycle completion.

That convergence increases confidence in the governance decision to distinguish:

- raw wallet count,
- source-captured smart labels,
- clean AS-OF wallet quality,
- entity-adjusted clean G3.

Only the last two remain candidates for meaningful incremental authority.

## What this does not prove

- It does not prove that skilled wallets have no edge.
- It does not measure sellable 5x or 10x returns.
- It does not prove that completion/graduation is profitable.
- It does not measure same-funder/controller independence.
- It does not authorize a negative production weight for `smart_degen_count`; the field simply remains non-authoritative.

## Next test

The next decisive experiment is the already specified `PROSPECTIVE_CLEAN_G3_BUYER_GRAPH_SPEC_v1`:

native Pump current-token buys -> self-initiated buyer attribution -> matured prior wallet outcomes available before cutoff -> entity/funder adjustment -> G2 vs clean-G3 ablation -> sellability / liquidity survival / sellable 2x, 5x and 10x outcomes.

RED-COHORT supplies structural cohort definitions and contamination-control lessons. Chain of Title supplies creator/funder/entity decontamination. Neither is allowed to substitute for the prospective economic-return test.
