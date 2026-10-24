// Research-only, dependency-free, exact-commit Git-object reconciliation. Node 20+.
// Usage: node script.mjs --inventory path.json --head <40hex> --expected-tree <40hex> [--repo-dir checkout]
// No moving HEAD or branch references accepted for --head. No historical PIT admission implied.
import fs from 'node:fs';
import os from 'node:os';
import {createHash} from 'node:crypto';
import path from 'node:path';
import { execFileSync } from 'node:child_process';
const HEX40=/^[0-9a-f]{40}$/;
function parseArgs(argv){
  const allowed=new Set(['--inventory','--head','--expected-tree','--repo-dir']);
  if(argv.length%2!==0)throw Error('Expected flag/value pairs');
  const o={};for(let i=0;i<argv.length;i+=2){if(!allowed.has(argv[i])||Object.hasOwn(o,argv[i]))throw Error('Unknown/repeated arg: '+argv[i]);o[argv[i]]=argv[i+1];}
  for(const k of ['--inventory','--head','--expected-tree'])if(!o[k])throw Error('Missing '+k);
  for(const k of ['--head','--expected-tree'])if(!HEX40.test(o[k]))throw Error(k+' must be exact 40-digit lowercase SHA; moving refs disallowed');
  return o;
}
function checkPath(p){return typeof p==='string'&&p.length>0&&!p.startsWith('/')&&!p.includes('\\')&&!p.includes(':')&&!p.includes('\n')&&!p.includes('//')&&!p.split('/').includes('..')&&!p.split('/').includes('.')}
function targetObject(head,p,git,verifyObject){
  let listing;
  try{listing=git(['ls-tree','-z',head,'--',':(literal)'+p]);}
  catch{throw Error('Unreadable target tree/object: '+p);}
  if(!listing)return null; // Only an intact target tree can prove a genuine missing path.
  const entries=listing.split('\0').filter(Boolean);
  const match=entries.length===1&&/^([0-7]{6}) (blob|tree|commit) ([0-9a-f]{40})\t(.+)$/u.exec(entries[0]);
  if(!match||match[4]!==p)throw Error('Ambiguous target path lookup: '+p);
  try{if(git(['cat-file','-t',match[3]])!==match[2])throw Error('Object type differs from tree entry');verifyObject(match[2],match[3]);}
  catch{throw Error('Unreadable target tree/object: '+p);}
  return {sha:match[3],type:match[2]};
}
function reconcile(inventory,head,expectedTree,git,verifyObject){
  if(!inventory||!HEX40.test(inventory.main_commit)||!HEX40.test(inventory.main_tree)||!Array.isArray(inventory.families))throw Error('Invalid immutable inventory anchor');
  if(git(['cat-file','-t',inventory.main_commit])!=='commit'||git(['cat-file','-t',head])!=='commit')throw Error('Pinned anchors must name direct commit objects');
  if(git(['rev-parse','--verify',inventory.main_commit+'^{tree}'])!==inventory.main_tree)throw Error('Pinned inventory root-tree SHA mismatch');
  if(git(['rev-parse','--verify',head+'^{tree}'])!==expectedTree)throw Error('Current pinned root-tree SHA mismatch');
  try{git(['merge-base','--is-ancestor',inventory.main_commit,head]);}
  catch(e){
    // Git's documented exit 1 denotes a genuine non-descendant. Fatal
    // subprocess failures (e.g. 128) are UNKNOWN, never source genealogy.
    if(e?.status===1)throw Error('Compared commit is not descended from pinned inventory');
    throw Error('Ancestry Git operation unverified');
  }
  if(inventory.families.length===0)throw Error('Empty source-family inventory');
  const indexed=new Map(),families=[];let refs=0;const seenFamilyIds=new Set();
  for(const family of inventory.families){if(!family||typeof family.id!=='string'||!family.id||!Array.isArray(family.sources))throw Error('Invalid source family');
    if(family.sources.length===0)throw Error('Empty source family: '+family.id);
    if(seenFamilyIds.has(family.id))throw Error('Duplicate source family: '+family.id);
    seenFamilyIds.add(family.id);families.push(family.id);
    for(const s of family.sources){refs++;if(!checkPath(s.path)||!HEX40.test(s.git_object_sha)||!['tree','blob'].includes(s.git_object_type))throw Error('Invalid source path/SHA/type');
      const norm=s.path.replace(/\/$/,'');let r=indexed.get(norm);if(r){if(r.pinned_object_sha!==s.git_object_sha||r.type!==s.git_object_type)throw Error('Conflicting shared source path: '+norm);r.families.push(family.id);}
      else indexed.set(norm,{path:s.path,type:s.git_object_type,pinned_object_sha:s.git_object_sha,families:[family.id]});
    }
  }
  if(refs===0||indexed.size===0)throw Error('Vacuous source inventory');
  const rows=[...indexed.values()].map(row=>{
    const path=row.path.replace(/\/$/,'');
    let oldSha,oldType;
    try{oldSha=git(['rev-parse','--verify',inventory.main_commit+':'+path]);oldType=git(['cat-file','-t',oldSha]);}
    catch{throw Error('Original pinned source object missing: '+path);}
    if(oldSha!==row.pinned_object_sha||oldType!==row.type)throw Error('Original pinned source SHA/type mismatch: '+path);
    try{verifyObject(oldType,oldSha);}catch{throw Error('Original pinned source object unreadable or hash mismatch: '+path);}
    const target=targetObject(head,path,git,verifyObject);
    const sha=target?.sha??null,type=target?.type??null;
    return {...row,checked_object_sha:sha,status:!sha?'MISSING':type!==row.type?'TYPE_MISMATCH':sha===row.pinned_object_sha?'UNCHANGED':'CHANGED'};
  });
  rows.sort((a,b)=>Buffer.compare(Buffer.from(a.path,'utf8'),Buffer.from(b.path,'utf8')));
  const counts=Object.fromEntries(['CHANGED','UNCHANGED','MISSING','TYPE_MISMATCH'].map(s=>[s,rows.filter(x=>x.status===s).length]));
  // A source switching Git object kind is not an ordinary content drift.
  // It invalidates the registered source contract: fail operationally closed
  // rather than returning the same drift exit code as a missing source.
  if(counts.TYPE_MISMATCH>0)throw Error('Compared source object TYPE_MISMATCH: '+rows.filter(x=>x.status==='TYPE_MISMATCH').map(x=>x.path).join(', '));
  return {contract:'TASK2_R0_GIT_OBJECT_RECONCILIATION_v1_1',original_pinned_source_objects_verified:true,scope:'PUBLIC_GIT_OBJECTS_ONLY_NOT_MARKET_PIT',inventory_base_commit:inventory.main_commit,inventory_base_tree:inventory.main_tree,compared_commit:head,compared_tree:expectedTree,family_count:families.length,source_references:refs,distinct_source_paths:rows.length,counts,verified_all_paths:counts.MISSING===0&&counts.TYPE_MISMATCH===0,verified_unchanged_source_set:counts.CHANGED===0&&counts.MISSING===0&&counts.TYPE_MISMATCH===0,rows,market_first_known_admitted:false,economic_edge_established:false};
}
try{
  const a=parseArgs(process.argv.slice(2));const cwd=a['--repo-dir']||process.cwd();
  // Don't let inherited GIT_DIR/GIT_WORK_TREE/GIT_CONFIG_* redirect a
  // purported exact-checkout verification to another repository.
  const gitEnv={...process.env};
  for(const key of Object.keys(gitEnv))if(key.startsWith('GIT_'))delete gitEnv[key];
  gitEnv.GIT_CONFIG_NOSYSTEM='1';
  gitEnv.GIT_CONFIG_GLOBAL=os.devnull;
  const git=(args,discardOutput=false)=>{const result=execFileSync('git',['--no-replace-objects',...args],{cwd,env:gitEnv,encoding:'utf8',stdio:['ignore',discardOutput?'ignore':'pipe','pipe'],maxBuffer:2e6});return result?.trim()||'';};
  // --no-replace-objects does NOT disable legacy .git/info/grafts; grafts can forge ancestry.
  // Fail closed in such repositories instead of accepting a synthetic parent relationship.
  const graftPath=path.resolve(cwd,git(['rev-parse','--git-path','info/grafts']));
  try {fs.lstatSync(graftPath);throw Error('Legacy Git grafts present: source ancestry untrustworthy');}
  catch (e) {if(e.code!=='ENOENT')throw e;}
  if(git(['rev-parse','--is-shallow-repository'])!=='false')throw Error('Shallow Git repository: complete ancestry unavailable');
  // Git cat-file may emit readable bytes from a loose object under the WRONG
  // SHA filename. Validate canonical Git type+length+raw bytes independently.
  // Spill to a temporary file and hash in chunks: no unbounded stdout buffer,
  // no shell pipeline or content printed into public logs.
  const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'task2-r0-verify-'));
  const verifyObject=(type,sha)=>{
    if(!['blob','tree'].includes(type)||!HEX40.test(sha))throw Error('Invalid object identity');
    const pathname=path.join(scratch,'object.bin');
    const fd=fs.openSync(pathname,'w+');
    try{
      execFileSync('git',['--no-replace-objects','cat-file',type,sha],{
        cwd,env:gitEnv,stdio:['ignore',fd,'pipe'],maxBuffer:2e6
      });
      const size=fs.fstatSync(fd).size;
      const h=createHash('sha1').update(Buffer.from(type+' '+size+'\0'));
      const chunk=Buffer.allocUnsafe(65536);
      for(let offset=0;offset<size;){
        const n=fs.readSync(fd,chunk,0,Math.min(chunk.length,size-offset),offset);
        if(n===0)throw Error('Incomplete Git object content');
        h.update(chunk.subarray(0,n));offset+=n;
      }
      if(h.digest('hex')!==sha)throw Error('Git object hash-path mismatch');
    }finally{fs.closeSync(fd);}
  };
  let result;
  try{
    const inv=JSON.parse(fs.readFileSync(a['--inventory'],'utf8'));
    result=reconcile(inv,a['--head'],a['--expected-tree'],git,verifyObject);
  }finally{fs.rmSync(scratch,{recursive:true,force:true});}
  process.stdout.write(JSON.stringify(result,null,2)+'\n');if(!result.verified_unchanged_source_set)process.exitCode=2;
}catch(e){process.stderr.write('TASK2_R0_RECONCILIATION_BLOCKED: '+e.message+'\n');process.exitCode=1;}
