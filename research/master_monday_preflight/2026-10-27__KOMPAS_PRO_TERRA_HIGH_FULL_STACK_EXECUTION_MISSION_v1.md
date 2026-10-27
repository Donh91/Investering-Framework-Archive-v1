# Kompas Pro / Terra 6.1 High / Full-stack execution mission
OWNER AUTHORIZED: 2026-10-27. STATUS: AUDIT AND IMPLEMENTATION HANDOFF, NOT PAID RUN OR MERGE.
Single existing owner route: #1516 forward price, #1593 weekly CN, #1553 Compass protection, #1578 SITE, #1596 Task 2, #1156 S1 release. Do not create new market engine, scheduler, site branch, supervisor or API budget.

## Verified source evidence on current main
- 05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json has target_week 2026-W39, source_week 2026-W38.
- research/cycle_navigator/operational_readback/2026-10-26_W44.json reports STALE, BRIDGE_TARGET_WEEK_MISMATCH, range_values_admitted=false for target W44.
- W44 original CN forecast freeze has BTC weekly 75000-86000, ETH 2150-2550 and valid three day-window scenarios. Distinguish from separate prospective bridge.
- W44 original BTC/ETH seven-day daily_price_path is UNAVAILABLE with zero points. No invented blue Graph B line.
- scripts/cycle_navigator/prospective_range_bridge.py is correctly fail-closed; suspected gap is lack of recurring pre-freeze producer/writer, not bad consumer validation.
- 05_CYCLE_NAVIGATOR/range_baselines/README.md defines an independent shadow benchmark. NEVER feed it into the AI forecast input as if official.
- Official Daily Compass may be DEGRADED, and site/vnext-live/compass-pro-readback.mjs requires valid Official status plus exact source parity before live PRO promotion.

## Terra 6.1 High one-off, advisory only
0. Fresh-read AGENTS.md, latest dashboard/handoff, current exact main SHA, owner contracts, current PR heads/diffs, #1823 high-impact HOLD and #1156 latest billing/routing evidence.
1. Previous Terra MAX/HIGH paid one-shot claims on #1823 are CONSUMED and terminally disabled. NEVER dispatch or retry those jobs. Distinct new Terra High audit permitted only after actual organization billing, unknown transport liability, model access and current runtime/gateway lane have been verified. Enforce lower of actual org cap and repo budget (USD40/month, USD3/call), safe cost reserve, immutable no-repeat claim. Do not treat receipt estimates as provider-billed facts.
2. The main api-agent-gateway-gate.yml live-smoke runs Daily Director, NOT this audit. This mission file does not automatically launch Terra. Use an EXISTING owner-approved controlled API gateway route with gpt-6.1-terra, reasoning_effort high, source-bounded packet, finite output and an actual receipt, or report TERRA_HIGH_DISPATCH_BLOCKED with exact missing precondition. Never launch a new charged attempt just to make a status green.
3. Terra must output a source-bound diagnosis, falsifiable failure matrix, prioritized P0-P3 existing-owner code fixes, test requirements and explicit unknowns. API can advise only, not approve code or merge.

## Mandatory 8-lane source -> decision -> render matrix
Include per row: owner, exact source path+SHA, first-known/time/quote unit, source status and SLA, eligibility, action authority, public projection, effective SITE renderer, chat rendering, tests, root cause, risk severity, original issue/PR.
1. Hourly BTC/ETH capture, flows, ETF, derivatives, breadth, ETH/BTC and source freshness; natural cron streak is not proven by recovery runs.
2. Native, Auto Market State, immutable Official Daily and public projection; Binance BTCUSDT/ETHUSDT is quoted in USDT, do not silently claim USD.
3. Shadow Compass v2 NONBINDING; expose disagreements but no shadow action promotion or same-packet double evidence.
4. Final Master Monday, CN source and target ISO weeks, issue numbers, frozen forecast, score, W39 stale bridge, independent baseline and Task 2 issuance time.
5. Strategic Compass 21-30d and 4-8w, distinguish horizon, uncalibrated scenario weights and missing numeric longer-term forecasts.
6. Pullback 1-5 ordinal, event probability uncalibrated, onset ETA vs review clock, depth, distribution, SELL/Swing, protection, re-entry as separate typed owners.
7. BTC, ETH, large, mid, small, micro and meme separate owner, ETH/BTC breadth survival and altseason; missing ETA explicitly unavailable.
8. SITE premium vs text-only phone-first chat Kompas Pro, Graph B existing owner, actual public JSON/source hashes/CDN parity, DA/EN and 390px.

## Root cause, repair and acceptance, finite phases
A. Diagnose W39 -> W44 bridge mismatch using existing tests/cycle_navigator/test_prospective_range_bridge.py. Check prior W44 complete READY actuals, exact pre-freeze capture/commits, and the existing weekly writer; do not change validator because it correctly rejects W39.
B. If source is eligible, produce a strictly prospective W45 range-bridge within existing #1516/#1593 owner and existing weekly workflow. No W44 rewrite, no new standalone issuer, no independent shadow baseline as model feature. If not eligible, preserve SOURCE_UNAVAILABLE with exact cause.
C. TEST FIRST: negatives for wrong target/source ISO week, late generation, missing or wrong frozen hash, Git ancestry, provenance path, source close/finality, invalid quote, missing sources, after-freeze mutation, range geometry, and private-data leakage. Mutation-test guards in isolation to show these tests detect a disabled guard.
D. Kompas parity negatives: Official DEGRADED with valid CN must not promote live PRO; shadow bullish + Official HOLD_WAIT must not grant BUY; SELL missing and memes missing remain unavailable; ordinal ELEVATED 3/5 is NOT 60% probability; no unsupported ETA, depth, 7-day future price line, stretched 2-3w to 4-8w.
E. Verify identical source/clock yields matching current official action, assets/horizons, degraded reasons across chat and SITE, while Monday freeze remains fixed. Run existing Python/Node suites and 390px DA/EN checks; count executed tests, not unrelated green jobs.
F. Engineer makes smallest scoped code changes in ORIGINAL owner PR/branch whenever active. Do not create review-of-review PRs. Freeze W44 byte exact; keep quote/unit and public/private controls. Test on exact current PR head.
G. Existing #1156 integrator may MERGE after exact diff/head, required CI, actually independent review (Terra self-review is NOT formal independent approval), no open P0/P1/P2, branch protections and security/recovery gate. PR #1823 HIGH_IMPACT remains HOLD until independent Vault/recovery safepoint. Never bypass gates.
H. After merge verify real main blob, next naturally due source run, prospectively frozen CN -> Official/Strategic -> site public JSON -> Pages CDN exact readback. Declare DONE only with consumer receipt, source age and no false COMPLETE on degraded evidence. Score matured predictions under #1596 only after original issuance cutoff, width-penalized baseline and admitted point-in-time data.

## Codex/GitHub Actions delivery
Companion schema-valid candidate at research/codex/intake/2026/10/codex-research-cn-prospective-range-weekly-source-repair-v1.json is code-only and EXPEDITED. On governed merge into main, the pre-existing codex-intake-dispatch.yml push-on-main listener dispatches the existing remediation maturation workflow. That controller alone may declare CODEX_READY. Do not declare code repaired merely because this PR merged; no direct automatic Terra call is wired by the candidate.

## Done criteria
Full source-bound audit (actual Terra High receipt OR exact dispatch blocker), scoped reproducible corrections, mutation-sensitive negative controls, W44 frozen bytes unchanged, verified natural next prospective W45 handoff or documented safe abstention, passed exact-head tests and independent review, governed merge and validated actual Pages main-to-CDN source parity. Keep original owner issues #1516 #1593 #1578 #1553 #1596 #1156, no new queues.
