from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

MODULE_PATH = Path(__file__).parents[2] / "scripts" / "health" / "build_operations_dashboard.py"
spec = importlib.util.spec_from_file_location("operations_dashboard", MODULE_PATH)
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)

UTC = timezone.utc


class OperationsDashboardTests(unittest.TestCase):
    def write_json(self, root: Path, rel: str, data: dict) -> Path:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def pointer(self, root: Path, rel: str) -> dict:
        path = root / rel
        return {"path": rel, "sha256": module.sha256_path(path)}

    def base_repo(self, root: Path, reference: datetime) -> None:
        capture = self.write_json(root, "captures/capture.json", {"captured_at_utc": "2026-08-04T12:00:00Z", "status": "PASS"})
        director = self.write_json(root, "director/output.json", {"completed_at_utc": "2026-08-04T12:10:00Z", "status": "PASS"})
        weekly = self.write_json(root, "weekly/output.json", {"completed_at_utc": "2026-08-03T08:00:00Z", "status": "PASS"})
        self.write_json(root, "LATEST_HANDOFF.json", {
            "contract": "LATEST_HANDOFF_v1",
            "generated_at_utc": "2026-08-04T12:15:00Z",
            "open_incidents": [],
            "pending_forecast_candidates": [],
            "pointers": {
                "latest_capture": {"path": str(capture.relative_to(root)), "sha256": module.sha256_path(capture)},
                "latest_director_output": {"path": str(director.relative_to(root)), "sha256": module.sha256_path(director)},
                "latest_weekly_output": {"path": str(weekly.relative_to(root)), "sha256": module.sha256_path(weekly)},
            },
        })
        self.write_json(root, "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", {"status": "GREEN", "generated_at_utc": "2026-08-04T12:20:00Z", "red_count": 0, "amber_count": 0, "blockers": []})
        self.write_json(root, "research/architecture_health/LATEST_ARCHITECTURE_HEALTH.json", {"status": "GREEN", "generated_at_utc": "2026-08-04T12:20:00Z", "blockers": []})

    def test_green_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = datetime(2026, 8, 4, 13, 0, tzinfo=UTC)
            self.base_repo(root, reference)
            dashboard = module.build_dashboard(root, reference)
            self.assertEqual(dashboard["overall_status"], "GREEN")
            self.assertEqual(dashboard["systems"]["daily_capture"]["status"], "GREEN")
            self.assertEqual(dashboard["required_actions"], [])

    def test_skipped_no_delta_is_not_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = datetime(2026, 8, 4, 13, 0, tzinfo=UTC)
            self.base_repo(root, reference)
            director_path = root / "director/output.json"
            director_path.write_text(json.dumps({"completed_at_utc": "2026-08-04T12:10:00Z", "status": "SKIPPED_NO_DELTA"}) + "\n")
            handoff = json.loads((root / "LATEST_HANDOFF.json").read_text())
            handoff["pointers"]["latest_director_output"]["sha256"] = module.sha256_path(director_path)
            (root / "LATEST_HANDOFF.json").write_text(json.dumps(handoff) + "\n")
            dashboard = module.build_dashboard(root, reference)
            self.assertEqual(dashboard["systems"]["openai_daily_director"]["status"], "GREEN")
            self.assertEqual(dashboard["systems"]["openai_daily_director"]["reason"], "EXPECTED_SKIP_NO_COMPARABLE_DELTA")

    def test_hash_mismatch_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = datetime(2026, 8, 4, 13, 0, tzinfo=UTC)
            self.base_repo(root, reference)
            handoff = json.loads((root / "LATEST_HANDOFF.json").read_text())
            handoff["pointers"]["latest_capture"]["sha256"] = "0" * 64
            (root / "LATEST_HANDOFF.json").write_text(json.dumps(handoff) + "\n")
            dashboard = module.build_dashboard(root, reference)
            self.assertEqual(dashboard["systems"]["daily_capture"]["status"], "RED")
            self.assertEqual(dashboard["overall_status"], "RED")

    def test_stale_capture_is_red(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = datetime(2026, 8, 5, 13, 0, tzinfo=UTC)
            self.base_repo(root, reference)
            dashboard = module.build_dashboard(root, reference)
            self.assertEqual(dashboard["systems"]["daily_capture"]["status"], "RED")

    def test_automation_red_propagates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reference = datetime(2026, 8, 4, 13, 0, tzinfo=UTC)
            self.base_repo(root, reference)
            self.write_json(root, "research/architecture_health/LATEST_AUTOMATION_HEALTH.json", {"status": "RED", "generated_at_utc": "2026-08-04T12:20:00Z", "red_count": 2, "amber_count": 0, "blockers": ["workflow-x:LATEST_RUN_FAILED"]})
            dashboard = module.build_dashboard(root, reference)
            self.assertEqual(dashboard["systems"]["automation_health"]["status"], "RED")
            self.assertEqual(dashboard["overall_status"], "RED")

    def test_missing_inputs_never_false_green(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dashboard = module.build_dashboard(root, datetime(2026, 8, 4, 13, 0, tzinfo=UTC))
            self.assertNotEqual(dashboard["overall_status"], "GREEN")
            self.assertTrue(dashboard["required_actions"])


if __name__ == "__main__":
    unittest.main()
