# GitHub + artifact state

Captured: 2026-08-23
Canonical repo: `Donh91/Investering-Framework-Archive-v1`
Main HEAD at capture: `c637037ddde1c4e1d63c5c89a5b3fb3dbb2c27fd`

## Major historical-lab milestones
- PR #433 — historical altseason lab time-integrity hardening. Merge commit `c65a961ebc8d41530660e714e6164aa4d8531a3d`.
- PR #441 — Intraday Execution Research Layer + Cowork addendum. Squash merge `bd1b1e24177fa999e996cfc211a3aecf609a7e6c`.
- PR #468 — v3 CFGI no-lookahead ASOF alignment and MARKET-only gapfill architecture.
- PR #471 — provider-bounded terminal CFGI v3.1, MARKET historical marked unavailable without proxy/fill. Merge `489a36dad7e2999c0f26be5f161a951897826b08`; finalizer commit `6724e5a5cfa1a814bb18b0798ce2532e4530cff3`.
- PR #472 — durable Cowork bundle receipt. Merge commit `b25e1b0e8e450a004d1cb6f57450591428f40e34`; handoff receipt commit `78269d431a00f9378e92cccce67c61fb54e3aa14`.
- Regression discovered by Opus: free publish commit `4d36966bdaab862a4b5f00318dbadda9c9307118` overwrote later paid/readiness state.
- PR #473 — repaired free-stage publisher so it cannot replace paid/readiness state wholesale; introduced allowlist + terminal lock. Merge `66b3bfd1faa5e2532d45322624057c6812f94a19`. v3.1 was re-finalized no-paid afterward.
- PR #487 — archived Round-2 terminal research decision and future method contract. Merge `f39c520c3b9d7c68bd4536975f0ed70927678173`.

## Current historical research readiness
Canonical file:
`06_RESEARCH_LAB/historical_altseason_pullback_v1/artifacts/RESEARCH_READINESS_MANIFEST.json`

Expected/current contract after repair:
`RESEARCH_READINESS_MANIFEST_v3_1_PROVIDER_BOUNDED`

Key facts:
- readiness: PASS
- blockers: 0
- no-lookahead: true
- alignment: `CFGI_ASOF_1H_NO_LOOKAHEAD_v1`
- BTC usable ASOF slots: 239/242
- ETH usable ASOF slots: 239/242
- MARKET historical availability: `NOT_TESTABLE_PROVIDER_UNAVAILABLE`
- no MARKET proxy/interpolation/fill
- no further paid MARKET retry authorized
- verified cumulative actual CFGI credits before failed MARKET gapfill: 10,518
- conservative cumulative credit upper bound: 13,181
- hard cap: 25,000
- minimum reserve: 50,000

## Cowork input/output artifacts
Historical Cowork input receipt:
`00_ARCHIVE_CONTROL/research_runtime/COWORK_HISTORICAL_ALTSEASON_BUNDLE_RECEIPT.json`

Verified original handoff build:
- workflow run: `32469588890`
- artifact id: `9441991289`
- handoff contract: `COWORK_GITHUB_NATIVE_HANDOFF_MANIFEST_v3_1_PROVIDER_BOUNDED`
- inner handoff SHA-256: `b52c1d2c59a2b555f45d9bcf4de8eb4335dbd2f24c07cc41c2442086097d1267`

Recovered bulk panel used by Round 2:
- file: `alt_hourly_panel.csv.gz`
- source workflow run: `32462841592`
- source artifact id: `9439933916`
- bytes: 49,378,300
- SHA-256: `c55c37aa7038f7cd412267bfb8702ebbaf4eabce8db3a76df244bc25de563118`

## Research result files already in repo
- `06_RESEARCH_LAB/historical_altseason_pullback_v1/ROUND2_TERMINAL_RESEARCH_DECISION.md`
- `06_RESEARCH_LAB/historical_altseason_pullback_v1/FUTURE_RESEARCH_METHOD_CONTRACT.md`

## External Claude output packages
The portable Work ZIP accompanying this GitHub handoff contains the Claude research packages currently available locally:
- Round 1: `HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip`
- Round 2: `ROUND2_CROSS_SECTIONAL_RESEARCH_PACKAGE.zip`

Do not commit these bulky external result ZIPs into the canonical research directory merely for duplication. Treat GitHub as operational source-of-truth and the portable handoff ZIP as transport/archive.