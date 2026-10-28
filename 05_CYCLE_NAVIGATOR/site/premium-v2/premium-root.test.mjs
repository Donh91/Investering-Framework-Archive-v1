import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPremiumRootHtml} from './premium-root.mjs';

const here=new URL('./graph-b/source-graph-b.html',import.meta.url);
const original=await readFile(here,'utf8');

test('Premium root renders original Graph B, Proof, official Compass and PATH',()=>{
 const root=buildPremiumRootHtml(original);
 for(const id of ['variant-panel','chart','proof-explorer','official-product-pilot','official-pilot-path'])
  assert.ok(root.includes('id="'+id+'"'),id);
 assert.match(root,/<h1 data-premium-copy="title">Ugens prognose\. Faktiske kurser\.<\/h1>/);
 assert.match(root,/Weekly Outlook <span class="alt-token">B<\/span>/);
 assert.match(root,/aria-label="Premium sektioner"/);
 assert.match(root,/data-premium-nav="compass"/);
 assert.match(root,/href="\/Investering-Framework-Archive-v1\/vnext\/#compass" class="premium-entry-pro" data-premium-nav="pro"/);
 assert.equal((root.match(/data-premium-nav="pro"/g)||[]).length,1);
 assert.match(root,/\.premium-entry-navigation \.premium-entry-pro\{/);
 assert.match(root,/data-premium-copy="disclaimer"/);
 assert.match(root,/name="robots" content="noindex,nofollow"/);
 assert.ok(root.indexOf('id="variant-panel"')<root.indexOf('id="proof-explorer"'));
 assert.ok(root.indexOf('id="variant-panel"')<root.indexOf('aria-label="Premium sektioner"'));
 assert.ok(root.indexOf('id="official-product-pilot"')<root.indexOf('id="variant-panel"'));
 assert.ok(root.indexOf('id="proof-explorer"')<root.indexOf('class="official-product-pilot premium-compass-detail"'));
 assert.ok(root.indexOf('id="official-product-pilot"')<root.indexOf('class="official-product-pilot premium-path"'));
 assert.ok(root.indexOf('class="official-product-pilot premium-path"')<root.indexOf('class="premium-meta"'));
 assert.equal((root.match(/id="feed-status"/g)||[]).length,1);
 assert.match(root,/href="\.\.\/data\/latest\.json" data-premium-nav="cnSource"/);
 assert.match(root,/href="\.\.\/data\/compass\.json" data-premium-nav="compassSource"/);
 assert.match(root,/href="\.\/premium-overhaul\.css"/);
});
test('first fold moves the single source-issued action ahead of original Graph B',()=>{
 const html=buildPremiumRootHtml(original);
 for(const id of ['official-product-pilot','official-pilot-action','official-pilot-status','variant-panel'])
  assert.equal((html.match(new RegExp('id="'+id+'"','g'))||[]).length,1,id);
 assert.ok(html.indexOf('premium-decision-summary')<html.indexOf('id="variant-panel"'));
 assert.ok(html.indexOf('id="variant-panel"')<html.indexOf('premium-compass-detail'));
 assert.equal((html.match(/id="official-pilot-gate"/g)||[]).length,1);
 assert.ok(html.indexOf('id="official-pilot-gate"')<html.indexOf('id="variant-panel"'));
 for(const id of ['official-pilot-horizons','official-pilot-rotation','official-pilot-path'])
  assert.match(html,new RegExp('id="'+id+'"'));
 assert.match(html,/Weekly Outlook <span class="alt-token">B<\/span>/);
});
test('root asset paths stay under NEXT and original nested HTML remains immutable',()=>{
 const before=original;
 const root=buildPremiumRootHtml(original);
 for(const path of [
  './graph-b/source-graph-b.css','./graph-b/source-graph-b.mjs',
  './proof/proof-explorer.css','./proof/proof-explorer.mjs',
  './compass/compass-path.css','./compass/compass-path-ui.mjs',
  './assets/CN_LOGO.svg','./premium-overhaul.css'
 ])assert.ok(root.includes(path),path);
 assert.equal(original,before);
 assert.match(original,/src="\.\/source-graph-b\.mjs"/);
 assert.ok(!root.includes('src="../assets/CN_LOGO.svg"'));
});
test('existing public data authority remains imported from first-party adapters',()=>{
 const root=buildPremiumRootHtml(original);
 assert.match(root,/src="\.\/graph-b\/source-graph-b\.mjs"/);
 assert.match(root,/src="\.\/proof\/proof-explorer\.mjs"/);
 assert.match(root,/src="\.\/compass\/compass-path-ui\.mjs"/);
 assert.doesNotMatch(root,/\bMath\.sin\s*\(/);
 assert.doesNotMatch(root,/src\/main\.ts/);
 assert.doesNotMatch(root,/github\.com\/Donh91\/secrets/);
});
test('mismatched original source and missing marker fail closed',()=>{
 assert.throws(()=>buildPremiumRootHtml(original.replace('id="variant-panel"','id="discarded"')),/SOURCE_MISMATCH/);
 assert.throws(()=>buildPremiumRootHtml(original.replace('src="../assets/CN_LOGO.svg"','src="../assets/missing.svg"')),/SOURCE_MISMATCH/);
 assert.throws(()=>buildPremiumRootHtml('<html></html>'),/SOURCE_UNAVAILABLE/);
 assert.throws(()=>buildPremiumRootHtml(original.replace('</head>','Math.sin(2)</head>')),/SYNTHETIC_SOURCE_FORBIDDEN/);
});
test('same original source produces identical Premium HTML',()=>{
 assert.equal(buildPremiumRootHtml(original),buildPremiumRootHtml(original));
});
test('Vite actual build must use build-time single-authority root plugin',async()=>{
 const config=await readFile(new URL('./vite.config.mjs',import.meta.url),'utf8');
 assert.match(config,/buildPremiumRootHtml\(original\)/);
 assert.match(config,/graph-b\/source-graph-b\.html/);
 assert.match(config,/context\.filename/);
 assert.match(config,/order:'pre'/);
 assert.match(config,/base:'\/Investering-Framework-Archive-v1\/next\/'/);
});

test('Graph B existing DA/EN control covers real Premium heading and navigation',async()=>{
 const js=await readFile(new URL('./graph-b/source-graph-b.mjs',import.meta.url),'utf8');
 assert.match(js,/data-premium-nav/);
 assert.match(js,/data-premium-copy/);
 assert.match(js,/Forecast meets reality/);
 assert.match(js,/Prognose møder virkelighed/);
 assert.match(js,/pro:'Compass PRO ↗'/);
 assert.match(js,/pro:'Kompas PRO ↗'/);
 const app=await readFile(new URL('../vnext-live/app.mjs',import.meta.url),'utf8');
 assert.match(app,/const initial=location\.hash\.slice\(1\)/);
 assert.match(app,/selectTab\(keys\.includes\(initial\)\?initial:'overview'\)/);
});
