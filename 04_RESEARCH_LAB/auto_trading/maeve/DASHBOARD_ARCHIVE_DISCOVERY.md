# MAEVE DASHBOARD ARCHIVE DISCOVERY

Date: 2026-09-08
Status: PARTIAL RECOVERY - EXACT HISTORICAL ENDPOINT CONFIRMED, FULL ROW PAYLOAD NOT YET RECOVERED

## Exact historical public endpoint

`https://cfgi.io/ai-dashboard`

This endpoint is independently corroborated by multiple contemporary 2025 sources as the public M.A.E.V.E trading dashboard where users could watch trades in real time and inspect full trading history.

The endpoint currently returns 404.

## Strongest surviving artifact

Official CFGI image:

`https://cfgi.io/images/articles/maeve_trades_dashboard.png`

The surviving screenshot is materially useful because it confirms row-level structure rather than only a performance headline.

Visible dashboard state:
- 721 closed positions
- 0 open positions
- Period Portfolio PNL +25.91%
- YTD Portfolio PNL +25.91%
- searchable/paginated trade table

Visible row fields include:
- symbol / asset
- PNL percentage
- status
- trade ID
- timeframe
- timestamp UTC
- average entry price
- exit price
- DCA

Visible assets include SOL, DOGE, ETH, BTC and BNB. Visible timeframes include 15m, 1h and 4h.

## Contemporary corroboration

### Public-history references

Multiple 2025 sources directly linked to `cfgi.io/ai-dashboard` and described the history as publicly verifiable.

Examples:
- a contemporary Medium article described 660+ live trades, stated every buy/sell signal was posted publicly, and linked the full verifiable history to the AI dashboard;
- TwStalker-preserved posts reference 650+ trades at 91.30% and point directly to `cfgi.io/ai-dashboard`;
- another preserved discussion describes MAEVE as approximately 91% win rate since the start of the year and explicitly cites the dashboard as verification;
- CFGI/press material from September 2025 says traders could access MAEVE through the AI Dashboard.

These sources establish that the URL and public-history function are not reconstructed from memory after the fact.

## Internet Archive / Wayback status

The correct Wayback lookup target is:

`https://web.archive.org/web/*/https://cfgi.io/ai-dashboard`

At this research pass, the available browsing tools could reach the Wayback service but could not reliably enumerate the nested-URL capture list through its CDX/API interface. Therefore:

- do NOT claim that a complete Wayback snapshot has already been recovered;
- do NOT claim that Wayback lacks captures;
- the exact historical URL is confirmed and should be queried directly in Wayback using a browser capable of its JavaScript UI/API calls.

## Important technical caveat

Even a successful archived HTML page may not contain the trade rows.

The dashboard appears to have behaved like an interactive web application. If the table was populated by JavaScript from a backend endpoint, the archived page may preserve only:
- HTML shell;
- JS/CSS bundles;
- table headers/layout;
- static summary values.

The actual 700+ trade records may instead have lived behind a JSON/API endpoint.

Therefore the archival hunt must include both page captures and dependent resources.

## Recovery strategy

### Track A - archived page

Search Wayback and other archives for:
- `https://cfgi.io/ai-dashboard`
- `https://www.cfgi.io/ai-dashboard`
- historical redirects or query variants

### Track B - archived JS bundles

For every recovered page snapshot:
1. enumerate script URLs;
2. recover same-date JS bundles;
3. search bundles for strings such as:
   - `closed_positions`
   - `open_positions`
   - `entry_price`
   - `exit_price`
   - `dca`
   - `timeframe`
   - `portfolio_pnl`
   - `ai-dashboard`
   - `maeve`
4. extract fetch/AJAX/WebSocket endpoint names;
5. query web archives for those dependent endpoint URLs.

### Track C - screenshots and social mirrors

Continue collecting dashboard screenshots because each image can expose 10 or more row-level trades with exact timestamps, entry/exit prices and timeframes.

A sufficient image corpus can reconstruct a meaningful partial ledger even if the original API is gone.

### Track D - X / Telegram reconciliation

Use recovered dashboard rows to search `CFGI_MAEVE` mirrors by:
- exact timestamp;
- symbol;
- entry price;
- exit price;
- trade ID if public.

This can tie dashboard rows back to contemporaneous forward posts and strengthen provenance.

## What becomes possible if the ledger is recovered

For each trade timestamp, reconstruct the public state available to MAEVE without look-ahead:

`trade row`
+ `10 CFGI components x relevant timeframes`
+ `score velocity / acceleration / rolling percentile`
+ `asset-vs-market sentiment dispersion`
+ `OHLCV / volatility / liquidity`
+ `Framework regime state`
= `labeled MAEVE decision event`

Then test:
- which public components best explain entry timing;
- whether three-way feature alignment is visible empirically;
- whether signal combinations differ by asset or timeframe;
- whether DCA occurs under repeatable state conditions;
- whether exit logic is asymmetric to entry logic;
- whether unexplained decisions cluster around latent/private feature proxies;
- which features explain winners versus losers;
- whether MAEVE's behavior adds value beyond simpler public baselines.

## Research boundary

The target is behavioral/statistical reconstruction from public outputs and legitimately accessible historical data.

Do not attempt to obtain proprietary source code, bypass access controls or claim recovery of secret algorithms from correlation alone.
