# RED-COHORT v1.1.1 schema / joinability result

Date: 2026-09-15  
Status: RESEARCH COMPLETE FOR SCHEMA PROBE / NO LIVE PROMOTION  
Workflow: https://github.com/Donh91/Investering-Framework-Archive-v1/actions/runs/35018496738  
Artifact ID: `10416702018`

## Provenance

Pinned release: `RED-COHORT-2026-v1_1_1.zip`, Zenodo record `21765387`, DOI `10.5281/zenodo.21765387`.

- bytes: `8,769,673`
- published MD5 verified: `172198eade99f702f1da0bfdd4cf3079`
- observed SHA-256: `f908d10f459e52de0e6f0d77af26db262e41a521dfe3872f30bd795e255841d0`
- catalogue rows: `1,012`
- intra-launch rows: `20,163`

The workflow printed no raw wallet addresses.

## Actual released schema

`sniper_cohorts_intra.jsonl.gz` top-level fields observed across the probe:

- `mint`
- `wallets` (list)
- `tx_sigs` (list)
- `detected_at`
- `first_rank`
- `avg_sol`
- `n_wallets`
- `window_sec`

The field-type probe found `mint` and list members as strings, `detected_at`, `first_rank`, `n_wallets`, `window_sec` as integers, and `avg_sol` as float in the first 5,000 inspected rows.

`sniper_cohorts.jsonl` includes:

- `cohort_id`, `cohort_size`, `wallets`
- `first_seen`, `first_seen_iso`, `last_seen`, `last_seen_iso`
- `n_launches`, `score`, `sol_total`
- `mints_hit[]` with `mint`, `n_wallets`, `first_rank`, `min_time`, `max_time`, `sum_sol`

## Code-level semantics observed

The released detector script references buyer-event fields including `mint`, `wallet`, `buyer_rank`, `blockTime`, `sol_in`, plus cohort fields. The PSM scripts reference launch/outcome fields including `mint`, `created_timestamp`, `buyers_30m`, `sol_30m`, `initial_market_cap_sol` and launch metadata controls.

This matters because the compact intra-launch release is a cohort-hit summary, not a complete per-wallet economic trade tape. It preserves exact mint identity, cohort wallet membership and transaction signatures, while some finer buyer-event variables referenced by the scripts live in the underlying analysis inputs rather than as top-level fields in the compact intra JSONL.

## Joinability verdict

**UPGRADED FROM STRUCTURAL-ONLY TO `STRUCTURAL_G3_WITH_CHAIN_RECONSTRUCTION_PATH`.**

The public release contains enough identity material to support a serious retrospective reconstruction attempt:

1. exact `mint` is present;
2. cohort `wallets` are present;
3. `tx_sigs` are present;
4. `detected_at`, `first_rank` and `window_sec` provide detection/order context;
5. the catalogue retains per-mint `min_time`, `max_time`, `sum_sol` and recurring cohort membership.

The important limitation remains: `avg_sol`/`sum_sol` are aggregates, not a complete proof of each wallet's exact executable entry and exit. Therefore the next retrospective economic test must reconstruct the cohort transactions from the released `tx_sigs` or another chain-native event source, and separately attach post-signal sellability/liquidity/return outcomes.

## What this unlocks

A bounded next experiment can now attempt:

`RED mint + tx_sigs -> chain-native cohort trade reconstruction -> freeze observer signal time -> entity/funder adjustment -> exact-mint post-signal market reconstruction -> sellable 2x/5x/10x + MFE/MAE`

This is substantially better than using the paper's +16.1% downstream buyer-count result as a proxy for investment alpha.

## Hard guardrails

- Cohort recurrence is not insider proof.
- `tx_sigs` make reconstruction possible but do not by themselves establish wallet independence.
- A common funder does not automatically collapse two wallets into one entity.
- Later wallet PnL or later cohort outcomes cannot be used in an earlier historical signal row.
- The published PSM result is buyer-flow evidence, not sellable return evidence.
- The public release intentionally redacts part of one offensive vanity address; that record cannot receive fabricated exact traceability.
- Dataset/code licensing and disclosed patent considerations remain separate questions for any future commercial reimplementation.
- No result from this probe changes BUY_NOW, live thresholds, sizing or execution.

## Decision

**KEEP RED-COHORT as P0 clean-G3 research.**

Run one bounded transaction-reconstruction feasibility study next. If released `tx_sigs` can be deterministically mapped back to the listed cohort wallets and their exact early buys without future information, continue to an economic-outcome join. If not, stop the retrospective economic branch and retain RED-COHORT only for structural feature design while prospective native Pump capture becomes the authoritative clean-G3 path.
