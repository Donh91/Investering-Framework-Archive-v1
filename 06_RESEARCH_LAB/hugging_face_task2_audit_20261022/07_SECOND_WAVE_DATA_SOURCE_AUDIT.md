# HF audit wave II — eight further candidates (source-document review)
**Timestamp:** 2026-10-22, Copenhagen. **Status:** EXTERNAL_SOURCE_SCREEN / RESEARCH ONLY / NO PIT OR MARKET-SKILL ADMISSION. **Method:** live Hugging Face authenticated Hub metadata, dataset structure and creator README / selected manifest files. File contents/rows not independently bulk downloaded or reconciled. GitHub main and current Task 2 R0–R7 owner read before any new owner suggestion. A Dataset Viewer 429 occurred on several sources; a 429 is not dataset absence.

## Candidate cards, dispositions and exact caveats

### HF-013 | Chainticks/stablecoin-flows
- Source: https://huggingface.co/datasets/Chainticks/stablecoin-flows; **CC BY 4.0** tag; Hub reports ~494k rows, 16 fields, 167 daily Parquet partitions, ~53.3 MB. README describes ERC-20 USDC/USDT mint, burn and bridge **on-chain events**, NOT exchange deposits or investor deployment, with `source_kind='on_chain_event'`.
- Source files `_schema.json`, `_manifest.json`, `LATEST_DATE.txt` are present and readable; on 2026-10-22, `LATEST_DATE.txt` returned 2026-10-22. This proves update pointer availability, not completeness/first-ever publication. The provided manifest excerpt showed 2026-05-14 range ending **03:53:35Z**, and following 2026-05-15 starting **00:22:47Z**, which flags a potentially large coverage hole / off-hours or limited population. Reconcile entire daily manifest before using any day as 24h flow.
- **Fit:** Task 2 stablecoin context and on-chain chronology; possible 2-week partitioned event-typing benchmark. **Cannot:** infer net speculative altcoin deployment or ETF-era capital rotation from transfer events alone; unique entity, burn/mint/bridge, chain, volume and cross-venue netting not established.
- **Decision:** `P1_SMALL_PARTITION_SOURCE_QA`. Proposed pilot tests daily expected file presence, data end/start vs UTC, unique on-chain event keys, type semantics, revision SHA and completeness before correlation.

### HF-014 | ochinimus/crypto-liquidation-ticks
- Source: https://huggingface.co/datasets/ochinimus/crypto-liquidation-ticks; **CC BY 4.0**; creator reports 1,442,664 individual prints from Bybit, Binance, OKX for ~800 symbols, spanning **2026-07-08 16:42:32 through 2026-08-06 23:59:42 UTC**; source file `liquidations_full_20260807.csv` and `coverage_20260807.csv`.
- **Critical:** original universe expands from **5 to 800 symbols at 2026-07-12 16:23 UTC**. Naive aggregate liquidation spike is collector expansion, not a market event. Restrict earlier analysis to five continuously followed pairs BTCUSDT/ETHUSDT/SOLUSDT/XRPUSDT/DOGEUSDT or start post expansion.
- Creator states Binance is throttled to one event per symbol per ~1 second and OKX similarly truncated; Bybit stream is presented as more complete. **Publisher claim, not independent provider receipt.** Cross-venue sums are **lower-bound coverage**, especially during cascades; price and side semantics vary by venue.
- **Fit:** Stress/Flush mechanics/relative venue quality. **Not a test of June 2026 flush** because collection starts July. Do not consume provider's separate x402 paid live service.
- **Decision:** `P1_VENUE_STRATIFIED_AUDIT_ONLY`, no universal predictive-lag claim.

### HF-015 | katelabs/crypto-news-scored
- Source: https://huggingface.co/datasets/katelabs/crypto-news-scored; **CC BY-NC 4.0** (non-commercial); 25,407 headlines from 54 outlets (2026-02-01 to 2026-04-30) plus 79,524 hourly bar closes and 36 pairs to May 4. Separate `published_at`, `ingested_at`, `news_type` and model tone score.
- Publisher reports median **11.8 minutes** ingestion delay and p90 15.3 minutes; 78.6% reactive vs 21.4% proactive. These are **source-card statistics not independently recomputed**. Publication time is publisher-stated. No original immutable collector receipt/model score-code SHA has been verified against retrospective modifications. Scorer model revision, training vintages, late edits, tag rule and publisher rights must be audited. The author says full/current dataset and commercial feed are separately licensed.
- **Fit:** Situation Room/news P1 historical red-team sample for news-first versus market-first, story dedup and same-clock action utility, **not** a live free news feed. Distinguish zero-to-one headline family from repeated syndication. Never credit sentiment before its actual `ingested_at` and first-delivered-to-*our*-system.
- **Decision:** `P1_LICENSE_NONCOMMERCIAL_RESEARCH_ONLY__PIT_CUSTODY_UNPROVEN`. Compare zero-news baseline and lagged/reshuffled score placebo.

### HF-016 | maryamfakhari/crypto-news-coindesk-2020-2025
- Source: https://huggingface.co/datasets/maryamfakhari/crypto-news-coindesk-2020-2025; 229.2k Hub-viewer rows / 13 fields, **CC BY-NC 4.0**.
- Creator says articles originate via CoinDesk Data through CryptoCompare API, retrospective publication dates, January 2020–January 2025. Academic/research use permission claimed, not a transferable license for current live API/news text or paid resale.
- **Fit:** historic text classification and event cluster/dedup only; first-known delivery unavailable. No direct chronological event-skill claim.
- **Decision:** `P2_SECONDARY_NONCOMMERCIAL_TEXT_SOURCE`.

### HF-017 | polyorderbooks/polymarket-crypto-updown-orderbooks-l2
- Source: https://huggingface.co/datasets/polyorderbooks/polymarket-crypto-updown-orderbooks-l2; **CC BY 4.0**, ~897,192 L2 snapshots, 805 resolved markets, three horizon cohorts (5m, 15m, 4h), 3 Parquet files ~45.4 MB.
- Creator reports **one-sided orderbooks** at 5m 16.9%, 15m 9.3%, 4h 0.5%; **crossed** books at 5m 3.24%, 15m 3.08%, 4h 1.50%. Original `winning_outcome` is attached to *every historical row*; must NEVER be included in a feature, replay price or preliminary selection.
- Captures once per second with periodic full reconciliation every 60s. Source states event-stream replay can diverge significantly from exact full-book snapshots because sequence numbers/removed levels can be missed.
- **Fit:** independent price-implied baseline and *execution feasibility* rather than aggregate prediction. Evaluate spread, missing bid/ask, last minute one-sided, fees, quote age and entry/exit at tradable side; do not use headline p(win) as attainable fill or assume markets independent. Check collision with existing HF-004 Polymarket dataset and owner.
- **Decision:** `P1_COST_AND_EXECUTABILITY_NEGATIVE_CONTROL` as research only.

### HF-018 | fati-80-Sho/RugPull1K
- Source: https://huggingface.co/datasets/fati-80-Sho/RugPull1K; creator README claims **1,028 token projects** across ETH/BSC/Polygon/Arbitrum/Fantom, **CC BY-NC 4.0**, and explicitly says **not suitable for trading, investment advice or commercial use**.
- The Hub Viewer reports **935.8k rows / only 1 column**, which does not match the described 1,028-project multivariate tabular research schema. File/tree inspection and actual row parsing are REQUIRED to reconcile representation before any claim of trainable features.
- Creator defines feature cutoff at each project's **lifecycle midpoint**. If midpoint depends on a known-final lifecycle endpoint, it may itself be unavailable to real traders at that time. Explicitly test chronology instead of accepting 'leakage-resistant' claim. Borderline case exclusion (>200) can create clean-label selection bias; reporting 1028 labelled projects alone gives no population base rate.
- **Decision:** `P2_FORMAT_MISMATCH_AND_DECISION_TIME_UNVERIFIED__NONCOMMERCIAL`; methodology literature only until reconstructed.

### HF-019 | AdamAtractor/24_crypto_orderbook_30lvl
- Source: https://huggingface.co/datasets/AdamAtractor/24_crypto_orderbook_30lvl; **CC BY 4.0**; creator explicitly says **7-day free promotional sample**, 24 assets, Hyperliquid L2 derived depth 1-minute aggregates. HF viewer has no Parquet rows; native HF files such as `BTC_1m_depth30.csv` exist.
- Claimed >12 months full history is offered externally as **paid commercial data**, not an included free-HF dataset. No justification to pay or mistake small single-week sample for all market cycles. Perpetual DEX orderbook is not a BTC spot or ETF tape.
- **Decision:** `P3_METHODS_DEMO_ONLY`, not Task 2 multi-cycle input.

### HF-020 | SahandNZ/cryptonews-articles-with-price-momentum-labels
- Source: https://huggingface.co/datasets/SahandNZ/cryptonews-articles-with-price-momentum-labels; OpenRAIL-tagged historical NLP classification dataset, Hub reports ~180.3k rows, four columns, train/test/validation.
- Source card gives no verified per-record independent **issue cutoff**, our first-known time, forward fee-adjusted execution or cohort independence. A price momentum label can be computed using a later price path; language model fit is not original forecast performance. Dataset news rights may differ from stated dataset license.
- **Decision:** `P3_TEXT_CLASSIFICATION_METHOD_ONLY`. Never market-skill admission.

## Method and classification
These eight sources are **newly screened for this PR**. Repository code search for their exact IDs before creating this delta returned no matches; this is not a complete cross-repo source census, and no new owner is created. Initial source row counts and self-reported limitations are NOT our independent QA measurements. The HF Dataset Viewer returned 429 on several sources, hence no record-level null/key/drift calculations were executed. No paid app or account upgrade used.

Every source requires revision file SHA, observed symbol/chain clock, source first-known claim quality, legal use classification, gap accounting, distinct-event N, outcome-censor handling and existing domain owner before further use.
