# Cycle Navigator / Market Notes 001 - First X draft

**Dato:** 2026-11-16
**Status:** DRAFT_NOT_APPROVED / NOT_PUBLISHED
**Område:** Selvstændig redaktionel Cycle Navigator X-serie
**Primary folder:** `05_CYCLE_NAVIGATOR/x_market_notes/editions/2026-W47/`
**Afsender:** Cycle Navigator / Market Notes
**Materiale dækket:** 2026-W45 og 2026-W46, UTC; fredagsafsluttede ETF-handelssessioner.
**Beslutning:** Researchbaseret redaktionelt forslag. Ikke ejer-godkendt. Ikke udgivet på X.

## Valgt historie

BTC faldt næsten tre gange så meget i W46 som i W45, mens de amerikanske spot-BTC-ETF'ers ugentlige nettoudstrømning blev mindre. Den observerede andel af aggressivt køb i BTCUSDT spotvolumen på den beholdte venue-feed skiftede fra 50,60 % til 48,93 %. ETF-tallene er for fem amerikanske handelssessioner, BTC-pris og spotfeed er for 168 timer, også weekend. Forskellig handelstid og markedspopulation er en kritisk fortolkningsgrænse.

Kandidater, fravalgt som hovedhistorie:
- Rent kursfald til 62.006 USDT: væsentligt, men udbredt i andre nyheder og ikke specifikt framework-fund.
- 30d rotation proxy steg W46 fra 24 til 33, 90d endte på 33: interessant, men ikke verificeret altrotation og næppe stærkt nok alene.
- Egen forecast-miss: relevant til intern modelaccountability, men strider mod ejerens beslutning om at stoppe scorecard-opslag som hovedformat.

## Endeligt anbefalet X-udkast v2

CYCLE NAVIGATOR / MARKET NOTES 001
16 November 2026

ETF selling slowed. Bitcoin fell harder.

BTC lost 4.5% in the first week of November. Last week it lost 12.7%.

But US spot Bitcoin ETF outflows went the other way: $1.28bn, then $1.07bn.

I checked the BTC spot trading feed I follow. The share of volume initiated by buyers slipped from 50.6% to 48.9%. Not a dramatic change, but the slight buy-side edge had disappeared.

The timing matters, too. ETF numbers cover Monday to Friday. Bitcoin traded down to $62k over the weekend, after those funds had closed.

None of this tells us exactly why Bitcoin fell. It does tell me that ETF flow headlines alone aren't enough.

For now, I'm watching two things: whether spot buying returns and whether ETH can stop losing ground against BTC. Until that improves, a bounce is only a bounce.

## Kilder og reproduktion

1. W45 marked:
`03_DAILY_CAPTURE_LOGS/weekly/2026/W45.json`
Blob SHA `343567105f0155daa95df58e4ecb706ce53a1669`
BTC open 78354.01, close 74851.44: -4.470186%. Tracked spot buy-initiated share 0.5059753690. BTC ETF weekly settled -1281.7 reported million USD.

2. W46 marked:
`03_DAILY_CAPTURE_LOGS/weekly/2026/W46.json`
Blob SHA `3d13f097ac42cf0e9aee6446a9cba4e303c50236`
BTC open 74851.44, close 65351.05, low 62006.00: -12.692328%. Tracked spot buy-initiated share 0.4892639969. BTC ETF settled -1065.3 reported million USD. BTC/ETH 168 of 168 hours observed. ETF sessions 2026-11-09 through 2026-11-13.

3. W46 Master Monday:
`research/api_agent/outputs/weekly/2026/W46/MASTER_MONDAY_REPORT.md`
Blob SHA `04b3e8af098c9ad2db4ae0a6711a0c95f344020c`.
Readback: severe drawdown, negative observed spot activity and ETF totals, late recovery but durable repair not proven. Shadow-only.

4. External primary ETF cross-check:
Farside Investors (US$ million), https://farside.co.uk/bitcoin-etf-flow-all-data/
Nov 2-6 sum -1281.7; Nov 9-13 sum -1065.3. Different clocks from 7d BTC spot price and no causal implication.

## Assertions og forbehold

- Spotandelen er aggressivt købsvolumen på den observerede børsfeed, ikke andel af købere, markedets samlede likviditet, global CVD eller bevis for årsag.
- Uge-ETF-strømme og 7d prisafkast har forskellige handelskalendere. En lavere ETF-udstrømning betyder ikke øget ETF-efterspørgsel.
- Weekendens cirka $62k low verificeret i W46 timeserien og uafhængige nyhedskilder den 16. november.
- Ingen påstand om prediktiv edge, investeringsafkast, køb/salg eller fuldt valideret genopretning.
- Post ikke automatisk. Ændr ikke `latest_published`; afvent ejers godkendelse af eksakt udgave og separate publiceringsbekræftelse.
