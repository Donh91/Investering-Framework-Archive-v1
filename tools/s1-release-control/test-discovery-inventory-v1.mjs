import test from 'node:test';
import assert from 'node:assert/strict';
import {inventory,classify,REPOS} from './discovery-inventory-v1.mjs';
test('private repos are included but details redacted by default',async()=>{
 const calls=[];
 const fetcher=async url=>{calls.push(url);return {ok:true,json:async()=>url.includes('/pulls?')?[{number:7,title:'private title',html_url:'https://github.com/example/pull/7'}]:[{number:8,title:'research parked',html_url:'https://github.com/example/issues/8'},{number:7,pull_request:{url:'x'}}]};};
 const x=await inventory({fetcher,token:''});
 assert.equal(x.repos.length,REPOS.length);
 assert.equal(x.complete,true);
 assert.equal(x.repos[3].open_pr_count,1);
 assert.equal(x.repos[3].open_issue_count,1);
 assert.equal(x.repos[3].items.length,0);
 assert.equal(x.repos[3].private_details,'REDACTED_LOCAL_ONLY');
 assert.equal(x.repos[0].items.length,2);
 assert.equal(x.release_permission,false);
 assert.equal(calls.length,10);
});
test('403 never becomes a false zero or complete inventory',async()=>{
 const x=await inventory({fetcher:async()=>({ok:false,status:403}),token:''});
 assert.equal(x.complete,false);
 assert.equal(x.repos[3].open_pr_count,null);
 assert.equal(x.repos[3].complete,false);
});
test('parked is a hint, never release permission',()=>{
 const x=classify({number:4,title:'parked research',labels:[]},'ISSUE');
 assert.equal(x.parked_hint,true);
 assert.equal(x.disposition,'UNOBSERVED_NEEDS_ORIGINAL_OWNER_AND_NATIVE_GATES');
});
