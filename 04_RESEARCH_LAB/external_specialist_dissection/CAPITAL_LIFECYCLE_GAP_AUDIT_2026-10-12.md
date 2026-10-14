# Capital lifecycle, REA fit, and next falsifiable experiment
Date: 2026-10-12
Status: OWNER-ADJACENT RESEARCH AUDIT / NO NEW ENGINE / NOT EDGE VALIDATED
Parent: https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1512
Authority: RESEARCH_ONLY; no portfolio, alert, swap, trading or score authority.

## Sources and observed state

This memo reads current main on 2026-10-12, not a claim that a live new alpha run was performed.
- Canonical queue: `04_RESEARCH_LAB/external_specialist_dissection/QUEUE_V1.json` at blob `ff8aaff5f30ea97c6714c52dde64abc7ad33e7b1`; its active gate is FIRST_FORWARD_PONS_BUYER_QUALITY_CASE_V1.
- REA owner pilot: #1512 comment 6123398768; isolated `rea-agents@6.4.0` CN static attempt failed on host process-ownership prerequisite; no incremental utility established.
- Existing MAL `scripts/wallet_alpha_cohort_replay_v1.py`: bounded transfer observation; explicitly **not** verified market buys, insiders or realizable profit.
- Existing MAL `scripts/forensics_relationship_resolver_v1.py`: infra exclusions and separate relationship/coordination views; common control requires stronger evidence.
- Existing Archive `scripts/api_agent/meme_alpha_pons_early_buyer.py`: Pons token recipient semantics, prospective cutoff, registry time filter and immutable-looking packet hash. Original first-10 membership is only known *after* events.
- Existing Archive `scripts/api_agent/robinhood_wallet_history_completeness_v1.py`: bounded pagination / complete-window gate.
- Existing preregistration `06_RESEARCH_LAB/alpha_lab/2026-10-02__wallet-precursor-execution-fidelity-prospective-experiment-v1__prereg.md`: champion public market visibility versus matched wallet/entity challenger, executable outcomes. **Do not restart or modify this frozen experiment.**
- Open MAL PR #145 already owns one SENDOVER whale/cross-project Etherscan case; PR #146 owns round-1 executable launch study. No parallel heavy implementation.
- REA upstream: https://github.com/morluto/rea ; source-code/browser analysis can reveal observable frontend contracts but cannot independently reconstruct secret backend labels or historical data.
- EVMole upstream: https://github.com/cdump/evmole ; direct EVM bytecode selectors, inferred arguments and storage for unverified contracts. Candidate, not safety proof.
- Heimdall: https://github.com/Jon-Becker/heimdall-rs ; separate decompilation challenger. Candidate, not an oracle.

## Research finding: the missing deliverable is a *joint timeline*, not another scanner

S2 wallet skill, S3 entity-adjusted control, S4 first-N retention, S6 egress, S7 attention, S1 sellability, #1340 prospective denominator and #1419 completeness already cover the underlying primitives. What is not demonstrated by the source audit is **one independently accepted, frozen cross-owner capital lifecycle packet** proving chronology and information advantage *against the simple public/price baseline*. It is a prospective EVIDENCE JOIN requirement, not permission to introduce a new runtime.

Hypothesis H1 (pre-public independent capital): multiple genuinely distinct qualified wallets enter *before* measured public attention and show realizable advantage over same-venue/age/liquidity market-momentum controls.
Falsifier: qualified wallets react after public attention, are same entity/infra, or advantage disappears after realized fees and latency.

Hypothesis H2 (early capital exit): the earliest qualified-wallet group starts measurable net exits/egress ahead of liquidity-adjusted price deterioration, even after benchmark controls.
Falsifier: egress only to internal custody/router, arrives after price declines, or adds no lift beyond volume+price.

Hypothesis H3 (repeatability): wallet/entity behavior repeats across **out-of-sample** launches rather than winning due to one hit, late reputation updates or retrospectively picked winners.
Falsifier: one-hit dominance, historical status leakage, no losers, or unbounded incomplete history.

The H1/H2/H3 decomposition is a proposed analytical lens on existing preregistered owners, NOT a new approved feature, score or production experiment.

## Minimal handoff contract: one case, one cohort, research-only

Join by (chain_id, canonical CA, canonical venue/pool, block, transaction/log index); never join on token name, ticker or screenshot.
Each input needs `source_ref`, `source_observed_at_utc`, `onchain_effective_at`, `available_to_framework_at_utc`, `cutoff_utc`, `completeness`, `source_status`.
For every observation define `eligible_at = max(source_observed_at, available_to_framework_at, applicable registry qualification time)`. A chain event at T0 discovered by the framework at T+30m cannot be credited as a T0 warning.
Carry distinct semantics for TOKEN_RECIPIENT, SELF_INITIATED_BUY_PROVEN, TRANSFER_ONLY, CONTRACT_EXECUTOR, INFRASTRUCTURE, QUALIFIED_WALLET and UNKNOWN. Never recode transfer as buy, whale as insider, probable coordination as common owner, common CEX as entity overlap, or no data as negative evidence.
Pre-cutoff wallet reputation/history only. `COMPLETE_WINDOW` is required for any negative claim about absence of prior trades. Partial/failed pagination => UNKNOWN, not zero.
Unverified destination `CEX_CANDIDATE` is not a realized sale; on-chain routed swaps are not always executable at modeled size. Separate holdings reduction, destination transfer and actual verified exit.
Freeze the public-visibility/price-only champion and challenger at the **same decision clock**. Maintain distinct discovery time, observed signal time, and earliest feasible execution/exit.
Record all eligible launched and unlaunched candidates, losers, expired, rugs, unsellable, source-missing and vetoed rows under existing #1340 owner. No ATH-selected case collection.
Pair with controls matching chain, venue, age, capital/liquidity bands, time window and baseline market momentum. Test wallet-label shuffled, infrastructure-only links, after-attention wallet entry, and false-positive exits.
Outcome: realizable net PnL/MAE, feasible order size, positive lead time, warning precision, incremental PR-AUC or decision utility with bootstrap CI as supported by existing statistics. A perfect retrospective chart or metric without full denominator = no edge.
Do not silently alter current Alpha signal thresholds, CN display, alert bridge, execution policy, queue state, or freeze.

## Eligible first proof gate (no new crawler)

**Gate 0**: Find one *already eligible* post-activation, complete Pons first-10 cohort from existing frozen artifacts. If none: `WAIT_FORWARD_COHORT`; do not backfill a manufactured prospective row.
**Gate 1**: Confirm existing early-buyer packet, Blockscout history receipts, cutoff and original source availability. Missing complete history => `DATA_PENDING`.
**Gate 2**: Use pre-existing S3 relationship resolver, S2 wallet registry, S4 retention and S6 egress outputs where the exact same chain/venue/cohort exist. Missing cross-owner join fields => `SCHEMA_GAP`, document exact mismatch, no new pipeline.
**Gate 3**: At common point-in-time compare established public champion versus challenger on pre-registered matured results. Preserve separate lead/lag timing and sellability; use #1340 owner.
**Gate 4**: A qualified reviewer either records `INCREMENTAL_SUPPORTED` or `NO_INCREMENTAL_VALUE` or `INSUFFICIENT_EVIDENCE`, with case hashes, counts, negative controls and linked receipts. No automatic promotion.

Owner routing: S2 (#101) history and skill; S3 (#105 completed) cluster; S4 Pons capture; S6 exit; S7 attention; #1340 denominator; #1512 cross-lane method. Supervisor coordinates only after all above gate ownership checks. Do not assign duplicate data collection.

## REA and external-tool decision (bounded, cost-conscious)

REA 6.4.0 status: `HOST_CAPABILITY_GATED`, **not** `FAILED_RESEARCH_HYPOTHESIS` or `BENEFICIAL`. The prior host's `ps` failure must not be bypassed by replacing an ownership check with dummy process data.
A compatible host requires both procps and supported Node runtime, clean license/supply-chain review, pinned package, no global/production registration, no sensitive HAR. Run `rea doctor --json` first; allow **one** authorized CN frontend feature, fixed source bytes and existing AST/browser baseline. Promote only an independently verified novel fact of actionable utility. Kill/no-op on no incremental evidence. No recurring retry.
EVMole/Heimdall are **better-matched hypotheses for unverified EVM contract reverse engineering**, but require a separate strict finite cohort trial, not immediate adoption. Freeze contract bytecode hash + verified ABI/ground-truth controls + non-contract/infra controls; report false selector/argument claims, missed relevant behavior, and cost compared with existing Blockscout/raw methods. Static selector extraction does not prove sellability, maliciousness or economic ownership.
REA, EVMole and Heimdall are alternatives for bounded specific questions, not sources of predicted moonshots. Do not consume another research slot or Actions budget until an owner has an eligible question and the heavy lane is free.

## Verdict, 2026-10-12

1. Highest near-term ROI: prove the **first eligible forward Pons cohort** end-to-end under existing owners, not redesign REA or build a new wallet dashboard.
2. Second: when the case has legitimate sufficient data, assess net lead-time and realizable returns of independent wallet convergence before attention; retain negative outcomes.
3. Third: evidence-backed egress and repeatability are potentially powerful but their current source maturity and economic value are UNVERIFIED.
4. REA: hold optional. EVMole: stronger specialized technical candidate, conditional sandbox only.
5. No code, score, trading or production authority changes in this memo. `QUEUE_V1.json` remains authoritative and unchanged.
