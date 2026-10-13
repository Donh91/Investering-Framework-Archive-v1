// Research-only independent synthetic oracle for Task 2, no market data or APIs.
// Node 20+. From repository root: node 04_MARKET_LEARNING/handlekompas/research/2026-10-12__task2_synthetic_oracle_v1.mjs
import fs from "node:fs";
import {execFileSync} from "node:child_process";
function audit(frozenVariants) {
  const H=3600000, M=60000, base=Date.UTC(2026,0,1), R={NORMAL:0,BUILDING:1,ELEVATED:2,HIGH:3,CONFIRMED:4};
  const dims=[["ELEVATED","HIGH","CONFIRMED"],[1,2,3,6],[0,1,3],[0,6,24,72]];
  const variants=[];
  for(const s of dims[0])for(const p of dims[1])for(const d of dims[2])for(const c of dims[3])
    variants.push({id:`${s}-P${p}-D${d}-C${c}`,minimum_state:s,persistence_hours:p,delay_hours:d,cooldown_hours:c});
  function ok(b,msg){if(!b)throw Error(msg)}
  ok(variants.length===144 && new Set(variants.map(v=>v.id)).size===144,"grid cardinality");
  if(frozenVariants)ok(JSON.stringify(variants)===JSON.stringify(frozenVariants),"manifest tuples/order mismatch");
  function row(i,state="HIGH",x={}) {
    return {asset:x.asset??"BTCUSDT",observed:base+i*H,known:x.known??(base+i*H+5*M),
      state,status:x.status??"PASS",segment:x.segment??"s1",policy:x.policy??"v1"};
  }
  function validate(rows){
    const prev=new Map(), by=new Map();
    for(const r of rows){
      ok(r.asset&&r.segment&&r.policy&&Number.isFinite(r.observed)&&Number.isFinite(r.known),"missing identity/clock");
      ok(r.observed<=r.known,"future observation");
      if(prev.has(r.asset)){const p=prev.get(r.asset);ok(r.observed>p.observed&&r.known>=p.known,"duplicate/out of order")}
      if(["PASS","OK"].includes(r.status))ok(r.state in R || r.state==="UNKNOWN"||r.state==="UNAVAILABLE","unregistered healthy state");
      prev.set(r.asset,r);
      if(!by.has(r.asset))by.set(r.asset,[]);
      by.get(r.asset).push(r);
    }
    return by;
  }
  function simulate(v,rows,maxAge=15*M){
    ok(Number.isFinite(maxAge)&&maxAge>0,"SOURCE_SPECIFIC_FRESHNESS_CONTRACT_UNRATIFIED");
    const grouped=validate(rows);let alerts=[];
    for(const [asset,raw] of [...grouped].sort((a,b)=>a[0].localeCompare(b[0]))){
      let decisions=[];
      for(const r of raw){const slot=Math.floor(r.known/H);if(decisions.length&&Math.floor(decisions.at(-1).known/H)===slot)decisions[decisions.length-1]=r;else decisions.push(r)}
      let streak=0,ready=null,lastFire=null,last=null;
      for(const r of decisions){
        const slot=Math.floor(r.known/H);
        const continuous=last&&r.observed-last.observed===H&&slot-Math.floor(last.known/H)===1&&r.segment===last.segment&&r.policy===last.policy;
        if(!continuous){streak=0;ready=null}
        if(last&&r.policy!==last.policy)lastFire=null;
        const usable=["PASS","OK"].includes(r.status)&&Object.hasOwn(R,r.state)&&r.known-r.observed>=0&&r.known-r.observed<=maxAge;
        if(!usable||R[r.state]<R[v.minimum_state]){streak=0;ready=null}
        else{
          streak++;
          if(streak===v.persistence_hours)ready=r.known;
          if(ready!==null&&r.known>=ready+v.delay_hours*H&&(lastFire===null||r.known>=lastFire+v.cooldown_hours*H)){
            alerts.push({asset,known:r.known,observed:r.observed});lastFire=r.known;
          }
        }
        last=r;
      }
    }
    return alerts;
  }
  const controls={
    NO_WARNING:Array.from({length:12},(_,i)=>row(i,"NORMAL")),
    CONTINUOUS_HIGH:Array.from({length:12},(_,i)=>row(i,"HIGH")),
    SINGLE_HIGH:[row(0),row(1,"NORMAL"),row(2,"NORMAL")],
    MISSING_HOUR:[row(0),row(2)],
    UNKNOWN_RESET:[row(0),row(1,"UNKNOWN"),row(2)],
    UNAVAILABLE_RESET:[row(0),row(1,"UNAVAILABLE"),row(2)],
    DEGRADED_RESET:[row(0),row(1,"HIGH",{status:"DEGRADED"}),row(2)],
    POLICY_CUTOVER:[row(0),row(1,"HIGH",{policy:"v2"})],
    SEGMENT_CUTOVER:[row(0),row(1,"HIGH",{segment:"s2"})],
    BATCH_SAME_INSTANT:[row(0,"HIGH",{known:base+3*H+5*M}),row(1,"HIGH",{known:base+3*H+5*M}),row(2,"HIGH",{known:base+3*H+5*M})],
    BATCH_SAME_SLOT:[row(0,"HIGH",{known:base+2*H}),row(1,"HIGH",{known:base+2*H+5*M})],
    STALE_TRICKLE:[row(0,"HIGH",{known:base+23*H+5*M}),row(1,"HIGH",{known:base+24*H+5*M})],
    V_RECOVERY:[row(0),row(1),row(2,"NORMAL"),row(3,"NORMAL"),row(4,"NORMAL"),row(5,"NORMAL")],
    MULTI_ASSET:[row(0),row(1),row(0,"HIGH",{asset:"ETHUSDT"}),row(1,"HIGH",{asset:"ETHUSDT"})]
  };
  const counts={}, failCases=[];
  const zeroAll=new Set(["NO_WARNING","STALE_TRICKLE"]);
  const resetP2=new Set(["SINGLE_HIGH","MISSING_HOUR","UNKNOWN_RESET","UNAVAILABLE_RESET","DEGRADED_RESET","POLICY_CUTOVER","SEGMENT_CUTOVER","BATCH_SAME_INSTANT","BATCH_SAME_SLOT"]);
  const ageOverride={BATCH_SAME_INSTANT:240*M,BATCH_SAME_SLOT:180*M};
  for(const [name,rows] of Object.entries(controls)){
    let fired=0,activeVariants=0;
    for(const v of variants){
      const alerts=simulate(v,rows,ageOverride[name]??(15*M));
      fired+=alerts.length;if(alerts.length)activeVariants++;
      if(zeroAll.has(name))ok(alerts.length===0,name+" must have no alerts");
      if(resetP2.has(name)&&v.persistence_hours>=2)ok(alerts.length===0,name+" illegal confirmation");
      if(name.startsWith("BATCH")&&v.persistence_hours===1)ok(alerts.length<=1,name+" duplicate decision alerts");
    }
    counts[name]={tested_variants:variants.length,active_variants:activeVariants,total_synthetic_alerts:fired};
  }
  const expectedP2=variants.find(v=>v.id==="HIGH-P2-D0-C0");
  ok(simulate(expectedP2,controls.CONTINUOUS_HIGH).length===11,"12 consecutive high rows produce 11 cooldown0 P2 observations");
  ok(simulate(expectedP2,controls.V_RECOVERY).length===1,"V recovery P2 one synthetic warning before reclaim");
  const p1=variants.find(v=>v.id==="HIGH-P1-D0-C0");
  ok(simulate(p1,controls.MULTI_ASSET).length===4,"same-time different assets independent per-asset mechanics");
  const invalid=[
    {name:"FUTURE_OBSERVATION",rows:[row(0,"HIGH",{known:base-M})]},
    {name:"DUPLICATE",rows:[row(0),row(0)]},
    {name:"OUT_OF_ORDER",rows:[row(1),row(0)]},
    {name:"UNREGISTERED_LABEL",rows:[row(0,"UNREGISTERED")]},
    {name:"MISSING_POLICY",rows:[row(0,"HIGH",{policy:""})]}
  ];
  for(const test of invalid){let rejected=false;try{simulate(p1,test.rows)}catch(e){rejected=true;}ok(rejected,test.name+" must reject");failCases.push(test.name)}
  let rejected=false;try{simulate(p1,[row(0)],null)}catch(e){rejected=true;}ok(rejected,"missing independent freshness must fail");
  return {contract:"TASK2_INDEPENDENT_SYNTHETIC_ORACLE_v1",research_only:true,
    implementation:"independent deterministic JS oracle; not production Python harness execution",
    grid_cardinality:variants.length,manifest_exact_tuple_match:!!frozenVariants,synthetic_scenarios:Object.keys(controls).length,
    synthetic_variant_case_runs:variants.length*Object.keys(controls).length,
    expected_invalid_cases_rejected:failCases.length+1,scenario_results:counts,
    invalid_negative_controls:[...failCases,"MISSING_FRESHNESS_CONTRACT"],historical_outcome_rows_scored:0,
    information_edge_established:false,economic_edge_established:false,live_trade_authority:false,
    notes:"Alert counts are synthetic mechanics only. V_RECOVERY has no market return or PnL meaning. All fixtures use artificial Jan 2026 hours. No variant chosen."};
}
const inventory=JSON.parse(fs.readFileSync(new URL('./2026-10-13__TASK2_R0_PINNED_PUBLIC_SOURCE_INVENTORY_v1.json',import.meta.url),'utf8'));
const manifestPath='06_RESEARCH_LAB/high_value_edge_research/EDGE-001_TSUNAMI/144_VARIANT_FROZEN_MANIFEST_v1.json';
const binding=inventory.families.flatMap(f=>f.sources).find(s=>s.path===manifestPath);
if(!binding||binding.git_object_type!=='blob')throw Error('FROZEN_MANIFEST_BINDING_MISSING');
const object=execFileSync('git',['rev-parse',inventory.main_commit+':'+manifestPath],{encoding:'utf8'}).trim();
if(object!==binding.git_object_sha||execFileSync('git',['cat-file','-t',object],{encoding:'utf8'}).trim()!=='blob')throw Error('FROZEN_MANIFEST_OBJECT_MISMATCH');
const manifest=JSON.parse(execFileSync('git',['show',object],{encoding:'utf8'}));
console.log(JSON.stringify(audit(manifest.variants),null,2));
