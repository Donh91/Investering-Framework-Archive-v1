/* S1 Release Control local PUBLIC-only observational history.
 * No private inputs, network access, scheduler, immutable-receipt or release authority.
 */
(function(root,factory){
 'use strict';
 var instance=factory();
 if(typeof module!=='undefined'&&module.exports)module.exports=instance;
 root.S1PublicHistory=instance;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
 'use strict';
 var PUBLIC=['Donh91/Investering-Framework-Archive-v1','Donh91/Eksperimenter-framework-','Donh91/CycleNavigator-scores'];
 var SHA=/^[a-f0-9]{40}$/i;
 function valid(x){return x&&x.schema==='S1_PUBLIC_LOCAL_OBSERVATION_v1'&&typeof x.observed_at==='string'&&
  Number.isFinite(Date.parse(x.observed_at))&&Array.isArray(x.repos)&&x.repos.length===PUBLIC.length&&
  x.repos.every(function(r){return PUBLIC.includes(r.repo)&&SHA.test(r.main_sha||'');})&&
  Array.isArray(x.prs)&&x.prs.length<=90&&x.prs.every(function(p){
   return PUBLIC.includes(p.repo)&&Number.isSafeInteger(p.number)&&p.number>0&&
    (p.head_sha===null||SHA.test(p.head_sha))&&['open','closed'].includes(p.state);
  });}
 function capture(repos,items,time){
  if(!Array.isArray(repos)||!Array.isArray(items)||repos.length!==PUBLIC.length||
   !PUBLIC.every(function(n){return repos.some(function(r){return r.repo===n&&r.ok===true&&SHA.test(r.main||'');});})||
   !Number.isFinite(Date.parse(time)))return null;
  var o={schema:'S1_PUBLIC_LOCAL_OBSERVATION_v1',observed_at:time,
   authority:'LOCAL_BROWSER_OBSERVATION_NOT_IMMUTABLE',scope:'PUBLIC_ONLY_NO_PRIVATE_DATA',
   repos:repos.map(function(r){return {repo:r.repo,main_sha:r.main};}),
   prs:items.filter(function(p){return PUBLIC.includes(p.repo)&&Number.isSafeInteger(p.number)&&p.number>0&&
     ['open','closed'].includes(p.state);}).slice(0,90).map(function(p){
    return {repo:p.repo,number:p.number,head_sha:SHA.test(p.head||'')?p.head:null,
     state:p.state,draft:!!p.draft};
   })};
  return valid(o)?o:null;
 }
 function clean(history){
  return (Array.isArray(history)?history:[]).filter(valid).slice(-28);
 }
 function append(history,observation){
  var a=clean(history);
  if(!valid(observation))return a;
  if(a.some(function(x){return x.observed_at===observation.observed_at;}))return a;
  a.push(observation);
  return a.slice(-28);
 }
 function delta(prev,curr){
  if(!valid(curr))return {changed:null,main_changed:null};
  if(!valid(prev))return {changed:null,main_changed:null};
  var a=new Map(prev.prs.map(function(p){return [p.repo+'#'+p.number,p];}));
  var b=new Map(curr.prs.map(function(p){return [p.repo+'#'+p.number,p];}));
  var keys=new Set([...a.keys(),...b.keys()]),changed=0;
  keys.forEach(function(k){var l=a.get(k),r=b.get(k);
   if(!l||!r||l.head_sha!==r.head_sha||l.state!==r.state||l.draft!==r.draft)changed++;
  });
  var mainChanges=curr.repos.filter(function(r){var old=prev.repos.find(function(p){return p.repo===r.repo;});return !old||old.main_sha!==r.main_sha;}).length;
  return {changed:changed,main_changed:mainChanges};
 }
 return {PUBLIC:PUBLIC.slice(),valid:valid,capture:capture,clean:clean,append:append,delta:delta};
});
