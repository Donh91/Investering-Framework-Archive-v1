import './tests/full-stack-readback.test.mjs';
import './vnext-live/validate.mjs';
import { readFile } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
const thisRepoRoot=resolve(fileURLToPath(new URL('.',import.meta.url)),'../..');
execFileSync('python3',['scripts/cycle_navigator/check_publication_lineage.py','--self-test'],
  {cwd:thisRepoRoot,stdio:'inherit',timeout:30000});

import { preserveLegacyShell, releasePremiumShell } from './premium-release.mjs';
const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [html,build,liveBuilder,liveWidget,weeklyWidget,app,product,css,history,premium,premiumCss,compassV5,precision,precisionCss,precisionBuilder]=await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./build-live-observation.mjs'),read('./live-observation.js'),read('./weekly-score.js'),read('./app.js'),read('./public-product.js'),read('./public-product.css'),read('./history-scoreboard.json'),read('./market-compass-premium.js'),read('./market-compass-premium.css'),read('./compass-product-v5.js'),read('./precision-accountability.js'),read('./precision-accountability.css'),read('../../scripts/cycle_navigator/build_public_live_precision.py')]);
// Security regression, Cloudflare-inspired trust-boundary audit:
// an unavailable private source must not serialize a raw filesystem exception into
// public data/compass.json. Exercise the real fallback function with a synthetic
// failure. The negative control recreates the old unsafe assignment in memory only.
const compassFactoryStart=build.indexOf('async function buildCompassSnapshot(');
const compassFactoryEnd=build.indexOf('// PUBLIC_COMPASS_FULL_STACK_READBACK_v1:',compassFactoryStart);
if(compassFactoryStart<0||compassFactoryEnd<=compassFactoryStart)throw Error('Compass fallback regression cannot isolate actual builder');
const compassFactorySource=build.slice(compassFactoryStart,compassFactoryEnd);
const safeFailureMarker='OFFICIAL_COMPASS_SOURCE_UNAVAILABLE';
const syntheticInternalPath='/synthetic/internal/location/not-for-public';
const failingSource=async()=>{throw Error('ENOENT: '+syntheticInternalPath)};
const makeCompassFactory=source=>new Function('readJson','COMPASS_POINTER_PATH',source+';return buildCompassSnapshot;')(failingSource,'synthetic-public-pointer');
const safeFallback=await makeCompassFactory(compassFactorySource)({});
if(safeFallback.failure_state!==safeFailureMarker||
   safeFallback.data_status!=='NOT_PUBLISHED'||
   safeFallback.action_now!=='UNAVAILABLE'||
   JSON.stringify(safeFallback).includes(syntheticInternalPath))
  throw Error('Internal Compass exception was exposed in public fallback');
const unsafeSource=compassFactorySource.replace(
  'failure_state:"OFFICIAL_COMPASS_SOURCE_UNAVAILABLE"',
  'failure_state:String(error?.message||error)');
if(unsafeSource===compassFactorySource)throw Error('No security guard to mutation-test');
const unsafeFallback=await makeCompassFactory(unsafeSource)({});
if(!JSON.stringify(unsafeFallback).includes(syntheticInternalPath))
  throw Error('Security negative control did not detect the previous path disclosure');

const h=JSON.parse(history);
const chartSource=await read('./frozen-week-chart.js'),chartCss=await read('./frozen-week-chart.css');
const vnextShell=await read('./vnext-live/index.html');

const lineageSource=await read('../../scripts/cycle_navigator/check_publication_lineage.py');
if(!lineageSource.includes('PUBLIC_HOURLY_PRICE_DIVERGENCE_')||
   !lineageSource.includes('PUBLIC_HOURLY_FUTURE_CUTOFF')||
   !lineageSource.includes('PUBLIC_HOURLY_FUTURE_OBSERVATION')||
   !lineageSource.includes('CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1'))
  throw Error('Publication lineage source-first no-hindsight guards missing');
const proofSource=await read('./validate-compass-site-v5.mjs');
const helperStart=proofSource.indexOf('function verifiedRawDigest(');
const helperEnd=proofSource.indexOf('const [op,ap,wp,shp,stp]',helperStart);
const rawDigest=helperStart>=0&&helperEnd>helperStart
 ?new Function('createHash',proofSource.slice(helperStart,helperEnd)+';return verifiedRawDigest;')(createHash)
 :()=>false;
// A real producer preserves the numeric token 82116.0; JS JSON.stringify turns
// it into 82116. Valid bytes MUST pass; any reserialised or mutated bytes FAIL.
const sourceWithoutDigest='{"anchor_id":"proof","market_reference":{"btc_usdt":82116.0}}\n';
const frozenDigest=createHash('sha256').update(sourceWithoutDigest,'utf8').digest('hex');
const originalRaw='{"anchor_id":"proof","anchor_sha256":"'+frozenDigest+'","market_reference":{"btc_usdt":82116.0}}\n';
const originalData=JSON.parse(originalRaw);
const hashAcceptsOriginal=rawDigest(originalRaw,originalData,'anchor_sha256',frozenDigest);
const hashRejectsJsRewrite=!rawDigest(originalRaw.replace('82116.0','82116'),originalData,'anchor_sha256',frozenDigest);
const hashRejectsCorruptedFingerprint=!rawDigest(originalRaw.replace('"proof"','"evil"'),originalData,'anchor_sha256',frozenDigest);
const hashRejectsWrongExpected=!rawDigest(originalRaw,originalData,'anchor_sha256','0'.repeat(64));

const chartAPI={};new Function('window','document',chartSource)(chartAPI,{addEventListener(){}});const chartModel=chartAPI.CNWeekChart.model,chartLinePlan=chartAPI.CNWeekChart.linePlan,chartGraphDescription=chartAPI.CNWeekChart.graphDescription;
const etaStart=product.indexOf('function pathEta'),etaEnd=product.indexOf('function pathStatus');
const productSyntaxOk=(()=>{try{new Function(product);return true}catch{return false}})();
const etaSlice=etaStart>=0&&etaEnd>etaStart?product.slice(etaStart,etaEnd):'';
const pathTiming=new Function('investorText',etaSlice+';return {weeklyBackstoppedEta,etaDistance};')(v=>String(v??''));
// Exercise public renderers with synthetic contract inputs; never fetch market values.
const extract=(source,name,next)=>source.slice(source.indexOf('function '+name+'('),source.indexOf('function '+next+'('));
const escapeHtml=v=>String(v??'').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const graph=new Function('esc','utcLabel','publicPathText','return '+extract(product,'weeklyJourney','pathContext'))(escapeHtml,v=>String(v??''),v=>String(v??''));
const recommendationTest=new Function(extract(premium,'publicAction','cnConclusion')+';return recommendation;')();
const risk=new Function('esc','clean','publicState','publicCompassText','recommendation','return '+extract(premium,'pullbackCard','renderPremium'))(escapeHtml,v=>typeof v==='string'&&v.trim()?v.trim():null,v=>String(v||''),v=>String(v||''),recommendationTest);
const synthetic={public_series:{current_public_projection:{public_issue_number:9,forecast_week:'2026-W41'}},public_live_precision:{contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',public_issue_number:9,forecast_week:'2026-W41',live_as_of_utc:'2026-10-07T12:00:00Z',window_scores:{day_1_2:{window_start_utc:'2026-10-05T00:00:00Z',window_end_utc:'2026-10-07T00:00:00Z'},day_3_4:{window_start_utc:'2026-10-07T00:00:00Z',window_end_utc:'2026-10-09T00:00:00Z'},day_5_7:{window_start_utc:'2026-10-09T00:00:00Z',window_end_utc:'2026-10-12T00:00:00Z'}},rows:['BTC','ETH'].flatMap(asset=>['day_1_2','day_3_4','day_5_7'].map(window=>({asset,window,forecast_low:100,forecast_high:120,actual_low_to_date:window==='day_1_2'?99:null,actual_high_to_date:window==='day_1_2'?111:null,coverage_complete_to_date:window==='day_1_2'})))}};
synthetic.public_live_precision.daily_observations={contract:'CN_PUBLIC_DAILY_OBSERVATIONS_v1',observed_through_utc:'2026-10-07T12:00:00Z',...Object.fromEntries(['BTC','ETH'].map(asset=>[asset,Array.from({length:7},(_,i)=>({day:i+1,date:`2026-10-${String(i+5).padStart(2,'0')}`,close:i<2?110:null,low:i<2?99:null,high:i<2?111:null,as_of_utc:i<2?`2026-10-${String(i+6).padStart(2,'0')}T00:00:00Z`:null,status:i<2?'COMPLETE':'NOT_STARTED',coverage_complete_to_date:i<2}))]))};
const dailyFixture=structuredClone(synthetic);dailyFixture.public_live_precision.daily_price_path={contract:'CN_FROZEN_DAILY_PRICE_PATH_v1',forecast_week:'2026-W41',...Object.fromEntries(['BTC','ETH'].map(asset=>[asset,{status:'PUBLISHED',points:Array.from({length:7},(_,i)=>({day:i+1,low:100,high:120,expected_close:105+i}))}]))};
const frozenBefore=JSON.stringify(synthetic),graphHtml=graph(synthetic),gap=structuredClone(synthetic);gap.public_live_precision.daily_observations.BTC.forEach(r=>r.coverage_complete_to_date=false);gap.public_live_precision.daily_observations.ETH.forEach(r=>r.coverage_complete_to_date=false);
const riskInput={contract:'PUBLIC_COMPASS_PROJECTION_v1',data_status:'OK',protection_tracker:{contract:'COMPASS_PROTECTION_TRACKER_v1',pullback_risk_state:'BUILDING',pullback_class:'ORDINARY RETEST WATCH; DEPTH AND SEVERITY UNQUANTIFIED.',confidence_quality:'LOW',eta_window:'Conditional watch only',reentry_state:'INACTIVE'},sell_assessment:{contract:'COMPASS_SELL_ASSESSMENT_v1',state:'UNAVAILABLE'}};
const riskHtml=risk(riskInput,'CURRENT'),limitedRisk=risk({...riskInput,data_status:'STALE'},'UNAVAILABLE'),expiredRisk=risk(riskInput,'LAST_VERIFIED');
const translateCompass = new Function('words', premium.slice(premium.indexOf('const publicCompassText ='), premium.indexOf('function officialScale'))+';return publicCompassText;')(v=>String(v||''));
const translateInvestor=new Function('return '+extract(product,'investorText','publicPathText'))();
const weekIdentityText=translateCompass('W40 BTC gained 2.44%. Possible W41 retest.');
const futureFixture=structuredClone(synthetic);futureFixture.public_live_precision.daily_observations.BTC[6]={day:7,date:'2026-10-11',close:110,low:100,high:120,as_of_utc:'2099-10-12T00:00:00Z',coverage_complete_to_date:true};
const badDaily=structuredClone(dailyFixture);badDaily.public_live_precision.daily_price_path.BTC.points[3].expected_close=130;
const badDate=structuredClone(synthetic);badDate.public_live_precision.daily_observations.BTC[0].date='2026-10-06';
const positivePlan=chartLinePlan(chartModel(dailyFixture,'BTC'));
const missingForecastPlan=chartLinePlan(chartModel(synthetic,'BTC'));
const observedGap=structuredClone(dailyFixture);
observedGap.public_live_precision.daily_observations.BTC[1].coverage_complete_to_date=false;
observedGap.public_live_precision.daily_observations.BTC[2]={
  day:3,date:'2026-10-07',close:112,low:100,high:118,
  as_of_utc:'2026-10-07T12:00:00Z',status:'PARTIAL',
  coverage_complete_to_date:true,observed_hours:12
};
const gappedPlan=chartLinePlan(chartModel(observedGap,'BTC'));
const hourlyActual=structuredClone(synthetic);
hourlyActual.public_live_precision.hourly_price_path={
 contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',forecast_week:'2026-W41',public_issue_number:9,
 source:'HOURLY_SPOT_PASS_ONLY',semantics:'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',
 observed_through_utc:'2026-10-07T12:00:00Z',
 BTC:[1,2,3,5,6].map((hour,i)=>({
   observed_at_utc:'2026-10-05T'+String(hour).padStart(2,'0')+':00:00Z',close:106+i
 })),
 ETH:[1,2].map(hour=>({
   observed_at_utc:'2026-10-05T'+String(hour).padStart(2,'0')+':00:00Z',close:2100+hour
 }))
};
const hourlySourceModel=chartModel(hourlyActual,'BTC'),actualHourlyPlan=chartLinePlan(hourlySourceModel);
const wrongHourlyWeek=structuredClone(hourlyActual);wrongHourlyWeek.public_live_precision.hourly_price_path.forecast_week='2026-W42';
const futureHourly=structuredClone(hourlyActual);futureHourly.public_live_precision.hourly_price_path.BTC.push({observed_at_utc:'2099-10-05T04:00:00Z',close:110});
const invalidHourlySource=structuredClone(hourlyActual);invalidHourlySource.public_live_precision.hourly_price_path.BTC[0].close=-2;
const hourMismatchIssue=structuredClone(hourlyActual);hourMismatchIssue.public_live_precision.hourly_price_path.public_issue_number=8;


// Render the actual shipped PATH mount against an instrumented TradingView v5
// and Canvas2D adapter. This catches omitted primitive attachment (a real P2)
// instead of trusting textual assertions about an unused drawing class.
function probeChartRender(data){
  const paints={fills:0,whiskerStrokes:0,intervalRects:0,attached:0};
  const ctx={
    save(){},restore(){},beginPath(){},moveTo(){},lineTo(){},closePath(){},
    fill(){paints.fills++},stroke(){paints.whiskerStrokes++},
    // Corridor price-band rectangles are 30px in this deterministic scale;
    // 20px label capsules and 320px future-time shading are not corridors.
    fillRect(x,y,width,height){if(height>20&&height<100)paints.intervalRects++},strokeRect(){},fillText(){},
    setLineDash(){},measureText(text){return {width:text.length*7}},
    createLinearGradient(){return {addColorStop(){}}}
  };
  const series=[];
  const scale={
    timeToCoordinate(t){return 25+(t-Date.parse('2026-10-05T00:00:00Z')/1000)/86400*58},
    setVisibleLogicalRange(){},fitContent(){}
  };
  const chart={
    timeScale(){return scale},remove(){},subscribeCrosshairMove(){},subscribeClick(){},
    addSeries(kind,options){
      const record={kind,options,data:[],primitives:[]};series.push(record);
      return {
        setData(points){record.data=points},
        priceToCoordinate(v){return 280-v*1.5},
        attachPrimitive(primitive){
          paints.attached++;record.primitives.push(primitive);
          primitive.attached({chart,requestUpdate(){}});
          primitive.paneViews()[0].renderer().draw({
            useMediaCoordinateSpace(f){f({context:ctx,mediaSize:{width:470,height:320}})}
          });
        }
      };
    }
  };
  const el={innerHTML:'',onclick:null,setAttribute(){}},buttons=Array.from({length:7},(_,i)=>({dataset:{fwDay:String(i)},setAttribute(){},onclick:null}));
  const host={
    isConnected:true,innerHTML:'',
    querySelector(selector){return el},
    querySelectorAll(selector){return selector==='[data-fw-day]'?buttons:[]}
  };
  chartAPI.LightweightCharts={
    ColorType:{Solid:'solid'},LineStyle:{Dotted:1,Solid:0,Dashed:2},
    LineType:{Simple:0},CrosshairMode:{Normal:0},LineSeries:'line',
    createChart(){return chart}
  };
  chartAPI.CNWeekChart.mount(host,data);
  return {paints,series};
}
// The actual shipped role=img description must not advertise a daily
// prediction when only weekly range windows were frozen. DA/EN covers VoiceOver copy.
const notYetObserved=structuredClone(dailyFixture);
notYetObserved.public_live_precision.daily_observations.BTC.forEach(p=>p.coverage_complete_to_date=false);
const neitherObservedNorPublished=structuredClone(synthetic);
neitherObservedNorPublished.public_live_precision.daily_observations.BTC.forEach(p=>p.coverage_complete_to_date=false);
chartAPI.CNI18n={language:'en'};
const a11yUnavailableEn=chartGraphDescription(chartModel(synthetic,'BTC'));
const a11yPublishedEn=chartGraphDescription(chartModel(dailyFixture,'BTC'));
const a11yPublishedNoActualEn=chartGraphDescription(chartModel(notYetObserved,'BTC'));
const a11yLegacyNoActualEn=chartGraphDescription(chartModel(neitherObservedNorPublished,'BTC'));
chartAPI.CNI18n.language='da';
const a11yUnavailableDa=chartGraphDescription(chartModel(synthetic,'BTC'));
const a11yPublishedDa=chartGraphDescription(chartModel(dailyFixture,'BTC'));
const a11yPublishedNoActualDa=chartGraphDescription(chartModel(notYetObserved,'BTC'));
const a11yLegacyNoActualDa=chartGraphDescription(chartModel(neitherObservedNorPublished,'BTC'));
chartAPI.CNI18n.language='en';
const publishedRender=probeChartRender(dailyFixture);
const legacyRender=probeChartRender(synthetic);
const hourlyRender=probeChartRender(hourlyActual);
const packageSanitizer=new Function(build.slice(build.indexOf('const pick='),build.indexOf('async function readJson'))+';return sanitizePackage;')();
const translationProjection=new Function('sanitizePackage','standaloneFreeze','publicStructureAnalysis','return '+build.slice(build.indexOf('function publicTranslations('),build.indexOf('const snapshot=')))(packageSanitizer,{},()=>null);
const bilingualFixture={market_state:'BTC gained +2.44% in week 40.',public_translations:[{en:'BTC gained +2.44% in week 40.',da:'BTC steg +2.44% i uge 40.'},{en:'BTC gained +2.44% in week 40.',da:'BTC faldt −2.44% i uge 40.'},{en:'Private forecast value 9000.',da:'Privat prognoseværdi 9000.'}],private_scenario:'Private forecast value 9000.'};
const acceptedTranslations=translationProjection(bilingualFixture);
const checks=[
 ['CRITICAL future 7-day blue expected CLOSE must timestamp each UTC DAY END not prior morning',
   positivePlan.forecast.every((p,i)=>p.time===chartModel(dailyFixture,'BTC').days[i].time+86400)&&
   positivePlan.forecast[0].time===Date.parse('2026-10-06T00:00:00Z')/1000&&
   positivePlan.forecast[6].time===Date.parse('2026-10-12T00:00:00Z')/1000],
 ['CRITICAL observed partial/closed-day fallback uses exact owner as_of, NOT day-start or future day-end',
   gappedPlan.actualRuns[0][0].time===Date.parse('2026-10-06T00:00:00Z')/1000&&
   gappedPlan.actualRuns[1][0].time===Date.parse('2026-10-07T12:00:00Z')/1000&&
   chartSource.includes('x(d.closeTime),y(d.forecast.high)')&&
   chartSource.includes('time:(m.start+horizon*DAY)/1000')&&
   chartSource.includes('scaleAnchor.setData([...m.days.map')],
 ['Real TradingView mount draws two independent GREEN 1h runs, BLUE daily series stays absent without source',
   hourlyRender.series.filter(s=>s.options?.color==='#27c59a').length===2&&
   hourlyRender.series.filter(s=>s.options?.color==='#27c59a').map(s=>s.data.length).join(',')==='3,2'&&
   hourlyRender.series.filter(s=>s.options?.color==='#5f96ff').every(s=>s.data.length===0)&&
   chartSource.includes('chart.timeScale().fitContent()')],
 ['Official owner-approved B navy shell retains source evidence, and no longer competes with a synthetic external design demo',
   chartSource.includes("drawer.className='fw-evidence-details'")&&
   chartSource.includes("host.ownerDocument?.createElement")&&
   chartCss.includes('.fw-evidence-details summary{min-height:44px')&&
   vnextShell.includes('class="cn-original-ranges"')&&
   vnextShell.includes('id="btc-range"')&&vnextShell.includes('id="eth-range"')&&
   vnextShell.includes('id="official-path-chart" class="frozen-week-chart"')&&
   !vnextShell.includes('cycle-navigator-forward-outlook-1-3w-z8say7.v2.appdeploy.ai')&&
   vnextShell.includes('class="cn-forward"')&&
   vnextShell.includes('data-t="forwardPriceMissing"')&&
   chartSource.includes("No authentic daily forecast was published, so no forecast curve is drawn.")],
 ['Owner-approved B forecast renders behind a thicker actual line, WITHOUT fabricating blue W43',
   publishedRender.series[0].options?.lineStyle===2&&publishedRender.series[0].options?.lineWidth===2&&
   publishedRender.series.some(s=>s.options?.color==='#27c59a'&&s.options?.lineStyle===0&&s.options?.lineWidth===4)&&
   hourlyRender.series[0].data.length===0&&
   hourlyRender.series.filter(s=>s.options?.color==='#27c59a').every(s=>s.options.lineWidth===4)&&
   chartCss.includes('CN_GRAPH_B_APPROVED_2026_10_21')&&chartCss.includes('.fw-legend .forecast{border-top:2px dashed #5f96ff}')],
 ['TRUE hourly observations render actual line with missing hours disconnected and no fake future forecast',
   hourlySourceModel.hourly.length===5&&actualHourlyPlan.forecast.length===0&&
   actualHourlyPlan.actualRuns.length===2&&actualHourlyPlan.actualRuns[0].length===3&&
   actualHourlyPlan.actualRuns[1].length===2&&
   actualHourlyPlan.actualRuns[0][0].value===106&&
   actualHourlyPlan.actualRuns[1][0].time-actualHourlyPlan.actualRuns[0].at(-1).time===7200],
 ['Wrong issue/week, future hour and invalid negative price fail hourly projection closed',
   [wrongHourlyWeek,hourMismatchIssue,futureHourly,invalidHourlySource].every(x=>
     chartModel(x,'BTC').hourly.length===0)&&chartModel(hourlyActual,'ETH').hourly.length===2],
 ['Published daily forecast preserves exact seven source points independently of hourly actuals',
   chartLinePlan(chartModel({...dailyFixture,public_live_precision:{...dailyFixture.public_live_precision,
     hourly_price_path:hourlyActual.public_live_precision.hourly_price_path}},'BTC')).forecast.length===7],
 ['Public hourly projection is bounded, source-guarded, and not a forecast',
   precisionBuilder.includes('public_hourly_price_path(')&&
   precisionBuilder.includes('HOURLY_SPOT_PASS_ONLY')&&
   precisionBuilder.includes('cutoff is None')&&
   chartSource.includes('CN_PUBLIC_HOURLY_PRICE_PATH_v1')&&
   chartSource.includes('point.time-current.at(-1).time!==3600')],
 ['W43 Pages byte-true anchor integrity accepts producer numeric spelling 82116.0 and rejects any altered source',hashAcceptsOriginal&&hashRejectsJsRewrite&&hashRejectsCorruptedFingerprint&&hashRejectsWrongExpected],
 ['Danish projection accepts public prose and rejects changed numeric signs',acceptedTranslations.length===1&&acceptedTranslations[0].da==='BTC steg +2.44% i uge 40.'],
 ['Danish projection cannot publish untranslated private-scenario source content',!acceptedTranslations.some(x=>x.en.includes('9000'))&&translationProjection({market_state:'Legacy source without translations.'}).length===0],
 ['weekly chart rejects future timestamps and wrong UTC day identity',!chartModel(futureFixture,'BTC').days[6].actual&&!chartModel(badDate,'BTC').days[0].actual],
 ['invalid daily forecast bounds fail to published ranges without fabricated line',chartModel(badDaily,'BTC').daily.length===0&&chartModel(badDaily,'BTC').rows.length===3],
 ['TradingView weekly chart is self-hosted and overlays authentic evidence only',liveBuilder.includes('vendor/lightweight-charts-5.2.0.js')&&chartSource.includes('lineVisible:false')&&chartSource.includes('if(d.actual)current.push(')&&chartSource.includes("['D1–2','D3–4','D5–7']")&&!chartSource.includes('LineType.Curved')],
 ['published daily forecast is exactly seven immutable points and actual does not extend into future',
    positivePlan.forecast.length===7&&positivePlan.actualRuns.length===1&&positivePlan.actualRuns[0].length===2&&
    positivePlan.forecast.every((p,i)=>p.time===chartModel(dailyFixture,'BTC').days[i].closeTime&&p.value===105+i)&&
    positivePlan.actualRuns[0].every((p,i)=>p.value===110&&p.time===Date.parse(chartModel(dailyFixture,'BTC').days[i].actual.as_of_utc)/1000)],
 ['unpublished daily path plots no fabricated forecast while preserving real observations',
    missingForecastPlan.forecast.length===0&&missingForecastPlan.actualRuns.length===1&&
    missingForecastPlan.actualRuns[0].length===2],
 ['missing source coverage splits actual line into disjoint runs, never bridges data gaps',
    gappedPlan.forecast.length===7&&gappedPlan.actualRuns.length===2&&
    gappedPlan.actualRuns.every(run=>run.length===1)&&
    gappedPlan.actualRuns[0][0].time===Date.parse(chartModel(observedGap,'BTC').days[0].actual.as_of_utc)/1000&&
    gappedPlan.actualRuns[1][0].time===Date.parse(chartModel(observedGap,'BTC').days[2].actual.as_of_utc)/1000],
 ['Approved B two-curve display has dashed frozen 7d forecast and dominant solid actual, with honest missing-path fallback',chartSource.includes('lineStyle:lib.LineStyle.Dashed,lineWidth:2')&&chartSource.includes('lineStyle:lib.LineStyle.Solid')&&chartSource.includes('scaleAnchor.attachPrimitive(new EvidenceOverlay(plotModel,scaleAnchor))')&&chartCss.includes('border-top:2px dashed #5f96ff')&&chartSource.includes('No authentic daily forecast was published, so no forecast curve is drawn.')&&chartModel(dailyFixture,'BTC').daily.length===7&&chartModel(synthetic,'BTC').daily.length===0&&chartModel(dailyFixture,'BTC').days.slice(2).every(d=>!d.actual)],
 ['VoiceOver: W42-style missing daily forecast is explicitly not presented as a daily forecast curve in both languages',
    a11yUnavailableEn.includes('No original seven-day')&&a11yUnavailableEn.includes('no daily forecast line')&&
    a11yUnavailableDa.includes('Ingen oprindelig syvdagesprognose')&&a11yUnavailableDa.includes('uden daglig prognoselinje')&&
    chartSource.includes('escape(graphDescription(m))')],
 ['VoiceOver: only verified PUBLISHED forecast is described as blue dotted and actual as green solid in DA/EN',
    a11yPublishedEn.includes('Blue dotted line')&&a11yPublishedEn.includes('Green solid line')&&
    a11yPublishedEn.includes('missing days are unconnected')&&
    a11yPublishedDa.includes('Blå stiplet linje')&&a11yPublishedDa.includes('Grøn fuldt optrukken linje')&&
    !a11yPublishedEn.includes('No original seven-day')],
 ['P2 VoiceOver: seven frozen future forecast points without eligible observations never announce an actual line or measured whiskers',
    a11yPublishedNoActualEn.includes('Blue dotted line')&&
    a11yPublishedNoActualEn.includes('No eligible observed daily prices yet')&&
    a11yPublishedNoActualEn.includes('no green actual line or measured high/low whiskers')&&
    !a11yPublishedNoActualEn.includes('Green solid line:')&&
    a11yPublishedNoActualDa.includes('Blå stiplet linje')&&
    a11yPublishedNoActualDa.includes('Endnu ingen gyldige observerede dagspriser')&&
    !a11yPublishedNoActualDa.includes('Grøn fuldt optrukken linje:')],
 ['P2 VoiceOver: range-only history with no observations advertises neither a dotted forecast nor green actual',
    a11yLegacyNoActualEn.includes('No original seven-day')&&
    a11yLegacyNoActualEn.includes('No eligible observed daily prices yet')&&
    !a11yLegacyNoActualEn.includes('Blue dotted line:')&&
    a11yLegacyNoActualDa.includes('Ingen oprindelig syvdagesprognose')&&
    a11yLegacyNoActualDa.includes('Endnu ingen gyldige observerede dagspriser')],
 ['P2: published 7-day PATH renders actual daily envelope AND observed source low/high whiskers',
    publishedRender.paints.attached===1&&
    publishedRender.paints.fills===1&&
    publishedRender.paints.whiskerStrokes===3&& // Two source high/low whiskers + one last-source timeline marker.
    publishedRender.series[0].data.length===7&&
    publishedRender.series.some(v=>v.data.length===2&&v.options.color==='#27c59a')],
 ['P2: legacy 3-window freeze renders authentic interval corridors with no forged daily forecast',
    legacyRender.paints.attached===1&&
    legacyRender.paints.fills===0&&
    legacyRender.paints.intervalRects===3&&
    legacyRender.series[0].data.length===0&&
    legacyRender.paints.whiskerStrokes>=5],
 ['P2: reset control actually measures at least 44 by 44 CSS pixels by its min-width and min-height contracts',
    chartCss.includes('.fw-reset{font-size:18px;min-width:44px;')&&
    chartCss.includes('.fw-assets button,.fw-reset{min-height:44px}')&&
    !chartCss.includes('.fw-reset{font-size:18px;min-width:38px;')],
 ['DA/ENG ships before product rendering with bound public prose only',liveBuilder.includes('./i18n.js')&&build.includes('presentation_translations:publicTranslations(pkg)')&&build.includes('allowed.has(x.en)')&&build.includes('digits(x.en)===digits(x.da)')],
 ['public tab links restore PATH or PROOF without creating another forecast',product.includes("const initialView=location.hash.slice(1)")&&product.includes("['path','proof'].includes(initialView)")&&product.includes("history.replaceState(null,'','#'+b.dataset.tab)")],
 ['public near-term no-observation status has a plain-language explanation',premium.includes("s === 'UNCHANGED NO NEW OBSERVATION'")&&premium.includes("return 'NO NEW READING'")&&premium.includes('Current action unchanged · awaiting a fresh near-term reading.')],
 ['PATH interval-only history cannot impersonate a frozen dotted forecast; controls are thumb-sized',
    chartSource.includes("m.daily.length?'forecast':'interval'")&&
    chartCss.includes('.fw-legend .interval{height:9px;')&&
    chartCss.includes('.fw-assets button,.fw-reset{min-height:44px}')&&
    missingForecastPlan.forecast.length===0&&positivePlan.forecast.length===7],
 ['Approved B chart legend matches dominant green actual and dashed blue forecast',chartSource.includes("BLUE='#5f96ff',GREEN='#27c59a'")&&chartCss.includes('.fw-legend .forecast{height:0;border-top:2px dashed #5f96ff')&&chartCss.includes('.fw-legend .actual{background:#27c59a}')],
 ['arrival windows and rotation facts remain readable on mobile',css.includes('.alt-transition small{font-size:12px')&&css.includes('.rotation-readout-v3 p{font-size:13px')],

 ['public Compass translation preserves historical week and future watch identity',weekIdentityText==='week 40 BTC gained 2.44%. Possible week 41 retest.'&&translateInvestor('W40 BTC gained 2.44%. Possible W41 retest.')===weekIdentityText&&!weekIdentityText.includes('This week')],
 ['weekly graph binds public issue and week and omits unavailable sources',graph({})===''&&graph({...synthetic,public_series:{current_public_projection:{public_issue_number:10,forecast_week:'2026-W41'}}})===''],
 ['weekly chart preserves freeze and plots only complete daily coverage',JSON.stringify(synthetic)===frozenBefore&&['BTC','ETH'].reduce((n,a)=>n+chartModel(synthetic,a).days.filter(d=>d.actual).length,0)===4&&chartModel(gap,'BTC').days.every(d=>!d.actual)],
 ['legacy freezes never fabricate a daily expected-close line',chartModel(synthetic,'BTC').daily.length===0&&chartModel(dailyFixture,'BTC').daily.length===7&&chartSource.includes('No authentic daily forecast was published, so no forecast curve is drawn.')],
 ['weekly graph identifies source cutoff and leaves future observations empty',chartModel(synthetic,'BTC').days.slice(2).every(d=>!d.actual)&&chartModel({...synthetic,public_live_precision:{...synthetic.public_live_precision,daily_observations:null,live_as_of_utc:'2020-01-01T00:00:00Z'}},'BTC').stale&&chartSource.includes('STALE SNAPSHOT')],
 ['pullback card separates ordinary unconfirmed dip from sell and re-entry',riskHtml.includes('Ordinary dip watch')&&riskHtml.includes('DEVELOPING · UNCONFIRMED')&&riskHtml.includes('NOT ESTABLISHED')&&riskHtml.includes('Not quantified')],
 ['pullback card fails unavailable and stale sources closed',risk({},'UNAVAILABLE').includes('Risk assessment unavailable')&&limitedRisk.includes('Risk assessment unavailable')&&!limitedRisk.includes('Conditional watch only')&&!expiredRisk.includes('ACTION NOW · COMPASS')&&!expiredRisk.includes('<strong>WAIT</strong>')&&expiredRisk.includes('LAST VERIFIED COMPASS ACTION · NOT CURRENT')],
 ['PATH removes duplicate overview and standalone tactical action',!extract(product,'renderPath','showProof').includes('pathOverview(')&&!extract(product,'renderPath','showProof').includes('pathActionLens(')&&product.includes('CYCLE CONCLUSION')],
 ['daily chart and investor disclosure ship through existing assets',product.includes('+weeklyJourney(data)')&&chartCss.includes('.fw-days')&&liveBuilder.includes('frozen-week-chart.js')&&premium.includes('+ pullbackCard(officialView,readingState)')&&premiumCss.includes('.premium-pullback')],
 ['public product browser script parses before release',productSyntaxOk],
 ['fallback action-first hero',html.includes('WHAT SHOULD I DO NOW?')],
 ['weekly authority firewall',html.includes('never rewrite the forecast')&&liveBuilder.includes('NON_AUTHORITATIVE_OBSERVATION_ONLY')],
 ['NOW/PATH/PROOF product tabs',['data-tab="now"','data-tab="path"','data-tab="proof"'].every(t=>product.includes(t))&&!product.includes('data-tab="score"')&&!product.includes('data-tab="how"')],
 ['Market Compass public language',product.includes('MARKET COMPASS')&&!product.includes('HANDLEKOMPAS ·')&&!product.includes('MASTER MONDAY →')],
 ['premium three-horizon Compass is Official-Compass owned',premium.includes('OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1')&&premium.includes('MARKET_WEATHER_SOURCE_OF_TRUTH_v1')&&premium.includes('site_synthesis_allowed')&&['1_3d','5_7d','2_3w'].every(x=>premium.includes("scale: '"+x+"'"))],
 ['premium Bull/Bear fails closed instead of synthesising',premium.includes("row.status === 'OK'")&&premium.includes('bull + bear === 10')&&premium.includes('No Bull/Bear number is reconstructed by the website.')&&!/expected_direction[^\n]{0,120}(bull|bear)\s*=/.test(premium)],
 ['premium conclusion recommendation and explainability',premium.includes('CYCLE NAVIGATOR · CONCLUSION')&&premium.includes('RECOMMENDATION')&&premium.includes('HOW THIS READING IS BUILT')&&premium.includes('PRICE & STRUCTURE')&&premium.includes('PARTICIPATION & ROTATION')&&premium.includes('LIQUIDITY & POSITIONING')&&premium.includes('SENTIMENT & CYCLE')&&premium.includes('Evidence balance, not probability')],
 ['premium owns the single first-visit hero',premiumCss.includes('#productNow.premium-compass-installed>.market-weather,#productNow.premium-compass-installed>.action-hero{display:none!important}')&&premium.includes('NEAR-TERM PRESSURE · 0–12H')&&premium.includes('WEEKLY OUTLOOK · 5–7D')&&premium.includes('RISK WATCH')&&premium.includes('near-term pressure and weekly outlook remain separate signals.')],
 ['front-page action is visibly time-bounded without hardcoding a forecast duration',premium.includes('function recommendationWindow')&&premium.includes('CURRENT ACTION')&&premium.includes('NEXT REVIEW · ')&&premium.includes('This is the reassessment window, not a promise that the action changes.')&&premium.includes('next_meaningful_change_eta')&&premium.includes('NEXT_12H')&&premiumCss.includes('.premium-action-window')],
 ['front page exposes hourly monitor freshness without stealing Market Compass authority',premium.includes('function hourlyMonitor')&&premium.includes('HOURLY MONITOR')&&premium.includes('Current action comes from the verified Market Compass.')&&premium.includes("live?.contract !== 'CYCLE_NAVIGATOR_PUBLIC_LIVE_OBSERVATION_v2'")&&premiumCss.includes('.premium-live-monitor')],
 ['NOW triad separates short-horizon pressure weekly outlook and risk timing',premium.includes('function decisionMeta')&&premium.includes('weeklyEta')&&premium.includes('riskEta')&&premium.includes('Current-state BTC/ETH direction proxy; not an independently validated 12H forecast.')&&premium.includes('No current validated 12H forecast.')&&premium.includes('current weekly view')],
 ['NOW triad opens a bounded investor and swing-trader drill-down',premium.includes('function decisionDetail')&&premium.includes('FOR AN INVESTOR')&&premium.includes('FOR A SWING TRADER')&&premium.includes('WHAT TO WATCH')&&premium.includes('data-live-detail')&&premium.includes('detail.scrollIntoView')&&premiumCss.includes('.premium-decision-detail')],
 ['three horizons expose a plain-English so-what line',premium.includes('function soWhat')&&premium.includes('SO WHAT?')&&premium.includes('do not chase high-beta')&&premiumCss.includes('.premium-so-what')],
 ['seven-rung risk curve reaches governed MEMES without proxy synthesis',premium.includes("['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES']")&&premium.includes('MEME RISK')&&premium.includes("String(row.segment).toUpperCase() === 'MEMES'")&&!premium.includes("MICROCAPS' ? 'MEMES")&&premiumCss.includes('.premium-rung-grid')],
 ['premium layer ships in final Pages bundle',liveBuilder.includes('market-compass-premium.js')&&liveBuilder.includes('market-compass-premium.css')&&premiumCss.includes('.premium-horizon-grid')&&premiumCss.includes('@media(max-width:520px)')],
 ['premium public copy filters internal framework vocabulary',premium.includes('const publicCompassText')&&premium.includes("replace(/\\bgoverned\\b/gi, 'verified')")&&premium.includes('AWAITING VERIFIED READ')&&premium.includes('RISK ROTATION · ')&&premium.includes('Published by the Market Compass.')&&!premium.includes('Official Compass remains the action owner.')&&!premium.includes('NEXT GOVERNED REVIEW · ')],
 ['premium public evidence drivers pass through the language filter',premium.includes('return rows.map((x) => publicCompassText(x));')&&premium.includes('30-day altcoin participation reading')&&premium.includes('Recent settled ETF flows favoured Bitcoin over Ethereum')&&premium.includes('Meme risk needs its own confirmed signal.')&&premium.includes('publicCompassText(clean(meme.reason)')],
 ['public fallbacks contain no internal governance jargon',premium.includes('Previously verified Compass · not current.')&&premium.includes('Official Compass unavailable · no current reading.')&&!premium.includes('Fresh market evidence is still loading.')&&premium.includes("replace(/\\bframework\\b/gi, 'research process')")&&!premium.includes('The framework is waiting for fresh evidence.')&&compassV5.includes('No supported horizon yet')&&compassV5.includes('Fresh verified evidence required')&&compassV5.includes('The current Compass stays in place until the new reading is confirmed.')&&!compassV5.includes('Awaiting governed horizon')&&!compassV5.includes('stays authoritative')&&!compassV5.includes('owner evidence')],
 ['single-action hero',product.includes("HOLD:'HOLD'")&&!product.includes("HOLD:'HOLD / WAIT'")],
 ['PATH separates macro phases from the single altcoin journey',product.includes('1 · MARKET CYCLE')&&product.includes('2 · THIS WEEK’S ROTATION')&&product.includes('Altcoin journey. Live rotation.')&&product.includes('macro-map')&&product.includes('The market journey.')],
 ['PATH v3 removes the duplicate Compass decision-window rail',!product.includes('DECISION WINDOWS')&&!product.includes('market-horizon-rail')&&!product.includes('function horizonCell')],
 ['PATH headline explains its three distinct scopes',product.includes('The market regime, altcoin rotation and weekly price plan.')],
 ['Market Cycle distinguishes current weekly phase from forward scenarios',product.includes('market_cycle_context?.current_phase')&&product.includes('Forward scenario: ')&&product.includes('Stable cycle phase not confirmed')],
 ['public strategic cycle payload omits private scenario and asset-detail fields',build.includes('next_21_30d:pick(dp.next_21_30d||{},["direction","summary","regime_destination","expected_path","action_posture","confidence"])')&&!build.includes('next_21_30d:pick(dp.next_21_30d||{},["direction","btc_direction"')],
 ['Macro cycle has one ordered thread, an integrated conclusion and a NOW link',product.includes('MAP · NOT A FORECAST')&&product.includes('Bitcoin → Ethereum')&&product.includes('Distribution → protection → new start')&&product.includes('CYCLE CONCLUSION')&&product.includes('data-now-link')&&css.includes('.macro-map')],
 ['Altcoin journey spans BTC through takeoff protection and re-entry',['BTC leadership','Ethereum leadership','Large + mid rotation','Altseason ignition','Micro acceleration','Broad altseason','Mania / euphoria','Distribution','Exit / protection','Cooldown / re-entry'].every(x=>product.includes("title:'"+x+"'"))],
 ['Cycle journey visually separates current checkpoint and next watch',product.includes("data-cycle-role=")&&product.includes("'current-checkpoint'")&&product.includes("'next-watch'")&&css.includes('.cycle-journey-step.current')&&css.includes('.cycle-journey-step.next')],
 ['Incoming ETA appears as a source-backed time distance between altcoin phases',product.includes('TIME DISTANCE')&&product.includes('etaDistance(row.eta)')&&product.includes('currentIndex+1')&&product.includes('alt-transition')],
 ['Five connector dots map ETA distance without progress or probability',pathTiming.etaDistance('1–3 days').dots===5&&pathTiming.etaDistance('1–2 weeks').dots===4&&pathTiming.etaDistance('Next 2–3 weeks, conditional').dots===3&&pathTiming.etaDistance('No supported ETA').dots===0&&product.includes('Array.from({length:5}')&&product.includes('This is not progress or probability.')&&css.includes('.alt-track-dots i.is-lit')],
 ['Takeoff readiness never invents a countdown or unconfirmed percentage',product.includes('No source-backed readiness percentage is published.')&&product.includes("takeoff=statusActive(small.status||small.action)")&&product.includes('100% · Small-cap takeoff confirmed')],
 ['Current cycle checkpoint is derived from existing live owners without upgrading status',product.includes('function cycleRouteState')&&product.includes("rotation.current?.segment==='ETH'")&&product.includes("rotation.current)currentKey='BTC'")&&product.includes("status:eth.status||eth.action||'UNAVAILABLE'")&&!product.includes("status:'CONFIRMED',eta:eth.eta")],
 ['Rotation remains a typed seven-rung BTC to MEMES ladder',product.includes("['BTC','Bitcoin']")&&product.includes("['ETH','Ethereum']")&&product.includes("['LARGE_CAPS','Large']")&&product.includes("['MID_CAPS','Mid']")&&product.includes("['SMALL_CAPS','Small']")&&product.includes("['MICROCAPS','Micro']")&&product.includes("['MEMES','Memes']")&&product.includes('capitalization_ladder')],
 ['Rotation uses one route with current next and unlock readout',product.includes('alt-journey-rail')&&product.includes('CURRENT POSITION')&&product.includes('NEXT GATE')&&product.includes('WHAT UNLOCKS IT')&&!product.includes('rotation-rung-v2')],
 ['Rotation journey cannot imply a fixed daily schedule',product.includes('elapsed time cannot open a gate')&&product.includes('No automatic loop')],
 ['Rotation timing reconciles live Compass with the slower frozen weekly sequence',pathTiming.weeklyBackstoppedEta('1-7d conditional','Next 2–3 weeks, conditional')==='Next 2–3 weeks, conditional'&&pathTiming.weeklyBackstoppedEta('1-7d conditional','No supported ETA')==='NO SUPPORTED ETA'&&product.includes('weeklyBackstoppedEta(sharedEta([large,mid]),monday(2).window)')&&product.includes('weeklyBackstoppedEta(small.eta,monday(3).window)')],
 ['Takeoff is integrated in the existing altcoin journey',product.includes('ALTSEASON WATCH · TAKEOFF')&&product.includes('takeoff-watch')&&!product.includes('function altseasonWatchPanel')],
 ['Altseason default watch target remains source-owned small-cap ignition',product.includes("eyebrow:'NEXT HIGH-BETA PHASE'")&&product.includes("title:'ALTSEASON IGNITION'")&&product.includes("subtitle:'Small caps begin to participate'")&&product.includes("eta:pathEta(ignition.eta)")],
 ['Altseason target can advance through micro broad mania protection and re-entry',product.includes("return{key:'MICRO'")&&product.includes("return{key:'BROAD'")&&product.includes("return{key:'MANIA'")&&product.includes("return{key:'DISTRIBUTION'")&&product.includes("return{key:'EXIT'")&&product.includes("return{key:'REENTRY'")&&product.includes('sell_assessment')&&product.includes('reentry_state')],
 ['PATH never manufactures a clock countdown or market ETA',product.includes('NO SUPPORTED ETA')&&etaSlice.includes('pathEta')&&!etaSlice.includes('Date')&&!etaSlice.includes('Date.now')&&etaSlice.includes('days<=7?5:days<=14?4:days<=21?3:days<=35?2:1')],
 ['Conditional timing is translated into a plain-English watch window',product.includes('function timingWindow')&&product.includes('WATCH WINDOW')&&product.includes('Only if confirmation arrives · not a countdown')&&product.includes("'$1–$2 days'")],
 ['Distribution evidence is distribution-specific and exit remains sell-owner only',product.includes(".find(x=>/distribution/i.test(String(x||'')))")&&product.includes("status:valid?p.distribution_risk:'UNAVAILABLE'")&&product.includes("status:valid?sell.state:'UNAVAILABLE'")&&product.includes('sell_assessment')],
 ['PATH preserves compound re-entry states and unavailable ordering',product.includes('WAIT_FOR_RECLAIM|WAIT_FOR_FLUSH')&&product.includes("replaceAll('_',' ')")&&product.includes("if(/INACTIVE|UNAVAILABLE|UNCLEAR|UNKNOWN|PAUSED|LOCKED/.test(s))return'unknown'")],
 ['Pages proves Compass weekly lineage from exact internal bound source',build.includes('INTERNAL_COMPASS_POINTER_PATH')&&build.includes('CN_COMPASS_WEEKLY_ALIGNMENT_v1')&&build.includes('internalPointer?.compass_id!==projection.compass_id')&&build.includes('machineSha===String(weeklyPointer?.machine_package_sha256||"")')&&build.includes('buildCompassSnapshot(pointer)')],
 ['Compass weekly lineage failure is isolated from NOW availability',build.includes('status:"UNVERIFIED"')&&build.includes('Preserve the independently verified public Compass for NOW')&&build.includes('Only PATH')&&build.includes('weekly_context')],
 ['PATH fails live overlays closed unless public issue and forecast week align',product.includes('function pathWeeklyAlignment')&&product.includes("receipt.status==='ALIGNED'")&&product.includes('currentIssue===receiptIssue')&&product.includes('currentWeek===receiptWeek')&&product.includes('liveCompass=alignment.ok?compass:null')],
 ['PATH exposes a compact public rollover warning only when alignment is not ready',product.includes('function pathAlignmentNotice')&&product.includes('LIVE SIGNALS REFRESHING')&&product.includes('The weekly path stays fixed while live data catches up.')&&css.includes('.path-alignment-warning')],
 ['Broad Altseason live state comes from the Compass lane not weekly prose',product.includes("const broadStatus=!valid?'UNAVAILABLE'")&&product.includes("pathStatus(cycle.state||cycle.action_posture||'UNAVAILABLE')")],
 ['Altcoin source stages remain neutral when live confirmation is unavailable',product.includes("status:valid?(small.status||small.action||'UNAVAILABLE'):'UNAVAILABLE'")&&product.includes("unavailableWhy='Live confirmation is unavailable. The weekly baseline remains visible in the details.'")],
 ['PATH v3 styling is mobile-first and timing-forward',css.includes('.market-cycle-v3')&&css.includes('.cycle-journey-rail')&&css.includes('.cycle-watch-v3')&&css.includes('.rotation-line-v3')&&css.includes('.rotation-readout-v3')&&css.includes('@media(max-width:640px)')],
 ['Mobile cycle and rotation rails remain swipeable and compact',css.includes('.cycle-journey-rail{display:flex')&&css.includes('.rotation-line-v3{display:flex')&&css.includes('scroll-snap-type:x proximity')&&css.includes('.cycle-journey-step{flex-basis:94px;min-width:94px}')&&css.includes('.rotation-node-v3{flex-basis:78px;min-width:78px}')&&css.includes('.rotation-readout-v3 article:last-child{grid-column:1/3}')],
 ['Macro and altcoin explanations stay behind visible disclosures',product.includes('Why this regime?')&&product.includes('Cycle plan and timing')&&product.includes('aria-hidden="true">↓')],
 ['PATH has a dedicated public-language filter for internal machine wording',product.includes('function publicPathText')&&product.includes("replace(/\\bgoverned\\b/gi,'verified')")&&product.includes("replace(/\\blineage\\b/gi,'data alignment')")&&product.includes("replace(/\\bowner\\b/gi,'signal source')")&&product.includes('function publicPathStatus')],
 ['PATH public labels avoid raw internal-facing status copy',product.includes('DATA STATUS')&&product.includes('NO SUPPORTED ETA')&&!product.includes('<span>LIVE OWNER</span>')],
 ['PATH fast-scan guide explains visual semantics and conservative timing',product.includes('function pathLegend')&&product.includes('READ PATH IN 10 SECONDS')&&product.includes('Blue = what is known now · Amber = next watch · Grey = not confirmed')&&product.includes('Time-distance dots')&&product.includes('not progress, probability or a countdown')&&css.includes('.path-read-guide')],
 ['Public PATH status translation remains conservative',product.includes('function publicHorizonState')&&product.includes("s==='UNAVAILABLE'?'NOT READY':s")&&product.includes('function dataStatusLabel')&&product.includes("return'UP TO DATE'")],
 ['Freshness and next update remain visible',product.includes('CURRENT OFFICIAL COMPASS')&&product.includes('LAST VERIFIED COMPASS · NOT CURRENT')&&product.includes('NEXT SCHEDULED CHECK')&&product.includes('ownerMinute=12')&&product.includes('CNOfficialReadingState')],

 ['Pages proves Compass weekly lineage from exact internal bound source',build.includes('INTERNAL_COMPASS_POINTER_PATH')&&build.includes('CN_COMPASS_WEEKLY_ALIGNMENT_v1')&&build.includes('internalPointer?.compass_id!==projection.compass_id')&&build.includes('machineSha===String(weeklyPointer?.machine_package_sha256||"")')&&build.includes('buildCompassSnapshot(pointer)')],
 ['Compass weekly lineage failure is isolated from NOW availability',build.includes('status:"UNVERIFIED"')&&build.includes('Preserve the independently verified public Compass for NOW')&&build.includes('Only PATH')&&build.includes('weekly_context')],
 ['PATH fails live overlays closed unless public issue and forecast week align',product.includes('function pathWeeklyAlignment')&&product.includes("receipt.status==='ALIGNED'")&&product.includes('currentIssue===receiptIssue')&&product.includes('currentWeek===receiptWeek')&&product.includes('liveCompass=alignment.ok?compass:null')],
 ['PATH exposes a compact public rollover warning only when alignment is not ready',product.includes('function pathAlignmentNotice')&&product.includes('LIVE SIGNALS REFRESHING')&&product.includes('The weekly path stays fixed while live data catches up.')&&css.includes('.path-alignment-warning')],
 ['Rotation cannot fall back to weekly prose as a live status',product.includes('function rotationSnapshot')&&product.includes("const status=valid?(live?.status||live?.action||'UNAVAILABLE'):'UNAVAILABLE'")&&product.includes("eta:valid&&live?pathEta(live.eta):'NO SUPPORTED ETA'")&&product.includes("reason:publicPathText(live?.reason||weekly?.status||'No public rotation explanation is available.')")&&!product.includes("status:weekly?.status")],
 ['Broad Altseason live state comes from the Compass lane, not frozen Monday status',product.includes("const broadStatus=!valid?'UNAVAILABLE'")&&product.includes("pathStatus(cycle.state||cycle.action_posture||'UNAVAILABLE')")&&!product.includes("String(cycle.state||'').toUpperCase()==='BROAD_ALTSEASON'?'ACTIVE':pathStatus(monday(4).phase)")],
 ['Altcoin stages preserve weekly windows as detail while unavailable live gates stay neutral',product.includes("status:valid?(small.status||small.action||'UNAVAILABLE'):'UNAVAILABLE'")&&product.includes("monday:monday(3).window")&&product.includes("unavailableWhy='Live confirmation is unavailable. The weekly baseline remains visible in the details.'")],

 ['PATH hero has intentional dark-surface contrast',css.includes('.path-v2-head h2{color:#fff}')&&css.includes('.path-v2-head p{max-width:760px;color:#cbd5e1}')&&css.includes('.path-v2-head small{color:#8dc1ff}')],
 ['Takeoff timing is legible on mobile and remains weekly-conservative',css.includes('.takeoff-watch small')&&css.includes('@media(max-width:640px)')&&product.includes('Weekly baseline · no supported ETA')&&product.includes('faster live Compass window cannot overrule the slower weekly sequence')],
 ['PATH v3 rails make current and next visually distinct on mobile',css.includes('.cycle-journey-step.current')&&css.includes('.cycle-journey-step.next')&&css.includes('.rotation-node-v3.current')&&css.includes('.rotation-node-v3.next')&&css.includes('content:"NOW"')&&css.includes('content:"NEXT"')],
 ['PATH has a dedicated public-language filter for internal machine wording',product.includes('function publicPathText')&&product.includes("replace(/\\bgoverned\\b/gi,'verified')")&&product.includes("replace(/\\blineage\\b/gi,'data alignment')")&&product.includes("replace(/\\bowner\\b/gi,'signal source')")&&product.includes('function publicPathStatus')],
 ['PATH public language translates remaining trader-internal terms',product.includes("replace(/ETH-relative/gi,'Ethereum-vs-Bitcoin')")&&product.includes("replace(/microstructure/gi,'short-term market structure')")&&product.includes('Meme risk is tracked separately. No verified meme-specific signal is available yet')],
 ['PATH public labels avoid raw internal-facing status and owner copy',!product.includes('<span>LIVE OWNER</span>')&&!product.includes('Monday path stays frozen while live Compass lineage catches up.')&&!product.includes('Frozen Monday context remains reference only until the live owner can place the sequence safely.')&&product.includes('DATA STATUS')&&product.includes('NOT AVAILABLE YET')],
 ['PATH fast-scan guide explains visual semantics and conservative timing',product.includes('function pathLegend')&&product.includes('READ PATH IN 10 SECONDS')&&product.includes('Blue = what is known now · Amber = next watch · Grey = not confirmed')&&product.includes('Time-distance dots')&&product.includes('not progress, probability or a countdown')&&css.includes('.path-read-guide')],
 ['PATH public horizon and data labels suppress raw availability codes',product.includes('function publicHorizonState')&&product.includes("s==='UNAVAILABLE'?'NOT READY':s")&&product.includes('function dataStatusLabel')&&product.includes("return'UP TO DATE'")],
 ['freshness and next update',product.includes('CURRENT OFFICIAL COMPASS')&&product.includes('LAST VERIFIED COMPASS · NOT CURRENT')&&product.includes('NEXT SCHEDULED CHECK')&&product.includes('ownerMinute=12')&&product.includes('CNOfficialReadingState')],


 ['scoreboard integrity uses coverage not a cross-era aggregate',h.policy?.cross_era_aggregate===false&&product.includes('completed forecasts with score evidence')&&!product.includes('HISTORICAL WEEKLY AVERAGE')&&!product.includes('mean(scores.map')],
 ['trust strip binds score coverage and prefers current projection identity',product.includes('cn-trust-strip')&&product.includes('Number.isInteger(currentIssue)?currentIssue:coverageOpen')&&product.includes('Forecast locked before outcome')&&product.includes('data-proof-link')],
 ['Since Last CN compares exact governed fields only',build.includes('EXACT_GOVERNED_FIELD_EQUALITY')&&!build.includes('freezeSignals')&&product.includes('SINCE LAST CN')],
 ['NOW refinements survive later Compass root replacements without loops',product.includes("if(!root.querySelector('.cn-now-refinements'))apply()")&&product.includes('nowObserver.observe(root')&&product.includes("if(root.querySelector('.cn-now-refinements'))return true")],
 ['NOW refinements stay compact while analysis moves to PATH',product.includes('wrap.innerHTML=trustStrip(data,history)')&&product.includes('renderPath(s,compass)')&&product.includes('sinceLastBlock(data)+whyThisCallBlock(data)')],
 ['trust-first components ship styled desktop and mobile layouts',['.cn-now-refinements','.cn-trust-strip','.cn-since-last','.cn-why-call','.completed-receipt','.completed-grid'].every(token=>css.includes(token))&&css.includes('@media(max-width:640px)')],
 ['Why This Call consumes governed structured dimensions with migration fallback',build.includes('market_structure_analysis.dimensions')&&build.includes('market_structure_v2.dimensions')&&!build.includes('value.includes(":")')&&product.includes("CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1")&&product.includes('dims.length!==5')],
 ['NOW refinements survive Compass unavailable renders',product.includes("root.querySelector('.action-hero,.fail-card')")&&product.includes('anchor.after(wrap)')],
 ['last completed receipt preserves canonical score precision',product.includes('function preciseScorePct')&&product.includes("value===null||value===undefined||value===''")&&product.includes('preciseScorePct(x.price_range_score)')&&product.includes("toFixed(2)")],
 ['last completed forecast binds to completed scorecard and survives publication lag',build.includes('deriveLatestCompletedForecast')&&build.includes('05_CYCLE_NAVIGATOR/public_scorecards/')&&build.includes('typeof latest?.price_range_score==="number"')&&!build.includes('Number(latest.price_range_score)')&&build.includes('evaluation?.strengths')&&build.includes('evaluation?.misses')&&!build.includes('outcome?.published_path')&&!build.includes('currentIssue!==completedIssue+1')&&product.includes('LAST COMPLETED FORECAST')&&product.includes('data-ledger-link')],
 ['live score fail-closed',product.includes('Waiting for evidence')&&product.includes('No percentage is shown until at least one call is genuinely scoreable.')&&liveWidget.includes("live.provisional_score !== null")],
 ['public live precision uses same final Price Range family and formula',precisionBuilder.includes('CN_PUBLIC_LIVE_PRICE_PRECISION_v1')&&precisionBuilder.includes('70pct_containment_plus_30pct_jaccard')&&precisionBuilder.includes('"final_row_count": 6')&&precision.includes('Same rows from Monday to final score.')],
 ['live precision has explicit hourly freshness fail-closed semantics',precisionBuilder.includes('"freshness_sla_minutes": 90')&&precisionBuilder.includes('"refresh_cadence": "HOURLY_OWNER_CHAIN"')&&precision.includes('PROVISIONAL · STALE')&&precision.includes('waiting for the next complete hourly owner update')],
 ['freeze archive distinguishes migration proof from native site source-of-record',precisionBuilder.includes('MIGRATED_VERIFIED_FREEZE')&&precisionBuilder.includes('SITE_NATIVE_SOURCE_OF_RECORD')&&precision.includes('PUBLIC FREEZE ARCHIVE')&&precision.includes('MIGRATED VERIFIED FREEZE')],
 ['future Day 1–2 scoring can start only after the frozen forecast exists',precisionBuilder.includes('FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1')&&precisionBuilder.includes('scoring_start_for_window')&&precision.includes('scored from')],
 ['full Proof accountability shows freeze live verified lifecycle',precision.includes('Frozen Monday. Scored live. Verified after close.')&&precision.includes('FROZEN PRICE RANGES')&&precision.includes('FROZEN MONDAY PATH')&&precision.includes('VERIFIED')&&precisionCss.includes('.pa-full')&&precisionCss.includes('.pa-pipeline')],
 ['NOW gets native lite accountability without duplicating full ledger',product.includes('function precisionLite(data)')&&product.includes('WEEKLY TRACK RECORD · ')&&product.includes('View full scorecard →')&&product.includes('data-pa-proof-native')&&precisionCss.includes('.pa-lite')],
 ['NOW renderer owns deterministic lite track record',product.includes('CN_PUBLIC_LIVE_PRICE_PRECISION_v1')&&product.includes('${precisionLite(data)}')&&product.includes("document.querySelector('[data-pa-proof-native]')?.addEventListener('click',showProof)")],
 ['precision layer is PROOF-only after native NOW ownership',!precision.includes('WEEKLY TRACK RECORD')&&!precision.includes('publicLiveAccountabilityLite')&&precision.includes('function watchProof()')&&precision.includes("document.getElementById('productProof')")],
 ['precision PROOF root observer is bounded',precision.includes('function watchRoot()')&&precision.includes("rootObserver.observe(document.body,{childList:true,subtree:true})")&&!precision.includes("document.getElementById('productNow')")],
 ['legacy claim-tracking panel yields to Price Range accountability',liveWidget.includes("snapshot?.public_live_precision?.contract === 'CN_PUBLIC_LIVE_PRICE_PRECISION_v1'")&&precision.includes("document.getElementById('livePrecisionObservation')")],
 ['precision lifecycle colors encode temporal state not performance thresholds',precisionCss.includes('.tone-settled')&&precisionCss.includes('.tone-live')&&precisionCss.includes('.tone-degraded')&&!precision.includes('score_to_date >=')&&!precision.includes('score_to_date >')],
 ['public site freeze is valid source-of-record and X is optional distribution',precisionBuilder.includes('"x_distribution_required": False')&&precision.includes('SITE SOURCE OF RECORD')&&precision.includes('X is optional distribution, not required for validity')],
 ['precision assets ship in final Pages bundle',liveBuilder.includes('precision-accountability.js')&&liveBuilder.includes('precision-accountability.css')&&precisionCss.includes('@media(max-width:560px)')],
 ['legacy standalone weekly score is not shipped into premium shell',build.includes('history-scoreboard.json')&&liveBuilder.includes('public-product.js')&&!liveBuilder.includes('weekly-score.js')],
 ['new scoring is price only',weeklyWidget.includes('Price Ranges')&&!weeklyWidget.includes('cal-summary-label">Market / Structure')],
 ['weekly precision stays price-only',build.includes('public_bull_bear_scale')&&weeklyWidget.includes('Price Ranges')&&!weeklyWidget.includes('BULL / BEAR')],
 ['prospective range bridge reaches homepage',app.includes('snapshot?.prospective_range')&&app.includes('website_consume')&&app.includes('prospective continuity baseline')],
 ['all issue weekly rollup',product.includes('publicScores')&&product.includes('mayDerive')&&product.includes('component rollup')],
 ['explicit no-derived-overall respected',product.includes('explicitDerive')&&h.records?.find(r=>r.cn===25)?.allow_derived_overall===false],
 ['public series identity reaches homepage',build.includes('CN_PUBLIC_SERIES_INDEX.json')&&product.includes('current_public_projection?.public_issue_number')],
 ['canonical public score lineage present',Array.isArray(h.records)&&h.records.length>0&&h.records.every(r=>Number.isInteger(Number(r.cn))&&typeof r.provenance==='string'&&r.provenance.length>0)],
 ['issue-level price aggregation',product.includes('Combined\\s+')&&product.includes('(?:BTC|ETH)')],
 ['non-price aggregation',product.includes('parseComponentScores')&&product.includes('intraday_display')&&product.includes('structure_display')],
 ['plain-English translator',product.includes('investorText')&&product.includes('Ethereum strengthens relative to Bitcoin')],
 ['public methodology describes data families',product.includes('PRICE & STRUCTURE')&&product.includes('PARTICIPATION & ROTATION')&&product.includes('LIQUIDITY & POSITIONING')&&product.includes('MACRO & NETWORK CONTEXT')],
 ['public product assets deployed',liveBuilder.includes('public-product.js')&&liveBuilder.includes('public-product.css')&&build.includes('history-scoreboard.json')],
 ['Market Structure is analysis only from cutover',build.includes('public_market_structure_analysis')&&product.includes('MARKET STRUCTURE · ANALYSIS ONLY')&&product.includes('No accuracy score from CN #27 onward')],
 ['legacy Market Structure history preserved',h.records?.find(r=>r.cn===26)?.structure_method==='LEGACY_PRE_V2'&&h.records?.find(r=>r.cn===26)?.structure_display==='Legacy Market/Structure 60'&&h.policy?.market_structure_score_cutover?.historical_rows_preserved===true],
 ['new Market Structure scores disabled',h.policy?.market_structure_score_cutover?.first_analysis_only_public_issue===27&&h.policy?.market_structure_score_cutover?.new_market_structure_scores===false],
 ['raw history remains locked',h.policy?.historical_scores_locked===true&&h.policy?.retroactive_rescoring===false],
 ['history coverage matches records',Number(h.coverage?.completed_issues)===Math.max(...h.records.map(r=>Number(r.cn)))&&Number(h.coverage?.latest_open_issue)===Number(h.coverage?.completed_issues)+1&&Number(h.coverage?.rows_with_published_or_canonical_score_evidence)===h.records.length]
];

// Premium release checks execute against the actual shipped same-origin HTML,
// not a mock redesign. Negative controls must fail before any root promotion.
const vnextRoot=await read('./vnext-live/index.html');
const releasedRoot=releasePremiumShell(vnextRoot);
const preservedLegacy=preserveLegacyShell(html);
const base='https://donh91.github.io/Investering-Framework-Archive-v1/';
const sourceResolved=new URL('../data/latest.json',new URL('./vnext/',base)).href;
let missingTabRejected=false,missingBundleRejected=false;
try{releasePremiumShell(vnextRoot.replace('id="view-results"','id="removed-results"'))}catch{missingTabRejected=true}
try{releasePremiumShell(vnextRoot.replace('src="./app.mjs"','src="./missing.mjs"'))}catch{missingBundleRejected=true}
checks.push(
 ['premium canonical home is a real shell, not redirect',releasedRoot.includes('<base href="./vnext/">')&&releasedRoot.includes('PREMIUM LIVE')&&releasedRoot.includes('id="view-results"')&&!releasedRoot.includes('src="./app.js"')],
 ['premium source path stays original same-origin public data',sourceResolved===base+'data/latest.json'&&releasedRoot.includes('src="./app.mjs"')],
 ['legacy rollback shell points to root assets',preservedLegacy.includes('<base href="../">')&&preservedLegacy.includes('src="./app.js"')&&preservedLegacy.includes('href="./legacy/#now"')&&preservedLegacy.includes('href="./legacy/#top"')],
 ['premium links to real rollback and no preview copy',releasedRoot.includes('href="../legacy/"')&&releasedRoot.includes('href="../#content"')&&!releasedRoot.includes('PREMIUM PREVIEW')&&!releasedRoot.includes('data-t="previewOnly"')],
 ['premium canonical metadata is not mislabelled preview',releasedRoot.includes('<title>Cycle Navigator · Premium</title>')&&releasedRoot.includes('current-source premium market cycle, compass and verified results')&&!releasedRoot.includes('not the canonical production home')],
 ['staged /vnext/ preview metadata remains separately honest',vnextRoot.includes('<title>Cycle Navigator · Premium Preview</title>')],
 ['cutover never changes production data ownership',build.includes('releasePremiumShell(premiumShell)')&&build.includes('preserveLegacyShell(index)')&&build.includes('resolve(dataDir,"latest.json")')],
 ['legacy-only client injection cannot corrupt premium root',liveBuilder.includes('indexPath=resolve(distDir,"legacy/index.html")')],
 ['premium fails closed for missing primary tab',missingTabRejected],
 ['premium fails closed for missing app bundle',missingBundleRejected]
);
let failed=0;for(const [name,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${name}`);if(!ok)failed++;}
if(failed)process.exit(1);console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator public product release checks`);

