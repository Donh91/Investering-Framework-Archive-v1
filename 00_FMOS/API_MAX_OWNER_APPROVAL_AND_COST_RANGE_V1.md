# API MAX, enkel ejergodkendelse og sikkert usikkerhedsinterval · v1

**Ejer:** original Archive #1156 og Research Lab Sol #1476. **Status:** Source-only operator contract, ikke et ekstra workflow, en ny agent eller en betalingsgodkendelse i sig selv.

## 1. Hvad ejeren behøver skrive fremover

> Godkend én MAX-analyse af [original mission/PR], brug senest **verificerede** Sol-model, kun offentligt tilladte kilder, samlet normalbudget 40 USD og absolut loft 45 USD. Ingen genforsøg med tidligere usikre POSTs.

Denne sætning er til eksisterende S1. S1 skal knytte godkendelsen til originalt issue, entydigt `work_id`, konkret model og kilde-HEAD, og give den til en **allerede eksisterende** autentificeret ejer-dispatch. Den må ikke direkte fortolke en chatbesked som en GitHub Actions-betaling.

Et modelnavn er ikke et privilegium. Når eksempelvis `gpt-6.2-sol` findes hos udbyderen, skal **modellen, dens aktuelle input/output-priser, den aktive Sol-rolle og den oprindelige task-registry** først være verificeret og gennemgået via almindelig original PR og CI. Den eksisterende budgetberegning er versionsneutral, men afviser ukendte/pris-usikre model-ID'er. Astra er fortsat ikke tilladt som autonom API-model.

## 2. Én regneregel på tværs af alle eksisterende ruter

`bekræftet forbrug + konservativ gammel POST-eksponering + ubrugte, bindende reservationer + ny forespørgsels øvre pris <= 45 USD`

* Normalbudget: **40 USD** pr. UTC-måned, med særlig ejergodkendelse af de sidste 5 USD. Undlad at hæve rutine-lane-budgetter, sætte reserve til nul eller øge den individuelle grænse for at bruge tolerancen.
* Absolut, kontoomfattende tolerance: **45 USD**, ikke et ekstra tillæg pr. job. Den seneste brugerbesked autoriserer ikke andre end den eksisterende ejer-dispatch.
* En gammel tvetydig POST får `lower=0` og et konservativt, begrundet `upper`. Indtil den faktisk er afstemt, reserveres øvre værdi. Ingen tidsbaseret udløb. Gamle forsøg har **ingen** ret til en ny HTTP POST.
* For 41870364609 (første FMOS-pass) og 41949497953 (Research Lab MAX) reserveres foreløbigt **op til 3 USD hver** i den eksisterende policy-risikoledgers `API_PENDING_BILLING_RISK_V1.json`, med kildehenvisninger til de oprindelige GitHub-kørsler og engangs-claim. 3 USD er et **governed admission risk estimate**, ikke en bekræftet providerfaktura eller en selvstændig udbydergaranti. Hvis den antagelse falsificeres eller udbyderen viser højere muligt forbrug, stands nye betalte POSTs, øg risikoestimatet under review og stop ved 45.
* Den enkelte nye forespørgsels maksimale reservation er fortsat **3 USD**, og et strengere existing lane-cap, større eksisterende minimumsreserve eller bindende betalingsregel har forrang. `--hard-stop-usd 30` og `--reserve-usd 12` forbliver 30/12, indtil en separat sikkerhedsgodkendt eksisterende rute reelt ændres.
* De uafklarede risiko-poster er **ikke** ny betalt API-spend. Ukendt faktura eller manglende ledger er ikke nul og må aldrig give PASS.

### Lokal, gratis prisforhåndsvisning (sender ingen POST)

```bash
python scripts/api_agent/check_monthly_cost_guard.py \
  --receipt-root research/api_agent/outputs \
  --hard-stop-usd 40 --reserve-usd 4 \
  --task SENIOR_REPAIR_AUDIT --model gpt-6.1-sol --effort max \
  --owner-work-id S1-MAX-APPROVED-20261106 \
  --input-token-upper 300000 --output-token-upper 45000
```

Svaret viser `exposure_range_min_usd`, `exposure_range_max_usd`, `pending_liability_upper_usd`, `normal_remaining_usd` og `approval_quote`. En PASS-kvittering her betyder **kun budgetforhåndsvisning**, ikke en godkendt source/owner-claim, uafhængigt review, API-kald eller release.

### For de sidste 5 USD

Den eksisterende **ejergodkendte og reviewede** caller skal eksplicit bruge `--hard-stop-usd 45` og nøjagtigt samme `work_id`, tilstrækkelig reservation, pris- og kildebevis, opdateret engangs-claim og aktuelle model-/lane-kontroller. Et arbitrært CLI-argument, dokument eller Issue-comment giver ikke selv rettigheder til at betale.

## 3. Faste kontrolpunkter før én ny MAX POST

1. Ægte GitHub issue-comment fra eksisterende owner, original `work_id` og public source SHA. Den nye MAX-brief fra merged PR #1952 er input, ikke en kørsel.
2. Faktiske regler/independent review/recovery på alle berørte HIGH_IMPACT source-/workflow-/betalingsændringer. #1944 må ikke auto-merges pga. grønne tests.
3. Kontroller model-pris og faktisk task-registry, `store`/30-dages samtykke, 1 aktiv mission, 1 claim og 1 POST. MAX er advisory uden kode-, merge- og handelsautoritet.
4. Kør budgetkontrollen inklusive risikoledger og alle native claims. Samme event, work_id, API-request og native original-branch writer må ikke kunne reserveres to gange. 403 fra policy-read er UNKNOWN, ikke ingen regler.
5. Gem provider-response-handle før GET-only opsamling. Afbrudt forbindelse uden handle -> reserver konservativt, **ingen anden POST**. Gennemfør separat efterkontrol af udbyderfaktura, ledger, kvittering og main/consumer.
6. Brug ORIGINAL ejerkæde #1476 -> #1156. Ingen ny scheduler, controller, parallel wallet/trade, automatisk Astra eller adgang til private Vault.

## 4. Acceptance og teknisk gæld

Budget-koden og `API_INTELLIGENCE_POLICY_v2.json` kan testes uafhængigt. Den konkrete eksisterende Sol-dispatch og fem-missionspakke har fortsat gamle 30/12-parametre, gammel single-use lås og betalings-/recovery-gates. **Denne budgetreparation ændrer ikke automatisk disse callers eller gør dem releaseklare**. Efter review skal en særskilt original rute-gennemgang dokumentere det samme tal, hvor det er bindende, og en kilde-bound engangs-claim skal være bevist på aktuel main før betalt launch.

**Ingen blankocheck på fremtidige modeller:** De behøver ikke ny budgetlogik, men et verificeret model/pris/rolle-snapshot og en konkret owner-autentificeret original mission. Kontrollens negative test skal afvise `gpt-6.2-sol` indtil dette er gjort.
