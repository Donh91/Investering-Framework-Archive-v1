import { readFile } from 'node:fs/promises';
const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [html,build,liveBuilder,product,history]=await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./build-live-observation.mjs'),read('./public-product.js'),read('./history-scoreboard.json')]);
const h=JSON.parse(history);
const checks=[
 ['fallback action-first hero',html.includes('WHAT SHOULD I DO NOW?')],
 ['weekly authority firewall',html.includes('never rewrite the forecast')&&liveBuilder.includes('NON_AUTHORITATIVE_OBSERVATION_ONLY')],
 ['NOW/PATH/SCORE/HOW product tabs',['data-tab="now"','data-tab="path"','data-tab="score"','data-tab="how"'].every(t=>product.includes(t))],
 ['Cycle Compass is the public NOW authority',product.includes('CYCLE COMPASS · WHAT SHOULD I DO NOW?')&&product.includes('current_action')],
 ['large-to-micro capital rotation line',product.includes('Bitcoin → microcaps')&&product.includes('rotation_ladder')&&product.includes('capital-line')],
 ['freshness and next-cycle timer',product.includes('LAST UPDATED')&&product.includes('NEXT UPDATE')&&product.includes('setUTCMinutes')],
 ['live state fails closed',product.includes('Data quality is limited')&&product.includes('DATA_DEGRADED')&&product.includes('No new risk signal is inferred')],
 ['rotation status has explicit public semantics',product.includes('MAJOR LIQUIDITY ANCHOR')&&product.includes('RELATIVE RESILIENCE')&&product.includes("return'hold'")],
 ['scoreboard rendered from locked history',product.includes('history-scoreboard.json')&&product.includes('arithmetic summaries')],
 ['three public score lenses',product.includes('WEEKLY SCORE')&&product.includes('PRICE RANGES')&&product.includes('MARKET & CYCLE')],
 ['How it works is public language',product.includes('MARKET DATA')&&product.includes('MARKET STRUCTURE')&&product.includes('INDEPENDENT ANALYSIS')&&product.includes('WEEKLY FORECAST')&&product.includes('LIVE CYCLE COMPASS')&&product.includes('OUTCOME & SCORE')&&product.includes('LEARNING LOOP')&&!product.includes('MASTER MONDAY')],
 ['public data categories are explained',product.includes('BTC DOMINANCE')&&product.includes('STABLECOINS')&&product.includes('ETF FLOWS')&&product.includes('DERIVATIVES')&&product.includes('ON-CHAIN CONTEXT')],
 ['public product assets deployed',liveBuilder.includes('public-product.js')&&liveBuilder.includes('public-product.css')&&build.includes('history-scoreboard.json')],
 ['retroactive rescoring forbidden',h.policy?.retroactive_rescoring===false],
 ['history coverage complete through CN25',h.coverage?.completed_issues===25&&h.coverage?.latest_open_issue===26]
];
let failed=0;for(const [n,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${n}`);if(!ok)failed++;}if(failed)process.exit(1);console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator public product release checks`);
