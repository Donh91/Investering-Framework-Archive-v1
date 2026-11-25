// Readback only. Source-owned descriptive categories, never a browser classifier.
const CONTRACT='CN_CYCLE_PARTICIPATION_READBACK_v1';
const SEMANTICS='OBSERVED_24H_RELATIVE_PERFORMANCE_NOT_CAPITAL_FLOW';
const AUTHORITY='DESCRIPTIVE_ONLY_NO_ACTION_OR_FORECAST';
const BUCKETS=['LARGE_ALT_PROXY','MID_ALT_PROXY','SMALL_ALT_PROXY'];
const STATES=['MAJORITY','MINORITY','HALF'];
const ORDER={MINORITY:0,HALF:1,MAJORITY:2};
// Same constituents: a harder benchmark cannot have a larger outperforming share.
function relativeConsistent(leader,row){
 const btc=ORDER[row.outperforming_btc],eth=ORDER[row.outperforming_eth];
 return leader==='ETH'?btc>=eth:leader==='BTC'?eth>=btc:btc===eth;
}
const stamp=x=>{
 if(typeof x!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z$/.test(x))return NaN;
 const ms=Date.parse(x);
 // Date.parse normalizes some impossible calendar dates and 24:00.
 return Number.isFinite(ms)&&new Date(ms).toISOString().slice(0,19)===x.slice(0,19)?ms:NaN;
};
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
     !['advancing','outperforming_btc','outperforming_eth'].every(f=>STATES.includes(row[f]))||
     !relativeConsistent(x.relative_leader,row))return null;
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
 const stack=compass.full_stack,proof=stack?.native_cycle_participation_binding;
 if(proof?.contract!=='CN_CYCLE_PARTICIPATION_BINDING_v1'||proof.status!=='VERIFIED_NATIVE_AUTO'||
    !['SOURCE_ALIGNED','VERIFIED_NEWER_OR_DIFFERENT_SOURCE'].includes(stack?.source_status?.native)||
    proof.issued_at_utc!==stack?.native?.checked_at_utc)return null;
 const a=safeBlock(proof.readback);
 if(!a)return null;
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
  state[m.buckets[k].outperforming_btc]+' '+(en?'outperform BTC':'slår BTC')+', '+
  state[m.buckets[k].outperforming_eth]+' '+(en?'outperform ETH':'slår ETH')+', '+
  state[m.buckets[k].advancing]+' '+(en?'advancing':'stiger'):(en?'unavailable':'utilgængelig'))).join(' · ')+
  (en?' · Top-100 tail is not the full small-cap universe. Micro/memes: unavailable. Observed returns, not capital flow or cycle phase. Rotation sequence unverified.':
      ' · Top-100-halen dækker ikke hele small-cap-universet. Micro/memes: utilgængelige. Observeret afkast, ikke kapitalflow eller cyklusfase. Rotationssekvens ikke verificeret.');
}

function safeAlt(x){
 if(x?.contract!=='CN_ALTSEASON_OBSERVATION_v1'||x.source!=='BLOCKCHAINCENTER_90D'||
    x.authority!=='CONTEXT_ONLY_NO_TRANSITION_OR_ETA'||
    !['OBSERVED','CARRIED_NOT_FRESH'].includes(x.status)||
    !['ALTCOIN_SEASON','BITCOIN_SEASON','BETWEEN_PUBLISHED_THRESHOLDS'].includes(x.state))return null;
 const observed=stamp(x.observed_at_utc),expiry=stamp(x.valid_until_utc);
 if(!Number.isFinite(observed)||!Number.isFinite(expiry)||
    expiry-observed!==(x.status==='OBSERVED'?24:72)*3600000)return null;
 return {contract:x.contract,source:x.source,authority:x.authority,status:x.status,state:x.state,
  observed_at_utc:x.observed_at_utc,valid_until_utc:x.valid_until_utc};
}
export function bindNativeAltseason(native,auto,{verified=false}={}){
 if(!verified||native?.contract!=='NATIVE_HANDLEKOMPAS_v1'||auto?.contract!=='AUTO_MARKET_STATE_PACKET_v1'||
    auto.validation_status==='FAIL'||typeof auto.packet_sha256!=='string'||!/^[0-9a-f]{64}$/.test(auto.packet_sha256)||
    native.source?.packet_sha256!==auto.packet_sha256)return null;
 const a=safeAlt(native.altseason_readback);
 if(!a)return null;
 const obs=stamp(a.observed_at_utc),exp=stamp(a.valid_until_utc),issued=stamp(native.generated_at_utc),packet=stamp(auto.packet_generated_at_utc);
 if(![obs,exp,issued,packet].every(Number.isFinite)||obs>packet||packet>issued||issued>=exp)return null;
 return {contract:'CN_ALTSEASON_NATIVE_BINDING_v1',status:'VERIFIED_NATIVE_AUTO',issued_at_utc:native.generated_at_utc,readback:a};
}
export function readAltseason(latest,compass,{nowUtc=new Date().toISOString()}={}){
 if(latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2'||compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1')return null;
 const stack=compass.full_stack,p=stack?.native_altseason_binding;
 if(p?.contract!=='CN_ALTSEASON_NATIVE_BINDING_v1'||p.status!=='VERIFIED_NATIVE_AUTO'||
    !['SOURCE_ALIGNED','VERIFIED_NEWER_OR_DIFFERENT_SOURCE'].includes(stack?.source_status?.native)||
    p.issued_at_utc!==stack?.native?.checked_at_utc)return null;
 const a=safeAlt(p.readback);
 if(!a)return null;
 const now=stamp(nowUtc),obs=stamp(a.observed_at_utc),exp=stamp(a.valid_until_utc),issued=stamp(p.issued_at_utc),delivery=stamp(latest.generated_at);
 if(![now,obs,exp,issued,delivery].every(Number.isFinite)||obs>issued||issued>delivery||delivery>now||now>=exp)return null;
 return a;
}
export function altseasonDisplay(latest,compass,{lang='da',nowUtc}={}){
 const a=readAltseason(latest,compass,{nowUtc}),en=lang==='en';
 const label=en?{'ALTCOIN_SEASON':'Altcoin season','BITCOIN_SEASON':'Bitcoin season','BETWEEN_PUBLISHED_THRESHOLDS':'Between thresholds'}:
  {'ALTCOIN_SEASON':'Altcoin-sæson','BITCOIN_SEASON':'Bitcoin-sæson','BETWEEN_PUBLISHED_THRESHOLDS':'Mellem tærskler'};
 return {title:en?'Altseason watch':'Altseason Watch',
 subtitle:en?'BlockchainCenter 90d · context only':'BlockchainCenter 90d · kun kontekst',
 eta:en?'No verified ETA':'Ingen verificeret ETA',
 state:a?label[a.state]+' · '+(a.status==='CARRIED_NOT_FRESH'?(en?'carried, not fresh':'videreført, ikke frisk'):(en?'observed':'observeret'))+' · '+a.observed_at_utc:
  (en?'Source observation unavailable':'Kildeobservation utilgængelig'),
 panel:a&&a.status==='OBSERVED'?'observed':'unverified'};
}
