import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildUnifiedRootHtml} from './unified-root.mjs';
import {buildPremiumRootHtml} from './premium-root.mjs';
import {VIEWS,currentCompass,sourceTranslation,readHorizon,lensContext,explainPosture,explainCurrentAction,sourceWatch} from './compass-reader.mjs';
import {publicOverview,directionVisual,readRotation,POSITION_GUIDE} from './compass-overview.mjs';

const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [original,pro]=await Promise.all([
 read('./graph-b/source-graph-b.html'),read('../vnext-live/index.html')
]);
const id=(html,s)=>(html.match(new RegExp('id="'+s+'"','g'))||[]).length;

test('isolated unified candidate contains ONE original B, ONE original Kompas PRO and ONE PATH',()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const name of [
  'variant-panel','chart','forecast','actual','proof-explorer','compass-pro',
  'premium-now-action','premium-now-direction','premium-risk-steps',
  'premium-sell','premium-distribution','pro-guidance','pro-forward-rows',
  'horizon-body','official-path-view','premium-path-rail','premium-rotation',
  'pro-source-status','pro-next-gate'
 ])assert.equal(id(html,name),1,'duplicate or missing '+name);
 for(const name of [
  'official-product-pilot','official-pilot-action','official-pilot-horizons',
  'official-pilot-rotation','official-pilot-path','official-path-chart'
 ])assert.equal(id(html,name),0,'promoted legacy '+name);
 assert.equal((html.match(/<nav class="premium-entry-navigation"/g)||[]).length,1);
 assert.ok(html.indexOf('class="premium-entry-navigation"')<html.indexOf('id="compass-pro"'));
 assert.ok(html.indexOf('id="compass-pro"')<html.indexOf('id="variant-panel"'));
 assert.ok(html.indexOf('id="variant-panel"')<html.indexOf('id="official-path-view"'));
 assert.ok(html.indexOf('id="official-path-view"')<html.indexOf('id="proof-explorer"'));
 assert.match(html,/href="#compass-pro" data-premium-nav="compass">Kompas PRO/);
 assert.match(html,/href="#official-path-view" data-premium-nav="path"/);
 assert.doesNotMatch(html,/\/vnext\/#compass/);
 assert.doesNotMatch(html,/src="\.\/compass\/compass-path-ui\.mjs"/);
 assert.match(html,/src="\.\/root-compass-pro\.mjs"/);
 assert.match(html,/name="robots" content="noindex,nofollow"/);
});

test('unified root must preserve the approved original B renderer and forecast refusal',()=>{
 const html=buildUnifiedRootHtml(original,pro);
 const originalB=original.slice(original.indexOf('<section id="variant-panel"'),
   original.indexOf('<section id="proof-explorer"'));
 assert.ok(html.includes(originalB.trim().replace(/<\/section>\s*$/,'').trim()),
  'original Graph B markup must be unchanged');
 assert.match(html,/id="range-band"/);
 assert.match(html,/id="forecast"/);
 assert.match(html,/id="actual"/);
 assert.match(html,/id="hour-slider"/);
 assert.match(html,/id="source-state"/);
 assert.doesNotMatch(html,/Math\.sin\s*\(/);
 assert.match(html,/Dagsprognoser vises kun, hvis de blev udstedt før udfaldet/);
});

test('existing PRO contract is reused, including risk, trader lenses and horizon table',()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const marker of ['data-investor-lens="holder"','data-investor-lens="active"',
  'data-investor-lens="micro"','id="premium-risk-steps"',
  'id="premium-sell-caveat"','id="pro-watch-window"','id="pro-next-review"',
  'id="pro-price-btc"','id="pro-price-eth"','id="pro-forward-rows"'])
  assert.ok(html.includes(marker),marker);
 assert.equal((html.match(/data-investor-lens="micro"/g)||[]).length,1);
 assert.match(html,/class="cn-pro-more"/);
 assert.match(html,/id="pro-horizon-table"/);
});

test('negative: removed official PRO source, false clone, or missing B cannot enter preview',()=>{
 assert.throws(()=>buildUnifiedRootHtml(original,'<html>none</html>'),/PRO_SOURCE_UNAVAILABLE/);
 assert.throws(()=>buildUnifiedRootHtml(original,pro.replace('id="pro-guidance"','id="missing"')),/PRO_CONTRACT_MISSING/);
 assert.throws(()=>buildUnifiedRootHtml(original.replace('id="variant-panel"','id="wrong"'),pro),/SOURCE_MISMATCH/);
 assert.throws(()=>buildUnifiedRootHtml(original,pro.replace('id="premium-now-action"','id="other"')),/PRO_CONTRACT_MISSING/);
});

test('existing /next index and original B build remain immutable and separate',async()=>{
 const before=buildPremiumRootHtml(original);
 buildUnifiedRootHtml(original,pro);
 assert.equal(buildPremiumRootHtml(original),before);
 const cfg=await read('./vite.config.mjs');
 assert.match(cfg,/buildPremiumRootHtml\(original\)/);
 assert.match(cfg,/buildUnifiedRootHtml\(original,pro\)/);
 assert.match(cfg,/unified:resolve\(root,'unified\.html'\)/);
 const runtime=await read('./root-compass-pro.mjs');
 assert.match(runtime,/inspectOfficialPublicFeeds/);
 assert.match(runtime,/renderProductExperience/);
 assert.match(runtime,/initProductExperience/);
 assert.match(runtime,/clock=setInterval\(paint,CLOCK_RECHECK_MS\)/);
 assert.match(runtime,/weeklyHealth/);
 assert.doesNotMatch(runtime,/\bMath\.sin\s*\(/);
});

test('PRO inventory is maintained without duplicate legacy presentation',()=>{
 const html=buildUnifiedRootHtml(original,pro);
 const section=pro.slice(pro.indexOf('<section id="view-compass"'),
   pro.indexOf('<section id="view-path"'));
 const expected=[...section.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]);
 const present=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));
 const allowedOmissions=new Set([
  // vNext tab/page containers are deliberately not repeated in the single page.
  'view-compass','compass-title',
  // The only seven-tier rotation is the PATH rail below Proof.
  'tier-body',
  // Legacy duplicate SELL/re-entry/risk readbacks are consolidated into
  // the one full PRO risk+SELL group and source-owned re-entry section.
  'sell-state','reentry-state','risk-2','sell-note'
 ]);
 const missing=expected.filter(x=>!present.has(x));
 assert.deepEqual(missing.sort(),[...allowedOmissions].sort(),
  'unexpected loss of an existing PRO feature or reintroduced duplicate');
 assert.equal(id(html,'pro-reentry-state'),1);
 assert.equal(id(html,'source-trace-body'),1);
 assert.equal(id(html,'monday-reading'),1);
 assert.equal(id(html,'cn-forward-source-status'),1);
 assert.equal(id(html,'premium-rotation'),1);
 // PRO source reuse must still be source-only, never an independent engine.
});


test('Quiet Precision v2 keeps the 12h nowcast distinct from 1–3d official horizon',()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const idName of ['cn-horizon-13','cn-horizon-13-label',
  'cn-horizon-13-posture','premium-now-direction','premium-now-action',
  'cn-risk-quick-state','cn-risk-quick-steps'])
  assert.equal(id(html,idName),1,idName);
 assert.match(html,/1–3 dage · kildevurdering/);
 assert.match(html,/id="cn-alt-milestone-eta"/);
 assert.match(html,/id="cn-alt-milestone-state"/);
 assert.match(html,/id="premium-path-rail"/);
 const runtimeSource=html.indexOf('id="compass-pro"');
 const chartSource=html.indexOf('id="variant-panel"');
 assert.ok(runtimeSource>=0&&chartSource>runtimeSource);
});
test('design keeps W44 without invented daily forecast, and source-issued 7d path available',async()=>{
 const adapter=await read('./graph-b/official-source-adapter.mjs');
 const graph=await read('./graph-b/source-graph-b.mjs');
 const runtime=await read('./root-compass-pro.mjs');
 const style=await read('./premium-overhaul.css');
 assert.match(adapter,/forecastStatus='SOURCE_ISSUED'/);
 assert.match(adapter,/values\.length===7/);
 assert.match(adapter,/forecastStatus='PUBLISHED_INVALID_FAIL_CLOSED'/);
 assert.match(graph,/attr\('forecast','d',''\)/);
 assert.match(graph,/edge\('forecast_high'\)/);
 assert.match(graph,/edge\('forecast_low'\)/);
 assert.match(style,/#variant-panel #range-band/);
 assert.match(style,/#variant-panel \.alt-token \{display:none!important\}/);
 assert.match(runtime,/renderQuickDecision\(\)/);
 assert.match(runtime,/renderRiskQuick\(\)/);
 assert.match(runtime,/renderAltMilestone\(\)/);
 assert.match(runtime,/No verified ETA/);
});


test('this week W44 frozen Monday ranges do not authorize a blue expected-close curve',async()=>{
 const frozen=JSON.parse(await read('../../weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
 assert.equal(frozen.daily_price_path.contract,'CN_FROZEN_DAILY_PRICE_PATH_v1');
 assert.equal(frozen.daily_price_path.forecast_week,'2026-W44');
 assert.equal(frozen.daily_price_path.BTC.status,'UNAVAILABLE');
 assert.equal(frozen.daily_price_path.ETH.status,'UNAVAILABLE');
 assert.deepEqual(frozen.daily_price_path.BTC.points,[]);
 assert.deepEqual(frozen.daily_price_path.ETH.points,[]);
 assert.equal(frozen.btc_range_low,75000);
 assert.equal(frozen.btc_range_high,86000);
 assert.equal(frozen.eth_range_low,2150);
 assert.equal(frozen.eth_range_high,2550);
});


test('frozen intraday windows are forecast presentation even without expected-close path',async()=>{
 const renderer=await read('./graph-b/source-graph-b.mjs');
 assert.match(renderer,/Original prognose · 3 vinduer/);
 assert.match(renderer,/Mandagens prisinterval/);
 assert.match(renderer,/bands\.map\(b=>/);
 assert.match(renderer,/paintFrozenWindowLedger\(bands\)/);
 assert.match(renderer,/paintFrozenWindowLedger\(\[\]\)/);
 assert.match(renderer,/cn-frozen-window-day/);
 const html=buildUnifiedRootHtml(original,pro);
 assert.equal(id(html,'cn-frozen-window-ledger'),1);
 assert.match(renderer,/attr\('forecast','d',''\)/);
 const frozen=JSON.parse(await read('../../weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
 for(const key of ['day_1_2','day_3_4','day_5_7'])
  assert.ok(frozen.intraday_map[key].includes('BTC')&&frozen.intraday_map[key].includes('ETH'),key);
 assert.equal(frozen.daily_price_path.BTC.status,'UNAVAILABLE');
 assert.equal(frozen.daily_price_path.ETH.status,'UNAVAILABLE');
});


test('premium finish: fabricated W44 midpoint curve and large test explanation do not ship',async()=>{
 const renderer=await read('./graph-b/source-graph-b.mjs');
 const html=buildUnifiedRootHtml(original,pro);
 assert.doesNotMatch(renderer,/illustrative-test-curve|cn-demo-warning|forecast_low\+w\.forecast_high/);
 assert.doesNotMatch(html,/illustrative-test-curve|cn-demo-warning|TESTLINJE · ILLUSTRATION/);
 assert.match(html,/class="cn-range-evidence"/);
 assert.equal(id(html,'cn-frozen-window-ledger'),1);
 assert.match(html,/id="cn-forecast-legend" hidden/);
 assert.match(renderer,/forecastLegend\.hidden=model\?\.forecast_status!=='SOURCE_ISSUED'/);
 assert.match(renderer,/hasDailyRanges/);
 assert.match(renderer,/paintDailyResearchNotes/);
 assert.match(renderer,/edge\('forecast_high'\)/);
 assert.match(renderer,/edge\('forecast_low'\)/);
 assert.match(renderer,/attr\('forecast','d',movePath\(f\.map\(xy\)\)\)/);
});

test('premium finish: visual proof screenshots are captured on exact tested root',async()=>{
 const browser=await read('./next-browser.test.mjs');
 assert.match(browser,/CN_DESIGN_SCREENSHOT_/);
 assert.match(browser,/Page\.captureScreenshot/);
 assert.match(browser,/scrollIntoView/);
 assert.match(browser,/assert\.ok\(shot\.data\?\.length>1000/);
});


test('site #1578: four genuine views are mounted only in the unified root',async()=>{
 const html=buildUnifiedRootHtml(original,pro);
 assert.match(html,/src="\.\/premium-tabs\.mjs"/);
 assert.match(html,/href="\.\/premium-tabs\.css"/);
 const tabs=await read('./premium-tabs.mjs');
 const css=await read('./premium-tabs.css');
 for(const k of ['compass','graph','path','proof'])
   assert.match(tabs,new RegExp("'"+k+"'"));
 for(const id of ['compass-pro','variant-panel','official-path-view','proof-explorer'])
   assert.match(tabs,new RegExp("'"+id+"'"));
 assert.match(tabs,/history\.pushState/);
 assert.match(tabs,/popstate/);
 assert.match(tabs,/hashchange/);
 assert.match(tabs,/aria-selected/);
 assert.match(tabs,/ArrowRight/);
 assert.match(tabs,/ArrowLeft/);
 assert.match(tabs,/if \(nav && nodes\.every\(x => x\.link && x\.panel\)\)/);
 assert.match(css,/\.cn-tabbed-ui \[role="tabpanel"\]\[hidden\]/);
 assert.match(css,/overflow-x:auto/);
 assert.match(css,/min-height:44px/);
 assert.doesNotMatch(tabs,/Math\.sin|forecast_low|forecast_high|fetch\(|probability|probabilit/);
 const old=buildPremiumRootHtml(original);
 assert.doesNotMatch(old,/premium-tabs\.mjs|premium-tabs\.css/);
});

test('pullback first fold mirrors only eligible official PRO stages, never raises risk itself',async()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const marker of [
  'cn-risk-quick-meaning','cn-risk-quick-action','cn-risk-quick-quality',
  'cn-risk-quick-onset','cn-risk-quick-state','cn-risk-quick-steps'
 ])assert.equal(id(html,marker),1,'missing or duplicate source-bound risk field '+marker);
 const runtime=await read('./root-compass-pro.mjs');
 assert.match(runtime,/view\.compass\.permit_path_live_gates===true/);
 assert.match(runtime,/feeds\.compass\.data_status==='OK'/);
 assert.match(runtime,/feeds\.compass\.compass_id===view\.compass\.compass_id/);
 assert.match(runtime,/feeds\.compass\.weekly_context\?\.status==='ALIGNED'/);
 assert.match(runtime,/copy\?\.action_authority===false/);
 assert.match(runtime,/copy\?\.risk_state===p\?\.pullback_risk_state/);
 assert.match(runtime,/\$\('pro-risk-stage'\)\?\.textContent/);
 assert.match(runtime,/\$\('pro-guidance'\)\?\.textContent/);
 assert.match(runtime,/surface\.dataset\.current=stage\?'true':'false'/);
 assert.doesNotMatch(runtime,/const\s+pullbackThreshold\s*=/);
 assert.doesNotMatch(html,/eventProbability\s*:\s*\d/);
 const css=await read('./premium-tabs.css');
 assert.match(css,/\.cn-risk-quick \.cn-risk-quick-guidance/);
 assert.match(css,/@media\(max-width:540px\)/);
});


test('owner Kompas reading: four sourced horizons, minimal glossary and no competing action owner',async()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const id of [
  'cn-reader-title','cn-reader-analysis','cn-reader-direction','cn-reader-posture',
  'cn-reader-source','cn-reader-lens-note','cn-reader-glossary-title'
 ])assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id);
 for(const {id} of VIEWS)assert.match(html,new RegExp('data-cn-reader-horizon="'+id+'"'));
 for(const lens of ['swing','hodl'])assert.match(html,new RegExp('data-cn-reader-lens="'+lens+'"'));
 assert.equal((html.match(/class="cn-reader-glossary"/g)||[]).length,1);
 for(let i=1;i<=5;i++){
  assert.match(html,new RegExp('id="cn-reader-term-'+i+'"'));
  assert.match(html,new RegExp('id="cn-reader-definition-'+i+'"'));
 }
 assert.ok(html.indexOf('cn-risk-quick')<html.indexOf('class="cn-reader"'));
 assert.ok(html.indexOf('class="cn-reader"')<html.indexOf('class="cn-pro-more"'));
 assert.equal((html.match(/id="premium-now-action"/g)||[]).length,1);
 const runtime=await read('./root-compass-pro.mjs');
 assert.match(runtime,/readHorizon\(/);
 assert.match(runtime,/renderReader\(\)/);
 assert.match(runtime,/selectedReaderHorizon/);
 assert.match(runtime,/selectedReaderLens/);
 assert.match(runtime,/SOURCE_RECHECK_MS=5\*60\*1000/);
 const src=await read('./compass-reader.mjs');
 assert.doesNotMatch(src,/fetch\(|Math\.random|expected_close|market\.price|apiKey|sell_assessment|risk_stage/);
 const css=await read('./premium-tabs.css');
 assert.match(css,/\.cn-reader-periods\{/);
 assert.match(css,/grid-template-columns:repeat\(4,minmax\(0,1fr\)\)/);
 assert.match(css,/min-height:44px/);
});

test('source-only Kompas interpretation: precise translations, stale abstention, no invented action',()=>{
 const now=Date.parse('2026-10-30T08:00:00Z');
 const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-TEST'},
  weekly:{forecast_week:'2026-W44'}};
 const path='MIXED with downside risk: original verified source analysis.';
 const compass={
  contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-TEST',
  issued_at_utc:'2026-10-30T07:19:13Z',
  full_stack:{official_freshness:{valid_until_utc:'2026-10-30T10:00:00Z'}},
  weekly_context:{status:'ALIGNED',forecast_week:'2026-W44'},
  action_now:'HOLD_WAIT',
  horizons:{NEXT_1_3D:{expected_direction:'MIXED',action_posture:'WAIT',
   expected_path:path},NEXT_5_7D:{expected_direction:'MIXED',action_posture:'WAIT',
   expected_path:'Untranslated but published original commentary.'}}
 };
 const latest={presentation_translations:[{en:path,da:'Blandede signaler med risiko for fald.'}]};
 assert.equal(currentCompass({compass,view,now}),true);
 const good=readHorizon({latest,compass,view,now,lang:'da'});
 assert.equal(good.current,true);
 assert.equal(good.direction,'Blandet');
 assert.equal(good.posture,'Afvent');
 assert.equal(good.description,'Blandede signaler med risiko for fald.');
 assert.equal(good.translated,true);
 assert.match(lensContext(good,'swing','da'),/afvent/);
 assert.match(lensContext(good,'hodl','da'),/ikke i sig selv tilladelse/);
 const noTranslation=readHorizon({latest,compass,view,now,lang:'da',id:'NEXT_5_7D'});
 assert.equal(noTranslation.translated,false);
 assert.equal(noTranslation.description,'Untranslated but published original commentary.');
 assert.equal(sourceTranslation('','', 'da').text,'');
 assert.equal(sourceTranslation('MIXED with UNAVAILABLE decision today.',{},'da').text,
   'blandet with ikke fastlagt decision today.');
 const stale=readHorizon({latest,compass,view:{...view,compass:{...view.compass,state:'DEGRADED'}},now,lang:'da'});
 assert.equal(stale.current,false);
 assert.match(stale.description,/Ingen aktuel/);
 assert.match(lensContext(stale,'swing','da'),/gamle eller manglende data/);
 assert.equal(readHorizon({latest,compass,view,now:Date.parse('2026-10-30T10:01:00Z')}).current,false);
 assert.equal(readHorizon({latest,compass:{...compass,data_status:'DEGRADED'},view,now}).current,false);
 assert.equal(readHorizon({latest,compass:{...compass,compass_id:'WRONG'},view,now}).current,false);
 assert.equal(readHorizon({latest,compass:{...compass,weekly_context:{...compass.weekly_context,forecast_week:'2026-W45'}},view,now}).current,false);
 assert.equal(readHorizon({latest,compass:{...compass,issued_at_utc:'2026-11-01T00:00:00Z'},view,now}).current,false);
});


test('Kompas WAIT is a contextual answer with horizon, distinct review window and no invented edge',()=>{
 const now=Date.parse('2026-10-30T09:00:00Z');
 const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-WAIT'},
  weekly:{forecast_week:'2026-W44'}};
 const latest={presentation_translations:[{
   en:'Watch whether ETH/BTC and breadth recover.',
   da:'Hold øje med, om ETH/BTC og markedsbredden forbedres.'
 }]};
 const compass={
  contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',compass_id:'CMP-WAIT',
  issued_at_utc:'2026-10-30T08:30:02Z',action_now:'HOLD_WAIT',
  weekly_context:{status:'ALIGNED',forecast_week:'2026-W44'},
  full_stack:{official_freshness:{valid_until_utc:'2026-10-30T11:00:00Z'}},
  horizons:{NEXT_1_3D:{expected_direction:'MIXED',action_posture:'WAIT',eta:'24-72h',
    expected_path:'The short-term evidence is mixed and weak.'}},
  protection_tracker:{
   pullback_risk_state:'ELEVATED',
   public_explanation:{
    contract:'CN_PUBLIC_PROTECTION_COPY_v1',action_authority:false,
    forecast_week:'2026-W44',risk_state:'ELEVATED',
    watch_for:'Watch whether ETH/BTC and breadth recover.'
   }
  }
 };
 const reading=readHorizon({latest,compass,view,lang:'da',now});
 assert.equal(reading.reviewWindow,'24–72h');
 assert.match(explainCurrentAction({latest,compass,view,lang:'da',now}),/1–3 dage: blandede signaler/);
 assert.match(explainCurrentAction({latest,compass,view,lang:'da',now}),/Revurdering: 24–72 timer/);
 assert.match(explainPosture(reading,'da'),/Afvent = signalerne peger begge veje/);
 assert.match(explainPosture(reading,'da'),/Intet nyt køb eller salg er bekræftet/);
 assert.equal(sourceWatch({latest,compass,view,lang:'da',now})?.text,
   'Hold øje med, om ETH/BTC og markedsbredden forbedres.');
 assert.match(explainPosture(reading,'en'),/Wait = evidence points both ways/);
 const down={...compass,horizons:{NEXT_1_3D:{
   ...compass.horizons.NEXT_1_3D,expected_direction:'DOWN'}}};
 assert.match(explainPosture(readHorizon({latest,compass:down,view,now})),/ikke et selvstændigt salgssignal/);
 assert.match(explainCurrentAction({latest,compass:down,view,now}),/intet selvstændigt salgssignal/);
 const up={...compass,horizons:{NEXT_1_3D:{
   ...compass.horizons.NEXT_1_3D,expected_direction:'UP'}}};
 assert.match(explainCurrentAction({latest,compass:up,view,now}),/intet nyt køb/);
 const unscoped={...compass,horizons:{NEXT_1_3D:{
   ...compass.horizons.NEXT_1_3D,eta:'2026-11-02T20:00:00Z'}}};
 assert.doesNotMatch(explainCurrentAction({latest,compass:unscoped,view,now}),/Revurdering/);
 const expired=Date.parse('2026-10-30T11:01:00Z');
 assert.match(explainCurrentAction({latest,compass,view,now:expired}),/Ingen gyldige aktuelle data/);
 assert.equal(sourceWatch({latest,compass,view,now:expired}),null);
 assert.equal(explainCurrentAction({latest,compass:{...compass,action_now:'BUY'},view,now}),null);
 assert.equal(sourceWatch({latest,compass:{...compass,protection_tracker:{
   ...compass.protection_tracker,public_explanation:{
   ...compass.protection_tracker.public_explanation,action_authority:true}}},view,now}),null);
});

test('source-bound interpretation is attached to original verdict without adding market authority',async()=>{
 const html=buildUnifiedRootHtml(original,pro);
 for(const id of ['premium-action-meaning','cn-reader-why','cn-reader-watch'])
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id);
 const runtime=await read('./root-compass-pro.mjs');
 assert.match(runtime,/explainCurrentAction\(/);
 assert.match(runtime,/set\('premium-action-meaning',adaptive\)/);
 assert.match(runtime,/explainPosture\(/);
 assert.match(runtime,/sourceWatch\(/);
 const reader=await read('./compass-reader.mjs');
 assert.doesNotMatch(reader,/fetch\(|Math\.random|apiKey|portfolio_execution/);
 assert.match(reader,/No new buy or sell is confirmed/);
 const css=await read('./premium-tabs.css');
 assert.match(css,/\.cn-reader-outlook \.cn-reader-why/);
});


test('visible Kompas product v3 has 12h observation, three sourced horizon cards, pullback rail and class summary in that order',async()=>{
 const html=buildUnifiedRootHtml(original,pro);
 const markers=[
  'id="premium-now-action"','id="premium-now-direction"','id="cn-horizon-13"',
  'id="cn-overview-heading"','data-cn-overview="d13"',
  'data-cn-overview="d57"','data-cn-overview="w23"',
  'id="cn-risk-quick-steps"','id="cn-risk-quick-brief"',
  'id="cn-rotation-classes"','id="cn-position-terms"','id="cn-reader-title"'
 ];
 for(const marker of markers)assert.equal((html.match(new RegExp(marker,'g'))||[]).length,1,marker);
 const positions=markers.map(x=>html.indexOf(x));
 for(let i=1;i<positions.length;i++)assert.ok(positions[i]>positions[i-1],
  'OUT_OF_ORDER '+markers[i-1]+' -> '+markers[i]);
 assert.match(html,/<details class="cn-risk-more">/);
 assert.match(html,/<details class="cn-reader-expand">/);
 assert.match(html,/<details class="cn-position-guide">/);
 assert.doesNotMatch(html,/<details class="cn-risk-more" open/);
 assert.doesNotMatch(html,/<details class="cn-reader-expand" open/);
 const runtime=await read('./root-compass-pro.mjs');
 assert.match(runtime,/renderOverview\(\)/);
 assert.match(runtime,/readRotation\(/);
 assert.match(runtime,/publicOverview\(/);
 assert.match(runtime,/cn-overview-'\+key\+'-balance/);
 const css=await read('./premium-tabs.css');
 assert.match(css,/\.cn-overview-cards/);
 assert.match(css,/\.cn-rotation-classes/);
 assert.match(css,/\.cn-risk-more/);
 assert.match(css,/\.cn-position-guide/);
});

test('official horizon evidence and capital ladder remain source-bound, not probabilities or invented 24h paths',()=>{
 const now=Date.parse('2026-10-30T09:00:00Z');
 const view={compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CID'},
  weekly:{forecast_week:'2026-W44'}};
 const horizons={
 NEXT_1_3D:{expected_direction:'MIXED',action_posture:'WAIT',expected_path:'Mixed early readings are conflicting.'},
 NEXT_5_7D:{expected_direction:'DOWN',action_posture:'WAIT',expected_path:'Source issued bearish weekly context.'},
 NEXT_2_3W:{expected_direction:'UP',action_posture:'WAIT',expected_path:'Source issued rising longer context.'}
 };
 const balance={
  contract:'OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1',
  owner:'OFFICIAL_COMPASS',resolution:'COARSE_CATEGORICAL_DIRECTION',
  authority:{probability_model:false,site_synthesis_allowed:false},
  horizons:{'1_3d':{status:'OK',bull:5,bear:5},
   '5_7d':{status:'OK',bull:2,bear:8},
   '2_3w':{status:'OK',bull:7,bear:3}}
 };
 const segments=[
 ['BTC','HOLD'],['ETH','HOLD'],['LARGE_CAPS','WAIT'],
 ['MID_CAPS','WAIT'],['SMALL_CAPS','WAIT'],['MICROCAPS','HARD_WAIT'],
 ['MEMES','UNAVAILABLE']
 ];
 const compass={
  compass_id:'CID',contract:'PUBLIC_COMPASS_PROJECTION_v1',
  data_status:'OK',issued_at_utc:'2026-10-30T08:00:00Z',
  full_stack:{official_freshness:{valid_until_utc:'2026-10-30T10:00:00Z'}},
  weekly_context:{status:'ALIGNED',forecast_week:'2026-W44'},
  market_now:{directional_state:'DOWN'},horizons,
  bull_bear_scale:balance,
  capitalization_ladder:segments.map(([segment,action])=>({segment,action,status:action}))
 };
 const source=publicOverview({compass,latest:{},view,now,lang:'da'});
 assert.equal(source.valid,true);
 assert.deepEqual(source.observed12,{arrow:'↘',text:'Faldende',source:'DOWN'});
 assert.deepEqual(source.cards.map(x=>x.arrow),['↗ ↘','↘','↗']);
 assert.deepEqual(source.cards.map(x=>x.evidence),[
   {bull:5,bear:5},{bull:2,bear:8},{bull:7,bear:3}
 ]);
 assert.deepEqual(source.cards.map(x=>x.position),['Afvent','Afvent','Afvent']);
 assert.equal(source.cards[1].summary.text,'Source issued bearish weekly context.');
 assert.equal(directionVisual('MIXED','da').text,'Blandet');
 assert.equal(directionVisual('NOT_A_REAL_DIRECTION','da').arrow,'?');
 const rot=readRotation({compass,view,now,lang:'da'});
 assert.equal(rot.valid,true);
 assert.deepEqual(rot.rows.map(x=>x.sourceAction),segments.map(x=>x[1]));
 assert.equal(rot.rows[0].stance,'Behold eksisterende');
 assert.equal(rot.rows[5].stance,'Skærpet afvent');
 assert.equal(rot.rows[6].stance,'Ingen kildevurdering');
 assert.equal(POSITION_GUIDE.length,8);
 const badEvidence={...compass,bull_bear_scale:{...balance,authority:{...balance.authority,probability_model:true}}};
 assert.equal(publicOverview({compass:badEvidence,view,now}).cards[0].evidence,null);
 const fakeRatio={...compass,bull_bear_scale:{...balance,horizons:{...balance.horizons,'1_3d':{status:'OK',bull:8,bear:7}}}};
 assert.equal(publicOverview({compass:fakeRatio,view,now}).cards[0].evidence,null);
 const misaligned={...compass,weekly_context:{status:'ALIGNED',forecast_week:'2026-W45'}};
 assert.equal(publicOverview({compass:misaligned,view,now}).valid,false);
 assert.equal(readRotation({compass:misaligned,view,now}).valid,false);
 assert.equal(publicOverview({compass,view,now:Date.parse('2026-10-30T10:01:00Z')}).valid,false);
 const duplicate={...compass,capitalization_ladder:[...compass.capitalization_ladder,segments[0]]};
 assert.equal(readRotation({compass:duplicate,view,now}).valid,false);
 // Progression from WAIT to HOLD is NOT part of the public dictionary or engine.
 assert.ok(!Object.keys(horizons).includes('NEXT_24H'));
 assert.doesNotMatch((awaitedPositionDescription()),/WAIT.*=>.*HOLD/);
 function awaitedPositionDescription(){return POSITION_GUIDE.map(p=>p.slice(0,3).join(' ')).join(' | ')}
});
