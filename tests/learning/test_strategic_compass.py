# CI audit trigger: validates current Strategic Compass runtime on main-equivalent code.
from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.learning.strategic_compass import alignment_class, materialize


def write(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value))


def fixture_repo(tmp_path: Path, *, month=True, cycle_direction="UP") -> Path:
    compass_rel = "04_MARKET_LEARNING/handlekompas/official/daily/2026/09/30/CMP-test.json"
    write(tmp_path / compass_rel, {
        "compass_id": "CMP-test",
        "market_reference": {"btc_usdt": 83000, "eth_usdt": 2660, "ethbtc": 0.032},
        "horizons": {
            "NEXT_12H": {"expected_direction": "DOWN", "expected_path": "retest", "action_posture": "HOLD"},
            "NEXT_1_3D": {"expected_direction": "DOWN", "expected_path": "retest", "action_posture": "HOLD"},
            "NEXT_5_7D": {"expected_direction": "SIDEWAYS", "expected_path": "absorption", "action_posture": "HOLD"},
        },
    })
    write(tmp_path / "04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json", {
        "compass_path": compass_rel,
        "compass_sha256": "official-sha",
    })
    projection = {
        "weeks_4_8": {
            "direction": cycle_direction, "summary": "structural bull", "state": "ROTATION",
            "action_posture": "HOLD", "warning": "NONE", "confidence": "MEDIUM",
        }
    }
    if month:
        projection["next_21_30d"] = {
            "direction": "UP", "summary": "recovery then expansion", "regime_destination": "EXPANSION",
            "expected_path": "retest -> absorption -> expansion", "action_posture": "HOLD",
            "falsification": ["breadth fails"], "confidence": "MEDIUM",
            "scenarios": [
                {"label": "BASE", "probability_pct": 55, "thesis": "expansion"},
                {"label": "BULL", "probability_pct": 20, "thesis": "fast expansion"},
                {"label": "BEAR", "probability_pct": 25, "thesis": "breakdown"},
            ],
        }
    cn_rel = "05_CYCLE_NAVIGATOR/weekly/2026/W40"
    write(tmp_path / cn_rel / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json", {
        "status": "READY", "issue_number": 28, "public_issue_number": 27,
        "decision_projection": projection,
    })
    write(tmp_path / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json", {
        "week_dir": cn_rel, "machine_package_sha256": "cn-sha", "iso_year": 2026, "iso_week": 40,
    })
    return tmp_path


class StrategicCompassTests(unittest.TestCase):
    def test_tactical_pullback_structural_bull_class(self):
        self.assertEqual(alignment_class(["DOWN", "DOWN", "SIDEWAYS", "UP", "UP"]), "TACTICAL_PULLBACK_STRUCTURAL_BULL")

    def test_materialize_preserves_horizon_disagreement(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td))
            result = materialize(repo, datetime(2026, 9, 30, 12, tzinfo=timezone.utc))
            self.assertEqual(result["status"], "CREATED")
            anchor = json.loads((repo / result["anchor_path"]).read_text())
            self.assertEqual(anchor["strategic_21_30d"]["direction"], "UP")
            self.assertEqual(anchor["cycle_4_8w"]["direction"], "UP")
            self.assertEqual(anchor["cross_horizon_alignment"]["class"], "TACTICAL_PULLBACK_STRUCTURAL_BULL")
            self.assertFalse(anchor["authority"]["portfolio_execution"])

    def test_missing_month_projection_fails_closed_without_stretching_2_3w(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td), month=False)
            result = materialize(repo, datetime(2026, 9, 30, 12, tzinfo=timezone.utc))
            anchor = json.loads((repo / result["anchor_path"]).read_text())
            self.assertEqual(anchor["strategic_21_30d"]["direction"], "UNAVAILABLE")
            self.assertFalse(anchor["strategic_21_30d"]["derived_from_2_3w"])
            self.assertEqual(anchor["strategic_21_30d"]["thesis_state"], "DATA_DEGRADED")

    def test_same_sources_are_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo = fixture_repo(Path(td))
            now = datetime(2026, 9, 30, 12, tzinfo=timezone.utc)
            first = materialize(repo, now)
            second = materialize(repo, now)
            self.assertEqual(first["status"], "CREATED")
            self.assertEqual(second["status"], "NOOP_SAME_SOURCES")


if __name__ == "__main__":
    unittest.main()
