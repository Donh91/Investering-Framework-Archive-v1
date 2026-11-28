/** Display-only operational cutover. No forecast-method or score authority. */
export const SYSTEM_CUTOVER_UTC='2026-11-27T22:37:10Z';
export const SYSTEM_CUTOVER_MS=Date.parse(SYSTEM_CUTOVER_UTC);
export function issuanceCohort(issued){
 if(typeof issued!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{3})?Z$/.test(issued))return 'UNVERIFIED';
 const ms=Date.parse(issued);
 if(!Number.isFinite(ms)||new Date(ms).toISOString()!==(issued.includes('.')?issued:issued.replace('Z','.000Z')))return 'UNVERIFIED';
 return ms<SYSTEM_CUTOVER_MS?'OLD_SYSTEM':'NEW_SYSTEM';
}
export function cohortLabel(issued,lang='da'){
 const code=issuanceCohort(issued);
 return code==='OLD_SYSTEM'?(lang==='en'?'Old system':'Gammelt system'):
  code==='NEW_SYSTEM'?(lang==='en'?'New system':'Nyt system'):
  (lang==='en'?'Original issue time unverified':'Oprindelig udstedelsestid ikke verificeret');
}
export function currentNewScoreCount(view){
 if(view?.status!=='PROVISIONAL_SOURCE_READBACK'||issuanceCohort(view.freeze_issued_at_utc)==='UNVERIFIED')return null;
 return issuanceCohort(view.freeze_issued_at_utc)==='NEW_SYSTEM'?
  (view.window_items||[]).filter(w=>typeof w.source_reported_score_to_date==='number'&&Number.isFinite(w.source_reported_score_to_date)).length:0;
}
