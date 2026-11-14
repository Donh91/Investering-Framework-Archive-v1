import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {liveViewModel,liveChart,liveChartSvg,formatPct,formatInt,LIVE_CONTRACT} from './kompas-live.mjs';
import {buildUnifiedRootHtml} from './unified-root.mjs';

const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const H=36e5;
const NOW=Date.parse('2026-11-13T18:00:00Z');
const iso=t=>new Date(t).toISOString().replace('.000Z','Z');

// Synthetic KOMPAS_LIVE_PATH_v1 document. The numbers are arbitrary but consistent: this module
// must only render them, so no value here is recomputed or checked against a formula.
function asset(p0,{down=true}={}){
 const points=[];
 for(let i=96;i>=0;i--)points.push([iso(NOW-i*H),Math.round((p0*(1+i*0.0009))*100)/100]);
 const ends=[...Array(8)].map((_,k)=>Date.parse('2026-11-14T00:00:00Z')+k*864e5);
 const days=ends.map((e,k)=>{const centre=p0*(down?1-0.01*(k+1):1),w=0.01*(k+1);
  return {index:k,start_utc:iso(k?e-864e5:NOW),end_utc:iso(e),h:(e-NOW)/H,weekday:['SAT','SUN','MON','TUE','WED','THU','FRI','SAT'][k],
   centre,lo:centre*(1-w),hi:centre*(1+w),log_shift:0}});
 const head=(end,day,pct)=>down?
  {direction:'DOWN',reason:null,end_utc:end,end_weekday:day,target:p0*(1+pct/100),target_display:p0>=1e4?68100:1920,pct,strength:'moderat',
   balance:{horizon:'1_3d',bull:3,bear:7},tilting_views:['1_3d'],official_direction:{'1_3d':'DOWN','5_7d':'MIXED'}}:
  {direction:'NONE',reason:'BALANCED',end_utc:end,end_weekday:day,target:p0,target_display:68900,pct:0,strength:null,
   balance:{horizon:'1_3d',bull:5,bear:5},tilting_views:[],official_direction:{'1_3d':'MIXED','5_7d':null}};
 const ev=(kind,t,price,deviation,since,da,en,extra={})=>({id:kind+'-'+t,kind,t_utc:t,price,deviation,since_pct:since,
  text:{da,en},author:'AUTOMATIC',text_source:'CODE_TEMPLATE_v1',ai_text:null,...extra});
 return {status:'OK',reason:null,quote:'USDT',as_of_utc:iso(NOW),p0,sigma_hourly:0.0042,daily_move_pct:2.0865,daily_move_level:'HIGH',
  daily_move_usdt_display:1440,chips:{change_24h_pct:-4.1203,change_week_pct:-7.892},drift_per_day:{g13:-0.004,g57:0},
  points,days,
  // B's model probability lives only here, under its own authority; the card must never render it.
  challenger_b:{model:'Challenger B',status:'TRIAL',authority:{research_only:true,compass_probability_claim:false,official_compass:false,rendered_on_site:false},
   applied:true,p_up_by_day:days.map(d=>({end_utc:d.end_utc,p_up:0.3141}))},
  headline:{'1':head('2026-11-15T00:00:00Z','SAT',-0.62),'3':head('2026-11-17T00:00:00Z','MON',-1.23),'7':head('2026-11-21T00:00:00Z','FRI',-1.31)},
  frozen_zone:{low:p0*1.034,high:p0*1.116,week:'2026-W46'},
  events:[
   ev('WEEK_START','2026-11-09T00:00:00Z',p0*1.085,{state:'INSIDE',pct:0},-7.892,'Ugen startede ved 74.851, inde i ugens frosne prognose (71.289–76.968).','The week opened at 74,851, inside this week’s frozen forecast (71,289–76,968).'),
   ev('NOW',iso(NOW),p0,{state:'BELOW',pct:-3.29},null,'Nu-tekst 3','Now text 3',{text_by_horizon:{'1':{da:'Nu-tekst 1',en:'Now text 1'},'3':{da:'Nu-tekst 3',en:'Now text 3'},'7':{da:'Nu-tekst 7',en:'Now text 7'}}}),
   ev('ZONE_BREAK','2026-11-11T10:00:00Z',p0*1.02,{state:'BELOW',pct:-1.4},-1.96,'Kursen lukkede under ugens frosne prognose-bund (71.289) 3 timer i træk.','Price closed below this week’s frozen forecast floor (71,289) for 3 hours in a row.'),
   ev('KOMPAS_1_3D_CHANGE','2026-11-09T12:18:11Z',p0*1.079,{state:'INSIDE',pct:0},-7.298,'Kompas 1–3 d skiftede fra Blandet til Faldende.','Compass 1–3 d changed from Mixed to Falling.')
  ]};
}
function fixture({down=true,flat=false,status='OK',reasons=[],eth=null}={}){
 return {contract:'KOMPAS_LIVE_PATH_v1',generated_at_utc:iso(NOW),official_source_valid_until_utc:iso(NOW+4*H),status,reasons,
  authority:{research_only:true,official_forecast:false,compass_probability_claim:false,trading:false,promotion:false,site_synthesis:false},
  display_rules:{freshness_sla_minutes:90,client_stale_after_minutes:180},
  week:{iso_week:'2026-W46',start_utc:'2026-11-09T00:00:00Z',end_utc:'2026-11-16T00:00:00Z'},
  horizon_end_utc:{'1':'2026-11-15T00:00:00Z','3':'2026-11-17T00:00:00Z','7':'2026-11-21T00:00:00Z'},
  models:{line:{applied:!flat,line:flat?'FLAT':'TILTED',reason:flat?'PREREG_ABSENT':null},frames:{z:0.966374,z_source:'REGISTERED_SEED'}},
  assets:{BTC:asset(68944.17,{down}),ETH:eth||asset(1938.29,{down})}};
}
function flatFixture(){
 const doc=fixture({flat:true});
 for(const a of Object.values(doc.assets))for(const k of ['1','3','7'])
  a.headline[k]={...a.headline[k],direction:'NONE',reason:'PREREG_ABSENT',strength:null,tilting_views:[]};
 return doc;
}
const allText=m=>JSON.stringify(m)+liveChartSvg(m,{width:360});

test('down headline in Danish and English attributes the direction word to Kompas and the tilt to Challenger B',()=>{
 const da=liveViewModel(fixture(),{lang:'da',hz:3,nowMs:NOW});
 assert.equal(da.state,'OK');
 assert.deepEqual([da.headline.arrow,da.headline.tone,da.headline.direction],['↘','down','DOWN']);
 assert.equal(da.headline.title,'Ned mod ca. 68.100');
 assert.equal(da.headline.sub,'−1,2 % ved mandagens lukning · moderat hældning');
 assert.equal(da.headline.source,"live, Challenger B's formel (forsøg) · Kompas 1–3 d: Faldende");
 const en=liveViewModel(fixture(),{lang:'en',hz:3,nowMs:NOW});
 assert.equal(en.headline.title,'Down toward approx. 68,100');
 assert.equal(en.headline.sub,'−1.2% by Monday\'s close · moderate tilt');
 assert.equal(en.headline.source,"live, Challenger B's formula (trial) · Compass 1–3 d: Falling");
 assert.equal(liveViewModel(fixture(),{lang:'da',hz:1,nowMs:NOW}).headline.sub,'−0,6 % ved lørdagens lukning · moderat hældning');
 assert.equal(liveViewModel(fixture(),{lang:'da',hz:7,nowMs:NOW}).headline.sub,'−1,3 % ved fredagens lukning · moderat hældning');
});

test('flat line without a registered Challenger B and a balanced Kompas read as no clear direction',()=>{
 const flat=liveViewModel(flatFixture(),{lang:'da',nowMs:NOW});
 assert.deepEqual([flat.headline.arrow,flat.headline.title],['→','Ingen klar retning']);
 assert.equal(flat.headline.sub,'Challenger B er ikke registreret endnu, så linjen er flad.');
 assert.match(flat.headline.source,/^Forventet luk uden hældning/);
 assert.equal(flat.legend.find(x=>x.key==='line').label,'Forventet luk · uden hældning');
 assert.match(flat.footer,/Challenger B \(forsøg\) er endnu ikke registreret/);
 const en=liveViewModel(flatFixture(),{lang:'en',nowMs:NOW});
 assert.deepEqual([en.headline.title,en.headline.sub],['No clear direction','Challenger B is not registered yet, so the line is flat.']);
 const balanced=liveViewModel(fixture({down:false}),{lang:'da',nowMs:NOW});
 assert.equal(balanced.headline.sub,'Kompas’ evidens er i balance for perioden.');
 assert.equal(balanced.headline.source,"live, Challenger B's formel (forsøg) · Kompas 1–3 d: Blandet");
});

test('unavailable producer, asset, contract and stale tab are calm states without a chart',()=>{
 const stale=liveViewModel(fixture({status:'UNAVAILABLE',reasons:['HOURLY_STALE']}),{lang:'da',nowMs:NOW});
 assert.equal(stale.state,'UNAVAILABLE');
 assert.equal(stale.unavailable.title,'Kompas live er midlertidigt utilgængelig');
 assert.equal(stale.unavailable.text,'Seneste timekurs er mere end 90 minutter gammel.');
 assert.equal(stale.chart,null);
 assert.equal(liveChartSvg(stale),'');
 assert.deepEqual([stale.feed,stale.chips,stale.headline],[[],[],null]);
 assert.equal(liveViewModel(fixture({status:'UNAVAILABLE',reasons:['HOURLY_STALE']}),{lang:'en',nowMs:NOW}).unavailable.text,
  'The latest hourly price is more than 90 minutes old.');
 const partial=fixture({status:'PARTIAL',eth:{status:'UNAVAILABLE',reason:'SIGMA_WINDOW_GAP',quote:'USDT'}});
 assert.equal(liveViewModel(partial,{asset:'BTC',nowMs:NOW}).state,'OK');
 const eth=liveViewModel(partial,{asset:'ETH',nowMs:NOW});
 assert.equal(eth.state,'UNAVAILABLE');
 assert.match(eth.unavailable.text,/Der mangler timekurser/);
 assert.equal(liveViewModel(fixture(),{nowMs:NOW+181*60e3}).reason,'STALE_IN_BROWSER');
 assert.equal(liveViewModel(fixture(),{nowMs:NOW+179*60e3}).state,'OK');
 for(const [flag,value] of [['official_forecast',true],['compass_probability_claim',true],['trading',true],['research_only',false]]){
  const forged=fixture();forged.authority[flag]=value;
  assert.equal(liveViewModel(forged,{nowMs:NOW}).reason,'SOURCE','authority '+flag);
 }
 assert.equal(liveViewModel({...fixture(),contract:'OTHER'},{nowMs:NOW}).state,'UNAVAILABLE');
 assert.equal(liveViewModel(null,{nowMs:NOW}).state,'UNAVAILABLE');
 assert.equal(liveViewModel(null,{nowMs:NOW,pending:true}).state,'LOADING');
 const broken=fixture();broken.assets.BTC.days[0].lo=broken.assets.BTC.days[0].hi+1;
 assert.equal(liveViewModel(broken,{nowMs:NOW}).state,'UNAVAILABLE');
 assert.match(liveViewModel(fixture({status:'UNAVAILABLE',reasons:['PRODUCER_ERROR:KeyError']}),{nowMs:NOW}).unavailable.text,/fejlede/);
});

test('source deadline independently expires live forecasts even in already-open browser with fresh price',()=>{
 const original=fixture();
 assert.equal(liveViewModel(original,{nowMs:NOW+3*H}).state,'OK');
 const shorter={...original,official_source_valid_until_utc:iso(NOW+H)};
 assert.equal(liveViewModel(shorter,{nowMs:NOW}).state,'OK');
 const atExpiry=liveViewModel(shorter,{nowMs:NOW+H});
 assert.equal(atExpiry.state,'UNAVAILABLE');
 assert.equal(atExpiry.reason,'OFFICIAL_POINTER_SOURCE_EXPIRED');
 assert.equal(atExpiry.chart,null);
 assert.equal(liveChartSvg(atExpiry),'');
 assert.equal(liveViewModel({...original,official_source_valid_until_utc:null},{nowMs:NOW}).reason,
  'OFFICIAL_POINTER_SOURCE_FRESHNESS_INVALID');
});

test('frames per horizon follow the producer horizon ends; one frosted frame per UTC day',()=>{
 for(const [hz,n] of [[1,2],[3,4],[7,8]]){
  const m=liveViewModel(fixture(),{hz,nowMs:NOW});
  assert.equal(m.chart.days.length,n,'hz '+hz);
  const svg=liveChartSvg(m,{width:720});
  assert.equal((svg.match(/class="kl-frame"/g)||[]).length,n,'frames hz '+hz);
  assert.equal((svg.match(/class="kl-line-dot"/g)||[]).length,n,'close dots hz '+hz);
  assert.deepEqual(m.hzButtons.map(b=>b.pressed),[1,3,7].map(x=>x===hz));
 }
 assert.equal(liveViewModel(fixture(),{hz:5,nowMs:NOW}).hz,3);
 assert.equal(liveViewModel(fixture(),{asset:'DOGE',nowMs:NOW}).asset,'BTC');
});

test('comment track is newest first, starts with Nu, follows the horizon and keeps code authorship',()=>{
 const m=liveViewModel(fixture(),{lang:'da',hz:7,nowMs:NOW});
 assert.deepEqual(m.feed.map(x=>x.kind),['NOW','ZONE_BREAK','KOMPAS_1_3D_CHANGE','WEEK_START']);
 assert.deepEqual([m.feed[0].when,m.feed[0].text,m.feed[0].since],['Nu','Nu-tekst 7',null]);
 assert.equal(m.feed[0].deviation.text,'−3,3 % under prognosen');
 assert.equal(m.feed[1].since.text,'Siden: −2,0 %');
 assert.equal(m.feed[3].deviation.text,'inde i prognosen');
 assert.ok(m.feed.every(x=>x.author==='Automatisk'));
 assert.match(m.feed[2].when,/^man\.? 13[.:]18$/);
 assert.equal(m.labels.feedPill,'AUTOMATISK');
 const en=liveViewModel(fixture(),{lang:'en',hz:1,nowMs:NOW});
 assert.deepEqual([en.feed[0].when,en.feed[0].text,en.feed[1].since.text],['Now','Now text 1','Since: −2.0%']);
});

test('trial labels, footer disclaimer and no probability claim on behalf of Kompas',()=>{
 const da=liveViewModel(fixture(),{lang:'da',nowMs:NOW});
 const en=liveViewModel(fixture(),{lang:'en',nowMs:NOW});
 assert.equal(da.legend.find(x=>x.key==='line').label,"live, Challenger B's formel (forsøg)");
 assert.equal(da.legend.find(x=>x.key==='frames').label,"live, beregnet hver time med Challenger A's formel");
 assert.equal(en.legend.find(x=>x.key==='line').label,"live, Challenger B's formula (trial)");
 assert.equal(en.legend.find(x=>x.key==='frames').label,"live, calculated hourly using Challenger A's formula");
 assert.match(da.footer,/ikke en købs- eller salgsanbefaling/);
 assert.match(da.footer,/ikke originale, fastfrosne A\/B-udstedelser/);
 assert.doesNotMatch(da.footer,/Begge modeller scores løbende/);
 assert.match(da.footer,/ikke en officiel prognose/);
 assert.match(en.footer,/not a buy or sell recommendation/);
 for(const m of [da,en,liveViewModel(flatFixture(),{nowMs:NOW}),liveViewModel(fixture({status:'UNAVAILABLE',reasons:['HOURLY_STALE']}),{nowMs:NOW})]){
  const text=allText(m);
  assert.doesNotMatch(text,/Kompas siger|Compass says/i);
  assert.doesNotMatch(text,/(?<!ikke )sandsynlighed/i);
  assert.doesNotMatch(text,/(?<!not a |not )probabilit/i);
  assert.doesNotMatch(text,/p_up|chance|odds|challenger_b|0[.,]3141|31[.,]4/i);
 }
});

test('SVG is an accessible image with a text summary, CSS-class colours and broken gaps',()=>{
 const m=liveViewModel(fixture(),{lang:'da',hz:3,nowMs:NOW});
 const svg=liveChartSvg(m,{width:360});
 assert.match(svg,/^<svg xmlns="http:\/\/www\.w3\.org\/2000\/svg" viewBox="0 0 360 259"/);
 assert.match(svg,/role="img"/);
 assert.match(svg,/aria-labelledby="cn-live-chart-title cn-live-chart-desc"/);
 assert.match(svg,/<title id="cn-live-chart-title">Kompas live · de næste dage · BTC<\/title>/);
 assert.match(svg,/<desc id="cn-live-chart-desc">BTC: faktisk kurs de seneste 4 døgn og Challenger B \(forsøg\) forventet luk for 3 dage\. Kurs nu 68\.944 USDT\./);
 assert.match(svg,/Ugens frosne prognose/);
 assert.match(svg,/class="kl-zone"/);
 assert.match(svg,/>NU</);
 assert.match(svg,/≈ 68\.100/);
 assert.doesNotMatch(svg,/style=|fill="#|stroke="#|<script|Math\.sin/);
 assert.equal((svg.match(/class="kl-actual"/g)||[]).length,1);
 const gap=fixture();gap.assets.BTC.points.splice(40,2);
 assert.equal((liveChartSvg(liveViewModel(gap,{nowMs:NOW}),{width:360}).match(/class="kl-actual"/g)||[]).length,2);
 const narrow=liveChart(m,{width:200});
 assert.equal(narrow.width,300,'phone-safe minimum geometry, scaled by CSS width:100%');
 assert.equal(liveChart({chart:null}),null);
});

test('formatting is presentation only and Danish first',()=>{
 assert.equal(formatPct(-1.234,'da'),'−1,2 %');
 assert.equal(formatPct(0.04,'da'),'0,0 %');
 assert.equal(formatPct(2.05,'en'),'+2.1%');
 assert.equal(formatInt(68944.17,'da'),'68.944');
 assert.equal(formatInt(68944.17,'en'),'68,944');
 const m=liveViewModel(fixture(),{lang:'da',nowMs:NOW});
 assert.deepEqual(m.chips.map(c=>[c.text,c.label,c.tone]),[
  ['−4,1 %','24 t','down'],['−7,9 %','siden mandag','down'],['± 2,1 %','dagsudsving · højt','neutral']]);
 assert.equal(m.price.text,'68.944');
 assert.equal(m.asOf.text,'Live 19.00');
});

test('pure module: no DOM, no fetch, no synthetic sine, no client-side tilt or probability maths',async()=>{
 const src=await read('./kompas-live.mjs');
 assert.doesNotMatch(src,/Math\.sin\s*\(|Math\.exp\s*\(|Math\.sqrt\s*\(|erf\b/);
 assert.doesNotMatch(src,/\bdocument\b|\bwindow\b|innerHTML|fetch\s*\(|localStorage/);
 assert.doesNotMatch(src,/bull\s*-\s*bear|\.bull\s*-|tilt\s*\*/);
 assert.equal(LIVE_CONTRACT,'KOMPAS_LIVE_PATH_v1');
});

test('Kompas root mounts one live card where DOM order equals visual order and fetches the producer JSON',async()=>{
 const [original,pro,runtime,tabs]=await Promise.all([read('./graph-b/source-graph-b.html'),
  read('../vnext-live/index.html'),read('./root-compass-pro.mjs'),read('./premium-tabs.css')]);
 const html=buildUnifiedRootHtml(original,pro);
 assert.equal((html.match(/id="cn-live-forecast"/g)||[]).length,1);
 const live=html.indexOf('id="cn-live-forecast"');
 // rendered after the first fold (decision, risk, horizons, next gate) and before swing, rotation,
 // BTC days and the accordion (premium-tabs.css grid row "live" after "gate"): same order in the DOM
 for(const above of ['id="premium-now-action"','id="pro-next-gate"','id="cn-overview-heading"','id="cn-risk-quick-brief"'])
  assert.ok(html.indexOf(above)<live,'above: '+above);
 for(const below of ['id="swing-rotation-overview"','id="cn-rotation-heading"','id="cn-btc-days"','<details class="cn-explain">','<details class="cn-pro-more">'])
  assert.ok(live<html.indexOf(below),'below: '+below);
 for(const id of ['cn-live-heading','cn-live-asof','cn-live-price','cn-live-chips','cn-live-dir','cn-live-dir-title',
  'cn-live-hz','cn-live-legend','cn-live-chart','cn-live-unavailable','cn-live-feed','cn-live-foot'])
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id);
 assert.match(html,/data-cn-live-hz="3" aria-pressed="true"/);
 assert.match(html,/data-cn-live-asset="BTC" aria-pressed="true"/);
 assert.match(html,/Visningen er ikke en købs- eller salgsanbefaling/);
 assert.match(runtime,/new URL\('\.\.\/\.\.\/data\/kompas-live\.json',import\.meta\.url\)\)\.catch\(\(\)=>null\)/);
 assert.match(runtime,/import \{liveViewModel,liveChart\} from '\.\/kompas-live\.mjs'/);
 assert.match(runtime,/renderLiveForecast\(\)/);
 assert.match(runtime,/createElementNS/);
 assert.doesNotMatch(runtime,/innerHTML/);
 assert.match(tabs,/"gate gate" "live live" "rot rot"/);
 assert.match(tabs,/"gate gate gate" "live live live" "rot rot btc"/);
 assert.match(tabs,/#cn-live-forecast\{grid-area:live/);
});

function luminance(hex){
 const c=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(n=>n<=0.04045?n/12.92:((n+0.055)/1.055)**2.4);
 return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2];
}
const contrast=(a,b)=>{const [l,d]=[luminance(a),luminance(b)].sort((x,y)=>y-x);return (l+0.05)/(d+0.05)};
test('light-only tokens meet WCAG AA, focus is visible and the pulse respects reduced motion',async()=>{
 const css=await read('./kompas-live.css');
 const token=name=>{const m=css.match(new RegExp('--kl-'+name+':(#[0-9a-fA-F]{6})'));assert.ok(m,'token '+name);return m[1]};
 // text on every card surface it is used on: chips/since/segmented controls sit on --kl-grid
 for(const name of ['ink','muted','up','down'])
  for(const surface of ['#ffffff',token('tile'),token('grid')])
   assert.ok(contrast(token(name),surface)>=4.5,name+' on '+surface);
 // text used only on white (target pill, zone label, now pill)
 for(const name of ['accent','actual-strong','zone-text'])assert.ok(contrast(token(name),'#ffffff')>=4.5,name+' on white');
 for(const name of ['actual','zone','accent'])assert.ok(contrast(token(name),'#ffffff')>=3,name+' graphic');
 assert.ok(contrast('#ffffff',token('actual-strong'))>=4.5,'now pill text');
 assert.ok(contrast('#7f8aa0','#ffffff')<4.5,'NEGATIVE_CONTROL: the v7 zone grey is not a text colour');
 assert.match(css,/button:focus-visible\{outline:2px solid var\(--kl-accent\)/);
 assert.match(css,/@media \(prefers-reduced-motion:no-preference\)\{[^}]*kl-pulse/);
 assert.doesNotMatch(css,/prefers-color-scheme|data-theme/);
 assert.match(css,/min-height:40px/);
});
