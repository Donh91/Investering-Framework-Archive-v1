/**
 * KOMPAS LIVE · pure view model and SVG description for the Kompas live card (v7 design).
 *
 * Renders ONLY the numbers of the server-side producer
 * scripts/cycle_navigator/build_kompas_live_path.py (contract KOMPAS_LIVE_PATH_v1).
 * Nothing here computes a tilt, a drift, a band or a probability: the Official Compass
 * bull/bear scale is EVIDENCE_BALANCE_NOT_PROBABILITY and the site keeps
 * site_synthesis_allowed === false. This module only selects, formats and lays out.
 *
 * Labels identify the blue line as a live hourly calculation using Challenger B\u0027s trial formula
 * and day frames as live hourly calculations using Challenger A\u0027s formula, NOT the frozen A/B issuances. The official Kompas direction word is shown attributed to
 * Kompas. The comment track is code-written ("Automatisk"); ai_text stays unused here.
 * No DOM, no fetch, no timers. Danish first; English when lang === 'en'.
 */
export const LIVE_CONTRACT='KOMPAS_LIVE_PATH_v1';
export const LIVE_HORIZONS=Object.freeze([1,3,7]);
export const LIVE_ASSETS=Object.freeze(['BTC','ETH']);

const HOUR=36e5,DAY=864e5;
const tr=(lang,da,en)=>lang==='en'?en:da;
const finite=v=>typeof v==='number'&&Number.isFinite(v);
const ms=v=>{const t=Date.parse(v);return Number.isFinite(t)?t:NaN};
const numberFormat=(lang,digits)=>new Intl.NumberFormat(lang==='en'?'en-US':'da-DK',
 {minimumFractionDigits:digits,maximumFractionDigits:digits});
export function formatInt(v,lang='da'){return numberFormat(lang,0).format(Math.round(v))}
export function formatPct(v,lang='da'){
 const r=Math.round(v*10)/10;
 const body=numberFormat(lang,1).format(Math.abs(r));
 return (r<0?'−':r>0?'+':'')+body+(lang==='en'?'%':' %');
}
const tone=v=>!finite(v)||Math.round(v*10)===0?'flat':v<0?'down':'up';
const clock=(t,lang,opts)=>new Intl.DateTimeFormat(lang==='en'?'en-GB':'da-DK',
 {timeZone:'Europe/Copenhagen',...opts}).format(new Date(t));

const OFFICIAL_WORD={UP:['Stigende','Rising'],DOWN:['Faldende','Falling'],MIXED:['Blandet','Mixed'],
 SIDEWAYS:['Sideværts','Sideways'],NO_EDGE:['Ingen dokumenteret fordel','No proven edge']};
const officialWord=(code,lang)=>OFFICIAL_WORD[code]?.[lang==='en'?1:0]||null;
const WEEKDAY_DA={MON:'mandag',TUE:'tirsdag',WED:'onsdag',THU:'torsdag',FRI:'fredag',SAT:'lørdag',SUN:'søndag'};
const WEEKDAY_EN={MON:'Monday',TUE:'Tuesday',WED:'Wednesday',THU:'Thursday',FRI:'Friday',SAT:'Saturday',SUN:'Sunday'};
const closePhrase=(code,lang)=>lang==='en'?'by '+(WEEKDAY_EN[code]||'the')+"'s close":'ved '+(WEEKDAY_DA[code]||'dagens')+'ens lukning';
const STRENGTH={svag:['svag hældning','weak tilt'],moderat:['moderat hældning','moderate tilt'],tydelig:['tydelig hældning','clear tilt']};
const DAY_LABEL={da:['SØN','MAN','TIR','ONS','TOR','FRE','LØR'],en:['SUN','MON','TUE','WED','THU','FRI','SAT']};

const UNAVAILABLE_REASON={
 HOURLY_STALE:['Seneste timekurs er mere end 90 minutter gammel.','The latest hourly price is more than 90 minutes old.'],
 HOURLY_MISSING:['Der er ingen verificerede timekurser.','There are no verified hourly prices.'],
 SIGMA_WINDOW_GAP:['Der mangler timekurser i de seneste 7 døgn, så udsvinget kan ikke beregnes.','Hourly prices are missing in the last 7 days, so volatility cannot be computed.'],
 SIGMA_NOT_POSITIVE:['Udsvinget kan ikke beregnes ud fra de seneste timekurser.','Volatility cannot be computed from the latest hourly prices.'],
 NO_VALID_OFFICIAL_PACKET_24H:['Der er ingen gyldig Kompas-udgave fra de seneste 24 timer.','There is no valid Compass issue from the last 24 hours.'],
 STALE_IN_BROWSER:['Siden har ikke fået nye live-data i over 3 timer.','The page has had no new live data for more than 3 hours.'],
 PRODUCER_ERROR:['Live-beregningen fejlede ved seneste opdatering.','The live computation failed at the latest update.'],
 SOURCE:['Live-data kunne ikke indlæses eller er ugyldige.','Live data could not be loaded or are invalid.']
};
const NONE_REASON={
 PREREG_ABSENT:['Challenger B er ikke registreret endnu, så linjen er flad.','Challenger B is not registered yet, so the line is flat.'],
 PREREG_INVALID:['Challenger B’s registrering kunne ikke læses, så linjen er flad.','Challenger B’s registration could not be read, so the line is flat.'],
 NO_VIEW:['Kompas har ingen gyldig vurdering for perioden.','Compass has no valid reading for the period.'],
 BALANCED:['Kompas’ evidens er i balance for perioden.','Compass evidence is balanced for the period.']
};

function labels(lang,flat){
 return {
  heading:tr(lang,'Kompas live · de næste dage','Compass live · the next days'),
  assetGroup:tr(lang,'Vælg aktiv','Choose asset'),
  hzGroup:tr(lang,'Horisont frem','Horizon ahead'),
  hz:{1:tr(lang,'1 dag','1 day'),3:tr(lang,'3 dage','3 days'),7:tr(lang,'7 dage','7 days')},
  legendTitle:tr(lang,'Signaturforklaring','Legend'),
  legend:{
   actual:tr(lang,'Faktisk kurs','Actual price'),
   line:flat?tr(lang,'Forventet luk · uden hældning','Expected close · no tilt'):
    tr(lang,"live, Challenger B's formel (forsøg)","live, Challenger B's formula (trial)"),
   frames:tr(lang,"live, beregnet hver time med Challenger A's formel","live, calculated hourly using Challenger A's formula"),
   zone:tr(lang,'Frossen ugeprognose','Frozen weekly forecast')
  },
  feedHeading:tr(lang,'Kommentarspor','Comment track'),
  feedPill:tr(lang,'AUTOMATISK','AUTOMATIC'),
  feedSub:tr(lang,'Skrevet af kode ud fra offentlige data. Afstanden er målt mod ugens frosne prognose.',
   'Written by code from public data. Distance is measured against this week’s frozen forecast.'),
  now:tr(lang,'Nu','Now'),
  author:tr(lang,'Automatisk','Automatic'),
  since:tr(lang,'Siden','Since'),
  footer:tr(lang,
   'Statistisk forsøgsvisning, ikke en officiel prognose. '+(flat?
    'Den blå linje er det forventede luk uden hældning; Challenger B (forsøg) er endnu ikke registreret i denne udgave. ':
    'Den blå linje er Challenger B (forsøg): en registreret forskningsmodel, der lader kursbanen hælde efter Kompas’ egne horisonter (1–3 og 5–7 dage). ')+
   'Kompas’ bull/bear er evidenspoint, ikke sandsynligheder. Rammerne beregnes live med Challenger A’s formel (50 %). '+
   'Disse timeberegnede kurver er ikke originale, fastfrosne A/B-udstedelser og må ikke indgå som original score. Kommentarerne er skrevet automatisk af kode. Visningen er ikke en købs- eller salgsanbefaling.',
   'Statistical trial display, not an official forecast. '+(flat?
    'The blue line is the expected close without tilt; Challenger B (trial) is not registered in this build yet. ':
    'The blue line is Challenger B (trial): a registered research model that tilts the path along Compass’s own horizons (1–3 and 5–7 days). ')+
   'Compass bull/bear are evidence points, not probabilities. The frames are calculated live using Challenger A’s formula (50%). '+
   'These hourly-calculated paths are not original frozen A/B issuances and must not be scored as such. Comments are written automatically by code. This display is not a buy or sell recommendation.'),
  unavailableTitle:tr(lang,'Kompas live er midlertidigt utilgængelig','Compass live is temporarily unavailable'),
  unavailableNote:tr(lang,'Der vises ingen kursbane, når data ikke er friske og gyldige.','No price path is shown when data are not fresh and valid.'),
  loading:tr(lang,'Henter live-data …','Loading live data …')
 };
}

function sourceIsValid(json){
 const a=json?.authority;
 return json?.contract===LIVE_CONTRACT&&a?.research_only===true&&a?.official_forecast===false&&
  a?.compass_probability_claim===false&&a?.trading===false&&json?.assets&&typeof json.assets==='object';
}
function validAssetBlock(b){
 return b?.status==='OK'&&finite(b.p0)&&b.p0>0&&Array.isArray(b.points)&&b.points.length>1&&
  Array.isArray(b.days)&&b.days.length>0&&b.headline&&Array.isArray(b.events)&&
  b.days.every(d=>finite(d.centre)&&finite(d.lo)&&finite(d.hi)&&d.lo>0&&d.lo<=d.centre&&d.centre<=d.hi&&Number.isFinite(ms(d.end_utc)));
}
function reasonText(code,lang){
 const key=String(code||'SOURCE').split(':')[0];
 return (UNAVAILABLE_REASON[key]||UNAVAILABLE_REASON.SOURCE)[lang==='en'?1:0];
}

function unavailableModel(base,code,lang){
 return {...base,state:'UNAVAILABLE',reason:String(code||'SOURCE'),
  unavailable:{title:base.labels.unavailableTitle,text:reasonText(code,lang),note:base.labels.unavailableNote},
  price:null,chips:[],headline:null,legend:[],chart:null,feed:[],
  asOf:{text:tr(lang,'Ikke live','Not live'),label:base.labels.unavailableTitle}};
}

function headlineModel(head,asset,lang,flat){
 const when=closePhrase(head.end_weekday,lang);
 const words=[['1_3d','1–3 d'],['5_7d','5–7 d']]
  .filter(([k])=>k==='1_3d'||(head.tilting_views||[]).includes(k))
  .map(([k,l])=>officialWord(head.official_direction?.[k],lang)?l+': '+officialWord(head.official_direction[k],lang):null)
  .filter(Boolean);
 const kompas=words.length?tr(lang,'Kompas ','Compass ')+words.join(' · '):null;
 const model=flat?tr(lang,'Forventet luk uden hældning','Expected close without tilt'):tr(lang,"live, Challenger B's formel (forsøg)","live, Challenger B's formula (trial)");
 const source=[model,kompas].filter(Boolean).join(' · ');
 if(head.direction==='UP'||head.direction==='DOWN'){
  const down=head.direction==='DOWN';
  return {direction:head.direction,tone:down?'down':'up',arrow:down?'↘':'↗',
   title:(down?tr(lang,'Ned mod ca. ','Down toward approx. '):tr(lang,'Op mod ca. ','Up toward approx. '))+formatInt(head.target_display,lang),
   sub:formatPct(head.pct,lang)+' '+when+(STRENGTH[head.strength]?' · '+STRENGTH[head.strength][lang==='en'?1:0]:''),
   source};
 }
 const sub=head.reason==='SMALL_MOVE'?
  formatPct(head.pct,lang)+' '+when+' · '+tr(lang,'for lille til at kalde en retning','too small to call a direction'):
  (NONE_REASON[head.reason]||NONE_REASON.NO_VIEW)[lang==='en'?1:0];
 return {direction:'NONE',tone:'none',arrow:'→',title:tr(lang,'Ingen klar retning','No clear direction'),sub,source};
}

function deviationModel(dev,lang){
 if(!dev||dev.state==='NO_ZONE'||!['BELOW','ABOVE','INSIDE'].includes(dev.state))return {text:'',tone:'none'};
 if(dev.state==='INSIDE')return {text:tr(lang,'inde i prognosen','inside the forecast'),tone:'inside'};
 return dev.state==='BELOW'?
  {text:formatPct(dev.pct,lang)+' '+tr(lang,'under prognosen','below the forecast'),tone:'down'}:
  {text:formatPct(dev.pct,lang)+' '+tr(lang,'over prognosen','above the forecast'),tone:'up'};
}

/**
 * View model for one asset and horizon. `nowMs` is only used for the client-side
 * freshness gate (fail closed in an open tab); all geometry uses the producer clock.
 */
export function liveViewModel(json,{lang='da',hz=3,asset='BTC',nowMs=Date.now(),pending=false}={}){
 lang=lang==='en'?'en':'da';
 hz=LIVE_HORIZONS.includes(Number(hz))?Number(hz):3;
 asset=LIVE_ASSETS.includes(asset)?asset:'BTC';
 const flat=json?.models?.line?.line==='FLAT'||json?.models?.line?.applied===false;
 const L=labels(lang,flat);
 const base={contract:LIVE_CONTRACT,lang,hz,asset,labels:L,
  hzButtons:LIVE_HORIZONS.map(n=>({hz:n,label:L.hz[n],pressed:n===hz})),
  assetButtons:LIVE_ASSETS.map(a=>({asset:a,label:a,pressed:a===asset})),footer:L.footer};
 if(pending&&!json)return {...unavailableModel(base,'SOURCE',lang),state:'LOADING',
  unavailable:{title:L.loading,text:'',note:''},asOf:{text:L.loading,label:L.loading}};
 if(!sourceIsValid(json))return unavailableModel(base,'SOURCE',lang);
 if(json.status==='UNAVAILABLE')return unavailableModel(base,(json.reasons||[])[0]||'SOURCE',lang);
 const a=json.assets[asset];
 if(!a||a.status!=='OK')return unavailableModel(base,a?.reason||'SOURCE',lang);
 if(!validAssetBlock(a))return unavailableModel(base,'SOURCE',lang);
 const asOf=ms(a.as_of_utc),issued=ms(json.generated_at_utc);
 const staleAfter=(json.display_rules?.client_stale_after_minutes??180)*60e3;
 if(!Number.isFinite(asOf)||!Number.isFinite(issued)||nowMs-asOf>staleAfter)
  return unavailableModel(base,'STALE_IN_BROWSER',lang);
 const head=a.headline[String(hz)];
 const hzEnd=ms(json.horizon_end_utc?.[String(hz)]);
 if(!head||!Number.isFinite(hzEnd))return unavailableModel(base,'SOURCE',lang);
 const days=a.days.filter(d=>ms(d.end_utc)<=hzEnd).map(d=>({s:ms(d.start_utc),e:ms(d.end_utc),
  centre:d.centre,lo:d.lo,hi:d.hi,weekday:d.weekday}));
 const zone=a.frozen_zone&&finite(a.frozen_zone.low)&&finite(a.frozen_zone.high)?
  {lo:a.frozen_zone.low,hi:a.frozen_zone.high,ws:ms(json.week?.start_utc),we:ms(json.week?.end_utc)}:null;
 const chips=[];
 if(finite(a.chips?.change_24h_pct))chips.push({key:'24h',text:formatPct(a.chips.change_24h_pct,lang),label:tr(lang,'24 t','24 h'),tone:tone(a.chips.change_24h_pct)});
 if(finite(a.chips?.change_week_pct))chips.push({key:'week',text:formatPct(a.chips.change_week_pct,lang),label:tr(lang,'siden mandag','since Monday'),tone:tone(a.chips.change_week_pct)});
 if(finite(a.daily_move_pct)){
  const level={HIGH:tr(lang,' · højt',' · high'),LOW:tr(lang,' · lavt',' · low')}[a.daily_move_level]||'';
  chips.push({key:'move',text:'± '+numberFormat(lang,1).format(a.daily_move_pct)+(lang==='en'?'%':' %'),
   label:tr(lang,'dagsudsving','daily move')+level,tone:'neutral'});
 }
 const headline=headlineModel(head,asset,lang,flat);
 const nowText=a.events.find(e=>e.kind==='NOW')?.text_by_horizon?.[String(hz)]?.[lang];
 const order={NOW:3,ZONE_BREAK:2,KOMPAS_1_3D_CHANGE:1,WEEK_START:0};
 const feed=a.events.filter(e=>e&&order[e.kind]!==undefined&&Number.isFinite(ms(e.t_utc)))
  .slice().sort((p,q)=>ms(q.t_utc)-ms(p.t_utc)||order[q.kind]-order[p.kind])
  .map(e=>{
   const now=e.kind==='NOW';
   const text=now&&typeof nowText==='string'?nowText:String(e.text?.[lang]||'');
   return {id:String(e.id||''),kind:e.kind,now,when:now?L.now:clock(ms(e.t_utc),lang,{weekday:'short',hour:'2-digit',minute:'2-digit'}),
    deviation:deviationModel(e.deviation,lang),text,author:L.author,
    since:!now&&finite(e.since_pct)?{text:L.since+': '+formatPct(e.since_pct,lang),tone:tone(e.since_pct)}:null};
  });
 const legend=[{key:'actual',label:L.legend.actual},{key:'line',label:L.legend.line},{key:'frames',label:L.legend.frames}];
 if(zone)legend.push({key:'zone',label:L.legend.zone});
 const lastDay=days[days.length-1];
 const timeText=clock(asOf,lang,{hour:'2-digit',minute:'2-digit'});
 const summary=[
  asset+': '+tr(lang,'faktisk kurs de seneste 4 døgn og ','actual price for the last 4 days and ')+
   (flat?tr(lang,'forventet luk uden hældning','expected close without tilt'):tr(lang,'Challenger B (forsøg) forventet luk','Challenger B (trial) expected close'))+
   tr(lang,' for ',' for ')+L.hz[hz]+'.',
  tr(lang,'Kurs nu ','Price now ')+formatInt(a.p0,lang)+' USDT.',
  headline.title+', '+headline.sub+'.',
  lastDay?tr(lang,'Typisk dagsspænd til sidst ','Typical daily span at the end ')+formatInt(lastDay.lo,lang)+'–'+formatInt(lastDay.hi,lang)+'.':'',
  zone?tr(lang,'Ugens frosne prognose ','This week’s frozen forecast ')+formatInt(zone.lo,lang)+'–'+formatInt(zone.hi,lang)+'.':''
 ].filter(Boolean).join(' ');
 return {...base,state:'OK',reason:null,unavailable:null,
  price:{value:a.p0,text:formatInt(a.p0,lang),quote:a.quote||'USDT'},
  asOf:{text:'Live '+timeText,label:tr(lang,'Seneste timekurs kl. ','Latest hourly price at ')+timeText+tr(lang,' dansk tid',' Copenhagen time')},
  chips,headline,legend,feed,
  chart:{now:issued,asOf,p0:a.p0,flat,points:a.points.map(([t,v])=>[ms(t),v]).filter(([t,v])=>Number.isFinite(t)&&finite(v)&&v>0),
   days,zone,lang,summary,target:head.target_display,title:L.heading+' · '+asset}};
}

function niceStep(raw){
 const p=Math.pow(10,Math.floor(Math.log10(raw))),f=raw/p;
 return (f<1.5?1:f<3.5?2:f<7.5?5:10)*p;
}
const fx=v=>Math.round(v*10)/10;

/**
 * SVG description of the chart: {root:{tag,attrs,children}} built only from the view model.
 * Colours come from CSS classes (kompas-live.css), never inline styles.
 */
export function liveChart(model,{width=360}={}){
 const c=model?.chart;
 if(!c||!c.days.length||c.points.length<2)return null;
 const lang=c.lang;
 const Wd=Math.max(300,Math.round(width||0)),Ht=Math.round(Math.max(250,Math.min(340,Wd*.72)));
 const m={l:2,r:60,t:16,b:28},iw=Wd-m.l-m.r,ih=Ht-m.t-m.b;
 const W0=c.now-96*HOUR,W1=c.days[c.days.length-1].e;
 const x=t=>m.l+(t-W0)/(W1-W0)*iw;
 const pts=c.points.filter(([t])=>t>=W0&&t<=W1);
 if(pts.length<2)return null;
 const vals=pts.map(p=>p[1]);
 const zoneVisible=c.zone&&Number.isFinite(c.zone.ws)&&c.zone.ws<W1&&c.zone.we>W0;
 let lo=Math.min(...vals,...c.days.map(d=>d.lo),...(zoneVisible?[c.zone.lo]:[]));
 let hi=Math.max(...vals,...c.days.map(d=>d.hi),...(zoneVisible?[c.zone.hi]:[]));
 const pad=(hi-lo)*.05||lo*.01;lo-=pad;hi+=pad;
 const y=v=>m.t+(1-(v-lo)/(hi-lo))*ih;
 const kids=[];
 const el=(tag,attrs,text)=>{const n={tag,attrs};if(text!=null)n.text=String(text);return n};
 const titleId='cn-live-chart-title',descId='cn-live-chart-desc';
 kids.push(el('title',{id:titleId},c.title),el('desc',{id:descId},c.summary));
 kids.push({tag:'defs',attrs:{},children:[
  {tag:'linearGradient',attrs:{id:'kl-area',x1:0,y1:0,x2:0,y2:1},children:[
   el('stop',{offset:0,class:'kl-area-top'}),el('stop',{offset:1,class:'kl-area-bottom'})]},
  {tag:'linearGradient',attrs:{id:'kl-frost',x1:0,y1:0,x2:0,y2:1},children:[
   el('stop',{offset:0,class:'kl-frost-edge'}),el('stop',{offset:.46,class:'kl-frost-mid'}),el('stop',{offset:1,class:'kl-frost-edge'})]}
 ]});
 const last=pts[pts.length-1],nowY=y(c.p0),end=c.days[c.days.length-1],tgtY=y(end.centre);
 // price grid and right-hand axis labels (hidden where a pill sits)
 const step=niceStep((hi-lo)/4);
 for(let v=Math.ceil(lo/step)*step;v<=hi;v+=step){
  kids.push(el('line',{class:'kl-grid',x1:m.l,x2:m.l+iw,y1:fx(y(v)),y2:fx(y(v))}));
  if(Math.abs(y(v)-nowY)>14&&Math.abs(y(v)-tgtY)>14)
   kids.push(el('text',{class:'kl-axis',x:m.l+iw+8,y:fx(y(v)+4)},formatInt(v,lang)));
 }
 // UTC day separators and weekday labels (thinned on long views)
 const names=DAY_LABEL[lang==='en'?'en':'da'];
 const pxDay=iw*DAY/(W1-W0),stride=pxDay<34?2:1,today=Math.floor(c.now/DAY)*DAY;
 for(let d=Math.floor(W0/DAY)*DAY;d<W1;d+=DAY){
  if(d>W0)kids.push(el('line',{class:'kl-daysep',x1:fx(x(d)),x2:fx(x(d)),y1:m.t,y2:m.t+ih}));
  const a0=Math.max(d,W0),a1=Math.min(d+DAY,W1);
  if(a1-a0<11*HOUR||Math.round((d-today)/DAY)%stride)continue;
  const current=c.now>=d&&c.now<d+DAY;
  kids.push(el('text',{class:current?'kl-day kl-day-now':'kl-day',x:fx(x((a0+a1)/2)),y:Ht-8,'text-anchor':'middle'},names[new Date(d).getUTCDay()]));
 }
 // common thread with Prognose: this week's frozen forecast zone, quiet dashed outline
 if(zoneVisible){
  const zx0=x(Math.max(c.zone.ws,W0)),zx1=x(Math.min(c.zone.we,W1));
  kids.push(el('rect',{class:'kl-zone',x:fx(zx0),y:fx(y(c.zone.hi)),width:fx(zx1-zx0),height:fx(y(c.zone.lo)-y(c.zone.hi))}));
  if(zx1-zx0>90)kids.push(el('text',{class:'kl-zone-label',x:fx(zx0+6),y:fx(y(c.zone.hi)+14)},tr(lang,'Ugens prognose','Weekly forecast')));
 }
 // one frosted frame per UTC day: Challenger A typical (50 %) span around the line
 for(const d of c.days){
  const span=x(d.e)-x(d.s),inset=Math.min(span*.09,8),x0=x(d.s)+inset,x1=x(d.e)-inset,w=x1-x0,top=y(d.hi),h=y(d.lo)-y(d.hi);
  if(w<4)continue;
  kids.push(el('rect',{class:'kl-frame',x:fx(x0),y:fx(top),width:fx(w),height:fx(h),rx:3}));
  kids.push(el('path',{class:'kl-frame-edge',d:'M'+fx(x0+w*.15)+','+fx(top)+'H'+fx(x1-w*.15)+'M'+fx(x0+w*.15)+','+fx(top+h)+'H'+fx(x1-w*.15)}));
 }
 // the line: from the price now through each expected daily close (Challenger B, or flat)
 const line=[[x(c.now),y(c.p0)],...c.days.map(d=>[x(d.e),y(d.centre)])];
 kids.push(el('path',{class:'kl-line',d:line.map((q,i)=>(i?'L':'M')+fx(q[0])+','+fx(q[1])).join('')}));
 for(const q of line.slice(1))kids.push(el('circle',{class:'kl-line-dot',cx:fx(q[0]),cy:fx(q[1]),r:3.6}));
 // actual hourly closes; a missing hour breaks the line (never interpolated)
 const segments=[];let seg=[];
 for(const p of pts){if(seg.length&&p[0]-seg[seg.length-1][0]>HOUR){segments.push(seg);seg=[]}seg.push(p)}
 if(seg.length)segments.push(seg);
 for(const s of segments){
  const pp=s.map(p=>[x(p[0]),y(p[1])]);
  const d=pp.map((q,i)=>(i?'L':'M')+fx(q[0])+','+fx(q[1])).join('');
  if(pp.length>1)kids.push(el('path',{class:'kl-area',d:d+'L'+fx(pp[pp.length-1][0])+','+(m.t+ih)+'L'+fx(pp[0][0])+','+(m.t+ih)+'Z'}));
  kids.push(el('path',{class:'kl-actual',d}));
 }
 const nx=x(last[0]),ny=y(last[1]);
 kids.push(el('line',{class:'kl-now',x1:fx(nx),x2:fx(nx),y1:m.t,y2:m.t+ih}));
 kids.push(el('circle',{class:'kl-now-dot',cx:fx(nx),cy:fx(ny),r:5}));
 kids.push(el('text',{class:'kl-now-label',x:fx(nx),y:m.t-5,'text-anchor':'middle'},tr(lang,'NU','NOW')));
 const pill=(yy,text,cls)=>{const pw=text.length*6.6+12;return [
  el('rect',{class:cls,x:m.l+iw+3,y:fx(yy-10),width:fx(pw),height:20,rx:10}),
  el('text',{class:cls+'-text',x:fx(m.l+iw+3+pw/2),y:fx(yy+4),'text-anchor':'middle'},text)]};
 if(Math.abs(tgtY-ny)>=22&&finite(c.target))kids.push(...pill(tgtY,'≈ '+formatInt(c.target,lang),'kl-pill-target'));
 kids.push(...pill(ny,formatInt(c.p0,lang),'kl-pill-now'));
 return {width:Wd,height:Ht,root:{tag:'svg',attrs:{xmlns:'http://www.w3.org/2000/svg',viewBox:'0 0 '+Wd+' '+Ht,
  class:'kl-svg',role:'img','aria-labelledby':titleId+' '+descId,focusable:'false'},children:kids}};
}

const escapeXml=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
function serialize(n){
 const attrs=Object.entries(n.attrs||{}).map(([k,v])=>' '+k+'="'+escapeXml(v)+'"').join('');
 const inner=(n.text!=null?escapeXml(n.text):'')+(n.children||[]).map(serialize).join('');
 return '<'+n.tag+attrs+(inner?'>'+inner+'</'+n.tag+'>':'/>');
}
/** The same chart as one SVG markup string (tests, static snapshots). */
export function liveChartSvg(model,{width=360}={}){
 const chart=liveChart(model,{width});
 return chart?serialize(chart.root):'';
}
