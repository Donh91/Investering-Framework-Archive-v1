/* Cycle Navigator Forward Outlook, read-only prospective source projection.
 * There is no simulated price path, market-state engine or trade authority.
 * Every displayed statement must originate in existing first-party public,
 * prospective source-bound and hash-verified owner readback. */
const DIRECTIONS=new Set(['UP','DOWN','SIDEWAYS','MIXED','NO_EDGE']);
const ALLOWED_CONF=new Set(['LOW','MEDIUM','HIGH','UNKNOWN']);
const safe=v=>typeof v==='string'&&v.length<=650&&!/\d|[$%]|https?:|wallet|secret|address|0x[0-9a-f]{8}/i.test(v)?v.trim():null;
const direction=v=>DIRECTIONS.has(v)?v:'UNAVAILABLE';
const empty=()=>({contract:'CN_PUBLIC_FORWARD_OUTLOOK_v1',status:'UNAVAILABLE',
 weekly:{direction:'UNAVAILABLE',summary:null},
 strategic:{available:false,direction:'UNAVAILABLE',btc_direction:'UNAVAILABLE',
  eth_direction:'UNAVAILABLE',confidence:'UNKNOWN',summary:null,issued_at_utc:null,
  expected_path:null,scenarios:[],falsifiers:[]},price_path_status:'NOT_ISSUED'});
export function forwardOutlook(latest,compass,trace){
 const out=empty();
 const cp=latest?.public_series?.current_public_projection;
 const wc=compass?.weekly_context;
 const f=compass?.full_stack;
 if(latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2'||compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'||
    f?.contract!=='PUBLIC_COMPASS_FULL_STACK_READBACK_v1'||
    trace?.contract!=='CN_PREMIUM_SOURCE_TRACE_v1'||trace.status==='UNVERIFIED'||
    !cp?.forecast_week||cp.forecast_week!==wc?.forecast_week||
    cp.public_issue_number!==wc?.public_issue_number)return out;
 const w=trace.long_horizons?.find(x=>x.id==='2_3w');
 if(w?.owner==='CYCLE_NAVIGATOR_WEEKLY'&&
    f.source_status?.cycle_navigator==='WEEKLY_POINTER_ALIGNED'){
   out.weekly.direction=direction(w.direction);
   out.weekly.summary=safe(f.weekly?.summary_2_3w);
 }
 const s=trace.long_horizons?.find(x=>x.id==='21_30d');
 const sc=f.strategic;
 const when=Date.parse(sc?.issued_at_utc);
 if(s?.owner==='CYCLE_NAVIGATOR_STRATEGIC_CONTEXT'&&
    s.direction!=='UNAVAILABLE'&&f.source_status?.strategic==='BOUND_WEEKLY_ANCHOR'&&
    sc?.status==='BOUND_WEEKLY_ANCHOR'&&
    sc?.authority==='CYCLE_NAVIGATOR_OWNED_NOT_NEW_SITE_FORECAST'&&
    Number.isFinite(when)&&when<=Date.now()){
    const h=sc.horizon_21_30d;
    out.strategic={available:true,direction:direction(s.direction),
     btc_direction:direction(h?.btc_direction),eth_direction:direction(h?.eth_direction),
     confidence:ALLOWED_CONF.has(h?.confidence)?h.confidence:'UNKNOWN',
     summary:safe(h?.summary),issued_at_utc:sc.issued_at_utc,
     expected_path:safe(h?.expected_path),
     scenarios:Array.isArray(h?.scenarios)?h.scenarios.filter(v=>['BASE','BULL','BEAR'].includes(v?.label)&&safe(v?.thesis)).
      slice(0,3).map(v=>({label:v.label,thesis:safe(v.thesis)})):[],
     falsifiers:Array.isArray(h?.falsifiers)?h.falsifiers.map(safe).filter(Boolean).slice(0,3):[]};
 }
 out.status=out.strategic.available||out.weekly.direction!=='UNAVAILABLE'?'FROZEN_CONTEXT_ONLY':'UNAVAILABLE';
 return out;
}
