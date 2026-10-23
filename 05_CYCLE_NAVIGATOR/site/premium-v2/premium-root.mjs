/**
 * Build /next/ FROM the ONE approved source-ported Graph B HTML.
 * Build-only presentation transform, never a new data source or forecast issuer.
 */
const substitutions=[
 ['<title>Cycle Navigator · B source-port (ISOLATED)</title>','<title>Cycle Navigator · Premium v2.1 · NEXT</title>'],
 ['href="./source-graph-b.css"','href="./graph-b/source-graph-b.css"'],
 ['href="../proof/proof-explorer.css"','href="./proof/proof-explorer.css"'],
 ['href="../compass/compass-path.css"','href="./compass/compass-path.css"'],
 ['src="../assets/CN_LOGO.svg"','src="./assets/CN_LOGO.svg"'],
 ['src="./source-graph-b.mjs"','src="./graph-b/source-graph-b.mjs"'],
 ['src="../proof/proof-explorer.mjs"','src="./proof/proof-explorer.mjs"'],
 ['src="../compass/compass-path-ui.mjs"','src="./compass/compass-path-ui.mjs"'],
 ['DESIGN QA · IKKE PRODUKTION','PREMIUM v2.1 · IKKE OFFICIEL FORSIDE']
];
const navigation=[
 '<div class="premium-entry">',
 '<div class="premium-entry-intro"><span class="premium-entry-overline">CYCLE NAVIGATOR / NEXT</span>',
 '<h1 data-premium-copy="title">Et klarere blik på markedet.</h1>',
 '<p data-premium-copy="intro">Følg den originale prognose, den faktiske udvikling og kildeudstedte signaler i ét instrument.</p></div>',
 '<nav class="premium-entry-navigation" aria-label="Premium sektioner">',
 '<a href="#variant-panel" data-premium-nav="graph">Graf B</a>',
 '<a href="#official-product-pilot" data-premium-nav="compass">Kompas</a>',
 '<a href="#official-pilot-path" data-premium-nav="path">PATH</a>',
 '<a href="#proof-explorer" data-premium-nav="proof">Proof</a>',
 '<a href="../" class="premium-entry-canonical" data-premium-nav="official">Officiel side ↗</a>',
 '</nav>',
 '<p class="premium-entry-disclaimer" data-premium-copy="disclaimer">Udviklingsvisning. Originale offentlige kilder, ingen demonstrationskurser. Den officielle forside er uændret.</p>',
 '</div>'
].join('\n');
const style=[
 '<style>',
 '.premium-entry{margin:18px 0 24px}',
 '.premium-entry-overline{font-size:10px;letter-spacing:.16em;color:#54718d;font-weight:750}',
 '.premium-entry-intro h1{font-size:clamp(28px,5.2vw,48px);line-height:1.12;letter-spacing:-.045em;color:#07172f;margin:10px 0 10px}',
 '.premium-entry-intro p{font-size:clamp(14px,2vw,16px);max-width:56ch;color:#596b80;line-height:1.6;margin:0 0 17px}',
 '.premium-entry-navigation{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 12px}',
 '.premium-entry-navigation a{display:inline-flex;align-items:center;justify-content:center;padding:10px 14px;min-height:44px;border:1px solid #dce4ed;background:#fff;border-radius:10px;color:#07172f;font-size:13px;font-weight:650;text-decoration:none}',
 '.premium-entry-navigation a:hover,.premium-entry-navigation a:focus-visible{border-color:#2f6fda;outline-offset:3px}',
 '.premium-entry-navigation .premium-entry-canonical{margin-left:auto;color:#2f6fda}',
 '.premium-entry-disclaimer{font-size:11px;line-height:1.55;color:#62758a;margin:0 0 15px}',
 '#variant-panel,#official-product-pilot,#official-pilot-path,#proof-explorer{scroll-margin-top:16px}',
 '@media(max-width:440px){.premium-entry-navigation .premium-entry-canonical{margin-left:0}}',
 '@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}',
 '</style>'
].join('\n');
function once(text,needle,label){
 const at=text.indexOf(needle);
 if(at===-1||text.indexOf(needle,at+needle.length)!==-1)
  throw Error('CN_PREMIUM_ROOT_SOURCE_MISMATCH:'+label);
}
export function buildPremiumRootHtml(source){
 if(typeof source!=='string'||source.length<1000)
  throw Error('CN_PREMIUM_ROOT_SOURCE_UNAVAILABLE');
 if(/\bMath\.sin\s*\(/.test(source)||/src\/main\.ts/.test(source))
  throw Error('CN_PREMIUM_ROOT_SYNTHETIC_SOURCE_FORBIDDEN');
 for(const [from,to] of substitutions){
  once(source,from,from.slice(0,45));
  source=source.replace(from,to);
 }
 once(source,'</head>','head-end');
 source=source.replace('</head>',style+'</head>');
 const marker='<p class="source-audit-status" id="feed-status"';
 once(source,marker,'source-status');
 source=source.replace(marker,navigation+'\n'+marker);
 for(const id of ['variant-panel','official-product-pilot','official-pilot-path','proof-explorer'])
  once(source,'id="'+id+'"',id);
 if(!source.includes('name="robots" content="noindex,nofollow"'))
  throw Error('CN_PREMIUM_ROOT_MISSING_NOINDEX');
 if(source.includes('href="../proof/')||source.includes('href="../compass/')||
    source.includes('src="../assets/')||source.includes('src="../proof/'))
  throw Error('CN_PREMIUM_ROOT_UNREWRITTEN_ASSET');
 return source;
}
