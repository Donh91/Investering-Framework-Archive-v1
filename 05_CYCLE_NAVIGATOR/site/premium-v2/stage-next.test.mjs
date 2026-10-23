import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {snapshotProtected,assertUnchanged,protectedPaths,stageNext} from './stage-next.mjs';

async function withProtected(fn){
 const dir=await mkdtemp(join(tmpdir(),'cn-next-preserve-'));
 try{
  for(const path of protectedPaths){
   await mkdir(dirname(join(dir,path)),{recursive:true});
   await writeFile(join(dir,path),'original:'+path);
  }
  await fn(dir);
 }finally{await rm(dir,{recursive:true,force:true})}
}
test('isolated staging records exact canonical root, legacy, vnext and all public source hashes',async()=>{
 await withProtected(async dir=>{
  const before=await snapshotProtected(dir);
  assert.equal(Object.keys(before).length,6);
  assert.ok(Object.values(before).every(x=>/^[a-f0-9]{64}$/.test(x)));
  assertUnchanged(before,await snapshotProtected(dir));
 });
});
test('changing even a single official data source is not a legal NEXT-only staging build',async()=>{
 await withProtected(async dir=>{
  const original=await snapshotProtected(dir);
  await writeFile(join(dir,'data/compass.json'),'tampered');
  assert.throws(()=>assertUnchanged(original,await snapshotProtected(dir)),/CANONICAL_PAGES_ARTIFACT_CHANGED:data\/compass.json/);
 });
});
test('missing public lineage or legacy shell fails closed before staging',async()=>{
 await withProtected(async dir=>{
  await rm(join(dir,'data/publication-lineage.json'));
  await assert.rejects(snapshotProtected(dir),/CANONICAL_PAGES_ARTIFACT_MISSING:data\/publication-lineage.json/);
 });
});
test('missing reviewed package lock blocks npm staging before any subprocess starts',async()=>{
 let calls=0;
 await assert.rejects(stageNext({run:()=>{calls++},lockfile:'/definitely-missing-reviewed-next-package-lock.json'}),/NEXT_STAGE_REVIEWED_PACKAGE_LOCK_REQUIRED/);
 assert.equal(calls,0);
});
