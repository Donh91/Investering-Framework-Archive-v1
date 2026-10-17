import assert from 'node:assert/strict';
import {requiredBrowserAssets,firstPartySourceFile,auditBrowserEvidence} from '../browser-source-binding.mjs';

// Deterministic adversarial browser receipt tests: no API, web or browser required.
const html='<html><head><link rel="stylesheet" href="./styles.css"><link rel="stylesheet" href="./precision-accountability.css"></head><body><script src="./i18n.js" defer></script><script src="./precision-accountability.js" defer></script><script src="./compass-product-v5.js" defer></script></body></html>';
const required=requiredBrowserAssets(html);
for(const file of ['index.html','i18n.js','precision-accountability.js','compass-product-v5.js','precision-accountability.css','styles.css','data/latest.json','data/compass.json','history-scoreboard.json']){
  assert(required.includes(file),'Required browser asset missed: '+file);
}
const base='https://donh91.github.io/Investering-Framework-Archive-v1/';
assert.equal(firstPartySourceFile(base,base),'index.html');
assert.equal(firstPartySourceFile(base+'data/latest.json?v=1',base),'data/latest.json');
assert.equal(firstPartySourceFile(base+'precision-accountability.js?v=1',base),'precision-accountability.js');
assert.equal(firstPartySourceFile('https://api.coingecko.com/api/v3/global',base),null);
assert.equal(firstPartySourceFile('https://donh91.github.io/not-our-site/script.js',base),null);
assert.equal(firstPartySourceFile(base+'%2e%2e/sneaky.js',base),null);
const okResponses=required.map(file=>({file,status:200,sha256:'frozen-'+file}));
function real(engine,responses=okResponses){return {engine,width:390,language:'da',state:'REAL',synthetic:false,responses};}
function errorCode(proof,code){return proof.failures.some(x=>x.error===code);}
const healthy=auditBrowserEvidence([real('chromium'),real('webkit')],required);
assert.equal(healthy.failures.length,0,JSON.stringify(healthy.failures));
assert.equal(healthy.realContextCount,2);
const missingWebKit=okResponses.filter(x=>x.file!=='precision-accountability.css');
const missing=auditBrowserEvidence([real('chromium'),real('webkit',missingWebKit)],required);
assert(errorCode(missing,'REQUIRED_SOURCE_NOT_SUCCESSFUL_IN_CONTEXT'),'Other engine must not mask missing WebKit CSS');
const failedWebKit=auditBrowserEvidence([real('chromium'),real('webkit',okResponses.map(x=>x.file==='styles.css'?{...x,status:404,sha256:null}:x))],required);
assert(errorCode(failedWebKit,'REQUIRED_SOURCE_NOT_SUCCESSFUL_IN_CONTEXT'),'Other engine must not mask WebKit HTTP 404');
const omittedJs=auditBrowserEvidence([real('chromium'),real('webkit',okResponses.filter(x=>x.file!=='i18n.js'))],required);
assert(errorCode(omittedJs,'REQUIRED_SOURCE_NOT_SUCCESSFUL_IN_CONTEXT'),'Static generated-index JS must be mandatory');
const mixed=auditBrowserEvidence([real('chromium'),real('webkit',okResponses.map(x=>x.file==='i18n.js'?{...x,sha256:'new-revision'}:x))],required);
assert(errorCode(mixed,'MIXED_STATIC_DEPLOYMENT'),'Mixed deployment must fail');
const hiddenRuntime=auditBrowserEvidence([real('chromium',[...okResponses,{file:'additional-runtime.js',status:200,sha256:'one'}]),real('webkit',[...okResponses,{file:'additional-runtime.js',status:200,sha256:'two'}])],required);
assert(hiddenRuntime.files.includes('additional-runtime.js'),'Unexpected loaded assets must be included in receipt');
assert(errorCode(hiddenRuntime,'MIXED_STATIC_DEPLOYMENT'),'Unlisted runtime JS must not evade mismatch detection');
const optional=auditBrowserEvidence([real('chromium',[...okResponses,{file:'data/compass-event.json',status:404}]),real('webkit',okResponses)],required);
assert.equal(optional.failures.length,0,'Explicit optional event source may fail closed in consumer without claiming a 200');
assert.equal(optional.optionalUnavailable.length,1,'Optional source failure must remain visible in receipt');
const changedWithin=auditBrowserEvidence([real('chromium',[...okResponses,{file:'data/compass.json',status:200,sha256:'new-data'}]),real('webkit')],required);
assert(errorCode(changedWithin,'SOURCE_CHANGED_WITHIN_CONTEXT'),'Multiple versions during one real render must fail');
const syntheticOnly=auditBrowserEvidence([{...real('chromium'),synthetic:true}],required);
assert(errorCode(syntheticOnly,'NO_REAL_BROWSER_CONTEXTS'));
console.log('PASS CN real-browser source-binding adversarial unit tests');
