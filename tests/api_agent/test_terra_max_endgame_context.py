import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path("scripts/api_agent/terra_max_endgame_context.py")
spec = importlib.util.spec_from_file_location("terra_max_endgame_context", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TerraMaxEndgameContextTests(unittest.TestCase):
    def test_public_source_allowlist_and_reject_private_data(self):
        self.assertGreaterEqual(len(mod.PUBLIC_FILES), 12)
        for path in mod.PUBLIC_FILES:
            self.assertTrue(mod.approved_public_path(path), path)
        for path in (
            "Donh91/secrets/AGENTS.md",
            "secrets/API_KEY.txt",
            ".env",
            "data/../secrets/private.json",
            "vault/backup.json",
            "/etc/passwd",
        ):
            self.assertFalse(mod.approved_public_path(path), path)

    def test_no_second_api_attempt_or_source_write_in_context_builder(self):
        source = SCRIPT.read_text()
        self.assertNotIn("api.openai.com/v1/responses", source)
        self.assertNotIn("git push", source)
        self.assertNotIn("git reset --hard", source)
        self.assertNotIn("subprocess.check_call", source)
        self.assertIn("MAX_PACKET_BYTES", source)
        self.assertEqual(mod.MODEL, "gpt-6.1-terra")
        self.assertEqual(mod.REASONING, "max")

    def test_owner_branch_manual_dispatch_is_not_blocked_by_ui_mode(self):
        # GitHub mobile submitted 'live-smoke' but Actions twice executed
        # ordinary dry-run. This checks the mutually exclusive branch gates.
        workflow = Path(".github/workflows/api-agent-gateway-gate.yml").read_text()
        gate = workflow.split("  gateway-gate:", 1)[1].split("  terra-max-endgame-once:", 1)[0]
        max_job = workflow.split("  terra-max-endgame-once:", 1)[1]
        gate_condition = gate.split("    if: >-", 1)[1].split("    runs-on:", 1)[0]
        max_condition = max_job.split("    if: >-", 1)[1].split("    concurrency:", 1)[0]
        self.assertIn("github.event_name == 'workflow_dispatch'", max_condition)
        self.assertIn("github.actor == 'Donh91'", max_condition)
        self.assertIn("github.run_attempt == 1", max_condition)
        self.assertIn("refs/heads/chore/model-class-currency-20261027", max_condition)
        self.assertNotIn("inputs.mode", max_condition)
        self.assertNotIn("inputs.mode", gate_condition)
        self.assertIn("github.actor == 'Donh91'", gate_condition)
        self.assertIn("terra_max_endgame_claim.py", max_job)
        self.assertLess(max_job.index("terra_max_endgame_claim.py"), max_job.index("      - name: 'ONE API call"))
        self.assertIn("github.run_attempt == 1", max_condition)
        claim = Path("scripts/api_agent/terra_max_endgame_claim.py").read_text()
        self.assertIn("NO_PAID_RERUN", claim)
        self.assertIn("ONE_TIME_PAID_LIABILITY_ALREADY_CLAIMED", claim)

    def test_goal_based_stop_conditions_and_scientific_safety(self):
        prompt = mod.prompt_text()
        for required in (
            "SIX consecutive", "GitHub Pages", "Graph B", "Task 2",
            "source ancestry", "forecast_candidates MUST be []",
            "NO", "advisory", "CODE_CHANGE", "TEST", "ACCEPTANCE",
        ):
            self.assertIn(required.lower(), prompt.lower())

    def test_source_preview_bounded(self):
        text = "x" * 30000
        clipped = mod.clipped(text, 6200)
        self.assertLessEqual(len(clipped), 6400)
        self.assertIn("OMITTED_MIDDLE", clipped)
        self.assertEqual(mod.clipped("a", 6200), "a")

    def test_external_endpoints_explicit_allowlist(self):
        for url in mod.PUBLIC_URLS:
            self.assertIn("donh91.github.io", url)
        with self.assertRaises(ValueError):
            mod.fetch_public_json("https://example.com/api/private")

    def test_pr_ids_bounded_to_existing_owner_lanes(self):
        self.assertEqual(mod.PUBLIC_PR_NUMBERS, (1814, 1815, 1823))
        with self.assertRaises(ValueError):
            mod.fetch_public_pr(9999)


if __name__ == "__main__":
    unittest.main()
