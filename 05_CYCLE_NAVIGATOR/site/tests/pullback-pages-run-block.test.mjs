import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';

const workflow=await readFile(new URL('../../../.github/workflows/cycle-navigator-pages.yml',import.meta.url),'utf8');
const title='Build privacy-safe public bundle';
const commands=[
 'node 05_CYCLE_NAVIGATOR/site/build-public.mjs',
 'node --test 05_CYCLE_NAVIGATOR/site/tests/pullback-research-readback.test.mjs',
 'node --test 05_CYCLE_NAVIGATOR/site/tests/pullback-pages-run-block.test.mjs',
 'node 05_CYCLE_NAVIGATOR/site/build-pullback-research.mjs',
 'test -f 05_CYCLE_NAVIGATOR/site/dist/data/pullback-research.json'
];

function extractBuildRun(yaml){
 const pos=yaml.indexOf('- name: '+title);
 if(pos<0)return null;
 const end=yaml.indexOf('\n      - name:',pos+title.length);
 const step=yaml.slice(pos,end===-1?undefined:end);
 const m=step.match(/\n        run: ([^\n]+)(?:\n([\s\S]*))?/);
 return m?{scalar:m[1].trim(),body:m[2]||''}:null;
}
function check(yaml){
 const x=extractBuildRun(yaml);
 if(!x||x.scalar!=='|')return false;
 const actual=x.body.split('\n').filter(Boolean).map(s=>s.trim()).filter(Boolean);
 return actual.length===commands.length&&actual.every((s,i)=>s===commands[i]);
}
test('the ACTUAL production Pages job runs five commands in a YAML literal block',()=>{
 assert.equal(check(workflow),true,'Missing literal block | will silently fold commands');
});
test('negative mutation: removal of | fails even with all command tokens present',()=>{
 const mut=workflow.replace('run: |\n          '+commands[0],'run: '+commands[0]);
 assert.notEqual(mut,workflow);
 assert.equal(check(mut),false);
});
test('negative mutation: removal of pullback builder fails',()=>{
 const mut=workflow.replace('          '+commands[3]+'\n','');
 assert.notEqual(mut,workflow);
 assert.equal(check(mut),false);
});
test('negative mutation: missing positive file check fails',()=>{
 const mut=workflow.replace('          '+commands[4]+'\n','');
 assert.notEqual(mut,workflow);
 assert.equal(check(mut),false);
});
test('PR validation and Pages deployment use the same research exporter and both test scripts',async()=>{
 const gate=await readFile(new URL('../../../.github/workflows/cn-site-v2-gate.yml',import.meta.url),'utf8');
 for(const command of [commands[1],commands[2],commands[3],commands[4]]){
  assert.ok(workflow.includes(command),'Pages missing '+command);
  assert.ok(gate.includes(command),'PR gate missing '+command);
 }
});
