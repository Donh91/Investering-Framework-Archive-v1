import { readFile } from 'node:fs/promises';
const read = p => readFile(new URL(p, import.meta.url),'utf8');
const [html,build,history] = await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./history-scoreboard.json')]);
const checks = [
 ['NOW/PATH/WHY navigation', /href="#now"/.test(html)&&/href="#path"/.test(html)&&/href="#why"/.test(html)],
 ['action-first hero', html.includes('WHAT SHOULD I DO NOW?')],
 ['live authority firewall', html.includes('never rewrite the forecast')],
 ['scoreboard renderer wired', html.includes('history-scoreboard.js')&&html.includes('scoreboard.css')],
 ['scoreboard assets deployed', build.includes('history-scoreboard.json')&&build.includes('history-scoreboard.js')&&build.includes('scoreboard.css')],
 ['no cross-era aggregate', JSON.parse(history).policy?.cross_era_aggregate===false],
 ['retroactive rescoring forbidden', JSON.parse(history).policy?.retroactive_rescoring===false]
];
let failed=0; for(const [name,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${name}`); if(!ok) failed++;}
if(failed) process.exit(1); console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator v2 release checks`);