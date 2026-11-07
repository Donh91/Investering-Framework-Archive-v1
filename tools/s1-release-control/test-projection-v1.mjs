import { readFileSync } from 'node:fs';
import { runInNewContext } from 'node:vm';
import assert from 'node:assert/strict';
import test from 'node:test';
import core from './release-core.js';
import { buildProjection } from './projection-v1.mjs';
const SHA_A='a'.repeat(40), SHA_B='b'.repeat(40), SHA_C='c'.repeat(40);
const owner='Donh91/Investering-Framework-Archive-v1';
const root='https://api.github.com/repos/'+owner;
const base={repo:owner,number:1996,author:'Donh91',state:'open',merged:false,draft:false,head:SHA_A,base:SHA_C,
  changedFiles:1,filesObserved:true,files:[{filename:'tools/s1-release-control/README.md'}],
  runObserved:true,runs:[{id:123,head_sha:SHA_A,conclusion:'success',status:'completed'}],
  reviewsObserved:true,reviews:[],labels:[],seed:false};
const pr=(patch={})=>({...base,...patch});
test('exact 40-digit SHA is required and missing head fails closed',()=>{
  assert.equal(core.safeSha('short'),false);
  assert.equal(core.ci(pr({head:'garbage'})).status,'UNOBSERVED');
  assert.equal(core.disposition(pr({head:'garbage'})),'UNOBSERVED');
});
test('green observed run is not merge authorization',()=>{
  const p=pr();assert.equal(core.ci(p).status,'PROVEN');
  assert.equal(core.disposition(p),'PROPOSED');
  assert.equal(core.project(p,SHA_B,'2026-11-07T12:00:00Z').merge_authorized,false);
  assert.equal(core.project(p,SHA_B,'2026-11-07T12:00:00Z').required_gates.required_checks,'UNOBSERVED');
});
test('draft and high impact always HOLD',()=>{
  assert.equal(core.disposition(pr({draft:true})),'HOLD');
  const high=pr({files:[{filename:'.github/workflows/release.yml'}]});
  high.risk=core.risk(high);
  assert.equal(high.risk,'HIGH');
  assert.equal(core.disposition(high),'HOLD');
});
test('review from another actor must be exact-head and latest',()=>{
  const valid={user:{login:'reviewer'},commit_id:SHA_A,state:'APPROVED',submitted_at:'2026-11-07T08:00:00Z'};
  assert.equal(core.review(pr({reviews:[{...valid,commit_id:SHA_B}]})),'UNOBSERVED');
  assert.equal(core.review(pr({reviews:[valid]})),'PROVEN');
  assert.equal(core.review(pr({reviews:[valid,{...valid,state:'CHANGES_REQUESTED',submitted_at:'2026-11-07T09:00:00Z'}]})),'UNOBSERVED');
  assert.equal(core.review(pr({reviews:[{...valid,user:{login:'Donh91'}}]})),'UNOBSERVED');
});
test('partial pagination, API misses and incorrect workflow HEAD never pass',()=>{
  assert.equal(core.risk(pr({filesObserved:false})),'UNKNOWN');
  assert.equal(core.risk(pr({changedFiles:101})),'UNKNOWN');
  assert.equal(core.ci(pr({runs:[{...base.runs[0],head_sha:SHA_B}]})).status,'UNOBSERVED');
  assert.equal(core.ci(pr({runs:[{...base.runs[0],conclusion:'in_progress',status:'in_progress'}]})).status,'UNOBSERVED');
  assert.equal(core.ci(pr({runs:[{...base.runs[0],conclusion:'failure'}]})).status,'BLOCKED');
});
test('closure is attributable only to native state, never scheduled S1',()=>{
  const p=pr({state:'closed',merged:true,merge_commit_sha:SHA_B});
  assert.equal(core.disposition(p),'MERGED');
  const row=core.project(p,SHA_C,'2026-11-07T12:00:00Z');
  assert.equal(row.autonomy_evidence,'UNOBSERVED');
  assert.equal(row.production_verified,false);
  assert.equal(row.merge_authorized,false);
});
function mkFetch({main=SHA_B,afterMain=SHA_B,runHead=SHA_A,denyFiles=false,denyBranch=false,fileCount=1}={}){
  let branchCalls=0;
  const sample={number:1996,title:'S1 Release Control',state:'open',draft:false,user:{login:'Donh91'},head:{sha:SHA_A},base:{sha:SHA_C},changed_files:fileCount,labels:[]};
  return async (url,opts)=>{
    assert.equal(opts.method,undefined);
    assert.equal(opts.headers.Authorization,undefined);
    let value,status=200;
    if(url===root+'/branches/main'){branchCalls++;if(denyBranch)status=403;value={commit:{sha:branchCalls===1?main:afterMain}};}
    else if(url===root+'/pulls?state=open&sort=updated&direction=desc&per_page=100')value=[sample];
    else if(url===root+'/pulls/1996')value=sample;
    else if(url===root+'/pulls/1996/files?per_page=100'){value=[{filename:'tools/s1-release-control/index.html'}];if(denyFiles)status=403;}
    else if(url===root+'/pulls/1996/reviews?per_page=100')value=[];
    else if(url===root+'/actions/runs?head_sha='+SHA_A+'&per_page=100')value={workflow_runs:[{id:123,head_sha:runHead,conclusion:'success',status:'completed',name:'Static'}]};
    else throw Error('UNEXPECTED_URL: '+url);
    return {ok:status===200,status,json:async()=>value};
  };
}
test('realistic public adapter uses GET-only and emits versioned schema',async()=>{
  const result=await buildProjection({fetcher:mkFetch(),repositories:[owner],clock:()=> '2026-11-07T12:00:00Z'});
  assert.equal(result.schema,'S1_RELEASE_PROJECTION_v1');
  assert.equal(result.source_repositories[0].main_sha,SHA_B);
  assert.equal(result.items[0].head_sha,SHA_A);
  assert.equal(result.items[0].release_disposition,'PROPOSED');
  assert.equal(result.items[0].merge_authorized,false);
  assert.equal(result.unattended_s1_closure_proven,false);
});
test('partial private-style denial never becomes a PASS',async()=>{
  const result=await buildProjection({fetcher:mkFetch({denyFiles:true}),repositories:[owner]});
  assert.equal(result.partial,true);
  assert.equal(result.items[0].risk,'UNKNOWN');
  assert.equal(result.items[0].release_disposition,'UNOBSERVED');
});
test('main change during scan revokes source integrity',async()=>{
  const result=await buildProjection({fetcher:mkFetch({afterMain:SHA_C}),repositories:[owner]});
  assert.equal(result.source_repositories[0].observed,false);
  assert.equal(result.items[0].main_sha,null);
  assert.equal(result.items[0].release_disposition,'UNOBSERVED');
});
test('exact-head runs from another commit never count',async()=>{
  const result=await buildProjection({fetcher:mkFetch({runHead:SHA_C}),repositories:[owner]});
  assert.equal(result.items[0].ci_observation.status,'UNOBSERVED');
});
test('public projection rejects unauthorized repos and unbounded scans',async()=>{
  await assert.rejects(()=>buildProjection({repositories:['Donh91/secrets']}),/ALLOWLIST/);
  await assert.rejects(()=>buildProjection({repositories:[owner],maxPerRepo:999}),/BOUNDED/);
});
test('no deployment, execution, auth or model route in sources',()=>{
  for(const file of ['release-core.js','projection-v1.mjs']){
    const source=readFileSync(new URL('./'+file,import.meta.url),'utf8');
    assert.doesNotMatch(source,/fetch\s*\([^,]*,\s*\{\s*method\s*:/);
    assert.doesNotMatch(source,/api\.openai\.com|ghp_|github_pat_|sk-proj-/);
    assert.doesNotMatch(source,/trade\s*\(|mergePullRequest\s*\(/);
  }
});

test('mutation negative: removing HIGH_IMPACT hold changes expected safety verdict',()=>{
  const source=readFileSync(new URL('./release-core.js',import.meta.url),'utf8');
  const clause='if(p.draft||p.risk==="HIGH")return "HOLD";';
  assert.ok(source.includes(clause),'cannot silently skip mutation coverage');
  const context={module:{exports:{}},globalThis:{}};
  runInNewContext(source.replace(clause,'/* MUTATED: removed HIGH_IMPACT guard */'),context);
  const mutant=context.module.exports;
  const candidate=pr({risk:'HIGH'});
  assert.equal(core.disposition(candidate),'HOLD','original critical policy guard');
  assert.notEqual(mutant.disposition(candidate),'HOLD','the negative test detects removal of guard');
});
test('mutation negative: removing exact run SHA condition invalidates cross-commit CI proof',()=>{
  const source=readFileSync(new URL('./release-core.js',import.meta.url),'utf8');
  const clause='r&&r.head_sha===p.head&&Number.isSafeInteger(r.id)';
  assert.ok(source.includes(clause),'cannot silently skip SHA mutation coverage');
  const context={module:{exports:{}},globalThis:{}};
  runInNewContext(source.replace(clause,'r&&Number.isSafeInteger(r.id)'),context);
  const mutant=context.module.exports;
  const wrong=pr({runs:[{id:123,head_sha:SHA_B,status:'completed',conclusion:'success'}]});
  assert.equal(core.ci(wrong).status,'UNOBSERVED');
  assert.equal(mutant.ci(wrong).status,'PROVEN','the negative test detects cross-commit admission');
});
test('mutation negative: stale formal approvals must not pass',()=>{
  const source=readFileSync(new URL('./release-core.js',import.meta.url),'utf8');
  const clause='r.commit_id===p.head';
  assert.ok(source.includes(clause),'cannot silently skip review mutation coverage');
  const context={module:{exports:{}},globalThis:{}};
  runInNewContext(source.replace(clause,'true'),context);
  const mutant=context.module.exports;
  const wrong=pr({reviews:[{user:{login:'reviewer'},submitted_at:'2026-11-07T01:00:00Z',commit_id:SHA_B,state:'APPROVED'}]});
  assert.equal(core.review(wrong),'UNOBSERVED');
  assert.equal(mutant.review(wrong),'PROVEN','the negative test detects stale-review admission');
});
