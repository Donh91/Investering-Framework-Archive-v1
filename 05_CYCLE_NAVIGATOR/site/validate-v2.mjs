import { readFile } from 'node:fs/promises';
const read=p=>readFile(new URL(p,import.meta.url),'utf8');
const [html,build,liveBuilder,liveWidget,weeklyWidget,app,product,css,history,premium,premiumCss]=await Promise.all([read('./index.html'),read('./build-public.mjs'),read('./build-live-observation.mjs'),read('./live-observation.js'),read('./weekly-score.js'),read('./app.js'),read('./public-product.js'),read('./public-product.css'),read('./history-scoreboard.json'),read('./market-compass-premium.js'),read('./market-compass-premium.css')]);
const h=JSON.parse(history);
const checks=[
 ['fallback action-first hero',html.includes('WHAT SHOULD I DO NOW?')],
 ['weekly authority firewall',html.includes('never rewrite the forecast')&&liveBuilder.includes('NON_AUTHORITATIVE_OBSERVATION_ONLY')],
 ['NOW/PATH/PROOF product tabs',['data-tab="now"','data-tab="path"','data-tab="proof"'].every(t=>product.includes(t))&&!product.includes('data-tab="score"')&&!product.includes('data-tab="how"')],
 ['Market Compass public language',product.includes('MARKET COMPASS')&&!product.includes('HANDLEKOMPAS ·')&&!product.includes('MASTER MONDAY →')],
 ['premium three-horizon Compass is Official-Compass owned',premium.includes('OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1')&&premium.includes('MARKET_WEATHER_SOURCE_OF_TRUTH_v1')&&premium.includes('site_synthesis_allowed')&&['1_3d','5_7d','2_3w'].every(x=>premium.includes("scale: '"+x+"'"))],
 ['premium Bull/Bear fails closed instead of synthesising',premium.includes("row.status === 'OK'")&&premium.includes('bull + bear === 10')&&premium.includes('No Bull/Bear number is reconstructed by the website.')&&!/expected_direction[^\n]{0,120}(bull|bear)\s*=/.test(premium)],
 ['premium conclusion recommendation and explainability',premium.includes('CYCLE NAVIGATOR · CONCLUSION')&&premium.includes('RECOMMENDATION')&&premium.includes('HOW THIS READING IS BUILT')&&premium.includes('PRICE & STRUCTURE')&&premium.includes('PARTICIPATION & ROTATION')&&premium.includes('LIQUIDITY & POSITIONING')&&premium.includes('SENTIMENT & CYCLE')&&premium.includes('Evidence balance, not probability')],
 ['premium layer ships in final Pages bundle',liveBuilder.includes('market-compass-premium.js')&&liveBuilder.includes('market-compass-premium.css')&&premiumCss.includes('.premium-horizon-grid')&&premiumCss.includes('@media(max-width:520px)')],
 ['single-action hero',product.includes("HOLD:'HOLD'")&&!product.includes("HOLD:'HOLD / WAIT'")],
 ['large-to-micro action rail',product.includes('Bitcoin → microcaps')&&product.includes('capitalRail')&&product.includes('rotation_ladder')],
 ['freshness and next update',product.includes('MARKET COMPASS UPDATED')&&product.includes('NEXT UPDATE')],
 ['conditional path rail with ETA',product.includes('CONDITIONAL MARKET PATH')&&product.includes('YOU ARE HERE')&&product.includes('ETA ·')],
 ['scoreboard integrity uses coverage not a cross-era aggregate',h.policy?.cross_era_aggregate===false&&product.includes('completed forecasts with score evidence')&&!product.includes('HISTORICAL WEEKLY AVERAGE')&&!product.includes('mean(scores.map')],
 ['trust strip binds score coverage and prefers current projection identity',product.includes('cn-trust-strip')&&product.includes('Number.isInteger(currentIssue)?currentIssue:coverageOpen')&&product.includes('Forecast locked before outcome')&&product.includes('data-proof-link')],
 ['Since Last CN compares exact governed fields only',build.includes('EXACT_GOVERNED_FIELD_EQUALITY')&&!build.includes('freezeSignals')&&product.includes('SINCE LAST CN')],
 ['NOW refinements survive later Compass root replacements without loops',product.includes("if(!root.querySelector('.cn-now-refinements'))apply()")&&product.includes('nowObserver.observe(root')&&product.includes("if(root.querySelector('.cn-now-refinements'))return true")],
 ['trust-first components ship styled desktop and mobile layouts',['.cn-now-refinements','.cn-trust-strip','.cn-since-last','.cn-why-call','.completed-receipt','.completed-grid'].every(token=>css.includes(token))&&css.includes('@media(max-width:640px)')],
 ['Why This Call consumes governed structured dimensions with migration fallback',build.includes('market_structure_analysis.dimensions')&&build.includes('market_structure_v2.dimensions')&&!build.includes('value.includes(":")')&&product.includes("CN_PUBLIC_MARKET_STRUCTURE_PRESENTATION_v1")&&product.includes('dims.length!==5')],
 ['NOW refinements survive Compass unavailable renders',product.includes("root.querySelector('.action-hero,.fail-card')")&&product.includes('anchor.after(wrap)')],
 ['last completed receipt preserves canonical score precision',product.includes('function preciseScorePct')&&product.includes("value===null||value===undefined||value===''")&&product.includes('preciseScorePct(x.price_range_score)')&&product.includes("toFixed(2)")],
 ['last completed forecast binds to completed scorecard and survives publication lag',build.includes('deriveLatestCompletedForecast')&&build.includes('05_CYCLE_NAVIGATOR/public_scorecards/')&&build.includes('typeof latest?.price_range_score==="number"')&&!build.includes('Number(latest.price_range_score)')&&build.includes('evaluation?.strengths')&&build.includes('evaluation?.misses')&&!build.includes('outcome?.published_path')&&!build.includes('currentIssue!==completedIssue+1')&&product.includes('LAST COMPLETED FORECAST')&&product.includes('data-ledger-link')],
 ['live score fail-closed',product.includes('Waiting for evidence')&&product.includes('No percentage is shown until at least one call is genuinely scoreable.')&&liveWidget.includes("live.provisional_score !== null")],
 ['latest completed precision uses public forecast lineage',weeklyWidget.includes('Latest completed public precision')&&weeklyWidget.includes('public_scorecard')&&weeklyWidget.includes('migration-era machine issue number alone')],
 ['new scoring is price only',weeklyWidget.includes('Price Ranges')&&!weeklyWidget.includes('cal-summary-label">Market / Structure')],
 ['weekly precision stays price-only',build.includes('public_bull_bear_scale')&&weeklyWidget.includes('Price Ranges')&&!weeklyWidget.includes('BULL / BEAR')],
 ['prospective range bridge reaches homepage',app.includes('snapshot?.prospective_range')&&app.includes('website_consume')&&app.includes('prospective continuity baseline')],
 ['all issue weekly rollup',product.includes('publicScores')&&product.includes('mayDerive')&&product.includes('component rollup')],
 ['explicit no-derived-overall respected',product.includes('explicitDerive')&&h.records?.find(r=>r.cn===25)?.allow_derived_overall===false],
 ['public series identity reaches homepage',build.includes('CN_PUBLIC_SERIES_INDEX.json')&&product.includes('current_public_projection?.public_issue_number')],
 ['canonical public score lineage present',Array.isArray(h.records)&&h.records.length>0&&h.records.every(r=>Number.isInteger(Number(r.cn))&&typeof r.provenance==='string'&&r.provenance.length>0)],
 ['issue-level price aggregation',product.includes('Combined\\s+')&&product.includes('(?:BTC|ETH)')],
 ['non-price aggregation',product.includes('parseComponentScores')&&product.includes('intraday_display')&&product.includes('structure_display')],
 ['plain-English translator',product.includes('investorText')&&product.includes('Ethereum strengthens relative to Bitcoin')],
 ['public methodology describes data families',product.includes('PRICE & STRUCTURE')&&product.includes('PARTICIPATION & ROTATION')&&product.includes('LIQUIDITY & POSITIONING')&&product.includes('MACRO & NETWORK CONTEXT')],
 ['public product assets deployed',liveBuilder.includes('public-product.js')&&liveBuilder.includes('public-product.css')&&build.includes('history-scoreboard.json')],
 ['Market Structure is analysis only from cutover',build.includes('public_market_structure_analysis')&&product.includes('MARKET STRUCTURE · ANALYSIS ONLY')&&product.includes('No accuracy score from CN #27 onward')],
 ['legacy Market Structure history preserved',h.records?.find(r=>r.cn===26)?.structure_method==='LEGACY_PRE_V2'&&h.records?.find(r=>r.cn===26)?.structure_display==='Legacy Market/Structure 60'&&h.policy?.market_structure_score_cutover?.historical_rows_preserved===true],
 ['new Market Structure scores disabled',h.policy?.market_structure_score_cutover?.first_analysis_only_public_issue===27&&h.policy?.market_structure_score_cutover?.new_market_structure_scores===false],
 ['raw history remains locked',h.policy?.historical_scores_locked===true&&h.policy?.retroactive_rescoring===false],
 ['history coverage matches records',Number(h.coverage?.completed_issues)===Math.max(...h.records.map(r=>Number(r.cn)))&&Number(h.coverage?.latest_open_issue)===Number(h.coverage?.completed_issues)+1&&Number(h.coverage?.rows_with_published_or_canonical_score_evidence)===h.records.length]
];
let failed=0;for(const [name,ok] of checks){console.log(`${ok?'PASS':'FAIL'} ${name}`);if(!ok)failed++;}
if(failed)process.exit(1);console.log(`PASS ${checks.length}/${checks.length} Cycle Navigator public product release checks`);
