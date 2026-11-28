import test from 'node:test';
import assert from 'node:assert/strict';
import {pagesArtifactConfig,inspectArtifactList,waitPagesArtifact} from './wait-pages-artifact.mjs';
const head='a'.repeat(40),env={GITHUB_REPOSITORY:'owner/repo',GITHUB_RUN_ID:'100',GITHUB_RUN_ATTEMPT:'2',PAGES_ARTIFACT_ID:'700',GITHUB_SHA:head,GITHUB_REF:'refs/heads/main',GH_TOKEN:'test-token'};
const c=pagesArtifactConfig(env);
const artifact=()=>({name:'github-pages',id:700,workflow_run:{id:100,head_sha:head,head_branch:'main'},expired:false,size_in_bytes:100});
const body=(...artifacts)=>({total_count:artifacts.length,artifacts});
const reply=(status,payload)=>({status,text:async()=>JSON.stringify(payload)});
test('exact current upload id and run are required',()=>{
 assert.equal(inspectArtifactList(body(),c),null);
 assert.deepEqual(inspectArtifactList(body(artifact()),c),{id:700,run:100,attempt:2,head,size:100});
 for(const mutate of [a=>a.id=699,a=>a.workflow_run.id=99,a=>a.workflow_run.head_sha='b'.repeat(40),a=>a.workflow_run.head_branch='feature',a=>a.expired=true,a=>a.size_in_bytes=0,a=>a.name='other']){
  const a=artifact();mutate(a);assert.throws(()=>inspectArtifactList(body(a),c),/IDENTITY_MISMATCH/);
 }
 assert.throws(()=>inspectArtifactList(body(artifact(),artifact()),c),/DUPLICATE/);
 assert.throws(()=>inspectArtifactList({total_count:1,artifacts:[]},c),/INCONSISTENT/);
});
test('missing or malformed trusted context fails closed',()=>{
 for(const [k,v] of [['GITHUB_REF','refs/heads/feature'],['GITHUB_RUN_ID','1e2'],['PAGES_ARTIFACT_ID',''],['GH_TOKEN',''],['GITHUB_REPOSITORY','../repo'],['GITHUB_SHA','x']])
  assert.throws(()=>pagesArtifactConfig({...env,[k]:v}),/CONFIG_INVALID/);
});
test('metadata propagation and transient HTTP/network failures are bounded',async()=>{
 const responses=[null,reply(502,{}),reply(200,body()),reply(200,body(artifact()))],sleeps=[];
 const result=await waitPagesArtifact(c,{sleep:async n=>sleeps.push(n),fetchImpl:async(url,opts)=>{
  assert.match(url,/^https:\/\/api.github.com\/repos\/owner\/repo\/actions\/runs\/100\/artifacts\?/);
  assert.equal(opts.redirect,'error');const r=responses.shift();if(!r)throw Error('network');return r;
 }});
 assert.equal(result.status,'REST_VISIBLE_NOT_DEPLOYED');assert.equal(result.polls,4);assert.deepEqual(sleeps,[2000,4000,6000,5000]);
 assert.ok(!JSON.stringify(result).includes('test-token'));
});
test('no retry on authorization or wrong identity; timeout never claims success',async()=>{
 let calls=0;
 await assert.rejects(waitPagesArtifact(c,{sleep:async()=>{},fetchImpl:async()=>{calls++;return reply(403,{})}}),/HTTP_403/);assert.equal(calls,1);
 calls=0;await assert.rejects(waitPagesArtifact(c,{sleep:async()=>{},fetchImpl:async()=>{calls++;return reply(200,body())}}),/VISIBILITY_TIMEOUT/);assert.equal(calls,6);
 calls=0;const a=artifact();a.id=699;
 await assert.rejects(waitPagesArtifact(c,{sleep:async()=>{},fetchImpl:async()=>{calls++;return reply(200,body(a))}}),/IDENTITY_MISMATCH/);assert.equal(calls,1);
});
