import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {stagingPlan,approvedAssets} from './build-next.mjs';
const here=new URL('./',import.meta.url);
test('staged v2 asset list excludes AppDeploy demos and canonical root',()=>{
 const p=stagingPlan();
 assert.ok(p.to.endsWith('/site/dist/next'));
 assert.equal(p.assets.length,11);
 assert.ok(!approvedAssets.some(x=>x.includes('reference/')||x.includes('src/main.ts')));
});
test('original B and Proof imports resolve only to staged first-party sources',async()=>{
 const html=await readFile(new URL('./graph-b/source-graph-b.html',here),'utf8');
 const js=await readFile(new URL('./graph-b/source-graph-b.mjs',here),'utf8');
 const proof=await readFile(new URL('./proof/proof-explorer.mjs',here),'utf8');
 assert.match(html,/\.\/source-graph-b\.css/);
 assert.match(html,/\.\.\/proof\/proof-explorer\.mjs/);
 assert.match(js,/\.\/official-source-adapter\.mjs/);
 assert.match(proof,/\.\/price-range-proof\.mjs/);
 assert.match(proof,/\.\/public-source-links\.mjs/);
 assert.doesNotMatch(html,/\.\.\/reference\/appdeploy-bc/);
 assert.doesNotMatch(js,/\bMath\.sin\s*\(/);
});
test('noncanonical client fetches existing root data, never writes new data',async()=>{
 const js=await readFile(new URL('./graph-b/source-graph-b.mjs',here),'utf8');
 const proof=await readFile(new URL('./proof/proof-explorer.mjs',here),'utf8');
 assert.match(js,/new URL\('\.\.\/\.\.\/data\/latest\.json',import\.meta\.url\)/);
 assert.match(js,/publication-lineage\.json/);
 assert.match(proof,/new URL\('\.\.\/\.\.\/data\/latest\.json',import\.meta\.url\)/);
 assert.doesNotMatch(js,/POST|PUT|DELETE|credentials:'include'/);
});

test('Official Compass/PATH pilot uses real source, not a new market issuer',async()=>{
 const html=await readFile(new URL('./graph-b/source-graph-b.html',here),'utf8');
 const ui=await readFile(new URL('./compass/compass-path-ui.mjs',here),'utf8');
 assert.match(html,/official-pilot-action/);
 assert.match(html,/compass-path-ui\.mjs/);
 assert.match(ui,/\.\/official-compass-path\.mjs/);
 assert.match(ui,/PUBLIC_FEED_HTTP/);
 assert.doesNotMatch(ui,/Math\.sin\(/);
});
