# Phase 3 | Task 2: HF as a no-hindsight external benchmark source

**Mission:** existing COMPASS-HORIZON-EDGE-20261011 R0–R7. **Authority:** RESEARCH_ONLY. Existing Task 2 handoff owns source admission; EDGE #1530, Compass action #1553, Task1.5 #1596 retain their roles. This note adds source candidates and failure tests, not another experiment owner, scheduler, forecast framework or new threshold.

## Current repo status observed 2026-10-22
- PR #1573 (original Task 2) MERGED.
- PR #1597 historical forecast audit MERGED.
- PR #1617 source SHA verification patch CLOSED, NOT MERGED. Do not treat old PR body as current problem proof: inspect subsequent main for same defect/fix.
- PR #1675 censor-aware counts and fail-closed lifecycle MERGED (merge SHA f5f11ddeac4d01248209140efac6bb5cab43d364).
- PR #1683 Master Monday handoff integrity MERGED; separate system, don't recompute its status from chat.
- Dated gate `2026-10-13__TASK2_FULL_STACK_AUDIT_EXECUTION_GATE_v1.json` includes R0/public preflight, synthetic negative controls and historic R1 blocked. It is NOT a fresh readback of all admissibility after later PRs.
- Exact audited main branch HEAD at one preflight: b4a644faa5893bc7f33d87834d7a74a0639371dc, 2026-10-22T16:23:58Z. Re-read this on actual execution.

## R0: external source census, no source invention
For each source/series, freeze HF repo revision, blob/file SHA, split, record grain, UTC and timezone, market instrument identity, venue, publication time, historical earliest *available* snapshot proof (not only economic bar timestamp), provider source, completeness and expected cost. Use the owner's existing inventory and receipt format.

Do not conflate the dataset's **event_ts** (when an event occurred), **publish_ts** (claimed first published), **first_known_at** (our observer accepted), **ingest_ts** (later library upload), **retrieval_ts**, and **label/outcome cutoff**. Retrospective uploaded bars lack evidence of historical delivery to our system.

## R1: PIT source admissibility
For original forecast i with issue cutoff t_i:
1. Read original immutable issued forecast ID, horizon, target, issue-clock receipt, model and relevant source SHA.
2. Establish source first-known `s_i`, verify `s_i <= t_i`. Absence -> `UNKNOWN_SOURCE_TIMING`, not proof of knowledge.
3. Establish benchmark availability by decision cutoff. OHLCV `open_time <= t_i` is insufficient if that bar's `close_time > t_i`.
4. Bind labels to original outcome process, keep every censored, unknown, missing, abstained, mature and rejected record in denominator.
5. Detect split/conversion drift, time-zone errors, overlapping horizons, market venue mismatch, synthetic vs observed clock, revised metadata and event family dependence.
6. Fail closed for any original first-known/custody failure. HF revision SHA verifies today's stored file, not necessarily historical publish state.

Negative controls: deliberately inject future close within live candle, scrambled timestamps, missing original forecast, after-target received label, synthetic source flag, duplicate cluster, late provider revision and defunct symbol. Every leak must be rejected. Prove tests fail when guards are removed.

## R2: mechanical benchmarks ONLY after R1 eligible cohort
- Naive no-change, random/no-signal, prior-return momentum, ATR range with frozen window, prior-week high/low, ETH/BTC same-clock relative strength, cash/HOLD/WAIT action; exact baseline depends on pre-registered owner's domain.
- Publish all events, class base rates, coverage, calibration, MAE/MFE, Brier/log loss when suitable, WIS/Winkler for intervals, net return utility after costs/fees/slippage and false-exit/missed-upside penalties.
- For market regime/rotation, require pre-registered event definitions, asset universe as-of, all delistings and broad participation criteria before metric selection.
- Prefer matched issued forecasts, same clock/venue/horizon rather than anecdotal cherry-picking. Cluster overlapping events into independent families.
- No evaluation that uses HF model trained on the test window without embargo/walk-forward separation.

## R3–R7 conditional path
R3 source ablation: does HF external context add value after independent cheap benchmarks? R4 adversarial challenge: leakage, false alarm, undercoverage, regime change, survivorship and spoofed news. R5 action utility: holder vs cash investor, execution latency and portfolio privacy boundary. R6 site/Kompas/CN projection: all identical eligible frozen evidence; source research must not feed current site/Kompas. R7 owner-governed outcome memory, negative result and retirement decision.

### Exit criteria / metrics for pilot acceptance
- Per-provider licensed usable data, exact pinned revision, full denominator and failure-aware schema, no future feature leakage.
- Reproducible join audit with missingness and sufficient independent market families; threshold/N taken from existing owner protocol, NOT invented here.
- Failing negative controls and verified acceptance receipts.
- Material positive decision divergence under walk-forward validation relative to cheapest baseline (or honest null/negative conclusion).
- Only owner may authorize R2+ after R1 source eligibility. Zero promotional claims before that gate.

## First-pass bounded experiments
**T2-HF-PILOT-A:** Read only 2 instruments/small exact-window OHLCV from HF-001, report 15-minute bar custody and completeness versus original issue clocks without scoring. **T2-HF-PILOT-B:** HF-004 `markets` + `prices` only; filter resolution=-1, missing fee and late market creation; compare probability calibration in research lane. **T2-HF-PILOT-C:** HF-009 news timestamp/URL dedup against a sample of already archived Situation Room events, retaining published vs first-known separation.

All pilots require existing owner signoff, pinned inputs, controlled execution location. This packet authorizes only data discovery and publication of source metadata.

## Avoid acting on GitHub Actions outage
This research does not restart existing collectors or substitute HF for scheduled Actions. On the user's reported exhausted October GitHub minutes, keep research read-only and avoid large CI/Action runs; evaluate production health separately through the existing Supervisor. No fake machine uptime or re-created source timestamps.
