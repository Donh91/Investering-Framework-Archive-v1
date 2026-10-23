/**
 * Graph B v2.1 source-first COMPONENT PILOT, not the canonical site app.
 *
 * This is a deliberately small port of AppDeploy B/C Studio's actual SVG
 * geometry/updateGraph architecture. It consumes ONLY published first-party
 * /data/latest.json through the independently tested official-source adapter.
 * The original AppDeploy Math.sin() fixture and demo switch are NOT imported.
 *
 * This file must never be treated as an Official Compass, forecast issuer,
 * independent proof attestation or score engine.
 */
import {readOfficialGraphB,replayObservedUntil} from './official-source-adapter.mjs';
const $=id=>document.getElementById(id);
const SVG='http://www.w3.org/2000/svg',HOUR=3600000,DAY=86400000;
let asset='BTC',language='da',model=null,sliderHour=0,playTimer=null;
const s=(n)=>typeof n==='number'&&Number.isFinite(n)&&n>0;
const t=(da,en)=>language==='da'?da:en;
const utc=ms=>new Date(ms).toLocaleString(language==='da'?'da-DK':'en-GB',{
 timeZone:'UTC',weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'
})+' UTC';
const num=value=>s(value)?new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{
  style:'currency',currency:'USD',maximumFractionDigits:2
 }).format(value):'—';
const set=(id,value)=>{const n=$(id);if(n)n.textContent=String(value)};
const attr=(id,key,value)=>{const n=$(id);if(n)n.setAttribute(key,String(value))};
const movePath=pts=>pts.map((p,i)=>(i?'L':'M')+p.x.toFixed(2)+','+p.y.toFixed(2)).join(' ');
const sourceUrl=new URL('../../data/latest.json',import.meta.url);
const lineageUrl=new URL('../../data/publication-lineage.json',import.meta.url);
function clearPlaying(){
 if(playTimer!==null){clearInterval(playTimer);playTimer=null}
 set('play-text',t('Afspil uge','Play week'));
}
function textLabels(){
 const labels={
  da:{card:'Weekly Outlook · B',desc:'Kursretning, oprindelige intervaller og faktiske observationer.',
    actual:'Faktiske timeslukkepriser · kun kildeverificerede',missing:'Original blå dagsprognose er ikke udstedt',
    forecast:'Original kildeudstedt kurs',observed:'Faktisk kurs',bounds:'Oprindelige low/high',
    title:'Spol gennem ugen',mon:'Mandag',sun:'Søndag'},
  en:{card:'Weekly Outlook · B',desc:'Price direction, original ranges and verified observations.',
    actual:'Observed hourly closes · source verified only',missing:'Original blue daily forecast not issued',
    forecast:'Original issued forecast',observed:'Observed price',bounds:'Original low/high',
    title:'Explore the week',mon:'Monday',sun:'Sunday'}
 }[language];
 set('card-heading',labels.card);
 const e=document.querySelector('.card-desc');if(e)e.textContent=labels.desc;
 const map=[['.instrument-left small',labels.actual],['.swatch-forecast + span',labels.forecast],
 ['.swatch-actual + span',labels.observed],['.swatch-band + span',labels.bounds],
 ['.time-control label',labels.title],['.time-extents span:first-child',labels.mon],
 ['.time-extents span:last-child',labels.sun]];
 for(const [selector,value] of map){const target=document.querySelector(selector);if(target)target.textContent=value}
 document.documentElement.lang=language;
 document.querySelectorAll('[data-lang]').forEach(button=>
  button.setAttribute('aria-pressed',String(button.dataset.lang===language)));
}
function plot(){
 textLabels();
 const card=$('variant-panel');card.dataset.variant='b';
 if(!model||model.source_status!=='SOURCE_BOUNDED'){
  ['range-band','range-upper','range-lower','forecast','actual'].forEach(id=>attr(id,'d',''));
  $('price-axis')?.replaceChildren();$('grid')?.replaceChildren();
  set('observed-value','—');set('time-label','—');set('source-state',t('Ingen verificeret kilde','No verified source'));
  $('endpoint')?.setAttribute('visibility','hidden');$('endpoint-halo')?.setAttribute('visibility','hidden');
  set('feed-status',t('Afventer gyldige officielle CN-data. Ingen prognose eller pris vises.','No valid official CN source. No forecast or price shown.'));
  return;
 }
 const bands=model.bands||[],hourly=model.hourly_observations||[];
 const start=Date.parse(bands[0].window_start_utc),end=Date.parse(bands.at(-1).window_end_utc);
 if(!Number.isFinite(start)||!Number.isFinite(end)||end-start!==7*DAY){model=null;plot();return}
 const availableMax=hourly.length?Math.max(0,Math.min(167,Math.floor((hourly.at(-1).time*1000-start)/HOUR))):0;
 sliderHour=Math.min(Math.max(0,sliderHour),availableMax);
 const hourInput=$('hour-slider');hourInput.max=String(availableMax);hourInput.value=String(sliderHour);
 hourInput.disabled=!hourly.length;
 const cursor=Math.min(end,start+sliderHour*HOUR);
 const observedRuns=replayObservedUntil(model,new Date(cursor).toISOString());
 const visible=observedRuns.flat();
 const values=[...bands.flatMap(b=>[b.forecast_low,b.forecast_high]),
  ...model.forecast.flatMap(p=>[p.expected_close,p.low,p.high]),...hourly.map(p=>p.value)].filter(s);
 if(values.length===0){model=null;plot();return}
 const min=Math.min(...values),max=Math.max(...values),padding=(max-min||1)*.07;
 const lo=min-padding,hi=max+padding;
 const x=ms=>14+Math.max(0,Math.min(1,(ms-start)/(end-start)))*972;
 const y=v=>28+((hi-v)/(hi-lo))*344;
 const xy=p=>({x:x(p.time*1000),y:y(p.value)});
 const area=arr=>movePath(arr.map(p=>({x:x(p.time*1000),y:y(p.high)})))+' '+
   movePath(arr.slice().reverse().map(p=>({x:x(p.time*1000),y:y(p.low)}))).replace(/^M/,'L')+' Z';
 if(model.forecast_status==='SOURCE_ISSUED'){
  const f=model.forecast.map(p=>({time:p.time,value:p.expected_close}));
  attr('forecast','d',movePath(f.map(xy)));
  attr('range-band','d',area(model.forecast));
  attr('range-upper','d',movePath(model.forecast.map(p=>({x:x(p.time*1000),y:y(p.high)}))));
  attr('range-lower','d',movePath(model.forecast.map(p=>({x:x(p.time*1000),y:y(p.low)}))));
 }else{
  attr('forecast','d','');
  // Three independently issued aggregate range windows: NEVER fabricate
  // a connecting expected-close price path across missing original days.
  attr('range-band','d',bands.map(b=>{
   const left=x(Date.parse(b.window_start_utc)),right=x(Date.parse(b.window_end_utc));
   const up=y(b.forecast_high),down=y(b.forecast_low);
   return 'M'+left+','+up+' L'+right+','+up+' L'+right+','+down+
    ' L'+left+','+down+' Z';
  }).join(' '));
  attr('range-upper','d','');attr('range-lower','d','');
 }
 attr('actual','d',observedRuns.map(run=>movePath(run.map(xy))).join(' '));
 const last=visible.at(-1);
 for(const id of ['endpoint','endpoint-halo'])$(id)?.setAttribute('visibility',last?'visible':'hidden');
 if(last){attr('endpoint','cx',x(last.time*1000));attr('endpoint','cy',y(last.value));
  attr('endpoint-halo','cx',x(last.time*1000));attr('endpoint-halo','cy',y(last.value))}
 attr('playhead','x1',x(cursor));attr('playhead','x2',x(cursor));
 const grid=$('grid');grid.replaceChildren();
 const addLine=(x1,y1,x2,y2,dashed)=>{
  const line=document.createElementNS(SVG,'line');
  [['x1',x1],['y1',y1],['x2',x2],['y2',y2],['stroke','var(--grid)'],
   ['stroke-opacity','.16'],['stroke-width','1']].forEach(([key,val])=>line.setAttribute(key,String(val)));
  if(dashed)line.setAttribute('stroke-dasharray','3 7');
  grid.append(line);
 };
 for(let i=0;i<5;i++){let py=28+(344/4)*i;addLine(14,py,986,py,false)}
 for(let i=1;i<7;i++)addLine(x(start+i*DAY),28,x(start+i*DAY),372,true);
 const axis=$('price-axis');axis.replaceChildren();
 for(let i=0;i<5;i++){const span=document.createElement('span');
  span.textContent=new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0}).format(hi-(hi-lo)*i/4);
  span.style.top=(100*(28+344*i/4)/405)+'%';axis.append(span)}
 set('pair',asset+' / USD');set('observed-value',num(last?.value));
 set('time-label',last?utc(last.time*1000):'—');
 set('timeline-label',utc(cursor));
 const st=model.forecast_status==='SOURCE_ISSUED'?
  t('BLÅ KURVE FRA ORIGINAL KILDE','BLUE CURVE FROM ORIGINAL SOURCE'):
  t('INGEN ORIGINAL DAGLIG PROGNOSE · KUN KILDEINTERVALLER','NO ORIGINAL DAILY FORECAST · SOURCE RANGES ONLY');
 set('source-state',st);
 const stale=model.live_freshness==='STALE';
 set('feed-status',(stale?t('FORÆLDEDE OBSERVATIONER. ','STALE OBSERVATIONS. '):'')+
 t('Kilde: offentlig CN '+model.forecast_week+' · #'+model.public_issue_number,
 'Source: public CN '+model.forecast_week+' · #'+model.public_issue_number)+
 ' · '+t('senest målt','last observed')+' '+(model.last_observed_at_utc||'—'));
 set('chart-title',t('Frossen kildeprognose mod faktisk kurs','Original forecast versus observed price'));
 set('chart-description',t('Kun verificerede timeslukkepriser; manglende timer er afbrudt. Blå dagsprognose vises kun, hvis den findes som originalt udstedte punkter.',
 'Verified hourly prices only; missing hours break the path. Blue daily forecasts require original published points.'));
 document.querySelectorAll('[data-asset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.asset===asset)));
}
async function getJson(url){
 const r=await fetch(url,{cache:'no-store',credentials:'omit'});
 if(!r.ok)throw Error('PUBLIC_FEED_HTTP_'+r.status);
 return r.json();
}
async function refresh(){
 clearPlaying();
 try{
  const [snapshot,lineage]=await Promise.all([getJson(sourceUrl),getJson(lineageUrl)]);
  model=readOfficialGraphB(snapshot,asset,{now_utc:new Date().toISOString(),publication_lineage:lineage});
  const start=Date.parse(model.bands?.[0]?.window_start_utc||'');
  const end=Date.parse(model.last_observed_at_utc||'');
  sliderHour=Number.isFinite(start)&&Number.isFinite(end)?Math.max(0,Math.min(167,Math.floor((end-start)/HOUR))):0;
 }catch{model=null}
 plot();
}
document.querySelectorAll('[data-asset]').forEach(b=>b.addEventListener('click',()=>{
 asset=b.dataset.asset==='ETH'?'ETH':'BTC';refresh();
}));
document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>{
 language=b.dataset.lang==='en'?'en':'da';plot();
}));
$('hour-slider')?.addEventListener('input',e=>{clearPlaying();sliderHour=Number(e.currentTarget.value);plot()});
$('play')?.addEventListener('click',()=>{
 if(playTimer!==null){clearPlaying();return}
 if(!model||model.source_status!=='SOURCE_BOUNDED'||$('hour-slider').disabled)return;
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)return;
 const end=Number($('hour-slider').max);
 if(sliderHour>=end)sliderHour=0;
 set('play-text',t('Stop','Pause'));
 playTimer=setInterval(()=>{sliderHour=Math.min(end,sliderHour+1);plot();if(sliderHour>=end)clearPlaying()},135);
});
document.addEventListener('visibilitychange',()=>{if(document.hidden)clearPlaying()});
window.addEventListener('pagehide',clearPlaying);
refresh();
