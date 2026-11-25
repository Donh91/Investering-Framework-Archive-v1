// Readback only. Source-owned descriptive categories, never a browser classifier.
const CONTRACT='CN_CYCLE_PARTICIPATION_READBACK_v1';
const SEMANTICS='OBSERVED_24H_RELATIVE_PERFORMANCE_NOT_CAPITAL_FLOW';
const AUTHORITY='DESCRIPTIVE_ONLY_NO_ACTION_OR_FORECAST';
const BUCKETS=['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY'];
const STATES=['MAJORITY','MINORITY','HALF'];
const stamp=x=>typeof x==='string'&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(x)?Date.parse(x):NaN;
function safeBlock(x){
 if(x?.contract!==CONTRACT||x.semantics!==SEMANTICS||x.authority!==AUTHORITY||
    x.phase!=='UNAVAILABLE'||x.rotation_confirmed!==false||
    !['OBSERVED_PARTICIPATION','PARTIAL_OBSERVATION'].includes(x.status)||
    !['BTC','ETH','TIED'].includes(x.relative_leader))return null;
 const rows={};
 for(const k of BUCKETS){
  const row=x.buckets?.[k];
  if(row?.state==='UNAVAILABLE'){rows[k]={state:'UNAVAILABLE'};continue;}
  const coverage=k==='SMALL_ALT_PROXY'?'TOP100_TAIL_ONLY_NOT_FULL_SMALL_CAP_UNIVERSE':'TOP100_FULL_RANK_WINDOW';
  if(row?.state!=='OBSERVED_PROXY'||row.coverage!==coverage||
     !['advancing','outperforming_btc','outperforming_eth'].every(f=>STATES.includes(row[f])))return null;
  rows[k]={state:row.state,coverage,advancing:row.advancing,outperforming_btc:row.outperforming_btc,outperforming_eth:row.outperforming_eth};
 }
 if(x.buckets?.MICROCAP_PROXY?.state!=='UNAVAILABLE'||x.buckets?.MEMES?.state!=='UNAVAILABLE')return null;
 rows.MICROCAP_PROXY={state:'UNAVAILABLE'};rows.MEMES={state:'UNAVAILABLE'};
 const complete=BUCKETS.every(k=>rows[k].state==='OBSERVED_PROXY');
 if((x.status==='OBSERVED_PARTICIPATION')!==complete)return null;
 return {contract:CONTRACT,semantics:SEMANTICS,authority:AUTHORITY,status:x.status,
  observed_at_utc:x.observed_at_utc,valid_until_utc:x.valid_until_utc,relative_leader:x.relative_leader,buckets:rows,
  phase:'UNAVAILABLE',rotation_confirmed:false};
}
// Builder calls this only after its existing internal/public artifact digest checks.
export function bindParticipation(internal,publicProjection,{verified=false}={}){
 if(!verified||typeof internal?.compass_id!=='string'||!internal.compass_id||
    internal.compass_id!==publicProjection?.compass_id||internal.issued_at_utc!==publicProjection.issued_at_utc)return null;
 const a=safeBlock(internal.cycle_participation), b=safeBlock(publicProjection.cycle_participation);
 if(!a||!b||JSON.stringify(a)!==JSON.stringify(b))return null;
 const observed=stamp(a.observed_at_utc), expiry=stamp(a.valid_until_utc), issued=stamp(internal.issued_at_utc);
 if(![observed,expiry,issued].every(Number.isFinite)||observed>issued||issued>=expiry||expiry-observed!==8*3600000)return null;
 return {contract:'CN_CYCLE_PARTICIPATION_BINDING_v1',status:'VERIFIED_INTERNAL_PUBLIC',compass_id:internal.compass_id,issued_at_utc:internal.issued_at_utc,readback:a};
}
// Native pointer, run and source packet are independently verified by the builder.
export function bindNativeParticipation(native,auto,{verified=false}={}){
 if(!verified||native?.contract!=='NATIVE_HANDLEKOMPAS_v1'||auto?.contract!=='AUTO_MARKET_STATE_PACKET_v1'||
    typeof auto.packet_sha256!=='string'||!/^[0-9a-f]{64}$/.test(auto.packet_sha256)||
    auto.validation_status==='FAIL'||native.source?.packet_sha256!==auto.packet_sha256)return null;
 const a=safeBlock(native.cycle_participation);
 if(!a)return null;
 const observed=stamp(a.observed_at_utc), expiry=stamp(a.valid_until_utc), issued=stamp(native.generated_at_utc), packet=stamp(auto.packet_generated_at_utc);
 if(![observed,expiry,issued,packet].every(Number.isFinite)||observed>packet||packet>issued||issued>=expiry||expiry-observed!==8*3600000)return null;
 return {contract:'CN_CYCLE_PARTICIPATION_BINDING_v1',status:'VERIFIED_NATIVE_AUTO',issued_at_utc:native.generated_at_utc,readback:a};
}
export function readCycleParticipation(latest,compass,{nowUtc=new Date().toISOString()}={}){
 if(latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2'||compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1')return null;
 const native=compass.full_stack?.native_cycle_participation_binding;
 const proof=native??compass.full_stack?.cycle_participation_binding;
 if(compass.full_stack?.native_cycle_participation_emitted===true&&!native)return null;
 if(proof?.contract!=='CN_CYCLE_PARTICIPATION_BINDING_v1')return null;
 const isNative=proof.status==='VERIFIED_NATIVE_AUTO';
 if(isNative){
  if(native!==proof||!['SOURCE_ALIGNED','VERIFIED_NEWER_OR_DIFFERENT_SOURCE'].includes(compass.full_stack?.source_status?.native)||
     proof.issued_at_utc!==compass.full_stack?.native?.checked_at_utc)return null;
 }else if(proof.status!=='VERIFIED_INTERNAL_PUBLIC'||proof.compass_id!==compass.compass_id||
    proof.issued_at_utc!==compass.issued_at_utc)return null;
 const a=safeBlock(isNative?proof.readback:compass.cycle_participation);
 if(!a||JSON.stringify(a)!==JSON.stringify(proof.readback))return null;
 const now=stamp(nowUtc), observed=stamp(a.observed_at_utc), expiry=stamp(a.valid_until_utc),
  issued=stamp(proof.issued_at_utc), delivery=stamp(latest.generated_at);
 if(![now,observed,expiry,issued,delivery].every(Number.isFinite)||observed>issued||issued>delivery||delivery>now||
    now>=expiry||expiry-observed!==8*3600000)return null;
 return a;
}
export const cycleParticipationMarkup='<p class="cn-map-state" id="cn-map-participation" hidden></p><p class="cn-map-caption" id="cn-map-participation-details" hidden></p>';
export function renderCycleParticipation(doc,latest,compass,{lang='da',nowUtc}={}){
 const row=doc.getElementById('cn-map-participation'),details=doc.getElementById('cn-map-participation-details');
 if(!row||!details)return;
 const m=readCycleParticipation(latest,compass,{nowUtc}),en=lang==='en';
 row.hidden=details.hidden=!m;
 row.textContent=details.textContent='';
 if(!m)return;
 const leader=m.relative_leader==='TIED'?(en?'BTC and ETH tied':'BTC og ETH lige'):(en?'24h relative leader: ':'Relativ fører, 24t: ')+m.relative_leader;
 row.textContent=leader+' · '+m.observed_at_utc;
 const labels=en?['Large','Mid','Top-100 tail']:['Store','Mellem','Top-100-hale'];
 const state=en?{MAJORITY:'majority',MINORITY:'minority',HALF:'half'}:{MAJORITY:'flertal',MINORITY:'mindretal',HALF:'halvdelen'};
 details.textContent=BUCKETS.map((k,i)=>labels[i]+': '+(m.buckets[k].state==='OBSERVED_PROXY'?
  state[m.buckets[k].outperforming_btc]+' '+(en?'outperform BTC':'slår BTC'):(en?'unavailable':'utilgængelig'))).join(' · ')+
  (en?' · Micro/memes: unavailable. Observed returns, not capital flow or cycle phase.':' · Micro/memes: utilgængelige. Observeret afkast, ikke kapitalflow eller cyklusfase.');
}
