# W46 methodological correction and evidence gate, 16 Nov 2026

Status: RESEARCH_ONLY / SOURCE_UNSEALED / NO_OFFICIAL_SCORE / ASTRA_NOT_RUN. Owner-directed corrective addendum to PR #2171, not a replacement for missing source evidence.

## 1. Original Binance raw capture provenance
Original public Binance BTCUSDT and ETHUSDT 1h response observed 2026-11-15T12:56:33.282Z was **not preserved byte-exact**. Therefore original response SHA-256, original response byte count, request/response headers, request completion timestamp and original complete OHLC record set are **NOT PROVEN**. Do not invent a checksum. Re-fetching now would create a distinct later observation, not seal the original capture or establish original market producer first-known. The original reported five-day prices remain retrospective unsealed observations pending independent raw archival. Source state SOURCE_UNSEALED; original PIT status UNVERIFIED.

## 2. Clock and currency invariants
All comparison target dates are UTC. A UTC daily close is the close of the fully completed 23:00-23:59 UTC hourly candle, available only after 00:00 UTC next day. Monday 9 Nov original 10:52:34.925867Z issue excludes Monday's target. Tue 10 to Sat 14 Nov are five mature UTC daily closes as of the original 15 Nov capture. Sunday 15 Nov was not mature at capture. First downside envelope breach timestamps use *hourly LOW*, not completed daily CLOSE, and do not prove a real-time alert was issued. Original B0 9 Nov 09:00-09:59 UTC bar was completed before the original issue, but its source was fetched retrospectively. BTCUSDT/ETHUSDT are quoted in **USDT**, not USD. No unproven 1:1 FX/peg or venue-equivalence assertion; native CN USD comparisons require separately established currency/venue comparability.

## 3. Scope and leakage
W46 Tue-Sat are five correlated daily observations from **one independent week**, not five independent forecast trials. Original production first-published/first-consumed lineage is unverified. MAE and interval coverage are developmental matched comparator diagnostics, not official performance. No late ETF/stablecoin/macroeconomic evidence may be retroactively inserted into W46 original issue. Original elevated bearish risk is acknowledged; no retrospective 4/5 warning is credited.

## 4. Reproduction gate
The original diagnostic JSON contains five daily summary rows per asset but does not contain byte-sealed complete Binance hourly OHLC responses. Thus independent full OHLC replay, first-breach verification and original checksum reproduction are NOT PROVEN. Recompute MAE and coverage from the JSON daily rows as a separate arithmetic check only, with original numbers preserved and discrepancies reported. Full source verification must wait for archived raw hourly bytes with provider request parameters, capture receipt, UTC timezone, quote currency, and SHA-256. Never promote this addendum to a verified raw-data receipt.

## 5. W47 pre-registration validity
Companion W47 prereg candidate was committed at 12f51efc81168473f0d868892c379ffe4ff5fd45, but **preissue first-main and consumer-delivery chronology is NOT PROVEN**. A candidate committed on a PR branch is not automatically immutable original-main preregistration. Compare exact original W47 issue UTC and first-main receipt. If candidate postdates issuance or source evidence is missing, label LATE_EXPLORATORY and exclude from forward validation. Undefined C1 qualifier, B0 ATR rule, alert budget or cost threshold cannot be fitted after outcomes. No production policy changes.

## 6. Review and CI
The common upstream test defects were repaired by independently reviewed and merged Archive PR #2187 (2026-11-16T10:18:40Z, squash `ec03ddafb7d7bf364839b6866804b579a1673d16`). That upstream release passed 5,940 native tests; it is **not** by itself CI evidence on this research PR. On 16 Nov the existing #2171 branch was updated from main by non-force merge, and its W46 development document was corrected for the true merged status of PR #2115, n=1 inference, `ASSUMED_UTC_ISO_WEEKDAY` mapping and low-trust context. On any new exact head require its own native full suite, source/privacy check and independent Claude method review. The original Task2 owner #1596 must approve research-only classification before merge. This addendum is not a release approval.

### Claude methodology follow-through
- **C1:** The descriptive MAE result is `NO_SKILL_DEMONSTRATED_vs_B0`, not evidence of universal inferior predictive skill. W46 is **one** independent correlated week.
- **C2:** Original Binance HTTP bytes cannot be restored retrospectively. The official historical `data.binance.vision` ZIP and matching published `.CHECKSUM` can be collected as a *new, timestamped, retrospective source receipt* by the authorized source owner, with exact byte hashes and privacy classification. It still cannot establish producer PIT or original 15 Nov capture bytes.
- **C3:** Original CN point day-to-calendar mapping remains `ASSUMED_UTC_ISO_WEEKDAY` until original first-issued contract is shown. Do not infer USD=USDT parity or same venue.
- **C4:** W47 companion was a branch research candidate, not proven first-main preissue. No confirmatory W47 risk test or retrospective threshold fitting. For future preregistration design, propose at least 6 independent adverse-event clusters and 6 quiet clusters before evaluation, subject to separately approved effective-sample and false-alarm plan. These counts are a **proposed future gate**, not a threshold registered before W47.
- **C5:** `charliedesk.com` is `LOW_TRUST_CONTEXT`, excluded from feature construction. ETF, stablecoin and macro inputs require #1827 original first-known plus D5 acceptance before eligible use; later publications cannot upgrade the W46 original evidence.

## 7. Astra HIGH admission
Existing false && workflow condition and authorized_paid_dispatch=false are binding. No paid dispatch until reviewed exact-head source-only one-shot executor, authenticated provider identity, cost enforcement, available budget, custody and original source readiness are proven. No API charge or Astra report is claimed.
