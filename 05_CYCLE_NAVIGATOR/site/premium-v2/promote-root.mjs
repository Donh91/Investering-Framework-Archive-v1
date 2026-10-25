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
export async function promoteRoot(root=dist){
 const prior=await readFile(resolve(root,'index.html'),'utf8');
 if(!prior.includes('<base href="./vnext/">')||!prior.includes('PREMIUM LIVE'))
  throw Error('ROOT_PROMOTION_UNEXPECTED_OLD_ROOT');
 for(const required of ['vnext/index.html','legacy/index.html','data/latest.json',
  'data/compass.json','data/publication-lineage.json'])await readFile(resolve(root,required));
 const before=await snapshotCanonicalTree(root);
 const next=await readFile(resolve(root,'next/index.html'),'utf8');
 const promoted=promoteHtml(next);
 await writeFile(resolve(root,'index.html'),promoted);
 const after=await snapshotCanonicalTree(root);
 for(const path of new Set([...Object.keys(before),...Object.keys(after)])){
  if(path!=='index.html'&&before[path]!==after[path])throw Error('ROOT_PROMOTION_UNRELATED_ASSET_CHANGED:'+path);
 }
 if(before['index.html']===after['index.html'])throw Error('ROOT_PROMOTION_NO_CHANGE');
 return {stage:'OWNER_APPROVED_ROOT',previous_root_sha256:before['index.html'],
  promoted_root_sha256:sha(promoted),next_sha256:sha(next),
  unchanged_non_root_assets:Object.keys(before).length-1,prior_version:'/vnext/',
  protected_data:['data/latest.json','data/compass.json','data/publication-lineage.json']};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 promoteRoot().then(x=>console.log(JSON.stringify(x,null,2)))
  .catch(e=>{console.error(e);process.exitCode=1});
}
