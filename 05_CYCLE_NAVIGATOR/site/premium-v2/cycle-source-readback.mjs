/**
 * Cycle Navigator PATH v3 · exact public owner-source presentation.
 * NO new stage classifier, timing model or trade action.
 * Weekly source can be DEGRADED while a qualified Official Compass is valid.
 */
const TIER = Object.freeze([
 ['BTC','BTC','BTC'],
 ['ETH','ETH','ETH'],
 ['LARGE_CAPS','Store','Large caps'],
 ['MID_CAPS','Mellem','Mid caps'],
 ['SMALL_CAPS','Små','Small caps'],
 ['MICROCAPS','Micro','Microcaps'],
 ['MEMES','Memes','Memes']
]);
const ACTION={
 HOLD:['Behold eksisterende','Hold existing','hold'],
 WAIT:['Afvent','Wait','wait'],
 HARD_WAIT:['Skærpet afvent','Strict wait','caution'],
 UNAVAILABLE:['Ingen selvstændig kilde','No dedicated source','missing']
};
const tr=(lang,da,en)=>lang==='en'?en:da;
const empty=lang=>({contract:'CN_CYCLE_SOURCE_EXPLAINER_v1',state:'UNAVAILABLE',
 weekLabel:tr(lang,'Afventer verificeret ugegrundlag','Awaiting verified weekly source'),
 meaning:tr(lang,'Ingen aktuel fase kan vises uden kildebevis.',
  'No current phase can be presented without source evidence.'),
 referenceKind:'NONE',rotation:[],rawSource:null});
export function cycleSourceReadback({view,lang='da'}={}){
 const p=view?.path,w=view?.weekly,c=view?.compass;
 const eligible=p?.state==='SOURCE_BOUND'&&c?.state==='FRESH'&&
  c.permit_path_live_gates===true&&
  p.source_issue===w?.public_issue_number&&
  p.source_week===w?.forecast_week&&
  p.source_identity===c?.compass_id&&
  Array.isArray(p.full_phases)&&p.full_phases.length===10&&
  ['OK','PASS','DEGRADED'].includes(p.source_health);
 if(!eligible)return empty(lang);
 const kind=p.current_checkpoint?.status==='FROZEN_WEEK_REFERENCE'&&
  p.full_phases.some(x=>x.key===p.current_checkpoint.key)?
   'FROZEN_WEEK_REFERENCE':'NO_VERIFIED_PHASE';
 const hasNext=kind==='FROZEN_WEEK_REFERENCE'&&
  p.next_checkpoint?.status==='UNCONFIRMED'&&
  p.full_phases.some(x=>x.key===p.next_checkpoint.key);
 const deg=p.source_health==='DEGRADED';
 const quality=deg?tr(lang,'Ugegrundlag delvist','Weekly source incomplete'):
  tr(lang,'Ugegrundlag verificeret','Weekly source verified');
 const weekLabel='CN #'+p.source_issue+' · '+p.source_week+' · '+quality;
 const meaning=kind==='FROZEN_WEEK_REFERENCE'?
  tr(lang,'Senest dokumenterede ugereference, ikke en bekræftet aktuel markedsfase.',
    'Last documented weekly reference, not a confirmed current market phase.'):
  tr(lang,'Ingen aktiv markedsfase er bekræftet. Cyklustrinene viser muligheder, ikke en tidsplan.',
    'No current market phase is confirmed. The cycle stages are reference, not a schedule.');
 const reason=deg?tr(lang,'Ugeanalysen er delvis. Afvent selvstændig bekræftelse.',
   'Weekly analysis is incomplete. Independent confirmation is still required.'):
  tr(lang,'Ugeanalysen alene kan ikke bekræfte et faseskift.',
    'The weekly analysis alone cannot confirm a phase transition.');
 const missingNext=tr(lang,'Næste fase er ikke dokumenteret endnu.',
   'The next phase is not documented yet.');
 const source=Array.isArray(p.rotation)?p.rotation:[];
 // All seven independent official asset-class owners must be present and
 // unique. One missing tier suppresses the entire presentation, no proxy.
 const keys=new Set(source.map(x=>x.key));
 const rotation=source.length===TIER.length&&keys.size===TIER.length&&
  TIER.every(([key])=>keys.has(key))?
  TIER.map(([key,da,en])=>{
   const raw=source.find(x=>x.key===key);
   const action=ACTION[raw?.action]||ACTION.UNAVAILABLE;
   return {key,label:tr(lang,da,en),action:tr(lang,action[0],action[1]),
    state:action[2],sourceAction:raw?.action||'UNAVAILABLE'};
  }):[];
 return {
  contract:'CN_CYCLE_SOURCE_EXPLAINER_v1',state:deg?'PARTIAL_WEEKLY':'SOURCE_ALIGNED',
  weekLabel,meaning,reason,
  referenceKind:kind,
  nextMeaning:hasNext?tr(lang,'Næste fase er kun et ubekræftet mål.',
    'The next phase is an unconfirmed watch target.'):missingNext,
  rotation,
  rawSource:'CN #'+p.source_issue+' · '+p.source_week+' · '+p.source_identity
 };
}
