# KOMPAS PRO | Terra 6.1 High, source-to-site audit and bounded repair mission

**Date:** 2026-10-27 (Europe/Copenhagen)  
**State:** AUDIT CONFIRMED, ENGINEERING/PRODUCTION FIX NOT YET EXECUTED  
**PR type:** ONE existing-owner execution branch, **draft until actual code, tests, review and production evidence**. Do not merge this briefing alone as if the repair is complete.  
**Model request:** OpenAI API `gpt-6.1-terra`, `reasoning_effort=high`, only after runtime and budget-gate verification. NOT Max.  
**Scope/owners:** Forward Path #1516 (single forecast/source issuer), Master Monday/CN #1593 (weekly producer), Site #1578 (consumer), Task 2 #1596 (scientific analysis), Compass protection #1553, Supervisor #1156 (release). No new issuer, scheduler, supervisor, PR hierarchy or automatic trading authority.

## 1. Verified issue and key nuance

1. Current W44 CN issue is **internal #32 / public #31**, pointer `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json` status `DEGRADED` / `COVERAGE_LIMITATION`, with verified consumer receipt. The immutable `05_CYCLE_NAVIGATOR/weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json` contains BTC 75,000–86,000 and ETH 2,150–2,550 **analytical published-source weekly bands**, plus Day 1–2, Day 3–4, Day 5–7 narrative bands. Do not retroactively change them.
2. `05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json` is a **continuity bridge for 2026-W39** from completed W38. `scripts/cycle_navigator/prospective_range_bridge.py::load_bridge` correctly returns `STALE/BRIDGE_TARGET_WEEK_MISMATCH` for W44, no range values admitted. This is a **missing recurring prospective source handoff**, not a reason to disable the validator, substitute the independent deterministic baseline, manufacture a W44 bridge or rewrite an issued freeze. Independently verified readback: `research/cycle_navigator/operational_readback/2026-10-26_W44.json`.
3. The weekly publication workflow separately issues `05_CYCLE_NAVIGATOR/range_baselines/forecasts/YYYY/Wxx.json`. This is an **independent prospective SHADOW BENCHMARK**, not the missing official source. See `05_CYCLE_NAVIGATOR/range_baselines/README.md` and the workflow's independence checks.
4. The Official daily Compass latest at audit was `CMP-20261027-2178a2d6c0d4`, issued `2026-10-27T21:32:10Z`, with `data_status=DEGRADED` and `action_now=HOLD_WAIT`; 1–3d, 5–7d, 2–3w are MIXED, 12h direction UNAVAILABLE, 4–8w cycle direction UNAVAILABLE. The `evidence_snapshot.mapping_integrity_status=FAIL_PASS_LANE_MISSING_VALUE` for `altseason_score_90d` (freshness PASS but actual value missing). This is separate from Hourly capture COMPLETE and Native `DATA_HEALTH.status=PASS` with optional catalyst degradation. Do not conflate their status semantics.
5. Pullback risk is under source state `ELEVATED` with `confidence_quality=LOW`, no typed onset window or drawdown depth; current OFFICIAL SELL assessment `UNAVAILABLE`, distribution `UNKNOWN`, re-entry `INACTIVE`. `3/5` is an ordinal display class only, NOT 60% event likelihood and never a SELL authorization.
6. `05_CYCLE_NAVIGATOR/site/vnext-live/compass-pro-readback.mjs` currently requires source `data_status=OK`, `view.compass.state=FRESH`, aligned weekly context and permitted live gates, else returns UNAVAILABLE. Its strict fail-closed policy must be kept unless an **existing approved contract explicitly authorizes safe partial/degraded presentation**. Do not secretly transform DEGRADED into OK or supply a false trade signal.
7. W44 `forecast_freeze.daily_price_path.BTC/ETH.points=[]`, status UNAVAILABLE. Therefore Graph B's seven-day predicted-close blue line is legitimately absent; do not synthesize expected closes from weekly midpoints, outcomes or the benchmark.
8. Relevant action route: `AGENTS.md` latest owner override, `07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json`. Two three-column tables, pullback category/evidence quality, weekly frozen source bands, separate SELL/Swing/re-entry, source age and explicit independent interpretation; TEXT ONLY in chat. Do not confuse Official bull/bear evidence 5/5 with frozen CN 4/6 for W44: they have different owners and issuance times.

## 2. Detailed Terra High forensic questions, MUST prove or falsify

A. Trace full exact SHA/clock/source authority: autonomous capture -> Auto Market State -> Native Compass -> immutable Official Compass -> Master Monday -> frozen CN -> prospective bridge -> public projection -> site builder -> GitHub Pages CDN. Map producer status vs consumer status, ownership, first-known and freeze-before-outcome, not simply green CI.

B. Verify whether recurring source-bound **prospective range issuance** already exists elsewhere under #1516 or has been deliberately withheld for provenance/quote-basis reasons. Before any change, re-read #1516, #1593, #1578, #1596, #1156, current main, PR #1823, their latest receipts, and the direct producers. Clearly distinguish (i) valid current CN analytical ranges, (ii) independent shadow baseline, (iii) optional historical W39 bridge, (iv) genuine prospective range issuer, (v) 12h/72h/7d/21d or 4–8w conditional paths. If issuer does not exist, **do not relabel** an existing series as issuer.

C. Scope smallest safe repair to **existing owner**: a recurring pre-publication, exact-week, source-bound W45+ producer/consumer path when admissible; or documented SOURCE_UNAVAILABLE when provenance is insufficient. Preserve separation between native Binance BTC/USDT (not USD) and ETH quotes, no assumed 1:1 exchange rate, no unobserved timestamps, no backfill as prospective. Ensure forecast week and hash/commit/time gates before accepting any bridge. W44 must stay frozen.

D. Check why Official feature `altseason_score_90d` may show PASS freshness but MISSING value. Trace source QA/mapping and consumer presentation separately. A repair must preserve UNKNOWN and cannot silently populate numeric value, reweight action rules, or claim new altseason confirmation. Distinguish actionable source defect vs correctly missing optional provider data.

E. Audit full Kompas Pro parity, including BTC, ETH, large, mid, small, micro, memes, 0–12h/24h, 1–3d, 5–7d, 2–3w, 21–30d, 4–8w. Confirm that Official action remains `HOLD_WAIT`, Native/Shadow/Strategic remain separately attributed, microcaps `HARD_WAIT`, memes without a decision owner remain UNAVAILABLE; no shadow promotion, no manufactured ETA/price path, and no SELL from Protection. Check site path + official GitHub Pages/CDN, DA/EN, 390/430px and desktop; test stale/wrong-week/null/changed hash. Site may present source-specific valid facts alongside clearly labeled degraded status **only if current canonical rules permit**; otherwise keep true unavailable.

F. Audit actual opportunity for incremental investor utility: benchmark relative to always WAIT / hold, false alarms, missed retests, forecast range width and prior public 100%-containment not proving economic edge. Task 2 / #1596 owns scientific admission and holdouts. No prospective forecast claimed by retrospective performance.

G. Audit forecast publication no-new-points case in Graph B. If trustworthy independent seven future closes are NOT issued, retain blank blue line and expected_close=UNAVAILABLE, even if analytical weekly bands exist. Never infer a market turn from a chart design.

## 3. Execution chain, one PR not an infinite review loop

**R0, before paid call:** compare newest main SHA, PR #1823 (model-current routing release remains HOLD until independent Vault/recovery safepoint), original issue owners and exact sources. Check `gpt-6.1-terra` actual API account/model availability, structured outputs and high effort. Existing owner-authorized Terra Max trials on #1823 are CONSUMED/TERMINALLY DISABLED: DO NOT dispatch or retry Max, especially after unknown-cost `RemoteDisconnected`. Maintain current gateway $40 monthly and $3 per-call hard stops, independently verify remaining budget; do not silently raise caps. A draft PR or text instruction is NOT proof a paid API ran.

**R1, Terra High API forensic audit:** Supply this mission and compact immutable evidence manifest through an EXISTING approved one-time, read-only API route (or route verified as approved by existing API owner). Output exact trace table, P0/P1/P2 classifications, reproduction, causal confidence, smallest patch boundaries, falsifiers, positive and negative tests, suggested implementation owner, expected decision value, cost and STOP cases. Include `MODEL_USED=gpt-6.1-terra; REASONING_EFFORT=high` in the actual gateway receipt, not in a fabricated assistant claim. Terra is advisory. No API-generated auto-merge or source-state promotion.

**R2, actual code remediation on THIS PR BRANCH by existing approved code executor:** Implement only P0/P1 proven, code-remediable changes. Use bounded patches in existing CN source/weekly/site/compass code plus tests. If investigation finds no safe issuer because source receipts do not exist, do NOT manufacture ranges: implement missingness/diagnostics or clean NOOP and document remaining owner gate. No second implementation PR unless safety-relevant repo separation forces it.

**R3, regression/adversarial:** Tests must run on actual code and fail on intentionally disabled guards. Prove:
- W39 bridge rejected for W44/W45; no foreign week or mutable latest-path substitution.
- Provenance SHA/commit tampering, late-issued bridge, unfinished prior week, missing raw source, wrong quote currency, and post-freeze generated bridge all fail closed with zero admitted values.
- W44 frozen weekly/intraday ranges unchanged byte-for-byte; baseline remains shadow-only and never becomes LLM input.
- True current eligible source routes to the single intended consumer, wrong-week source does not; site/Compass cross-check same snapshot with explicit as-of clocks.
- `data_status=DEGRADED`, freshness stale, missing `altseason_score_90d` and native PASS/official DEGRADED mismatch never become false healthy/BUY/SELL.
- `ELEVATED` maps to ordinal 3/5 with LOW evidence quality but no numeric chance, event clock or drawdown; SELL UNAVAILABLE and re-entry INACTIVE preserved.
- No 7d expected-close blue Graph B line when `daily_price_path.points=[]`.
- DA/EN/mobiles 390/430 and desktop plus Pages CDN source/byte readback, with clear staged status if physical Safari not available.

**R4, one exact-head independent review and safe merge:** Only after actual implementation, focused and broader CI, quality negatives and mutation tests, independent technical review, governance safety/recovery confirmation, exact current head and explicit user-authorized existing integrator. Resolve concrete P0/P1 defects on SAME PR rather than spawning PRs. Never forge formal APPROVED from an API review; GitHub branch protections remain binding. After merge verify main blobs, natural production producer/consumer receipt, public site/CDN parity and closure owner. If weekly opportunity has already passed, test **next actual prospectively eligible week**, never W44 retroactive correction.

## 4. Non-negotiable authority and stopping gates

- NEVER rewrite W44 frozen forecasts, historical precision, official forecast/outcome records, source timestamps or Task 2 evidence.
- NEVER create a new forecast engine, agent scheduler, hourly watcher, standing API charge, task owner or third-party deployment.
- NO credential/private raw data in public GitHub; no Round 3 analysis or trading execution.
- NO market thresholds/weights, native BUY/SELL semantics or official eligibility weakening to make a test green.
- Existing required GitHub protections, separated independent recovery, and exact-head integrated release remain binding.
- If source cannot prove prospective authority: `SOURCE_UNAVAILABLE`. If no new code defect: `NO_CODE_CHANGE_JUSTIFIED`, then close mission as an honest gated outcome, not a green completion.
- Final release decision must state the actual model receipt, code diff, test outputs, CI conclusion, review findings, merge SHA and live readback. A documentation PR alone is NOT DONE.

## 5. Initial source evidence identifiers at audit

- Main SHA at authoring: `8b449cdc34c7de0e723fbf54a02c552a2602be67`. Refresh before execution.
- W44 CN pointer `05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json`, freeze `05_CYCLE_NAVIGATOR/weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json`.
- Historical bridge `05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json`, target `2026-W39`.
- Independent readback `research/cycle_navigator/operational_readback/2026-10-26_W44.json`: `STALE`, `BRIDGE_TARGET_WEEK_MISMATCH`, `range_values_admitted=false`.
- Official `04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json`, audit ID `CMP-20261027-2178a2d6c0d4`, status `DEGRADED`; target `official/daily/2026/10/27/CMP-20261027-2178a2d6c0d4.json`.
- Native `04_MARKET_LEARNING/handlekompas/LATEST.json`, strategic `04_MARKET_LEARNING/handlekompas/strategic/LATEST_STRATEGIC_COMPASS.json`, shadow `04_MARKET_LEARNING/handlekompas/shadow_v2/LATEST.json`.
- Hourly `03_DAILY_CAPTURE_LOGS/hourly/LATEST.json`: at audit window_end `2026-10-27T21:00:00Z` / 26h COMPLETE; later freshness requires new read.
- PR #1823 contains current Terra model routing but release HOLD, historic Max one-shot consumed, no retry. Neither a passing PR gate nor this mission document is proof of live Terra High invocation.
