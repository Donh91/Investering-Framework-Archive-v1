# W45, ny original CN/B1 sammenligning - Task2 #1596

**Research only, 9 November 2026.** Den oprindelige CN W45-prognose, den uafhængige B1 og sitets frysebevis blev første gang udstedt i samme GitHub-commit ae6a3b5f61ac26e86257d25decd5f2fb96bf0ad2 (2026-11-02 08:19:09 UTC), med registreret frysning 08:19:08 UTC. Research er ikke et autoriseret live-markedssignal.

## Originale data og ny observation

Alle seks inputfiler er låst til deres faktiske Git-blob SHA-1 i scriptet. W45 har 168/168 sammenhængende nominelle UTC-timelys, med 160 komplette candle-endpoints efter den første lovlige 09:00 UTC scoring og **159 hele candles, som også åbnede efter original udstedelse**. Dermed inkluderes ikke preissue-OHLC i den strenge analyse. W46 scorecard er kun efterfølgende facit til W45, ikke en forecast-inputkilde.

| Asset | Observeret LOW/HIGH (USDT) | Original CN (USD) | Original B1 range | CN full-range | B1 full-range | CN overlap | B1 overlap | CN/B1 width |
|---|---|---|---|---|---|---|---|---|
| BTC | 73,510 / 81,196.01 | 72,000 - 84,000 | 74,624.88 - 79,512.77 | YES | NO | 0.640501 | 0.635947 | 2.455x |
| ETH | 2,060 / 2,450 | 2,000 - 2,500 | 2,101.06 - 2,324.69 | YES | NO | 0.780000 | 0.573399 | 2.236x |

W44 originale CN holdt begge low/high inden for et bredt interval, mens B1 var mere placeringspræcis. I W45 har CN både fuld containment og en lidt/større Jaccard-fordel, stadig med mere end dobbelt så brede bånd. **Ingen konsistent modelvinder, ingen selvstændig forsknings- eller porteføljefordel.**

**Videnskabelige blokeringer:** Originalens USD-kvotering er endnu ikke bevist ækvivalent med USDT-truth-tape; upstream historisk first-known kan ikke afledes fra Git-commit, og reel levering til slutbruger er ikke dokumenteret. W44 og W45 er blot to successive testuger i én afhængig markedstidsserie. Ingen prospektivt forudregistreret uafhængig testkohorte eller pris/likviditetsbaseret handelsnytte. F5-shadow med breddebetinget naiv baseline kan ikke alene bevise incremental skill.

**Næste videnskabelige gate:** kør eksisterende ejer #1596 / #1516 og dokumentér fremtidige fastlåste CN, B1, persistence, momentum, volatility og HOLD sammen på identiske 1/3/7-dages tidspunkt/quote/cohort, udfald/abstention, actual first-known, late issue, censoring, block-independent stress og efter-omkostninger. Bevar live W46 og historiske scorecards uændret. Ingen nyt workflow, cron, API, betalt model eller automatisk promotion.
