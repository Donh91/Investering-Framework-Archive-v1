/**
 * Kompas PRO · two independent source clocks, presentation only.
 * This must never refresh/extend an Official decision or issue new momentum.
 */
import {currentCompass,expiredOfficial} from './compass-reader.mjs';
import {observedMarketClock} from './compass-overview.mjs';

const tr=(lang,da,en)=>lang==='en'?en:da;
const at=(iso,lang)=>{
 const ms=Date.parse(iso);
 return Number.isFinite(ms)?new Date(ms).toLocaleTimeString(lang==='en'?'en-GB':'da-DK',
  {hour:'2-digit',minute:'2-digit',timeZone:'Europe/Copenhagen'}):null;
};

export function kompasSourceClockReadback({compass,view,lang='da',now=Date.now()}={}){
 const officialCurrent=currentCompass({compass,view,now});
 const officialExpired=!officialCurrent&&expiredOfficial({compass,view,now});
 const until=at(compass?.full_stack?.official_freshness?.valid_until_utc,lang);
 const official=officialCurrent&&until?
  {status:'CURRENT',tone:'current',label:tr(lang,
   'Officielt Kompas · gyldigt til '+until,'Official Compass · valid until '+until)}:
  officialExpired&&until?
  {status:'EXPIRED',tone:'warning',label:tr(lang,
   'Officielt Kompas · udløb '+until,'Official Compass · expired '+until)}:
  {status:'UNAVAILABLE',tone:'missing',label:tr(lang,
   'Officielt Kompas · ikke aktuelt','Official Compass · unavailable')};
 // A current site bundle is not evidence of an independently fresh market candle.
 const sourceAligned=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
  compass?.data_status==='OK'&&
  compass.compass_id===view?.compass?.compass_id&&
  compass.weekly_context?.status==='ALIGNED'&&
  compass.weekly_context.forecast_week===view?.weekly?.forecast_week;
 const obs=sourceAligned?observedMarketClock({compass,now}):
   {state:'OBSERVATION_CLOCK_INVALID'};
 let observation={status:'UNAVAILABLE',tone:'missing',
   label:tr(lang,'Prisobservation · ingen gyldig kilde','Price observation · no valid source')};
 if(obs.state==='FRESH_OBSERVATION'){
  const open=Date.parse(compass.market_now.market_observation_open_utc);
  const completed=at(new Date(open+3600000).toISOString(),lang);
  if(completed)observation={status:'CURRENT',tone:'current',
   label:tr(lang,'Afsluttet timekurs · '+completed,'Completed hourly close · '+completed)};
 }else if(obs.state==='OBSERVATION_DELAYED'){
  observation={status:'DELAYED',tone:'warning',
   label:tr(lang,'Prisobservation · forsinket','Price observation · delayed')};
 }else if(obs.state==='NO_NEW_PRICE_OBSERVATION'){
  observation={status:'NO_NEW_OBSERVATION',tone:'warning',
   label:tr(lang,'Prisobservation · ingen ny måling','Price observation · no new reading')};
 }
 return {contract:'CN_KOMPAS_PRO_DUAL_SOURCE_CLOCK_v1',official,observation};
}
