# EDGE DETECTIVE CP03 | Solana Pump.fun source-eligibility mini-audit (700 sampled rows)

Date: 2026-11-21 Europe/Copenhagen. **NON-ADMISSIBLE EXPLORATORY CHECKPOINT; NOT EDGE, NOT MODEL CALIBRATION.** No source integration, credentials, private data, paid compute, trading, thresholds, PR merge or market authority. This checkpoint exists to preserve a reproducible research idea and its limitations while the original Alpha Lab data owners mature. No action should use the example figures.

## 1. Frozen public inspection method

Source: Hugging Face `loopholetape/pumpfun-launches`, config `launches` split `train`; published dataset under CC BY 4.0. Provider describes `launches` as post-2026-09-27 decoder period, with **1,853,849** launch rows, **43** columns and known quality caveats; `launches_legacy` remains excluded from primary analytics. Source card: https://huggingface.co/datasets/loopholetape/pumpfun-launches ; provider issues: https://huggingface.co/datasets/loopholetape/pumpfun-launches/blob/main/KNOWN_ISSUES.md .

Read-only hub viewer `hub_repo_details(dataset_preview, config=launches, split=train, limit=100)` was requested at fixed *dataset offsets* `20,000; 220,000; 420,000; 620,000; 820,000; 1,020,000; 1,220,000; 1,420,000; 1,620,000`. Initial responses with parseable 100-row tables at **seven** offsets (all except 620,000 and 1,420,000) totaled **700** rows; they are spread across launch dates **Sep27, Oct01, Oct05, Oct14, Oct18, Oct22, Oct31 2026**. Offset 620,000 returned an actual Hugging Face Dataset Viewer **502 Bad Gateway** on follow-up; offset 1,420,000 returned data later but was **not** added to the frozen seven-bucket analytic set. Never backfill the missing 2 buckets into the reported sample after seeing results. Source repository revision/Parquet bytes and the 700 underlying row hashes were **not pinned or downloaded**; the hosted viewer can change, so the numbers are exploratory transparency targets and **not independently reproducible audited outputs**. The visible viewer prints only first 30 of 43 fields; `f10_age` and complete source first-known/quote receipts are not visible in this mini-audit.

Parser: tables had one row per 100-row viewer block; Markdown `|` columns were counted and validated before extracting `decoder_complete, quote_asset, mayhem, rugged, rug_dt_s, f10_insider_share, f10_bundle_wallets`. No raw creator/wallet/mint rows stored in Archive.

**Eligibility for this *descriptive* mini-audit only**:
- post-decoder `decoder_complete=1`; SOL-quoted `quote_asset=sol`; classic mode `mayhem=0`;
- `rugged` must be explicitly 0 or 1 (null != 0);
- `f10_insider_share` and `f10_bundle_wallets` are present (the dataset provider says such snapshots refer to the first 0–10 s);
- if source reports rug timestamp, exclude cases with `rug_dt_s <= 10s` because the prospective feature could already be post-event; preserve `UNKNOWN` if field missing or semantics ambiguous.

This does NOT prove legal source availability at 0–10 s, microsecond ordering, trade quote reachability, independent wallet ownership, or an economic decision before the rug. All these remain source-admission gates.

## 2. Measured at this limited viewer grain

- Seven preview blocks returned **700** rows.
- All 700 were marked `decoder_complete=1`; **575** were SOL-quoted; **183** were mayhem; **402** were both SOL-quoted and classic after decoder gate.
- Of 402, **396** had non-null `rugged` label; issuer's operational `rugged=1` applied in **274/396 = 69.19%** of this selected subset. This is NOT real-world fraud prevalence and is not a cash-loss measure.
- After requiring early insider/bundle features, explicit outcome and excluding potentially already-rugged within first 10 seconds as above, **292** rows remained.
- Heuristic post-inspection group, first snapshot `f10_insider_share >0.20`: **66/75 = 88.00%** eventually marked rugged.
- Group `f10_insider_share <=0.20`: **118/217 = 54.38%** eventually marked rugged.
- For `f10_bundle_wallets >=5`: **35/41 = 85.37%** labelled rugged; for `<5`: **149/251 = 59.36%**.
- Absolute 20%-insider split risk-label difference is about **+33.62 percentage points**; this is a **selected exploratory association**, not a calibrated risk model, inferential confidence interval or incremental edge.

These two splits reuse the *same 292 rows* and are correlated, not independent discoveries. Other feature thresholds were not comprehensively tried here; the displayed 20% / 5-wallet heuristics were chosen during exploration, not frozen before data access. No p-value or effect-size significance is claimable from contiguous viewer blocks, launch-time dependence, post-event label semantics and upstream missingness.

## 3. Why this is NOT an economic edge

1. **Selection and population:** early snapshots exist on 81.6% of provider's larger corpus but selection is non-random. Source's own `KNOWN_ISSUES.md` reports different rug rates for sampled/unsampled launches. Our 292 are a much smaller further-selected convenience sample and not the original Alpha Lab eligible opportunity universe.
2. **Label leakage / construct coupling:** the operational `rugged` label partly uses developer sell/drop mechanics; high insider holdings can be mechanically related to future creator sales. An association with a label partly defined by issuer behavior is NOT proof of future real liquidity loss, and apparent predictive signal may duplicate simpler developer-share or liquidity baselines.
3. **As-of unknown:** exact network capture timestamp, original event units, feature admission and original alpha candidate first-observed clock are not verified. The preview omits `f10_age` and detailed proofs. Retrospective creator information should not be silently inserted as pre-decision evidence.
4. **Capacity/exit absent:** no $100/$500/$1,000 buy/full-exit quotes, priority fee, failure-to-fill, latency, migration phase, free cash or false-veto opportunity cost. "Avoiding rugged labels" is not equivalent to avoiding executable losses.
5. **Source version:** Hub viewer lacks an immutable downloaded raw source digest and independent checksum readback. A provider 502 blocked two fixed preview offsets initially; absence was preserved instead of imputed.
6. **Multiplicity, timing and dependence:** contiguous sampled rows within 100-item slices, clustered days and unknown launch/funder entity repetition destroy IID assumptions; bootstrap or p-values on raw rows would overstate confidence.

## 4. Minimum meaningful next source-admission action, routed to originals

- Keep this as a lead under existing MAL original Smart Filter/issuer #154, prospectively joined to first-known #120/#70, exact identity #194/#126, trade/exit mechanics #98, outcome #77/#85 and Archive #1512, not a new data-feed owner.
- Next check should be **single-day**, **source-revision-pinned** Parquet scope with original decoded SOL-quoted classic launches and **all** early sampled/unsampled statuses, an independently reconciled public-chain source and **true as-of** feature timestamp. Assert absence of post-rug/migration inputs. Test simple dev/curve liquidity baseline vs incremental insider/funding features **on the same eligible cohort**, with day/creator/funder clusters and chronological untouched holdout.
- Admit only if the original source custodian can prove publication terms, provider integrity and event-clock availability and the existing Alpha engine proves quote capacity and realistic fees. Source audit alone cannot change canonical Alpha models.
- Stop or reject the use of the public corpus for live decision if first-known events or spendable price/exit truth cannot be reconstructed; do not purchase paid HF compute or vendor data from this exploratory note.

**CP03 disposition:** `DESCRIPTIVE_ASSOCIATION_VISIBLE` and `POTENTIAL_RISK_CONTEXT`, but `INCREMENTAL_INFORMATION_EDGE_UNPROVEN`, `TRADING_EDGE_NOT_TESTED`, `SOURCE_ATTESTATION_MISSING`. Preserve nulls, unobserved launch opportunities, reviewer dissent and native source authority. This checkpoint is a PR #2300 research-note artifact only until independent exact-head review/CI and original S1 release routing.
