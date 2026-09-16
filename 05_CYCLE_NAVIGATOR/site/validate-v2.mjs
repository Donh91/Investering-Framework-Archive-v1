import { readFile } from 'node:fs/promises';
const read = p => readFile(new URL(p, import.meta.url),'utf8');
const [html,build,liveBuilder,product,history] = await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./build-live-observation.mjs'),read('./public-product.js'),read('./history-scoreboard.json')]);
const historyJson=JSON.parse(history);
const checks = [
 ['fallback action-first hero', html.includes('WHAT SHOULD I DO NOW?')],
 ['weekly authority firewall', html.includes('never rewrite the forecast')&&liveBuilder.includes('NON_AUTHORITATIVE_OBSERVATION_ONLY')],
 ['v3 NOW/PATH/SCORE/HOW product tabs', ['data-tab="now"','data-tab="path"','data-tab="score"','data-tab="how"'].every(token=>product.includes(token))],
 ['Handlekompas is the NOW authority', product.includes('HANDLEKOMPAS · WHAT SHOULD I DO NOW?')&&product.includes('current_action')],
 ['large-to-micro rotation compass', product.includes('Bitcoin to microcaps')&&product.includes('rotation_ladder')],
 ['freshness and next-cycle timer', product.includes('HANDLEKOMPAS UPDATED')&&product.includes('NEXT HOURLY DATA CYCLE')&&product.includes('nextHourlySourceCycle')],
 ['scoreboard rendered from locked history', product.includes('history-scoreboard.json')&&product.includes('no retroactive rescoring')],
 ['How it works pipeline present', product.includes('DATA → SPECIALIST ANALYSIS → EVIDENCE & CHALLENGE → MASTER MONDAY → FROZEN CYCLE NAVIGATOR → LIVE HANDLEKOMPAS → SCORE & LEARNING')],
 ['public product assets deployed', liveBuilder.includes('public-product.js')&&liveBuilder.includes('public-product.css')&&build.includes('history-scoreboard.json')],
 ['no cross-era aggregate', historyJson.policy?.cross_era_aggregate===false],
 ['retroactive rescoring forbidden', historyJson.policy?.retroactive_rescoring===false],
 ['history coverage complete through CN25', historyJson.coverage?.completed_issues===25&&historyJson.coverage?.latest_open_issue===26]
];
let failed=0; for(const [name,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${name}`); if(!ok) failed++;}
if(failed) process.exit(1); console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator public product release checks`);
