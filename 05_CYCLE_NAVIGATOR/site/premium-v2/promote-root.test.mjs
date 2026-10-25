import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {buildPremiumRootHtml} from './premium-root.mjs';
import {promoteHtml} from './promote-root.mjs';

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
