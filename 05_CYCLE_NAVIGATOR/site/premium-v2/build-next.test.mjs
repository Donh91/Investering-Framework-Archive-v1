import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {stagingPlan,approvedAssets} from './build-next.mjs';
const here=new URL('./',import.meta.url);
test('staged v2 asset list excludes AppDeploy demos and canonical root',()=>{
 const p=stagingPlan();
 assert.ok(p.to.endsWith('/site/dist/next'));
 assert.equal(p.assets.length,13);
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

test('real CN logo and Vite multi-entry keep isolated B visible at /next/graph-b',async()=>{
 const html=await readFile(new URL('./graph-b/source-graph-b.html',here),'utf8');
 const root=await readFile(new URL('./index.html',here),'utf8');
 const config=await readFile(new URL('./vite.config.mjs',here),'utf8');
 const logo=await readFile(new URL('./assets/CN_LOGO.svg',here),'utf8');
 assert.match(logo,/CN_LOGO Cycle Navigator/);
 assert.match(html,/\.\.\/assets\/CN_LOGO\.svg/);
 assert.match(root,/\.\/assets\/CN_LOGO\.svg/);
 assert.match(config,/graph-b\/source-graph-b\.html/);
 assert.match(config,/Investering-Framework-Archive-v1\/next/);
 assert.match(config,/publicDir:false/);
});

test('Vite source port is an explicit two-entry build rather than a default single-index',async()=>{
 const vite=await readFile(new URL('./vite.config.mjs',here),'utf8');
 const pkg=JSON.parse(await readFile(new URL('./package.json',here),'utf8'));
 const index=await readFile(new URL('./index.html',here),'utf8');
 assert.match(vite,/graphB:resolve\(root,'graph-b\/source-graph-b\.html'\)/);
 assert.match(vite,/index:resolve\(root,'index\.html'\)/);
 assert.match(vite,/base:'\/Investering-Framework-Archive-v1\/next\/'/);
 assert.match(vite,/publicDir:false/);
 assert.equal(pkg.scripts['build:next'],'vite build --config vite.config.mjs');
 assert.ok(index.includes('CN_LOGO.svg'));
});

test('GitHub Pages first-party data URLs survive both native ESM and Vite asset locations',()=>{
 const prefix='https://donh91.github.io/Investering-Framework-Archive-v1/';
 for(const module of ['next/graph-b/source-graph-b.mjs','next/assets/source-graph-b.abc123.js']){
   const resolved=new URL('../../data/latest.json',new URL(module,prefix));
   assert.equal(resolved.href,prefix+'data/latest.json');
   const compass=new URL('../../data/compass.json',new URL(module,prefix));
   assert.equal(compass.href,prefix+'data/compass.json');
   const lineage=new URL('../../data/publication-lineage.json',new URL(module,prefix));
   assert.equal(lineage.href,prefix+'data/publication-lineage.json');
 }
});
test('never ship imported AppDeploy sine-wave graph fixture from Vite source',async()=>{
 const html=await readFile(new URL('./graph-b/source-graph-b.html',here),'utf8');
 const b=await readFile(new URL('./graph-b/source-graph-b.mjs',here),'utf8');
 const proof=await readFile(new URL('./proof/proof-explorer.mjs',here),'utf8');
 const compass=await readFile(new URL('./compass/compass-path-ui.mjs',here),'utf8');
 for(const s of [html,b,proof,compass]){
   assert.doesNotMatch(s,/reference\/appdeploy-bc\/src\/main\.ts/);
   assert.doesNotMatch(s,/Math\.sin\(/);
   assert.doesNotMatch(s,/github\.com\/Donh91\/secrets/);
 }
});
