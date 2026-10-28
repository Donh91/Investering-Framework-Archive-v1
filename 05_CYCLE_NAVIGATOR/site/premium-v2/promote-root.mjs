/** Owner-approved release of the already staged Graph B artifact to /.
 * Keep /next/ immutable and retain the prior homepage at /vnext/.
 */
import {readFile,writeFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {snapshotCanonicalTree} from './stage-next.mjs';

const dist=resolve(dirname(fileURLToPath(import.meta.url)),'../dist');
const sha=b=>createHash('sha256').update(b).digest('hex');
function replaceOnce(input,from,to){
 const first=input.indexOf(from);
 if(first<0||input.indexOf(from,first+from.length)>=0)throw Error('ROOT_PROMOTION_SOURCE_MISMATCH:'+from);
 return input.replace(from,to);
}
export function promoteHtml(input){
 if(!input.includes('id="variant-panel"')||!input.includes('id="official-product-pilot"')||
    !input.includes('id="proof-explorer"')||!input.includes('id="official-pilot-path"')||
    !input.includes('Weekly Outlook <span class="alt-token">B</span>'))
  throw Error('ROOT_PROMOTION_GRAPH_B_COMPONENT_MISSING');
 let html=input;
 for(const [from,to] of [
  ['<meta name="robots" content="noindex,nofollow">','<meta name="description" content="Cycle Navigator: oprindelige prognoseintervaller, faktiske kurser, Proof, officielt Kompas og PATH.">'],
  ['<title>Cycle Navigator · Premium v2.1 · NEXT</title>','<title>Cycle Navigator · Weekly Outlook B</title>'],
  ['<body class="premium-next">','<body class="premium-next premium-home">'],
  ['CYCLE NAVIGATOR / NEXT','CYCLE NAVIGATOR / OFFICIEL'],
  ['PREMIUM v2.1 · IKKE OFFICIEL FORSIDE','CYCLE NAVIGATOR · OFFICIEL'],
  ['Forhåndsvisning · Kildebaseret, uden demonstrationskurser.','Kildebaseret · Oprindelige intervaller og observerede kurser.'],
  ['href="../" class="premium-entry-canonical"','href="./vnext/" class="premium-entry-canonical"'],
  ['>Officiel side ↗</a>','>Forrige version ↗</a>'],
  ['href="../data/latest.json"','href="./data/latest.json"'],
  ['href="../data/compass.json"','href="./data/compass.json"']
 ])html=replaceOnce(html,from,to);
 if(/noindex|PREMIUM v2\.1 · IKKE OFFICIEL|Math\.sin\s*\(/.test(html))
  throw Error('ROOT_PROMOTION_PREVIEW_OR_SYNTHETIC_SOURCE');
 if(!html.includes('/Investering-Framework-Archive-v1/next/assets/'))
  throw Error('ROOT_PROMOTION_VITE_ASSET_PATH_MISSING');
 return html;
}
/**
 * Preview-only, PURE unified release transformer.
 * Never changes / by itself and must not be called by the legacy auto-promoter.
 * Exact built /next/unified.html -> candidate root; actual upload requires
 * separate owner-approved governed release and public readback.
 */
export function promoteUnifiedHtml(input){
 if(typeof input!=='string'||input.length<2000)
  throw Error('UNIFIED_PROMOTION_SOURCE_MISSING');
 const required=[
  'variant-panel','chart','forecast','actual','proof-explorer','compass-pro',
  'premium-now-action','premium-risk-steps','pro-reentry-state',
  'cn-forward-source-status','official-path-view','premium-path-rail'
 ];
 for(const id of required){
  const n=input.split('id="'+id+'"').length-1;
  if(n!==1)throw Error('UNIFIED_PROMOTION_SINGLETON_MISSING:'+id+':'+n);
 }
 for(const legacy of ['official-product-pilot','official-pilot-action',
  'official-pilot-rotation','official-pilot-path','official-path-chart']){
  if(input.includes('id="'+legacy+'"'))throw Error('UNIFIED_PROMOTION_LEGACY_OWNER:'+legacy);
 }
 if(input.includes('/vnext/#compass')||
    input.includes('src="./compass/compass-path-ui.mjs"'))
  throw Error('UNIFIED_PROMOTION_COMPETING_COMPASS');
 let html=input;
 for(const [from,to] of [
  ['<meta name="robots" content="noindex,nofollow">',
   '<meta name="description" content="Cycle Navigator: officielt Kompas PRO, original Graph B, markedets kildeverificerede prisintervaller og dokumenteret efterkontrol.">'],
  ['<title>Cycle Navigator · Premium v2.1 · NEXT</title>',
   '<title>Cycle Navigator · Kompas PRO & Graph B</title>'],
  ['<body class="premium-next">','<body class="premium-next premium-home">'],
  ['CYCLE NAVIGATOR / NEXT','CYCLE NAVIGATOR / OFFICIEL'],
  ['PREMIUM v2.1 · IKKE OFFICIEL FORSIDE','CYCLE NAVIGATOR · OFFICIEL'],
  ['Forhåndsvisning · Kildebaseret, uden demonstrationskurser.',
   'Kildebaseret · Oprindelige intervaller og observerede kurser.'],
  ['href="../" class="premium-entry-canonical"',
   'href="./vnext/" class="premium-entry-canonical"'],
  ['>Officiel side ↗</a>','>Forrige version ↗</a>'],
  ['href="../data/latest.json"','href="./data/latest.json"'],
  ['href="../data/compass.json"','href="./data/compass.json"']
 ])html=replaceOnce(html,from,to);
 if(/noindex|IKKE OFFICIEL FORSIDE|Math\.sin\s*\(/.test(html))
  throw Error('UNIFIED_PROMOTION_PREVIEW_OR_SYNTHETIC_SOURCE');
 if(!html.includes('/Investering-Framework-Archive-v1/next/assets/'))
  throw Error('UNIFIED_PROMOTION_COMPILED_ASSETS_MISSING');
 if(html.includes('src="../')||html.includes('href="../data/'))
  throw Error('UNIFIED_PROMOTION_RELATIVE_ASSET_ESCAPE');
 return html;
}

export async function promoteRoot(root=dist){
 const prior=await readFile(resolve(root,'index.html'),'utf8');
 if(!prior.includes('<base href="./vnext/">')||!prior.includes('PREMIUM LIVE'))
  throw Error('ROOT_PROMOTION_UNEXPECTED_OLD_ROOT');
 for(const required of ['vnext/index.html','legacy/index.html','data/latest.json',
  'data/compass.json','data/publication-lineage.json'])await readFile(resolve(root,required));
 const before=await snapshotCanonicalTree(root);
 // Promote the already verified SINGLE PRO + original B entry, not the
 // old /next/index.html pilot. Its Vite assets remain immutable in /next/.
 const next=await readFile(resolve(root,'next/unified.html'),'utf8');
 const promoted=promoteUnifiedHtml(next);
 await writeFile(resolve(root,'index.html'),promoted);
 const after=await snapshotCanonicalTree(root);
 for(const path of new Set([...Object.keys(before),...Object.keys(after)])){
  if(path!=='index.html'&&before[path]!==after[path])throw Error('ROOT_PROMOTION_UNRELATED_ASSET_CHANGED:'+path);
 }
 if(before['index.html']===after['index.html'])throw Error('ROOT_PROMOTION_NO_CHANGE');
 return {stage:'OWNER_APPROVED_ROOT',previous_root_sha256:before['index.html'],
  promoted_root_sha256:sha(promoted),next_sha256:sha(next),
  source_entry:'next/unified.html',single_compass:'compass-pro',approved_graph:'graph-b',
  unchanged_non_root_assets:Object.keys(before).length-1,prior_version:'/vnext/',
  protected_data:['data/latest.json','data/compass.json','data/publication-lineage.json']};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 promoteRoot().then(x=>console.log(JSON.stringify(x,null,2)))
  .catch(e=>{console.error(e);process.exitCode=1});
}
