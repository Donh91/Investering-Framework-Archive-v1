# GCBLO FULL EXPERIMENT — RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_GCBLO
run: 2026-07-25 16:0x CEST / 14:0x UTC (klokanker: Kraken server 1784988187)
rolle: Claude/Fable = adversarial auditor + compute. Governance = ChatGPT. Ingen kanonisk ændring foretages her.
protokol: ChatGPT-spec (frossent grid, resemblance-first, outcome-second). Reference-dokumenter: ChatGPT GCBLO-vurdering (PR #147/#148) + Fable foreløbigt svar 2026-07-25 ~15:20 UTC.

## 1. FROSSET PROTOKOL (før outcomes)
Grid: h∈{1,4,13,26,52}w × L_z∈{26,52,104,156}w(rullende) × EMA∈{4,8,13,26,52} × vægte∈{EQ,GDP,USDSHARE,INVVOL} × valuta∈{A_native,B_usd} × RRP∈{wed,avg,last} × TGA{wed} (WDTGAL BLOCKED_EGRESS) × q∈{.55,.65,.75,.82,.90}.
Tærskler: S_hi=quantile(S⁺,q); S_lo=−0.6908·S_hi (ratio låst af tan-forholdet 80/86). Shape-gate sat≥0.45.
Statemaskine = hans Step 1–4 med halving-maske. Ankre (hans juli-26-chart): SELL 2013-12-23 / 2017-11-27 / 2021-03-15 / 2025-09-15; RE 2015-01-05 / 2019-01-14 / 2022-06-27. 2026-RE scores IKKE (det er selve claimet).
Score=Σ|ugefejl| over 7 ankre (+52 pr. manglende). PASS-bar ≤45.

## 2. HOVEDRESULTATER
R-A REPRODUCERBARHED: 4575 shape-gatede konfig., 3240 med 7/7 signaler. **PASS=0.** Bedste score 106.7 uger (~15 u/anker). Chartet kan ikke genskabes fra opskriften inden for governance-griddet. Original formel: IKKE genfundet — nu demonstreret, ikke blot konstateret.
R-B ASYMMETRI (median |Δu|, bedste-50): s13 16.2 / s17 14.7 / s21 9.7 / s25 8.7 — mod r15 9.0 / **r19 36.3 / r22 35.0**. Salgssiden har delvis makrorealitet; genkøbssiden er ikke-reproducerbar. Direkte støtte til R2 (exit-only).
R-C ARCTAN=KOSMETIK: downcross-datoer for S vs osc(+86) identiske (n=16). ±86/−80 har ingen selvstændig information (bekræfter ChatGPT §"det afgørende problem").
R-D MASKENS ARBEJDE: rå tærskelkryds 29 → maskeret 7. Halving-masken sletter 76 % af signalerne. Det "rene 4-cyklus-billede" er skabt af masken, ikke af oscillatoren.
R-E NUVÆRENDE TILSTAND, selektionsafhængig:
  • bedste-50 (ligner hans historik mest): RE_FIRED 18 %, 76 % har end ikke nået stay-out-zonen (S aldrig < S_lo efter 2025-salget). osc_nu spænder −84…+92 → fortegnsuenighed selv i topsættet (R4-spredningsgate: FAIL).
  • hele 3240-sættet (ingen selektion): RE_FIRED 57 %, median osc_nu −12.4.
  Konklusion: "−78,37 tæt på −80" er ét punkt i en sky der dækker begge fortegn. Ingen robust re-entry.
R-F STEELMAN (hans anker-datoer som strategi, settled Kraken-uger): Sharpe 1.24, maxDD(log) −1.01 vs hold 0.66/−1.82; roundtrips +125/+172/+193 % vs hold. MEN toppræcision falsk selv i egne ankre: solgt −33/−50/−15/−7.7 % under senere cyklustop (missed +50.7/+100.7/+17.1/+8.4 %). Værdien er bear-undgåelse, ikke toptiming.
R-G RE-KVALITET (hans egne ankre): 2015 fwd26 −10 %, MAE26 −41.6 %; 2022 fwd26 −17.6 %, MAE26 −23 %; kun 2019 stærk (+169 %, MAE −7.5 %). 2 af 3 genkøb var tidlige med store MAE.
R-H USELEKTERET PERFORMANCE (alle 3240 maskerede konfig.): median Sharpe 0.58 < hold 0.66; kun 9 % slår 40W-MA (0.87). TOP-1's 1.39 og steelman 1.24 er selektions-/annoteringsartefakter, ikke familie-egenskab.
R-I LOCO: drop-cyklus-{1,2,3} → held-out fejl SELL 24/59/20 u, RE 66/98/42 u. Ingen generalisering.
R-J ABLATION (resemblance): ALL5 106.7 < CB3 188 < FED_ONLY 218 < NO_BOJ 252 < US_NET 269. Chartets FORM kræver global+BoJ. Men foreløbigt svar viste at PRÆDIKTIV kvalitet ligger i US-only (Sharpe 0.67>0.63, robust for lag). Form-driver ≠ edge-driver → stærkt tegn på at chartet er kalibreret på udseende.
R-K MODEL A/B: B_usd dominerer resemblance (107 vs 126). FX-translationen (JPY-svækkelse) er indbygget i chartets form — bekræfter foreløbigt fund (BoJ −0.985 T USD-led ≈ FX).
R-L VINTAGE: ALFRED-fetch BLOCKED_EGRESS (503, genforsøg senere). Udgivelseskalender-dom står alene: uge-06-10-2025-baren settlede 12/10; WALCL for 08/10 udkom 09/10; ECB-ugeopgørelse 07/10. En SETTLED cross "én dag efter ATH" var informationsteoretisk umulig 07/10. Hans eget 07/10-screenshot viser 87,27 = OVER tærsklen + "nearing". Juli-26-claimet er en retroaktiv opgradering LIVE→SETTLED (OTA-v2 taksonomibrud).
R-M TRANSMISSION (3-lag, kreditben BLOCKED): L3-prisgate ville have vendt 2015 (fwd26 −10→+51 %) og 2022 (−17.6→+22.8 %), kostet 2019 (+169→+53 %); MAE forbedret 2/3. NU: L2(DXY Δ13w=+1.93) FAIL, L3 (BTC 66.072 < 40W-MA 79.080) FAIL → staged verdict: WATCH, intet mere.

## 3. AFSTEMNING
Mod ChatGPT-dokumentet: alle ni klassifikationer bekræftet; tre skærpet med rækker (formel ikke-genfundet→irreproducerbar under frossent grid; tærskler ubevist→arctan-kosmetik bevist + fortegnsspredning; regimeværdi lovende→uselekteret median 0.58 sætter baren, endnu ikke slået).
Mod foreløbigt svar (nævnes eksplicit, jf. ordre): 980-config-griddet (8,5 % re-entry, median −97,3) måler NIVEAU under fast ±86/80-geometri; dette run måler STATEMASKINE-tilstand under per-config-tærskler. Begge står; frossent-protokol-tallene er governance-referencen fremadrettet. Lead/lag (peak L=0), benchmark-batteri, BoJ/FX-dekomposition og top/bund-lags fra foreløbigt svar består uændret og indgår som R-baggrund. Én QA-note: rå Kraken-fetch indeholdt live-candle (64.053); verificeret ekskluderet fra alle beregninger (settled 2026-07-23 close 66.072,5, UTC-basis, cross-check ikke ledger).

## 4. BLOCKED_ITEMS
WDTGAL (TGA-ugegennemsnit-akse), BAMLH0A0HYM2 (kreditben L2), ALFRED-vintages, PBoC-serie (3 FRED-kandidater 503/ukendt; anbefal manuel PBoC-månedstabel via hovedframework). Alle blokerer KUN eget lag.

## 5. NEXT_EXACT_EVENT
ChatGPT-afgørelser: (1) EXT-GCBLO-2026-07-24-ledgerrække (maturity 2026-10-23, preregistrering i foreløbigt svar §R6) optages? (2) R2 exit-only + R1 FX-dekomponering promoveres med rækkekrav? (3) R3-mætningsforbud + R4-spredningsgate som generelle optagelseskriterier? (4) PBoC-kilde. Rebuy: LOCKED, uændret, ingen ny evidens for frigivelse — tværtimod (R-E, R-M).
