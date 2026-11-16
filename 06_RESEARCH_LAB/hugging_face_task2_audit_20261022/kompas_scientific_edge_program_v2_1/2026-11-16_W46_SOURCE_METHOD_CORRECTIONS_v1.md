# W46 methodological correction and evidence gate, 16 Nov 2026

Status: RESEARCH_ONLY / SOURCE_UNSEALED / NO_OFFICIAL_SCORE / ASTRA_NOT_RUN. Owner-directed corrective addendum to PR #2171, not a replacement for missing source evidence.

## 1. Original Binance raw capture provenance
Original public Binance BTCUSDT and ETHUSDT 1h response observed 2026-11-15T12:56:33.282Z was **not preserved byte-exact**. Therefore original response SHA-256, original response byte count, request/response headers, request completion timestamp and original complete OHLC record set are **NOT PROVEN**. Do not invent a checksum. Re-fetching now would create a distinct later observation, not seal the original capture or establish original market producer first-known. The original reported five-day prices remain retrospective unsealed observations pending independent raw archival. Source state SOURCE_UNSEALED; original PIT status UNVERIFIED.

## 2. Clock and currency invariants
All comparison target dates are UTC. A UTC daily close is the close of the fully completed 23:00-23:59 UTC hourly candle, available only after 00:00 UTC next day. Monday 9 Nov original 10:52:34.925867Z issue excludes Monday's target. Tue 10 to Sat 14 Nov are five mature UTC daily closes as of the original 15 Nov capture. Sunday 15 Nov was not mature at capture. First downside envelope breach timestamps use *hourly LOW*, not completed daily CLOSE, and do not prove a real-time alert was issued. Original B0 9 Nov 09:00-09:59 UTC bar was completed before the original issue, but its source was fetched retrospectively. BTCUSDT/ETHUSDT are quoted in **USDT**, not USD. No unproven 1:1 FX/peg or venue-equivalence assertion; native CN USD comparisons require separately established currency/venue comparability.

## 3. Scope and leakage
W46 Tue-Sat are five correlated daily observations from **one independent week**, not five independent forecast trials. Original production first-published/first-consumed lineage is unverified. MAE and interval coverage are developmental matched comparator diagnostics, not official performance. No late ETF/stablecoin/macroeconomic evidence may be retroactively inserted into W46 original issue. Original elevated bearish risk is acknowledged; no retrospective 4/5 warning is credited.

## 4. Reproduction gate
The prior JSON contains daily summary rows but does not contain byte-sealed complete Binance hourly OHLC responses. Thus independent full OHLC replay, first-breach verification and original checksum reproduction are NOT PROVEN. Recompute MAE and coverage from the JSON daily rows as a separate arithmetic check only, with original numbers preserved and discrepancies reported. Full source verification must wait for archived raw hourly bytes with provider request parameters, capture receipt, UTC timezone, quote currency, and SHA-256. Never promote this addendum to a verified raw-data receipt.

## 5. W47 pre-registration validity
Companion W47 prereg candidate was committed at 12f51efc81168473f0d868892c379ffe4ff5fd45, but **preissue first-main and consumer-delivery chronology is NOT PROVEN**. A candidate committed on a PR branch is not automatically immutable original-main preregistration. Compare exact original W47 issue UTC and first-main receipt. If candidate postdates issuance or source evidence is missing, label LATE_EXPLORATORY and exclude from forward validation. Undefined C1 qualifier, B0 ATR rule, alert budget or cost threshold cannot be fitted after outcomes. No production policy changes.

## 6. Review and CI
Current PR must be safely updated against current main without rebase/force-push and preserve three research artifacts. Previous 12 test failures (run 43769308309) appear stale-base-related but are not proven resolved. Require new full native CI, source/privacy check, independent Claude exact-head methodology review, and Task2 owner #1596 acceptance before ready/merge. This addendum is not a review or release approval.

## 7. Astra HIGH admission
Existing false && workflow condition and authorized_paid_dispatch=false are binding. No paid dispatch until reviewed exact-head source-only one-shot executor, authenticated provider identity, cost enforcement, available budget, custody and original source readiness are proven. No API charge or Astra report is claimed.
