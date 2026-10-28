import json
import unittest

from scripts.api_agent.endgame_progress_packet import manifest


class EndgameProgressPacketTests(unittest.TestCase):
    def valid(self):
        return {"contract":"TERRA_ENDGAME_PROGRESS_QUEUE_v1","active":
                {"work_id":"CN_W45_PROSPECTIVE_ISSUER_P0_20261028",
                 "owner_pr":1825,"expected_pr_head":"a"*40,"objective":"Bounded original source audit",
                 "paths":["scripts/cycle_navigator/prospective_range_bridge.py"]}}

    def test_valid_original_pr(self):
        x=manifest(self.valid())
        self.assertEqual(x["owner_pr"],1825)

    def test_original_pr_exact_head_required(self):
        x=self.valid()
        x["active"]["expected_pr_head"]="unknown"
        with self.assertRaises(ValueError):manifest(x)

    def test_no_path_escape(self):
        for bad in ("../secrets/README.md","/etc/passwd","research/../secrets/README.md"):
            x=self.valid()
            x["active"]["paths"]=[bad]
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                manifest(x)

    def test_no_unapproved_repo_or_pr(self):
        x=self.valid()
        x["active"]["owner_pr"]=9999
        with self.assertRaises(ValueError):manifest(x)

    def test_no_unbounded_scope_or_payment_fingerprint(self):
        x=self.valid()
        x["active"]["paths"]=["scripts/x.py"]*10
        with self.assertRaises(ValueError):manifest(x)
        x=self.valid()
        x["active"]["work_id"]="x; echo secret"
        with self.assertRaises(ValueError):manifest(x)

    def test_contract_locked(self):
        x=self.valid()
        x["contract"]="INVALID"
        with self.assertRaises(ValueError):manifest(x)


if __name__=="__main__":
    unittest.main()
