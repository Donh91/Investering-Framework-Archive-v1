/**
 * KOMPAS PRO · source-owned original 7-day BTC + ETH price summary.
 *
 * Read-only consumer of the SAME canonical Graph B adapter and release
 * lineage. Absolutely no inferred target, new forecast, quote conversion,
 * source promotion, mathematical path drawing or trading authorization.
 *
 * The Monday forecast's validity must NOT depend on whether a separate
 * green hourly observation is more than 90 minutes old.
 */
import {readOfficialGraphB} from './graph-b/official-source-adapter.mjs';

const empty=(reason)=>({
 contract:'CN_KOMPAS_PRO_ORIGINAL_WEEK_PRICE_READBACK_v1',
 status:'UNAVAILABLE',
 source_reason:reason,
 forecast_week:null,
 public_issue_number:null,
 BTC:null,
 ETH:null,
 frozen_at_utc:null,
 quote:null,
 official_action_authority:false,
 forecast_issued_by_this_consumer:false
});

export function verifiedOriginalWeekPrices({
 latest,publicationLineage,nowUtc
}={}){
 if(publicationLineage?.contract!=='CN_PUBLICATION_LINEAGE_RELEASE_RECEIPT_v1')
   return empty('ORIGINAL_PUBLIC_LINEAGE_NOT_AVAILABLE');
 if(typeof nowUtc!=='string'||!Number.isFinite(Date.parse(nowUtc)))
   return empty('AS_OF_CLOCK_INVALID');
 const models={};
 for(const asset of ['BTC','ETH']){
  const original=readOfficialGraphB(latest,asset,{
   now_utc:nowUtc,publication_lineage:publicationLineage
  });
  if(original.source_status!=='SOURCE_BOUNDED')
    return empty(asset+'_SOURCE_'+(original.source_reason||'UNAVAILABLE'));
  if(original.publication_lineage_status!=='MATCHED')
    return empty(asset+'_PUBLIC_LINEAGE_NOT_MATCHED');
  if(original.forecast_status!=='SOURCE_ISSUED'||
      original.daily_range_status!=='SOURCE_ISSUED'||
      original.forecast.length!==7||
      original.daily_ranges.length!==7)
    return empty(asset+'_NO_ELIGIBLE_ORIGINAL_SEVEN_DAYS');
  if(original.forecast_comparison_quote_status!=='SAME_DECLARED_UNIT'||
      original.actual_quote_unit!=='USDT'||
      original.forecast_declared_quote_unit!=='USDT')
    return empty(asset+'_NO_COMPARABLE_USDT_QUOTE');
  if(original.forecast_week!==publicationLineage.forecast_week||
      original.public_issue_number!==publicationLineage.public_issue_number)
    return empty(asset+'_WEEK_OR_ISSUE_IDENTITY_MISMATCH');
  if(!original.forecast.every((x,i)=>{
     const range=original.daily_ranges[i];
     return x.day===i+1&&range.day===i+1&&
       x.low===range.low&&x.high===range.high&&
       x.low<=x.expected_close&&x.expected_close<=x.high;
   }))return empty(asset+'_DAILY_BOUNDS_MISMATCH');
  const closes=original.forecast.map(x=>x.expected_close);
  const lows=original.daily_ranges.map(x=>x.low);
  const highs=original.daily_ranges.map(x=>x.high);
  models[asset]=Object.freeze({
    original_expected_closes:7,
    original_low_high_days:7,
    expected_first_daily_close:closes[0],
    expected_last_daily_close:closes[6],
    week_daily_low_min:Math.min(...lows),
    week_daily_high_max:Math.max(...highs),
    // The SAME verified original 7 points (no interpolation, no new values),
    // exposed so Kompas can show today and the next two source-issued days.
    original_daily:Object.freeze(original.forecast.map(x=>Object.freeze({
      day:x.day,low:x.low,high:x.high,expected_close:x.expected_close}))),
    last_observed_at_utc:original.last_observed_at_utc,
    actual_price_freshness:original.live_freshness,
    price_quote:'USDT'
  });
 }
 const {BTC,ETH}=models;
 const snapshotWeek=latest?.public_live_precision?.forecast_week;
 const sourceFreeze=latest?.public_live_precision?.frozen_at_utc;
 if(!sourceFreeze||!Number.isFinite(Date.parse(sourceFreeze))||
    snapshotWeek!==publicationLineage.forecast_week)
   return empty('FROZEN_SOURCE_IDENTITY_UNAVAILABLE');
 return {
   contract:'CN_KOMPAS_PRO_ORIGINAL_WEEK_PRICE_READBACK_v1',
   status:'SOURCE_ISSUED_BOTH',
   source_reason:null,
   forecast_week:snapshotWeek,
   public_issue_number:publicationLineage.public_issue_number,
   BTC,ETH,
   frozen_at_utc:sourceFreeze,
   quote:'USDT',
   // Never conflate source-issued price with Official daily action.
   official_action_authority:false,
   forecast_issued_by_this_consumer:false
 };
}

export function originalWeekPriceLabel(readback,{lang='da'}={}){
 if(readback?.status!=='SOURCE_ISSUED_BOTH'||!readback.BTC||!readback.ETH)
   return null;
 const fmt=n=>new Intl.NumberFormat(lang==='en'?'en-US':'da-DK',{
  maximumFractionDigits:2
 }).format(n);
 const btc=readback.BTC,eth=readback.ETH;
 // No invented confidence, trajectory, current price, or daily values.
 return lang==='en'?
  'Originally frozen '+readback.forecast_week+' · BTC Sunday close '+fmt(btc.expected_last_daily_close)+
  ' USDT, daily low/high span '+fmt(btc.week_daily_low_min)+'–'+fmt(btc.week_daily_high_max)+
  ' · ETH Sunday close '+fmt(eth.expected_last_daily_close)+' USDT':
  'Oprindeligt frosset '+readback.forecast_week+' · BTC søndagsluk '+
  fmt(btc.expected_last_daily_close)+' USDT, dags-low/high samlet '+
  fmt(btc.week_daily_low_min)+'–'+fmt(btc.week_daily_high_max)+
  ' · ETH søndagsluk '+fmt(eth.expected_last_daily_close)+' USDT';
}
