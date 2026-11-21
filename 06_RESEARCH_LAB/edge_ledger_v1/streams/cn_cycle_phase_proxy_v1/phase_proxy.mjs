// Research-only pure functions. No IO or Round 3 access, no production authority.
export const phaseMap=Object.freeze({PRE_ROTATION:'EXPANSION',ROTATION:'EXPANSION',BROAD_ALTSEASON:'EXPANSION',PARABOLIC_ALTSEASON:'EXPANSION',DISTRIBUTION:'DISTRIBUTION'});
const known=new Set(['ACCUMULATION','EXPANSION','DISTRIBUTION','CONTRACTION']);
const positive=x=>typeof x==='number'&&Number.isFinite(x)&&x>0;
export function forecaster(ctx){return ['OK','PASS'].includes(ctx?.status)&&Object.hasOwn(phaseMap,ctx?.phase)?phaseMap[ctx.phase]:null;}
export function persistence(ctx){return forecaster(ctx?.prior);}
export function trend(ctx){const {past,asof}=ctx||{};return positive(past)&&positive(asof)?(asof>=past?'EXPANSION':'CONTRACTION'):null;}
export function outcome({past,asof,end}={}) {
 if(![past,asof,end].every(positive))return null;
 return asof>=past?(end>=asof?'EXPANSION':'DISTRIBUTION'):(end>=asof?'ACCUMULATION':'CONTRACTION');
}
export function loss(predicted,actual){if(!known.has(actual))return null;return predicted===actual?0:1;}
export function score(row){
 if(row?.readiness!==true||!row.issue_clock||!row.snapshot_id||!row.run_id)return null;
 const y=outcome(row.outcome);
 if(!y)return null;
 return {model:loss(row.model,y),persistence:loss(row.persistence,y),trend:loss(row.trend,y)};
}
