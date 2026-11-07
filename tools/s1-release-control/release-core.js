/* S1 Release Control shared conservative status engine.
 * Presentation-only. No release authority. Node CJS and same-origin browser.
 */
(function(root, build){
  "use strict";
  var core=build();
  if(typeof module!=="undefined" && module.exports)module.exports=core;
  root.S1ReleaseCore=core;
})(typeof globalThis!=="undefined"?globalThis:this,function(){
  "use strict";
  var SHA40=/^[0-9a-f]{40}$/i;
  var safeSha=function(s){return typeof s==="string"&&SHA40.test(s);};
  var id=function(p){return p.repo+"#"+p.number;};
  function risk(p){
    if(p.seed)return p.risk||"UNKNOWN";
    if(!p.filesObserved||!Number.isSafeInteger(p.changedFiles)||p.changedFiles<0||p.changedFiles>100||!Array.isArray(p.files)||p.files.length!==p.changedFiles||p.files.length>=100)return "UNKNOWN";
    var names=p.files.map(function(f){return f.filename||"";});
    if(names.some(function(n){return /(^\.github\/workflows\/|^AGENTS\.md$|\/governance\/|\/api_agent\/|\/backup\/|\/recovery\/|\/billing\/|\/permissions\/|\/security\/|\/secrets\/|charge.once|allowlist|safety.policy|release.policy|build-public\.mjs)/i.test(n);}))return "HIGH";
    return p.changedFiles>=20?"MEDIUM":"LOW";
  }
  function ci(p){
    if(!safeSha(p.head)||!p.runObserved||!Array.isArray(p.runs))return {status:"UNOBSERVED",n:0,label:"exact-HEAD ukendt"};
    var runs=p.runs.filter(function(r){return r&&r.head_sha===p.head&&Number.isSafeInteger(r.id);});
    if(!runs.length)return {status:"UNOBSERVED",n:0,label:"ingen exact-HEAD runs"};
    var good=runs.filter(function(r){return r.status==="completed"&&r.conclusion==="success";}).length;
    var fail=runs.some(function(r){return ["failure","cancelled","timed_out","action_required"].includes(r.conclusion);});
    return {status:fail?"BLOCKED":good===runs.length?"PROVEN":"UNOBSERVED",n:runs.length,label:good+"/"+runs.length+" observerede runs",required_checks:"UNOBSERVED"};
  }
  function review(p){
    if(!safeSha(p.head)||!p.reviewsObserved||!Array.isArray(p.reviews))return "UNOBSERVED";
    var latest={};
    p.reviews.forEach(function(r){
      if(!r||!r.user||!r.user.login)return;
      var who=r.user.login;
      if(!latest[who]||String(r.submitted_at||"")>=String(latest[who].submitted_at||""))latest[who]=r;
    });
    return Object.keys(latest).some(function(who){
      var r=latest[who];
      return who!==p.author&&r.state==="APPROVED"&&r.commit_id===p.head;
    })?"PROVEN":"UNOBSERVED";
  }
  function disposition(p){
    if(p.state!=="open"){
      if(p.merged&&safeSha(p.merge_commit_sha))return "MERGED";
      return "CLOSED";
    }
    if(p.draft||p.risk==="HIGH")return "HOLD";
    if(!safeSha(p.head)||p.risk==="UNKNOWN"||ci(p).status!=="PROVEN")return "UNOBSERVED";
    return "PROPOSED"; // Merely a candidate for examination, NEVER permission to merge.
  }
  function next(p){
    if(p.state!=="open")return {code:"OBSERVE",label:"Verificér main og faktisk outcome"};
    if(p.draft&&p.risk==="HIGH")return {code:"RECOVERY",label:"Recovery + HIGH_IMPACT"};
    if(p.draft)return {code:"DRAFT",label:"Afklar draft"};
    if(p.risk==="HIGH")return {code:"RECOVERY",label:"Safepoint og governance"};
    if(p.risk==="UNKNOWN"||!safeSha(p.head))return {code:"OBSERVE",label:"Verificér HEAD og fuldt filscope"};
    if(ci(p).status!=="PROVEN")return {code:"CI",label:"Verificér exact-HEAD runs og required checks"};
    if(review(p)!=="PROVEN")return {code:"REVIEW",label:"Teknisk review og ejerbeslutning"};
    return {code:"REVIEW",label:"Kontrollér branchregler og releasegates"};
  }
  function priority(p){
    var s=p.state==="open"?100:0;
    if(p.risk==="HIGH")s+=18;
    if(p.draft)s+=8;
    if(p.labels&&p.labels.some(function(x){return /^(P0|priority: p0)$/i.test(x);}))s+=50;
    if(p.labels&&p.labels.some(function(x){return /^(P1|priority: p1)$/i.test(x);}))s+=25;
    return s;
  }
  function rank(items){
    return items.slice().filter(function(p){return p.state==="open"&&safeSha(p.head);}).sort(function(a,b){
      return priority(b)-priority(a)||String(a.repo).localeCompare(String(b.repo))||a.number-b.number;
    });
  }
  function project(p,main,observedAt){
    var observed=!!(p.filesObserved&&p.runObserved&&p.reviewsObserved&&safeSha(main));
    return {
      repo:p.repo,pr_number:p.number,head_sha:safeSha(p.head)?p.head:null,main_sha:safeSha(main)?main:null,
      base_sha:safeSha(p.base)?p.base:null,owner:p.author||null,risk:p.risk||risk(p),
      evidence_class:observed?"SOURCE_OBSERVED_PARTIAL_GATES":"UNOBSERVED",
      ci_observation:ci(p),review_observation:review(p),release_disposition:disposition(p),
      required_gates:{required_checks:"UNOBSERVED",branch_rules:"UNOBSERVED",separation:"UNOBSERVED",recovery:"UNOBSERVED",billing:"UNOBSERVED",owner_release:"UNOBSERVED"},
      dependencies:[],dependencies_evidence:"UNOBSERVED",next_action:next(p),
      source_ref:"https://github.com/"+p.repo+"/pull/"+p.number,
      head_ref:safeSha(p.head)?"https://github.com/"+p.repo+"/commit/"+p.head:null,
      observed_at:observedAt,execution_provenance:"INTERACTIVE_OR_READONLY_PROJECTION",
      autonomy_evidence:"UNOBSERVED",merge_authorized:false,production_verified:false
    };
  }
  return Object.freeze({schema:"S1_RELEASE_PROJECTION_v1",safeSha:safeSha,id:id,risk:risk,ci:ci,review:review,disposition:disposition,next:next,rank:rank,project:project});
});
