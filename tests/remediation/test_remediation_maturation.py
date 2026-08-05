import json
import tempfile
import unittest
from pathlib import Path

from scripts.remediation.build_remediation_maturation import build


class RemediationMaturationTests(unittest.TestCase):
    def make_repo(self, workflow):
        root = Path(tempfile.mkdtemp())
        path = root / 'research/architecture_health'
        path.mkdir(parents=True)
        (path / 'LATEST_AUTOMATION_HEALTH.json').write_text(json.dumps({'generated_at_utc':'2026-08-05T10:00:00Z','workflows':[workflow]}))
        return root

    def test_first_daily_failure_is_observed(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['LATEST_RUN_FAILED'],'live':{'failure_streak':1,'success_streak':0,'latest_run':{'id':1}}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'OBSERVED')
        self.assertEqual(row['route'], 'OBSERVE')

    def test_repeated_failure_becomes_codex_ready(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['REPEATED_CONSECUTIVE_FAILURES'],'live':{'failure_streak':3,'success_streak':0,'latest_run':{'id':2}}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'CODEX_READY')
        self.assertEqual(row['route'], 'CODEX_PR')

    def test_critical_hash_mismatch_is_immediate(self):
        root = self.make_repo({'workflow':'weekly.yml','scheduled':True,'cron_count':1,'findings':['HASH_MISMATCH'],'live':{'failure_streak':1,'latest_run':{'id':3}}})
        self.assertEqual(build(root)['items'][0]['state'], 'CODEX_READY')

    def test_authority_change_never_goes_to_codex(self):
        root = self.make_repo({'workflow':'framework.yml','scheduled':False,'cron_count':0,'findings':['AUTHORITY_BOUNDARY_CHANGE_REQUIRED'],'live':{}})
        row = build(root)['items'][0]
        self.assertEqual(row['state'], 'NEEDS_MORE_EVIDENCE')
        self.assertEqual(row['route'], 'FRAMEWORK_OWNER_PROPOSAL_ONLY')

    def test_no_automatic_code_or_merge(self):
        root = self.make_repo({'workflow':'daily.yml','scheduled':True,'cron_count':5,'findings':['LATEST_RUN_FAILED'],'live':{'failure_streak':1}})
        out = build(root)
        self.assertFalse(out['automatic_code_write'])
        self.assertFalse(out['automatic_merge'])


if __name__ == '__main__':
    unittest.main()
