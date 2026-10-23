/**
 * ONE existing Pages artifact, NEXT-only staging.
 * Run from EXISTING Pages job AFTER canonical build, lineage, score and social
 * stages, and BEFORE upload-pages-artifact. This script is NOT hooked to CI
 * until the exact-head lockfile, review, Actions budget and staging gates pass.
 */
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {dirname,resolve} from 'node:path';
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
export async function stageNext({run=execute}={}){
 // No speculative npm installation or staging when the reviewed lockfile is missing.
 try{await readFile(resolve(here,'package-lock.json'))}
 catch{throw Error('NEXT_STAGE_REVIEWED_PACKAGE_LOCK_REQUIRED')}
 const before=await snapshotProtected();
 run('npm',['ci']);
 run('npm',['test']);
 run('npm',['run','build:next']);
 const manifest=await verifyViteOutput();
 const after=await snapshotProtected();
 assertUnchanged(before,after);
 return {...manifest,preservation:'SIX_CANONICAL_ARTIFACT_HASHES_IDENTICAL',
  stage:'NONCANONICAL_NEXT_ONLY',pages_workflow:'EXISTING_WORKFLOW_ONLY'};
}
if(process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 stageNext().then(x=>console.log(JSON.stringify(x,null,2)))
  .catch(e=>{console.error(e.message);process.exitCode=1});
}
