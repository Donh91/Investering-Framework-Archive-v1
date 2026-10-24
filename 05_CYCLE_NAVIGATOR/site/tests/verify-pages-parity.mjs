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
async function check(path,{readAsset=readFile,fetchAsset=fetch}={}){
  // Reject paths before either local or remote access, including in self-tests.
  const url=publicUrl(path);
  let expected=null;
  try{
    expected=sha(await readAsset(resolve(dist,path)));
  }catch{
    // A missing/unreadable uploaded asset must still produce a failure receipt.
    // Retrying the CDN cannot repair the local release bundle.
    return {path,status:'LOCAL_ASSET_UNAVAILABLE',expected:null,actual:null};
  }
  try{
    // No cachebuster that might mask normal public URL bytes; request no-cache
    // to make CDN prove this release rather than a prior cached variant.
    const response=await fetchAsset(url,{
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
  const bytes=Buffer.from('release bytes');
  const readAsset=async()=>bytes;
  const fetchAsset=async()=>new Response(bytes);
  const pass=await check('index.html',{readAsset,fetchAsset});
  assert.equal(pass.status,'PASS');
  assert.equal(pass.expected,sha(bytes));
  assert.equal(pass.actual,sha(bytes));
  assert.equal((await check('index.html',{readAsset,
    fetchAsset:async()=>new Response('stale bytes')})).status,'MISMATCH');
  const denied=await check('index.html',{readAsset,
    fetchAsset:async()=>new Response('denied',{status:403})});
  assert.equal(denied.status,'HTTP_ERROR');
  assert.equal(denied.http_status,403);
  assert.equal(denied.actual,null);
  const timeout=await check('index.html',{readAsset,
    fetchAsset:async()=>{throw new DOMException('private diagnostic','TimeoutError')}});
  assert.equal(timeout.status,'FETCH_FAILED');
  assert.equal(timeout.note,'TimeoutError');
  assert.ok(!JSON.stringify(timeout).includes('private diagnostic'));
  const bodyFailure=await check('index.html',{readAsset,
    fetchAsset:async()=>({ok:true,arrayBuffer:async()=>{throw new Error('body failed')}})});
  assert.equal(bodyFailure.status,'FETCH_FAILED');
  let fetched=false;
  const missing=await check('index.html',{
    readAsset:async()=>{throw new Error('private local path')},
    fetchAsset:async()=>{fetched=true;return new Response(bytes)}});
  assert.equal(missing.status,'LOCAL_ASSET_UNAVAILABLE');
  assert.equal(missing.expected,null);
  assert.equal(fetched,false);
  const receipt=snapshotSummary([missing],'DEGRADED',1,null);
  assert.equal(receipt.files[0].status,'LOCAL_ASSET_UNAVAILABLE');
  assert.equal(receipt.files[0].expected_sha256,null);
  await assert.rejects(check('../secrets/password',{
    readAsset:async()=>assert.fail('invalid path was read'),
    fetchAsset:async()=>assert.fail('invalid path was fetched')
  }),/NOT_AN_ALLOWLISTED_PUBLIC_ASSET/);
  assert.equal((await Promise.all(files.map(path=>check(path,{readAsset,fetchAsset}))))
    .filter(row=>row.status==='PASS').length,files.length);
  console.log('CN_PAGES_PARITY_SELF_TEST_PASS: exact bytes, mismatch, HTTP, timeout, body failure, missing local asset, traversal and all 11 public assets');
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
    if(pass||rows.some(row=>row.status==='LOCAL_ASSET_UNAVAILABLE'))break;
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
