// Offline Node 20+ regression tests for v1.1: synthetic Git objects, never private data.
import {mkdtempSync,mkdirSync,writeFileSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {execFileSync,spawnSync} from 'node:child_process';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const dir=mkdtempSync(join(tmpdir(),'task2-r0-v11-'));let count=0;
function git(...args){return execFileSync('git',args,{cwd:dir,encoding:'utf8'}).trim()}
function run(inv,head,tree){writeFileSync(join(dir,'inventory.json'),JSON.stringify(inv));return spawnSync(process.execPath,[fileURLToPath(new URL('./2026-10-14__task2_r0_git_object_reconcile_v1_1.mjs',import.meta.url)),'--inventory',join(dir,'inventory.json'),'--head',head,'--expected-tree',tree,'--repo-dir',dir],{encoding:'utf8'});}
function test(name,runTest){runTest();count++;process.stdout.write('PASS '+name+'\n')}
try{
  git('init','-q');git('config','user.email','r0-test@example.invalid');git('config','user.name','R0 Test');
  mkdirSync(join(dir,'fixture'));writeFileSync(join(dir,'fixture','a.json'),'A');writeFileSync(join(dir,'gone.json'),'gone');git('add','.');git('commit','-qm','base');
  const base=git('rev-parse','HEAD'),baseTree=git('rev-parse',base+'^{tree}');
  const objA=git('rev-parse',base+':fixture/a.json'),objDir=git('rev-parse',base+':fixture'),objGone=git('rev-parse',base+':gone.json');
  const inventory={contract:'TASK2_R0_PUBLIC_SOURCE_INVENTORY_v1',main_commit:base,main_tree:baseTree,families:[
    {id:'A',sources:[{path:'fixture/a.json',git_object_sha:objA,git_object_type:'blob'},{path:'gone.json',git_object_sha:objGone,git_object_type:'blob'},{path:'fixture/',git_object_sha:objDir,git_object_type:'tree'}]},
    {id:'SHARED',sources:[{path:'fixture/a.json',git_object_sha:objA,git_object_type:'blob'}]}]};
  writeFileSync(join(dir,'fixture','a.json'),'B');rmSync(join(dir,'gone.json'));git('add','-A');git('commit','-qm','head');const head=git('rev-parse','HEAD'),tree=git('rev-parse',head+'^{tree}');
  test('valid anchored drift, missing, shared refs',()=>{const r=run(inventory,head,tree);assert.equal(r.status,2);const d=JSON.parse(r.stdout);assert.equal(d.counts.CHANGED,2);assert.equal(d.counts.MISSING,1);assert.equal(d.source_references,4);assert.equal(d.distinct_source_paths,3);assert.equal(d.original_pinned_source_objects_verified,true)});
  test('tampered original SHA rejected',()=>{const d=structuredClone(inventory);d.families[0].sources[0].git_object_sha='0'.repeat(40);d.families[1].sources[0].git_object_sha='0'.repeat(40);const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Original pinned source SHA\/type mismatch/)});
  test('tampered original type rejected',()=>{const d=structuredClone(inventory);d.families[0].sources[0].git_object_type='tree';d.families[1].sources[0].git_object_type='tree';const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Original pinned source SHA\/type mismatch/)});
  test('missing original path rejected',()=>{const d=structuredClone(inventory);d.families[0].sources[0].path='ghost.json';d.families[1].sources[0].path='ghost.json';const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Original pinned source object missing/)});
  test('wrong independently expected tree rejected',()=>{const r=run(inventory,head,baseTree);assert.equal(r.status,1);assert.match(r.stderr,/Current pinned root-tree SHA mismatch/)});
  test('moving HEAD identifier rejected',()=>{const r=run(inventory,'HEAD',tree);assert.equal(r.status,1);assert.match(r.stderr,/exact 40-digit lowercase SHA/)});
  test('non-ancestor head rejected',()=>{const d=structuredClone(inventory);d.main_commit=head;d.main_tree=tree;const r=run(d,base,baseTree);assert.equal(r.status,1);assert.match(r.stderr,/not descended/)});
  test('conflicting shared path rejected',()=>{const d=structuredClone(inventory);d.families[1].sources[0].git_object_sha='b'.repeat(40);const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Conflicting shared source path/)});
  test('unsafe traversal path rejected',()=>{const d=structuredClone(inventory);d.families[0].sources[0].path='../private.json';const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Invalid source path/)});
  test('newline path rejected',()=>{const d=structuredClone(inventory);d.families[0].sources[0].path='bad\nname';const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Invalid source path/)});
  test('empty source-family census fails closed',()=>{const d=structuredClone(inventory);d.families=[];const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Empty source-family inventory/)});
  test('empty family source list fails closed',()=>{const d=structuredClone(inventory);d.families[0].sources=[];const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Empty source family/)});
  test('duplicate family identifier fails closed',()=>{const d=structuredClone(inventory);d.families[1].id='A';const r=run(d,head,tree);assert.equal(r.status,1);assert.match(r.stderr,/Duplicate source family/)});
  test('same original commit and tree succeeds',()=>{const r=run(inventory,base,baseTree);assert.equal(r.status,0,r.stderr);const j=JSON.parse(r.stdout);assert.equal(j.verified_all_paths,true);assert.equal(j.counts.UNCHANGED,3)});
  test('replacement object cannot forge ancestry',()=>{const target=git('commit-tree',baseTree,'-m','unrelated-root');const replacement=git('commit-tree',baseTree,'-p',base,'-m','replacement-with-parent');git('replace',target,replacement);try{const falsifier=spawnSync('git',['merge-base','--is-ancestor',base,target],{cwd:dir});assert.equal(falsifier.status,0);const corrected=run(inventory,target,baseTree);assert.equal(corrected.status,1,corrected.stdout);assert.match(corrected.stderr,/not descended/)}finally{git('replace','-d',target)}});
  test('legacy graft cannot forge ancestry even with --no-replace-objects',()=>{const target=git('commit-tree',baseTree,'-m','unrelated-root-graft');const graftPath=join(dir,git('rev-parse','--git-path','info/grafts'));writeFileSync(graftPath,target+' '+base+'\n');try{const vulnerable=spawnSync('git',['--no-replace-objects','merge-base','--is-ancestor',base,target],{cwd:dir});assert.equal(vulnerable.status,0);const guarded=run(inventory,target,baseTree);assert.equal(guarded.status,1,guarded.stdout);assert.match(guarded.stderr,/Legacy Git grafts present/)}finally{rmSync(graftPath,{force:true})}});
  test('annotated-tag SHA is not direct commit',()=>{git('tag','-a','r0-test-annotated','-m','tag object',base);const tag=git('rev-parse','refs/tags/r0-test-annotated');assert.equal(git('cat-file','-t',tag),'tag');const r=run(inventory,tag,baseTree);assert.equal(r.status,1);assert.match(r.stderr,/direct commit/)});
  test('file URL path decodes spaces',()=>{const u=new URL('./synthetic%20space/script.mjs',import.meta.url);assert.ok(fileURLToPath(u).includes('synthetic space'))});
  console.log('ALL '+count+' R0 v1.1 TESTS PASS (synthetic Git fixture only)');
}finally{rmSync(dir,{recursive:true,force:true})}
