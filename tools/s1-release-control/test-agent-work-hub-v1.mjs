import test from 'node:test';
import assert from 'node:assert/strict';
import {buildHub,ownerOf,laneOf} from './agent-work-hub-v1.mjs';
import {classify} from './discovery-inventory-v1.mjs';

const native={
  number:4,title:'Repair orphan task',state:'open',html_url:'https://github.com/Donh91/Archive/pull/4',
  draft:true,labels:[],updated_at:'2026-11-08T08:00:00Z',
  user:{login:'author-is-not-owner'},assignees:[{login:'existing-owner'}]
};
const base=(items,complete=true)=>({
 schema:'S1_DISCOVERY_INVENTORY_v1',generated_at:'2026-11-08T08:20:00Z',
 complete,repository_enumeration_complete:complete,coverage_scope:'CREDENTIAL_ACCESSIBLE_OWNER_REPOS_ONLY',warnings:[],
 repos:[{repo:'Donh91/Investering-Framework-Archive-v1',visibility:'PUBLIC',complete,
  open_pr_count:1,open_issue_count:0,items:[...items]},
 {repo:'Donh91/Investering-AI-Audit-Bridge',visibility:'PRIVATE',complete:true,
  open_pr_count:1,open_issue_count:0,items:[{...classify({...native,title:'PRIVATE_WORK'},'PR'),number:88}]},
 {repo:'Donh91/secrets',visibility:'PRIVATE',complete:true,open_pr_count:1,
  items:[{...classify(native,'PR'),title:'DO_NOT_EXPOSE'}]}]
});
test('Native GitHub assignee is explicitly distinguished from author',()=>{
 const item=classify(native,'PR');const h=buildHub(base([item]));
 assert.deepEqual(item.assignees,['existing-owner']);
 assert.equal(h.work[0].owner.logins[0],'existing-owner');
 assert.equal(h.work[0].author_not_owner,'author-is-not-owner');
 assert.equal(h.work[0].lane_hint,'OPEN_DRAFT_HINT');
 assert.equal(h.counts.by_assignee['existing-owner'],1);
 assert.equal(h.can_block_actions,false);
 assert.equal(h.release_permission,false);
});
test('Private details are excluded by default even when accidentally present',()=>{
 const h=buildHub(base([classify(native,'PR')]));
 assert.equal(h.work.length,1);
 assert.equal(JSON.stringify(h).includes('PRIVATE_WORK'),false);
 assert.equal(JSON.stringify(h).includes('DO_NOT_EXPOSE'),false);
 assert.equal(h.repo_summary.find(x=>x.visibility==='PRIVATE').details,'REDACTED');
});
test('Private caller may see authorized private records, but never restricted secrets',()=>{
 const h=buildHub(base([classify(native,'PR')]),{includePrivate:true});
 assert.equal(h.work.length,2);
 assert.equal(h.work.some(x=>x.title==='PRIVATE_WORK'),true);
 assert.equal(JSON.stringify(h).includes('DO_NOT_EXPOSE'),false);
});
test('Unknown or multiple assignees cannot be assigned via title or author guesses',()=>{
 assert.equal(ownerOf({title:'S1 owns it',author:'S1'}).status,'OWNER_UNOBSERVED');
 assert.equal(ownerOf({assignees:['a','b']}).status,'MULTIPLE_GITHUB_ASSIGNEES');
});
test('Incomplete and invalid data never blocks normal agent operation',()=>{
 const h=buildHub(base([classify(native,'PR')],false));
 assert.equal(h.coverage_complete,false);assert.equal(h.status,'PARTIAL');
 assert.equal(h.fallback,'CONTINUE_WITH_ORIGINAL_GITHUB_OWNERS');
 assert.equal(h.can_block_actions,false);
 const bad=buildHub(null);assert.equal(bad.status,'UNAVAILABLE');
 assert.equal(bad.work.length,0);assert.equal(bad.can_block_actions,false);
});
test('Open and parked status are only hints, not actual activity proof or READY',()=>{
 const w=classify({...native,draft:false,title:'Research parked'},'PR');
 assert.match(laneOf(w),/HINT/);
 assert.equal(buildHub(base([w])).work[0].original_source_recheck_required,true);
});

test('closed parked research is opt-in and excluded from active work',()=>{
 const rec=classify({number:91,title:'PARKED shadow revisit',state:'closed',labels:[]},'CLOSED_ISSUE');
 const data=base([classify(native,'PR')]);
 data.repos[0].closed_parked_candidates=[rec];
 const normal=buildHub(data),extended=buildHub(data,{includeClosedParked:true});
 assert.equal(normal.counts.open_work_items_observed,1);
 assert.equal(normal.counts.closed_research_hints,0);
 assert.equal(extended.counts.open_work_items_observed,1);
 assert.equal(extended.counts.closed_research_hints,1);
 assert.equal(extended.work.find(x=>x.kind==='CLOSED_ISSUE').lane_hint,'CLOSED_RESEARCH_HINT_NOT_ACTIVE');
 assert.equal(extended.can_block_actions,false);
});

// Security regression: malformed or forged visibility cannot expose private work.
test('unknown visibility never defaults to public; counts are unknown',()=>{
 const data=base([classify(native,'PR')]);
 data.repos.push({repo:'Donh91/Unclassified-New-Repo',visibility:'UNKNOWN',complete:true,
   open_pr_count:1,open_issue_count:0,items:[{...classify(native,'PR'),title:'SECRET_UNKNOWN'}]});
 const h=buildHub(data);
 assert.equal(h.coverage_complete,false);
 assert.equal(JSON.stringify(h).includes('SECRET_UNKNOWN'),false);
 const summary=h.repo_summary.find(x=>x.visibility==='UNKNOWN');
 assert.equal(summary.repo,null);
 assert.equal(summary.open_pr_count,null);
});
test('known private source cannot be downgraded by PUBLIC claim or a private-details flag',()=>{
 const data=base([classify(native,'PR')]);
 data.repos[1].visibility='PUBLIC';
 const h=buildHub(data,{includePrivate:true});
 assert.equal(h.coverage_complete,false);
 assert.equal(JSON.stringify(h).includes('PRIVATE_WORK'),false);
 assert.equal(h.repo_summary[1].details,'REDACTED');
});
test('restricted data-plane name is excluded case-insensitively, including opt-in',()=>{
 const data=base([classify(native,'PR')]);
 data.repos[2].repo='DONH91/SECRETS';
 const h=buildHub(data,{includePrivate:true,includeClosedParked:true});
 assert.equal(JSON.stringify(h).includes('DO_NOT_EXPOSE'),false);
 assert.equal(h.repo_summary.some(x=>/secrets/i.test(x.repo||'')),false);
});
test('non-owner repo is not an admissible source',()=>{
 const data=base([classify(native,'PR')]);
 data.repos.push({repo:'OtherOwner/public',visibility:'PUBLIC',complete:true,
   items:[{...classify(native,'PR'),title:'FOREIGN_SOURCE'}]});
 const h=buildHub(data);
 assert.equal(h.coverage_complete,false);
 assert.equal(JSON.stringify(h).includes('FOREIGN_SOURCE'),false);
});
