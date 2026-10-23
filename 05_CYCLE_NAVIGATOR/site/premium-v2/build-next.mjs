/**
 * Premium v2.1 noncanonical static B+Proof staging bundle, manual invocation.
 * No production root/data changes. DO NOT include quarantined AppDeploy demo JS.
 */
import {fileURLToPath} from 'node:url';
import {dirname,resolve,relative} from 'node:path';
import {readFile,writeFile,mkdir} from 'node:fs/promises';
const here=dirname(fileURLToPath(import.meta.url));
const site=resolve(here,'..');
export const approvedAssets=[
 'graph-b/source-graph-b.html',
 'graph-b/source-graph-b.css',
 'graph-b/source-graph-b.mjs',
 'graph-b/official-source-adapter.mjs',
 'proof/proof-explorer.css',
 'proof/proof-explorer.mjs',
 'proof/price-range-proof.mjs',
 'proof/public-source-links.mjs',
 'compass/compass-path.css',
 'compass/compass-path-ui.mjs',
 'compass/official-compass-path.mjs',
 'assets/CN_LOGO.svg'
];
export function stagingPlan(){
 const from=resolve(site,'premium-v2'),to=resolve(site,'dist','next');
 if(relative(resolve(site,'dist'),to)!=='next')throw Error('NEXT_DEPLOYMENT_OUT_OF_SANDBOX');
 if(new Set(approvedAssets).size!==approvedAssets.length)throw Error('DUPLICATE_ALLOWLIST');
 if(approvedAssets.some(f=>f.startsWith('/')||f.includes('..')||f.includes('reference')||!/^[-/.a-z0-9]+$/.test(f)))
  throw Error('QUARANTINED_ASSET_IMPORT_FORBIDDEN');
 return{from,to,assets:approvedAssets};
}
export async function buildNext(){
 const plan=stagingPlan();
 const contents=await Promise.all(plan.assets.map(async asset=>{
  const data=await readFile(resolve(plan.from,asset));
  if(/\bMath\.sin\s*\(/.test(data.toString('utf8')))throw Error('SYNTHETIC_DATA_IN_DEPLOY_BUNDLE:'+asset);
  return{asset,data};
 }));
 for(const{asset,data}of contents){
  const target=resolve(plan.to,asset);
  await mkdir(dirname(target),{recursive:true});await writeFile(target,data);
 }
 await mkdir(plan.to,{recursive:true});
 const index='<!doctype html><html lang="da"><head><meta charset="utf-8">'+
  '<meta name="viewport" content="width=device-width,initial-scale=1">'+
  '<meta name="robots" content="noindex,nofollow">'+
  '<title>Cycle Navigator · Isolated NEXT</title></head><body><main>'+
  '<p>Udviklingstest, ikke den officielle Cycle Navigator.</p>'+
  '<a href="./graph-b/source-graph-b.html">Åbn isoleret graf B + Proof →</a>'+
  '</main></body></html>';
 await writeFile(resolve(plan.to,'index.html'),index,'utf8');
 console.log(JSON.stringify({contract:'CN_PREMIUM_V2_NEXT_STAGING_BUNDLE_v1',
  mode:'NONCANONICAL_NEXT_ONLY',copied:contents.map(x=>x.asset),output:plan.to,
  official_homepage_untouched:true,synthetic_demo_source_copied:false}));
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 buildNext().catch(error=>{console.error(String(error));process.exitCode=1});
}
