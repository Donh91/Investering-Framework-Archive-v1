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
  const forward=excerpt(proSource,
    '<section class="cn-forward"',
    '<section class="section"><div class="section-heading"><h2 data-t="tiersHeading"',
    'pro-long-range');
  // Preserve the existing optional Master Monday/source-trace PRO drawer, not
  // a second source, page, action or execution owner.
  const interpretation=excerpt(proSource,
    '<details class="product-more"><summary data-exp-t="interpretation">',
    '<details class="product-more"><summary data-exp-t="protection">',
    'pro-source-interpretation');
  const reentry='<section class="cn-pro-reentry" aria-labelledby="pro-reentry-heading">'+
    '<h3 id="pro-reentry-heading">Genkøb · officiel status</h3>'+
    '<strong id="pro-reentry-state">Afventer kilde</strong>'+
    '<p id="pro-reentry-note">En risikoadvarsel er ikke et genkøbssignal.</p></section>';
  // Target milestone is source-owned ALT_IGNITION, immediately before
  // micro acceleration in the existing 10-stage journey. No fake ETA.
  const path=excerpt(proSource,
    '<section id="view-path"', '<section id="view-results"', 'pro-path')
    .replace('<section id="view-path" class="view" hidden role="tabpanel" aria-labelledby="tab-path">',
      '<section id="official-path-view" class="cn-path-source" aria-label="PATH · kildeverificeret markedsforløb">')
    .replace('<section class="section"><div class="section-heading"><div><p class="eyebrow">02 / MARKET CYCLE</p>',
      '<aside class="cn-alt-milestone" aria-labelledby="cn-alt-milestone-title">'+
      '<div><span class="cn-milestone-eyebrow">NÆSTE STORE ALTCOIN-MILEPÆL</span>'+
      '<h2 id="cn-alt-milestone-title">Altseason ignition</h2>'+
      '<p id="cn-alt-milestone-subtitle">Før small/micro-acceleration · kræver verificeret rotation</p></div>'+
      '<div class="cn-milestone-eta"><span id="cn-alt-milestone-eta-label">Tid til fase</span>'+
      '<strong id="cn-alt-milestone-eta">Ingen verificeret ETA</strong>'+
      '<small id="cn-alt-milestone-state">Betinget watch · ikke nedtælling</small></div>'+
      '</aside>'+
      '<section class="section"><div class="section-heading"><div><p class="eyebrow">02 / MARKET CYCLE</p>');

  // The original PRO product's one official action is visible immediately.
  // Risk, trading lenses and longer official horizons stay within the same
  // semantic PRO component behind accessible disclosure, never cloned.
  const riskMarker='<div class="balance">';
  unique(core,riskMarker,'pro-risk-marker');
  const coreDisclosure=core.replace(riskMarker,
    '<details class="cn-pro-more"><summary>Risiko, beskyttelse og trader-visning</summary>'+riskMarker)
    .replace(/<\/section>\s*$/,extra+'\n'+forward+'\n'+reentry+'\n'+interpretation+'\n</details>\n</section>');
  if(!coreDisclosure.includes('id="pro-forward-rows"')||
     !coreDisclosure.includes('id="cn-forward-source-status"')||
     !coreDisclosure.includes('id="pro-reentry-state"')||
     !coreDisclosure.includes('id="monday-reading"')||
     !coreDisclosure.includes('id="source-trace-body"')||
     !coreDisclosure.includes('id="premium-risk-steps"'))
    throw Error('CN_UNIFIED_ROOT_PRO_FEATURES_MISSING');
  // Three purposeful first-fold readings: authoritative action, 12h observed
  // momentum (NOT a forecast) and official source-issued 1–3d posture.
  const compactCore=coreDisclosure.replace(
    '<strong id="premium-now-direction">—</strong></div></div>',
    '<strong id="premium-now-direction">—</strong></div>'+
    '<div class="product-cell cn-13d" aria-label="Official 1–3 day source reading">'+
    '<small id="cn-horizon-13-label">1–3 dage · kildevurdering</small>'+
    '<strong id="cn-horizon-13">—</strong>'+
    '<span class="product-action-meaning" id="cn-horizon-13-posture">—</span>'+
    '</div></div>');
  if(!compactCore.includes('id="cn-horizon-13"'))
    throw Error('CN_QUIET_PRO_FIRST_FOLD_INSERT_FAILED');
  const pro='<section id="compass-pro" class="cn-pro-surface" aria-labelledby="pro-heading">'+
    '<div class="cn-pro-intro"><span class="small-kicker">OFFICIEL BESLUTNINGSSTØTTE</span>'+
    '<h2 id="pro-heading">Kompas PRO</h2>'+
    '<p>Handling, observeret retning og risiko vises hver for sig. '+
    'Kun gyldige officielle kildebeslutninger er aktuelle.</p></div>'+
    '<p id="pro-source-status" class="cn-pro-source" role="status">Kontrollerer officiel kilde og gyldighed…</p>'+
    compactCore.replace('<details class="cn-pro-more">',
      '<p id="pro-next-gate" class="cn-pro-next-gate" role="status"></p>'+
      '<section class="cn-risk-quick" aria-label="Pullback classification">'+
      '<div class="cn-risk-quick-head"><div><small id="cn-risk-quick-label">PULLBACK / 5 RISIKOKLASSER</small>'+
      '<strong id="cn-risk-quick-state">Afventer kilde</strong></div>'+
      '<span id="cn-risk-quick-note">Kildens trin · ikke sandsynlighed</span></div>'+
      '<div id="cn-risk-quick-steps" class="risk-class-rail" aria-hidden="true"></div>'+
      '</section><details class="cn-pro-more">')+'</section>';

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
  // Decision -> chart -> cycle / altseason -> proof. Do not bury the user's
  // actionable source-bound market timeline underneath the audit appendix.
  const proofAt=unique(html,'<section id="proof-explorer"','source-proof');
  if(proofAt>=c)throw Error('CN_QUIET_PROOF_ORDER_SOURCE_MISMATCH');
  const originalProof=html.slice(proofAt,c);
  html=html.slice(0,proofAt)+path+'\n'+originalProof+html.slice(d);
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
  html=html.slice(0,target)+nav+'\n'+html.slice(target);
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
  // The original B root shipped anchor CSS for the now-retired legacy pilot.
  // Rewrite only the anchor list in the unified HTML, never the approved B
  // SVG, renderer or source gate. No orphan anchor names on the official route.
  const oldAnchors='#variant-panel,#official-product-pilot,#official-pilot-path,#proof-explorer{scroll-margin-top:16px}';
  const newAnchors='#variant-panel,#compass-pro,#official-path-view,#proof-explorer{scroll-margin-top:16px}';
  if(!html.includes(oldAnchors))throw Error('CN_UNIFIED_ROOT_SCROLL_ANCHOR_SOURCE_MISMATCH');
  html=html.replace(oldAnchors,newAnchors);
  if(html.includes('src="./compass/compass-path-ui.mjs"')||
     html.includes('href="/Investering-Framework-Archive-v1/vnext/#compass"'))
    throw Error('CN_UNIFIED_ROOT_COMPETING_COMPASS');
  return html;
}
