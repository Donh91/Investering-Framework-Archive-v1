# EDGE DETECTIVE CP06 | Prespecified holdout source failure and ranked next action

**Date 2026-11-21 Europe/Copenhagen. AUTHORITY RESEARCH_ONLY. Verdict: SOURCE_UNAVAILABLE_FOR_HELDOUT, no inferential result.**
Preceding frozen setup: `2026-11-21__EDGE_DETECTIVE_CP05_SOLANA_SOURCE_AND_HOLDOUT_PREREG_v1.md` on same PR #2300 branch, written before source read. This checkpoint is the adverse-result and decision record, not an implementation job.

## 1. Actual attempted holdout, no hidden replacement

Tool: connected Hugging Face Hub dataset viewer `hub_repo_details(dataset_preview)`, dataset `loopholetape/pumpfun-launches`, config `launches`, split `train`, 100 rows each at exactly these precommitted offsets:
`1700000, 1720000, 1740000, 1760000, 1780000, 1800000, 1820000, 1840000, 1850000`.

**ALL NINE requests returned HTTP 502 Bad Gateway (viewer).** No row tables were retrieved. No alternative offsets selected, no data imputed, no results calculated. `analysed_N=0` means **no available test rows**, NOT zero prevalence, zero discrimination, zero trading edge or a statistical rejection. The preregistered >20% insider / >=5 bundle and simple `dev_share` comparisons remain `NOT_TESTED_SOURCE_OUTAGE`. CP03's earlier 292 selected rows cannot be considered an out-of-sample effect estimate, and no risk model threshold may be adopted.

A second check with connected Hugging Face filesystem `hf_fs ls` verified **file listing** for 40 individual 2026-09-27 to 2026-11-05 `data/launches/YYYY-MM-DD.parquet` files, including Oct15 6,760,066 bytes, Oct22 6,477,633 bytes and Nov05 6,220,699 bytes as reported by Hub. This is **metadata/availability proof only**, not file-byte integrity or ingestion proof. A direct static-file attempt could not establish authorized reachable bytes in the current execution environment; original SHA-256, complete row counts and PIT as-of remained unverified. Do not imply the hosted viewer's outage proves the underlying files disappeared.

No per-row identifiers or third-party wallet values written into the public Archive; no private datasets, customer data, wallet trades or Round 3 evidence touched.

## 2. Additional primary framework truth, discovered in original Alpha source

Alpha `architecture/MEME_ALPHA_V4_PROSPECTIVE_CENSUS.md` on main (Git blob `0bc9bac2a801b2ddd270207052177936fa087493`) says Solana is `trending/narrative observation only; no census, no paper trading`. It is **not** a semantic synonym for Robinhood Pons birth. The current collector `scripts/collectors/prospective_census_v4.py` (Git blob `258132d446d99a1a24c02ae139e911dd47585841`) defines `SOLANA_SHADOW_NETWORKS` and does not include Solana in birth-census `GT_NETWORKS`.

Existing Alpha `research/alpha_audit/alpha_pro_parallel_20261109/L03_SOL_IDENTITY.md` independently reports `PERSISTENCE_BLOCKED` for Solana canonical Case Memory. Alpha #194 and #126 are on-demand exact token and identity original owners; Pons #120/#70 is specifically Robinhood Chain source. The Alpha program `handoff/ALPHA_LAB_PRO_PROGRAM_ORDER_V1.json` is already ordered and marked P009–P012 source, identity, economics, eligible outcome blockers. This is a **source ownership and data-stage mismatch** to address through the originals, not proof that a consumer bug can be solved with one added Solana icon.

Therefore: **do not** insert HF labels into V4 as if they had first-party birth timestamps; do not assume DEX trending rows cover all launches. A future native Solana passive source-admission proposal requires original owner approval to add a source and independently verified event+observation/venue/quote proofs. This docs PR neither authorizes nor implements the change.

## 3. Explicit evidence/value ranking, grounded in blocker order

| Priority | Research opportunity | Next *falsifiable* original-owner action | Kill / hold trigger |
| --- | --- | --- | --- |
| 1 (P0) | Solana source completeness and exact identity, not positive score | Original Alpha #194/#126 + #228 decide if bounded *non-scheduled* first-party Pump.fun protocol/clock/coverage feasibility is worth proposing under #1512; no data or new collector before authority | no independent first-known/full population, unreproducible program/venue versions -> `HOLD_SOURCE` |
| 2 (P0 after source) | $100/$500/$1000 exit-capacity and available free cash on Solana | Original #98 acceptance for Solana native curve->Pool type, exact token/pool/quantity, real execution route receipts; not import EVM GoPlus claims | no 2-way capacity or evidence -> `NOT_IDENTIFIABLE` |
| 3 (P1 after first two) | Insider/bundle/creator risk veto versus simple first-known model | Original #22/#77/#85, independent complete candidates+losers, freeze rules and first-available controls, ensure no post-outcome label features; actual denied winners as opportunity cost | same-cohort after-cost improvement fails / false veto unacceptable -> `REJECT_EXTRA_COMPLEXITY` |
| 4 (P1 after matched outcomes) | Phoenix second leg survivor and wallet independent demand | Existing strategy arena, true spendable cash and all misses; reuse 4 family x 2 arm strategy versions | no utility vs age/liquidity baseline -> `PARK` |
| Park | Wallet-copy generic / 1h dip buy / OPEX | Existing archived negative studies and owner stop, do not reactivate | previous negative controls and lack of action edge |

**Value-of-information principle**: Spending modest deterministic effort to prove first-known, source and sellability is currently more useful than paid AI to optimize a score that cannot produce executable outcomes. This is a **decision priority**, not a numerical return/ROI estimate. Keep one original heavy lane maximum and the already-approved #1512/Alpha queues unchanged.

## 4. What makes EDGE DETECTIVE a durable system without another agent

Re-use the existing Archive `06_RESEARCH_LAB/high_value_edge_research/README.md` CLAIM LADDER, and Alpha `research/alpha_audit/continuous_improvement/AUDIT_TO_EVIDENCE_SKILL_V1.md` twelve-stage pipeline. Add one **case-level detective card**, written to the existing research packet as evidence-only and submitted to original #1512:
- First-observed anomaly and its baseline; independent source/protocol and exact event clock;
- Prize: incremental **after-cost economic decision utility**, not hit rate or peak; include real capacity, missed upside and alternative HOLD;
- Killer test and pre-registered stop threshold before seeing fresh outcomes;
- Original owner, duplicate protection and source contract;
- Data access state `AVAILABLE/UNAVAILABLE/UNAUTHORIZED` with exact byte/clock proof, including negative tool outcomes;
- A compact one-of `REJECT, RETAIN_SHADOW, ELIGIBLE_FOR_ORIGINAL_OWNER_REVIEW` (no independent approval/merge authority).
- Only after original qualified science and accepted consumer, request minimal PR to original code with negative tests and exact-HEAD independent reviewer.

**No new automations, duplicate agents, source queues or scheduled surveillance should be created to 'keep Edge Detective alive'.** A checkpoint has value when it changes a decision or closes uncertainty; mere additional reports are not progress.

## 5. Execution receipt

- `CP05_METHOD_FROZEN_BEFORE_NEW_VIEWER_READ=YES`
- `HUGGINGFACE_HOLDOUT_REQUESTS=9`
- `HUGGINGFACE_HOLDOUT_SUCCESS=0`
- `HUGGINGFACE_VIEWER_HTTP_502=9`
- `HOLDOUT_OUTCOME_ESTIMATE=UNAVAILABLE`
- `REALIZED_EDGE=NOT_DEMONSTRATED`
- `SOURCE_TO_SOLANA_EXECUTION_CHAIN=NOT_QUALIFIED`
- `PR_2300_MAIN_MERGE=NO_AT_DOCUMENT_CREATION`
- `EXISTING_ALPHA_SOURCE_CONTRACT_MODIFIED=NO`
- `PAID_API_USED=NO`
- `REAL_TRADE_OR_BUDGET_AUTHORITY=NONE`

**Main research verdict:** `SOLANA_RISK_FILTER_RETAIN_SHADOW_UNTIL_SOURCE_AND_EXECUTION_PROOF`; `NO_DOCUMENTED_EDGE`; `NEXT_ACTION_ORIGINAL_OWNER_SOLANA_SOURCE_ADMISSION_PRECHECK`. No further viewer retries should be made absent a changed source/provider condition. Do not call this a kill of the underlying hypothesis.
