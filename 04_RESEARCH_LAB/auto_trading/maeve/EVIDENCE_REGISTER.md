# MAEVE EVIDENCE REGISTER

Purpose: track what is actually supported, where it came from, and how strongly it may be used in later reverse-engineering work.

## Evidence classes

- `PRIMARY_PUBLIC` - original CFGI/MAEVE source or first-party documentation.
- `SECONDARY_CONTEMPORARY` - contemporary third-party article, mirror or preserved discussion.
- `SECONDARY_TECHNICAL` - technically detailed reconstruction/summary whose primary provenance is incomplete.
- `USER_SUPPLIED_SCREENSHOT` - screenshot supplied directly for research; provenance beyond the visible source context may be incomplete.
- `CLAIM_ONLY` - promotional/community claim without row-level evidence.

---

## MAEVE-EV-0001 - Public launch / roadmap

Source: https://pastebin.com/zx6Y4wT4
Date: 2025-01-09
Class: PRIMARY_PUBLIC

Supported:
- M.A.E.V.E = Markets and Emotion Valuation Engine.
- Powered by CFGI.io.
- Public beta v1.00.
- Official X account identified as `CFGI_MAEVE`.
- Roadmap included risk-on improvements, GMDI integration and later live dashboard/user integration.

Does NOT support:
- exact decision rules;
- performance quality;
- exact private features.

---

## MAEVE-EV-0002 - Detailed architecture reconstruction

Source: https://studylib.net/doc/28348344/maeve-trading-strategy---maeve-trading-strategy--1---2-
Class: SECONDARY_TECHNICAL

Supported only as a research lead unless primary material is recovered.

Reported concepts:
- three aligned data points for entry/exit in earlier system;
- coin/timeframe-specific triggers;
- ten public CFGI inputs plus four private inputs;
- DCA;
- later rolling Market Range Evaluator;
- dynamic Optimal Data Trigger selection;
- compatibility/redundancy checks;
- global + asset GMDI context;
- portfolio-aware position sizing;
- target, stop and time-loss;
- single-condition exit and possible reversal.

Risk:
The page appears to contain a derived summary/conversation rather than authenticated CFGI source documentation. Do not label these exact mechanics as verified proprietary architecture.

---

## MAEVE-EV-0003 - Mid-2025 performance promotion

Source: https://medium.com/@cplguru606/cfgi-m-a-e-v-e-real-trades-real-revenue-real-utility-42d54ef91553
Date: 2025-07-01 era
Class: SECONDARY_CONTEMPORARY / PROMOTIONAL

Reported:
- 660+ live trades;
- 91.3% win rate;
- 4.1% average monthly portfolio growth;
- 21.8% YTD;
- claim that trades were posted live and history was available on CFGI.

Use:
Performance checkpoint / source-discovery lead only.

Do not treat as audited performance.

---

## MAEVE-EV-0004 - Official September 2025 performance checkpoint

Source: https://cfgi.io/articles/how-maeve-ai-trading-maximizes-crypto-profits
Date: 2025-09-10
Class: PRIMARY_PUBLIC, PERFORMANCE CLAIM

Reported:
- 84.85% win rate;
- 1,427 trades;
- 1.20% monthly returns;
- approximately 25% over eight months;
- V2 added leverage trading.

Research importance:
The lower win rate relative to earlier 90%+ claims suggests performance/version/regime drift worth reconstructing rather than assuming one stable strategy.

Still not audited unless row-level trade history independently reproduces it.

---

## MAEVE-EV-0005 - AI dashboard / public-history claim

Sources:
- https://mfgi.io/ai-trading
- contemporary links to `https://cfgi.io/ai-dashboard`
Class: PRIMARY/SECONDARY MIXED

Reported:
- public real-time dashboard;
- full trading history;
- 91.30% headline win rate during one historical snapshot.

Current status:
The exact historical public endpoint is now confirmed as `https://cfgi.io/ai-dashboard`. The URL currently returns 404, so recovery requires archived/cached copies or dependent data endpoints.

Research priority:
Locate/capture historical dashboard payloads, static HTML, API calls, JS bundles or cached page data if still publicly retrievable.

---

## MAEVE-EV-0006 - Multi-timeframe CFGI relationship

Sources:
- CFGI press releases and current developer documentation.
Class: PRIMARY_PUBLIC

Supported:
- MAEVE was described as applying CFGI's multi-timeframe sentiment framework.
- CFGI exposes historical/public API data and algorithmic components.

Research implication:
Reconstructing public CFGI state around MAEVE timestamps is technically plausible if historical access and licensing permit.

---

## MAEVE-EV-0007 - X public-forward history

Source target: https://x.com/CFGI_MAEVE
Class: PRIMARY_PUBLIC TARGET
Status: NOT YET FULLY RECOVERED

What is known:
Multiple contemporary references claim individual trades were posted live on the MAEVE X account.

What is NOT yet known:
- completeness of recoverable tweet history;
- deleted posts;
- exact timestamp-to-fill convention;
- whether every DCA/partial exit was posted;
- whether X posts were synchronous or delayed.

No completeness claim is permitted until reconciled against an independent trade count/checkpoint.

---

## MAEVE-EV-0008 - Third-party X mirrors/checkpoints

Examples include TwStalker-preserved posts/comments citing roughly:
- 500+ trades at approximately 94-95% win rate;
- 650+ trades at approximately 91.3% win rate.

Class: SECONDARY_CONTEMPORARY

Use:
- establish approximate checkpoint chronology;
- discover original account/status URLs;
- cross-check missing periods.

Do not use mirror claims as trade rows unless original trade text/timestamp is preserved.

---

## MAEVE-EV-0009 - Official surviving dashboard screenshot

Source image: https://cfgi.io/images/articles/maeve_trades_dashboard.png
Source context: CFGI article, `How M.A.E.V.E’s AI Trading Maximizes Crypto Profits`
Class: PRIMARY_PUBLIC VISUAL ARTIFACT

Visible / recoverable from the surviving official screenshot:
- dashboard summary shows 721 closed positions and zero open positions;
- period portfolio PNL and YTD portfolio PNL are shown as +25.91% in the captured state;
- a paginated/searchable trade table exists;
- visible columns include asset/symbol, PNL, status, ID, timeframe, UTC timestamp, average entry price, exit price and DCA;
- visible examples include SOL, DOGE, ETH, BTC and BNB;
- visible timeframes include 15m, 1h and 4h;
- the artifact proves the old dashboard contained row-level trade records rather than only aggregate marketing metrics.

Research importance:
This is the strongest surviving visual proof so far that row-level trade history existed publicly. The table structure can be used to constrain parser/schema recovery and identify likely API fields.

Do NOT infer all 721 rows from this screenshot alone. Only the visible rows are directly evidenced.

---

## MAEVE-EV-0010 - User-supplied CFGI methodology screenshots

Captured: 2026-09-08
Class: USER_SUPPLIED_SCREENSHOT

Local research hashes at intake:
- `IMG_6942.webp` SHA-256 `8b63a7c02e7752ae99a7630fa033927e7b9860de4a652976150b5104d40e37ee`
- `IMG_6943.webp` SHA-256 `5bf21851181b7695ec286b7dd9dcfd564198e8860c0d8cea3bbb0239a56b2fcf`

Visible claims in the methodology screenshot:
- CFGI says it rebuilt the traditional Fear & Greed approach beginning in 2022;
- ten named public algorithm families are visible: Price, Volatility, Volume, Impulse, Technical, Dominance, Whale Activity, Social Sentiment, Search Engines and Order Books;
- each currency is shown with 1D, 4H, 1H and 15M timeframes;
- each timeframe is described as running the ten AI algorithms;
- each individual timeframe/algorithm data point and CFGI score is described as saved every 15 minutes;
- the screenshot claims this historical storage has been occurring since late 2022 for every currency and is used as fuel for AI.

Visible claims in the comparison screenshot:
- CFGI describes itself as multi-timeframe and refreshed every 15 minutes;
- the chart compares CFGI against another fear/greed source at specific BTC timestamps;
- the page states its advanced public data algorithms are intended to support developers and its own AI trading system.

Research implication:
If the historical data store remains accessible through API/export or lawful account access, the natural MAEVE experiment is unusually strong: reconstruct public feature vectors at each MAEVE trade timestamp and perform feature attribution, ablation and behavioral-clone tests.

Caution:
These screenshots do not reveal proprietary weights, hidden features, training logic or decision rules. Their value is in confirming the public feature families, timeframes and claimed historical sampling cadence.

---

## Open evidence hunts

1. Original X trade posts from `CFGI_MAEVE`.
2. Search-engine cached tweet text/status IDs.
3. Third-party X mirrors with timestamp + full post body.
4. Internet Archive / other web-archive captures of `https://cfgi.io/ai-dashboard`.
5. Historical dashboard JS bundles and network/API endpoints that populated the row-level table.
6. GitBook pages or historical docs describing MAEVE rules.
7. Telegram public MAEVE trade channel/log if one existed.
8. Version-change announcements to define v1/v2 epochs.
9. Additional screenshots/images that contain historical trade tables.
10. Exact meaning of `win`, breakeven and DCA trade counting.
11. Primary source for MRE/ODT technical description.
12. Historical CFGI feature export/API coverage for 2025 trade timestamps.
