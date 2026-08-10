import unittest

from scripts.daily_capture.classify_verification_scope import classify


class VerificationScopeTests(unittest.TestCase):
    def test_hourly_builder_routes_only_hourly_live_smoke(self):
        self.assertEqual(classify(["scripts/daily_capture/build_hourly_sequence.py"]), {"hourly_source": True, "farside_source": False})

    def test_hourly_workflow_routes_only_hourly_live_smoke(self):
        self.assertEqual(classify([".github/workflows/hourly-sequence-capture.yml"]), {"hourly_source": True, "farside_source": False})

    def test_farside_parser_routes_only_farside_live_smoke(self):
        self.assertEqual(classify(["scripts/data_terminal/farside_etf_owner.py"]), {"hourly_source": False, "farside_source": True})

    def test_farside_workflow_routes_only_farside_live_smoke(self):
        self.assertEqual(classify([".github/workflows/daily-settled-etf-calibration.yml"]), {"hourly_source": False, "farside_source": True})

    def test_gate_change_runs_both_live_smokes(self):
        self.assertEqual(classify([".github/workflows/daily-capture-architecture-gate.yml"]), {"hourly_source": True, "farside_source": True})

    def test_router_change_runs_both_live_smokes(self):
        self.assertEqual(classify(["scripts/daily_capture/classify_verification_scope.py"]), {"hourly_source": True, "farside_source": True})

    def test_master_monday_change_runs_no_market_source_smoke(self):
        self.assertEqual(classify(["scripts/master_monday/build_preflight_package_v3.py"]), {"hourly_source": False, "farside_source": False})

    def test_archived_capture_data_runs_no_market_source_smoke(self):
        self.assertEqual(classify(["03_DAILY_CAPTURE_LOGS/hourly/2026/08/10.csv"]), {"hourly_source": False, "farside_source": False})

    def test_mixed_source_change_runs_both(self):
        self.assertEqual(classify(["scripts/daily_capture/build_hourly_sequence.py", "scripts/data_terminal/farside_etf_owner.py"]), {"hourly_source": True, "farside_source": True})

    def test_dot_slash_normalization_preserves_github_path(self):
        self.assertEqual(classify(["./.github/workflows/hourly-sequence-capture.yml"]), {"hourly_source": True, "farside_source": False})


if __name__ == "__main__":
    unittest.main()
