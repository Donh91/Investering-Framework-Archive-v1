import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildUnifiedRootHtml} from './unified-root.mjs';
import {buildPremiumRootHtml} from './premium-root.mjs';

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
 assert.match(renderer,/MANDAGENS 3 PROGNOSEVINDUER/);
 assert.match(renderer,/Mandagens intraday-prognose/);
 assert.match(renderer,/bands\.map\(b=>/);
 assert.match(renderer,/attr\('forecast','d',''\)/);
 const frozen=JSON.parse(await read('../../weekly/2026/W44/CYCLE_NAVIGATOR_FORECAST_FREEZE.json'));
 for(const key of ['day_1_2','day_3_4','day_5_7'])
  assert.ok(frozen.intraday_map[key].includes('BTC')&&frozen.intraday_map[key].includes('ETH'),key);
 assert.equal(frozen.daily_price_path.BTC.status,'UNAVAILABLE');
 assert.equal(frozen.daily_price_path.ETH.status,'UNAVAILABLE');
});
