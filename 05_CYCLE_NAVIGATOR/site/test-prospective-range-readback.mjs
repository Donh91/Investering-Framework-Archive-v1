import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
import {resolve,dirname} from 'node:path';
import {mkdtemp,mkdir,writeFile,symlink,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {prospectiveRangeReadback} from './prospective-range-readback.mjs';
const source=resolve(dirname(fileURLToPath(import.meta.url)),'../..');
const root=await mkdtemp(resolve(tmpdir(),'cn-range-readback-'));
try{
  await symlink(resolve(source,'scripts'),resolve(root,'scripts'),'dir');
  await mkdir(resolve(root,'05_CYCLE_NAVIGATOR'));
  await writeFile(resolve(root,'05_CYCLE_NAVIGATOR/LATEST_PROSPECTIVE_RANGE.json'),JSON.stringify({contract:'CN_PROSPECTIVE_RANGE_BRIDGE_v1',target_week:'2026-W39',weekly:{BTC:{low:1,high:2}}}));
  const pointer={iso_year:2026,iso_week:44};
  const pkg={generated_unix:1792997869};
  const actual=await prospectiveRangeReadback(root,pointer,pkg);
  assert.equal(actual.range_values_admitted,false);
  assert.equal(actual.status,'STALE');
  assert.deepEqual(actual.reason_codes,['BRIDGE_TARGET_WEEK_MISMATCH']);
  assert.equal(actual.weekly,undefined);
  assert.equal(actual.intraday,undefined);
  const missing=await prospectiveRangeReadback('/does-not-exist',pointer,pkg);
  assert.equal(missing.status,'SOURCE_UNAVAILABLE');
  assert.equal(missing.weekly,undefined);
  const clock=await prospectiveRangeReadback(root,pointer,{generated_unix:null});
  assert.deepEqual(clock.reason_codes,['FORECAST_CLOCK_UNVERIFIED']);
}finally{await rm(root,{recursive:true,force:true});}
console.log('PASS stale bridge excluded, missing validator and missing freeze fail closed');
