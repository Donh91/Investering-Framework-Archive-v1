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
// Explicit directory URL is the investor entry, not merely /index.html.
const HOME_ALIAS='canonical-homepage';
const canonicalFiles=[
  HOME_ALIAS,
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
  'data/publication-lineage.json',
  'data/kompas-live.json',
  'graph-history/index.html'
];
const sha=bytes=>createHash('sha256').update(bytes).digest('hex');
/**
 * A valid public history must have both a real timeline and renderer.
 * If the optional builder failed, only an explicit UNAVAILABLE status page
 * may remain. Never silently deploy a 404, or an old/stale timeline as live.
 */
async function graphHistoryParityAssets(root){
 const html=await readFile(resolve(root,'graph-history/index.html'),'utf8');
 let hasTimeline=false;
 try{await readFile(resolve(root,'data/graph-history/timeline.json'));hasTimeline=true}
 catch(error){if(error.code!=='ENOENT')throw error}
 const unavailable=html.includes('data-cn-history-status="UNAVAILABLE"');
 if(unavailable===hasTimeline)throw Error('GRAPH_HISTORY_ROUTE_DATA_STATUS_MISMATCH');
 return ['graph-history/index.html',...(hasTimeline?['data/graph-history/timeline.json']:[])];
}
const safePath=path=>{
  assert.equal(typeof path,'string','PUBLIC_ASSET_PATH_INVALID');
  assert.match(path,/^[A-Za-z0-9._/-]+$/,'PUBLIC_ASSET_PATH_INVALID');
  assert.ok(path&&!path.startsWith('/')&&!path.includes('//'),'PUBLIC_ASSET_PATH_INVALID');
  assert.ok(!path.split('/').some(part=>part===''||part==='.'||part==='..'),'PUBLIC_ASSET_PATH_INVALID');
  return path;
};
/** Bind an ACTUAL public CDN asset to the frozen original seven-day product. */
async function discoverOriginalWeek(root=dist){
  const snapshot=JSON.parse(await readFile(resolve(root,'data/latest.json'),'utf8'));
  const p=snapshot?.public_live_precision;
  assert.equal(p?.contract,'CN_PUBLIC_LIVE_PRICE_PRECISION_v1','CN_ORIGINAL_PRECISION_MISSING');
  const week=p.forecast_week,issue=p.public_issue_number;
  assert.match(week||'',/^\d{4}-W\d{2}$/,'CN_ORIGINAL_WEEK_INVALID');
  assert.ok(Number.isInteger(issue)&&issue>0,'CN_ORIGINAL_ISSUE_INVALID');
  const path=safePath(p.freeze_receipt_public_path);
  assert.equal(path,'data/public-freezes/'+week.slice(0,4)+'/W'+week.slice(6)+'/CN'+issue+'_PUBLIC_FREEZE.json','CN_ORIGINAL_FREEZE_PATH_MISMATCH');
  const r=JSON.parse(await readFile(resolve(root,path),'utf8'));
  assert.equal(r.contract,'CN_SITE_PUBLIC_FREEZE_RECEIPT_v1','CN_ORIGINAL_FREEZE_CONTRACT');
  assert.equal(r.status,'SITE_FROZEN_SOURCE_OF_RECORD','CN_ORIGINAL_FREEZE_NOT_ORIGINAL');
  assert.equal(r.forecast_week,week,'CN_ORIGINAL_FREEZE_WEEK_MISMATCH');
  assert.equal(r.public_issue_number,issue,'CN_ORIGINAL_FREEZE_ISSUE_MISMATCH');
  assert.match(p.freeze_sha256||'',/^[0-9a-f]{64}$/,'CN_ORIGINAL_FREEZE_SHA_INVALID');
  assert.equal(r.source_forecast_freeze_sha256,p.freeze_sha256,'CN_ORIGINAL_FREEZE_SHA_MISMATCH');
  const accepted=r.daily_product_acceptance;
  assert.equal(accepted?.contract,'CN_MONDAY_SEVEN_DAY_PRODUCT_ACCEPTANCE_v1','CN_ORIGINAL_ACCEPTANCE_CONTRACT');
  assert.equal(accepted.forecast_week,week,'CN_ORIGINAL_ACCEPTANCE_WEEK_MISMATCH');
  assert.equal(accepted.status,'COMPLETE','CN_ORIGINAL_PRODUCT_INCOMPLETE');
  assert.equal(accepted.no_backward_reconstruction,true,'CN_ORIGINAL_BACKFILL_NOT_ALLOWED');
  for(const asset of ['BTC','ETH']){
    const a=accepted.assets?.[asset];
    assert.equal(a?.status,'COMPLETE','CN_ORIGINAL_ASSET_INCOMPLETE_'+asset);
    assert.equal(a?.expected_close_points,7,'CN_ORIGINAL_CLOSE_COUNT_'+asset);
    assert.equal(a?.low_high_range_points,7,'CN_ORIGINAL_RANGE_COUNT_'+asset);
    assert.deepEqual(a?.missing_requirements,[],'CN_ORIGINAL_ASSET_REQUIREMENTS_'+asset);
  }
  assert.deepEqual(p.daily_product_acceptance,accepted,'CN_ORIGINAL_PUBLIC_SOURCE_DIVERGENCE');
  return {path,forecast_week:week,public_issue_number:issue,
    source_forecast_freeze_sha256:p.freeze_sha256,issued_at_utc:accepted.issued_at_utc,
    seven_day_product:'COMPLETE'};
}
/**
 * Attestation is optional evidence, never a prerequisite for public CDN bytes
 * or independently scheduled hourly observation. Preserve the failure reason
 * without promoting any INCOMPLETE or malformed original to COMPLETE.
 */
async function originalEvidenceOrUnavailable(root=dist){
  try{return await discoverOriginalWeek(root)}
  catch(error){
    return {status:'NOT_ATTESTABLE',
      reason:String(error?.message||'ORIGINAL_SOURCE_UNAVAILABLE').split(String.fromCharCode(10))[0].split(':')[0].slice(0,80)};
  }
}
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
  if(path===HOME_ALIAS)return ORIGIN;
  const url=new URL(path,ORIGIN);
  assert.equal(url.origin,'https://donh91.github.io');
  assert.equal(decodeURIComponent(url.pathname),'/Investering-Framework-Archive-v1/'+path);
  return url.href;
};
function snapshotSummary(rows,status,round,head,discoveryError=null,original=null){
  return {
    contract:'CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1',
    status,checked_at_utc:new Date().toISOString(),run_head_sha:process.env.GITHUB_SHA||null,
    built_checkout_sha:head,rounds:round,
    canonical_public_url:ORIGIN,
    discovery_status:discoveryError?'FAILED':'PASS',
    discovery_error:discoveryError,
    original_weekly_product:original,
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
    expected=sha(await readAsset(resolve(root,path===HOME_ALIAS?'index.html':path)));
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
    await mkdir(resolve(temporary,'graph-history'),{recursive:true});
    await mkdir(resolve(temporary,'data/graph-history'),{recursive:true});
    await writeFile(resolve(temporary,'graph-history/index.html'),'<html><main>Valid original historical chart</main></html>');
    await writeFile(resolve(temporary,'data/graph-history/timeline.json'),'{"contract":"CN_GRAPH_HISTORY_TIMELINE_v1"}');
    assert.deepEqual(await graphHistoryParityAssets(temporary),[
      'graph-history/index.html','data/graph-history/timeline.json'
    ]);
    await rm(resolve(temporary,'data/graph-history/timeline.json'));
    await assert.rejects(graphHistoryParityAssets(temporary),/GRAPH_HISTORY_ROUTE_DATA_STATUS_MISMATCH/);
    await writeFile(resolve(temporary,'graph-history/index.html'),
      '<html><main data-cn-history-status="UNAVAILABLE">No verified history</main></html>');
    assert.deepEqual(await graphHistoryParityAssets(temporary),['graph-history/index.html']);
    await writeFile(resolve(temporary,'data/graph-history/timeline.json'),'{"contract":"fake"}');
    await assert.rejects(graphHistoryParityAssets(temporary),/GRAPH_HISTORY_ROUTE_DATA_STATUS_MISMATCH/);
    await rm(resolve(temporary,'data/graph-history/timeline.json'));
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
    assert.equal(publicUrl(HOME_ALIAS,allowed),ORIGIN);
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
    // Negative control: /index.html matches while the ACTUAL root URL does not.
    const homepageStale=await check(HOME_ALIAS,allowed,{
      readAsset,fetchAsset:async url=>new Response(url===ORIGIN?'stale homepage':bytes),
      root:temporary});
    assert.equal(homepageStale.status,'MISMATCH');
    assert.equal((await check('index.html',allowed,{
      readAsset,fetchAsset:async()=>new Response(bytes),root:temporary})).status,'PASS');
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
    const originalPath='data/public-freezes/2026/W48/CN35_PUBLIC_FREEZE.json';
    const product={contract:'CN_MONDAY_SEVEN_DAY_PRODUCT_ACCEPTANCE_v1',forecast_week:'2026-W48',
      status:'COMPLETE',no_backward_reconstruction:true,
      assets:Object.fromEntries(['BTC','ETH'].map(a=>[a,{status:'COMPLETE',
        expected_close_points:7,low_high_range_points:7,missing_requirements:[]}]))};
    const originalReceipt={contract:'CN_SITE_PUBLIC_FREEZE_RECEIPT_v1',status:'SITE_FROZEN_SOURCE_OF_RECORD',
      forecast_week:'2026-W48',public_issue_number:35,source_forecast_freeze_sha256:'a'.repeat(64),
      daily_product_acceptance:product};
    const snap={public_live_precision:{contract:'CN_PUBLIC_LIVE_PRICE_PRECISION_v1',
      forecast_week:'2026-W48',public_issue_number:35,freeze_sha256:'a'.repeat(64),
      freeze_receipt_public_path:originalPath,daily_product_acceptance:product}};
    await mkdir(resolve(temporary,'data/public-freezes/2026/W48'),{recursive:true});
    await writeFile(resolve(temporary,'data/latest.json'),JSON.stringify(snap));
    await writeFile(resolve(temporary,originalPath),JSON.stringify(originalReceipt));
    assert.equal((await discoverOriginalWeek(temporary)).path,originalPath);
    await writeFile(resolve(temporary,originalPath),JSON.stringify({...originalReceipt,source_forecast_freeze_sha256:'b'.repeat(64)}));
    await assert.rejects(discoverOriginalWeek(temporary),/CN_ORIGINAL_FREEZE_SHA_MISMATCH/);
    await writeFile(resolve(temporary,originalPath),JSON.stringify({...originalReceipt,daily_product_acceptance:{...product,
      assets:{...product.assets,BTC:{...product.assets.BTC,expected_close_points:6}}}}));
    await assert.rejects(discoverOriginalWeek(temporary),/CN_ORIGINAL_CLOSE_COUNT_BTC/);
    await writeFile(resolve(temporary,originalPath),JSON.stringify(originalReceipt));
    await writeFile(resolve(temporary,'data/latest.json'),JSON.stringify({public_live_precision:{
      ...snap.public_live_precision,forecast_week:'2026-W49'}}));
    await assert.rejects(discoverOriginalWeek(temporary),/CN_ORIGINAL_FREEZE_PATH_MISMATCH/);
    await writeFile(resolve(temporary,'data/latest.json'),JSON.stringify(snap));
    await writeFile(resolve(temporary,originalPath),JSON.stringify({...originalReceipt,public_issue_number:34}));
    await assert.rejects(discoverOriginalWeek(temporary),/CN_ORIGINAL_FREEZE_ISSUE_MISMATCH/);
    await writeFile(resolve(temporary,originalPath),JSON.stringify(originalReceipt));
    // The entire week can legitimately be INCOMPLETE: attest unavailable,
    // while the ordinary public-byte parity surface still succeeds.
    const incomplete={...originalReceipt,daily_product_acceptance:{...product,status:'INCOMPLETE'}};
    await writeFile(resolve(temporary,originalPath),JSON.stringify(incomplete));
    const evidence=await originalEvidenceOrUnavailable(temporary);
    assert.equal(evidence.status,'NOT_ATTESTABLE');
    assert.equal(evidence.reason,'CN_ORIGINAL_PRODUCT_INCOMPLETE');
    const canonicalOnly=new Set([...canonicalFiles]);
    const bytesForParity=Buffer.from('independent public bundle bytes');
    assert.equal((await check('data/latest.json',canonicalOnly,{
      readAsset:async()=>bytesForParity,
      fetchAsset:async()=>new Response(bytesForParity),root:temporary
    })).status,'PASS');
    await writeFile(resolve(temporary,originalPath),JSON.stringify(originalReceipt));
    assert.equal((await originalEvidenceOrUnavailable(temporary)).seven_day_product,'COMPLETE');
  }finally{
    await rm(temporary,{recursive:true,force:true});
  }
  console.log('CN_PAGES_PARITY_SELF_TEST_PASS: canonical allowlist + complete dynamic NEXT tree, exact bytes, mismatch, HTTP, timeout, body failure, missing local asset and path rejection');
}else{
  let head=null;try{head=execFileSync('git',['rev-parse','HEAD'],{encoding:'utf8'}).trim()}catch{}
  let files=[];
  let discoveryError=null;
  // The original seven-day attestation must NOT decide CDN byte parity.
  // INCOMPLETE is an intentional producer outcome throughout the week.
  const original=await originalEvidenceOrUnavailable(dist);
  try{
    const nextFiles=await discoverFiles(dist,'next');
    const historyFiles=await graphHistoryParityAssets(dist);
    files=[...new Set([...canonicalFiles,...(original.path?[original.path]:[]),...historyFiles,...nextFiles])];
  }catch(error){
    // Do not expose local paths or exception text. NEXT should exist because the
    // current workflow stages it before upload; absence is a release failure.
    discoveryError=String(error?.message||'NEXT_DISCOVERY_FAILED').split(':')[0].slice(0,80);
  }
  const allowed=new Set(files);
  let last=null;
  if(discoveryError){
    last=snapshotSummary([], 'DEGRADED',0,head,discoveryError,original);
    console.log('CN_PAGES_PARITY_RECEIPT '+JSON.stringify(last));
  }else{
    for(let round=1;round<=6;round++){
      const rows=await Promise.all(files.map(path=>check(path,allowed)));
      const pass=rows.every(row=>row.status==='PASS');
      last=snapshotSummary(rows,pass?'PASS':'DEGRADED',round,head,null,original);
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
  if(process.env.CN_PAGES_RECEIPT_PATH){
    await writeFile(resolve(process.cwd(),process.env.CN_PAGES_RECEIPT_PATH),JSON.stringify(last,null,2)+'\n');
  }
  if(last.status!=='PASS'){
    console.error('CN_PAGES_DELIVERY_PARITY_DEGRADED: public CDN differs from uploaded bundle or unavailable after bounded retries');
    process.exitCode=1;
  }
}
