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
  await writeFile(join(dir,'unified.html'),
    '<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body>'+
    '<section id="compass-pro"><strong id="premium-now-action"></strong><div id="premium-risk-steps"></div>'+
    '<table><tbody id="pro-forward-rows"></tbody></table></section>'+
    '<section id="variant-panel"><svg id="chart"></svg></section>'+
    '<section id="proof-explorer"></section><section id="official-path-view"><ol id="premium-path-rail"></ol></section>'+
    '<script type="module" src="./assets/app.js"></script></body></html>');
  await writeFile(join(dir,'graph-b/source-graph-b.html'),'<!doctype html><html><head><meta name="robots" content="noindex,nofollow"><link rel="stylesheet" href="/Investering-Framework-Archive-v1/next/assets/site.css"></head><body><svg id="chart"></svg><script type="module" src="/Investering-Framework-Archive-v1/next/assets/app.js"></script></body></html>');
  await writeFile(join(dir,'assets/site.css'),'body{color:#07172f}');
  await writeFile(join(dir,'assets/logo.svg'),'<svg xmlns="http://www.w3.org/2000/svg"/>');
  await writeFile(join(dir,'assets/app.js'),'new URL("../../data/latest.json",import.meta.url);new URL("../../data/compass.json",import.meta.url);new URL("../../data/publication-lineage.json",import.meta.url);const pro=["premium-now-action","pro-reentry-state","source-trace-body","CN_VNEXT_PUBLIC_FEED_PARITY_v1","OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1"];');
  await run(dir);
 }finally{await rm(dir,{recursive:true,force:true})}
}

test('three Vite preview pages, emitted assets and 3 source references PASS',async()=>{
 await withBundle(async dir=>{
  const result=await verifyViteOutput(dir);
  assert.equal(result.status,'PASS');
  assert.deepEqual(result.entrypoints,['index.html','unified.html','graph-b/source-graph-b.html']);
  assert.equal(result.asset_count,6);
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

test('missing unified PRO entry blocks staging even with original B intact',async()=>{
 await withBundle(async dir=>{
  await rm(join(dir,'unified.html'));
  await assert.rejects(verifyViteOutput(dir),/MISSING_ENTRY:unified.html/);
 });
});
test('missing or duplicate single Graph B and PRO nodes fail compiled artifact',async()=>{
 await withBundle(async dir=>{
  const path=join(dir,'unified.html');
  const {readFile}=await import('node:fs/promises');
  const original=await readFile(path,'utf8');
  await writeFile(path,original.replace('id="compass-pro"','id="wrong-pro"'));
  await assert.rejects(verifyViteOutput(dir),/UNIFIED_SINGLETON_ID:compass-pro/);
  await writeFile(path,original.replace('</body>','<svg id="chart"></svg></body>'));
  await assert.rejects(verifyViteOutput(dir),/UNIFIED_SINGLETON_ID:chart/);
 });
});
test('legacy second Compass or competing PRO route fail independently',async()=>{
 await withBundle(async dir=>{
  const path=join(dir,'unified.html');
  const {readFile}=await import('node:fs/promises');
  const original=await readFile(path,'utf8');
  await writeFile(path,original.replace('</body>','<div id="official-product-pilot"></div></body>'));
  await assert.rejects(verifyViteOutput(dir),/UNIFIED_LEGACY_DUPLICATE/);
  await writeFile(path,original.replace('</body>','<a href="/vnext/#compass">2nd PRO</a></body>'));
  await assert.rejects(verifyViteOutput(dir),/UNIFIED_COMPETING_COMPASS_ROUTE/);
 });
});

test('compiled candidate without the actual PRO source/expiry JS cannot stage',async()=>{
 await withBundle(async dir=>{
  const app=join(dir,'assets/app.js');
  const {readFile}=await import('node:fs/promises');
  const code=await readFile(app,'utf8');
  await writeFile(app,code.replace('OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1','REMOVED_SOURCE_FRESHNESS_GUARD'));
  await assert.rejects(verifyViteOutput(dir),/MISSING_UNIFIED_PRO_JS_BINDING:OFFICIAL_COMPASS_SOURCE_FRESHNESS_READBACK_v1/);
  await writeFile(app,code.replace('pro-reentry-state','REMOVED_REENTRY_VIEW'));
  await assert.rejects(verifyViteOutput(dir),/MISSING_UNIFIED_PRO_JS_BINDING:pro-reentry-state/);
 });
});
