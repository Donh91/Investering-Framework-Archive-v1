import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {verifyViteOutput} from './verify-vite-output.mjs';

async function withBundle(run){
 const dir=await mkdtemp(join(tmpdir(),'cn-next-vite-'));
 try{
  await mkdir(join(dir,'graph-b'),{recursive:true});
  await mkdir(join(dir,'assets'),{recursive:true});
  await writeFile(join(dir,'index.html'),'<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body><img src="./assets/logo.svg"><a href="./graph-b/source-graph-b.html">B</a><svg id="chart"></svg><section id="variant-panel"></section><section id="proof-explorer"></section><section id="official-product-pilot"><ol id="official-pilot-path"></ol></section></body></html>');
  await writeFile(join(dir,'graph-b/source-graph-b.html'),'<!doctype html><html><head><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/Investering-Framework-Archive-v1/next/assets/site.css"></head><body><svg id="chart"></svg><script type="module" src="/Investering-Framework-Archive-v1/next/assets/app.js"></script></body></html>');
  await writeFile(join(dir,'assets/site.css'),'body{color:#07172f}');
  await writeFile(join(dir,'assets/logo.svg'),'<svg xmlns="http://www.w3.org/2000/svg"/>');
  await writeFile(join(dir,'assets/app.js'),'new URL("../../data/latest.json",import.meta.url);new URL("../../data/compass.json",import.meta.url);new URL("../../data/publication-lineage.json",import.meta.url);');
  await run(dir);
 }finally{await rm(dir,{recursive:true,force:true})}
}

test('both Vite pages, emitted assets and 3 source references PASS',async()=>{
 await withBundle(async dir=>{
  const result=await verifyViteOutput(dir);
  assert.equal(result.status,'PASS');
  assert.deepEqual(result.entrypoints,['index.html','graph-b/source-graph-b.html']);
  assert.equal(result.asset_count,5);
  assert.ok(result.assets.every(x=>/^[a-f0-9]{64}$/.test(x.sha256)));
 });
});
test('missing nested B HTML catches historical NoSuchKey',async()=>{
 await withBundle(async dir=>{
  await rm(join(dir,'graph-b/source-graph-b.html'));
  await assert.rejects(verifyViteOutput(dir),/MISSING_ENTRY:graph-b\/source-graph-b.html/);
 });
});
test('unresolved Vite asset blocks staging',async()=>{
 await withBundle(async dir=>{
  await rm(join(dir,'assets/site.css'));
  await assert.rejects(verifyViteOutput(dir),/MISSING_REFERENCED_ASSET/);
 });
});
test('wrong Pages basepath cannot escape NEXT staging',async()=>{
 await withBundle(async dir=>{
  await writeFile(join(dir,'graph-b/source-graph-b.html'),'<html><head><meta name="robots" content="noindex"></head><body><svg id="chart"></svg><script src="/assets/app.js"></script></body></html>');
  await assert.rejects(verifyViteOutput(dir),/ASSET_OUTSIDE_NEXT/);
 });
});
test('original sine demo forbidden in compiled bundle',async()=>{
 await withBundle(async dir=>{
  await writeFile(join(dir,'assets/app.js'),'Math.sin(1);new URL("../../data/latest.json",import.meta.url);');
  await assert.rejects(verifyViteOutput(dir),/NEXT_SYNTHETIC_SOURCE/);
 });
});
test('missing source feed references or noindex block release',async()=>{
 await withBundle(async dir=>{
  await writeFile(join(dir,'assets/app.js'),'const x = 1;');
  await assert.rejects(verifyViteOutput(dir),/MISSING_FIRST_PARTY_FEED_REFERENCE/);
  await writeFile(join(dir,'index.html'),'<html><body>Unindexed?</body></html>');
  await assert.rejects(verifyViteOutput(dir),/MISSING_NOINDEX/);
 });
});

test('placeholder root without original Graph B, Proof or Compass cannot be released',async()=>{
 await withBundle(async dir=>{
  await writeFile(join(dir,'index.html'),'<html><head><meta name="robots" content="noindex"></head><body><a href="./graph-b/source-graph-b.html">Open demo</a></body></html>');
  await assert.rejects(verifyViteOutput(dir),/MISSING_PREMIUM_ROOT_MARKUP/);
 });
});
