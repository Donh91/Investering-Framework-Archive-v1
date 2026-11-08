import test from 'node:test';
import assert from 'node:assert/strict';
import {createRequire} from 'node:module';
const require=createRequire(import.meta.url);
const H=require('./history-core.js');
const MAIN='a'.repeat(40),HEAD='b'.repeat(40);
const repos=H.PUBLIC.map(repo=>({repo,ok:true,main:MAIN}));
const items=[{repo:H.PUBLIC[0],number:18,head:HEAD,state:'open',draft:false,title:'Public'}];
test('capture is restricted to three fully observed public repositories',()=>{
 const now=new Date().toISOString(),r=H.capture(repos,items,now);
 assert.equal(r.repos.length,3);assert.equal(r.prs.length,1);assert.equal(H.valid(r),true);
 assert.equal(H.capture(repos.slice(0,2),items,now),null);
 assert.equal(H.capture(repos.map((x,i)=>i===0?{...x,ok:false}:x),items,now),null);
});
test('private items, titles, secrets, full runs and review contents never persist',()=>{
 const privateItem={repo:'Donh91/Meme-Alpha-Lab',number:42,title:'PRIVATE_SECRET',head:HEAD,state:'open'};
 const x=H.capture(repos,[...items,privateItem],new Date().toISOString());
 assert.ok(x);assert.equal(x.prs.length,1);assert.equal(JSON.stringify(x).includes('PRIVATE_SECRET'),false);
 assert.equal(JSON.stringify(x).includes('Public'),false);
 assert.equal(JSON.stringify(x).includes('Meme-Alpha-Lab'),false);
});
test('closed/open and head changes can be compared without claiming completeness',()=>{
 const a=H.capture(repos,items,'2026-11-08T10:00:00.000Z');
 const b=H.capture(repos,[{...items[0],head:'c'.repeat(40)}],'2026-11-08T11:00:00.000Z');
 assert.equal(H.delta(a,b).changed,1);
 assert.equal(H.delta(null,b).changed,null);
});
test('invalid local snapshots fail closed and history is bounded and deduplicated',()=>{
 const a=H.capture(repos,items,'2026-11-08T10:00:00.000Z');
 assert.equal(H.append([],a).length,1);assert.equal(H.append([a],a).length,1);
 const forged={...a,repos:[{repo:'Donh91/secrets',main_sha:MAIN}]};
 assert.equal(H.append([],forged).length,0);
 assert.equal(H.clean([a,forged]).length,1);
 let list=[];for(let i=0;i<40;i++){list=H.append(list,H.capture(repos,items,new Date(Date.UTC(2026,10,8,10,i)).toISOString()));}
 assert.equal(list.length,28);
});
