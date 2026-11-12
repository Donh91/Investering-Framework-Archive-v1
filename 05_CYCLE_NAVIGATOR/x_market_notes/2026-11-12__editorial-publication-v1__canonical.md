# Market Notes - Udgivelsesrutine v1

**Dato:** 2026-11-12  
**Status:** CANONICAL  
**Område:** Redaktionel publikation, separat fra CN forecast  
**Primary folder:** \`05_CYCLE_NAVIGATOR/x_market_notes/\`  
**Depends on:** Existing final Master Monday + existing Cycle Navigator/current Compass evidence.

## Timing
- Torsdag 12. november 2026: opret arkiv, stilregler og researchbrief. Ingen gammel forecast-udgave konverteres.
- Mandag 16. november 2026: første ordinære \`CN-MN-001\`, baseret på den afsluttede W46 og de på det tidspunkt gyldige kildeudtræk. Aftalt udgivelsesdag er ikke et løfte om fast klokkeslæt.
- Senere: én kandidat pr. uge, kun når der findes en rigtig historie. Ikke automatisk X-posting; ingen ny planlagt opgave oprettes.

## Kildearbejdet
1. Find afsluttet kildeuge og korrekt \`as_of\` (UTC/Copenhagen angives uden sammenblanding). Brug eksisterende afsluttede kilder, ikke kladder.
2. Undersøg tre mulige historier. Skriv hvorfor den valgte er mere interessant end ren prisbeskrivelse.
3. Kontroller påstand mod det præcise eksisterende kildefilnavn, commit SHA, observationstid, quote/enhed og eventuelle datamangler.
4. Skeln mellem målt forhold, rimelig fortolkning og uprøvet hypotese. Ingen tidsbestemte fremtidspåstande hvis den oprindelige kilde ikke indeholder dem.
5. Kontrollér, at ingen restricted/private værdier eller personlige porteføljer lækkes til offentligt GitHub/X.
6. Skræddersy 100-220 engelske ord som normalramme; længere kun hvis historien kræver det. Ingen tvungen graf.
7. Udarbejd alternativ indledning, fjern generiske fraser, kontroller tal, datoer og eventuel stale-markedssituation.
8. Arkivér \`CN-MN-NNN_DRAFT.md\` med \`DRAFT_NOT_APPROVED\`, kilder, \`as_of\`, manuskript og redaktionel beslutning.
9. Ved ejergodkendelse: frys \`APPROVED_NOT_PUBLISHED\` med eksakt tekst og checksum. Opdatér kun \`EDITION_INDEX.json\`; original beholdes.
10. Først efter ejerens bekræftelse af faktisk X-publicering: \`PUBLISHED_CONFIRMED_BY_USER\` med eksakt version, X-URL hvis oplyst og dato hvis kendt. Aldrig opfind X-link eller udgivelsestid.

## Ejerskab
Ikke en ny model eller markedsautoritet: Existing CN forbliver kilde til forecast, eksisterende Main Framework fastlægger frameworkets tilstand, og site forbliver uændret. Redaktionel tekst kan ikke ændre prognosen, scorer, historiske udgaver, risikogrænser eller wallet-/trade-signaler.

## Kvalitetskrav før publicering
- Et tydeligt, efterprøvbart fund.
- Kildevej og commit noteret.
- Mindst én begrænsning eller seriøs modforklaring.
- Ingen falsk prognose-/handelsedge.
- Datoer, enheder og tidsreference afstemt.
- Ingen intern jargon, rutineoverskrifter eller kunstig dramatik.
- Materialet kan forstås uden adgang til sitet.

## Når historien ikke holder
Ingen ugentlig tvang. Status \`NO_STRONG_STORY\` og kort hvorfor. Hellere et godt opslag hver anden uge end generisk fyld.
