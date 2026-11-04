import importlib.util
import json
import tempfile
import unittest
import os
import io
from contextlib import redirect_stdout
from unittest.mock import patch
from pathlib import Path

SCRIPT = Path('scripts/framework_intelligence/operational_memory_fail_to_codex_intake_v1.py')
spec = importlib.util.spec_from_file_location('operational_memory_fail_to_codex_intake_v1', SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

VALIDATOR_SCRIPT = Path('scripts/remediation/merge_codex_research_intake.py')
validator_spec = importlib.util.spec_from_file_location('merge_codex_research_intake', VALIDATOR_SCRIPT)
validator = importlib.util.module_from_spec(validator_spec)
validator_spec.loader.exec_module(validator)


def audit_doc(status='FAIL', failures=None, head='a' * 40):
    return {
        'contract': 'OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT_v1',
        'generated_at_utc': '2026-09-15T12:00:00Z',
        'status': status,
        'source_head_sha': head,
        'failures': failures or ['stale_memory_not_quarantined:OE-1'],
        'warnings': [],
    }


class OperationalMemoryFailToCodexIntakeV1Test(unittest.TestCase):
    def test_workflow_native_roundtrip_dedupes_and_closes_once(self):
        workflow=Path('.github/workflows/framework-learning-supervisor.yml').read_text()
        block=workflow.split('      - name: Manage Operational Memory audit escalation\n',1)[1].split('      - name: Route failed audit',1)[0]
        source=block.split("          python - <<'PY'\n",1)[1].rsplit('          PY',1)[0]
        source='\n'.join(line[10:] if line.startswith('          ') else line for line in source.splitlines())
        repo='Donh91/Investering-Framework-Archive-v1'
        comments=[]
        runs={}
        opened=False
        closed=0
        current=100
        def check_output(args,**kwargs):
            nonlocal opened
            if args[1:3]==['issue','list']:
                return json.dumps([{'number':42,'title':'incident','author':{'login':'github-actions[bot]'}}] if opened else [])
            if args[1:3]==['issue','create']:
                opened=True
                return f'https://github.com/{repo}/issues/42\n'
            if args[1]=='api':
                endpoint=args[2]
                if '/comments?' in endpoint:
                    return json.dumps(comments)
                if '/actions/runs/' in endpoint:
                    return json.dumps(runs[int(endpoint.rsplit('/',1)[1])])
                return json.dumps({'comments':len(comments)})
            self.fail(str(args))
        def run(args,**kwargs):
            nonlocal opened,closed
            if args[1:3]==['issue','comment']:
                comments.append({'id':len(comments)+1,'body':args[args.index('--body')+1],
                                 'user':{'login':'github-actions[bot]','type':'Bot'},
                                 'created_at':'2026-11-04T10:02:00Z','updated_at':'2026-11-04T10:02:00Z'})
            elif args[1:3]==['issue','close']:
                opened=False
                closed+=1
            else:
                self.fail(str(args))
        previous_cwd=Path.cwd()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            try:
                os.chdir(root)
                for tick in range(16):
                    current=100+tick
                    runs[current]={'id':current,'path':'.github/workflows/framework-learning-supervisor.yml',
                        'head_branch':'main','event':'schedule','status':'completed',
                        'html_url':f'https://github.com/{repo}/actions/runs/{current}',
                        'run_started_at':'2026-11-04T10:00:00Z','updated_at':'2026-11-04T10:05:00Z'}
                    audit=audit_doc(head=str(tick).zfill(40))
                    if tick==12:
                        audit['failures']=['different_failure']
                    elif tick>=13:
                        audit['status']='PASS'
                    self.write_audit(root,audit)
                    env={'GITHUB_REPOSITORY':repo,'ISSUE_TITLE':'incident','GITHUB_SERVER_URL':'https://github.com','GITHUB_RUN_ID':str(current)}
                    with patch.dict(os.environ,env),patch('subprocess.check_output',side_effect=check_output),patch('subprocess.run',side_effect=run),redirect_stdout(io.StringIO()):
                        exec(compile(source,'workflow_notice','exec'),{})
                    if tick==11:
                        self.assertEqual(len(comments),1)
                self.assertEqual(len(comments),3)  # first fail, changed fail, recovery
                self.assertEqual(closed,1)
            finally:
                os.chdir(previous_cwd)

    def test_twelve_identical_failures_notify_once_despite_clock_and_head(self):
        previous=None
        notices=0
        for tick in range(12):
            audit=audit_doc(head=str(tick).zfill(40))
            audit['generated_at_utc']=f'2026-11-04T{tick:02}:00:00Z'
            if mod.notification_action(audit,previous,census_complete=True)=='PUBLISH_FAILURE':
                notices+=1
                previous=mod.notice_payload(audit,100+tick)
        self.assertEqual(notices,1)
        changed=audit_doc(failures=['new_integrity_failure'])
        self.assertEqual(mod.notification_action(changed,previous,census_complete=True),'PUBLISH_FAILURE')

    def test_recovery_notified_once_and_recurrence_reactivates(self):
        previous=mod.notice_payload(audit_doc(),100)
        healthy=audit_doc(status='PASS')
        self.assertEqual(mod.notification_action(healthy,previous,census_complete=True),'PUBLISH_RECOVERY')
        previous=mod.notice_payload(healthy,101)
        self.assertEqual(mod.notification_action(healthy,previous,census_complete=True),'RECOVERY_ALREADY_NOTIFIED')
        self.assertEqual(mod.notification_action(audit_doc(),previous,census_complete=True),'PUBLISH_FAILURE')

    def test_incomplete_census_never_claims_delivery_or_recovery(self):
        for status in ('FAIL','PASS'):
            self.assertEqual(mod.notification_action(audit_doc(status=status),None,census_complete=False),'NOTICE_EVIDENCE_UNAVAILABLE')

    def test_native_receipt_rejects_spoofed_actor_run_and_late_marker(self):
        repo='Donh91/Investering-Framework-Archive-v1'
        payload=mod.notice_payload(audit_doc(),100)
        comment={'user':{'login':'github-actions[bot]','type':'Bot'},
                 'body':mod.NOTICE_PREFIX+json.dumps(payload),
                 'created_at':'2026-11-04T10:02:00Z','updated_at':'2026-11-04T10:02:00Z'}
        run={'id':100,'path':'.github/workflows/framework-learning-supervisor.yml',
             'head_branch':'main','event':'schedule','status':'completed',
             'html_url':f'https://github.com/{repo}/actions/runs/100',
             'run_started_at':'2026-11-04T10:00:00Z','updated_at':'2026-11-04T10:05:00Z'}
        self.assertEqual(mod.native_notice(comment,run,repo),payload)
        for user in ({'login':'someone','type':'User'}, {'login':'github-actions[bot]','type':'User'}):
            self.assertIsNone(mod.native_notice({**comment,'user':user},run,repo))
        for key,value in [('path','.github/workflows/unrelated.yml'),('head_branch','feature'),('event','pull_request'),('id',101),('status','in_progress')]:
            self.assertIsNone(mod.native_notice(comment,{**run,key:value},repo))
        self.assertIsNone(mod.native_notice({**comment,'created_at':'2026-11-04T10:06:00Z'},run,repo))
        self.assertIsNone(mod.native_notice(comment,run,'other/repository'))
        self.assertIsNone(mod.native_notice({**comment,'updated_at':'2026-11-04T10:03:00Z'},run,repo))

    def test_dispatch_only_new_intake_natural_receiver_handles_pending(self):
        result={'created':True,'reason':'FAIL_ROUTED_TO_BOUNDED_CODEX_INTAKE','candidate_id':'original','path':'original.json'}
        self.assertTrue(mod.maturation_dispatch_required(result))
        for patch in ({'created':False},{'created':'true'},{'reason':'MATCHING_PENDING_CANDIDATE_EXISTS'},{'path':None}):
            self.assertFalse(mod.maturation_dispatch_required({**result,**patch}))

    def write_audit(self, root: Path, doc: dict) -> Path:
        path = root / 'research/framework_learning/operational_memory/LATEST_OPERATIONAL_MEMORY_POST_PRODUCTION_AUDIT.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc))
        return path

    def test_non_fail_is_noop(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc(status='PASS'))
            out = mod.route(root, audit)
            self.assertFalse(out['created'])
            self.assertEqual(out['reason'], 'AUDIT_NOT_FAIL')

    def test_fail_creates_valid_bounded_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc())
            out = mod.route(root, audit)
            self.assertTrue(out['created'])
            candidate_path = root / out['path']
            candidate = json.loads(candidate_path.read_text())
            self.assertEqual(candidate['contract'], 'CODEX_RESEARCH_CANDIDATE_v1')
            self.assertEqual(candidate['status'], 'SUBMITTED')
            self.assertEqual(candidate['authority_boundary'], 'CODE_REMEDIATION_ONLY')
            self.assertFalse(candidate['requires_framework_owner_authority'])
            self.assertEqual(set(candidate['forbidden_changes']), set(mod.REQUIRED_FORBIDDEN))
            self.assertTrue(candidate['acceptance_tests']['positive'])
            self.assertTrue(candidate['acceptance_tests']['negative'])
            self.assertTrue(candidate['authority']['code_remediation_only'])
            self.assertFalse(candidate['authority']['automatic_merge'])
            self.assertEqual(Path(out['path']).stem, candidate['candidate_id'])
            status, reasons = validator.validate_candidate(candidate_path, candidate)
            self.assertEqual(status, 'VALID', reasons)
            self.assertEqual(reasons, [])

    def test_same_fail_pending_candidate_dedupes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc())
            first = mod.route(root, audit)
            second = mod.route(root, audit)
            self.assertTrue(first['created'])
            self.assertFalse(second['created'])
            self.assertEqual(second['candidate_id'], first['candidate_id'])
            self.assertEqual(second['reason'], 'MATCHING_PENDING_CANDIDATE_EXISTS')

    def test_completed_candidate_allows_one_recurrence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            audit = self.write_audit(root, audit_doc(head='b' * 40))
            first = mod.route(root, audit)
            completion = root / 'research/codex/completions' / f"{first['candidate_id']}.json"
            completion.parent.mkdir(parents=True, exist_ok=True)
            completion.write_text('{}')
            second = mod.route(root, audit)
            self.assertTrue(second['created'])
            self.assertNotEqual(second['candidate_id'], first['candidate_id'])
            self.assertIn('bbbbbbbbbb', second['candidate_id'])
            third = mod.route(root, audit)
            self.assertFalse(third['created'])
            self.assertEqual(third['candidate_id'], second['candidate_id'])

    def test_failure_fingerprint_is_order_insensitive(self):
        a = audit_doc(failures=['b', 'a', 'a'])
        b = audit_doc(failures=['a', 'b'])
        self.assertEqual(mod.failure_fingerprint(a), mod.failure_fingerprint(b))

    def test_allowed_scope_does_not_broaden_authority(self):
        forbidden_tokens = {'market gates', 'model weights', 'canonical authority', 'portfolio logic', 'api budget', 'new policy semantics'}
        allowed = ' '.join(mod.ALLOWED_SCOPE).lower()
        self.assertFalse(any(token in allowed for token in forbidden_tokens))


if __name__ == '__main__':
    unittest.main()

