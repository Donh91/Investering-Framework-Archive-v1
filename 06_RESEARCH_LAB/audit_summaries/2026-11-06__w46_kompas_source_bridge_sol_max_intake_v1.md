# W46 Kompas /goal Mission 2: source-first adversarial intake (6 Nov 2026)

**Contract:** W46_SOL_MAX_PUBLIC_SOURCE_BRIDGE_INTAKE_v1. **Authority:** advisory only; not an issue freeze, forecast, P0 release approval, trading instruction, owner approval, or independently witnessed natural-delivery series. **Public sources only.** Every statement labeled VERIFIED is limited to its listed repository/source receipt and must be tested again against exact fresh main before claiming current deployment.

## Verified existing fixes, never propose them twice

- Original Archive PR #1953 MERGED: 14-horizon diagnostic/source-gap routing. Research G0, NOT 14-horizon official price prediction.
- Original Archive PR #1954 MERGED: 56-day BTC/USDT research code unblock. It does NOT license 14–30 day forward forecasts or 4–8 week/1–12 month official targets.
- Original Archive PR #1956 MERGED: quote unit firewall USD/USDT, same seven daily source bounds, genuine observed daily high/low Graph B. Exact original CI and Pages release previously passed; not evidence of future W46 issue.
- Original Archive PR #1960 MERGED: no second provider POST **within one CN invocation**. Cross-run durable original issue/claim is not proven; never backfill a failed payment as zero, nor silently copy Research Lab public-30-day storage consent to CN primary store=false.
- Original Archive PR #1879 MERGED: bounded 7-day semantic recovery. Research freeze/history and source-to-natural consumer remain separately unproven.
- The actual Task2 Archive-first #1967 and #1968 are MERGED and published as ADVISORY_ONLY, scientific outcome INSUFFICIENT_EVIDENCE, not new profitable forecast evidence.
- **Pending separate ORIGINAL SITE patch:** Archive PR #1970, bounded Graph B P1 daily UTC-day cells plus P2 replay axis not seeing later actuals, original source/quote guards unchanged. At intake initial head 3aa23292d622c2f3c072a94d64c2d539001d898d, adds eight native BTC/ETH renderer tests into pre-existing Premium v2 npm test gate. Treat current PR status/HEAD/test result as UNKNOWN until native reread; do not recommend the same patch a second time.

## P0 liveness: independently inspect before modeling

Public repo `03_DAILY_CAPTURE_LOGS/hourly/LATEST.json` on verified read 6 Nov at Archive main blob `e80e38b3427d9f005a04451eac9bc3238d52e9b2`:
- retrieved_at_utc 2026-11-06T10:50:24Z
- window_end_utc 2026-11-06T10:00:00Z (last completed source UTC hour)
- status COMPLETE, requested 26/26 only relative to that **old** 26-hour window; NOT fresh as of afternoon 6 Nov.
- First genuine natural Hourly→source→Pages→CDN was independently verified in original #1827 comment 6683797857 via native scheduled Hourly run #42205621427. This is 1/3 consecutive authentic hourly deliveries, not 3/3.
- Original #1827 owner observations: natural GitHub schedule-created runs of Hourly Sequence Capture and Native Market Recovery occurred sparsely in bounded samples on 5–6 Nov. **No authoritative single root cause confirmed.** Differentiate missing *scheduled run creation*, GitHub runner queue, `framework-market-owner-writer` lock, failing source execution, rejected stale source clock and missing Pages/CDN ACK. An intermittently successful manual workflow_dispatch cannot substitute for 3 consecutive native scheduled completions. Preempt speculative new cron, new task/agent or disabled controls.
- Existing exact workflow `.github/workflows/hourly-sequence-capture.yml` deliberately uses UTC '12 * * * *', real source writer, source-hour preflight and Pages handoff; source materializer `scripts/daily_capture/build_hourly_sequence.py`, recovery `.github/workflows/native-market-recovery.yml`, watchdog `.github/workflows/compass-schedule-watchdog.yml`. Read current actual Actions run census and stage/job logs; propose smallest source-only bounded repair only if failure reproducible. A GitHub scheduling service delay/drop is EXTERNAL until independently falsified.

## Independent Grok Bridge source review

Original advisory-only [Bridge PR #146](https://github.com/Donh91/Investering-AI-Audit-Bridge/pull/146), report created 2026-11-06T15:20:36Z, source-pinned Archive SHA 82f23f6a171f2e3d5ee8e5203fa9e754bf96cfbe and later source-drift acknowledgement, documented 94 offline tests (three deliberate failures) but NOT formal independent APPROVED. Findings:
- N1 P1 renderer daily bounds wrongly applied to end-of-day close timestamps instead of each original UTC day cell; exact source repair proposed, now separately STAGED in #1970, not automatically accepted.
- N2 P2 replay axis includes future unshown actuals; staged #1970.
- N3 P1 absence of durable cross-invocation *primary* forecast paid-request claim before original freeze/receipt. Existing #1960 is still valid per-invocation. No real double charge proved. Require a native atomic durable one-issue claim with independently reconcilable UNKNOWN-liability, request+source hash and no second POST on timeout, restart, concurrent jobs or month rollover. The Research Lab's own Sol MAX native claim is NOT automatically authorized for CN.
- Not demonstrated: actual Sunday–Monday prospective daily forecasts/7/7 high-low-close, all provider fees, full live Safari/390/430 acceptance, three natural hourly->CDN ACKs, original W46 first-known/timezone lineage, correct economic scoring.
- KR004 bull/bear scalar display is not independent predictive evidence; avoid duplicated pointless ablation. Distinguish independent original market signal/first-known event-family denominators from derived display ratios.

## Monday W46 acceptance / negative tests

9 Nov 2026 UTC 00:00 to 16 Nov UTC 00:00 is 09 Nov 01:00 to 16 Nov 01:00 Copenhagen. Original issued-at/scoring-valid-from must be explicit. Monday 09 Nov day bounds issued after UTC start cannot be scored as fully ex-ante 24h without an owner-approved scoring rule. Never retrofit W45 or issue the week after knowing future outcomes.

Require, per BTC and ETH, seven honest source-issued daily `expected_close`, low, high, exact companion daily range equality and declared comparable currency; immutable time-stamped Monday original, a future independently observed series with exact source/UTC hour first-known, no zero-filled future/phantom high-low. Graph expected close knots must be seven UTC-end positions; range band must occupy its own seven UTC-day cells, replay hidden future actuals must not affect axis. On actual source gap, render STALE / UNAVAILABLE rather than a current live price.

Separate outcomes G0 code readiness, G1 original source/attestation, G2 first true W46 issuance, G3 native Pages/CDN parity with 3 successive scheduled hourly source deliveries, G4 independent price precision scored only after outcome maturity. A green PR/CN code path, ad-hoc manual delivery or advisory research is never 100%-readiness.

## Sol MAX research deliverable, no private data or paid replay

Falsify top three true remaining *current* causal defects by original code/workflow/source/runner/consumer, including at least one upstream scheduling/root-cause hypothesis and cross-run economic claim. Distinguish VERIFIED vs LOCALLY_REPRODUCED vs ADVISORY vs FUTURE vs UNKNOWN, and report exact original owner #1827, #1516, #1578, #1476 or S1 #1156, minimal test/mutation, no-go, economic cost and next action. Do not duplicate #1953/#1954/#1956/#1960/#1970, raise a new supervisor, bypass GH independent high-impact review or invent future delivery/forecast scores. Original bridge PR #146 is not model authority.
