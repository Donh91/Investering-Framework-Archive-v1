/**
 * Graph B v2.1 source-first COMPONENT PILOT, not the canonical site app.
 *
 * This is a deliberately small port of AppDeploy B/C Studio's actual SVG
 * geometry/updateGraph architecture. It consumes ONLY published first-party
 * /data/latest.json through the independently tested official-source adapter.
 * The original AppDeploy synthetic sine-wave fixture and demo switch are NOT imported.
 *
 * This file must never be treated as an Official Compass, forecast issuer,
 * independent proof attestation or score engine.
 */
import {readOfficialGraphB,replayObservedUntil} from './official-source-adapter.mjs';
const $=id=>document.getElementById(id);
const SVG='http://www.w3.org/2000/svg',HOUR=3600000,DAY=86400000;
const SOURCE_RECHECK_MS=5*60*1000;
let asset='BTC',language='da',model=null,sliderHour=0,playTimer=null,staleTimer=null,requestGeneration=0;
let inspectView=null,inspectHour=null;
const s=(n)=>typeof n==='number'&&Number.isFinite(n)&&n>0;
const t=(da,en)=>language==='da'?da:en;
const utc=ms=>new Date(ms).toLocaleString(language==='da'?'da-DK':'en-GB',{
 timeZone:'UTC',weekday:'short',day:'numeric',month:'short',hour:'2-digit',minute:'2-digit'
})+' UTC';
const num=(value,unit)=>s(value)?new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{
  minimumFractionDigits:2,maximumFractionDigits:2
 }).format(value)+' '+(unit==='USDT'?'USDT':'UNAVAILABLE'):'—';
const set=(id,value)=>{const n=$(id);if(n)n.textContent=String(value)};
const attr=(id,key,value)=>{const n=$(id);if(n)n.setAttribute(key,String(value))};
const movePath=pts=>pts.map((p,i)=>(i?'L':'M')+p.x.toFixed(2)+','+p.y.toFixed(2)).join(' ');
// v2.4G2b PROPOSAL: monotone cubic (Fritsch–Carlson, = d3.curveMonotoneX) through the SAME
// source points. Passes exactly through every point and never leaves the y-range of each
// neighbouring pair (no implied highs/lows). Used only for the 7 daily expected closes.
const monotonePath=pts=>{
 const n=pts.length;if(n<3)return movePath(pts);
 const dx=[],m=[];for(let i=0;i<n-1;i++){dx[i]=pts[i+1].x-pts[i].x;m[i]=(pts[i+1].y-pts[i].y)/dx[i]}
 const t=[m[0]];for(let i=1;i<n-1;i++)t[i]=m[i-1]*m[i]<=0?0:(3*(dx[i-1]+dx[i]))/((2*dx[i]+dx[i-1])/m[i-1]+(dx[i]+2*dx[i-1])/m[i]);
 t[n-1]=m[n-2];
 for(let i=0;i<n-1;i++){if(m[i]===0){t[i]=0;t[i+1]=0;continue}const a=t[i]/m[i],b=t[i+1]/m[i],h=a*a+b*b;if(h>9){const k=3/Math.sqrt(h);t[i]=k*a*m[i];t[i+1]=k*b*m[i]}}
 let d='M'+pts[0].x.toFixed(2)+','+pts[0].y.toFixed(2);
 for(let i=0;i<n-1;i++){const h=dx[i]/3;d+=' C'+(pts[i].x+h).toFixed(2)+','+(pts[i].y+t[i]*h).toFixed(2)+' '+(pts[i+1].x-h).toFixed(2)+','+(pts[i+1].y-t[i+1]*h).toFixed(2)+' '+pts[i+1].x.toFixed(2)+','+pts[i+1].y.toFixed(2)}
 return d;
};
const sourceUrl=new URL('../../data/latest.json',import.meta.url);
const lineageUrl=new URL('../../data/publication-lineage.json',import.meta.url);
function clearPlaying(){
 if(playTimer!==null){clearInterval(playTimer);playTimer=null}
 set('play-text',t('Afspil uge','Play week'));
}
function textLabels(){
 const labels={
  da:{card:'Ugens markedsudsyn',desc:'Mandagens prisprognose sammenholdt med de faktiske kurser.',
    actual:'Verificerede timesluk · UTC',missing:'Ingen udstedt dagsprognose',
    forecast:'Forventet dagskurs',observed:'Faktisk kurs',bounds:'Mandagens prisinterval',
    title:'Spol gennem ugen',mon:'Mandag',sun:'Søndag'},
  en:{card:'Weekly outlook',desc:'Monday’s forecast range compared with observed prices.',
    actual:'Verified hourly closes · UTC',missing:'No issued daily forecast',
    forecast:'Expected daily close',observed:'Observed price',bounds:'Monday’s price range',
    title:'Explore the week',mon:'Monday',sun:'Sunday'}
 }[language];
 // Preserve the ORIGINAL AppDeploy "B" accent badge, not flattened text.
 const heading=$('card-heading');
 if(heading){
  const badge=heading.querySelector('.alt-token');
  heading.replaceChildren(document.createTextNode(t('Ugens prisgraf ','Weekly outlook ')));
  if(badge){badge.textContent='B';heading.append(badge)}
  else{const b=document.createElement('span');b.className='alt-token';b.textContent='B';heading.append(b)}
 }
 const e=document.querySelector('.card-desc');if(e)e.textContent=labels.desc;
 const map=[['.instrument-left small',labels.actual],['.swatch-forecast + span',labels.forecast],
 ['.swatch-actual + span',labels.observed],['.swatch-band + span',labels.bounds],
 ['.time-control label',labels.title],['.time-extents span:first-child',labels.mon],
 ['.time-extents span:last-child',labels.sun]];
 for(const [selector,value] of map){const target=document.querySelector(selector);if(target)target.textContent=value}

 // NEXT's single-source Premium entry uses this same DA/EN control.
 // The isolated nested B reference has no Premium navigation, so these are NOOPs there.
 const officialHome=!!document.body?.classList?.contains('premium-home');
 const rootWords=language==='en'?{
  title:'This week’s forecast. Observed prices.',
  intro:'Monday’s original price range versus observed prices.',
  disclaimer:officialHome?'Source-backed · Original ranges and observed prices.':'Preview · Source-backed, without demo prices.',
  graph:'Weekly chart',compass:'Compass',pro:'Compass PRO ↗',path:'PATH',proof:officialHome?'Results':'Results & method',official:officialHome?'Archive ↗':'Official site ↗',meta:'SOURCES & METHOD',metaTitle:'Evidence, not assumptions.',
  metaCopy:'Public Cycle Navigator, Official Compass and observed market prices. No recreated forecasts or interpolated outcomes.',
  metaOpen:'Sources and documentation',
  metaMethod:'Cycle, Compass and market observations have separate source rules. Archived results remain tied to their original published evidence.',
  cnSource:'Cycle Navigator ↗',compassSource:'Compass ↗',scoreArchive:'Results archive ↗'
 }:{
  title:'Ugens prognose. Faktiske kurser.',
  intro:'Mandagens frosne høj/lav-intervaller mod den faktiske kursudvikling.',
  disclaimer:officialHome?'Kildebaseret · Oprindelige intervaller og observerede kurser.':'Forhåndsvisning · Kildebaseret, uden demonstrationskurser.',
  graph:'Ugens graf',compass:'Kompas',pro:'Kompas PRO ↗',path:'PATH',proof:officialHome?'Resultater':'Resultat og metode',official:officialHome?'Arkiv ↗':'Officiel side ↗',meta:'KILDER & METODE',metaTitle:'Dokumenteret, ikke antaget.',
  metaCopy:'Offentlig Cycle Navigator, officielt Kompas og observerede markedspriser. Ingen konstruerede prognoser eller udfald.',
  metaOpen:'Kilder og dokumentation',
  metaMethod:'Cyklus, Kompas og observerede markedspriser har hver deres kildekrav. Historiske resultater bygger på den oprindelige offentliggjorte dokumentation.',
  cnSource:'Cycle Navigator ↗',compassSource:'Kompas ↗',scoreArchive:'Resultatarkiv ↗'
 };
 document.querySelectorAll('[data-premium-nav]').forEach(el=>{
  const v=rootWords[el.dataset.premiumNav];if(v)el.textContent=v;
  if(officialHome&&el.dataset.premiumNav==='official')el.setAttribute('aria-label',language==='en'?'Previous version':'Forrige version');
  if(officialHome&&el.dataset.premiumNav==='proof')el.setAttribute('aria-label',language==='en'?'Results and method':'Resultat og metode');
 });
 document.querySelectorAll('[data-premium-copy]').forEach(el=>{
  const v=rootWords[el.dataset.premiumCopy];if(v)el.textContent=v;
 });

 const staticLabels=[
  ['.premium-entry-overline',officialHome?t('CYCLE NAVIGATOR / OFFICIEL','CYCLE NAVIGATOR / OFFICIAL'):
   'CYCLE NAVIGATOR / NEXT'],
  ['[data-t="cardEyebrow"]',t('UGENS PROGNOSE / FAKTISKE KURSER','WEEKLY FORECAST / OBSERVED PRICES')],
  ['[data-t="freeze"]',model?.forecast_status==='SOURCE_ISSUED'?
   t('Original kildeudstedt prognose','Original source-issued forecast'):
   t('Oprindelig ugeprognose','Original weekly forecast')],
  ['.dev-brand span',officialHome?t('CYCLE NAVIGATOR · OFFICIEL','CYCLE NAVIGATOR · OFFICIAL'):
   document.querySelector('.premium-entry')?
   t('PREMIUM v2.1 · IKKE OFFICIEL FORSIDE','PREMIUM v2.1 · NOT OFFICIAL HOMEPAGE'):
   t('DESIGN QA · IKKE PRODUKTION','DESIGN QA · NOT PRODUCTION')]
 ];
 for(const [selector,value] of staticLabels){const n=document.querySelector(selector);if(n)n.textContent=value}
 // v2 (AUDIT F18): premium-tabs.mjs owns the tablist label; do not overwrite it on every plot().
 for(const [selector,value] of [
  ['.asset-select',t('Aktiv','Asset')],
  ...(document.querySelector('[role="tablist"].premium-entry-navigation')?[]:
   [['.premium-entry-navigation',t('Premium sektioner','Premium sections')]]),
  ['#hour-slider',t('Time for den observerede kurve','Hour of the observed curve')]
 ]){const n=document.querySelector(selector);if(n)n.setAttribute('aria-label',value)}
 set('play-text',playTimer===null?t('Afspil uge','Play week'):t('Stop','Pause'));
 document.documentElement.lang=language;
 document.querySelectorAll('[data-lang]').forEach(button=>
  button.setAttribute('aria-pressed',String(button.dataset.lang===language)));
}
function paintFrozenWindowLedger(bands){
 const parent=$('cn-frozen-window-ledger');
 if(!parent)return;
 parent.replaceChildren();
 if(!Array.isArray(bands)||bands.length!==3)return;
 for(let i=0;i<3;i++){
  const v=bands[i];
  if(!s(v.forecast_low)||!s(v.forecast_high)||v.forecast_low>=v.forecast_high)return parent.replaceChildren();
  const box=document.createElement('div');box.className='cn-frozen-window';
  const tag=document.createElement('span');tag.className='cn-frozen-window-day';
  tag.textContent=(language==='en'?'DAYS ':'DAG ')+['1–2','3–4','5–7'][i];
  const value=document.createElement('strong');value.textContent=
   new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0}).format(v.forecast_low)+
   ' – '+new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0}).format(v.forecast_high)+' '+(model?.forecast_declared_quote_unit||'UNAVAILABLE');
  const title=document.createElement('small');
  title.textContent=language==='en'?'Original frozen range':'Originalt frosset interval';
  box.append(tag,value,title);parent.append(box);
 }
}
function paintDailyResearchNotes(daily){
 const details=$('cn-daily-research-notes'),body=$('cn-daily-research-rows');
 if(!details||!body)return;
 body.replaceChildren();
 const ok=Array.isArray(daily)&&daily.length===7;
 details.hidden=!ok;
 if(!ok){details.open=false;return}
 const nf=new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0});
 for(const point of daily){
  const article=document.createElement('article');article.className='cn-daily-note';
  const title=document.createElement('strong');title.textContent=
   (language==='da'?'Dag ':'Day ')+point.day+' · '+nf.format(point.low)+' – '+nf.format(point.high)+' '+(model?.forecast_declared_quote_unit||'UNAVAILABLE');
  const reason=document.createElement('p');reason.textContent=point.why;
  const condition=document.createElement('small');condition.textContent=
    (language==='da'?'Ugyldig hvis: ':'Invalid if: ')+point.invalidate_if;
  article.append(title,reason,condition);body.append(article);
 }
}
function paintActualDailyRanges(days,x,y){
 const svg=$('chart');
 if(!svg)return;
 let parent=svg.querySelector('[data-actual-daily-ranges]');
 if(!parent){
  parent=document.createElementNS(SVG,'g');
  parent.setAttribute('data-actual-daily-ranges','');
  parent.setAttribute('role','group');
  parent.setAttribute('aria-label','Observed daily high and low');
  svg.append(parent);
 }
 parent.replaceChildren();
 for(const day of days){
  const g=document.createElementNS(SVG,'g');
  g.setAttribute('data-actual-day',String(day.day));
  g.setAttribute('data-observation-state',day.status);
  const title=document.createElementNS(SVG,'title');
  title.textContent=day.date+' UTC | '+day.status+' | low '+day.low+
    ', high '+day.high+', close '+day.close+', as of '+day.as_of_utc;
  g.append(title);
  const cx=x(day.as_of_time*1000),lo=y(day.low),hi=y(day.high);
  for(const [x1,y1,x2,y2] of [
   [cx,hi,cx,lo],[cx-5,hi,cx+5,hi],[cx-5,lo,cx+5,lo]]){
   const line=document.createElementNS(SVG,'line');
   for(const [key,value] of [['x1',x1],['y1',y1],['x2',x2],['y2',y2],
     ['stroke','var(--actual)'],['stroke-width',2],['stroke-linecap','round']])
     line.setAttribute(key,String(value));
   g.append(line);
  }
  parent.append(g);
 }
}
function plot(){
 // Never present BTC-source numeric evidence as ETH while a new fetch is pending.
 if(model && model.asset!==asset)model=null;
 textLabels();
 // A source outage must never make the selected BTC/ETH control lie.
 // Update focus and pair before the early missing-source return.
 document.querySelectorAll('[data-asset]').forEach(b=>
  b.setAttribute('aria-pressed',String(b.dataset.asset===asset)));
 set('pair',asset+' / '+(model?.actual_quote_unit||'UNAVAILABLE'));
 const card=$('variant-panel');card.dataset.variant='b';
 card.dataset.source=model?.forecast_status==='SOURCE_ISSUED'?'published':'missing';
 card.dataset.freshness=model?.source_status==='SOURCE_BOUNDED'?model.live_freshness.toLowerCase():'unavailable';
 const actualLabel=document.querySelector('.instrument-left small');
 if(actualLabel&&model?.live_freshness==='STALE')actualLabel.textContent=
  t('Forældet observation · ikke aktuel kurs','Stale observation · not a current price');
 const headerWeek=document.querySelector('.instrument-right > span');
 if(headerWeek)headerWeek.textContent=model?.forecast_week?
  model.forecast_week+' · CN #'+model.public_issue_number:t('UGE · KILDE AFVENTER','WEEK · SOURCE PENDING');
 const dayWords=language==='da'?['MAN','TIR','ONS','TOR','FRE','LØR','SØN']:
  ['MON','TUE','WED','THU','FRI','SAT','SUN'];
 document.querySelectorAll('.day-axis [data-day]').forEach((item,i)=>{item.textContent=dayWords[i]||''});
 const forecastLegend=$('cn-forecast-legend');
 if(forecastLegend)forecastLegend.hidden=model?.forecast_status!=='SOURCE_ISSUED';
 if(!model||model.source_status!=='SOURCE_BOUNDED'){
  paintFrozenWindowLedger([]);
  paintDailyResearchNotes([]);
  ['range-band','range-upper','range-lower','forecast','forecast-points','actual'].forEach(id=>attr(id,'d',''));
  $('chart')?.querySelector('[data-actual-daily-ranges]')?.replaceChildren();
  $('price-axis')?.replaceChildren();$('grid')?.replaceChildren();
  set('observed-value','—');set('time-label','—');set('timeline-label','—');
  set('source-state',t('Ingen verificeret kilde','No verified source'));
  $('hour-slider').disabled=true;$('hour-slider').value='0';$('hour-slider').max='0';
  $('playhead').setAttribute('visibility','hidden');
  $('endpoint')?.setAttribute('visibility','hidden');$('endpoint-halo')?.setAttribute('visibility','hidden');
  set('feed-status',t('Afventer gyldige officielle CN-data. Ingen prognose eller pris vises.','No valid official CN source. No forecast or price shown.'));
  inspectView=null;hideInspector();
  return;
 }
 const bands=model.bands||[],hourly=model.hourly_observations||[];
 const quoteComparable=model.forecast_comparison_quote_status==='SAME_DECLARED_UNIT';
 paintFrozenWindowLedger(bands);
 const hasDailyRanges=model.daily_range_status==='SOURCE_ISSUED'&&model.daily_ranges?.length===7;
 paintDailyResearchNotes(hasDailyRanges?model.daily_ranges:[]);
 const rlabel=document.querySelector('.swatch-band + span');
 if(rlabel&&hasDailyRanges)rlabel.textContent=t('7 daglige frosne høj/lav-intervaller','7 original daily high/low ranges');
 const start=Date.parse(bands[0].window_start_utc),end=Date.parse(bands.at(-1).window_end_utc);
 if(!Number.isFinite(start)||!Number.isFinite(end)||end-start!==7*DAY){model=null;plot();return}
 const availableMax=hourly.length?Math.max(0,Math.min(168,Math.floor((hourly.at(-1).time*1000-start)/HOUR))):0;
 sliderHour=Math.min(Math.max(0,sliderHour),availableMax);
 const hourInput=$('hour-slider');hourInput.max=String(availableMax);hourInput.value=String(sliderHour);
 hourInput.disabled=!hourly.length;
 const cursor=Math.min(end,start+sliderHour*HOUR);
 $('playhead').setAttribute('visibility','visible');
 const observedRuns=replayObservedUntil(model,new Date(cursor).toISOString());
 const visible=observedRuns.flat();
 // Only show days whose ORIGINAL observation cutoff is at/before replay time.
 const visibleActualDays=(model.actual_daily_ranges||[]).filter(p=>p.as_of_time*1000<=cursor);
 const values=[...(quoteComparable?bands.flatMap(b=>[b.forecast_low,b.forecast_high]):[]),
  ...(hasDailyRanges?model.daily_ranges.flatMap(d=>[d.low,d.high]):[]),
  ...model.forecast.flatMap(p=>[p.expected_close,p.low,p.high]),
  ...visible.map(p=>p.value),...visibleActualDays.flatMap(p=>[p.low,p.high])].filter(s);
 if(values.length===0){model=null;plot();return}
 const min=Math.min(...values),max=Math.max(...values),padding=(max-min||1)*.07;
 const lo=min-padding,hi=max+padding;
 const x=ms=>14+Math.max(0,Math.min(1,(ms-start)/(end-start)))*972;
 const y=v=>28+((hi-v)/(hi-lo))*344;
 const xy=p=>({x:x(p.time*1000),y:y(p.value)});
 const area=arr=>movePath(arr.map(p=>({x:x(p.time*1000),y:y(p.high)})))+' '+
   movePath(arr.slice().reverse().map(p=>({x:x(p.time*1000),y:y(p.low)}))).replace(/^M/,'L')+' Z';
 attr('forecast-points','d','');
 if(model.forecast_status==='SOURCE_ISSUED'){
  const f=model.forecast.map(p=>({time:p.time,value:p.expected_close}));
  attr('forecast','d',monotonePath(f.map(xy)));
  // v2.4G2: a dot on each of the 7 source-issued expected closes (zero-length round-cap
  // subpaths stay circular under the non-uniform viewBox). Same points, nothing added.
  attr('forecast-points','d',f.map(xy).map(p=>'M'+p.x.toFixed(2)+','+p.y.toFixed(2)+' l0,0').join(' '));
  // Each source-issued daily high/low belongs to its original UTC day cell.
  // The seven forecast close points stay at their original end-of-day timestamps.
  const cells=model.forecast.map((p,i)=>({
   left:x(start+i*DAY),right:x(start+(i+1)*DAY),low:p.low,high:p.high
  }));
  attr('range-band','d',cells.map(p=>
   'M'+p.left+','+y(p.high)+' L'+p.right+','+y(p.high)+
   ' L'+p.right+','+y(p.low)+' L'+p.left+','+y(p.low)+' Z').join(' '));
  for(const [id,key] of [['range-upper','high'],['range-lower','low']])
   attr(id,'d',cells.map(p=>
    'M'+p.left.toFixed(2)+','+y(p[key]).toFixed(2)+
    ' L'+p.right.toFixed(2)+','+y(p[key]).toFixed(2)).join(' '));
 }else if(hasDailyRanges){
  // Authentic daily high/low envelope only. Never draw an implied close line.
  attr('forecast','d','');
  const d=model.daily_ranges;
  const segments=d.map(p=>{
   const left=x(Date.parse(p.window_start_utc)),right=x(Date.parse(p.window_end_utc));
   return 'M'+left+','+y(p.high)+' L'+right+','+y(p.high)+
     ' L'+right+','+y(p.low)+' L'+left+','+y(p.low)+' Z';
  });
  attr('range-band','d',segments.join(' '));
  const edge=key=>d.map(p=>{
   const left=x(Date.parse(p.window_start_utc)),right=x(Date.parse(p.window_end_utc));
   return 'M'+left.toFixed(2)+','+y(p[key]).toFixed(2)+
     ' L'+right.toFixed(2)+','+y(p[key]).toFixed(2);
  }).join(' ');
  attr('range-upper','d',edge('high'));
  attr('range-lower','d',edge('low'));
 }else if(!quoteComparable){
  // Retain the original ledger, but never draw forecast numbers on a
  // native spot axis when the declared quote is different or unknown.
  for(const id of ['forecast','range-band','range-upper','range-lower'])attr(id,'d','');
 }else{
  attr('forecast','d','');
  // Each frozen intraweek window is already a prospective range forecast.
  // Draw the authentic three-step horizon envelope directly; do NOT imply
  // a daily expected-close line or interpolate between window centers.
  // Three independently issued aggregate range windows: NEVER fabricate
  // a connecting expected-close price path across missing original days.
  attr('range-band','d',bands.map(b=>{
   const left=x(Date.parse(b.window_start_utc)),right=x(Date.parse(b.window_end_utc));
   const up=y(b.forecast_high),down=y(b.forecast_low);
   return 'M'+left+','+up+' L'+right+','+up+' L'+right+','+down+
    ' L'+left+','+down+' Z';
  }).join(' '));
  // Visibly retain the full issued high/low envelope without a giant blue
  // rectangle dominating the price chart: restrained horizontal boundary
  // rails per independently frozen window, NOT a connected forecast curve.
  const edge=key=>bands.map(b=>{
   const left=x(Date.parse(b.window_start_utc)),right=x(Date.parse(b.window_end_utc));
   const level=y(b[key]);
   return 'M'+left.toFixed(2)+','+level.toFixed(2)+
     ' L'+right.toFixed(2)+','+level.toFixed(2);
  }).join(' ');
  attr('range-upper','d',edge('forecast_high'));
  attr('range-lower','d',edge('forecast_low'));
 }
 attr('actual','d',observedRuns.map(run=>movePath(run.map(xy))).join(' '));
 paintActualDailyRanges(visibleActualDays,x,y);
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
 set('pair',asset+' / '+(model?.actual_quote_unit||'UNAVAILABLE'));set('observed-value',num(last?.value,model?.actual_quote_unit));
 set('time-label',last?utc(last.time*1000):'—');
 set('timeline-label',utc(cursor));
 const incompatibleQuote=!quoteComparable;
 const issuedButIncomparable=model.forecast_status==='SOURCE_ISSUED_QUOTE_INCOMPARABLE'||
  model.daily_range_status==='SOURCE_ISSUED_QUOTE_INCOMPARABLE';
 const st=model.forecast_status==='SOURCE_ISSUED'?
  t('Kildeudstedt dagsprognose','Source-issued daily forecast'):
  issuedButIncomparable?t('Kildeudstedt, anden/ukendt valuta','Source-issued, different/unknown quote'):
  incompatibleQuote?t('Valuta ikke sammenlignelig','Quote not comparable'):
  hasDailyRanges?t('7 frosne dagsintervaller','7 frozen daily ranges'):
  t('Original prognose · 3 vinduer','Original forecast · 3 windows');
 set('source-state',st);
 const stale=model.live_freshness==='STALE';
 const historicalFallback=model.transport_fallback_historical===true;
 const clockMs=Date.parse(model?.last_observed_at_utc||'');
 const observedClock=Number.isFinite(clockMs)?
  new Date(clockMs).toLocaleString(language==='da'?'da-DK':'en-GB',{
   timeZone:'Europe/Copenhagen',day:'2-digit',month:'short',hour:'2-digit',minute:'2-digit'
  }):'—';
 set('feed-status',(historicalFallback?
  t('Kilden kan ikke hentes nu. Kun tidligere verificeret historik vises. ',
    'Source temporarily unavailable. Previously verified history only. '):'')+
 (stale?t('Observerede kurser er forældede, ikke aktuelle. ',
  'Observed prices are stale, not current. '):'')+
 t('Offentlig Cycle Navigator og verificerede spotobservationer. ',
   'Public Cycle Navigator and verified spot observations. ')+
 t('Seneste dokumenterede timeluk: ','Last documented hourly close: ')+observedClock+
 ' · '+(model.actual_quote_unit==='USDT'?'USDT':t('valuta ikke bekræftet','quote not confirmed'))+
 '. '+(incompatibleQuote?
   t('Den originale prognosekurve skjules, da kursvalutaerne ikke kan sammenlignes.',
     'Original forecast line hidden because the currencies are not comparable.'):
   t('Kun originale, sammenlignelige prognosedata vises.',
     'Only original, comparable forecast data is shown.')));
 const observedDay=visibleActualDays.at(-1);
 if(observedDay){
  const frozenDay=model.forecast?.find(row=>row.day===observedDay.day);
  const details=t('Faktisk dagsinterval','Observed daily range')+' '+
   observedDay.date+' UTC ('+
   (observedDay.status==='LIVE'?t('delvis','partial'):t('komplet','complete'))+
   '): '+num(observedDay.low,model.actual_quote_unit)+' / '+
   num(observedDay.high,model.actual_quote_unit)+
   ' · '+t('luk','close')+' '+num(observedDay.close,model.actual_quote_unit)+
   ' · '+utc(observedDay.as_of_time*1000);
  set('feed-status',$('feed-status').textContent+' '+details+
   (frozenDay?' · '+t('oprindeligt forventet luk','original expected close')+
     ' '+num(frozenDay.expected_close,model.forecast_declared_quote_unit):''));
 }
 set('chart-title',t('Mandagens syv frosne dagsintervaller mod faktisk kurs','Monday’s seven frozen daily ranges versus observed price'));
 set('chart-description',t('Mandagens syv frosne høj/lav-intervaller, ét pr. UTC-døgn. Den grønne observerede kurs brydes ved manglende timer. Blå stiplet forventet dagskurs kræver syv udstedte punkter.',
 'Monday’s seven frozen high/low ranges, one per UTC day. Verified hourly prices only; missing hours break the path. Blue daily forecasts require seven original published points.'));
 document.querySelectorAll('[data-asset]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.asset===asset)));
 // v2 presentation only: hand the already-validated, already-drawn values to the
 // read-only inspector. No new values, no interpolation, no extra fetch.
 inspectView={start,end,lo,hi,cursor,observed:visible,
  forecast:model.forecast_status==='SOURCE_ISSUED'&&quoteComparable?model.forecast:null,
  unit:model.actual_quote_unit,forecastUnit:model.forecast_declared_quote_unit,stale};
 alignDayAxis(cursor,start);
 refreshInspector();
}
/* ---- CN SITE v2: read-only chart inspector (presentation only) ----------------
 * Crosshair + tooltip + keyboard value text for the existing Graph B SVG.
 * It ONLY reads values plot() has already validated and drawn (inspectView).
 * Observed price is shown solely for an actual source hour (no interpolation,
 * gaps stay gaps). Forecast values are shown only when plot() drew the original
 * source-issued, quote-comparable daily path. Text via textContent only.
 */
let inspectMode=null,inspectNodes=null;
function alignDayAxis(cursor,start){
 const current=Math.max(0,Math.min(6,Math.floor((cursor-start)/DAY)));
 const svg=$('chart'),axis=document.querySelector('#variant-panel .day-axis');
 const geo=axis&&svg&&typeof svg.getBoundingClientRect==='function'?
  [svg.getBoundingClientRect(),axis.getBoundingClientRect()]:null;
 // Day labels sit at the centre of the SAME UTC day cell the SVG draws
 // (x = 14 + (i + .5) * 972/7 in viewBox units), at every breakpoint.
 if(geo&&geo[0].width>0)axis.classList?.add('cn-v2-aligned');
 document.querySelectorAll('.day-axis [data-day]').forEach((n,i)=>{
  n.classList?.toggle('is-current',i===current);
  if(geo&&geo[0].width>0&&n.style)n.style.left=
   (geo[0].left-geo[1].left+(14+(i+.5)*972/7)/1000*geo[0].width).toFixed(1)+'px';
 });
}
function inspectorNodes(){
 if(inspectNodes)return inspectNodes;
 const shell=document.querySelector('#variant-panel .plot-shell');
 const svg=$('chart');
 if(!shell||!svg||typeof svg.getBoundingClientRect!=='function')return null;
 const make=(cls,hidden)=>{const n=document.createElement('div');n.className=cls;
  if(hidden)n.setAttribute('aria-hidden','true');n.hidden=true;shell.append(n);return n};
 const line=make('cn-v2-crosshair',true),dot=make('cn-v2-dot',true),tip=make('cn-v2-tip',false);
 tip.setAttribute('role','tooltip');tip.id='cn-v2-tip';
 inspectNodes={shell,svg,line,dot,tip};
 return inspectNodes;
}
function hideInspector(){
 inspectMode=null;inspectHour=null;
 const n=inspectNodes;if(!n)return;
 for(const k of ['line','dot','tip'])n[k].hidden=true;
 n.shell.classList?.remove('is-inspecting');
}
function inspectLines(hourMs){
 const v=inspectView;if(!v)return null;
 const lines=[[utc(hourMs),'cn-v2-tip-time']];
 const hit=v.observed.find(p=>Math.abs(p.time*1000-hourMs)<HOUR/2);
 if(hit)lines.push([t('Faktisk kurs ','Observed ')+num(hit.value,v.unit),'cn-v2-tip-actual']);
 else if(hourMs>v.cursor)lines.push([t('Ikke observeret endnu','Not observed yet'),'cn-v2-tip-muted']);
 else lines.push([t('Ingen verificeret timeobservation','No verified hourly observation'),'cn-v2-tip-muted']);
 const day=Math.floor((hourMs-v.start)/DAY);
 const f=v.forecast&&day>=0&&day<7?v.forecast[day]:null;
 if(f){
  lines.push([t('Dag ','Day ')+(day+1)+' · '+t('forventet luk ','expected close ')+num(f.expected_close,v.forecastUnit),'cn-v2-tip-forecast']);
  if(s(f.low)&&s(f.high))lines.push([t('Frosset interval ','Frozen range ')+
   new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0}).format(f.low)+' – '+
   new Intl.NumberFormat(language==='da'?'da-DK':'en-US',{maximumFractionDigits:0}).format(f.high),'cn-v2-tip-band']);
 }
 if(hit&&v.stale)lines.push([t('Forældet observation · ikke aktuel kurs','Stale observation · not a current price'),'cn-v2-tip-muted']);
 return {lines,hit};
}
function showInspectorAt(hourMs){
 const v=inspectView,n=inspectorNodes();
 if(!v||!n||!(hourMs>=v.start&&hourMs<=v.end)){hideInspector();return}
 const info=inspectLines(hourMs);if(!info){hideInspector();return}
 const r=n.svg.getBoundingClientRect(),sr=n.shell.getBoundingClientRect();
 if(!r.width||!r.height)return;
 const sx=14+((hourMs-v.start)/(v.end-v.start))*972;
 const px=r.left-sr.left+sx/1000*r.width;
 n.line.style.left=px.toFixed(1)+'px';
 n.line.style.top=(r.top-sr.top+28/405*r.height).toFixed(1)+'px';
 n.line.style.height=(344/405*r.height).toFixed(1)+'px';
 n.line.hidden=false;
 if(info.hit){
  const sy=28+((v.hi-info.hit.value)/(v.hi-v.lo))*344;
  n.dot.style.left=px.toFixed(1)+'px';
  n.dot.style.top=(r.top-sr.top+sy/405*r.height).toFixed(1)+'px';
  n.dot.hidden=false;
 }else n.dot.hidden=true;
 n.tip.replaceChildren(...info.lines.map(([text,cls])=>{
  const row=document.createElement('span');row.className=cls;row.textContent=text;return row}));
 n.tip.hidden=false;
 const w=n.tip.offsetWidth||180,room=sr.width;
 let left=px+14;if(left+w>room-4)left=px-14-w;
 n.tip.style.left=Math.max(4,left).toFixed(1)+'px';
 n.shell.classList?.add('is-inspecting');
}
function refreshInspector(){
 const v=inspectView;
 const slider=$('hour-slider');
 // Keyboard / screen-reader parity: the slider announces the same values.
 if(v&&slider){
  const info=inspectLines(Math.floor(v.cursor/HOUR)*HOUR);
  if(info)slider.setAttribute('aria-valuetext',info.lines.map(x=>x[0]).join(' · '));
 }
 if(!v){hideInspector();return}
 if(inspectMode==='slider')showInspectorAt(Math.floor(v.cursor/HOUR)*HOUR);
 else if(inspectMode==='pointer'&&inspectHour!==null)showInspectorAt(inspectHour);
}
function installInspector(){
 const n=inspectorNodes();if(!n)return;
 const fromPointer=e=>{
  const v=inspectView;if(!v)return;
  const r=n.svg.getBoundingClientRect();if(!r.width)return;
  const sx=(e.clientX-r.left)/r.width*1000;
  const ms=v.start+Math.max(0,Math.min(1,(sx-14)/972))*(v.end-v.start);
  inspectMode='pointer';inspectHour=Math.round(ms/HOUR)*HOUR;
  showInspectorAt(inspectHour);
 };
 n.svg.addEventListener('pointermove',fromPointer);
 n.svg.addEventListener('pointerdown',fromPointer);
 n.svg.addEventListener('pointerleave',e=>{if(e.pointerType==='mouse')hideInspector()});
 document.addEventListener('pointerdown',e=>{if(inspectMode==='pointer'&&!n.svg.contains(e.target))hideInspector()});
 document.addEventListener('keydown',e=>{if(e.key==='Escape')hideInspector()});
 const slider=$('hour-slider');
 slider?.addEventListener('focus',()=>{inspectMode='slider';refreshInspector()});
 slider?.addEventListener('blur',()=>{if(inspectMode==='slider')hideInspector()});
 const relayout=()=>{if(inspectView)alignDayAxis(inspectView.cursor,inspectView.start);if(inspectMode)refreshInspector()};
 window.addEventListener('resize',relayout);
 // Tabs, fonts and scrollbars change the SVG width after plot(); keep labels on their day cells.
 if(typeof ResizeObserver==='function')new ResizeObserver(relayout).observe(n.svg);
}
async function getJson(url){
 const r=await fetch(url,{cache:'no-store',credentials:'omit',redirect:'error',
  signal:AbortSignal.timeout(12000)});
 if(!r.ok)throw Error('PUBLIC_FEED_HTTP_'+r.status);
 return r.json();
}
async function refresh({background=false}={}){
 const request=++requestGeneration,selected=asset;
 const oldMax=Number($('hour-slider')?.max||0);
 const followLatest=sliderHour>=oldMax;
 const replayHour=sliderHour;
 if(!background){
  clearPlaying();
  if(staleTimer!==null){clearTimeout(staleTimer);staleTimer=null;}
  // Asset changes invalidate the old asset immediately.
  model=null;sliderHour=0;plot();
 }
 try{
  // v2.5.1: lineage is optional in the adapter; a missing/invalid lineage file must not blank the chart.
  const [snapshot,lineage]=await Promise.all([getJson(sourceUrl),getJson(lineageUrl).catch(()=>null)]);
  if(request!==requestGeneration||selected!==asset)return;
  const next=readOfficialGraphB(snapshot,selected,{now_utc:new Date().toISOString(),publication_lineage:lineage});
  if(next.asset!==asset)return;
  if(staleTimer!==null){clearTimeout(staleTimer);staleTimer=null;}
  model=next;
  if(next.source_status==='SOURCE_BOUNDED'&&next.live_freshness==='FRESH'){
   const deadline=Date.parse(next.last_observed_at_utc)+next.source_freshness_sla_minutes*60000;
   const ms=deadline-Date.now()+150;
   if(ms>0&&ms<2147483000)staleTimer=setTimeout(()=>{
      // The original observation's SLA must expire even if a periodic fetch hangs.
      // requestGeneration guards fetched responses, NOT the active source deadline.
      if(asset!==selected)return;
      const currentDeadline=Date.parse(model?.last_observed_at_utc||'')+
       Number(model?.source_freshness_sla_minutes)*60000;
      if(model?.asset===selected&&model.source_status==='SOURCE_BOUNDED'&&
         model.live_freshness==='FRESH'&&Number.isFinite(currentDeadline)&&Date.now()>=currentDeadline){
       model={...model,live_freshness:'STALE',is_current_quote:false};
       plot();
      }
   },ms);
  }
  const start=Date.parse(next.bands?.[0]?.window_start_utc||'');
  const end=Date.parse(next.last_observed_at_utc||'');
  const latestHour=Number.isFinite(start)&&Number.isFinite(end)?
   Math.max(0,Math.min(168,Math.floor((end-start)/HOUR))):0;
  sliderHour=background&&!followLatest?Math.min(replayHour,latestHour):latestHour;
 }catch{
  if(request!==requestGeneration||selected!==asset)return;
  clearPlaying();
  if(staleTimer!==null){clearTimeout(staleTimer);staleTimer=null;}
  // Only after a previously authenticated source-bound Graph B: a temporary
  // network/JSON transport failure must not erase genuine observed history.
  // This is a HISTORICAL read, not a live/current price or an admitted new
  // source. Explicit source-integrity rejection still produces UNAVAILABLE.
  if(background&&model?.asset===selected&&model.source_status==='SOURCE_BOUNDED'){
   model={...model,live_freshness:'STALE',is_current_quote:false,
    transport_fallback_historical:true};
  }else{model=null;sliderHour=0;}
 }
 plot();
}
document.querySelectorAll('[data-asset]').forEach(b=>b.addEventListener('click',()=>{
 asset=b.dataset.asset==='ETH'?'ETH':'BTC';refresh();
}));
document.querySelectorAll('[data-lang]').forEach(b=>b.addEventListener('click',()=>{
 language=b.dataset.lang==='en'?'en':'da';plot();
 document.dispatchEvent(new CustomEvent('cn:languagechange',{detail:{language}}));
}));
$('hour-slider')?.addEventListener('input',e=>{clearPlaying();sliderHour=Number(e.currentTarget.value);plot()});
$('play')?.addEventListener('click',()=>{
 if(playTimer!==null){clearPlaying();return}
 if(!model||model.source_status!=='SOURCE_BOUNDED'||$('hour-slider').disabled)return;
 const end=Number($('hour-slider').max);
 // v2 (AUDIT F14): reduced motion jumps straight to the latest observed hour instead of doing nothing.
 if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){sliderHour=end;plot();return}
 if(sliderHour>=end)sliderHour=0;
 set('play-text',t('Stop','Pause'));
 playTimer=setInterval(()=>{sliderHour=Math.min(end,sliderHour+1);plot();if(sliderHour>=end)clearPlaying()},135);
});
document.addEventListener('visibilitychange',()=>{
 if(document.hidden)clearPlaying();
 else refresh({background:model?.source_status==='SOURCE_BOUNDED'});
});
window.addEventListener('pagehide',clearPlaying);
// Pages can publish a new source bundle while the iPhone tab stays open.
// Re-read the public files; never extend a quote's freshness from a local timer.
const sourceRecheck=setInterval(()=>{if(!document.hidden&&playTimer===null)refresh({background:true})},SOURCE_RECHECK_MS);
try{installInspector()}catch{/* presentation layer must never block the source chart */}
window.addEventListener('pagehide',()=>clearInterval(sourceRecheck));
refresh();
