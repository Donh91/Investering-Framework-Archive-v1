/**
 * ONE existing Pages artifact, NEXT-only staging.
 * Run from EXISTING Pages job AFTER canonical build, lineage, score and social
 * stages, and BEFORE upload-pages-artifact. This script is NOT hooked to CI
 * until the exact-head lockfile, review, Actions budget and staging gates pass.
 */
import {readFile,readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,resolve,relative,sep} from 'node:path';
import {fileURLToPath} from 'node:url';
import {verifyViteOutput} from './verify-vite-output.mjs';

const here=dirname(fileURLToPath(import.meta.url));
const dist=resolve(here,'../dist');
export const protectedPaths=[
 'index.html','legacy/index.html','vnext/index.html',
 'data/latest.json','data/compass.json','data/publication-lineage.json'
];

export async function snapshotProtected(root=dist){
 const hashes={};
 for(const path of protectedPaths){
  let b;
  try{b=await readFile(resolve(root,path))}
  catch{throw Error('CANONICAL_PAGES_ARTIFACT_MISSING:'+path)}
  hashes[path]=createHash('sha256').update(b).digest('hex');
 }
 return hashes;
}
/**
 * Snapshot every non-NEXT byte in the public artifact, including files whose
 * names were not known at authoring time. A six-file sentinel by itself
 * cannot prevent silently deleting a canonical JS/CSS/scorecard asset.
 * NEXT is the ONLY allowed added/changed subtree.
 */
export async function snapshotCanonicalTree(root=dist){
 const base=resolve(root),result={};
 async function visit(folder){
  for(const entry of await readdir(folder,{withFileTypes:true})){
   const file=resolve(folder,entry.name);
   const path=relative(base,file).split(sep).join('/');
   if(path==='next')continue;
   if(path==='..'||path.startsWith('../'))throw Error('PAGES_BUNDLE_PATH_ESCAPE');
   if(entry.isDirectory()){await visit(file);continue}
   if(!entry.isFile())throw Error('PAGES_BUNDLE_UNSAFE_FILE:'+path);
   result[path]=createHash('sha256').update(await readFile(file)).digest('hex');
  }
 }
 await visit(base);
 if(!Object.keys(result).length)throw Error('CANONICAL_PAGES_BUNDLE_EMPTY');
 return result;
}
export function assertCanonicalTreeUnchanged(before,after){
 const names=new Set([...Object.keys(before),...Object.keys(after)]);
 for(const name of names){
  if(!before[name]||!after[name]||before[name]!==after[name])
   throw Error('CANONICAL_PAGES_BUNDLE_CHANGED:'+name);
 }
}

export function assertUnchanged(before,after){
 for(const path of protectedPaths){
  if(before[path]!==after[path]||!before[path])
   throw Error('CANONICAL_PAGES_ARTIFACT_CHANGED:'+path);
 }
}
function execute(bin,args){
 const x=spawnSync(bin,args,{cwd:here,stdio:'inherit',timeout:300000,env:process.env});
 if(x.error)throw x.error;
 if(x.status!==0)throw Error('NEXT_STAGE_COMMAND_FAILED:'+bin+' '+args.join(' ')+':'+x.status);
}
export async function stageNext({run=execute,lockfile=resolve(here,'package-lock.json')}={}){
 // No speculative npm installation or staging when the reviewed lockfile is missing.
 try{await readFile(lockfile)}
 catch{throw Error('NEXT_STAGE_REVIEWED_PACKAGE_LOCK_REQUIRED')}
 const before=await snapshotProtected();
 const fullBefore=await snapshotCanonicalTree();
 run('npm',['ci']);
 run('npm',['test']);
 run('npm',['run','build:next']);
 const manifest=await verifyViteOutput();
 const after=await snapshotProtected();
 const fullAfter=await snapshotCanonicalTree();
 assertUnchanged(before,after);
 assertCanonicalTreeUnchanged(fullBefore,fullAfter);
 return {...manifest,preservation:'ALL_NON_NEXT_ARTIFACT_HASHES_IDENTICAL',
  canonical_public_asset_count:Object.keys(fullBefore).length,
  stage:'NONCANONICAL_NEXT_ONLY',pages_workflow:'EXISTING_WORKFLOW_ONLY'};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 stageNext().then(x=>console.log(JSON.stringify(x,null,2)))
  .catch(e=>{console.error(e.message);process.exitCode=1});
}
