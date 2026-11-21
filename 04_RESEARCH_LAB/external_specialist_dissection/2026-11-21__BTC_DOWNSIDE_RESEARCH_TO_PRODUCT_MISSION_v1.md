# BTC downside, capitulation, reflexivity og Kompas: adversarial research-to-product mission v1

**Dato:** 2026-11-21, Europe/Copenhagen.  
**Dokumenttype:** Ejerbestilt forskningsmission og integrationsbrief, ikke en ny motor, strategi, autoritetsfil, forskningskø eller aktiv preregistrering.  
**Status:** PROPOSED_FOR_INDEPENDENT_REVIEW / RESEARCH_ONLY / NO_EXECUTION_PERMISSION.  
**Public snapshot:** Archive main b214f083ff55488d7f929f5d1f470130567e77df (2026-11-21 10:50:35Z). Sourcepointers nedenfor er enkelte kontrollerede blobs, ikke bevis for hele arkivets tilstand.  
**Originale ejere:** Research intake #1512; Strategist/adjudikation #1157; Task2 og metode #1596; Forward Path/CN #1516; risk-to-action #1553; datalinje #1827; S1 release/orchestration #1156. Alpha-konsument: Meme-Alpha-Lab #228/#77/#98.  
**Ændring i denne PR:** præcis ét read-only researchdokument. Ingen workflow, JS/Python-model, tests, scheduler, API-pakke, kode, source write, offentlig siteændring, privat data eller porteføljehandling.

## 0. Ejerbeslutning, den mindste relevante indsats

Første og højeste opgave er at finde årsagen til, at Cycle Navigator i november 2026 beskrev et svagt marked, men samtidigt udsendte prisforventninger og downside-bånd, som ikke fulgte det efterfølgende accelererende fald. Årsagen er IKKE på forhånd kendt. Mulighederne er kilde- og tidspunktsfejl, en faktisk manglende inputfamilie, dårlig formidling mellem eksisterende risiko og pris-output, eller strukturelt for smalle nedre haler. Test først om et eksisterende signal ikke blev forbrugt, før nogen ny signalmotor overvejes.

Anden prioritet er at skelne (a) fortsat forværring, (b) tvangssalg/kapitulation, (c) en mulig kortvarig stabilisering, og (d) faktisk tilbagevendende efterspørgsel. Disse må ikke sammenblandes med udsagnet "BTC-bunden er inde". Prognose, risikoadvarsel, prisinterval, investorbeslutning og økonomisk værdi er forskellige claims.

Hvis fase 1 alene dokumenterer en eksisterende wiring-fejl, repareres den via det eksisterende ejerskab. En ny ML-feature er da ikke accepteret. Hvis en simpel ATR-/persistence-baseline er nok, skal den komplekse kandidat dræbes. Succeskriteriet er ikke et stort forskningsdokument, men ét kildebundet, selvkritisk og nyttigt produktforløb fra original udsendelse til brugbar brugerflade og verificeret effekt, eller et ærligt afslag.

## 1. Eksplicit stopliste og mandat

**Tilladt nu:** public-safe kildeundersøgelse; eksisterende test- og PR-overlap; original først-kendt udstedelse; skema- og metodeaudit; adversarial edge-hypoteser; deterministiske tests på syntetiske fixtures i en senere særskilt godkendt PR; kun read-only undersøgelse af 2026-11-udfald med tydeligt RETROSPECTIVE_DIAGNOSTIC; dette dokument som research-PR.

**Ikke tilladt af denne missionstekst:** Round 3 hypothesis-testing, outcome scoring, effektberegning eller PnL; retroaktiv ændring af W45-W47; ændring af officiel CN-score/forecast; nye automatiseringer, parallel Research Lab, autonome reviewers, scanner, prognosemotor, nye wallet-arm eller alle-aktiver-deploy; direkte handelsordrer; nye finansielle beslutningsregler; privat raw/normaliseret providerdata i offentligt repo; Vault handling; ændring af S1-boots, releasepolitik, .github eller opdatering af main uden exact-head review. Ny betalt Sol/Astra/Claude API-dispatch kræver særskilt gældende model-/budget-/owner trigger. Standard for denne mission: USD 0 paid API. Ingen automatisk fallback til Astra.

Dette dokument er et supplerende forskningsinput til den allerede eksisterende MASTER_PLAN_v1 på Bridge claude/log, reports/claude/plan/MASTER_PLAN_v1.md (blob 5f738b4820354e42083ba3a838b53fdc67d3841f); det ændrer ikke Master Plan, Current pointer eller ejerbeslutningerne. D1 er public, close-only, med separat beskrivende intraweek_breach og ingen score-effekt. D2 placerer Pages workflow-trigger i planlagt Fable W5 re-chain, ikke #2277. D3 giver RISK-02 et muligt W48-startvindue kun ved rettidig videnskabelig accept, ellers W49; start må aldrig tilbageføres. Bridge OWNER_DECISIONS_20261121.md blob f737ad1f21f18cf6572a5487e47bd5b4934bfcf1.

## 2. Overlap, kill og afhængigheder før enhver ny forskning

| Del | Eksisterende hovedspor | Vores disposition |
|---|---|---|
| BTC halverings-/fireårscyklus | Archive PR #2281, #1596/#1516 | DEDUP_TO #2281, hverken ny cyklusmodel eller kalenderbaseret promotion |
| VIX term stress / 72h episode | Draft PR #2284, #1596/#1553 | DEDUP_TO #2284, særskilt review; ikke en skjult erstatning for P0 |
| Nov 16-20 videnskabeligt audit | PR #2282 | Brug kun reelt nyt forbrugerkritisk delta, ingen gentagelsesrapport |
| L04 ETF band location | Oprindelig prereg under #1596/#1516/#1827, A1-addendum merged som #2283 ved main b214f083 | Ingen parameterændring, 26 fremtidige kohorter; revideret basisklokke skal accepteres som egen gate |
| EQM/BTCAnalytica | #1512/#1530/#1157; specialist audit og offentlig replay | SOURCE_NOT_REPRODUCIBLE for vendor; genbrug negative historiske resultater |
| MVRV/SOPR/BlockHorizon | Existing onchain research og privat binding, prospective gate | Ingen ny feature før kilde-admission; tidligere MVRV-udfald negativt |
| Pullback/Task2 | #1596/#1553; T5 OI/funding, divergence, failed recovery, false alarms, stablecoin, changepoint | Forbind eksisterende inputfamilier, ingen ny T5-kø |
| CRE shadow research | 06_RESEARCH_LAB/compass_research_engine_v1; eksisterende Chat CRE task | Kun kilde- og registry-ejet tests, ingen uafhængig scorer |
| Alpha Lab | MAL #98 sellability, #77 recall/outcome, #228 portal design | Kun verificeret, versioneret public-to-private regime-forbrug, paper-only, ingen ny scanner |
| Kompas site og scorecard | MASTER_PLAN_v1 P1, #1516/#1596 | Implementér evt. i den allerede planlagte produkt-PR, ikke her |
| S1 | #1156, W2b og aktiv task | Release steward og verifikation, ikke den der opfinder hypoteser eller godkender egen kode |

**Backpressure:** Research Lab #1512 har maksimum TRE aktive research-to-implementation handoffs framework-wide. Denne dokument-PR er ET RESEARCH-INTAKE-FORSLAG, ikke en fjerde aktiv håndoff. Før eksekvering skal #1157 deduplicere og afgive eksplicit disposition. Ingen ny Codex candidate, PR, betalt mission eller test-ID, før ejeren og intake er afklaret. Gammel kilde og ingen ny substans = NOOP.

## 3. Kildekort og red-team-afgørelser

### 3.1 Ajax Crypto, 13 månedlige BTC-candles

Brugerens skærmbillede hævder, at alle bear-markeder varer 13 månedscandles, og at månedscandle 13 i november 2026 varsler et bull-marked. Dette er et anekdotisk, endpoint-sensitivt plot, ikke et kalibreret 2026-bundsignal. 13 viste candles er ikke nødvendigvis 13 måneder fra onset og er ikke 13 røde candles. Inkludér korte mislykkede bear-episoder, alle historiske cyklers alternative onset/exit-regler og 2011. Store top-til-bund-episoder med cirka 12-13 måneder er for få uafhængige hændelser. Forsøg IKKE at publicere et sandsynligt vendetidspunkt ud fra et historisk histogram alene.

Testbar hypotese, K-CYCLE: Kun hvis en kalender-/bear-varighedskomponent føjer prognoseværdi til identisk source-clock pris/trend/regime champion og overlever leave-one-cycle-out. Placér i eksisterende #2281, ikke her. Kill ved selektiv episodeudvælgelse, endpoint-/candle-definition-ustabilitet, historiske labels skabt med kommende trough eller udglatning uden information-time. Ingen "bull om ni dage".

### 3.2 Astronomer Zero, elproduktionsomkostning og 50k-gulv

Screenshot-kæden indeholder 2W purple modelbånd, E-cost estimeret cirka USD 60.300/BTC, 17 historiske "touches", cirka USD 56k spot, påstand om USD 50k floor og en personlig fase 3 for planlagte longs. Dette er SOURCE_CLAIM, ikke 17 uafhængige prospektive beslutninger. Før historisk test skal en reproducerbar metode definere netværkshashrate, difficulty, energi per hash, effektivitetsfordeling, kWh-pris, blokudbytte/fees, modelrevision, datavintage og time-as-of. Minearbejdernes omkostninger og difficulty er endogene; en prisnedtur kan reducere omkostningen og føre til miner-salg. Minerproduceret ny issuance er ikke flertallet af den eksisterende BTC-forsyning.

Testbar hypotese, K-MINER: Stressratio og as-of ændring i hashprice/minerøkonomi forbedrer fremtidig downside-risk eller kapitulationskontekst ud over pris/trend/ATR, efter genberegnings- og kildeforsinkelsesstresstest. Fald ikke i "price cannot fall below production cost" fælden. Cambridge-modellen har eksplicitte antagelser og CoinShares viser selskabsvariation. Brug elektropris-scenarier (0.02, 0.05, 0.065 USD/kWh) som deskriptiv sensitivitet, ikke bagudvalgt bund. Et eksternt modelplot er ikke first-known historisk output.

### 3.3 Soros, refleksivitet

YouTube https://www.youtube.com/watch?v=oCaCrWzFPYY er George Soros' General Theory of Reflexivity lecture, ikke en direkte BTC-analyse. En mekanisme med forventninger -> flows/gearing -> pris -> forventninger kan være selvforstærkende eller korrigerende. Falsificér med to retninger af laggede forbindelser og uafhængige eksogene begivenheder; simultan korrelation er ikke kausalitet. Eksisterende DWF Labs' ETF-studie finder betydeligt mere forhold til foregående BTC-afkast end følgende fem dage, hvilket udfordrer ETF-flow som selvstændig forecast. Den valgte mekanisme skal slå pris-only, kontemporær-stress-kontrol og forsinkede flow-proxies.

Testbar hypotese, K-REFLEX: Et lille, frozen feedback-state diagnostisk output kan forudregistreret opdage risikoeskalering/afvikling med bedre lead-versus-false-alarm-afvejning end eksisterende risk-state, uden selv at blive til et ekstra stemmesystem. Kill ved kun nutidig beskrivelighed, afhængige features, tidsforskydningsartefakter eller manglende performance fremadrettet. Mulige labels er eksplorative, aldrig live-gates.

### 3.4 Stærkere, men ikke ukritisk, eksterne kilder

- Glassnode Week Onchain Nov 17 2026: realiserede tab, ETF-udstrømning, kortsigtet køber-cost-basis og demand-svaghed, rapportens tidspunkt og målemetode er kritiske. https://research.glassnode.com/the-week-onchain-week-46-2026/
- Glassnode Market Pulse Nov 16 2026: spot/perp CVD, ETF-dynamik og optionsskew, kilderevisioner og historisk adgang skal undersøges. https://research.glassnode.com/btc-market-pulse-week-47-2026/
- CryptoQuant Nov 20 2026: negativ Coinbase-premium sammen med positiv funding er kontekst, ikke allerede bevist forløber; alle støttezoner bliver stale ved efterfølgende brud. https://cryptoquant.com/blog/6b0033dc69f4771eacc5f395-How-Deep-Is-the-Bitcoin-Dip-What-On-Chain-Data-Says
- Cambridge: antagelser om elpris/ASIC/difficulty forhindrer universelle cost floors. https://ccaf.io/cbnsi/cbeci/mining_map/mining_data
- CoinShares Q2 2026 miner cost: selskabs- og accounting-forskelle betyder, at virksomhedstal ikke er én netværksomkostning. https://etp.coinshares.com/us/insights/research-data/bitcoin-mining-report-q2-2026/
- DWF Labs Oct 2026 ETF timing: 694 sessioner, rapporteret ca. 0.54 korrelation med tidligere BTC 5d afkast og 0.03 med følgende; check definition og kilde før genbrug. https://www.dwf-labs.com/research/do-etf-flows-predict-where-bitcoin-goes-next
- Soros forelæsning: https://www.georgesoros.com/2009/10/26/general_theory_of_reflexivity_lecture/
- Galaxys BTC cycle review, med episode-definitioner: https://www.galaxy.com/insights/research/bitcoin-50-week-moving-average-bear-market-ceiling-200-week-floor-analysis

Kilderne er hypotesegenererende. Ingen eksternt rapporteret graf eller historisk panel erstatter et første-kendt, provider-identisk og reproducerbart datasæt.

## 4. Det observerede problem, med tal der MÅ OG IKKE MÅ bruges

Originale offentlige CN-dokumenter:
- W45: 05_CYCLE_NAVIGATOR/weekly/2026/W45/CYCLE_NAVIGATOR_READABLE.md, blob 2a52581b77ae098bd6034f42854cf536548c1e53. MIXED/downside, 72k-84k BTC weekly band; ingen kalibreret 2-3w sandsynlighed.
- W46: 05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_READABLE.md, blob c2c1abb9d12105bbe70cd3b92c56bfa1dcbd43d1. 15. november forventet BTC close 74,799.94 USDT, expected daily low 73,584.69; original 0/7 expected closes på første udgave og senere samme-dags rettelse er BEGGE historiske udstedelser.
- W47: 05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_READABLE.md, blob 56374828f5a25bd3fd1ce98715e39c561b665667. 20. november forventet close 64,834.98 USDT / low 63,803.60; 21. november forventet close 65,551.40 / low 64,454.88.
- Eksternt observerede CoinGlass USD-candles er i forrige brugertråds researchmateriale gengivet med 15. nov close ca. 65,305 og 20. nov ca. 58,799. Different venue/quote, dynamiske sider og first-known endnu ikke bound: DIAGNOSTIC_ONLY, aldrig officiel score. 21. nov intradag 55,1k vs W47 low 64,455 er deskriptivt floor-breach, ikke afsluttet 21. november lukning.

Her er det substantielle problem: risikoen var delvist beskrevet, men det valgte punkt og især nedre hale blev overhalet af markedets fald. Én årsag skal IKKE udledes af to udvalgte store fejl. Gentag på fuldt antal eligible, originalt udstedte W45-W47-dage samt efterhånden andre perioder, med samme quote og completed-UTC-candle. Officielle outcome- og source-ejere bestemmer scoring. W47 dagslukninger efter denne PRs oprettelse er ikke indeholdt som facit.

### F1, præcis forensisk spørgsmålsstilling

"For hver oprindelig udstedt og faktisk tilgængelig CN-forecast, hvilken earliest pre-issuance observation eller komponent, hvis nogen, indikerede større nedadgående hale, og hvorfor blev den ikke leveret til den konkrete pris-/risk-konsument?"

Adskil mindst:
1. DATA_TIMELINESS, input var ikke tilgængeligt, blev revideret, havde tidszone-/quote-/venue-mismatch eller nåede ikke forbrugeren.
2. FEATURE_MISSING, upstream observerede ikke en informationstype, som retrospektivt ser nødvendig ud. Dette er kun en HYPOTESE, ikke en bevislig feature.
3. MODEL_CONTEXT_ASSIMILATION, upstream risiko var til stede men blev ikke brugt i forecast-lokation, bands eller alarm.
4. TAIL_UNDERCOVERAGE, model-/banddesign undervurderer stress- og regimeskift i distributionens venstre hale.
5. PUBLIC_CONSUMER_DELIVERY, korrekt eller usikker information nåede ikke live site/API-bruger i tide.
6. UNKNOWN_OR_MULTIPLE_CAUSES, samtidig flere årsager eller utilstrækkelige beviser.

Krav: for hver dato original file blob, første GitHub server-recorderede udstedelse, provider available_at før forecast, consumer seen_at, source cutoff, UTC target, completed-bar proof, alle alternative/bortfaldne versioner, status, baseline, risk input, output, actual og abstention. Git-commit-tid alene er ikke bevis for upstream first-known eller slutbrugerlevering.

## 5. Afhængig forskningsplan, én primary delta ad gangen

### G0 SOURCE + CONTROL-PREFLIGHT, før scoring

Executor: existing Research Lab #1512 og Task2 #1596; gerne deterministiske/parallelt uafhængige read-only inspectorer, men én samlet outputpakke. Input: current AGENTS, branch/main SHA, cross-plane boundary, issue #1596, #1516, #1553, #1827, #1157, #1156, aktuelle original CN/B1/A issued files og native machine receipts, data owner/clock. Output: SOURCE_CENSUS_AND_OVERLAP_NOTE med antal eligible/missing, eksakt dataklasse, tidsregler, original/final versions and consumer mapping. Ingen hændelsesscoring. Stop ved private data authority unavailable eller source-clock ambiguity, ikke proxy-udfyldning.

### G1 NOVEMBER FORECAST MISS, primær P0

Executor: #1596 / #1827 / #1516. Freeze original source and comparator first. Inspektér W45, W46 initial og revised, W47; anvend fuld denominator med alle udstedelser og udgåede/afviste dage. Separat indikatorer:
- issuance/consumer coverage og missing-as-UNKNOWN;
- expected-close absolute error, median/MAE kun for maturerede og samme quote/venue;
- daily / weekly lower-tail containment, interval width og interval score (Winkler når nominelt dækningsmål faktisk er fastlagt);
- pre-issue bearish risk versus issued expected price delta;
- first detectable deterioration, first issuer/consumer evidence, alert lead/lag og false-negative/false-positive burden;
- persistence/B1, original CN og deterministic ATR 1.5/2.0 / volatility benchmark på identiske klokker (juli CN audit fandt ATR-benchmarks stærkere end simple envelopes, men ikke en universal ATR-kalibrering);
- skeln lukkekurs fra intraday low; anvend D1 close-only scoring, særskilt intraweek_breach descriptor.
Resultat: ONE root-cause classification per failure family med kilde + patch-locus eller SOURCE_BLOCKED. Ingen optimeret/ny bandparameter fra W47. Kill alt nyt ved eksisterende wiring-fix eller source-blocker. Rapportér både stærkeste evidens FOR og IMOD den valgte årsag.

### G2 DOWNSIDE TAIL / CHANGEPOINT, betinget P1 shadow challenger

Kun hvis G1 viser en dokumenteret og ikke-allerede-løst model-/tail-mangel. Eksisterende T5-CHANGEPOINT/T5-FAILED-RECOVERY og Kompas/HRE ejer en mulig minimal udfordrer. Definér én forecast-time feature/fallback med tidligere afsluttede ATR/realized volatility + price trend; en ekstremt simpel unconditional ATR eller no-change/persistence er baseline. Vælg én primary outcome FØR fremtidige data, f.eks. same-clock downside interval score ved fastlåst nominelt dækningsmål og mindst lige så stram false-alarm-byrde, ikke "bedst på W47". Sekundært report lower-tail miss count, sharpness, abstention, lead-time og risk alert cost. Sensitivitet: fuldt stress-/rolig-perioder, quote/venue, completed OHLC, embargo, 72h event clustering, multiple-testing budget. Fremadrettet evidence tilpasset registreret test; ikke nye R3 tests. Kill hvis simple baselines er lige så gode, effekten kun findes i retrospektive W46/47 eller sættes af én episode.

### G3 CAPITULATION VS RECOVERY, betinget P1 efter source-clocks

Eksisterende T5-OI-FUNDING, T5-SPOT-DERIV-DIV, T5-STABLECOIN, ETF temporal source and BlockHorizon. Adskil:
- forcing/supply: liquidations, OI level/delta i egnede enheder, funding, basis, miner sales, options skew;
- absorption/demand: completed-hour spot CVD, premium/basis, liquidity replenishment, verified market depth/spread, positive independent capital flow;
- persistence/participation: BTC hold, ETH/BTC, breadth survival, stablecoin deployment, ETF/realized cap, with correct availability;
- invalidators: new downside low after apparent washout, fading spot buying, source outage, correlated feature duplicates.
At most ONE additional shadow explanatory output in EXISTING risk owner, not a new five-vote classification engine. Frozen semantic labels for research only: DETERIORATING, CAPITULATION_NOT_RECOVERY, STABILIZING_UNCONFIRMED, DEMAND_RECOVERY_EVIDENCE, UNKNOWN. "Bunden er inde" er ikke et output. Validate dependence within groups, lead-lag both directions and interaction against price trend controls. Kill if no lead over champion or poor false-warning economics.

### G4 SECONDARY FALSIFICATION, P2/P3 low-resource lanes

K-MINER: Cambridge price-per-BTC sensitivity at 0.02/0.05/0.065 USD/kWh, hashprice/difficulty/fees lag, fleet heterogeneity, cost-endogeneity, source vintage; no hard floor and no backfill. K-CYCLE: delegate to open #2281. K-REFLEX: DAG with belief proxies, lagged feedback, macro common-cause controls and placebo time shifts. MVRV/SOPR: old result remains negative pending NEW admissible evidence. EQM / rank / DCA: old retrospective DCA comparison is NOT a live allocation instruction. Use bounded source/design verdict REJECT, EXPLANATORY_ONLY or FORWARD_TEST_CANDIDATE without new runs unless a clearly documented material delta appears.

### G5 CONSUMPTION TEST, only for evidence admitted by owners

No value until a real consumer reads the actual frozen output. For public Kompas, receipt chain is actual forecast/score source -> site mapper -> displayed score and D1 close-only vs intraday flag -> user-facing timestamp and correct NONE/UNKNOWN. Existing MASTER_PLAN_v1 P1 owns implementation; no separate rebuild. For Alpha, only owner-approved public-to-private Archive projection with immutable projection hash, issued_at <= decision time, stale/missing fallback, readonly consumption; existing MAL arena/paper_wallet_v4 uses sellability, execution realism, slippage and VOID as actual outcomes. Paper-wallet outcome row must cite that precise regime snapshot, otherwise UNKNOWN. No MAL->Archive private return, no live trading, no new scanner, no implied Alpha edge. If consumer cannot show data or only reads placeholder, mark NOT_INTEGRATED even if report and CI are green.

### G6 SCIENTIFIC ADJUDICATION AND GOVERNED IMPLEMENTATION

Research Lab #1512 nominates max ONE actionable delta/family and its exact owner; Strategist #1157 emits only allowed disposition: REJECTED_FALSIFIED / DEDUPED_TO_EXISTING_OWNER / SOURCE_BLOCKED_WITH_TRIGGER / PROSPECTIVE_COLLECTION_ONLY / FORWARD_TEST_PREREGISTERED / APPROVED_FOR_IMPLEMENTATION_REVIEW / NOT_DECISION_USEFUL. Attach no more than 3 active handoffs. A reproducible bounded code defect follows .agents/skills/codex-intake/SKILL.md: source+reproduction -> schema-bound CODEX_RESEARCH_CANDIDATE PR -> only official maturation controller may mark CODEX_READY -> one scoped original-owner Codex PR -> independent exact-head review. Scientific hypotheses do NOT become Codex ready. P1 site changes via existing P1 owner, private MAL via MAL #228/98 and separate strict data boundary. S1 #1156 only orchestrates eligible tasks and verifies closure.

### G7 POST-MERGE OUTCOME AND RESTART CONDITIONS

One accepted PR must pass native exact-head CI, independently qualified review (reviewer ≠ author), privacy/source/permission checks, changed-blob readback against approved head, actual main+consumer evidence; only then MERGED_VERIFIED, not simply "PR open". If real new natural observations prove absence of improvement, return to #1157 as REGRESSED / KILLED with original negative record, not retune historic cohort. Completion states: VERIFIED_CLOSED, FALSIFIED, DUPLICATE_CLOSED, BLOCKED_WITH_EXPLICIT_TRIGGER. No indefinite WATCH. Report next observed trigger and one responsible owner. Stop repeated reviews when evidence unchanged.

## 6. Forskningsmetode, clocks, data og statistik

**Data unit:** independent forecast issuance / forecast target / episode, not an arbitrary hourly file count. Raw OHLC can provide many features, not many independent bear-market replications. Labels crossing 72h windows group into episodes; overlapping events are not unique true positives. Market regime split at minimum pre-ETF and ETF-era, multiple unique stress and calm episodes; do not claim power where few episodes exist.

**Timestamp contract:** event_time, collector_observed_at, provider_published_at, first_known_at, source_captured_at, original_issuance_at, consumer_available_at, source_revision_id, target_completed_close_at. Null -> ineligible/UNKNOWN per owner, not silently advanced. Check market session calendars and timezone (US ETF flows Friday availability versus UTC Monday cutoff), quote identity USD vs USDT, close vs wick, late ETF, future-refit regressions, survivorship, missing and duplicated files. A historical CSV downloaded today only proves retrospective archive availability, not earlier as-of truth.

**Common comparators:** official original CN risk; original issued forecast; price-only persistence; B1 band and Challenger A only on actually issued/matured source clocks; price-only trend; ATR1.5/2.0 with frozen causal lag. Do not mix horizon 12h/1d/7d/21d or score UNAVAILABLE/NO_EDGE as direction. For intervals use proper scoring, nominal coverage, average width and lower-tail coverage, report no-signal/abstention; for alerts use detection delay, per-episode recall, false alarms per calendar time, warning burden and economic cost of false exit/missed risk. For capital effects require separately preregistered and authorized paper cohorts with fillability/fee/missed-opportunity denominator, NEVER R3 analysis before firewall lift.

**Statistical trust:** train-only features; rolling-origin walk-forward; purge and embargo; frozen feature family and single primary endpoint; negative controls such as shuffled lag/permuted signs, no-ETF-days, stale sources, placebo shift, no-skill price baseline, leave-one-era-out; cluster-aware uncertainty. Multiple comparisons ledger and no retroactive "best settings" promotion. Report actual distinct effective N, not row count. No deterministic success if power is insufficient. Choose a kill condition before prospective observations: e.g. no incremental paired endpoint gain, materially worse tail false alarms/coverage, high source abstention, untraceable consumer or negative independent review. The numeric safety tolerances are to be frozen by ORIGINAL owner prior to prospective enrollment, never invented in this research memo.

**Adversarial input tests for any later code:** stale/absent snapshot; current data passed as historical vintage; quote inversion; future-dated candle; unfinished candle; UTC/US equity-session mismatches; ETF flow arriving after issuance; duplicate episodes; adversarial/revised chart; degenerate ATR; price gaps; source outage; same info double counted as two evidence votes; cost-floor moving with price; all bearish confidence but upward point forecast; low without close; missing/expired private projection; wrong hash; same agent self-approval; wrong PR head; negative controls where the challenger MUST abstain. Tests must be sensitive to mutated protections, not just nominal green fixtures.

## 7. Særlige fund fra eksisterende forskningsarkiv, som skal bevares

- 06_RESEARCH_LAB/onchainmind_source_admission_v1/RESEARCH_EXPERIMENT_SPEC_v0_1.md blob 99e19eae3052bc731ee82e2e965806bbf4d70823: 48 månedlige MVRV replay-observationer, NO_ROBUST_INCREMENTAL_PREDICTIVE_VALUE mod simpel pris baseline. Ikke ny stor MVRV sweep.
- 04_RESEARCH_LAB/external_specialist_dissection/2026-11-18__EQM_001_VALUATION_DISAGREEMENT_AUDIT_v1.md blob 39754859960bc9d7a001396ea250a5fb4eaa08c6: leverandør EQM SOURCE_NOT_REPRODUCIBLE; retro diagnose understøtter ikke vendor predictor.
- 04_RESEARCH_LAB/external_specialist_dissection/2026-11-19__EQM_001_RISK_TREND_DCA_CHALLENGE_v1.md blob 9e58a13c024646755899187f1c3b40265f63e216: matching gross exposure/fee er afgørende; fixed DCA slog de undersøgte risikoforskudte DCA-cases i fuld retrospectiv sum. Intet prospektivt investeringsråd.
- 05_CYCLE_NAVIGATOR/calibration/2026-07-08__cn-rd-audit-regime-phase-range-calibration__canonical.md blob 790612a442b55bcbe15d127dcb723fb521e76111: walk-forward labeling; defensive value per return foregone; 1.5x ATR var en hårdere, ofte bedre benchmark end et bredt envelope. ETH/BTC-threshold alene har høj fakeout risk.
- 06_RESEARCH_LAB/compass_research_engine_v1/README.md blob 3f79b17e6a54bb9353e4d0163c86191242969808: prospective first-issued evidence gate er ikke automatisk opfyldt af bestået syntetisk kode.
- 06_RESEARCH_LAB/blockhorizon_source_candidate_v1/ASTRA_RESEARCH_PROTOCOL_v1.md blob bff4d893334a310372f8b31b8bc862e83f59d60c: private source binding, leakguard, no forward result fra 2029 model-grid.
- 06_RESEARCH_LAB/audit_summaries/2026-10-14__TASK2_DR01_DR05_PUBLIC_RESEARCH_INTAKE_v3.json blob 1d213a05e4811f271b7febb85f44959da6f7a28f: already owns relevant T5 families. Ikke flere agentkøer.
- 04_RESEARCH_LAB/external_specialist_dissection/2026-11-05__CROSS_FRAMEWORK_OSS_SOURCE_SNAPSHOT_v1.json blob 4a8642669b2c6e24327b88a991c9f92d7276c53c: already assessed Qlib (time as-of), River ADWIN, ruptures PELT, LEAN fills, Hummingbot paper-trade and CCXT as possible primitives. Prefer test of smallest behavior, exact upstream revision/license/rescanning before copying.
- 04_MARKET_LEARNING/handlekompas/research/2026-11-19__KOMPAS_L04_ETF_FLOW_LOCATION_PREREGISTRATION_v1.md blob 7a285ff2d275d442113e053989ba36d25bff6a64: original L04 contract, W48 prospective, 26 cohorts, 0.25 h band offset. Read actual #2283 merged baseline-clock addendum on main before any test.
- Existing Research Lab Sol queue research/api_agent/research_lab_sol/RESEARCH_LAB_SOL_QUEUE_v1.json blob 998f2d739ceb961c3a20f9ac114255fd36d08396: ACTIVE, 31 entries, max_active_missions 1 at inspected snapshot. No parallel release, no consumed ID repeat.
- Research #1512 workflow is SOURCE/OVERLAP -> FALSIFICATION -> #1157 DISPOSITION -> original owner -> #1156 verification -> final observed outcome. This mission is a single intake family, not permission to skip the pipeline.

## 8. Skills og roller, fra spørgsmål til verificeret integration

Dette er den præcise rækkefølge, og SKILL-filerne skal genlæses fra det aktuelle commit, ikke et ChatGPT-hukommelsessnapshot:

| Trin | Nødvendig skill/metode | Hvorfor, konkret input/output | Grænse |
|---|---|---|---|
| 0 | .agents/skills/canonical-context-router/SKILL.md | Pin original owner, index, branch, data plane og operative current outputs | Ingen prognose/handling |
| 1 | .agents/skills/adaptive-analysis-methods/SKILL.md (pilot) | Vælg primært CAUSAL-AS-OF FORENSICS og én supplerende RED_TEAM; afvis method inflation | Ingen automatisk betalt model |
| 2 | .agents/skills/developer-source-research/SKILL.md | Opdater officiel downstream teknisk kilde/OSS license eller API-timeclock, ikke som market-signal oracle | Public-safe, pin source/licens |
| 3 | .agents/skills/research-lab-red-team/SKILL.md | Frozen claims, sources, baselines, independent countercases, false negatives, falsifiers, verdict | Ingen selvpromovering |
| 4 | .agents/skills/research-parallel-lanes/SKILL.md (eksplicit, pilot) | Del uafhængige læseopgaver: A clocks, B model/wiring, C vendor cost, D consumer; afhængig syntese serialiseres | Ingen nye agents/jobs uden særskilt lovlig runner |
| 5 | .agents/skills/prospective-evidence-ledger/SKILL.md | Undersøg om allerede REGISTRERET fremtidig protokol faktisk har immutable original row, maturity og matched source | Skaber ikke ny test; R3 scoring OFF |
| 6 | Data plugin: analyze-data-quality / validate-data / build-report | Kontroller completeness, timestamps, duplicate, quote/venue, regnestykker og kildetro forskningsrapport | Metodehjælp, ikke autoritet |
| 7 | .agents/skills/conclusion-challenge-loop/SKILL.md (pilot) | Én stærk post-conclusion gencheck mod billigste baseline, modbevis og produktbehov | Gentages kun ved reel ny evidens |
| 8 | .agents/skills/archive-governance/SKILL.md | Dokumentér disponering på isoleret branch; korrekt offentlig/privat placering, blob readback og indeks/routing | Ingen direkte main writes, ingen Vault |
| 9 | .agents/skills/codex-intake/SKILL.md, kun ved reproduceret kodefejl | Frys original failing case, schema candidate, positive/negative/mutation test, kun maturation kan markere CODEX_READY | Ingen selvdeklareret CODEX_READY |
| 10 | Original PR-review og S1 #1156 | Same-head native CI, independent Codex/Claude review, owner lane, squash merge/readback, consumer/runtimereceipt | Ingen self-review/self-merge |
| 11 | .agents/skills/skill-quality-gate/SKILL.md, kun hvis skills ændres | Evaluer ændret skill mod frozen no-skill baseline og negative tests | Static inspection er ikke performance |

**Højeste effekt i praksis:** Ingen ny skill opfindes. Skills er callable arbejdsprotokoller, ikke bevis for at jobs faktisk kører. Research Parallel Lanes' enkelte parallelværktøjsreads kan udføres i én chat nu, men vil ikke blive selvkørende bagefter. For vedvarende drift må man kun bruge den allerede eksisterende Task2/CRE/S1/MAL schedule og dens verified native receipts. Intet i denne PR tilføjer en automation.

## 9. Konkret rollesplit, ingen lukket epistemisk kreds

- **ChatGPT Research Lab intake:** indsamler kildebundet materiale, modsiger opslag, foreslår én delta og forbereder dokumentation. Må aldrig skrive både en market-model og erklære den økonomisk bevist.
- **Eksisterende deterministiske scripts/PR-only CI:** reproducerer schema/clock/formatter/negative fixtures. Grøn CI beviser code integrity, ikke forecasting edge.
- **Codex:** implementerer eneste prioriterede bounded code defect gennem current CODEX_READY og original owner, eller reviewer uafhængigt Claude/ChatGPT-skrevne LOW/MEDIUM PR'er.
- **Claude:** uafhængig reviewer for Codex-skrevet kode og relevant HIGH/HIGH_IMPACT; vurderer source/method med dokumenteret exact-head og begrundede findings. Den som byggede en PR kan ikke være independent reviewer.
- **Sol 6.2 MAX:** kun hvis en dokumenteret, uafklaret original research/metodebeslutning ikke kan løses offline, og eksisterende shared runbook, original owner, live provider GET, et særskilt signed per-mission owner mandate, one-use claim, budget og native receipts alle accepterer. Ikke til at omskrive dette dokument.
- **S1:** review-routing, tilstand, release og post-merge verifikation på samme PR. Ikke selvvalgt ny research eller paid model. Ved lange ventetider log én præcis event-baseret blocker og ejer, ikke uendelige statusrapporter.

## 10. Outputartefakter, der faktisk kan lukkes

| Milepæl | Mindste acceptable bevis | Beslutning |
|---|---|---|
| M0 intake | Original kilde, førstekendt dato, overlapkort, billig baseline, ejer og modargument | REJECT / DEDUP / proceed G0 |
| M1 source census | Alle W45-W47 issued rows, initial/revised, first-known, samme quote/venue, unknowns og consumer | DATA_BLOCKED eller eligible descriptive audit |
| M2 root cause | For hver berørt family forekomst, SOURCE/BUSINESS/TAIL/CONSUMER årsag med hash og minimal patch-locus | Én bounded defect eller afvis nyt |
| M3 challenger prereg | Én primary endpoint, simple baselines, future cohort, source vintage, negative controls, false-alarm budget og kill | Prospective only når owner ratificerer |
| M4 code PR | Kun original-owner files; positive/negative/mutation tests; current source/main; CI exact head | Independent review, aldrig self merge |
| M5 release | Squash main SHA, approved changed blobs readback, real rendered site/konsumentstempel, no leakage | MERGED_VERIFIED eller hold |
| M6 effect | Modnet prospective sammenligning med originalt champion og coverage + risk/miss cost | DOCUMENTED_IMPROVEMENT / UNPROVEN / REGRESSED / KILLED |
| M7 closure | Endelig #1157-disposition, #1512 intake/outcome, #1156 verified closure/handoff | VERIFIED_CLOSED / FALSIFIED / DUPLICATE_CLOSED / BLOCKED_WITH_EXPLICIT_TRIGGER |

M0-M2 er højeste aktuelle værdi. M3 kan ikke "opfyldes" ved at bruge W47 som holdout, da udfaldet allerede er kendt. M4-M6 må ikke betragtes som udført, før separate git/run/consumer receipts eksisterer. Ved source-data-blokade defineres eksakt reaktiveringstrigger og afsluttes foreløbigt som BLOCKED_WITH_EXPLICIT_TRIGGER.

## 11. Uafhængig reviewer, værst tænkelige fejl først

**Bed reviewer bekræfte eller afvise følgende før enhver merge:**
1. Er P0 reelt nyt og ikke allerede løst i P1/site eller #2282/#2281/#2284?
2. Matcher alle konkrete kilder det faktiske main SHA og rapporterede blob SHA; er gamle W46 første-udgave, W47 partial og D1 korrekt behandlet?
3. Er der en falsk konklusion om, at en 55k wick allerede er en officiel scored closing miss?
4. Kan original consumer first-known dokumenteres, eller er det kun GitHub-kildeskrivning?
5. Er de private data, Round 3 og forkert clock reelt beskyttet?
6. Kan alle forslåede G2-G4 challengers dræbes af simpler price-only, ATR og persistence, og er source-availability gate før test?
7. Er der for mange aktive handoffs eller løfter om selvkørende monitorering?
8. Er en source-fixed cost model blevet et usandt 50k prisgulv?
9. Skaber refleksivitet falske, korrelerede evidensstemmer?
10. Er der en konkret brugerfunktion/consumer efter eventuel kodemerge, ikke kun research og green CI?
11. Bør denne dokument-PR holdes/closed som redundant i forhold til den aktuelle Claude MASTER_PLAN_v1 eller uafsluttede RISK-02? Hvis ja, REJECT/DEDUP er ønsket resultat.
12. Skal en specifik reproducérbar issue klassificeres HIGH ved site/offentlig ændring, i overensstemmelse med S1's aktuelle release-manifest, ikke forfatterens MEDIUM-ønske?

**Requested review disposition:** APPROVE_RESEARCH_HANDOFF, REQUEST_CHANGES, DUPLICATE_CLOSE eller BLOCKED_WITH_TRIGGER. Et review af dokumentet er IKKE godkendelse til paid dispatch, kodeændring, preskriptiv markedsstrategi eller merge af en efterfølgende implementerings-PR.

## 12. Fortsat research uden at opfinde falsk autonomi

Ved hver reel, allerede autoriseret efterfølgende S1/Task2/CRE observation: brug den samme originale issue/PR og disse event-triggere. Hvis nye originale as-of forecaster og actuals er modne, kan reviewer følge M1-M3; hvis en kilde har ændret SHA, rebind og gentest netop den berørte del; hvis intet er ændret, svar NOOP. Aktiv opfølgning kræver en faktisk igangværende existing task, ikke at denne PR har skrevet ordene "fortsæt". Flere planlagte ChatGPT-tasks eller native workflows oprettes IKKE her.

**Konklusion:** Det vigtigste er at få Kompas til at opdage og indrømme accelererende downside hurtigere, uden hindsight eller falske claims. Grib eksisterende mulige wiring-/tail-fejl før der opfindes ny indikator. Miner economics, 13 måneders bars og Soros refleksivitet forbliver svage, falsificerbare kontekst/hypoteser. En færdig integration er kun færdig, hvis det korrekte, levende produkt bruger den præcise kilde, og en senere uafhængig vurdering kan se om den hjalp.

## 13. Oprindelse og datagrænser

Research-intake hidrører fra ejerens 2026-11-21 skærmbilleder af @ajaxcryptogod, @astronomer_zero 2W miner-cost/tekst og Soros-videoen, plus tidligere samtalebundne researchpakker RESEARCH_LAB_INPUT_2026-11-21_BTC13M_REFLEXIVITY.md og RESEARCH_LAB_ADVERSARIAL_PRIORITIES_2026-11-21.md. Disse lokale rapporter er ikke automatisk GitHub-public proof. Screenshots' originale X post ID, edits, raw TradingView formula og live market-vintages er ikke valideret her. De ni opfølgende inline billeder blev synlige som filer i den nuværende samtales container, så det tidligere notat om manglende adgang gælder ikke som aktuel teknisk begrænsning; der er dog ingen uafhængig X-original-verifikation.

Alle navngivne research- og kildeændringer i dette dokument er forslag eller read-only status på den ovenstående source-blob / aktuelt verificeret issue. Dette dokument er ikke en levering af færdig reproduceret W45-W47 source-to-outcome scoreboard, ikke en ny model og ikke en videnskabeligt valideret edge.