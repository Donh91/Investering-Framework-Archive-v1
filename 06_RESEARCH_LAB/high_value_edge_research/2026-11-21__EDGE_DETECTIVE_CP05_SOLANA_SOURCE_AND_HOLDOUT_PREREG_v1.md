# EDGE DETECTIVE CP05 | Solana source truth correction + frozen public holdout plan

**Date 2026-11-21 Copenhagen. State: PRECOMMITTED_EXPLORATORY_SOURCE_AUDIT, not scientific admission or trade permission.** Existing Archive #1512, Alpha #228 and domain originals retain authority. This document is on PR #2300 review branch, not Archive main.

## A. Root-cause clarification, correcting CP01/CP04 routing

Fresh original Alpha source `architecture/MEME_ALPHA_V4_PROSPECTIVE_CENSUS.md` on current Alpha main, Git blob `0bc9bac2a801b2ddd270207052177936fa087493`, explicitly defines:
> Solana: trending/narrative observation only; **no census, no paper trading**.
The V4 Birth Tape includes Ethereum/BNB/Base via GeckoTerminal new pools and Robinhood Chain via Pons v2 native RPC. Pons owner **MAL #120/#70 specifically owns ROBINHOOD Pons**, NOT Solana Pump.fun. Existing Solana GeckoTerminal/DexScreener rows are *observation-only* data without an independent exact-mint T0 denominator. CP01/CP04 were valid on the observed counts but the prior shorthand suggesting MAL #120/#70 directly establish Solana-native coverage is misleading and must **not** be used as proof of a Solana source.

**Correct source owner decision:** existing original product MAL #228 and source/identity MAL #126/#194 must first approve *a chain-specific, bounded Solana source-admission study* under Archive #1512 before any new Solana launch parser/collector, endpoint, schedule, custody, private rows or downstream trading is considered. The existing MAL V4 Solana observation-only posture is a deliberate scope restriction, not a hidden implementation bug. Any Solana adapter requires separate original owner-controlled, safe source/venue/clock/privacy acceptance; no parallel scanner. Pons #120/#70 remains the Robinhood comparator for *methodology only*, not a Solana producer.

Existing `research/alpha_audit/alpha_pro_parallel_20261109/L03_SOL_IDENTITY.md` (blob `5e3ade447b80eb527f79491ce16e515bdd5dd1b8`) independently warns Solana exact-mint persistence into canonical Case Memory is **PERSISTENCE_BLOCKED**, EVM-only as-of control and privacy checks. Existing `scripts/research/alpha_edge_economic_tournament_v1.py` knows the Solana Base58 *format* but that is not source correctness or executable quote coverage.

**Consequent gating change:** For Solana *do not call the original Pons HOT source check a solved Solana source gap*. An eventual native Solana candidate must have own venue/program version, exact mint/curve/PumpSwap pool, quote-denomination/decimals, original event + first-observed + finalized+decision clocks, source completeness and original #228 approval. Then original economic #98/#77/#85 gates apply at same $100/$500/$1000 source-eligible, buy+sell sizes and matured negative controls. No new source collection is authorized by this docs PR.

## B. Pre-specified second look at public third-party rug labels (NO trade skill)

Previous CP03 used seven 100-row Hugging Face Dataset Viewer blocks (700 launches; 292 rows in selected early+resolved/age-limited sample) at offsets Sep27-Oct31 and *post-hoc* 20% insider / 5 bundle-wallet thresholds. Any analysis further inspecting CP03 same sampled data is IN-SAMPLE and cannot validate its strength. To test *directional stability only*, BEFORE reading any new source rows we pre-register the following:

**Source** `loopholetape/pumpfun-launches`, config `launches`, split `train` (CC BY 4.0). Fetch exactly 100 rows per **offset** `1700000, 1720000, 1740000, 1760000, 1780000, 1800000, 1820000, 1840000, 1850000`, intended later chronological source portion (likely early Nov); do not replace failed offsets after seeing labels. Record actual viewer-observed date ranges, returned row counts and explicit any transport errors. The source's raw revision and Parquet SHA-256 are not available from viewer, so outcome MUST remain `EXPLORATORY_UNPINNED_SOURCE`, not prospective point-in-time. Do not persist individual wallet/mint/creator/private user data in public Archive.

**Row inclusion** `decoder_complete=1`, `quote_asset=sol`, `mayhem=0`, `rugged in {0,1}`, non-null numeric `f10_insider_share,f10_bundle_wallets,dev_share`; if `rugged==1`, require `rug_dt_s>10` as an imperfect temporal negative gate. Distinct mint duplication across fixed blocks to be checked if visible; any result `NULL` remains missing. Only issuer-defined `rugged` labels, no real fraud/no actual exit.

**Predeclared tests**:
1. Compare operational rug-label prevalence when `f10_insider_share>0.20` vs <=0.20, and separately `f10_bundle_wallets>=5` vs <5, as in CP03. Report N/denominator, not just rates.
2. Compare to **simple incipient developer-share risk** `dev_share>0.20` vs <=0.20 to test whether insider>20 offers any incremental discriminative benefit beyond developer concentration; inspect overlap/discordance. In model-free analysis report per-group rug-label rate and **AUC** of `f10_insider_share` vs `dev_share` (same eligible rows), with direction only. AUC gain is NOT proved by point estimate without actor/time clustered prospective proof.
3. The **negative test**: if apparent lift disappears in Nov holdout or equals/underperforms simple developer-share, `REJECT_EXTRA_COMPLEXITY` for the label exercise. If it survives, only `RETAIN_SHADOW_SOURCE_UNVERIFIED`; NEVER promote it to Alpha risk filter or economic trading edge.
4. Keep all true/outcome-missing and early snapshot-missing counts at each filter stage. No Bernoulli p-value or bootstrap from correlated 100-row slices, no equity PnL, no source-replay leakage claim, no fresh thresholds fitted to holdout.
5. Before any official research, the original source owner must acquire and hash-pin full-day files or independently verify original event-time source receipts and rule-definition stability; the viewer result is useful for choosing next experiment ONLY.

**STOP** if external view omits needed columns or revision, mixed genres, no legal source or impossible as-of; leave `SOURCE_UNQUALIFIED` and archive failures.

## C. Reusable detector principle, not a new agent

Existing Alpha `research/alpha_audit/continuous_improvement/AUDIT_TO_EVIDENCE_SKILL_V1.md` already defines Observe->Novelty->Dedup->Hypothesize->Reproduce->owner patch->review->outcome. The high-value EDGE DETECTIVE pattern should remain **one optional specialization of this existing skill**, not its own task/scheduler or duplicate S1. The reusable unique addition is `expected information edge -> economically realizable user decision -> falsification -> STOP/SHADOW/ADMIT`, with verified first-known evidence and full false-rejection opportunity cost, and conditional source acquisition only if the expected value of information beats cost.

**Pre-study verdict**: `SOLANA_NATIVE_CENSUS_NOT_IMPLEMENTED_IN_CURRENT_V4`; `V4_SOLANA_OBSERVATION_ONLY`; `RISK_LABEL_EDGE_UNKNOWN`; `COST-AWARE_EDGE_TEST_BLOCKED`. PR #2300 must pass exact-head native CI and independent review before merge.
