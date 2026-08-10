import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation.build_remediation_maturation import build, signature
from scripts.remediation.write_transition_receipt import build_receipt


class RemediationMaturationTests(unittest.TestCase):
    def make_repo(self, workflow):
        root = Path(tempfile.mkdtemp())
        path = root / 'research/architecture_health'
        path.mkdir(parents=True)
        (path / 'LATEST_AUTOMATION_HEALTH.json').write_text(json.dumps({'generated_at_utc':'2026-08-05T10:00:00Z','workflows':[workflow]}))
        return root

    def save_prior(self, root, items):
        path = root / 'research/remediation'
        path.mkdir(parents=True, exist_ok=True)
        (path / 'LATEST_REMEDIATION_QUEUE.json').write_text(json.dumps({'items': items}))

    def save_tasks(self, root, tasks):
        (root / 'LATEST_CODEX_READY_TASKS.json').write_text(json.dumps({'tasks': tasks}))

    def save_transition(self, root, sig, **extra):
        path = root / 'research/remediation/transitions'
        path.mkdir(parents=True, exist_ok=True)
        data = {'contract':'REMEDIATION_TRANSITION_RECEIPT_v1','signature':sig,'state':'IN_REMEDIATION','branch':'agent/fix'}
        data.update(extra)
        (path / f'{sig}.json').write_text(json.dumps(data))

    def test_first_daily_failure_is_observed(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['LATEST_RUN_FAILED'],'live':{'failure_streak':1,'success_streak':0,'latest_run':{'id':1}}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'OBSERVED')
        self.assertEqual(row['route'], 'OBSERVE')

    def test_repeated_failure_becomes_codex_ready_with_goal_contract(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['REPEATED_CONSECUTIVE_FAILURES'],'live':{'failure_streak':3,'success_streak':0,'latest_run':{'id':2}}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'CODEX_READY')
        self.assertEqual(row['route'], 'CODEX_PR')
        for key in ('objective','precondition','success_evidence','clean_noop_condition','stop_condition','escalation_condition','task_contract_sha256'):
            self.assertTrue(row.get(key), key)
        self.assertTrue(row['transition_receipt_required'])
        self.assertIn(row['signature'], row['fresh_state_preflight_command'])

    def test_non_actionable_expected_block_is_not_remediation_work(self):
        root = self.make_repo({'workflow':'frozen.yml','scheduled':False,'cron_count':0,'lifecycle_state':'EXPECTED_BLOCK','findings':['EXPECTED_BLOCK'],'live':{'failure_streak':5,'latest_run':{'id':3}}})
        out = build(root)
        self.assertEqual(out['items'], [])
        self.assertEqual(out['codex_ready_tasks'], [])

    def test_critical_hash_mismatch_is_immediate(self):
        root = self.make_repo({'workflow':'weekly.yml','scheduled':True,'cron_count':1,'findings':['HASH_MISMATCH'],'live':{'failure_streak':1,'latest_run':{'id':3}}})
        self.assertEqual(build(root)['items'][0]['state'], 'CODEX_READY')

    def test_authority_change_never_goes_to_codex(self):
        root = self.make_repo({'workflow':'framework.yml','scheduled':False,'cron_count':0,'findings':['AUTHORITY_BOUNDARY_CHANGE_REQUIRED'],'live':{}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'NEEDS_MORE_EVIDENCE')
        self.assertEqual(row['route'], 'FRAMEWORK_OWNER_PROPOSAL_ONLY')

    def test_codex_ready_disappears_before_binding_becomes_clean_noop(self):
        root = self.make_repo({'workflow':'other.yml','scheduled':False,'cron_count':0,'findings':[],'live':{}})
        sig = signature('daily.yml','REPEATED_CONSECUTIVE_FAILURES')
        self.save_prior(root, [{'signature':sig,'workflow':'daily.yml','finding':'REPEATED_CONSECUTIVE_FAILURES','state':'CODEX_READY'}])
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'CLEARED_NO_CHANGE')
        self.assertEqual(row['terminal_reason'], 'FINDING_ABSENT_BEFORE_REMEDIATION_BINDING')

    def test_transition_receipt_binds_current_finding_to_in_remediation(self):
        finding = 'REPEATED_CONSECUTIVE_FAILURES'
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':[finding],'live':{'failure_streak':3,'latest_run':{'id':2}}})
        sig = signature('daily.yml', finding)
        self.save_transition(root, sig)
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'IN_REMEDIATION')
        self.assertEqual(row['route'], 'CODEX_PR_IN_PROGRESS')
        self.assertEqual(row['transition_receipt']['signature'], sig)

    def test_bound_fix_moves_to_post_fix_then_resolved(self):
        sig = signature('daily.yml','REPEATED_CONSECUTIVE_FAILURES')
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':[],'live':{'success_streak':1}})
        self.save_prior(root, [{'signature':sig,'workflow':'daily.yml','finding':'REPEATED_CONSECUTIVE_FAILURES','state':'IN_REMEDIATION','post_fix_successes':0}])
        self.save_transition(root, sig)
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'POST_FIX_OBSERVATION')
        self.assertEqual(row['post_fix_successes'], 1)

        self.save_prior(root, [row])
        row2 = build(root)['items'][0]
        self.assertEqual(row2['state'], 'POST_FIX_OBSERVATION')
        self.assertEqual(row2['post_fix_successes'], 2)

        self.save_prior(root, [row2])
        row3 = build(root)['items'][0]
        self.assertEqual(row3['state'], 'RESOLVED')
        self.assertEqual(row3['post_fix_successes'], 3)
        self.assertEqual(row3['terminal_reason'], 'POST_FIX_GATE_SATISFIED')

    def test_reappearing_signature_after_post_fix_is_reopened(self):
        finding = 'REPEATED_CONSECUTIVE_FAILURES'
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':[finding],'live':{'failure_streak':2,'latest_run':{'id':4}}})
        sig = signature('daily.yml', finding)
        self.save_prior(root, [{'signature':sig,'workflow':'daily.yml','finding':finding,'state':'POST_FIX_OBSERVATION','post_fix_successes':1}])
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'REOPENED')

    def test_transition_writer_rejects_stale_task_and_unsafe_branch(self):
        finding = 'REPEATED_CONSECUTIVE_FAILURES'
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':[finding],'live':{'failure_streak':3,'latest_run':{'id':2}}})
        task = build(root)['codex_ready_tasks'][0]
        self.save_tasks(root, [task])
        receipt = build_receipt(root, task['signature'], 'agent/fix-daily')
        self.assertEqual(receipt['state'], 'IN_REMEDIATION')
        self.assertEqual(receipt['task_contract_sha256'], task['task_contract_sha256'])
        with self.assertRaisesRegex(ValueError, 'UNSAFE_REMEDIATION_BRANCH'):
            build_receipt(root, task['signature'], 'main')

        health_path = root / 'research/architecture_health/LATEST_AUTOMATION_HEALTH.json'
        health_path.write_text(json.dumps({'generated_at_utc':'2026-08-05T11:00:00Z','workflows':[{'workflow':'daily.yml','findings':[]}]}))
        with self.assertRaisesRegex(ValueError, 'STALE_TASK_NO_CHANGE'):
            build_receipt(root, task['signature'], 'agent/fix-daily')

    def test_no_automatic_code_or_merge(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['LATEST_RUN_FAILED'],'live':{'failure_streak':1}})
        out = build(root)
        self.assertFalse(out['automatic_code_write'])
        self.assertFalse(out['automatic_merge'])


if __name__ == '__main__':
    unittest.main()
