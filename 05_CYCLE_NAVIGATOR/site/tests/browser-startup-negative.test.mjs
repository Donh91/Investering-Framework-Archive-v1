/* Negative control: two Chrome bootstrap failures MUST block a release and
 * preserve diagnostics; no Chrome binary or network dependency is needed here.
 * Actual positive 390/430 assertions still run with the real browser.
 */
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {mkdtempSync,writeFileSync,chmodSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {resolve,join,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=mkdtempSync(join(tmpdir(),'cn-chrome-negative-'));
try {
 const fake=join(root,'mock-chrome');
 writeFileSync(fake, '#!/usr/bin/env node\nprocess.stderr.write("SIMULATED_BOOT_FAILURE\\n");process.exit(71);\n');
 chmodSync(fake,0o700);
 const target=resolve(dirname(fileURLToPath(import.meta.url)),'premium-mobile-browser.test.mjs');
 const run=spawnSync(process.execPath,[target],{
   env:{...process.env,CHROME_BIN:fake},encoding:'utf8',timeout:10000,
 });
 assert.equal(run.error,undefined,'Negative control must run, not time out');
 assert.notEqual(run.status,0,'Two failed Chrome startups must never allow Pages release');
 assert.match(run.stderr,/NO_CHROME_DEVTOOLS_PORT/);
 assert.match(run.stderr,/"attempt":1/);
 assert.match(run.stderr,/"attempt":2/);
 assert.match(run.stderr,/SIMULATED_BOOT_FAILURE/);
 assert.match(run.stderr,/"exitCode":71/);
 console.log('PASS Chrome dual-failure fails closed with bounded stderr and no false release');
} finally {
 rmSync(root,{recursive:true,force:true});
}
