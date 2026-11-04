/**
 * Kompas PRO · meaningful, source-first freshness readback.
 *
 * Official decision expiry and the age of its own observed price basis are
 * independent. Public hourly delivery may advance without re-issuing the
 * original Official Compass. This file never extends the expiry, creates a
 * trading action or promotes hourly observation into an official reading.
 */
import {currentCompass,expiredOfficial} from './compass-reader.mjs';
import {observedMarketClock} from './compass-overview.mjs';

const tr=(lang,da,en)=>lang==='en'?en:da;
const hour=(utc,lang)=>{
 const ms=Date.parse(utc);
 return Number.isFinite(ms)?new Date(ms).toLocaleTimeString(
  lang==='en'?'en-GB':'da-DK',
  {hour:'2-digit',minute:'2-digit',timeZone:'Europe/Copenhagen'}):null;
};

export function kompasSourceClockReadback({compass,view,lang='da',now=Date.now()}={}){
 const verified=compass?.contract==='PUBLIC_COMPASS_PROJECTION_v1'&&
  compass?.data_status==='OK'&&
  compass.compass_id===view?.compass?.compass_id&&
  compass.weekly_context?.status==='ALIGNED'&&
  compass.weekly_context.forecast_week===view?.weekly?.forecast_week;
 const officialCurrent=currentCompass({compass,view,now});
 const officialExpired=!officialCurrent&&expiredOfficial({compass,view,now});
 const expires=hour(compass?.full_stack?.official_freshness?.valid_until_utc,lang);
 const official=officialCurrent&&expires?
  {status:'CURRENT',tone:'current',label:tr(lang,
   'Kompas-vurdering · gælder til kl. '+expires,
   'Compass outlook · valid until '+expires)}:
  officialExpired&&expires?
  {status:'EXPIRED',tone:'warning',label:tr(lang,
   'Kompas-vurdering · udløb kl. '+expires,
   'Compass outlook · expired at '+expires)}:
  {status:'UNAVAILABLE',tone:'missing',label:tr(lang,
   'Ingen aktuel Kompas-vurdering','No current Compass outlook')};

 const obs=verified?observedMarketClock({compass,now}):
  {state:'OBSERVATION_CLOCK_INVALID'};
 const raw=compass?.market_now?.market_observation_open_utc;
 const open=typeof raw==='string'?Date.parse(raw):NaN;
 const closed=Number.isFinite(open)?open+3600000:NaN;
 const basisTime=Number.isFinite(closed)&&closed<=now?
   hour(new Date(closed).toISOString(),lang):null;
 let observation={status:'UNAVAILABLE',tone:'missing',
  label:tr(lang,'Kompas-måling · intet gyldigt tidspunkt',
    'Compass observation · time not verified')};
 if(obs.state==='FRESH_OBSERVATION'&&basisTime){
  observation={status:'CURRENT',tone:'current',
   label:tr(lang,'Kompas-måling afsluttet kl. '+basisTime,
     'Compass price observation completed '+basisTime)};
 }else if(obs.state==='OBSERVATION_DELAYED'&&basisTime){
  observation={status:'DELAYED',tone:'warning',
   label:tr(lang,'Kompas-måling fra kl. '+basisTime,
     'Compass observation from '+basisTime)};
 }else if(obs.state==='NO_NEW_PRICE_OBSERVATION'&&basisTime){
  observation={status:'NO_NEW_OBSERVATION',tone:'warning',
   label:tr(lang,'Kompas-måling · ingen ny observation',
     'Compass observation · no new reading')};
 }
 // Only source-bound, independently completed hourly metadata can establish
 // that a later Hourly window exists. Its timestamp never refreshes Kompas.
 const health=compass?.public_data_health;
 const end=Date.parse(health?.latest_complete_market_hour_utc);
 const retrieved=Date.parse(health?.hourly_retrieved_at_utc);
 const hourlyAvailable=verified&&
  health?.contract==='CN_PUBLIC_DATA_HEALTH_v1'&&
  health.hourly_status==='COMPLETE'&&
  health.native_data_health==='PASS'&&
  Number.isFinite(end)&&Number.isFinite(retrieved)&&
  end<=retrieved&&retrieved<=now&&end<=now;
 const newerHourly=hourlyAvailable&&Number.isFinite(closed)&&end>closed;
 let explanation=tr(lang,
  'Kun den officielle vurdering styrer handling. Kursgrafen opdateres separat.',
  'Only the official outlook owns action. The price chart updates separately.');
 if(officialCurrent&&observation.status==='DELAYED')explanation=
  newerHourly?tr(lang,
   'Nyere Hourly-data findes, men ændrer ikke Kompas-vurderingen.',
   'Newer Hourly data exist but do not update the Compass outlook.'):
  tr(lang,
   'Kompas bygger på ældre kursdata. Det er ikke en livekurs.',
   'Compass uses older price evidence. This is not a live price.');
 else if(officialCurrent&&observation.status==='CURRENT')explanation=
  tr(lang,'Kompas bruger en nyligt afsluttet kursmåling, ikke en livekurs.',
    'Compass uses a recently completed price observation, not a live price.');
 else if(officialCurrent&&observation.status==='NO_NEW_OBSERVATION')explanation=
  tr(lang,'Ingen ny Kompas-måling. Kursgraf og vurdering er adskilt.',
    'No new Compass observation. The chart and outlook are separate.');
 else if(!officialCurrent)explanation=
  tr(lang,'Tidligere vurderinger må ikke bruges som aktuelle signaler.',
    'Previous readings must not be treated as current signals.');
 const context=officialCurrent?
  observation.status==='DELAYED'&&basisTime?
   tr(lang,'Prisgrundlag fra kl. '+basisTime+' · ældre end 90 min.',
     'Price evidence from '+basisTime+' · over 90 minutes old.'):
  observation.status==='CURRENT'&&basisTime?
   tr(lang,'Prisgrundlag fra kl. '+basisTime+' · afsluttet time.',
     'Price evidence from '+basisTime+' · completed hour.'):
  observation.status==='NO_NEW_OBSERVATION'?
   tr(lang,'Ingen ny verificeret prisobservation i Kompas.',
     'No newly verified Compass price observation.'):
   tr(lang,'Prisgrundlag kan ikke verificeres.','Price evidence cannot be verified.'):
  tr(lang,'Afventer en ny verificeret officiel udgivelse.',
    'Awaiting a new verified official publication.');
 return {
  contract:'CN_KOMPAS_PRO_DUAL_SOURCE_CLOCK_v2',
  official,observation,
  headline:official.label,context,explanation,
  tone:officialCurrent?(observation.status==='DELAYED'?'qualified':'current'):
   officialExpired?'expired':'missing',
  hourlyStatus:hourlyAvailable?(newerHourly?'NEWER_HOURLY_UNBOUND':'HOURLY_AVAILABLE'):'UNAVAILABLE',
  observationStatus:obs.state,
  sourceQuote:'NO_NEW_MARKET_FORECAST'
 };
}
