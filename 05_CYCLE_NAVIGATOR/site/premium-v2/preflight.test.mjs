// Run manually: node --test 05_CYCLE_NAVIGATOR/site/premium-v2/preflight.test.mjs
// NO additional GitHub Actions job/workflow. Tests only the development lane.
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
const base=new URL('./',import.meta.url);
const from=path=>readFile(new URL(path,base),'utf8');
test('Design Registry is owner-authorized and canonical first',async()=>{
 const data=JSON.parse(await from('./design-registry.json'));
 assert.equal(data.contract,'CN_PREMIUM_V2_DESIGN_REGISTRY_v1');
 assert.equal(data.production_release_allowed,false);
 for(const id of ['QUIET_PRECISION','KOMPAS_MINIMAL','PATH_V3','GRAPH_B','PROOF_REPLAY'])
  assert.ok(data.authorities.some(entry=>entry.id===id));
});
test('AppDeploy B/C is archived EXACT source, but not approved runtime forecast data',async()=>{
 const oldHtml=await from('./reference/appdeploy-bc/index.html');
 const oldTS=await from('./reference/appdeploy-bc/src/main.ts');
 const css=await from('./reference/appdeploy-bc/src/styles.css');
 assert.match(oldHtml,/id="range-band"/);
 assert.match(oldHtml,/data-asset="BTC"/);
 assert.match(oldHtml,/id="hour-slider"/);
 assert.match(css,/\.graph-card \{/);
 assert.match(css,/\.graph-card\[data-variant='b'\] #forecast/);
 assert.match(oldTS,/Math\.sin\(/); // quarantine/source-provenance fact, not a production feature
});
test('V2 source-first B view preserves original anatomy, removes demo, includes honest source reader',async()=>{
 const v=await from('./graph-b/source-graph-b.html');
 const runtime=await from('./graph-b/source-graph-b.mjs');
 const adapter=await from('./graph-b/official-source-adapter.mjs');
 for(const id of ['variant-panel','chart','range-band','range-upper','range-lower','forecast','actual','hour-slider','playhead'])
  assert.ok(v.includes('id="'+id+'"'));
 assert.doesNotMatch(v,/id="missing"/); // studio synthetic forecast restore switch
 assert.doesNotMatch(v,/\$83,000/); // original synthetic starting quote
 assert.doesNotMatch(runtime,/Math\.sin\(/);
 assert.doesNotMatch(runtime,/api\.coingecko|dexscreener|api_key|authorization/i);
 assert.match(runtime,/readOfficialGraphB/);
 assert.match(runtime,/replayObservedUntil/);
 assert.match(runtime,/publication-lineage\.json/);
 assert.match(adapter,/PUBLISHED_INVALID_FAIL_CLOSED/);
});
test('Existing Pages builder MUST NOT publish quarantined design lab',async()=>{
 const builder=await from('../build-public.mjs');
 const release=await from('../premium-release.mjs');
 assert.doesNotMatch(builder,/premium-v2/);
 assert.doesNotMatch(release,/premium-v2/);
 assert.match(release,/preserveLegacyShell/);
 assert.match(release,/releasePremiumShell/);
});
test('Proof source links require commit-pinned public repositories only',async()=>{
 const code=await from('./proof/public-source-links.mjs');
 assert.match(code,/blob/);
 assert.match(code,/source_commit/);
 assert.doesNotMatch(code,/Donh91\/secrets['"]/);
});

test('Original B small badge survives localization and unavailable source clears stale replay',async()=>{
 const html=await from('./graph-b/source-graph-b.html');
 const js=await from('./graph-b/source-graph-b.mjs');
 assert.match(html,/class="alt-token">B<\/span>/);
 assert.ok(js.includes("heading.replaceChildren(document.createTextNode(t('Ugens prisgraf ','Weekly outlook ')))"));
 assert.match(js,/badge\.textContent='B'/);
 assert.doesNotMatch(html,/ONS 15:00 UTC/);
 assert.doesNotMatch(html,/Illustrative forecast against observed path/);
 assert.match(js,/\$\('playhead'\)\.setAttribute\('visibility','hidden'\)/);
 assert.match(js,/card\.dataset\.source=model\?\.forecast_status==='SOURCE_ISSUED'/);
});


test('NEXT staging is isolated and sequenced after canonical builders and before existing Pages upload',async()=>{
 const pages=await from('../../../.github/workflows/cycle-navigator-pages.yml');
 const gate=await from('../../../.github/workflows/cn-site-v2-gate.yml');
 const builder=await from('../build-public.mjs');
 const steps=[
  'Build privacy-safe public bundle',
  'Build public live Price Range precision',
  'Build and verify social preview',
  'Verify final investor-facing shell and privacy',
  'Stage verified isolated NEXT, preserving all canonical public assets',
  'Upload Cycle Navigator public bundle only'
 ];
 let last=-1;
 for(const step of steps){
  const at=pages.indexOf(step);
  assert.ok(at>last,'PAGES_NEXT_STAGE_ORDER_INVALID:'+step);
  last=at;
 }
 assert.equal((pages.match(/stage-next\.mjs/g)||[]).length,1);
 assert.equal((pages.match(/upload-pages-artifact@v4/g)||[]).length,1);
 assert.equal((pages.match(/deploy-pages@v4/g)||[]).length,1);
 assert.match(pages,/path: 05_CYCLE_NAVIGATOR\/site\/dist/);
 assert.doesNotMatch(builder,/premium-v2/);
 assert.ok(gate.includes('Prove isolated NEXT Vite build'));
 assert.ok(gate.includes('next-browser.test.mjs'));
 assert.ok(gate.indexOf('stage-next.mjs')<gate.indexOf('next-browser.test.mjs'));
});
