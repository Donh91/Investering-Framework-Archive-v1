from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.data_ping.zero_manual_feed_graduation import evaluate


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


class ZeroManualFeedGraduationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.state = Path("state/STATE.json")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def materialize(self, sha: str, *, manual_residual: float = 0.0, manual_required: bool = False) -> None:
        auto_path = Path(f"auto/{sha}.json")
        handle_path = Path(f"handle/{sha}.json")
        write_json(self.repo / auto_path, {"packet_sha256": sha, "manual_input_residual_pct": manual_residual})
        write_json(self.repo / "04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json", {"packet_path": auto_path.as_posix(), "packet_sha256": sha})
        write_json(self.repo / handle_path, {
            "source": {"packet_sha256": sha},
            "manual_market_data_required": manual_required,
            "authority": {"portfolio_execution": False, "market_threshold_change": False},
        })
        write_json(self.repo / "04_MARKET_LEARNING/handlekompas/LATEST.json", {"handlekompas_path": handle_path.as_posix(), "source_packet_sha256": sha})

    def run_cycle(self, sha: str, n: int) -> dict:
        self.materialize(sha)
        return evaluate(self.repo, self.state, upstream_event="workflow_run", upstream_conclusion="success", upstream_run_id=str(n))

    def test_three_distinct_natural_cycles_graduate(self) -> None:
        self.assertEqual(self.run_cycle("a" * 64, 1)["consecutive_valid_natural_cycles"], 1)
        self.assertEqual(self.run_cycle("b" * 64, 2)["consecutive_valid_natural_cycles"], 2)
        state = self.run_cycle("c" * 64, 3)
        self.assertEqual(state["consecutive_valid_natural_cycles"], 3)
        self.assertTrue(state["graduated"])

    def test_duplicate_source_does_not_advance(self) -> None:
        self.run_cycle("a" * 64, 1)
        state = self.run_cycle("a" * 64, 2)
        self.assertEqual(state["consecutive_valid_natural_cycles"], 1)
        self.assertEqual(state["last_cycle_status"], "DUPLICATE_SOURCE_NOT_COUNTED")

    def test_invalid_natural_cycle_resets_streak(self) -> None:
        self.run_cycle("a" * 64, 1)
        self.materialize("b" * 64, manual_residual=1.0)
        state = evaluate(self.repo, self.state, upstream_event="workflow_run", upstream_conclusion="success", upstream_run_id="2")
        self.assertEqual(state["consecutive_valid_natural_cycles"], 0)
        self.assertFalse(state["graduated"])

    def test_scheduled_handlekompas_is_ignored(self) -> None:
        self.materialize("a" * 64)
        state = evaluate(self.repo, self.state, upstream_event="schedule", upstream_conclusion="success", upstream_run_id="1")
        self.assertEqual(state["consecutive_valid_natural_cycles"], 0)
        self.assertEqual(state["last_cycle_status"], "IGNORED_NON_NATURAL_TRIGGER")


if __name__ == "__main__":
    unittest.main()
