/**
 * KOMPAS · owner-brief presentation readbacks (v2.2b).
 *
 * Pure functions. They only RE-PRESENT fields that the official public bundle
 * already carries and that other Kompas modules already verify:
 *  - importantStatusLine: official issue time/action versus the newer native
 *    check in full_stack.native (typed enums only, no new judgment);
 *  - btcNextDays: today and the next two days from the verified ORIGINAL
 *    frozen 7-day BTC forecast (original-week-price-readback) plus the frozen
 *    week interval from the validated weekly view;
 *  - extraHorizonRows: 0–12 h (observed momentum, from the 14-horizon matrix)
 *    and 4–8 weeks altcoins (key CYCLE_ALTCOINS_3_8W, from the official reader).
 * No fetch, no interpolation, no probability, no new action or price target.
 */
import {currentCompass} from './compass-reader.mjs';

const tr=(lang,da,en)=>lang==='en'?en:da;
const ACTIONS=Object.freeze({
 HOLD_WAIT:['Afvent','Wait'],
 HOLD_WAIT_DATA_DEGRADED:['Afvent · datakvalitet forringet','Wait · data quality degraded']
});
const clock=(utc,lang)=>{
 const ms=Date.parse(utc);
 if(!Number.isFinite(ms))return null;
 return new Date(ms).toLocaleTimeString(lang==='en'?'en-GB':'da-DK',
  {timeZone:'Europe/Copenhagen',hour:'2-digit',minute:'2-digit'});
};
const action=(code,lang)=>ACTIONS[code]?.[lang==='en'?1:0]||null;

export function importantStatusLine({compass,view,lang='da',now=Date.now()}={}){
 if(!currentCompass({compass,view,now}))return null;
 const officialAt=clock(compass.issued_at_utc,lang);
 const officialAction=action(compass.action_now,lang);
 if(!officialAt||!officialAction)return null;
 const parts=[tr(lang,'Officiel udgave ','Official issue ')+officialAt+': '+officialAction+'.'];
 let tone='ok';
 const stack=compass.full_stack;
 const n=stack?.contract==='PUBLIC_COMPASS_FULL_STACK_READBACK_v1'?stack.native:null;
 const checked=Date.parse(n?.checked_at_utc),issued=Date.parse(compass.issued_at_utc);
 const nativeAction=action(n?.now,lang);
 if(nativeAction&&Number.isFinite(checked)&&checked>issued&&checked<=now){
  const notes=[];
  if(n.data_health!=='PASS'&&n.now!=='HOLD_WAIT_DATA_DEGRADED')
   notes.push(tr(lang,'datakvalitet forringet','data quality degraded'));
  if(n.official_source_aligned===false)
   notes.push(tr(lang,'ikke afstemt med officiel udgave','not aligned with the official issue'));
  if(notes.length||n.now!==compass.action_now)tone='warning';
  parts.push(tr(lang,'Nyere kontrol ','Newer check ')+clock(n.checked_at_utc,lang)+': '+
   nativeAction+(notes.length?', '+notes.join(', '):'')+'.');
 }
 parts.push(tr(lang,'Kun den officielle vurdering styrer handlingen.',
  'Only the official outlook owns action.'));
 return {text:parts.join(' '),tone};
}

function isoWeekMondayUtc(week){
 const m=/^(\d{4})-W(\d{2})$/.exec(week||'');
 if(!m)return NaN;
 const year=+m[1],w=+m[2];
 const jan4=Date.UTC(year,0,4);
 const dow=(new Date(jan4).getUTCDay()+6)%7;
 return jan4-dow*86400000+(w-1)*7*86400000;
}

export function btcNextDays({readback,view,nowUtc,lang='da'}={}){
 if(readback?.status!=='SOURCE_ISSUED_BOTH'||readback.quote!=='USDT')return null;
 const days=readback.BTC?.original_daily;
 if(!Array.isArray(days)||days.length!==7)return null;
 const monday=isoWeekMondayUtc(readback.forecast_week);
 const now=Date.parse(nowUtc);
 if(!Number.isFinite(monday)||!Number.isFinite(now))return null;
 const today=Math.floor((now-monday)/86400000)+1;
 if(today<1||today>7)return null;
 const fmt=n=>new Intl.NumberFormat(lang==='en'?'en-US':'da-DK',{maximumFractionDigits:0}).format(n);
 const rows=days.filter(d=>d.day>=today&&d.day<=today+2).map(d=>({
  day:d.day,
  label:(d.day===today?tr(lang,'I dag · ','Today · '):'')+
   new Date(monday+(d.day-1)*86400000).toLocaleDateString(lang==='en'?'en-GB':'da-DK',
    {timeZone:'UTC',weekday:'short',day:'numeric',month:'short'}),
  range:fmt(d.low)+'–'+fmt(d.high)+' USDT',
  close:tr(lang,'forventet luk ','expected close ')+fmt(d.expected_close)
 }));
 const wk=view?.weekly;
 const r=wk?.forecast_week===readback.forecast_week&&['OK','DEGRADED'].includes(wk.state)?wk.btc_range:null;
 const week=Number.isFinite(r?.low)&&Number.isFinite(r?.high)&&r.low>0&&r.high>r.low?
  fmt(r.low)+'–'+fmt(r.high)+' USDT':null;
 return {
  week:readback.forecast_week,rows,weekRange:week,
  caption:tr(lang,'Oprindeligt frosset '+readback.forecast_week+
   ' · prognose, ikke realiserede kurser · dagens lav/høj pr. UTC-døgn',
   'Originally frozen '+readback.forecast_week+
   ' · forecast, not realised prices · daily low/high per UTC day')
 };
}

export function extraHorizonRows({matrix,reading,lang='da'}={}){
 const h12=matrix?.rows?.find(x=>x.id==='H0_12H');
 return {
  h12:h12?{direction:h12.value,position:tr(lang,'Måling, ikke prognose','Observation, not a forecast'),tone:h12.tone}:
   {direction:tr(lang,'Afventer gyldig kilde','Awaiting verified source'),position:'—',tone:'missing'},
  c38:reading?{direction:reading.direction,position:reading.posture,
   tone:reading.hasDirection?'mixed':'missing'}:
   {direction:tr(lang,'Afventer gyldig kilde','Awaiting verified source'),position:'—',tone:'missing'}
 };
}
