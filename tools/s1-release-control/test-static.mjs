import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import test from 'node:test';
const source = readFileSync(new URL('./index.html', import.meta.url),'utf8');
const script = source.match(/<script>([\s\S]*?)<\/script>/)?.[1];
test('standalone site and parsable client script', () => {
  assert.ok(source.includes('<title>S1 Release Control</title>'));
  assert.ok(script);
  assert.doesNotThrow(() => new Function(script));
});
test('read-only anonymous GitHub public REST client', () => {
  assert.match(source,/return fetch\(BASE\+path/);
  assert.doesNotMatch(source,/method\s*:\s*['"](?:POST|PUT|PATCH|DELETE)['"]/i);
  assert.doesNotMatch(source,/Authorization\s*:/i);
  assert.doesNotMatch(source,/github_pat_|ghp_|sk-proj-/i);
  assert.doesNotMatch(source,/api\.openai\.com/i);
  assert.match(source,/connect-src https:\/\/api\.github\.com/);
});
test('private repos remain unobserved', () => {
  assert.match(source,/PRIVATE · UNOBSERVED/);
  assert.match(source,/RESTRICTED=/);
  assert.doesNotMatch(source,/api\(.*RESTRICTED/);
  assert.doesNotMatch(source,/Donh91\/secrets/);
});
test('release gates fail closed and queue never invents entries', () => {
  assert.match(source,/if\(p\.draft\)return 'HOLD'/);
  assert.match(source,/if\(p\.risk==='HIGH'\)return 'HOLD'/);
  assert.match(source,/return 'PROPOSED'/);
  assert.match(source,/action_limit_per_existing_S1_tick:3/);
  assert.match(source,/no_release_authority:true/);
  assert.match(source,/slice\(0,state\.limit\)/);
  assert.match(source,/if\(!p\.filesObserved\|\|p\.changedFiles>100\|\|p\.files\.length>=100\)/);
});
test('proven exact-HEAD actions check SHA, stale fallback labeled',()=>{
  assert.match(source,/r\.head_sha===p\.head/);
  assert.match(source,/r\.commit_id===p\.head/);
  assert.match(source,/IKKE live/);
  assert.match(source,/UNOBSERVED/);
  assert.match(source,/immutable/i);
});
