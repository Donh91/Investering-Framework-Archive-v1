/**
 * SOURCE-ONLY Official Compass / PATH product adapter, not a model.
 * Only accepted original fields and current expiry readback may affect UI.
 * No synthesized BUY/SELL, market probabilities, horizon ETA or rotation.
 */
const HORIZONS=['NEXT_12H','NEXT_1_3D','NEXT_5_7D','NEXT_2_3W','CYCLE_ALTCOINS_3_8W'];
const TIERS=['BTC','ETH','LARGE_CAPS','MID_CAPS','SMALL_CAPS','MICROCAPS','MEMES'];
const PHASES=[
 'BTC leadership','ETH leadership','Large + Mid rotation','Altseason ignition',
 'Micro acceleration','Broad altseason','Mania / euphoria',
 'Distribution','Exit / protection','Cooldown / re-entry'
];
const iso=s=>typeof s==='string'?Date.parse(s):NaN;
const nullModel=reason=>({contract:'CN_PREMIUM_V2_COMPASS_PATH_UI_v1',status:'UNAVAILABLE',
 reason,official_action:null,official_action_current:false,horizons:[],
 capitalization_ladder:[],bull_bear:null,path_phases:PHASES,
 path_current_phase:'UNAVAILABLE',path_next_gate:null,rotation_confirmed:false,
 price_source_current:false,probability_model:false,decision_authority:false});
export function readOfficialCompassPath(compass,latest,{now_utc}={}){
 const bad=reason=>nullModel(reason);
 const now=iso(now_utc);
 if(!Number.isFinite(now))return bad('CLOCK_UNVERIFIED');
 if(compass?.contract!=='PUBLIC_COMPASS_PROJECTION_v1'||
    latest?.schema!=='CN_PUBLIC_SNAPSHOT_V2')return bad('PUBLIC_CONTRACT_UNVERIFIED');
 const issued=iso(compass.issued_at_utc);
 if(!Number.isFinite(issued)||issued>now||compass.data_status!=='OK')
  return bad('OFFICIAL_ISSUE_OR_STATUS_UNAVAILABLE');
 const freshness=compass.full_stack?.official_freshness;
 const source=iso(freshness?.source_asof_utc),validTo=iso(freshness?.valid_until_utc);
 if(freshness?.contract!=='OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1'||
    freshness.status!=='VERIFIED_OWNER_POLICY'||
    !Number.isFinite(source)||!Number.isFinite(validTo)||validTo<=source||
    source>issued||validTo<issued)return bad('OFFICIAL_SOURCE_FRESHNESS_UNVERIFIED');
 if(typeof compass.action_now!=='string'||!['HOLD_WAIT','HOLD','WAIT','BUY','SELL','HARD_WAIT','UNAVAILABLE'].includes(compass.action_now))
   return bad('UNRECOGNIZED_OFFICIAL_ACTION');
 const hs=compass.horizons||{},ladder=compass.capitalization_ladder;
 if(!HORIZONS.every(k=>hs[k]&&typeof hs[k].expected_direction==='string')||
    !Array.isArray(ladder)||ladder.length!==7||
    !TIERS.every((k,i)=>ladder[i]?.segment===k))return bad('FIVE_HORIZON_SEVEN_TIER_CONTRACT_MISMATCH');
 const scale=compass.bull_bear_scale;
 const gauge=scale?.contract==='OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1'&&
   scale?.semantics==='EVIDENCE_BALANCE_NOT_PROBABILITY'&&
   scale?.authority?.probability_model===false&&
   ['1_3d','5_7d','2_3w'].every(k=>{
     const obj=scale.horizons?.[k];
     return obj&&Number.isInteger(obj.bull)&&Number.isInteger(obj.bear)&&
       obj.bull>=1&&obj.bull<=10&&obj.bear>=1&&obj.bear<=10;
   })?scale.horizons:null;
 const ctx=latest.package?.market_cycle_context||{};
 const phase=(typeof ctx.current_phase==='string'&&PHASES.includes(ctx.current_phase))?
   ctx.current_phase:'UNAVAILABLE';
 const current=now<validTo;
 return {
  contract:'CN_PREMIUM_V2_COMPASS_PATH_UI_v1',status:current?'SOURCE_CURRENT':'SOURCE_EXPIRED',
  official_compass_id:compass.compass_id,issued_at_utc:compass.issued_at_utc,
  source_asof_utc:freshness.source_asof_utc,valid_until_utc:freshness.valid_until_utc,
  official_action:compass.action_now,
  official_action_current:current,action_allowed_to_display_as_current:current&&compass.action_now!=='UNAVAILABLE',
  horizons:HORIZONS.map(id=>({id,direction:hs[id].expected_direction,
    action_posture:hs[id].action_posture,description:hs[id].expected_path,
    eta_source:hs[id].eta||null})),
  capitalization_ladder:ladder.map(v=>({segment:v.segment,
    status:v.status,action:v.action,direction:v.direction,reason:v.reason})),
  bull_bear:gauge,
  bull_bear_semantics:gauge?'EVIDENCE_BALANCE_NOT_PROBABILITY':'UNAVAILABLE',
  path_phases:PHASES,path_current_phase:phase,
  path_next_gate:typeof ctx.next_gate==='string'?ctx.next_gate:null,
  rotation_confirmed:phase!=='UNAVAILABLE',
  price_source_current:current,probability_model:false,decision_authority:false
 };
}
