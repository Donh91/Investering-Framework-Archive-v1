// Research-only, dependency-free, exact-commit Git-object reconciliation. Node 20+.
// Usage: node script.mjs --inventory path.json --head <40hex> --expected-tree <40hex> [--repo-dir checkout]
// No moving HEAD or branch references accepted for --head. No historical PIT admission implied.
import fs from 'node:fs';
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
function reconcile(inventory,head,expectedTree,git){
  if(!inventory||!HEX40.test(inventory.main_commit)||!HEX40.test(inventory.main_tree)||!Array.isArray(inventory.families))throw Error('Invalid immutable inventory anchor');
  if(git(['cat-file','-t',inventory.main_commit])!=='commit'||git(['cat-file','-t',head])!=='commit')throw Error('Pinned anchors must name direct commit objects');
  if(git(['rev-parse','--verify',inventory.main_commit+'^{tree}'])!==inventory.main_tree)throw Error('Pinned inventory root-tree SHA mismatch');
  if(git(['rev-parse','--verify',head+'^{tree}'])!==expectedTree)throw Error('Current pinned root-tree SHA mismatch');
  try{git(['merge-base','--is-ancestor',inventory.main_commit,head]);}catch{throw Error('Compared commit is not descended from pinned inventory');}
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
    let sha=null,type=null;
    try{sha=git(['rev-parse','--verify',head+':'+path]);type=git(['cat-file','-t',sha]);}catch{}
    return {...row,checked_object_sha:sha,status:!sha?'MISSING':type!==row.type?'TYPE_MISMATCH':sha===row.pinned_object_sha?'UNCHANGED':'CHANGED'};
  });
  rows.sort((a,b)=>a.path.localeCompare(b.path));
  const counts=Object.fromEntries(['CHANGED','UNCHANGED','MISSING','TYPE_MISMATCH'].map(s=>[s,rows.filter(x=>x.status===s).length]));
  return {contract:'TASK2_R0_GIT_OBJECT_RECONCILIATION_v1_1',original_pinned_source_objects_verified:true,scope:'PUBLIC_GIT_OBJECTS_ONLY_NOT_MARKET_PIT',inventory_base_commit:inventory.main_commit,inventory_base_tree:inventory.main_tree,compared_commit:head,compared_tree:expectedTree,family_count:families.length,source_references:refs,distinct_source_paths:rows.length,counts,verified_all_paths:counts.MISSING===0&&counts.TYPE_MISMATCH===0,rows,market_first_known_admitted:false,economic_edge_established:false};
}
try{
  const a=parseArgs(process.argv.slice(2));const cwd=a['--repo-dir']||process.cwd();
  const git=(args)=>execFileSync('git',['--no-replace-objects',...args],{cwd,encoding:'utf8',stdio:['ignore','pipe','pipe'],maxBuffer:2e6}).trim();
  // --no-replace-objects does NOT disable legacy .git/info/grafts; grafts can forge ancestry.
  // Fail closed in such repositories instead of accepting a synthetic parent relationship.
  const graftPath=path.resolve(cwd,git(['rev-parse','--git-path','info/grafts']));
  try {fs.lstatSync(graftPath);throw Error('Legacy Git grafts present: source ancestry untrustworthy');}
  catch (e) {if(e.code!=='ENOENT')throw e;}
  if(git(['rev-parse','--is-shallow-repository'])!=='false')throw Error('Shallow Git repository: complete ancestry unavailable');
  const inv=JSON.parse(fs.readFileSync(a['--inventory'],'utf8'));
  const result=reconcile(inv,a['--head'],a['--expected-tree'],git);
  process.stdout.write(JSON.stringify(result,null,2)+'\n');if(!result.verified_all_paths)process.exitCode=2;
}catch(e){process.stderr.write('TASK2_R0_RECONCILIATION_BLOCKED: '+e.message+'\n');process.exitCode=1;}
