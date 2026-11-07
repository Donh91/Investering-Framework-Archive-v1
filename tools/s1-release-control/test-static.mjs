import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
const source=readFileSync(new URL('./index.html',import.meta.url),'utf8');
const core=readFileSync(new URL('./release-core.js',import.meta.url),'utf8');
const script=source.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('standalone cockpit JS is parseable with shared read-only core',()=>{
  assert.match(source,/<title>S1 Release Control<\/title>/);
  assert.match(source,/src="\.\/release-core\.js"/);
  assert.ok(script);
  assert.doesNotThrow(()=>new Function(script));
  assert.doesNotThrow(()=>new Function(core));
});
test('browser only reads public GitHub GET, no tokens or privileged APIs',()=>{
  assert.match(source,/return fetch\(BASE\+path/);
  assert.doesNotMatch(source,/method\s*:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  assert.doesNotMatch(source,/Authorization\s*:/i);
  assert.doesNotMatch(source,/github_pat_|ghp_|sk-proj-/i);
  assert.doesNotMatch(source,/api\.openai\.com/i);
  assert.match(source,/connect-src https:\/\/api\.github\.com/);
});
test('private repo data never requested or exported',()=>{
  assert.match(source,/PRIVATE · UNOBSERVED/);
  assert.match(source,/RESTRICTED=/);
  assert.doesNotMatch(source,/api\(.*RESTRICTED/);
  assert.doesNotMatch(source,/Donh91\/secrets/);
});
test('UI uses shared fail-closed release logic and bounded queue',()=>{
  assert.match(source,/var rank=CORE\.rank,risk=CORE\.risk,ci=CORE\.ci/);
  assert.match(core,/if\(p\.draft\|\|p\.risk==="HIGH"\)return "HOLD"/);
  assert.match(core,/return "PROPOSED"/);
  assert.match(source,/action_limit_per_existing_S1_tick:3/);
  assert.match(source,/no_release_authority:true/);
  assert.match(source,/slice\(0,state\.limit\)/);
  assert.match(core,/p\.files\.length!==p\.changedFiles/);
});
test('exact HEAD, stale fallback, immutable links and no self-approval',()=>{
  assert.match(source,/r\.head_sha===p\.head/);
  assert.match(core,/r\.commit_id===p\.head/);
  assert.match(source,/IKKE live/);
  assert.match(source,/UNOBSERVED/);
  assert.match(source,/immutable/i);
  assert.doesNotMatch(core,/merge_authorized:true/);
});
