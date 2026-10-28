import json
import unittest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent.endgame_progress_packet import manifest, build, original_pr_head_admitted


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

    def test_self_pr_single_commit_checkout_admitted_only_for_exact_parent(self):
        x = self.valid()
        x["active"].update(owner_pr=1823, expected_pr_head="a" * 40)
        with patch("scripts.api_agent.endgame_progress_packet.git",
                   side_effect=[b"b" * 40, b"a" * 40]) as git_read:
            self.assertTrue(original_pr_head_admitted(x["active"], "b" * 40))
            self.assertEqual(git_read.call_count, 2)

    def test_self_pr_stale_or_wrong_checkout_fails_closed(self):
        x = self.valid()
        x["active"].update(owner_pr=1823, expected_pr_head="a" * 40)
        for checkout, parent in (("c" * 40, "a" * 40),
                                 ("b" * 40, "c" * 40)):
            with self.subTest(checkout=checkout, parent=parent), patch(
                "scripts.api_agent.endgame_progress_packet.git",
                side_effect=[checkout.encode(), parent.encode()]
            ):
                self.assertFalse(original_pr_head_admitted(x["active"], "b" * 40))

    def test_other_pr_head_drift_never_uses_parent_exception(self):
        x = self.valid()
        x["active"].update(owner_pr=1814, expected_pr_head="a" * 40)
        with patch("scripts.api_agent.endgame_progress_packet.git") as git_read:
            self.assertFalse(original_pr_head_admitted(x["active"], "b" * 40))
            git_read.assert_not_called()
        self.assertTrue(original_pr_head_admitted(x["active"], "a" * 40))

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

    def test_packet_preserves_full_diff_and_rejects_missing_patch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'queue.json').write_text(json.dumps(self.valid()))
            pr = {'head': {'sha': 'a' * 40, 'ref': 'original'}, 'state': 'open',
                  'base': {'sha': 'b' * 40}, 'draft': False}
            files = [{'filename': 'scripts/x.py', 'status': 'modified', 'patch': 'x' * 5000}]
            with patch('scripts.api_agent.endgame_progress_packet.ROOT', root), \
                 patch('scripts.api_agent.endgame_progress_packet.git', side_effect=[b'c' * 40, b'source']), \
                 patch('scripts.api_agent.endgame_progress_packet.subprocess.check_output',
                       side_effect=[json.dumps(pr).encode(), json.dumps(files).encode()]), \
                 patch.dict(os.environ, {'GITHUB_REPOSITORY': 'Donh91/Investering-Framework-Archive-v1'}):
                result = build(root / 'out', Path('queue.json'))
                self.assertEqual(result['original_pr']['files'][0]['patch'], 'x' * 5000)
            files[0]['patch'] = None
            with patch('scripts.api_agent.endgame_progress_packet.ROOT', root), \
                 patch('scripts.api_agent.endgame_progress_packet.git', side_effect=[b'c' * 40, b'source']), \
                 patch('scripts.api_agent.endgame_progress_packet.subprocess.check_output',
                       side_effect=[json.dumps(pr).encode(), json.dumps(files).encode()]), \
                 patch.dict(os.environ, {'GITHUB_REPOSITORY': 'Donh91/Investering-Framework-Archive-v1'}):
                with self.assertRaisesRegex(ValueError, 'PR_DIFF_INCOMPLETE'):
                    build(root / 'out2', Path('queue.json'))

    def test_exact_original_pr_added_file_is_admissible_not_unverified_main(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            work=self.valid()
            (root/"queue.json").write_text(json.dumps(work))
            pr={"head":{"sha":"a"*40,"ref":"original"},"base":{"sha":"b"*40},
                "state":"open","draft":False}
            changed=[{"filename":"scripts/cycle_navigator/prospective_range_bridge.py",
                      "status":"added","patch":"+real source"}]
            with patch("scripts.api_agent.endgame_progress_packet.ROOT",root), \
                 patch("scripts.api_agent.endgame_progress_packet.git",
                       side_effect=[b"c"*40,subprocess.CalledProcessError(1,"git"),b"real source"]), \
                 patch("scripts.api_agent.endgame_progress_packet.subprocess.check_output",
                       side_effect=[json.dumps(pr).encode(),json.dumps(changed).encode(),
                                    json.dumps(pr).encode(),json.dumps(changed).encode()]), \
                 patch.dict(os.environ,{"GITHUB_REPOSITORY":"Donh91/Investering-Framework-Archive-v1"}):
                out=build(root/"out",Path("queue.json"))
            self.assertEqual(out["evidence"][0]["source_ref"],"PINNED_PR_ADDED:"+"a"*40)

    def test_missing_main_source_cannot_be_forged_by_modified_pr_file(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/"queue.json").write_text(json.dumps(self.valid()))
            pr={"head":{"sha":"a"*40},"state":"open"}
            changes=[{"filename":"scripts/cycle_navigator/prospective_range_bridge.py",
                      "status":"modified","patch":"@@ changed"}]
            with patch("scripts.api_agent.endgame_progress_packet.ROOT",root), \
                 patch("scripts.api_agent.endgame_progress_packet.git",
                       side_effect=[b"c"*40,subprocess.CalledProcessError(1,"git")]), \
                 patch("scripts.api_agent.endgame_progress_packet.subprocess.check_output",
                       side_effect=[json.dumps(pr).encode(),json.dumps(changes).encode()]), \
                 patch.dict(os.environ,{"GITHUB_REPOSITORY":"Donh91/Investering-Framework-Archive-v1"}):
                with self.assertRaisesRegex(ValueError,"SOURCE_UNAVAILABLE"):
                    build(root/"blocked",Path("queue.json"))

    def test_oversized_source_fails_before_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'queue.json').write_text(json.dumps(self.valid()))
            with patch('scripts.api_agent.endgame_progress_packet.ROOT', root), \
                 patch('scripts.api_agent.endgame_progress_packet.git', side_effect=[b'c' * 40, b'x' * 100001]):
                with self.assertRaisesRegex(ValueError, 'SOURCE_TOO_LARGE'):
                    build(root / 'out', Path('queue.json'))
            self.assertFalse((root / 'out').exists())


if __name__=="__main__":
    unittest.main()

