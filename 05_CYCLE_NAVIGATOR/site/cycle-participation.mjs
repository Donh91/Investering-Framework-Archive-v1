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
export const cycleParticipationMarkup='<p class="cn-map-state" id="cn-map-participation" hidden></p><p class="cn-map-caption" id="cn-map-participation-details" hidden></p><p class="cn-map-caption" id="cn-map-t6-research" hidden></p>';
export function renderCycleParticipation(doc,latest,compass,{lang='da',nowUtc}={}){
 const research=doc.getElementById('cn-map-t6-research');
 if(research){research.textContent=t6ResearchDisplay(latest,compass,{lang,nowUtc});research.hidden=!research.textContent;}
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

// T6 is a research observation owner, never a live phase or rotation classifier.
// The builder verifies the original canonical bytes including Python float spelling.
const T6_ROOT='research/framework_memory/rotation_survival_forward_rows/';
const T6_EVENTS=['NO_ELIGIBLE_FIRST_CROSS','FIRST_CROSS_FROZEN','ACTIVE_SEQUENCE_OBSERVATION','ETHBTC_REVERSAL_OBSERVED'];
const T6_AUTH={binding:false,market_interpretation:'NONE',canonical_acceptance:false,state_change:false,portfolio_action:false,market_threshold_change:false,model_weight_change:false,research_only:true};
const t6Authority=x=>x&&Object.keys(x).length===Object.keys(T6_AUTH).length&&Object.entries(T6_AUTH).every(([k,v])=>x[k]===v);
const t6Sequence=x=>typeof x==='string'&&/^T6-[a-f0-9]{16}$/.test(x);
export function t6ObservationPath(p){
 const path=p?.observation_path;
 if(p?.contract!=='ROTATION_SURVIVAL_LATEST_v1'||typeof path!=='string'||!path.startsWith(T6_ROOT+'observations/')||
    !/^\d{4}-\d\d-\d\d_[a-f0-9]{20}\.json$/.test(path.slice((T6_ROOT+'observations/').length))||
    !Number.isFinite(stamp(p.observed_at_utc))||path.slice((T6_ROOT+'observations/').length,(T6_ROOT+'observations/').length+10)!==p.observed_at_utc.slice(0,10))return null;
 return path;
}
export function bindT6Observation(pointer,observation,digest,{nowUtc=new Date().toISOString()}={}){
 const p=pointer,o=observation;
 if(!t6ObservationPath(p)||typeof digest!=='string'||!/^[a-f0-9]{64}$/.test(digest)||p.observation_sha256!==digest||
    o?.contract!=='ROTATION_SURVIVAL_OBSERVATION_v1'||!t6Authority(p.authority)||!t6Authority(o.authority)||
    !T6_EVENTS.includes(p.event)||o.event!==p.event||o.observed_at_utc!==p.observed_at_utc||
    o.retrospective_creation!==false||typeof o.first_cross_detected!=='boolean'||
    !/^[a-f0-9]{64}$/.test(o.source_packet_sha256||''))return null;
 const now=stamp(nowUtc),at=stamp(o.observed_at_utc);
 if(!Number.isFinite(now)||!Number.isFinite(at)||at>now)return null;
 if(p.event==='NO_ELIGIBLE_FIRST_CROSS'){
  if(p.active_sequence_id!==null||o.active_sequence_id_before!==null||o.first_cross_detected!==false||o.right_censored!==true||'sequence_id' in o||'time_in_state_days' in o)return null;
 }else if(p.event==='FIRST_CROSS_FROZEN'){
  if(!t6Sequence(p.active_sequence_id)||o.active_sequence_id_before!==null||o.first_cross_detected!==true||
     'sequence_id' in o||'time_in_state_days' in o||'right_censored' in o)return null;
 }else{
  const active=p.event==='ACTIVE_SEQUENCE_OBSERVATION';
  if(!t6Sequence(o.sequence_id)||o.active_sequence_id_before!==o.sequence_id||
     p.active_sequence_id!==(active?o.sequence_id:null)||o.right_censored!==active||
     (o.first_cross_detected&&!active)||
     typeof o.time_in_state_days!=='number'||!Number.isFinite(o.time_in_state_days)||o.time_in_state_days<0)return null;
 }
 return {contract:'CN_T6_RESEARCH_READBACK_v1',authority:'RESEARCH_HISTORY_ONLY_NO_PHASE_ROTATION_ETA_OR_ACTION',
         event:p.event,observed_at_utc:o.observed_at_utc};
}
export function t6ResearchDisplay(latest,compass,{lang='da',nowUtc=new Date().toISOString()}={}){
 const en=lang==='en',r=compass?.full_stack?.t6_research_observation;
 if(latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2'||compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'||
    r?.contract!=='CN_T6_RESEARCH_READBACK_v1'||r.authority!=='RESEARCH_HISTORY_ONLY_NO_PHASE_ROTATION_ETA_OR_ACTION'||
    !T6_EVENTS.includes(r.event))return '';
 const at=stamp(r.observed_at_utc),delivery=stamp(latest.generated_at),now=stamp(nowUtc);
 if(![at,delivery,now].every(Number.isFinite)||at>delivery||delivery>now)return '';
 const labels=en?{NO_ELIGIBLE_FIRST_CROSS:'No eligible first cross recorded',FIRST_CROSS_FROZEN:'First cross recorded',ACTIVE_SEQUENCE_OBSERVATION:'Sequence observation recorded',ETHBTC_REVERSAL_OBSERVED:'ETH/BTC reversal recorded'}:
 {NO_ELIGIBLE_FIRST_CROSS:'Intet kvalificeret første kryds registreret',FIRST_CROSS_FROZEN:'Første kryds registreret',ACTIVE_SEQUENCE_OBSERVATION:'Sekvensobservation registreret',ETHBTC_REVERSAL_OBSERVED:'ETH/BTC-reversering registreret'};
 return (en?'Last recorded T6 research observation: ':'Senest registrerede T6-forskningsobservation: ')+labels[r.event]+' · '+r.observed_at_utc+
  (en?' · Historical observation, not current rotation confirmation or forecast.':' · Historisk observation, ikke aktuel rotationsbekræftelse eller prognose.');
}
