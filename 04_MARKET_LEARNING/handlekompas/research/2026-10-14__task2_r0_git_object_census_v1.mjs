// Task 2 R0 Git-object census; public metadata only, no PIT or edge admission.
// Node 20+. Requires a checkout with both explicitly pinned commits.
// Usage:
// node 2026-10-14__task2_r0_git_object_census_v1.mjs --inventory PATH --baseline SHA40 --current SHA40
// node 2026-10-14__task2_r0_git_object_census_v1.mjs --self-test
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,mkdtempSync,mkdirSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import assert from 'node:assert/strict';
const RE_SHA=/^[a-f0-9]{40}$/;
function sha(x){if(!RE_SHA.test(x??''))throw Error('INVALID_PINNED_SHA');return x;}
function pathSafe(p){if(typeof p!=='string'||!/^[A-Za-z0-9_.\/-]+$/.test(p)||p.startsWith('/')||p.includes('..')||p.includes('//'))throw Error('INVALID_PATH');return p.endsWith('/')?p.slice(0,-1):p;}
function git(argv,cwd,optional=false){const x=spawnSync('git',argv,{cwd,encoding:'utf8',timeout:15000});if(x.error||(!optional&&x.status!==0))throw Error('GIT_FAILED: '+argv[0]);return x.status===0?x.stdout.trim():null;}
function objectAt(commit,path,cwd){const id=git(['rev-parse','--verify',sha(commit)+':'+pathSafe(path)],cwd,true);if(!id)return null;const type=git(['cat-file','-t',id],cwd);if(!['tree','blob'].includes(type))throw Error('BAD_OBJECT_TYPE');return{sha:sha(id),type};}
export function census(inv,baseline,current,cwd=process.cwd()){
  sha(baseline);sha(current);
  if(!inv||inv.contract!=='TASK2_R0_PUBLIC_SOURCE_INVENTORY_v1'||!Array.isArray(inv.families)||inv.main_commit!==baseline||!RE_SHA.test(inv.main_tree??''))throw Error('MANIFEST_BASE_MISMATCH');
  const baselineTree=sha(git(['rev-parse','--verify',baseline+'^{tree}'],cwd));
  if(baselineTree!==inv.main_tree)throw Error('ROOT_TREE_MISMATCH');
  git(['rev-parse','--verify',current+'^{commit}'],cwd);
  const unique=new Map();let references=0;
  for(const family of inv.families){
    if(typeof family.id!=='string'||!Array.isArray(family.sources))throw Error('BAD_FAMILY');
    for(const s of family.sources){
      references++;const p=pathSafe(s.path);sha(s.git_object_sha);
      if(!['tree','blob'].includes(s.git_object_type))throw Error('BAD_MANIFEST_TYPE');
      const old=unique.get(p);
      if(old){if(old.original_sha!==s.git_object_sha||old.type!==s.git_object_type)throw Error('DUPLICATE_CONFLICT');old.families.push(family.id);}
      else unique.set(p,{path:s.path,original_sha:s.git_object_sha,type:s.git_object_type,families:[family.id]});
    }
  }
  const objects=[...unique.values()].sort((a,b)=>a.path.localeCompare(b.path)).map(s=>{
    const before=objectAt(baseline,s.path,cwd);
    if(!before||before.sha!==s.original_sha||before.type!==s.type)throw Error('BASELINE_SOURCE_MISMATCH: '+s.path);
    const after=objectAt(current,s.path,cwd);
    const state=!after?'MISSING':after.type!==s.type?'TYPE_CHANGED':after.sha===before.sha?'UNCHANGED':'CHANGED';
    return{...s,current_sha:after?.sha??null,current_type:after?.type??null,state};
  });
  const counts=Object.fromEntries(['CHANGED','UNCHANGED','MISSING','TYPE_CHANGED'].map(k=>[k,objects.filter(s=>s.state===k).length]));
  return{contract:'TASK2_R0_GIT_OBJECT_CENSUS_v1',scope:'PUBLIC_OBJECT_IDENTITY_NOT_PIT_ADMISSION',baseline_main_sha:baseline,baseline_tree_sha:baselineTree,current_main_sha:current,families:inv.families.length,source_references:references,distinct_paths:objects.length,counts,provider_first_known:'NOT_ADJUDICATED',historical_simulations_executed:0,signal_promotion:false,objects};
}
function test(){
  const cwd=mkdtempSync(join(tmpdir(),'task2-r0-'));
  try{
    git(['init','-q'],cwd);git(['config','user.name','R0 Fixture'],cwd);git(['config','user.email','r0@example.invalid'],cwd);
    mkdirSync(join(cwd,'data'));writeFileSync(join(cwd,'data','a.json'),'a\n');
    git(['add','.'],cwd);git(['commit','-qm','a'],cwd);
    const baseline=git(['rev-parse','HEAD'],cwd),tree=git(['rev-parse','HEAD^{tree}'],cwd);
    const d=objectAt(baseline,'data/',cwd),a=objectAt(baseline,'data/a.json',cwd);
    const inv={contract:'TASK2_R0_PUBLIC_SOURCE_INVENTORY_v1',main_commit:baseline,main_tree:tree,families:[{id:'X',sources:[{path:'data/',git_object_sha:d.sha,git_object_type:'tree'},{path:'data/a.json',git_object_sha:a.sha,git_object_type:'blob'}]},{id:'Y',sources:[{path:'data/',git_object_sha:d.sha,git_object_type:'tree'}]}]};
    let r=census(inv,baseline,baseline,cwd);assert.equal(r.counts.UNCHANGED,2);assert.equal(r.source_references,3);
    writeFileSync(join(cwd,'data','a.json'),'b\n');git(['add','.'],cwd);git(['commit','-qm','b'],cwd);let head=git(['rev-parse','HEAD'],cwd);
    r=census(inv,baseline,head,cwd);assert.equal(r.counts.CHANGED,2);
    assert.throws(()=>census({...inv,main_tree:'0'.repeat(40)},baseline,head,cwd),/ROOT_TREE_MISMATCH/);
    assert.throws(()=>census({...inv,main_commit:head},baseline,head,cwd),/MANIFEST_BASE_MISMATCH/);
    assert.throws(()=>census({...inv,families:[{id:'bad',sources:[{path:'../oops',git_object_sha:a.sha,git_object_type:'blob'}]}]},baseline,head,cwd),/INVALID_PATH/);
    assert.throws(()=>census({...inv,families:[{id:'bad',sources:[{path:'data/a.json',git_object_sha:'f'.repeat(40),git_object_type:'blob'}]}]},baseline,head,cwd),/BASELINE_SOURCE_MISMATCH/);
    rmSync(join(cwd,'data','a.json'));git(['add','-A'],cwd);git(['commit','-qm','removed'],cwd);
    const deleted={...inv,families:[{id:'M',sources:[{path:'data/a.json',git_object_sha:a.sha,git_object_type:'blob'}]}]};
    assert.equal(census(deleted,baseline,git(['rev-parse','HEAD'],cwd),cwd).counts.MISSING,1);
    return{status:'PASS',synthetic_scenarios:7,historical_pit_admitted:false};
  }finally{rmSync(cwd,{recursive:true,force:true});}
}
const args=process.argv.slice(2);
if(args.length===1&&args[0]==='--self-test')console.log(JSON.stringify(test()));
else if(import.meta.url===new URL('file://'+process.argv[1]).href){
  const flag=k=>{const i=args.indexOf(k);if(i<0||!args[i+1])throw Error('MISSING '+k);return args[i+1];};
  const inv=JSON.parse(readFileSync(flag('--inventory'),'utf8'));
  const result=census(inv,flag('--baseline'),flag('--current'));
  if(args.includes('--out'))writeFileSync(flag('--out'),JSON.stringify(result,null,2)+'\n');
  else console.log(JSON.stringify(result,null,2));
}
