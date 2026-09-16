from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "learning" / "build_calibration_population_census.py"
_spec = importlib.util.spec_from_file_location("build_calibration_population_census", SCRIPT)
_module = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_module)
build_census = _module.build_census


class CalibrationPopulationCensusTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def write_json(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, sort_keys=True) + "\n")
        return path

    def population(self, census: dict, population_id: str) -> dict:
        return next(row for row in census["populations"] if row["population_id"] == population_id)

    def test_missing_api_agent_roots_are_reported_not_inferred(self):
        census = build_census(self.root)
        api = self.population(census, "API_AGENT_RATIFIED_T13")
        self.assertFalse(api["forecast_root_exists"])
        self.assertFalse(api["outcome_root_exists"])
        self.assertEqual(api["forecast_file_count"], 0)
        self.assertEqual(api["outcome_file_count"], 0)
        self.assertEqual(census["status"], "PASS")
        self.assertEqual(census["decision_guardrail"], "DO_NOT_REPOINT_CALIBRATION_PATHS_FROM_THIS_CENSUS_ALONE")

    def test_framework_memory_counts_schema_and_ephemeral_evidence(self):
        self.write_json("research/framework_memory/forecast_memory/a.json", {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "A",
            "model": "m",
            "task": "t",
            "horizon_days": 3,
            "metric_path": "x",
            "prompt_sha256": "p",
        })
        self.write_json("research/framework_memory/forecast_memory/b.json", {
            "contract": "FROZEN_FORECAST_v1",
            "forecast_id": "B",
            "model": None,
            "task": None,
            "horizon_days": None,
            "metric_path": "y",
            "prompt_sha256": None,
        })
        self.write_json("research/framework_memory/outcome_memory/a.json", {
            "contract": "MATURED_OUTCOME_v3",
            "forecast_id": "A",
            "status": "MATURED",
            "result": "HIT",
            "scientific_score_eligible": True,
            "evidence_path": "/tmp/run/evidence/A.json",
        })
        durable = self.write_json("evidence/B.json", {"ok": True})
        self.write_json("research/framework_memory/outcome_memory/b.json", {
            "contract": "MATURED_OUTCOME_v3",
            "forecast_id": "B",
            "status": "MATURED",
            "result": "MISS",
            "scientific_score_eligible": False,
            "evidence_path": str(durable.relative_to(self.root)),
        })

        memory = self.population(build_census(self.root), "FRAMEWORK_MEMORY_BROAD")
        self.assertEqual(memory["forecast_file_count"], 2)
        self.assertEqual(memory["outcome_file_count"], 2)
        self.assertEqual(memory["scientific_score_eligible_count"], 1)
        self.assertEqual(memory["forecast_field_completeness"]["model"]["missing"], 1)
        self.assertEqual(memory["forecast_field_completeness"]["horizon_days"]["missing"], 1)
        self.assertEqual(memory["evidence_path_classes"]["ABSOLUTE_TMP_EPHEMERAL"], 1)
        self.assertEqual(memory["evidence_path_classes"]["REPO_RELATIVE_RESOLVABLE"], 1)

    def test_population_overlap_is_measured_without_merging(self):
        for base in (
            "research/api_agent/forecast_candidates/FROZEN",
            "research/framework_memory/forecast_memory",
        ):
            self.write_json(f"{base}/same.json", {
                "contract": "FROZEN_FORECAST_v1",
                "forecast_id": "SAME",
            })
        census = build_census(self.root)
        self.assertEqual(census["cross_population"]["forecast_id_overlap_count"], 1)
        self.assertEqual(census["next_required_decision"], "DEFINE_POPULATION_OWNERSHIP_AND_COHORT_SEMANTICS_BEFORE_CANONICAL_LEDGER_CHANGE")

    def test_malformed_json_is_visible_in_status(self):
        bad = self.root / "research/framework_memory/forecast_memory/bad.json"
        bad.parent.mkdir(parents=True, exist_ok=True)
        bad.write_text("{")
        census = build_census(self.root)
        memory = self.population(census, "FRAMEWORK_MEMORY_BROAD")
        self.assertEqual(census["status"], "WARN_PARSE_ERRORS")
        self.assertEqual(len(memory["parse_errors"]), 1)


if __name__ == "__main__":
    unittest.main()
