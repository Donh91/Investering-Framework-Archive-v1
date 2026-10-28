/**
 * SITE #1578 · Source-composed SINGLE homepage. The original approved B SVG
 * stays owned by graph-b/source-graph-b.mjs. Reuse the existing current-source
 * Kompas PRO product markup and module; no second forecast or Compass model.
 * Build only: no browser fetch or execution, and no private data.
 */
import {buildPremiumRootHtml} from './premium-root.mjs';

function unique(source,token,label){
  const a=source.indexOf(token);
  if(a<0||source.indexOf(token,a+token.length)!==-1)
    throw Error('CN_UNIFIED_ROOT_SOURCE_MISMATCH:'+label);
  return a;
}
function excerpt(s,start,end,label){
  const a=unique(s,start,label+' start'),b=unique(s,end,label+' end');
  if(b<=a)throw Error('CN_UNIFIED_ROOT_SOURCE_ORDER:'+label);
  return s.slice(a,b).trim();
}
export function buildUnifiedRootHtml(graphSource,proSource){
  if(typeof proSource!=='string'||proSource.length<10000)
    throw Error('CN_UNIFIED_ROOT_PRO_SOURCE_UNAVAILABLE');
  if(!proSource.includes('id="premium-now-action"')||
     !proSource.includes('id="pro-guidance"')||
     !proSource.includes('id="premium-path-rail"'))
    throw Error('CN_UNIFIED_ROOT_PRO_CONTRACT_MISSING');
  let html=buildPremiumRootHtml(graphSource);
  const core=excerpt(proSource,
    '<section class="product-first" aria-label="Official Compass decision">',
    '<section class="section"><div class="section-heading"><h2 data-t="horizonsHeading">',
    'pro-core');
  const extra=excerpt(proSource,
    '<section class="section"><div class="section-heading"><h2 data-t="horizonsHeading">',
    '<section class="cn-forward"', 'pro-horizons-and-ranges')
    .replace('data-t="horizonsHeading"','id="pro-horizon-heading" data-t="horizonsHeading"')
    .replace('<span data-t="ownerOfficial"','<span id="pro-horizon-owner" data-t="ownerOfficial"')
    .replace('<div class="table-scroll"><table>','<div class="table-scroll"><table id="pro-horizon-table">');
  const path=excerpt(proSource,
    '<section id="view-path"', '<section id="view-results"', 'pro-path')
    .replace('<section id="view-path" class="view" hidden role="tabpanel" aria-labelledby="tab-path">',
      '<section id="official-path-view" class="cn-path-source" aria-label="PATH · kildeverificeret markedsforløb">');

  // The original PRO product's one official action is visible immediately.
  // Risk, trading lenses and longer official horizons stay within the same
  // semantic PRO component behind accessible disclosure, never cloned.
  const riskMarker='<div class="balance">';
  unique(core,riskMarker,'pro-risk-marker');
  const coreDisclosure=core.replace(riskMarker,
    '<details class="cn-pro-more"><summary>Risiko, beskyttelse og trader-visning</summary>'+riskMarker)
    .replace(/<\/section>\s*$/,extra+'\n</details>\n</section>');
  if(!coreDisclosure.includes('id="pro-forward-rows"')||
     !coreDisclosure.includes('id="premium-risk-steps"'))
    throw Error('CN_UNIFIED_ROOT_PRO_FEATURES_MISSING');
  const pro='<section id="compass-pro" class="cn-pro-surface" aria-labelledby="pro-heading">'+
    '<div class="cn-pro-intro"><span class="small-kicker">OFFICIEL BESLUTNINGSSTØTTE</span>'+
    '<h2 id="pro-heading">Kompas PRO</h2>'+
    '<p>Handling, observeret retning og risiko vises hver for sig. '+
    'Kun gyldige officielle kildebeslutninger er aktuelle.</p></div>'+
    '<p id="pro-source-status" class="cn-pro-source" role="status">Kontrollerer officiel kilde og gyldighed…</p>'+
    coreDisclosure+'<p id="pro-next-gate" class="cn-pro-next-gate" role="status"></p></section>';

  const oldDecision='<section class="official-product-pilot premium-decision-summary"';
  const graph='<section id="variant-panel"';
  const a=unique(html,oldDecision,'old-decision');
  const b=unique(html,graph,'original-graph');
  if(b<=a)throw Error('CN_UNIFIED_ROOT_DECISION_ORDER');
  html=html.slice(0,a)+pro+'\n'+html.slice(b);
  const details='<section class="official-product-pilot premium-compass-detail"';
  const meta='<aside class="premium-meta"';
  const c=unique(html,details,'legacy-details');
  const d=unique(html,meta,'source-meta');
  if(d<=c)throw Error('CN_UNIFIED_ROOT_LEGACY_ORDER');
  html=html.slice(0,c)+path+'\n'+html.slice(d);
  html=html.replace('<a href="#official-product-pilot" data-premium-nav="compass">Kompas</a>',
    '<a href="#compass-pro" data-premium-nav="compass">Kompas PRO</a>');
  // No second PRO route or second graph entry in the official navigation.
  const proLink=/<a href="\/Investering-Framework-Archive-v1\/vnext\/#compass" class="premium-entry-pro"[^>]*>Kompas PRO ↗<\/a>\n/;
  if(!proLink.test(html))throw Error('CN_UNIFIED_ROOT_DUPLICATE_PRO_LINK_SOURCE_MISMATCH');
  html=html.replace(proLink,'');
  html=html.replace('href="#official-pilot-path" data-premium-nav="path"',
    'href="#official-path-view" data-premium-nav="path"');
  // The single product navigation belongs before the single PRO first fold,
  // rather than being discovered only after scrolling past the weekly chart.
  const navStart='<nav class="premium-entry-navigation"';
  const navClose='</nav>';
  const n=unique(html,navStart,'single-navigation');
  const nEnd=html.indexOf(navClose,n);
  if(nEnd<0)throw Error('CN_UNIFIED_ROOT_NAV_UNCLOSED');
  const nav=html.slice(n,nEnd+navClose.length);
  html=html.slice(0,n)+html.slice(nEnd+navClose.length);
  const target=unique(html,'<section id="compass-pro"','pro-nav-target');
  html=html.slice(0,target)+nav+'\\n'+html.slice(target);
  const oldScript='<script type="module" src="./compass/compass-path-ui.mjs"></script>';
  unique(html,oldScript,'legacy-compass-script');
  html=html.replace(oldScript,
    '<script type="module" src="./root-compass-pro.mjs"></script>');
  // The source ports remain available as nonpromoted historical rollback.
  for(const x of [
    'id="variant-panel"','id="chart"','id="forecast"','id="actual"',
    'id="compass-pro"','id="premium-now-action"','id="pro-guidance"',
    'id="premium-risk-steps"','id="pro-forward-rows"',
    'id="official-path-view"','id="premium-path-rail"',
    'id="proof-explorer"'
  ])unique(html,x,'singleton '+x);
  for(const x of [
    'id="official-product-pilot"','id="official-pilot-action"',
    'id="official-pilot-horizons"','id="official-pilot-rotation"',
    'id="official-pilot-path"','id="official-path-chart"'
  ])if(html.includes(x))throw Error('CN_UNIFIED_ROOT_LEGACY_DUPLICATE:'+x);
  if(html.includes('src="./compass/compass-path-ui.mjs"')||
     html.includes('href="/Investering-Framework-Archive-v1/vnext/#compass"'))
    throw Error('CN_UNIFIED_ROOT_COMPETING_COMPASS');
  return html;
}
