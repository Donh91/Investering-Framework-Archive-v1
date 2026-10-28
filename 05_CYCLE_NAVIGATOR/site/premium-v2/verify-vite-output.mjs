/**
 * Validate the REAL Vite multi-page output before any existing Pages artifact upload.
 * This does not build or deploy anything, modify canonical root, or infer market data.
 * Run only AFTER: npm ci && npm run build:next.
 */
import {readdir,readFile,stat} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {resolve,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';

const project=resolve(fileURLToPath(new URL('.',import.meta.url)));
const base='/Investering-Framework-Archive-v1/next/';
const host='https://donh91.github.io';
const mandatory=['index.html','unified.html','graph-b/source-graph-b.html'];

export async function verifyViteOutput(dist=resolve(project,'../dist/next')){
 const root=resolve(dist),inventory=[],errors=[];
 async function walk(dir){
  for(const ent of await readdir(dir,{withFileTypes:true})){
   const abs=resolve(dir,ent.name),rel=relative(root,abs).split(sep).join('/');
   if(rel.startsWith('../')||rel==='..')throw Error('NEXT_PATH_ESCAPE');
   if(ent.isDirectory()){await walk(abs);continue;}
   if(!ent.isFile())throw Error('NEXT_UNEXPECTED_FILE_TYPE:'+rel);
   if(rel.startsWith('reference/')||rel.includes('/node_modules/')||rel.endsWith('src/main.ts'))
     throw Error('NEXT_QUARANTINED_ASSET:'+rel);
   const bytes=await readFile(abs);
   if(/\.(?:html|js|mjs|css)$/i.test(rel)){
    const text=bytes.toString('utf8');
    if(/\bMath\.sin\s*\(/.test(text)||/reference\/appdeploy-bc\/src\/main\.ts/.test(text))
     throw Error('NEXT_SYNTHETIC_SOURCE:'+rel);
    if(/github\.com\/Donh91\/secrets(?:\/|["'])/.test(text))
     throw Error('NEXT_RESTRICTED_REPOSITORY_LINK:'+rel);
   }
   inventory.push({path:rel,bytes:bytes.length,sha256:createHash('sha256').update(bytes).digest('hex')});
  }
 }
 await walk(root);
 const files=new Set(inventory.map(x=>x.path));
 for(const path of mandatory)if(!files.has(path))errors.push('MISSING_ENTRY:'+path);
 const pages={};
 // All three preview entries are explicit build outputs. If unified is missing,
 // staging fails instead of silently shipping the old duplicate Compass layout.
 for(const path of mandatory){
  if(!files.has(path))continue;
  const html=await readFile(resolve(root,path),'utf8');
  pages[path]=html.length;
  if(!/noindex/i.test(html))errors.push('MISSING_NOINDEX:'+path);
  if(path.includes('graph-b/')&&!html.includes('id="chart"'))
   errors.push('MISSING_GRAPH_B_MARKUP');
  if(path==='index.html'){
   for(const id of ['chart','variant-panel','proof-explorer','official-product-pilot','official-pilot-path']){
    if(!html.includes('id="'+id+'"'))errors.push('MISSING_PREMIUM_ROOT_MARKUP:'+id);
   }
  }
  if(path==='unified.html'){
   for(const id of [
    'chart','variant-panel','proof-explorer','compass-pro',
    'premium-now-action','premium-risk-steps','pro-forward-rows',
    'official-path-view','premium-path-rail'
   ])if((html.match(new RegExp('id="'+id+'"','g'))||[]).length!==1)
     errors.push('UNIFIED_SINGLETON_ID:'+id);
   for(const id of ['official-product-pilot','official-pilot-action',
     'official-pilot-path','official-path-chart'])
    if(html.includes('id="'+id+'"'))errors.push('UNIFIED_LEGACY_DUPLICATE:'+id);
   if(html.includes('/vnext/#compass')||
      html.includes('src="./compass/compass-path-ui.mjs"'))
     errors.push('UNIFIED_COMPETING_COMPASS_ROUTE');
  }
  const entryUrl=new URL(base+path,host);
  const refPattern=/<(?:script|link|img)\b[^>]*?\s(?:src|href)=["']([^"']+)["']/gi;
  for(const m of html.matchAll(refPattern)){
   const ref=m[1].trim();
   if(!ref||ref.startsWith('#')||/^(?:data|blob|mailto|tel):/.test(ref))continue;
   const target=new URL(ref,entryUrl);
   if(target.origin!==host||!target.pathname.startsWith(base)){
    errors.push('ASSET_OUTSIDE_NEXT:'+path+':'+ref);continue;
   }
   const targetRel=decodeURIComponent(target.pathname.slice(base.length));
   if(targetRel.includes('..')||!files.has(targetRel))
    errors.push('MISSING_REFERENCED_ASSET:'+path+':'+ref);
  }
 }
 const javascript=inventory.filter(x=>/\.m?js$/.test(x.path));
 if(!javascript.length)errors.push('MISSING_BUNDLED_JS');
 const jsText=(await Promise.all(javascript.map(x=>readFile(resolve(root,x.path),'utf8')))).join('\n');
 for(const feed of ['latest.json','compass.json','publication-lineage.json'])
  if(!jsText.includes(feed))errors.push('MISSING_FIRST_PARTY_FEED_REFERENCE:'+feed);
 // HTML singletons are insufficient: fail if Vite emitted an empty or
 // chart-only JS bundle instead of the actual protected PRO source controller.
 for(const marker of [
  'premium-now-action','pro-reentry-state','source-trace-body',
  'CN_VNEXT_PUBLIC_FEED_PARITY_v1','OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1'
 ])if(!jsText.includes(marker))errors.push('MISSING_UNIFIED_PRO_JS_BINDING:'+marker);
 if(errors.length)throw Error('NEXT_VITE_ARTIFACT_INVALID:'+errors.join(';'));
 return {contract:'CN_NEXT_VITE_ARTIFACT_CHECK_v1',status:'PASS',
  output_root:'site/dist/next',base,entrypoints:mandatory,asset_count:inventory.length,
  assets:inventory.sort((a,b)=>a.path.localeCompare(b.path)),canonical_homepage_modified:false};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 verifyViteOutput().then(x=>console.log(JSON.stringify(x,null,2)))
  .catch(e=>{console.error(e.message);process.exitCode=1});
}
