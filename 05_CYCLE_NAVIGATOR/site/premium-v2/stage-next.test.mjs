import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {join,dirname} from 'node:path';
import {tmpdir} from 'node:os';
import {snapshotProtected,assertUnchanged,snapshotCanonicalTree,assertCanonicalTreeUnchanged,protectedPaths,stageNext} from './stage-next.mjs';

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
  const modified=await snapshotProtected(dir);
  assert.throws(()=>assertUnchanged(original,modified),/CANONICAL_PAGES_ARTIFACT_CHANGED:data\/compass.json/);
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

test('NEXT-only addition preserves all public asset hashes and manifest names',async()=>{
 await withProtected(async dir=>{
  await mkdir(join(dir,'assets'),{recursive:true});
  await writeFile(join(dir,'assets/root-script.js'),'export const live = true');
  const before=await snapshotCanonicalTree(dir);
  await mkdir(join(dir,'next/assets'),{recursive:true});
  await writeFile(join(dir,'next/index.html'),'<main>NEW PREMIUM</main>');
  await writeFile(join(dir,'next/assets/app.js'),'export const premium = true');
  const after=await snapshotCanonicalTree(dir);
  assertCanonicalTreeUnchanged(before,after);
  assert.equal(Object.keys(after).length,protectedPaths.length+1);
  assert.ok(!Object.keys(after).some(name=>name.startsWith('next/')));
 });
});
test('a missing or changed unlisted canonical CSS/JS asset blocks staging',async()=>{
 await withProtected(async dir=>{
  await mkdir(join(dir,'assets'),{recursive:true});
  await writeFile(join(dir,'assets/original.css'),'body{color:#07172f}');
  const baseline=await snapshotCanonicalTree(dir);
  await writeFile(join(dir,'assets/original.css'),'body{color:red}');
  const changedCss=await snapshotCanonicalTree(dir);
  assert.throws(()=>assertCanonicalTreeUnchanged(baseline,changedCss),
   /CANONICAL_PAGES_BUNDLE_CHANGED:assets\/original.css/);
  await rm(join(dir,'assets/original.css'));
  const missingCss=await snapshotCanonicalTree(dir);
  assert.throws(()=>assertCanonicalTreeUnchanged(baseline,missingCss),
   /CANONICAL_PAGES_BUNDLE_CHANGED:assets\/original.css/);
 });
});
test('a new non-NEXT root artifact cannot silently enter the public site',async()=>{
 await withProtected(async dir=>{
  const baseline=await snapshotCanonicalTree(dir);
  await writeFile(join(dir,'unauthorized.js'),'console.log("added")');
  const added=await snapshotCanonicalTree(dir);
  assert.throws(()=>assertCanonicalTreeUnchanged(baseline,added),
   /CANONICAL_PAGES_BUNDLE_CHANGED:unauthorized.js/);
 });
});
test('malicious symbolic links fail the complete public bundle snapshot',async t=>{
 const {symlink}=await import('node:fs/promises');
 await withProtected(async dir=>{
  try{await symlink('/etc/passwd',join(dir,'unexpected-link'))}
  catch(e){if(['EPERM','EACCES','ENOTSUP'].includes(e.code)){t.skip('environment denies symlinks');return;}throw e}
  await assert.rejects(snapshotCanonicalTree(dir),/PAGES_BUNDLE_UNSAFE_FILE:unexpected-link/);
 });
});
