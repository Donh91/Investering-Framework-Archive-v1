import test from 'node:test';
import assert from 'node:assert/strict';
import {playOnce} from './play-once.mjs';
const el=()=>{const s=new Set();return {classList:{add:c=>s.add(c),remove:c=>s.delete(c),has:c=>s.has(c)}}};
const env=({reduce=false,store={},throws=false}={})=>{const timers=[];return {timers,
 matchMedia:()=>({matches:reduce}),setTimeout:(fn)=>timers.push(fn),
 sessionStorage:{getItem:k=>{if(throws)throw Error('blocked');return store[k]??null},setItem:(k,v)=>{if(throws)throw Error('blocked');store[k]=v}}}};
test('playOnce plays once per visit and removes the class afterwards',()=>{
 const store={},e=el(),x=env({store});
 assert.equal(playOnce('k',e,'c',900,x),true);assert.ok(e.classList.has('c'));assert.equal(store.k,'1');
 x.timers.forEach(f=>f());assert.ok(!e.classList.has('c'));
 assert.equal(playOnce('k',el(),'c',900,x),false,'same visit, new element: no replay');
 assert.equal(playOnce('k',e,'c',900,env()),false,'same element: never twice');
});
test('playOnce is static under reduced motion and stores nothing',()=>{
 const store={},e=el();assert.equal(playOnce('k',e,'c',900,env({reduce:true,store})),false);
 assert.ok(!e.classList.has('c'));assert.deepEqual(store,{});
});
test('playOnce survives blocked storage (plays once for this page load) and missing elements',()=>{
 const e=el();assert.equal(playOnce('k',e,'c',900,env({throws:true})),true);
 assert.equal(playOnce('k',e,'c',900,env({throws:true})),false);
 assert.equal(playOnce('k',null,'c',900,env()),false);
});
