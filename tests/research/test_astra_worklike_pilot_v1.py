import copy
import unittest
from scripts.research import astra_worklike_pilot_v1 as p

class TestWorklikePilot(unittest.TestCase):
    def setUp(self):
        self.pre = dict.fromkeys(p.PATHS)
        self.proposal = {"contract": "ASTRA_WORKLIKE_PROPOSAL_v1", "files": [
            {"path": path, "preimage_sha256": None, "content": "pass\n"} for path in p.PATHS]}

    def test_first_stage_deterministic_high_no_tools(self):
        a, quote = p.request_for_stage(1, "clock test", "synthetic fixture")
        self.assertEqual(a["model"], "gpt-6.2-astra")
        self.assertEqual(a["reasoning"], {"effort": "high"})
        self.assertNotIn("tools", a)
        self.assertNotIn("previous_response_id", a)
        self.assertEqual(quote["request_sha256"], p.sha(p.canonical(a)))
        self.assertFalse(quote["paid_authority"])
        self.assertEqual((a, quote), p.request_for_stage(1, "clock test", "synthetic fixture"))

    def test_verified_test_failure_only(self):
        prior = {"stage": 1, "status": "VERIFIED_TEST_FAILURE", "receipt_sha256": "a"*64, "test_log": "failed assertion"}
        p.request_for_stage(2, "repair", "fixture", prior)
        for status in ("PASS", "POST_UNKNOWN", "TIMEOUT", "MODEL_FAILED", "WAIT_REVIEW"):
            bad = dict(prior, status=status)
            with self.assertRaises(p.PilotBlocked):
                p.request_for_stage(2, "repair", "fixture", bad)

    def test_stage_limit_and_budget(self):
        self.assertLessEqual(p.MAX_STAGES*p.STAGE_CAP_MICROUSD, p.PILOT_CAP_MICROUSD)
        for stage in (0, 4, True, 1.0):
            with self.assertRaises(p.PilotBlocked):
                p.request_for_stage(stage, "task", "fixture")
        with self.assertRaises(p.PilotBlocked):
            p.request_for_stage(1, "task", "x"*p.MAX_REQUEST_BYTES)

    def test_structure_receipt_no_execution(self):
        result = p.validate_proposal(self.proposal, self.pre)
        self.assertEqual(result["status"], "STRUCTURE_ONLY_NO_EXECUTION")
        self.assertFalse(result["release_authority"])
        self.assertEqual(result["proposal_sha256"], p.sha(p.canonical(self.proposal)))

    def test_path_escape_and_protected_paths(self):
        for path in ("../x.py", "/tmp/x.py", ".github/workflows/x.yml", "AGENTS.md", "research/api_agent/x.py", p.PATHS[1]):
            bad = copy.deepcopy(self.proposal)
            bad["files"][0]["path"] = path
            with self.assertRaises(p.PilotBlocked):
                p.validate_proposal(bad, self.pre)

    def test_wrong_preimage(self):
        bad = copy.deepcopy(self.proposal)
        bad["files"][0]["preimage_sha256"] = "a"*64
        with self.assertRaises(p.PilotBlocked):
            p.validate_proposal(bad, self.pre)

    def test_malformed_and_oversize(self):
        for content in ("", "\x00", "x"*(p.MAX_FILE_BYTES+1), 1, "\ud800"):
            bad = copy.deepcopy(self.proposal)
            bad["files"][0]["content"] = content
            with self.assertRaises(p.PilotBlocked):
                p.validate_proposal(bad, self.pre)
        bad = copy.deepcopy(self.proposal)
        bad["files"][0]["unexpected"] = "write"
        with self.assertRaises(p.PilotBlocked):
            p.validate_proposal(bad, self.pre)

    def test_closes_previous_stage_not_replay(self):
        for prior in (None, {}, {"stage": 1, "status": "VERIFIED_TEST_FAILURE", "receipt_sha256": "a"*64, "test_log": "x"}):
            with self.assertRaises(p.PilotBlocked):
                p.request_for_stage(3, "task", "fixture", prior)
        with self.assertRaises(p.PilotBlocked):
            p.request_for_stage(1, "task", "fixture", {"stage": 0})


    def test_existing_launcher_narrow_high_preview(self):
        from scripts.research import owner_astra_mission_v1 as m
        from unittest import mock
        with mock.patch.object(m.core, "http_json", side_effect=AssertionError("NETWORK_FORBIDDEN")):
            req, data, meta = m.build_request(m.WORKLIKE_STAGE1)
        self.assertEqual(req["reasoning"], {"effort": "high"})
        self.assertEqual(req["model"], p.MODEL)
        self.assertEqual(meta["max_usd"], 1.5)
        self.assertEqual(req["max_output_tokens"], p.MAX_OUTPUT_TOKENS)
        self.assertEqual(meta["request_sha256"], p.sha(data))
        self.assertLessEqual(meta["worst_case_usd"], 1.5)
        self.assertNotIn("tools", req)
        self.assertEqual(m.mission_effort({"mission_id": "ASTRA-ORDINARY-TEST"}), "max")
        _, _, mission = m.load_mission(m.WORKLIKE_STAGE1)
        for mutation in ({"reasoning_effort": "max"}, {"model": "gpt-6.2-sol"},
                         {"max_usd": 2}, {"max_output_tokens": 128000}):
            with self.assertRaises(ValueError):
                m.mission_effort(dict(mission, **mutation))


    def test_native_workflow_isolation_contract(self):
        import json
        import yaml
        from pathlib import Path
        from scripts.research import astra_worklike_oracle_v1 as oracle
        root = Path(__file__).resolve().parents[2]
        wf = yaml.safe_load((root/".github/workflows/owner-astra-mission.yml").read_text())
        jobs = wf["jobs"]
        smoke, sandbox = jobs["worklike-smoke"], jobs["worklike-sandbox"]
        for job in (smoke, sandbox):
            self.assertEqual(job["permissions"], {"contents": "read"})
            dumped = json.dumps(job)
            for forbidden in ("secrets.", "OPENAI_API_KEY", "GITHUB_TOKEN", "workflow_dispatch"):
                self.assertNotIn(forbidden, dumped)
            self.assertIn(oracle.PINNED_IMAGE, dumped)
        self.assertEqual(smoke["if"], "github.event_name == 'pull_request'")
        self.assertEqual(sandbox["needs"], ["paid", "recover"])
        cond = sandbox["if"]
        for predicate in ("github.event_name == 'issue_comment'",
                          "github.event.issue.number == 1156",
                          "github.event.comment.user.login == 'Donh91'",
                          "github.ref == 'refs/heads/main'", "github.run_attempt == 1",
                          "needs.paid.result == 'success'", "needs.recover.result == 'success'",
                          "OWNER_LAUNCH_ASTRA_MISSION ASTRA-KOMPAS-L04-WORKLIKE-PILOT-S1-20261120 ",
                          "OWNER_COLLECT_ASTRA_MISSION ASTRA-KOMPAS-L04-WORKLIKE-PILOT-S1-20261120 "):
            self.assertIn(predicate, cond)
        self.assertIn("astra-mission-evidence-", json.dumps(sandbox))
        self.assertIn("astra-worklike-result-", json.dumps(sandbox))

if __name__ == "__main__":
    unittest.main()
