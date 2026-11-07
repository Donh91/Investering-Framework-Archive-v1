# HRE native historical pilot, original owner Task2 #1596

**Owner-authorized:** 7 November 2026, existing original owner issue comment https://github.com/Donh91/Investering-Framework-Archive-v1/issues/1596#issuecomment-6709645392
**R1/M1:** Native source and baseline pilot, never a claimed Official Kompas reconstruction, predictive improvement or approval of a new signal.
**Code:** scripts/research/hre_native_replay_pilot_v1.py
**Tests:** tests/research/test_hre_native_replay_pilot_v1.py
**Execution:** existing read-only GitHub PR-only Research Parallel Lanes Skill Contract CI, three independent jobs; no new workflow, cron, identity, provider API key or billed AI request.

## Native public data source

Binance Public Data https://github.com/binance/binance-public-data, specifically *monthly SPOT hourly BTCUSDT and ETHUSDT* ZIP files from https://data.binance.vision/data/spot/monthly/klines/.

Current code uses direct source ZIP bytes and upstream contemporaneous hosted **.CHECKSUM** file SHA256, stores compact source file SHA256 and provider metadata in artifacts. It verifies the internal ZIP has one exact expected CSV path, rejects oversized input, invalid/duplicate/out-of-month OHLC and missing contiguous hourly candles, checks UTC close and quote. SPOT from Jan 2025 has timestamps in microseconds, earlier SPOT uses milliseconds; normalize both. Monthly ZIP bytes can change from upstream vendor and may have been published/revised years after the market day. **Thus these archives are retrospective price/outcome truth tapes, not authenticated original provider first-known archives or immutable original Kompas inputs.** A stored source revision hash now is necessary for reproducibility, but does not establish original-era information arrival.

Quotes are USDT, never silently USD. No restricted wallet, owner portfolio or source-private payloads in public GitHub. Only bounded ordinary ZIP downloads with named allowlisted symbols/months; no remote code, free Hugging Face download, Github token or API secret required.

### Three independent jobs and falsifiers

**SOURCE (2020 February/March; 2025 September/October):** Verify BTC+ETH spot hourly source file count, continuity and exact sha256. Distinguish 2020 and 2025 cohorts so no artificial 5-year stitched continuity.

**CRISIS (2020 February-April and 2025 September-October):** Compute fixed price-only controls for **daily midnight UTC cutoffs**. At the cutoff use last closed hour, past 24h return, past 72h high/low; label future worst hourly low over 72h from the cutoff price, threshold -8%. Baseline warning if past24h return <=-5%; challenger warning if past24h <=-3% AND past72h drawdown >=8%. Show descriptive TP/FP/FN/TN, preserve all quiet days and misses. These are **hand-selected exploratory thresholds, not original Kompas Risk severity, not statistically significant**. 72h forward labels at daily cutoffs overlap and cannot be treated as independent event counts; later research must use independent episode blocking, alternatives, multi-event and leave-one-crisis-out.

**WEEKLY (February-May 2021):** Each eligible historical Monday 00:00 UTC, use 29 previous complete daily closes to calculate 28 daily absolute returns. For each of the upcoming **seven separate days**, freeze last closed price as naive expected close and compare:
- baseline daily range = previous close +/- 2% * sqrt(forecast day index);
- alternative daily range = previous close +/- 1.5 * median(prior28 daily absolute return) * sqrt(forecast day index).

Score actual daily high+low covered, average relative range width, seven individual expected-close MAE. The two arms have **identical expected-close price** and cannot establish a directional edge. This is a **retrospective historical control** for later actual Cycle Navigator research, NOT a real CN issuance from 2021 or complete current seven-day model. W45 2026 native original 0/7 stays immutable.

### Scientific conclusions allowed

This pilot can provide actual source-file QA, a valid algorithmic historical control, baseline score distributions, and an after-source next specific research question. It cannot claim live sensor edge, earlier original alerts, historical issuer authenticity, generic independent crash N, Kompas/CN 2026 predictive skill, true original first-known access, any signal promotion, investor P&L or automatic trades.

### Receipt and durability

Each native PR job logs separate job/run/commit identities and uploads one source-bound JSON with original ZIP SHA256 evidence, full rule definitions, counts and limitation text. Artifacts expire after 30 days, so compact scientific and metadata receipts should be read back and preserved in existing Task2 evidence/owner research upon successful qualified PR merge. Large or restricted data stays out of public Git. No provider data is persisted as a market-wide authority.

The scientist must classify actual provider 404, 429, 5xx, unavailable or revised archives as SOURCE_GAP or PROVIDER_TEMPORARY_ERROR and record the true job log, not treat as PASS or compensate by fabricating bars.
