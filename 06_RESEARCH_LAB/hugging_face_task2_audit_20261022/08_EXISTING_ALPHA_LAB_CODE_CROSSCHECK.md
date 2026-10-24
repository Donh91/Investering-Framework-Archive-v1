# Owner-aware code audit: existing HF Alpha Lab experiment, not a new project
**Date:** 2026-10-22. **Status:** STATIC_READ_ONLY_CODE_REVIEW / NEW RESEARCH OBSERVATIONS. Zero tests executed and no scientific performance rerun claimed. Existing Alpha owner must triage remediations under its own permitted branch/governance. Current GitHub content read from main, not old discussions.

## Established reuse paths in canonical archive
- `research/api_agent/meme_alpha/experiments/trenches_point_in_time_ablation_v1.py` already implements published `Tr4m0ryp/trenches-pumpfun-forward-2026-08` features+labels+split lifecycle ablation. This invalidates any suggestion to build another equivalent HF wrapper.
- `research/api_agent/meme_alpha/experiments/CLEAN_G3_SOURCE_CAPABILITY_MATRIX_v1.json` already defines that source's scope, vendor annotation limitations, field derivability, non-overlapping prior chain trade paths and clean-G3 prerequisites. Existing `research/api_agent/meme_alpha/PUBLIC_ALPHA_HARVEST_EXECUTION_v1_1.json` already prioritizes the source in the Alpha harvest.
- `.github/workflows/meme-alpha-trenches-point-in-time.yml` already exists (PR / workflow_dispatch). Do NOT create a duplicate workflow or manually invoke it during the user's reported October GitHub Actions minutes exhaustion; do not defeat the pause.
- `scripts/research/task2_cfgi_price_expost_4h_v1.py` is already an existing Task 2 ex-post price/CFGI script explicitly described as **NOT scientific PIT / NOT original issued forecasts**. No relabeling its retrospective joins as trading skill. A cheap source QA proposal should connect to its *existing owner*, not replace it.

## Concrete static code findings, ordered by impact
**ALPHA-HF-C1 | P1 | Feature admissibility does not uniformly prove first-known cutoff.**
- The model defines a G2 allowlist, excluding reach/X and obvious curve progress, which is good.
- Nevertheless `age_seconds`, `tweet_age_s`, 24h vendor activity counters and other numeric inputs are selected by column name only. The code's `timing_audit` reports negative token-age statistics and reach lag, but **does not filter/gate G2 samples per field derivability stamp** or exclude negative-age records from model fitting.
- Publisher documents **1,225 negative-age first sightings**, minimum -27.6723s; some source fields may require a more conservative decision clock. Whether this materially changes actual metrics is **UNKNOWN**, requires fixed holdout ablation under existing Alpha owner. No assertion that all G2 features are necessarily invalid.
- **Suggested smallest repair:** audit `decision_ms` vs every allowed feature block's `tau__...` effective/read timestamp, quarantine ambiguous/missing stamps; require negative age conservative-bound sensitivity; record resulting eligible denominator, then rerun same frozen arms.

**ALPHA-HF-C2 | P1/P2 | Test-set-aware feature inclusion.**
- `numericize(panel, G2_FIELDS)` and `numericize(panel, SOURCE_G3_FIELDS)` run on the full merged panel **before** train and test are selected from `split.json`. This selects whether features are usable using test-cohort non-null prevalence/uniqueness. It is unsupervised *test distribution awareness* and should be kept out of a strict forward-only evaluation.
- **Suggested smallest repair:** derive eligible columns, imputers, transformations exclusively on training split and apply frozen choices to test; flag if ranking/average precision or selected columns changes. Existing `Pipeline` correctly fits its imputing/scaling/logistic stages on train, which is good; the upstream selection is the issue.

**ALPHA-HF-C3 | P1 | Source download is mutable on execution.**
- The existing workflow downloads `/resolve/main` source files `features.parquet`, `labels.parquet`, `split.json` and `MANIFEST.json`. It logs resulting SHA-256 but does **not** compare downloaded files with manifest-declared expected digests, nor pin a particular HF revision before execution. Two runs could use different source versions even when each run logs hashes.
- **Suggested smallest repair:** exact HF dataset commit revision + manifest hash verification, fail closed on mismatch, record revision in result receipt and compare pinned source schemas/split to allowed cohort. No broad CI additions before Nov Actions availability.

**ALPHA-HF-C4 | P2 | Output is not economic alpha.**
- Correctly labels `path_completed` as lifecycle graduation, not realizable/sellable 5x/10x returns, and correctly segregates `smart_degen_count` from clean reconstructed wallet intelligence. Treat these as retained safeguards, not as research proof of economic edge. No BUY/NOW or production action.

**ALPHA-HF-C5 | P2 | Split controls should be asserted, not merely assumed.**
- Existing code checks that the in/out sample mint sets exist and runs `validate='one_to_one'` on the merge, but visible code does not explicitly assert `in_sample`, `out_of_sample` and `embargoed` set disjointness, full denominator, known group identity and stable capture cutoff, as a protective run precondition. The author's split may be valid; fail closed if a future upstream revision violates it.
- No file-level attestation of original known publication time or frozen external seed is present. `20260814` seed is author-described, not proof of pre-registered launch selection.

## Practical tests to hand to owner, no duplicate implementation now
1. Training-only feature selection with baseline vs patched columns on identical frozen HF SHA; observe effect on selected features and AP/PR-AUC.
2. Deliberately inject one late G2 `tau__`, negative-age first sighting and an unavailable X block, confirm rejection and exact denominator.
3. Deliberately alter MANIFEST SHA or change `resolve/main` between source files, confirm fail closed.
4. Deliberately overlap train and out_of_sample/embargoed token IDs, confirm gate catches it.
5. Keep explicit `path_completed != sellable_return` failure fixture.
6. If source licensing is noncommercial, keep commercial repurposing blocked without rights review.

## Owner handling
Route a **single bounded intake/delta** to existing Alpha Lab/PUBLIC_ALPHA_HARVEST and its experiment script, not to a new Alpha Lab/Task 2 main owner, not to Work credit-consuming Codex unless separately approved; exact owner PR and latest head review required before applying code. This audit has not shown execution logs/results of the workflow and does not assert success or failure of any live experiment. Zero market authority, zero production wiring.
