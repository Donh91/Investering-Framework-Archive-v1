/* D0-D6 source-aware PATH design regression. Never changes live source. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {pathModel,pathRotationDisplay,pathSourceReadback} from './premium-experience.mjs';

const page=readFileSync(fileURLToPath(new URL('./index.html',import.meta.url)),'utf8');
const css=readFileSync(fileURLToPath(new URL('./premium-experience.css',import.meta.url)),'utf8');
const parts=page.split(' <section id="view-path"');
assert.equal(parts.length,2,'exactly one original PATH panel');
const region=parts[1].split(' <section id="view-results"')[0];
const phaseKeys=['BTC','ETH','LARGE_MID','ALT_IGNITION','MICRO','BROAD','MANIA','DISTRIBUTION','PROTECTION','REENTRY'];
const tierKeys=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
const base={
 weekly:{forecast_week:'2026-W45',public_issue_number:32},
 compass:{state:'FRESH',permit_path_live_gates:true,compass_id:'CMP-TEST-2026W45'},
 path:{state:'SOURCE_BOUND',source_week:'2026-W45',source_issue:32,
  source_identity:'CMP-TEST-2026W45',
  current_checkpoint:{key:'BTC',label:'BTC leadership',status:'FROZEN_WEEK_REFERENCE'},
  next_checkpoint:{key:'ETH',label:'Ethereum leadership',status:'UNCONFIRMED'},
  next_gate:'ETH/BTC confirmation pending',
  full_phases:phaseKeys.map((key,index)=>({key,label:key,index,status:'REFERENCE_ONLY'})),
  altseason:{status:'WATCH_ONLY',target:'Altseason ignition'},
  rotation:tierKeys.map(key=>({key,action:key==='MICROCAPS'?'HOLD':key==='MEMES'?'UNAVAILABLE':'WAIT',eta:null}))
 }
};
const latest={public_live_precision:{
 contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
 forecast_week:'2026-W45',public_issue_number:32,live_as_of_utc:'2026-11-05T07:00:00Z',
 price_quote_labels:{contract:'CN_PUBLIC_PRICE_QUOTE_LABELS_v1',
  actual_native_spot:{BTC:'USDT',ETH:'USDT'},conversion_applied:false},
 hourly_price_path:{contract:'CN_PUBLIC_HOURLY_PRICE_PATH_v1',source:'HOURLY_SPOT_PASS_ONLY',
  semantics:'OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST',
  forecast_week:'2026-W45',public_issue_number:32,observed_through_utc:'2026-11-05T07:00:00Z',
  BTC:[{observed_at_utc:'2026-11-05T07:00:00Z',close:80649.36}],
  ETH:[{observed_at_utc:'2026-11-05T07:00:00Z',close:2430}]
 }
}};
const clone=o=>structuredClone(o);

assert.equal(pathModel(base,'da').eligible,true);
assert.equal(pathModel(base,'da').phases.length,10);
assert.deepEqual(pathModel(base,'da').phases.filter(x=>x.kind==='reference').map(x=>x.key),['BTC']);
assert.deepEqual(pathModel(base,'da').phases.filter(x=>x.kind==='next').map(x=>x.key),['ETH']);
assert.equal(pathRotationDisplay(pathModel(base,'da'),'da').length,7);
assert.deepEqual(pathRotationDisplay(pathModel(base,'en'),'en').map(x=>x.key),tierKeys);
assert.equal(pathRotationDisplay(pathModel(base,'da'),'da')[6].source,false);
assert.match(pathRotationDisplay(pathModel(base,'da'),'da')[6].action,/Afventer kilde/);
assert.equal(pathRotationDisplay(pathModel(base,'da'),'da')[5].action,'HOLD');
assert.notEqual(pathRotationDisplay(pathModel(base,'da'),'da')[5].action,
 pathRotationDisplay(pathModel(base,'da'),'da')[6].action);

const good=pathSourceReadback(base,latest,'da',Date.parse('2026-11-05T08:00:00Z'));
assert.equal(good.eligible,true);
assert.equal(good.weekly,'CN #32 · 2026-W45');
assert.equal(good.quoteVerified,true);
assert.match(good.observed,/07:|08:|09:/);
assert.match(good.observed,/BTC\/USDT/);
const en=pathSourceReadback(base,latest,'en',Date.parse('2026-11-05T08:00:00Z'));
assert.match(en.observed,/Latest documented hourly close/);
assert.match(en.weekly,/2026-W45/);

for(const mutate of [
 x=>{x.path.source_week='2026-W44'},
 x=>{x.path.source_issue=31},
 x=>{x.path.source_identity='FORGED'},
 x=>{x.compass.state='EXPIRED'},
 x=>{x.compass.permit_path_live_gates=false},
 x=>{x.path.full_phases=x.path.full_phases.slice(0,4)},
 x=>{x.path.state='UNAVAILABLE'}
]){
 const v=clone(base);mutate(v);
 const path=pathModel(v,'da');
 assert.equal(path.eligible,false,'stale/wrong weekly state must not earn source-bound stage');
 assert.equal(path.phases.filter(x=>x.kind==='reference'||x.kind==='next').length,0);
 assert.equal(pathSourceReadback(v,latest,'da',Date.parse('2026-11-05T08:00:00Z')).eligible,false);
 assert.equal(pathRotationDisplay(path,'da').filter(x=>x.source).length,0);
 assert.equal(pathRotationDisplay(path,'da').length,7,'missing data retains neutral structural map');
}
for(const mutate of [
 x=>{x.public_live_precision.forecast_week='2026-W44'},
 x=>{x.public_live_precision.public_issue_number=33},
 x=>{x.public_live_precision.hourly_price_path.public_issue_number=31},
 x=>{x.public_live_precision.hourly_price_path.source='OTHER_PROVIDER'},
 x=>{x.public_live_precision.price_quote_labels.actual_native_spot.BTC='USD'},
 x=>{x.public_live_precision.price_quote_labels.actual_native_spot.ETH='USD'},
 x=>{x.public_live_precision.price_quote_labels.conversion_applied=true},
 x=>{x.public_live_precision.hourly_price_path.BTC[0].close=-1},
 x=>{x.public_live_precision.hourly_price_path.BTC[0].observed_at_utc='2026-11-05T06:00:00Z'},
 x=>{x.public_live_precision.hourly_price_path.ETH[0].observed_at_utc='2026-11-05T06:00:00Z'},
 x=>{x.public_live_precision.hourly_price_path.ETH=[]},
 x=>{x.public_live_precision.hourly_price_path.observed_through_utc='2026-11-09T00:00:00Z'}
]){
 const v=clone(latest);mutate(v);
 const status=pathSourceReadback(base,v,'da',Date.parse('2026-11-05T08:00:00Z'));
 assert.equal(status.quoteVerified,false,'unverified/wrong-hour source must not produce a precise clock');
 assert.match(status.observed,/Intet verificeret/);
}
const future=pathSourceReadback(base,latest,'da',Date.parse('2026-11-04T07:00:00Z'));
assert.equal(future.quoteVerified,false);

assert.equal((region.match(/id="premium-path-rail"/g)||[]).length,1);
assert.equal((region.match(/id="premium-rotation"/g)||[]).length,1);
assert.equal((region.match(/id="premium-path-alt"/g)||[]).length,1);
assert.equal((region.match(/id="path-source-disclosure"/g)||[]).length,1);
assert.ok(region.indexOf('class="path-alt-milestone"')<
 region.indexOf('</section>\n  <section class="section path-rotation-section"'),
 'Altseason Watch belongs WITHIN market cycle before separate rotation');
assert.ok(region.includes('class="path-legend"'),'source status legend missing');
assert.ok(region.includes('class="path-source-disclosure"')&&
 region.includes('<details class="path-source-disclosure"'),
 'Public method disclosure must default closed');
assert.equal((region.match(/class="path-source-links"/g)||[]).length,1);
assert.equal((region.match(/target="_blank" rel="noopener noreferrer"/g)||[]).length,3);
assert.doesNotMatch(region,/https:\/\/github\.com\/Donh91\/secrets|Investering-Framework-Vault/i);
for(const id of ['premium-path-source-summary','premium-path-observed',
 'premium-path-rail','premium-rotation','premium-path-alt','premium-path-now'])
 assert.ok(region.includes('id="'+id+'"'),'source/readback anchor lost: '+id);
assert.ok(css.includes('/* PATH · Quiet Editorial v1'));
const rootCss=readFileSync(fileURLToPath(new URL('../premium-v2/premium-overhaul.css',import.meta.url)),'utf8');
const sourceBlock=css.slice(css.indexOf('/* PATH · Quiet Editorial v1'));
assert.ok(rootCss.endsWith(sourceBlock.replaceAll('#view-path','.premium-next #official-path-view')),
 'Canonical PATH and composed-root design system diverged');
const composedRoot=readFileSync(fileURLToPath(new URL('../premium-v2/unified-root.mjs',import.meta.url)),'utf8');
assert.match(composedRoot,/id="official-path-view" class="cn-path-source path-editorial"/);
assert.match(composedRoot,/cn-alt-milestone" hidden style="display:none"/);
const scoped=css.slice(css.indexOf('/* PATH · Quiet Editorial v1'));
assert.ok(scoped.includes('@media(max-width:1040px)')&&
 scoped.includes('@media(max-width:680px)')&&
 scoped.includes('@media(max-width:365px)'));
assert.ok(scoped.includes(':focus-visible')&&scoped.includes('prefers-reduced-motion'));
assert.doesNotMatch(scoped,/#official-path-chart|\.frozen-week-chart|\.balance-dial/);
assert.ok(scoped.includes('#view-path .path-node[data-kind=reference]'));
assert.ok(scoped.includes('#view-path .rotation-tier[data-source=unavailable]'));
console.log('PASS PATH D0-D6 source-gated editorial hierarchy, public-only disclosure, 7 tiers, invalid source and responsive style controls');
