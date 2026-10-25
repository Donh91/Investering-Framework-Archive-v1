/**
 * CN Pages v1 - source artifact to ACTUAL PUBLIC delivery parity.
 * Read-only, allowlisted, no action/forecast/model authority and no new schedule.
 * Runs after the existing Pages deployment. Checks exact binary bytes from the
 * stable canonical allowlist plus every dynamically built /next/ staging asset.
 */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,appendFile,readdir,mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {resolve,dirname,relative,sep} from 'node:path';
import {tmpdir} from 'node:os';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {setTimeout as delay} from 'node:timers/promises';

const ORIGIN='https://donh91.github.io/Investering-Framework-Archive-v1/';
const dist=resolve(dirname(fileURLToPath(import.meta.url)),'../dist');
const canonicalFiles=[
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
const safePath=path=>{
  assert.equal(typeof path,'string','PUBLIC_ASSET_PATH_INVALID');
  assert.match(path,/^[A-Za-z0-9._/-]+$/,'PUBLIC_ASSET_PATH_INVALID');
  assert.ok(path&&!path.startsWith('/')&&!path.includes('//'),'PUBLIC_ASSET_PATH_INVALID');
  assert.ok(!path.split('/').some(part=>part===''||part==='.'||part==='..'),'PUBLIC_ASSET_PATH_INVALID');
  return path;
};
async function discoverFiles(root,prefix){
  safePath(prefix);
  const base=resolve(root);
  const start=resolve(root,prefix);
  const output=[];
  async function visit(folder){
    for(const entry of await readdir(folder,{withFileTypes:true})){
      const item=resolve(folder,entry.name);
      const path=relative(base,item).split(sep).join('/');
      safePath(path);
      if(entry.isDirectory()){await visit(item);continue}
      if(!entry.isFile())throw Error('PUBLIC_ASSET_UNSAFE_FILE:'+path);
      output.push(path);
    }
  }
  await visit(start);
  output.sort();
  if(!output.length)throw Error('PUBLIC_ASSET_SUBTREE_EMPTY:'+prefix);
  return output;
}
const publicUrl=(path,allowed)=>{
  safePath(path);
  assert.ok(allowed.has(path),'NOT_AN_ALLOWLISTED_PUBLIC_ASSET');
  const url=new URL(path,ORIGIN);
  assert.equal(url.origin,'https://donh91.github.io');
  assert.equal(decodeURIComponent(url.pathname),'/Investering-Framework-Archive-v1/'+path);
  return url.href;
};
function snapshotSummary(rows,status,round,head,discoveryError=null){
  return {
    contract:'CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1',
    status,checked_at_utc:new Date().toISOString(),run_head_sha:process.env.GITHUB_SHA||null,
    built_checkout_sha:head,rounds:round,
    canonical_public_url:ORIGIN,
    discovery_status:discoveryError?'FAILED':'PASS',
    discovery_error:discoveryError,
    files:rows.map(x=>({path:x.path,status:x.status,expected_sha256:x.expected,served_sha256:x.actual,
      http_status:x.http_status??null,etag:x.etag??null,last_modified:x.last_modified??null,
      note:x.note||null}))
  };
}
async function check(path,allowed,{readAsset=readFile,fetchAsset=fetch,root=dist}={}){
  // Reject paths before either local or remote access, including in self-tests.
  const url=publicUrl(path,allowed);
  let expected=null;
  try{
    expected=sha(await readAsset(resolve(root,path)));
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
  const temporary=await mkdtemp(resolve(tmpdir(),'cn-pages-parity-'));
  try{
    await mkdir(resolve(temporary,'next/assets'),{recursive:true});
    await mkdir(resolve(temporary,'next/graph-b'),{recursive:true});
    await writeFile(resolve(temporary,'next/index.html'),'next');
    await writeFile(resolve(temporary,'next/assets/app-A1.css'),'css');
    await writeFile(resolve(temporary,'next/graph-b/source-graph-b.html'),'graph');
    const discovered=await discoverFiles(temporary,'next');
    assert.deepEqual(discovered,[
      'next/assets/app-A1.css','next/graph-b/source-graph-b.html','next/index.html'
    ]);
    const files=[...new Set([...canonicalFiles,...discovered])];
    const allowed=new Set(files);
    assert.equal(publicUrl('next/assets/app-A1.css',allowed),ORIGIN+'next/assets/app-A1.css');
    assert.throws(()=>publicUrl('../secrets/password',allowed),/PUBLIC_ASSET_PATH_INVALID/);
    assert.throws(()=>publicUrl('next/not-built.js',allowed),/NOT_AN_ALLOWLISTED_PUBLIC_ASSET/);
    assert.equal(new Set(files).size,files.length);
    assert.ok(files.includes('vnext/premium-experience.css')&&files.includes('next/index.html'));
    const bytes=Buffer.from('release bytes');
    const readAsset=async()=>bytes;
    const fetchAsset=async()=>new Response(bytes);
    const pass=await check('index.html',allowed,{readAsset,fetchAsset,root:temporary});
    assert.equal(pass.status,'PASS');
    assert.equal(pass.expected,sha(bytes));
    assert.equal(pass.actual,sha(bytes));
    assert.equal((await check('index.html',allowed,{readAsset,
      fetchAsset:async()=>new Response('stale bytes'),root:temporary})).status,'MISMATCH');
    const denied=await check('index.html',allowed,{readAsset,
      fetchAsset:async()=>new Response('denied',{status:403}),root:temporary});
    assert.equal(denied.status,'HTTP_ERROR');
    assert.equal(denied.http_status,403);
    assert.equal(denied.actual,null);
    const timeout=await check('index.html',allowed,{readAsset,
      fetchAsset:async()=>{throw new DOMException('private diagnostic','TimeoutError')},root:temporary});
    assert.equal(timeout.status,'FETCH_FAILED');
    assert.equal(timeout.note,'TimeoutError');
    assert.ok(!JSON.stringify(timeout).includes('private diagnostic'));
    const bodyFailure=await check('index.html',allowed,{readAsset,
      fetchAsset:async()=>({ok:true,arrayBuffer:async()=>{throw new Error('body failed')}}),root:temporary});
    assert.equal(bodyFailure.status,'FETCH_FAILED');
    let fetched=false;
    const missing=await check('index.html',allowed,{
      readAsset:async()=>{throw new Error('private local path')},
      fetchAsset:async()=>{fetched=true;return new Response(bytes)},root:temporary});
    assert.equal(missing.status,'LOCAL_ASSET_UNAVAILABLE');
    assert.equal(missing.expected,null);
    assert.equal(fetched,false);
    const receipt=snapshotSummary([missing],'DEGRADED',1,null);
    assert.equal(receipt.files[0].status,'LOCAL_ASSET_UNAVAILABLE');
    assert.equal(receipt.files[0].expected_sha256,null);
    assert.equal((await Promise.all(files.map(path=>check(path,allowed,{readAsset,fetchAsset,root:temporary}))))
      .filter(row=>row.status==='PASS').length,files.length);
  }finally{
    await rm(temporary,{recursive:true,force:true});
  }
  console.log('CN_PAGES_PARITY_SELF_TEST_PASS: canonical allowlist + complete dynamic NEXT tree, exact bytes, mismatch, HTTP, timeout, body failure, missing local asset and path rejection');
}else{
  let head=null;try{head=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim()}catch{}
  let files=[];
  let discoveryError=null;
  try{
    const nextFiles=await discoverFiles(dist,'next');
    files=[...new Set([...canonicalFiles,...nextFiles])];
  }catch(error){
    // Do not expose local paths or exception text. NEXT should exist because the
    // current workflow stages it before upload; absence is a release failure.
    discoveryError=String(error?.message||'NEXT_DISCOVERY_FAILED').split(':')[0].slice(0,80);
  }
  const allowed=new Set(files);
  let last=null;
  if(discoveryError){
    last=snapshotSummary([], 'DEGRADED',0,head,discoveryError);
    console.log('CN_PAGES_PARITY_RECEIPT '+JSON.stringify(last));
  }else{
    for(let round=1;round<=6;round++){
      const rows=await Promise.all(files.map(path=>check(path,allowed)));
      const pass=rows.every(row=>row.status==='PASS');
      last=snapshotSummary(rows,pass?'PASS':'DEGRADED',round,head);
      // No JSON payload, secrets, portfolio or private URLs printed. All checked
      // assets are intentionally already publicly accessible.
      console.log('CN_PAGES_PARITY_RECEIPT '+JSON.stringify(last));
      if(pass||rows.some(row=>row.status==='LOCAL_ASSET_UNAVAILABLE'))break;
      if(round<6)await delay([0,5000,8000,12000,16000,20000][round]);
    }
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
