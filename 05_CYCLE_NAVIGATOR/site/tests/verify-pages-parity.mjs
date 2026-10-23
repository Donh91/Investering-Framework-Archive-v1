/**
 * CN Pages v1 - source artifact to ACTUAL PUBLIC delivery parity.
 * Read-only, allowlisted, no action/forecast/model authority and no new schedule.
 * Runs after the existing Pages deployment. Checks the exact binary bytes
 * the public CDN serves, not just success of build/upload/deploy actions.
 */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,appendFile} from 'node:fs/promises';
import {resolve,dirname} from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {setTimeout as delay} from 'node:timers/promises';

const ORIGIN='https://donh91.github.io/Investering-Framework-Archive-v1/';
const dist=resolve(dirname(fileURLToPath(import.meta.url)),'../dist');
const files=[
  'index.html',
  'vnext/index.html',
  'vnext/premium.css',
  'vnext/premium-experience.css',
  'vnext/app.mjs',
  'frozen-week-chart.js',
  'frozen-week-chart.css',
  'data/latest.json',
  'data/compass.json',
  'data/compass-event.json',
  'data/publication-lineage.json'
];
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
const publicUrl=path=>{
  assert.ok(files.includes(path),'NOT_AN_ALLOWLISTED_PUBLIC_ASSET');
  const url=new URL(path,ORIGIN);
  assert.equal(url.origin,'https://donh91.github.io');
  assert.equal(url.pathname,'/Investering-Framework-Archive-v1/'+path);
  return url.href;
};
function snapshotSummary(rows,status,round,head){
  return {
    contract:'CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1',
    status,checked_at_utc:new Date().toISOString(),run_head_sha:process.env.GITHUB_SHA||null,
    built_checkout_sha:head,rounds:round,
    canonical_public_url:ORIGIN,
    files:rows.map(x=>({path:x.path,status:x.status,expected_sha256:x.expected,served_sha256:x.actual,
      http_status:x.http_status??null,etag:x.etag??null,last_modified:x.last_modified??null,
      note:x.note||null}))
  };
}
async function check(path){
  const expected=sha(await readFile(resolve(dist,path)));
  try{
    // No cachebuster that might mask normal public URL bytes; request no-cache
    // to make CDN prove this release rather than a prior cached variant.
    const response=await fetch(publicUrl(path),{
      redirect:'error',headers:{'Cache-Control':'no-cache','Pragma':'no-cache'},
      signal:AbortSignal.timeout(12000)
    });
    if(!response.ok)return {path,status:'HTTP_ERROR',expected,actual:null,http_status:response.status};
    const actual=sha(Buffer.from(await response.arrayBuffer()));
    return {path,status:actual===expected?'PASS':'MISMATCH',expected,actual,
      http_status:response.status,etag:response.headers.get('etag'),
      last_modified:response.headers.get('last-modified')};
  }catch(error){
    return {path,status:'FETCH_FAILED',expected,actual:null,
      note:String(error?.name||'NETWORK_ERROR').slice(0,50)};
  }
}
if(process.argv.includes('--self-test')){
  assert.equal(sha(Buffer.from('abc')),
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad');
  assert.equal(publicUrl('data/compass.json'),
    ORIGIN+'data/compass.json');
  assert.throws(()=>publicUrl('../secrets/password'),/NOT_AN_ALLOWLISTED_PUBLIC_ASSET/);
  assert.equal(new Set(files).size,files.length);
  assert.ok(files.includes('vnext/premium-experience.css')&&files.includes('data/latest.json'));
  console.log('CN_PAGES_PARITY_SELF_TEST_PASS: bounded public exact-byte hash, 11 allowlisted assets');
}else{
  let head=null;try{head=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim()}catch{}
  let last=null;
  for(let round=1;round<=6;round++){
    const rows=await Promise.all(files.map(check));
    const pass=rows.every(row=>row.status==='PASS');
    last=snapshotSummary(rows,pass?'PASS':'DEGRADED',round,head);
    // No JSON payload, secrets, portfolio or private URLs printed. All checked
    // assets are intentionally already publicly accessible.
    console.log('CN_PAGES_PARITY_RECEIPT '+JSON.stringify(last));
    if(pass)break;
    if(round<6)await delay([0,5000,8000,12000,16000,20000][round]);
  }
  if(process.env.GITHUB_STEP_SUMMARY){
    const p=last.files.filter(x=>x.status==='PASS').length;
    await appendFile(process.env.GITHUB_STEP_SUMMARY,
      '\n### Cycle Navigator: artifact → real GitHub Pages CDN\n'+
      'Status **'+last.status+'** | **'+p+'/'+files.length+
      '** byte-for-byte SHA-256 matches | built checkout **'+(head||'UNKNOWN')+
      '** | latest attempt '+last.rounds+'\n');
  }
  if(last.status!=='PASS'){
    console.error('CN_PAGES_DELIVERY_PARITY_DEGRADED: public CDN differs from uploaded bundle or unavailable after bounded retries');
    process.exitCode=1;
  }
}
