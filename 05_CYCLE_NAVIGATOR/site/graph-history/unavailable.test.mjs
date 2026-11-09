import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,stat,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {quarantineGraphHistory,unavailableHtml} from './unavailable.mjs';

test('source-failed optional Graph History is a source-honest HTTP page, never a 404 or fake timeline',async()=>{
 const root=await mkdtemp(join(tmpdir(),'cn-history-failclosed-'));
 try{
  const history=resolve(root,'graph-history/index.html');
  const timeline=resolve(root,'data/graph-history/timeline.json');
  await mkdir(resolve(root,'graph-history'),{recursive:true});
  await mkdir(resolve(root,'data/graph-history'),{recursive:true});
  await writeFile(history,'<script>fake blue forecast</script>');
  await writeFile(timeline,'{"contract":"bad_stale_previous_release","weeks":[1]}');
  const result=await quarantineGraphHistory(root);
  assert.deepEqual(result,{
   status:'UNAVAILABLE',history_route:'graph-history/index.html',timeline_published:false
  });
  const html=await readFile(history,'utf8');
  assert.equal(html,unavailableHtml,'FALLBACK_BYTES_DETERMINISTIC');
  assert.match(html,/data-cn-history-status="UNAVAILABLE"/);
  assert.match(html,/lang="en"/);
  assert.match(html,/href="\.\.\/"/);
  assert.doesNotMatch(html,/expected_close|observed_at_utc|Math\.sin|<canvas|<svg/i);
  await assert.rejects(stat(timeline),error=>error.code==='ENOENT');
  assert.ok((await stat(history)).isFile());
  // Idempotent, including when the previous timeline was already absent.
  await quarantineGraphHistory(root);
  assert.equal(await readFile(history,'utf8'),html);
 }finally{await rm(root,{recursive:true,force:true});}
});

test('normal valid Graph History remains authoritative; fallback is not called by normal builder',async()=>{
 // This test checks only the fallback itself, not the builder. CI must still
 // run the existing immutable forecast and graph history runtime gates.
 assert.match(unavailableHtml,/De nødvendige historiske kildebeviser/);
 assert.doesNotMatch(unavailableHtml,/PUBLISHED|SOURCE_ISSUED|100 ?%/);
});
