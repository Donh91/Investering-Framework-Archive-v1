import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPremiumRootHtml} from './premium-root.mjs';
import {buildUnifiedRootHtml} from './unified-root.mjs';
import {promoteHtml,promoteUnifiedHtml} from './promote-root.mjs';

const source=await readFile(new URL('./graph-b/source-graph-b.html',import.meta.url),'utf8');
const staged=buildPremiumRootHtml(source)
 .replace('<link rel="stylesheet" href="./premium-overhaul.css">',
  '<link rel="stylesheet" href="/Investering-Framework-Archive-v1/next/assets/index-test.css">');
test('official root preserves original B and removes preview metadata',()=>{
 const html=promoteHtml(staged);
 assert.match(html,/premium-next premium-home/);
 assert.match(html,/Weekly Outlook <span class="alt-token">B<\/span>/);
 assert.doesNotMatch(html,/noindex|IKKE OFFICIEL FORSIDE|Forhåndsvisning/);
 assert.match(html,/href="\.\/vnext\/" class="premium-entry-canonical"/);
 assert.match(html,/href="\.\/data\/latest\.json"/);
 assert.match(html,/href="\.\/data\/compass\.json"/);
 assert.match(html,/\/Investering-Framework-Archive-v1\/next\/assets\//);
 assert.equal((html.match(/id="feed-status"/g)||[]).length,1);
});
test('broken entry or unexpected source fails closed',()=>{
 assert.throws(()=>promoteHtml(staged.replace('id="variant-panel"','id="missing"')),/COMPONENT_MISSING/);
 assert.throws(()=>promoteHtml(staged.replace('href="../data/latest.json"','href="bad"')),/SOURCE_MISMATCH/);
 assert.throws(()=>promoteHtml(staged.replace('Weekly Outlook <span class="alt-token">B<\/span>','Demo')),/COMPONENT_MISSING/);
});

const proSource=await readFile(new URL('../vnext-live/index.html',import.meta.url),'utf8');
const stagedUnified=buildUnifiedRootHtml(source,proSource)
 .replace('<link rel="stylesheet" href="./premium-overhaul.css">',
  '<link rel="stylesheet" href="/Investering-Framework-Archive-v1/next/assets/unified-test.css">');

test('pure governed unified cutover preserves one B / PRO and correct official links',()=>{
 const html=promoteUnifiedHtml(stagedUnified);
 assert.match(html,/premium-next premium-home/);
 assert.match(html,/id="compass-pro"/);
 assert.match(html,/id="variant-panel"/);
 assert.match(html,/id="official-path-view"/);
 assert.match(html,/id="proof-explorer"/);
 assert.match(html,/id="pro-reentry-state"/);
 assert.doesNotMatch(html,/noindex|IKKE OFFICIEL FORSIDE|official-product-pilot/);
 assert.match(html,/href="\.\/vnext\/" class="premium-entry-canonical"/);
 assert.match(html,/href="\.\/data\/latest\.json"/);
 assert.match(html,/href="\.\/data\/compass\.json"/);
 assert.match(html,/\/Investering-Framework-Archive-v1\/next\/assets\//);
 assert.equal((html.match(/id="chart"/g)||[]).length,1);
 assert.equal((html.match(/id="compass-pro"/g)||[]).length,1);
 assert.equal((html.match(/id="feed-status"/g)||[]).length,1);
 assert.doesNotMatch(html,/\.\.\/data\//);
});

test('unified cutover aborts on missing/duplicate identity, legacy owner and bad links',()=>{
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('id="compass-pro"','id="bad"')),
  /UNIFIED_PROMOTION_SINGLETON_MISSING:compass-pro/);
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('id="chart"','id="bad"')),
  /UNIFIED_PROMOTION_SINGLETON_MISSING:chart/);
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('</body>','<svg id="chart"></svg></body>')),
  /UNIFIED_PROMOTION_SINGLETON_MISSING:chart/);
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('</body>','<div id="official-product-pilot"></div></body>')),
  /UNIFIED_PROMOTION_LEGACY_OWNER/);
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('href="../data/latest.json"','href="../wrong/latest.json"')),
  /ROOT_PROMOTION_SOURCE_MISMATCH/);
 assert.throws(()=>promoteUnifiedHtml(stagedUnified.replace('/Investering-Framework-Archive-v1/next/assets/','/bad-prefix/assets/')),
  /UNIFIED_PROMOTION_COMPILED_ASSETS_MISSING/);
});
