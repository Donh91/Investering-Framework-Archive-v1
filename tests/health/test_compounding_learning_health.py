import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "health" / "build_compounding_learning_health.py"


class CompoundingLearningHealthTest(unittest.TestCase):
    def seed(self, root: Path, drift: bool = False) -> None:
        adjudication = {"contract": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1", "generated_at_utc": "2026-01-01T00:00:00Z"}
        base = root / "00_ARCHIVE_CONTROL/research_governance_v1/compounding_learning_v1"
        base.mkdir(parents=True)
        adj_dir = root / "research/experiment_lifecycle/weekly_adjudication"
        adj_dir.mkdir(parents=True)
        (adj_dir / "LATEST.json").write_text(json.dumps(adjudication))
        state = {
            "contract": "COMPOUNDING_LEARNING_CONTROLLER_STATE_v1",
            "authority": "RESEARCH_ONLY_NON_CANONICAL",
            "scientific_interpretation_owner": "UNIFIED_EXPERIMENTAL_LIFECYCLE_ADJUDICATION_v1",
            "controller_role": "NEXT_LEARNING_STRATEGY_ONLY",
            "adjudication_generated_at_utc": "old" if drift else adjudication["generated_at_utc"],
            "descriptive_checkpoint_days": [7,14,30,60,90,120,180,240],
            "learning_event_ids": [],
            "hypothesis_families": [],
            "canonical_effect": False,
            "portfolio_execution": False,
            "automatic_promotion": False,
            "automatic_canonical_write": False,
            "automatic_threshold_change": False,
            "automatic_weight_change": False,
            "automatic_market_rule_change": False,
            "model_weight_change": False,
            "retrospective_rescore_allowed": False,
            "frozen_parent_rewrite_allowed": False,
        }
        proposal = {
            "contract": "NEXT_BEST_EXPERIMENT_PROPOSAL_v1",
            "proposal_status": "NO_NEW_SCIENTIFICALLY_ELIGIBLE_CHILD_TEST",
            "canonical_effect": False,
            "portfolio_execution": False,
            "model_weight_change": False,
            "automatic_promotion": False,
        }
        backlog = {"contract": "LEARNING_BACKLOG_v1", "entry_count": 0, "entries": []}
        for name, value in (("STATE.json", state), ("NEXT_BEST_EXPERIMENT.json", proposal), ("LEARNING_BACKLOG.json", backlog)):
            (base / name).write_text(json.dumps(value))

    def run_health(self, root: Path):
        output = root / "health.json"
        process = subprocess.run([sys.executable, str(SCRIPT), "--repo-root", str(root), "--output", str(output)], capture_output=True, text=True)
        return process, json.loads(output.read_text())

    def test_passes_when_wiring_is_current(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.seed(root)
            process, output = self.run_health(root)
            self.assertEqual(process.returncode, 0)
            self.assertEqual(output["status"], "PASS")

    def test_fails_on_adjudication_drift(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); self.seed(root, drift=True)
            process, output = self.run_health(root)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn("COMPOUNDING_LEARNING_ADJUDICATION_DRIFT", output["blockers"])


if __name__ == "__main__":
    unittest.main()
