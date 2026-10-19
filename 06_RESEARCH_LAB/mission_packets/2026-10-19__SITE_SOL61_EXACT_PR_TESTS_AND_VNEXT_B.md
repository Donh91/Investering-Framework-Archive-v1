# FROZEN GITHUB PR REVIEW SOURCE: #1683
Exact SHA: ac0002837d304631f42fa44e3255a73b83004d52
Base at capture: eeb298aba14d3d0763aef674ca61113a6eb0bfa1
Draft: true
CI: Master Monday Preflight Gate=success | Daily Capture Architecture Gate=success | Data Architecture Gate=success | Full Architecture 1-7 Gate=success | Storage Health Gate=success | Shadow Admission AI Decider=success | Cycle Navigator Public Contract Gate=success | Cycle Navigator Public Product Gate=success | Compass Event Refresh=success | Automation Production Health Gate=success | Experiment Lifecycle Gate=success | Official Daily Compass=success
COMPLETE changed-file list: .github/workflows/weekly-api-calibration-shadow.yml; 05_CYCLE_NAVIGATOR/site/build-public.mjs; 05_CYCLE_NAVIGATOR/site/market-compass-premium.js; 05_CYCLE_NAVIGATOR/site/tests/full-stack-readback.test.mjs; research/master_monday_preflight/2026-10-19__COMPASS_FULL_STACK_PARITY_AND_NONREGRESSION_ADDENDUM.md; research/master_monday_preflight/2026-10-19__SITE_TRUTH_FIRST_INDEPENDENT_DESIGN_AUDIT.md; research/master_monday_preflight/2026-10-19__SIX_REPOSITORY_PROVENANCE_AND_SITE_TRUST_AUDIT.md; research/master_monday_preflight/2026-10-19__SOL_6_1_WEEKLY_INTELLIGENCE_SITE_COMPASS_EXECUTION_MISSION.md; research/master_monday_preflight/2026-10-19__weekly-intelligence-audit-and-contract-gap-review.md; scripts/master_monday/publish_master_monday_outputs.py; tests/master_monday/test_durable_repairs.py
Research input only. This is a GitHub patch excerpt, not full surrounding code. Omitted/unreadable code is UNKNOWN. Do not infer runtime execution.

### 05_CYCLE_NAVIGATOR/site/tests/full-stack-readback.test.mjs (patch_chars=6820, included=6820)
```diff
@@ -40,8 +40,42 @@ function fixture(){
  const installForecast=()=>{const f=signed(forecast,'forecast_sha256');files.set(resolve(root,forecastPath),f.raw);pointers.set('shadow',{contract:'SHADOW_COMPASS_V2_LATEST_POINTER_v1',forecast_path:forecastPath,forecast_sha256:f.hash,forecast_id:'f',source_fingerprint:'fp'});};installForecast();
  const context={resolve,relative,createHash,Date,repoRoot:root,COMPASS_POINTER_PATH:'public',INTERNAL_COMPASS_POINTER_PATH:'official',AUTO_MARKET_STATE_POINTER_PATH:'auto',NATIVE_COMPASS_POINTER_PATH:'native',SHADOW_COMPASS_V2_POINTER_PATH:'shadow',STRATEGIC_COMPASS_POINTER_PATH:'strategic',MASTER_MONDAY_HANDOFF_PATH:'handoff',readJson:async p=>pointers.get(p),readFile:async(p,encoding)=>{if(!files.has(p))throw Error('missing');return encoding?files.get(p):Buffer.from(files.get(p));}};
  vm.createContext(context);vm.runInContext(source.slice(source.indexOf('function verifiedRelative'),source.indexOf('\nasync function buildCompassEventSnapshot'))+';globalThis.run=buildFullStackReadback;globalThis.digest=verifiedRawDigest;',context);
- return {root,files,pointers,forecast,installForecast,autoPath,officialPath,projectionPath,weeklyPath,context,run:()=>context.run({compass_id:'c',issued_at_utc:now,data_status:'OK',action_now:'HOLD'},wp,{issue_number:29})};
+ return {root,files,pointers,forecast,installForecast,autoPath,officialPath,projectionPath,weeklyPath,weeklyPointer:wp,context,run:()=>context.run({compass_id:'c',issued_at_utc:now,data_status:'OK',action_now:'HOLD'},wp,{issue_number:29})};
 }
+// A verified weekly delivery pointer is insufficient: the referenced Master
+// Monday machine package must itself be readable and match its declared SHA.
+for (const mode of ['valid','missing','tampered','wrong-digest','wrong-week','not-ready','escaped-path','wrong-freeze','missing-freeze','complete','sensitive','conflicting-status']) {
+ const f=fixture();
+ const pointerPath='research/api_agent/outputs/weekly/2026/W40/MASTER_MONDAY_DELIVERY_POINTER.json';
+ const packagePath='research/api_agent/outputs/weekly/2026/W40/MASTER_MONDAY_MACHINE_PACKAGE.json';
+ const signedMachine=signed({contract:'MASTER_MONDAY_MACHINE_PACKAGE_v1',iso_year:2026,iso_week:40,freeze_sha256:'a'.repeat(64),api_status:'success',analysis:mode==='sensitive'?'PRIVATE_WALLET_KEY_SHOULD_NOT_BE_PUBLIC':'Shadow-only weekly context',scorecard:{status:mode==='complete'?'READY':'UNAVAILABLE_API_CONTRACT'},operational_translation:{status:mode==='complete'?'READY':'UNAVAILABLE_API_CONTRACT'}},'package_sha256');
+ const machine=signedMachine.raw;
+ const pointer={contract:'MASTER_MONDAY_DELIVERY_POINTER_v1',status:mode==='not-ready'?'PARTIAL':'READY',
+   iso_year:2026,iso_week:mode==='wrong-week'?39:40,
+   ...(mode==='missing-freeze'?{}:{freeze_sha256:mode==='wrong-freeze'?'b'.repeat(64):'a'.repeat(64)}),
+   machine_package_path:mode==='escaped-path'?'../../private/secret.json':packagePath,
+   machine_package_sha256:mode==='wrong-digest'?'f'.repeat(64):signedMachine.hash,
+   scorecard_status:['complete','conflicting-status'].includes(mode)?'READY':'UNAVAILABLE_API_CONTRACT',
+   operational_translation_status:mode==='complete'?'READY':'UNAVAILABLE_API_CONTRACT'};
+ const raw=JSON.stringify(pointer);
+ f.weeklyPointer.completed_source_year=2026;
+ f.weeklyPointer.completed_source_week=40;
+ f.weeklyPointer.master_monday_pointer_sha256=hash(raw);
+ f.files.set(resolve(f.root,pointerPath),raw);
+ f.files.set(resolve(f.root,packagePath),mode==='tampered'?machine.replace('"iso_week":40','"iso_week":39'):machine);
+ if(mode==='missing')f.files.delete(resolve(f.root,packagePath));
+ f.pointers.set('handoff',{pointers:{latest_weekly_output:{path:pointerPath,sha256:hash(raw)}}});
+ const result=await f.run();
+ const got=result.source_status.master_monday;
+ assert.equal(got,['valid','complete','sensitive','conflicting-status'].includes(mode)?'SOURCE_ALIGNED':'UNVERIFIED','Master Monday target readback: '+mode);
+ assert.equal(result.source_status.master_monday_analysis,mode==='complete'?'COMPLETE':mode==='conflicting-status'?'CONFLICTING_ANALYTICS':got==='SOURCE_ALIGNED'?'PARTIAL_ANALYTICS':'UNVERIFIED');
+ assert.equal(result.master_monday?.authority,'WEEKLY_CONTEXT_ONLY_NO_CURRENT_ACTION');
+ assert.equal(result.master_monday?.machine_package_sha256,undefined);
+ assert.equal(result.master_monday?.freeze_sha256,undefined);
+ assert.equal(result.master_monday?.machine_package_path,undefined);
+ assert.doesNotMatch(JSON.stringify(result.master_monday),/PRIVATE_WALLET_KEY_SHOULD_NOT_BE_PUBLIC/);
+}
+
 let f=fixture();assert.equal((await f.run()).shadow.status,'ALIGNED_RESEARCH');
 f=fixture();f.pointers.get('official').source_packet_sha256='a'.repeat(64);let result=await f.run();assert.equal(result.source_status.official,'DEGRADED');assert.notEqual(result.shadow.status,'ALIGNED_RESEARCH');
 f=fixture();f.pointers.get('auto').packet_generated_at_utc='2099-01-01T00:00:00Z';result=await f.run();assert.equal(result.source_status.auto_market_state,'UNVERIFIED');assert.notEqual(result.shadow.status,'ALIGNED_RESEARCH');
@@ -129,4 +163,22 @@ const oldEvent=render('OK','PUBLIC_COMPASS_PROJECTION_v1',{
   ...scheduled,detected_at_utc:'2026-10-11T06:30:00Z'});
 assert.doesNotMatch(oldEvent,/SCHEDULED UPDATE DELAYED/);
 assert.doesNotMatch(render('OK'),/SCHEDULED UPDATE DELAYED/);
+// SITE must show Monday provenance/completeness without substituting it for
+// the current official action or leaking raw API narrative.
+{
+ const context={esc:String,publicState:String,publicCompassText:String,recommendation:()=>({action:'HOLD'})};
+ vm.createContext(context);
+ vm.runInContext(premium.slice(premium.indexOf('function compositeIntel('),premium.indexOf('function refreshStatusBanner('))+';globalThis.render=compositeIntel;',context);
+ const weekly={contract:'PUBLIC_COMPASS_FULL_STACK_READBACK_v1',status:'PARTIAL_OR_DEGRADED',source_status:{official:'VERIFIED'},
+   master_monday:{status:'SOURCE_ALIGNED',completed_week:'2026-W42',analytics_status:'PARTIAL_ANALYTICS'}};
+ const html=context.render({data_status:'OK',action_now:'HOLD',full_stack:weekly},'CURRENT');
+ assert.match(html,/MONDAY BASELINE/);
+ assert.match(html,/2026-W42/);
+ assert.match(html,/ANALYSIS PARTIAL/);
+ const conflict=context.render({data_status:'OK',action_now:'HOLD',full_stack:{...weekly,master_monday:{status:'SOURCE_ALIGNED',completed_week:'2026-W42',analytics_status:'CONFLICTING_ANALYTICS'}}},'CURRENT');
+ assert.match(conflict,/ANALYTICAL SOURCE CONFLICT/);
+ assert.match(html,/OFFICIAL ACTION/);
+ const missing=context.render({data_status:'OK',action_now:'HOLD',full_stack:{...weekly,master_monday:{status:'UNVERIFIED'}}},'CURRENT');
+ assert.match(missing,/MONDAY BASELINE · SOURCE UNVERIFIED/);
+}
 console.log('FULL_STACK_READBACK_REGRESSION_PASS');
```

### tests/master_monday/test_durable_repairs.py (patch_chars=4722, included=4722)
```diff
@@ -131,4 +131,75 @@ def test_master_monday_missing_and_malformed_cfgi_fail_closed(self):
                 self.assertEqual(value['cfgi'],{})
 
 
+
+class WeeklyIntelligenceAuditTests(unittest.TestCase):
+    def _fixture(self):
+        machine={
+            'iso_year':2026,'iso_week':42,'package_sha256':'a'*64,
+            'freeze_sha256':'b'*64,'preflight_sha256':'c'*64,
+            'context_hash':'d'*64,'api_status':'failure',
+            'api_receipt':{'model':'gpt-6.1-sol','estimated_cost_usd':0.25,
+                           'api_key':'PRIVATE_API_SECRET_SHOULD_NOT_APPEAR'},
+            'analysis':{'wallet_address':'PRIVATE_WALLET_SHOULD_NOT_APPEAR'},
+            'learning_decision_impact':{'assessment_status':'NOT_EVALUABLE_NOVEL_INPUT_NOT_CONSUMED'},
+        }
+        pointer={
+            'iso_year':2026,'iso_week':42,'machine_package_sha256':'a'*64,
+            'status':'READY_WITH_API_FAILURE','producer_status':'READY_WITH_API_FAILURE',
+            'preflight_status':'FULL_MASTER_MONDAY_INPUT',
+            'consumer_receipt_status':'PASS','consumer_receipt_state':'VERIFIED',
+            'scorecard_status':'UNAVAILABLE_API_CONTRACT',
+            'operational_translation_status':'UNAVAILABLE_API_CONTRACT',
+            'experiment_learning_status':'AVAILABLE',
+        }
+        return machine,pointer
+
+    def test_weekly_audit_is_deterministic_private_safe_and_failure_honest(self):
+        from scripts.master_monday.publish_master_monday_outputs import build_weekly_intelligence_audit
+        machine,pointer=self._fixture()
+        freeze={'final_week_close':{'package_sha256':'9'*64,'raw_private':'SECRET_SOURCE_VALUE'},
+                'weekly_capture_bridge':{'sha256':'8'*64}}
+        preflight={'meta':{'blocking_gap_count':0,'confidence_reducing_gap_count':24,
+                           'planned_core_actions':60},
+                   'quality':{'PASS':36,'PARTIAL':8,'UNAVAILABLE':16},
+                   'private_raw':'SECRET_PREFLIGHT_VALUE'}
+        machine['scorecard']={'matured_outcome_count':140,'private':'SECRET_SCORECARD_VALUE'}
+        out=build_weekly_intelligence_audit(machine,pointer,'e'*64,'f'*64,freeze,preflight)
+        self.assertEqual(out,build_weekly_intelligence_audit(machine,pointer,'e'*64,'f'*64,freeze,preflight))
+        self.assertIn('\n\n```json\n',out)
+        payload=json.loads(out.split('```json\n')[1].split('\n```')[0])
+        self.assertEqual(payload['completed_week'],'2026-W42')
+        self.assertEqual(payload['delivery']['api'],'FAILURE')
+        self.assertEqual(payload['analysis_completeness']['scorecard'],'UNAVAILABLE_API_CONTRACT')
+        self.assertEqual(payload['downstream_not_yet_claimed']['site'],'PENDING_DOWNSTREAM_OWNER')
+        self.assertEqual(payload['source_provenance']['machine_self_sha256'],'a'*64)
+        self.assertEqual(payload['source_provenance']['machine_file_sha256'],'e'*64)
+        self.assertEqual(payload['evidence_quality']['confidence_reducing_gap_count'],24)
+        self.assertEqual(payload['evidence_quality']['core_pass'],36)
+        self.assertEqual(payload['outcome_and_learning']['registry_matured_count_not_scored_or_admitted'],140)
+        self.assertEqual(payload['source_provenance']['settled_week_close_sha256'],'9'*64)
+        self.assertFalse(payload['restricted_payloads_included'])
+        for private in ('PRIVATE_API_SECRET_SHOULD_NOT_APPEAR','PRIVATE_WALLET_SHOULD_NOT_APPEAR','SECRET_SOURCE_VALUE','SECRET_PREFLIGHT_VALUE','SECRET_SCORECARD_VALUE'):
+            self.assertNotIn(private,out)
+
+    def test_weekly_audit_rejects_cross_week_and_unbound_machine(self):
+        from scripts.master_monday.publish_master_monday_outputs import build_weekly_intelligence_audit
+        machine,pointer=self._fixture()
+        pointer['iso_week']=41
+        with self.assertRaisesRegex(ValueError,'week_mismatch'):
+            build_weekly_intelligence_audit(machine,pointer,'e'*64,'f'*64)
+        pointer['iso_week']=42
+        pointer['machine_package_sha256']='0'*64
+        with self.assertRaisesRegex(ValueError,'digest_mismatch'):
+            build_weekly_intelligence_audit(machine,pointer,'e'*64,'f'*64)
+        pointer['machine_package_sha256']='a'*64
+        with self.assertRaisesRegex(ValueError,'file_hash_invalid'):
+            build_weekly_intelligence_audit(machine,pointer,'not-a-hash','f'*64)
+        machine['iso_year']=2025
+        machine['iso_week']=53
+        pointer['iso_year']=2025
+        pointer['iso_week']=53
+        with self.assertRaisesRegex(ValueError,'invalid_iso_week'):
+            build_weekly_intelligence_audit(machine,pointer,'e'*64,'f'*64)
+
 if __name__=='__main__': unittest.main()
```

# FROZEN GITHUB PR REVIEW SOURCE: #1680
Exact SHA: 5301a94482de5bcde45c729096e2757243fe7efb
Base at capture: fe96b875fc1cd5b09297d2c38028ced40f0cf68e
Draft: false
CI: Official Daily Compass=success | Cycle Navigator Public Product Gate=success | Compass Event Refresh=success | Cycle Navigator Public Contract Gate=success | Data Architecture Gate=success | Storage Health Gate=success
COMPLETE changed-file list: 05_CYCLE_NAVIGATOR/site/build-public.mjs; 05_CYCLE_NAVIGATOR/site/validate-v2.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/README.md; 05_CYCLE_NAVIGATOR/site/vnext-live/app.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/chart-source-key.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/index.html; 05_CYCLE_NAVIGATOR/site/vnext-live/official-bullbear.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/official-feed-parity.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/official-path.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/official-pullback-eta.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/official-pullback-investor-view.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/official-pullback-stage.mjs; 05_CYCLE_NAVIGATOR/site/vnext-live/premium.css; 05_CYCLE_NAVIGATOR/site/vnext-live/validate.mjs
Research input only. This is a GitHub patch excerpt, not full surrounding code. Omitted/unreadable code is UNKNOWN. Do not infer runtime execution.

### 05_CYCLE_NAVIGATOR/site/vnext-live/app.mjs (patch_chars=15379, included=4200)
```diff
@@ -0,0 +1,137 @@
+
+/* Premium candidate only. Same-origin read-only official public data.
+ * Never synthesize a market action, forecast, score or hidden source. */
+import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
+import {chartSourceFingerprint} from './chart-source-key.mjs';
+const $=id=>document.getElementById(id),keys=['overview','compass','results'];
+const H=[['NEXT_12H','0–12h'],['NEXT_1_3D','1–3d'],['NEXT_5_7D','5–7d'],['NEXT_2_3W','2–3u'],['CYCLE_ALTCOINS_3_8W','3–8u']];
+const T=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
+const dict={
+da:{tabOverview:'Overblik',tabCompass:'Kompas',tabResults:'Resultater',overviewEyebrow:'MARKEDSBILLEDE / LIGE NU',heroOne:'Forstå',heroTwo:'retningen.',heroIntro:'Én tydelig læsning. Én officiel handling. Ægte markedsdata.',weeklyState:'UGENS MARKEDSSTATUS',actionLabel:'OFFICIEL HANDLING · NU',proxyLabel:'RETNINGSPROXY · 0–12 TIMER',proxyCaveat:'Observeret bevægelse, ikke selvstændigt valideret prognose.',riskLabel:'PULLBACK-RISIKO',distributionLabel:'DISTRIBUTION',nextGateLabel:'NÆSTE BEKRÆFTELSE',cycleHeading:'Hvor i cyklussen?',noEta:'Ingen udokumenteret ETA',forecastHeading:'Prognose møder virkelighed.',frozenRange:'Oprindeligt fastlåst interval',chartTitle:'Frossen prognose / faktiske priser',chartTrust:'Grafen viser kun frosne kildepunkter og gyldige observationer. Manglende dagsprognoser tegnes ikke.',compassHeading:'Tydeligere beslutninger.',compassSub:'Markedsretning, handling og tid adskilles. Ingen nye handelssignaler skabes her.',horizonsHeading:'Tidshorisonter',ownerOfficial:'Kun officielt Kompas',time:'Tid',direction:'Retning',actionShort:'Handling',tiersHeading:'Kapitalrotation',asset:'Aktiv',state:'Status',protectionHeading:'Beskyttelse og re-entry',pullback:'PULLBACK',resultsHeading:'Beviser frem for hype.',resultsSub:'Den senest afsluttede uge, dens reelle dækning og seks frosne intervaller. Ikke en opdigtet samlet præcision.',completedPrecision:'SENEST AFSLUTTEDE PRISPRÆCISION',coverage:'KILDEDÆKNING',hours:'Kvalificerede observationstimer',weeklyScoreTable:'Frossent interval vs. faktisk',sixWindows:'BTC / ETH · 3 vinduer',assetWindow:'Aktiv / vindue',frozenForecast:'Frossen prognose',observed:'Observeret',precision:'Præcision',methodHeading:'Hvad er egentlig verificeret?',methodText:'Prisintervaller måles med 70/30-metoden. Strukturanalyse scores ikke i procent efter CN #26. Uafhængig forsegling må ikke påstås uden bevis.',openScoreRepo:'Åbn offentligt kildearkiv ↗',previewOnly:'Ikke standardforsiden',legacySite:'Åbn eksisterende site ↗'},
+en:{tabOverview:'Overview',tabCompass:'Compass',tabResults:'Results',overviewEyebrow:'MARKET OVERVIEW / RIGHT NOW',heroOne:'Read',heroTwo:'the shift.',heroIntro:'One clear reading. One official action. Real market evidence.',weeklyState:'THIS WEEK’S MARKET STATUS',actionLabel:'OFFICIAL ACTION · NOW',proxyLabel:'DIRECTION PROXY · 0–12 HOURS',proxyCaveat:'Observed continuation, not an independently validated forecast.',riskLabel:'PULLBACK RISK',distributionLabel:'DISTRIBUTION',nextGateLabel:'NEXT CONFIRMATION',cycleHeading:'Where are we in the cycle?',noEta:'No unsupported ETA',forecastHeading:'Forecast meets reality.',frozenRange:'Originally frozen weekly range',chartTitle:'Frozen forecast / actual prices',chartTrust:'Only original frozen points and eligible observations are shown. Missing daily forecasts are not drawn.',compassHeading:'Clearer decisions.',compassSub:'Direction, action and timing remain separate. No new trading signals are created here.',horizonsHeading:'Time horizons',ownerOfficial:'Official Compass only',time:'Horizon',direction:'Direction',actionShort:'Action',tiersHeading:'Capital rotation',asset:'Asset',state:'Status',protectionHeading:'Protection and re-entry',pullback:'PULLBACK',resultsHeading:'Receipts, not hype.',resultsSub:'Last completed week, real evidence coverage and six original frozen windows. No invented overall accuracy.',completedPrecision:'LATEST COMPLETED PRICE PRECISION',coverage:'SOURCE COVERAGE',hours:'Eligible observation hours',weeklyScoreTable:'Frozen range vs actual',sixWindows:'BTC / ETH · 3 windows',assetWindow:'Asset / window'
[TRUNCATED 11179 chars - no claim of full coverage]
```

### 05_CYCLE_NAVIGATOR/site/vnext-live/chart-source-key.mjs (patch_chars=1366, included=1366)
```diff
@@ -0,0 +1,23 @@
+/* Staged premium chart source identity. Pure, no clock, no market logic.
+ * The original chart uses BOTH the live precision artifact and the public
+ * publication projection, so a data-refresh key must include BOTH. */
+export function chartSourceFingerprint(latest, nowMs=Date.now()) {
+  const v=latest?.public_live_precision||null;
+  const projection=latest?.public_series?.current_public_projection||null;
+  const pointer=latest?.pointer||null;
+  // Match the embedded original CNWeekChart model's SOURCE freshness policy.
+  // Re-mount once when observed evidence goes STALE; avoid 1-minute refresh
+  // remounts and user zoom/selected-asset loss while evidence remains fresh.
+  const cutoff=Date.parse(v?.daily_observations?.observed_through_utc||v?.live_as_of_utc);
+  const age=nowMs-cutoff;
+  const sla=Math.max(30,Number(v?.freshness_sla_minutes)||90)*60000;
+  const stale=!Number.isFinite(cutoff)||age<0||age>sla;
+  return JSON.stringify([
+    projection?.public_issue_number??null,projection?.forecast_week??null,
+    pointer?.issue_number??null,pointer?.iso_year??null,pointer?.iso_week??null,
+    pointer?.status??null,stale,
+    v?.public_issue_number??null,v?.forecast_week??null,
+    v?.window_scores??null,v?.rows??null,v?.daily_price_path??null,
+    v?.daily_observations??null,v?.live_as_of_utc??null
+  ]);
+}
```

### 05_CYCLE_NAVIGATOR/site/vnext-live/official-feed-parity.mjs (patch_chars=15419, included=4200)
```diff
@@ -0,0 +1,307 @@
+/**
+ * Read-only Cycle Navigator vNext adapter for the EXISTING production site feeds.
+ *
+ * Inputs MUST be the official site/build-public.mjs outputs:
+ *   dist/data/latest.json  (CN_PUBLIC_SNAPSHOT_V2)
+ *   dist/data/compass.json (PUBLIC_COMPASS_PROJECTION_v1)
+ *
+ * This module does not fetch secrets, publish a forecast, score prices,
+ * change official actions, or generate any production HTML.
+ * Keep it on the isolated design branch until source parity is accepted.
+ */
+
+import { officialPullbackDisplay } from './official-pullback-eta.mjs';
+import { officialPullbackStage } from './official-pullback-stage.mjs';
+import { officialPullbackInvestorView } from './official-pullback-investor-view.mjs';
+import { officialBullBear } from './official-bullbear.mjs';
+import { officialPathView } from './official-path.mjs';
+
+const RANGE_FORMULA = '70pct_containment_plus_30pct_jaccard';
+const SCORE_CONTRACT = 'CN_PUBLIC_WEEKLY_SCORECARD_v1';
+const PUBLIC_SERIES_CONTRACT = 'CN_PUBLIC_SERIES_INDEX_v1';
+const VALID_WEEKLY_HEALTH = new Set(['OK', 'PASS', 'DEGRADED']);
+const HOUR_MS = 3600000;
+
+function finite(value) {
+  return typeof value === 'number' && Number.isFinite(value);
+}
+
+function validUtc(value) {
+  if (typeof value !== 'string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d(?::\d\d(?:\.\d+)?)?(?:Z|[+-]\d\d:\d\d)$/.test(value)) return null;
+  const unix = Date.parse(value);
+  return Number.isFinite(unix) ? unix : null;
+}
+
+function normalizeAge(value, nowEpochMs, maxHours) {
+  const issued = validUtc(value);
+  if (issued === null) return 'NO_TIMESTAMP';
+  const diff = nowEpochMs - issued;
+  if (diff < -5 * 60000) return 'FUTURE_TIMESTAMP';
+  if (diff > maxHours * HOUR_MS) return 'STALE';
+  return 'FRESH';
+}
+
+function sourceRange(low, high) {
+  return finite(low) && finite(high) && low > 0 && high > low ? { low, high } : null;
+}
+
+function scoreRowEligible(row) {
+  return row && ['forecast_low', 'forecast_high', 'actual_low', 'actual_high', 'score'].every((field) => finite(row[field])) &&
+    row.forecast_low > 0 && row.forecast_low < row.forecast_high &&
+    row.actual_low > 0 && row.actual_low <= row.actual_high &&
+    row.score >= 0 && row.score <= 100 &&
+    ['BTC', 'ETH'].includes(row.asset) &&
+    ['day_1_2', 'day_3_4', 'day_5_7'].includes(row.window);
+}
+
+/**
+ * @param {object} latest official generated latest.json
+ * @param {object} compass official generated compass.json
+ * @param {object} options for deterministic tests: {nowUtc, compassMaxAgeHours, deliveryMaxAgeHours}
+ * @returns {object} source-bounded public presentation state only
+ */
+export function inspectOfficialPublicFeeds(latest, compass, options = {}) {
+  const {
+    nowUtc = new Date().toISOString(),
+    compassMaxAgeHours = 24,
+    deliveryMaxAgeHours = 24
+  } = options;
+  const nowEpochMs = validUtc(nowUtc);
+  if (nowEpochMs === null || !finite(compassMaxAgeHours) || compassMaxAgeHours <= 0 ||
+      !finite(deliveryMaxAgeHours) || deliveryMaxAgeHours <= 0) {
+    throw new Error('INVALID_READBACK_CLOCK_POLICY');
+  }
+  const result = {
+    contract: 'CN_VNEXT_PUBLIC_FEED_PARITY_v1',
+    source_authority: 'READ_ONLY_PRESENTATION',
+    generated_at: latest?.generated_at ?? null,
+    delivery_health: 'UNAVAILABLE',
+    weekly: {
+      state: 'UNAVAILABLE', public_issue_number: null, machine_issue_number: null,
+      forecast_week: null, btc_range: null, eth_range: null, path_state: 'UNAVAILABLE'
+    },
+    compass: {
+      state: 'UNAVAILABLE', compass_id: null, issued_at_utc: null,
+      weekly_alignment: 'UNVERIFIED', action_now: 'UNAVAILABLE',
+      pullback_risk_state: 'UNAVAILABLE', distribution_risk: 'UNKNOWN',
+      sell_assessment_state: 'UNAVAILABLE', reentry_state: 'UNAVAILABLE',
+      pullback_window: null, pullback_stage: null, pullback_investor_facts: null, bull_bear_1_3d: null,
+      permit_path_live_gates: false
+    },
+    completed_score: {
+      state: 'UNAVAILABLE', public_issue_number: null, forecast_week: null,
+      price_range_precision: null, btc_score: null, eth_score: null,
+      intraday_window_scores: null, rows: [],
+      market_structure_pr
[TRUNCATED 11219 chars - no claim of full coverage]
```

### 05_CYCLE_NAVIGATOR/site/vnext-live/official-path.mjs (patch_chars=11403, included=4200)
```diff
@@ -0,0 +1,194 @@
+/**
+ * Cycle Navigator vNext PATH · SOURCE-ONLY presentation.
+ * Source owners: weekly CN phase/structure, official Compass capital ladder,
+ * protection and SELL, not browser-authored phase forecast or ETA.
+ * An archived snapshot must never be represented as a current live phase.
+ */
+export const PATH_CONTRACT = 'CN_PATH_SOURCE_PRESENTATION_v1';
+
+const PHASES = Object.freeze([
+  ['BTC','BTC leadership','BTC-lederskab'],
+  ['ETH','Ethereum leadership','ETH-lederskab'],
+  ['LARGE_MID','Large + mid rotation','Large + mid-rotation'],
+  ['ALT_IGNITION','Altseason ignition','Altseason begynder'],
+  ['MICRO','Micro acceleration','Micro-acceleration'],
+  ['BROAD','Broad altseason','Bred altseason'],
+  ['MANIA','Mania / euphoria','Mani / eufori'],
+  ['DISTRIBUTION','Distribution','Distribution'],
+  ['PROTECTION','Exit / protection','Exit / beskyttelse'],
+  ['REENTRY','Cooldown / re-entry','Afkøling / re-entry']
+]);
+const LABEL = Object.freeze({
+  da:{
+    noSource:'Kilde utilgængelig',archived:'Arkiv · ikke live',observed:'Dokumenteret reference',
+    noPoint:'Aktuel fase ikke verificeret',next:'Næste betingelse',noGate:'Næste gate ikke dokumenteret',
+    etaUnknown:'Ingen verificeret ETA',condition:'Betinget kildevindue, ikke nedtælling',
+    window:'Kildevindue',watch:'Watch · ikke bekræftet',paused:'Afventer bekræftelse',
+    noAlt:'Ingen bekræftet bred altseason',btc:'BTC ledte den senest afsluttede uge',
+    eth:'ETH/BTC skal stabiliseres og fastholdes',transmission:'Large/mid deltagelse skal dokumenteres',
+    small:'Små selskaber skal deltage vedvarende',long:'90- og 365-dages bredde skal bekræfte',
+    wait:'Ingen faseopgradering uden verificerede signaler',
+    rotation:'Denne uges rotation',noTransfer:'Kapitaloverførsel til altcoins ikke bekræftet',
+    source:'Frosset uge',step:'Strukturel reference',later:'Ikke verificeret',
+    unavailable:'UTILGÆNGELIG',notConfirmed:'IKKE BEKRÆFTET',
+    hold:'HOLD',waitAction:'AFVENT',hardWait:'HARD WAIT',unavailableAction:'UTILGÆNGELIG',
+    altTitle:'Altseason-watch',sourceCaveat:'Tidsrum er observationsvinduer, ikke sikre fase-startdatoer.'
+  },
+  en:{
+    noSource:'Source unavailable',archived:'Archived · not live',observed:'Documented reference',
+    noPoint:'Current phase not verified',next:'Next confirmation',noGate:'Next gate not documented',
+    etaUnknown:'No verified ETA',condition:'Conditional source window, not a countdown',
+    window:'Source window',watch:'Watch · unconfirmed',paused:'Awaiting confirmation',
+    noAlt:'No confirmed broad altseason',btc:'BTC led the last completed week',
+    eth:'ETH/BTC must stabilize and persist',transmission:'Large/mid participation needs confirmation',
+    small:'Sustained small-cap participation required',long:'90- and 365-day breadth need to confirm',
+    wait:'Do not promote phases without verified signals',
+    rotation:'This week\'s rotation',noTransfer:'Capital transmission to alts unconfirmed',
+    source:'Frozen week',step:'Structural reference',later:'Not verified',
+    unavailable:'UNAVAILABLE',notConfirmed:'UNCONFIRMED',
+    hold:'HOLD',waitAction:'WAIT',hardWait:'HARD WAIT',unavailableAction:'UNAVAILABLE',
+    altTitle:'Altseason watch',sourceCaveat:'Time windows are observation watches, not guaranteed phase-start dates.'
+  }
+});
+const ALLOWED_ACTIONS=new Set(['HOLD','WAIT','HARD_WAIT','UNAVAILABLE']);
+const TIER=[
+  ['BTC','BTC'],
+  ['ETH','ETH'],
+  ['LARGE_CAPS','LARGE'],
+  ['MID_CAPS','MID'],
+  ['SMALL_CAPS','SMALL'],
+  ['MICROCAPS','MICRO'],
+  ['MEMES','MEMES']
+];
+const validWeek=(x)=>typeof x==='string'&&/^20\d{2}-W(?:0[1-9]|[1-4][0-9]|5[0-3])$/.test(x);
+const ss=(x)=>typeof x==='string'&&x.trim()?x.trim():null;
+
+// Conservative, source-only FROZEN BTC reference. Natural language is NOT a
+// market-classification engine: explicit negation/uncertainty vetoes the
+// reference, and anything ambiguous stays neutral on the cycle rail.
+export function verifiedBtcFrozenReference(marketState,btcStatus){
+ if(!ss(marketState)||!ss(btcStatus))return false;
+ if(!/\bBTC[\s-]+led\b/i.test(marketState)||
+    !/\b(?:led|leader|leadership)\b/
[TRUNCATED 7203 chars - no claim of full coverage]
```

### 05_CYCLE_NAVIGATOR/site/vnext-live/validate.mjs (patch_chars=11274, included=4200)
```diff
@@ -0,0 +1,178 @@
+// Premium vNext candidate production-source contract tests.
+// Runs in current SITE gate; synthetic source fixtures NEVER reach public dist.
+import assert from 'node:assert/strict';
+import {readFileSync} from 'node:fs';
+import {resolve,dirname} from 'node:path';
+import {fileURLToPath} from 'node:url';
+import {execFileSync} from 'node:child_process';
+import {inspectOfficialPublicFeeds} from './official-feed-parity.mjs';
+import {chartSourceFingerprint} from './chart-source-key.mjs';
+import {verifiedBtcFrozenReference} from './official-path.mjs';
+const dir=dirname(fileURLToPath(import.meta.url));
+const read=name=>readFileSync(resolve(dir,name),'utf8');
+const site=readFileSync(resolve(dir,'../build-public.mjs'),'utf8');
+const html=read('index.html'),client=read('app.mjs'),css=read('premium.css');
+const now='2026-10-19T09:00:00Z';
+const windows=['day_1_2','day_3_4','day_5_7'];
+const rows=windows.flatMap((window,i)=>['BTC','ETH'].map((asset)=>({
+  window,asset,forecast_low:asset==='BTC'?77000:2150,
+  forecast_high:asset==='BTC'?86500:2600,
+  actual_low:asset==='BTC'?79500:2260,
+  actual_high:asset==='BTC'?84300:2480,
+  score:asset==='BTC'?86-i:84-i
+})));
+const latest={
+ schema:'CN_PUBLIC_SNAPSHOT_V2',generated_at:'2026-10-19T08:55:00Z',
+ pointer:{iso_year:2026,iso_week:43,issue_number:31,status:'DEGRADED'},
+ package:{issue_number:31,status:'DEGRADED',forecast_freeze:{
+  btc_range_low:77000,btc_range_high:86500,eth_range_low:2150,eth_range_high:2600}},
+ public_series:{contract:'CN_PUBLIC_SERIES_INDEX_v1',
+  current_public_projection:{public_issue_number:30,forecast_week:'2026-W43'},
+  latest_completed_score:{public_issue_number:29,forecast_week:'2026-W42',status:'FINAL_DUAL_TRACK',price_range_score:85.25}},
+ public_scorecard:{contract:'CN_PUBLIC_WEEKLY_SCORECARD_v1',status:'FINAL_DUAL_TRACK',
+  public_issue_number:29,forecast_week:'2026-W42',
+  combined_score:null,market_structure_precision:null,
+  price_range_precision:{formula:'70pct_containment_plus_30pct_jaccard',
+    score:85.25,btc_score:86,eth_score:84,actuals_hourly_coverage:168,rows,
+    intraday_window_scores:{day_1_2:84,day_3_4:85,day_5_7:86}}}
+};
+const compass={
+ contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',
+ compass_id:'CMP-SYNTHETIC-W43',issued_at_utc:'2026-10-19T08:50:00Z',
+ weekly_context:{status:'ALIGNED',forecast_week:'2026-W43',public_issue_number:30},
+ full_stack:{official_freshness:{
+  contract:'OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1',
+  status:'VERIFIED_OWNER_POLICY',semantics:'SOURCE_FRESHNESS_EXPIRY_NOT_FORECAST_ETA',
+  source_asof_utc:'2026-10-19T08:45:00Z',valid_until_utc:'2026-10-19T10:00:00Z'
+ }},
+ action_now:'HOLD_WAIT',horizons:{NEXT_12H:{expected_direction:'UP'}},
+ protection_tracker:{pullback_risk_state:'ELEVATED',
+  distribution_risk:'UNKNOWN',reentry_state:'INACTIVE'},
+ sell_assessment:{state:'UNAVAILABLE'}
+};
+const run=(l=latest,c=compass,clock=now)=>inspectOfficialPublicFeeds(l,c,{nowUtc:clock});
+
+// An explicit denial must NEVER become a blue CURRENT/LEADERSHIP badge.
+assert.equal(verifiedBtcFrozenReference(
+ 'BTC-led rotation was not confirmed','BTC leadership is unconfirmed'),false);
+assert.equal(verifiedBtcFrozenReference(
+ 'BTC led on the completed week','BTC leadership was not confirmed'),false);
+assert.equal(verifiedBtcFrozenReference(
+ 'BTC did not lead during the completed week','BTC was the leader'),false);
+assert.equal(verifiedBtcFrozenReference(
+ 'The market has no confirmed leader','BTC lead remains unknown'),false);
+assert.equal(verifiedBtcFrozenReference(
+ 'BTC led the completed week','BTC leadership was confirmed'),true);
+const good=run();
+assert.equal(good.weekly.forecast_week,'2026-W43');
+assert.equal(good.weekly.state,'DEGRADED');
+assert.deepEqual(good.weekly.btc_range,{low:77000,high:86500});
+assert.equal(good.compass.state,'FRESH');
+assert.equal(good.compass.action_now,'HOLD_WAIT');
+assert.equal(good.compass.permit_path_live_gates,true);
+assert.equal(good.completed_score.state,'FINAL_PUBLIC_SCORECARD');
+assert.equal(good.completed_score.forecast_week,'2026-W42');
+assert.equal(good.completed_score.price_range_prec
[TRUNCATED 7074 chars - no claim of full coverage]
```