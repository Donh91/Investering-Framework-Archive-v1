# TechDev ex-top-10 dominance: falsifikation, timing og marginal værdi

**Dato:** 2026-08-30
**Status:** SHADOW_ONLY / REJECT_CURRENT_ADMISSION
**Område:** TechDev, rotation, offensiv opportunity cost
**Primary folder:** `06_RESEARCH_LAB/audit_summaries/techdev_dominance_20260830/`
**Current-main audit anchor:** `5e0fbb913208b8cadf8de46f77c2069b92cbba00`
**Eksisterende owner:** T7 `TECHDEV_CLAIM_LEDGER`, med T3/T5/T6 som sammenligningsområder. Ingen ny test eller engine.

**Leveringsstatus ved PR-forberedelse 2026-08-31:** Den oprindelige skriveblokering er fulgt af brugerens godkendelse til publicering. Pakken er gendannet fra de gemte arkiver og kontrolleret mod nyeste main. Aktuel CI- og merge-status skal læses på den tilknyttede pull request; de historiske beregningsresultater ændres ikke.

## Dom og opgavens faktiske dækning

**REJECT** for at optage eller aktivere det nuværende, utilstrækkeligt specificerede signal som PREPARE-companion. Det er en afvisning af operationel optagelse på det foreliggende grundlag, **ikke en statistisk falsifikation af signalets mulige økonomiske edge**.

Kilde- og metodeauditten er udført. Den primære historiske event study er **DATA_BLOCKED**: originale SAR-indstillinger, indikatorens egen beregningsperiode, reproducerbar OHLC-historik og samtidige signal-vintages er ikke genfundet. Derfor er historisk edge, false-positive rate og numeriske lead/lag **ukendte**, ikke nul. En tom eller ugyldig test må ikke præsenteres som gennemført backtest.

Det sekundære S&P/BTC-appendix er faktisk beregnet. På 2.445 sessioner forsvinder næsten hele den store samme-dags-forskel, når BTC-vinduet først starter efter kendt aktieluk. Ingen af fem efterfølgende horisonter dokumenterer robust positiv effekt. Binær grøn/rød S&P-dag parkeres som førende timingfilter; andre aktie- og makrosignaler er ikke afvist.

| Spørgsmål | Svar |
|---|---|
| A. Reproducerbart? | Ticker-identiteten kan matches til OTHERS.D. Det originale signal kan ikke reproduceres præcist. |
| B. Edge ud over simple baselines? | Ukendt for TechDev-signalet. Baseline- og parametertest er ikke kørt uden de nødvendige data. |
| C. Førende relativt til current framework? | Ikke dokumenteret. Ingen gyldige matchede event/owner-rækker. |
| D. False-positive og opportunity-cost risiko? | Ikke kvantificerbar uden alle events, ikke-events, handlingsregler og prisstier. |
| E. Overførbart til ETF-era? | Ubevist. To udvalgte før-ETF-analogier giver ikke transportabilitet. |
| F. Framework-beslutning? | REJECT nu; bevar kildeaudit under T7. Ingen ny SHADOW_FORWARD_TEST-runtime og ingen ændring af PREPARE/deployment. |

## 1. Det, der faktisk kan rekonstrueres

[Originalopslaget](https://x.com/TechDev_52/status/2094062742386651556) blev publiceret 30. august 2026 kl. 14:00:38 UTC. Det vedhæftede diagram er mærket 13:59 UTC, viser `Crypto Total Market Cap Excluding Top 10 Dominance, %`, `2M`, `CRYPTOCAP` og indikatornavnet `SAR`. De tre annotationer står ved 1. maj 2016, 1. maj 2020 og 1. marts 2026. Billedernes bytes og SHA-256 er registreret i `SOURCE_MANIFEST.json`; billeder er kildebevis, ikke observerede dataserier.

Titlen matcher [TradingViews OTHERS.D](https://www.tradingview.com/symbols/OTHERS.D/). Leverandørens [metodebeskrivelse](https://www.tradingview.com/support/solutions/43000550480-where-do-i-find-crypto-market-capitalization-and-dominance/) definerer TOTAL som top-125 og OTHERS som denne population med BTC og bestemte andre store coins udeladt. Dominance er `100 * OTHERS / TOTAL`. Historisk medlemskab, udelukkelsesliste, supply-revisioner og indeksversion skal følge med en rigtig reproduktion. Dagens rangeringsliste kan ikke anvendes baglæns som historisk univers.

Det er ikke en ligevægtet breadth-indikator eller en direkte mikrocap-indikator. Identiteten

`ændring i log(OTHERS.D) = ændring i log(OTHERS) - ændring i log(TOTAL)`

viser, hvorfor andelen kan stige, mens begge kapitaliseringer falder. Ændringer i supply eller medlemskab kan også påvirke kapitalisering. Derfor skal afkast, relativ styrke, koncentration, faktisk deltagelse og deployment testes særskilt. En procentvis dominance-stigning er ikke i sig selv afkastet på en investerbar portefølje.

[TradingViews SAR-dokumentation](https://www.tradingview.com/support/solutions/43000502597-parabolic-sar-sar/) oplyser standardværdierne start 0,02, increment 0,02 og maksimum 0,20. Dokumentationen beskriver desuden en særskilt indikator-timeframe. Ingen af disse indstillinger er synlige på TechDev-billedet. Standardværdier er en mulig challenger-specifikation, ikke bevis for hans valg. Beregningen bruger high/low og tilstandshistorik; en tegnet close-linje er ikke tilstrækkelig. Den blå flade kan være en area-visning af SAR, men konstruktionen af fladen og teksten “Accumulation” kan ikke fastslås ud fra billedet. En eventuel maske skal testes separat fra rå SAR-flips.

## 2. Den afgørende forskel på tre ure

| Annotation på grafen | Hvis den angiver åbningen på en almindelig 2M-bar | Verificeret første samtidige signaltilgængelighed |
|---|---|---|
| 2016-05-01 | Barluk ville være 2016-07-01 | Ukendt |
| 2020-05-01 | Barluk ville være 2020-07-01 | Ukendt |
| 2026-03-01 | Barluk ville være 2026-05-01 | Ukendt; det aktuelle opslag er fra 2026-08-30 |

Midterkolonnen er en **betinget kalenderberegning**, ikke genfundne signaldatoer. En intraperiode-trigger kan have en anden dato, og en indikator på en anden timeframe kan lukke senere. Det seneste almindelige juli-august-2M-vindue var endnu ikke lukket ved opslaget.

2026-annotationens dato ligger **182 kalenderdage før opslaget**. Selv det hypotetiske 2M-barluk ligger 121 dage før. Ingen af disse forskelle er dokumenteret forspring til frameworket. De viser, hvorfor en martsmarkering ikke må behandles som en verificeret martsbeslutning. Et forward-test-forløb oprettet efter opslaget kan heller ikke kalde marts-august for prospektive outcomes.

Yderligere oplyser TradingView, at medlemsændringer kan skabe indeksudsving, som senere kan [udjævnes manuelt](https://www.tradingview.com/support/solutions/43000743044-why-do-spikes-occur-in-crypto-market-capitalization-and-dominan-ce-charts/). Det beviser ikke revision af netop disse markeringer, men gør historiske vintages relevante. En test på dagens historik alene er højst et retrospektivt replay.

## 3. Alle events, nær-signaler og lead/lag

Der er **tre observerede annotationer og nul uafhængigt reproducerede trigger-events**. Det komplette antal historiske triggers, nær-signaler og fejl er ukendt. De to fremhævede historiske cases må ikke bruges som en 100% hitrate. Selv to hypotetiske succeser i to uafhængige, ikke-selekterede forsøg ville have en tosidet 95% eksakt nedre succesgrænse på kun cirka 15,8%; udvalgte cases opfylder ikke engang den forsøgsmodel.

Artefakterne gør manglerne eksplicit:

- `EVENT_INVENTORY.csv`: de tre annotationer med adskilte tidsbegreber.
- `EVENT_HORIZONS.csv`: 24 efterspurgte event/horizon-pladser, alle uden opfundne returns, MAE, MFE eller scores.
- `LEAD_LAG.csv`: 21 pladser for de syv confirmation-aksepunkter. Tom numerisk lead betyder ukendt, ikke samtidig confirmation.
- `SENSITIVITY_STATUS.csv`: 15 mulige SAR-varianter, fem baselines, tre proxydefinitioner og tre kontroltyper. **26 planlagte sammenligninger, nul udførte primære tests.**

Det rigtige estimat er `første confirmation kendt_at - trigger kendt_at`. Confirmation, der allerede er opfyldt ved triggeren, skal mærkes særskilt, eventuelt med negativt lead. Man må ikke vente på næste confirmation og derved skabe et kunstigt positivt lead. Venstrecensorering, aldrig-confirmation, højrecensorering og manglende data er forskellige tilstande. Kæden må gerne forgrene sig; det er ikke et krav, at alle markører optræder i den antagne rækkefølge.

Matchede ikke-triggerperioder er nødvendige for at måle falske alarmer og missede rotationer. Alle observationer med overlappende 26-ugersvinduer skal grupperes, og 15 parametervarianter på samme cyklus er ikke 15 uafhængige hændelser. Større historisk n skal komme fra reelle hændelser, ikke flere rækker omkring de samme to bevægelser.

Søgningen omfattede aktuelle TechDev-tekster i control plane, offentlige kildeopslag og metadata i restricted plane ved commit `79d26a54f3577c01bd873f649a2edf31be2ffee7`. Ingen navngiven komplet OTHERS.D/OHLC-binding blev identificeret. Den betalte #100-kildes receipt er delvis og blev ikke anvendt som dataset. Alle historiske PDF-binaries er **ikke** udtømmende OCR-gennemsøgt. TradingView [tilbyder ifølge egen dokumentation ikke et data/indikator-API](https://www.tradingview.com/support/solutions/43000474413-i-need-access-to-your-api-in-order-to-get-data-or-indicator-values/). Der var ingen tilgængelig autentificeret chart-eksport. Ingen adgangskontrol blev omgået, og ingen tilnærmet kurve blev aflæst som præcise markedsdata.

## 4. Sammenholdt med current framework

De autoritative filer og deres hashes står i `SOURCE_MANIFEST.json`.

| Eksisterende område | Betydning for denne kandidat |
|---|---|
| T7 TechDev Claim Ledger og Operational Weighting v1 | TechDev-rotation har shadow-rolle. Ingen selvstændig alt-, rebuy- eller porteføljeautoritet. Denne audit udvider kildesporet, ikke antallet af gyldige outcomes. |
| T6 Rotation Survival | Sammenligner ETH/BTC, breadth, BTC.D, deployment og flow-survival mod first-cross, inklusive delay cost. Det er den eksisterende owner for det foreslåede incremental-lead-spørgsmål. |
| T3 Graduated Alt Deployment og T5 FNP | Et PREPARE-varsels informationsværdi og en tidligere positions falske-permissionstab skal måles hver for sig. Manglende breadth/deployment må ikke blive en gyldig deployment-række. |
| ETF-transmission-protokollen | ETF-absorption, stablecoin-supply, aktivitet og faktisk altcoin-deltagelse er adskilte akser. Positivt ETF-print er ikke dokumenteret transmission. |
| External Indicator Admission Gates | Kræver original formel/parametre, source-vintages, tilgængelighedstid, stabilitet og marginal værdi. Visuel lighed og valgte historiske datoer er utilstrækkelige. |
| Early Rotation Pre-Trigger | Et beslægtet, allerede registreret forskningsspørgsmål findes. En ny indikator skal ikke blive en parallel engine eller en ekstra stemme for samme information. |

`backtest_engine/rotation.py` indeholder en konkret engineering-klassifikation, men pakkens `SCOPE.md` tillader ikke at ophøje den til historisk økonomisk eller canonical permission-bevis. At anvende dagens regel i 2016 ville under alle omstændigheder være et **current-rule replay**, ikke dokumentation for en faktisk daværende framework-beslutning.

T11's aktuelle runtime-fil er `QUARANTINED_PENDING_POST_REPAIR_EVIDENCE_AND_ACTIVATION_REVIEW` med nul gyldige divergence-rækker. En ældre slutrapport om aktiveret collection blev derfor ikke brugt som aktuel runtime-autoritet. Round 3-providerdata blev ikke åbnet, koblet til outcomes eller scoret. De særskilt hentede offentlige S&P/BTC-serier genåbner ikke Round 1/2.

Det stærkeste argument for kandidaten er, at mindre coins' relative andel måske vender før ETH-lederskab og bred deltagelse bliver synlig. Det stærkeste modargument er, at samme prisinformation, langsom SAR-decay, indeksændringer eller en efterfølgende valgt maske kan producere et flot signal uden ny beslutningsværdi. Begge forklaringer kræver test; ingen er afgjort af grafen.

## 5. Beregnet S&P/BTC-appendix

Kilder: [Coin Metrics' arkiv ved fast commit](https://github.com/coinmetrics/data/tree/f1a36afb962731c387bb03982758ab0103063da5), deres [PriceUSD-tidsdefinition](https://gitbook-docs.coinmetrics.io/network-data/network-data-overview/market/price) og [FRED SP500](https://fred.stlouisfed.org/series/SP500). Coin Metrics-data er CC BY-NC 4.0. FRED råværdier og kildesnapshots bevares privat, ikke i det offentlige repository.

FRED leverer cirka ti års daglig historik; Coin Metrics' tilgængelige arkiv slutter med PriceUSD mærket 23. maj 2026. Pris mærket dag d er **ved afslutningen af UTC-dag d**, ikke ved dens begyndelse. Derfor:

1. Klassificér S&P-session d efter dens close relativt til forrige børsdag.
2. Brug BTC PriceUSD(d) som entry ved d+1 kl. 00:00 UTC.
3. Mål efterfølgende 1-5 kalenderdage; ingen forudgående BTC-bevægelse indgår som prædiktion.

Flade S&P-sessioner udelades, helligdage springes over ved S&P-ændringen, men ikke i BTC-prisstien. Ingen manglende pris forward-filles. Den amerikanske close antages kendt ved entry. Historiske FRED-publikationsvintages er ikke tilgængelige: testen handler om den kendte indeks-close, **ikke** en dokumenteret rettidig FRED-baseret handelsimplementering. De første 3-4 timer efter normal S&P-close frem til UTC-midnat er heller ikke testet særskilt.

Metoden blev fastlagt før beregningen, efter at socialgrafens påstand var kendt. Dette er explorativ historisk analyse, ikke en prospektiv præregistrering eller ægte out-of-sample-confirmation. Intervaller bruger 2.000 blok-bootstraptræk med 20-sessionersblokke. Null-testen bruger 1.999 cirkulære signalforskydninger og fem-horisont-Holm-korrektion. Cirkulær forskydning har en stationaritetsbegrænsning; overlappende horisonter og regimeskift gør ikke rækkerne uafhængige.

Alle forskelle nedenfor er **basispoint i gennemsnitligt log-afkast**, grøn minus rød S&P-session. 100 bp svarer til 1 procentpoint log-afkast.

| BTC-vindue efter entry | n | Forskel | 95% blokinterval | Holm-korrigeret p |
|---|---:|---:|---:|---:|
| 1 dag | 2.445 | +1,25 bp | -30,16 til +31,69 | 1,00 |
| 2 dage | 2.444 | -2,37 bp | -44,48 til +38,85 | 1,00 |
| 3 dage | 2.443 | +9,77 bp | -42,22 til +58,21 | 1,00 |
| 4 dage | 2.442 | +9,80 bp | -46,96 til +62,76 | 1,00 |
| 5 dage | 2.441 | +8,13 bp | -54,20 til +63,94 | 1,00 |

På præcis de samme 2.445 eligible sessioner er den **samme-dags deskriptive forskel +133,56 bp**, mod +1,25 bp efter den kendte close. Det første tal viser samvariation, ikke et handelssignal tilgængeligt før dagens afkast.

Én-dags-forskellen er -6,60 bp før 2018, +5,08 bp i 2018-2023 og -2,35 bp fra 11. januar 2024. BTC over sin kendte 200D-gennemsnitspris giver +15,95 bp, øvrige dage -23,18 bp. Alle disse én-dags-blokintervaller indeholder nul. Undergrupperne er exploratory, ikke uafhængige bekræftelser; januar 1-10 2024 indgår i totalen, men ikke i de angivne delregimer.

En supplerende, fuldt specificeret strategi holder BTC én kalenderdag efter grøn S&P-session og ellers cash. Over 3.553 kalenderdage bliver brutto-multiplen 4,90x med 74,15% maksimal drawdown. Med 10 bp per envejsændring i eksponering bliver multiplen cirka 1,00x; 1.592 envejsændringer gør omkostningerne væsentlige. Samme 1D-vinduer efter **alle** S&P-sessioner giver 15,82x brutto, og calendar buy-and-hold 133,09x. Disse strategier har forskellig eksponering; multiplerne alene er ikke et risikotilpasset alfaestimat. Ingen af dem reproducerer originalforfatterens uspecificerede strategi.

Originalopslagets [tre dollarbeløb](https://x.com/sminston_with/status/2093838690791694534) er ikke reproduceret: perioden 2010-august 2026, BTC-kilde, timezone, weekender, flat-dage og geninvesteringsregler mangler. Beløbene bør ikke i sig selv kaldes en regnefejl: afrunding af den røde slutværdi til $0,06 er stor relativt til beløbet og kan forklare en produktforskel. Den væsentlige indvending er informationstidspunktet, ikke denne afrunding.

## 6. Hvad kan genåbne spørgsmålet?

Bevar auditten som `REJECT_CURRENT_ADMISSION` under T7 uden betalt dataanskaffelse, schedule eller sensorvægt. Genåbn kun ved nyt kildegrundlag, ikke fordi markedet efterfølgende stiger:

- Præcis script-/settings-identitet, indikator-timeframe, trigger og Accumulation-konstruktion.
- Lovligt tilgængelig OHLC- og medlemskabshistorik med vintages, eller eksplicit mærket reconstructed challenger. Ingen screenshot-digitisering til pseudo-OHLC.
- Et komplet eventregister med nær-signaler og ikke-signaler samt samtidige owner-inputs for de påståede sammenligninger.
- Separat T7/T6/T3-admission og en ny fremtidig, uforanderlig eligibility floor før nye outcomes. Succes, failure, kill, omkostninger og baseline skal være fastlagt inden aktivering.

Et kvalificeret senere studie skal måle tidligere information, falsk PREPARE, falsk permission, maksimal adverse excursion, tid forkert positioneret og missede muligheder på de samme uafhængige episoder. Conditioning skal være kendt ved triggeren: equity risk, BTC-trend, BTC.D, likviditet, breadth og ETF-era-variabler med publikationstid. Uobserveret stablecoin-deployment må ikke erstattes af supply. Fremtidige regimeskift må ikke bruges som filtre for gamle triggerdatoer.

## Reproduktion og kontrol

Udpak den separat bevarede `TechDev_audit_source_inputs_2026-08-30.zip` i en privat mappe. Kør fra repository-roden med Python, numpy 2.3.5 og pandas 2.2.3:

```bash
python 06_RESEARCH_LAB/audit_summaries/techdev_dominance_20260830/audit.py --self-test
python 06_RESEARCH_LAB/audit_summaries/techdev_dominance_20260830/audit.py --inputs /absolute/private/input-directory --output /absolute/temporary/results
python 06_RESEARCH_LAB/audit_summaries/techdev_dominance_20260830/build_inventory.py
```

`audit.py` afviser ændrede input-hashes. Den lagrede FRED-fil er nødvendig, fordi et senere download kan have et andet rullende historikvindue. `APPENDIX_RUN_RECEIPT.json` binder script, metode, input og outputs. Self-test kontrollerer faktisk kausal tidsjustering, fremtidsmutation, manglende prisstier, flade sessioner, dobbelte/omvendte datoer og Holm-korrektion. De syntetiske self-testdata er kun softwarekontrol og indgår ikke i markedsresultaterne.

Ingen Core-promotion, nye markedsregler, ændrede thresholds, holdings, portfolio execution eller gyldige prospektive outcome-rækker er skabt. Den primære mangel er bevaret synligt frem for skjult bag en tilnærmet backtest.
