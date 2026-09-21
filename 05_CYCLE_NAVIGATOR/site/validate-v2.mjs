import { readFile } from 'node:fs/promises';
const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [html,build,liveBuilder,liveWidget,weeklyWidget,app,product,history]=await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./build-live-observation.mjs'),read('./live-observation.js'),read('./weekly-score.js'),read('./app.js'),read('./public-product.js'),read('./history-scoreboard.json')]);
const h=JSON.parse(history);
const checks=[
 ['fallback action-first hero',html.includes('WHAT SHOULD I DO NOW?')],
 ['weekly authority firewall',html.includes('never rewrite the forecast')&&liveBuilder.includes('NON_AUTHORITATIVE_OBSERVATION_ONLY')],
 ['NOW/PATH/PROOF product tabs',['data-tab="now"','data-tab="path"','data-tab="proof"'].every(t=>product.includes(t))&&!product.includes('data-tab="score"')&&!product.includes('data-tab="how"')],
 ['Market Compass public language',product.includes('MARKET COMPASS')&&!product.includes('HANDLEKOMPAS ·')&&!product.includes('MASTER MONDAY →')],
 ['single-action hero',product.includes("HOLD:'HOLD'")&&!product.includes("HOLD:'HOLD / WAIT'")],
 ['large-to-micro action rail',product.includes('Bitcoin → microcaps')&&product.includes('capitalRail')&&product.includes('rotation_ladder')],
 ['freshness and next update',product.includes('MARKET COMPASS UPDATED')&&product.includes('NEXT UPDATE')],
 ['conditional path rail with ETA',product.includes('CONDITIONAL MARKET PATH')&&product.includes('YOU ARE HERE')&&product.includes('ETA ·')],
 ['proof rollups',product.includes('HISTORICAL WEEKLY AVERAGE')&&product.includes('PRICE RANGE ACCURACY')&&product.includes('MARKET & CYCLE UNDERSTANDING')],
 ['live score fail-closed',product.includes('Waiting for evidence')&&product.includes('No percentage is shown until at least one call is genuinely scoreable.')&&liveWidget.includes("live.provisional_score !== null")],
 ['latest completed precision consumes reconciled range score',weeklyWidget.includes('snapshot?.range_score')&&weeklyWidget.includes('No synthetic overall score is shown.')],
 ['prospective range bridge reaches homepage',app.includes('snapshot?.prospective_range')&&app.includes('website_consume')&&app.includes('prospective continuity baseline')],
 ['all issue weekly rollup',product.includes('publicScores')&&product.includes('archived??mean')&&product.includes('component rollup')],
 ['issue-level price aggregation',product.includes('Combined\\s+')&&product.includes('(?:BTC|ETH)')],
 ['non-price aggregation',product.includes('parseComponentScores')&&product.includes('intraday_display')&&product.includes('structure_display')],
 ['plain-English translator',product.includes('investorText')&&product.includes('Ethereum strengthens relative to Bitcoin')],
 ['public methodology describes data families',product.includes('PRICE & STRUCTURE')&&product.includes('PARTICIPATION & ROTATION')&&product.includes('LIQUIDITY & POSITIONING')&&product.includes('MACRO & NETWORK CONTEXT')],
 ['public product assets deployed',liveBuilder.includes('public-product.js')&&liveBuilder.includes('public-product.css')&&build.includes('history-scoreboard.json')],
 ['raw history remains locked',h.policy?.historical_scores_locked===true&&h.policy?.retroactive_rescoring===false],
 ['history coverage complete through CN25',h.coverage?.completed_issues===25&&h.coverage?.latest_open_issue===26]
];
let failed=0;for(const [name,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${name}`);if(!ok)failed++;}
if(failed)process.exit(1);console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator public product release checks`);
