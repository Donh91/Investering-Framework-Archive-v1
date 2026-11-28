"""R0: with no preregistered decision rule, eligible evidence stays INCONCLUSIVE.

Real-code tests of ``experiment_lifecycle.registry``. Score eligibility uses the
existing synthetic accepted-main seam (``AcceptedMainSource.matches``), which
never claims a real trusted clock exists. Everything else runs the production
binding, settlement and state-selection code.
"""
import hashlib
import importlib.util
import itertools
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.experiments.experiment_lifecycle import registry

# Load the sibling fixture module by path: works under both unittest discover
# and repository-root pytest collection, and does not re-collect its TestCases.
_spec = importlib.util.spec_from_file_location(
    "_r0_lifecycle_fixture", Path(__file__).with_name("test_experiment_lifecycle.py"))
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

NO_RULE = "NO_PREREGISTERED_DECISION_RULE"
ANCHOR = "scripts.experiments.source_git_anchor.AcceptedMainSource.matches"


def tree_digest(root: Path) -> dict:
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file() and ".git" not in p.parts}


class NoPreregisteredRuleTests(unittest.TestCase):
    sample_registry = _base.CensoredOutcomeIntegrityTests.sample_registry
    outcome = staticmethod(_base.CensoredOutcomeIntegrityTests.outcome)

    def eligible_registry(self, root: Path, results):
        records = [self.outcome(f"EXP-FC-{i}", result=r) for i, r in enumerate(results)]
        with patch(ANCHOR, return_value=True):
            return self.sample_registry(root, records)

    def rerun(self, root: Path, now="2026-10-18T01:00:00Z"):
        with patch(ANCHOR, return_value=True):
            return registry(root / "candidates", root / "observations", root / "forecasts",
                            root / "outcomes", root / "receipts", now)

    def assert_inconclusive(self, reg, results):
        row = reg["candidates"][0]
        self.assertEqual(row["state"], "MATURED_INCONCLUSIVE")
        self.assertEqual(row["matured_state_reason_v1"], NO_RULE)
        self.assertEqual(row["matured_outcome_count"], len(results))
        self.assertEqual(row["scientific_score_eligible_outcome_count"], len(results))
        self.assertEqual(row["scientific_score_nonadmission_counts_v1"], {})
        self.assertEqual(row["outcome_record_count"], len(results))
        self.assertEqual(row["censored_outcome_count"], 0)
        self.assertEqual(row["unknown_outcome_count"], 0)
        self.assertEqual(reg["state_counts"], {"MATURED_INCONCLUSIVE": 1})
        self.assertNotIn("MATURED_SUPPORTED", reg["state_counts"])
        self.assertNotIn("MATURED_NOT_SUPPORTED", reg["state_counts"])
        self.assertEqual(reg["rules"]["matured_decision_rule"],
                         "NONE_PREREGISTERED_ELIGIBLE_EVIDENCE_STAYS_INCONCLUSIVE")

    def test_single_hit_is_inconclusive_with_reason(self):
        with tempfile.TemporaryDirectory() as td:
            self.assert_inconclusive(self.eligible_registry(Path(td), ["HIT"]), ["HIT"])

    def test_single_miss_is_inconclusive_with_reason(self):
        with tempfile.TemporaryDirectory() as td:
            self.assert_inconclusive(self.eligible_registry(Path(td), ["MISS"]), ["MISS"])

    def test_99_miss_plus_1_hit_is_inconclusive(self):
        results = ["MISS"] * 99 + ["HIT"]
        with tempfile.TemporaryDirectory() as td:
            self.assert_inconclusive(self.eligible_registry(Path(td), results), results)

    def test_extremes_all_hit_and_all_miss_100(self):
        for value in ("HIT", "MISS"):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as td:
                results = [value] * 100
                self.assert_inconclusive(self.eligible_registry(Path(td), results), results)

    def test_exhaustive_hit_miss_sequences_length_1_to_6(self):
        seen = 0
        for n in range(1, 7):
            for seq in itertools.product(("HIT", "MISS"), repeat=n):
                with self.subTest(seq=seq), tempfile.TemporaryDirectory() as td:
                    self.assert_inconclusive(self.eligible_registry(Path(td), seq), seq)
                seen += 1
        self.assertEqual(seen, 126)

    def test_matured_without_eligibility_has_no_rule_reason(self):
        # Unchanged path: matured but not eligible was already INCONCLUSIVE.
        with tempfile.TemporaryDirectory() as td:
            row = self.sample_registry(Path(td), [self.outcome("EXP-FC-1")])["candidates"][0]
            self.assertEqual(row["state"], "MATURED_INCONCLUSIVE")
            self.assertEqual(row["scientific_score_eligible_outcome_count"], 0)
            self.assertIsNone(row["matured_state_reason_v1"])

    def test_target_unit_quarantine_still_wins(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.eligible_registry(root, ["HIT"])
            cand = root / "candidates/test.json"
            value = json.loads(cand.read_text())
            value["spec"] = {"kind": "FORECAST_TEST", "title": "Legacy unit forecast",
                             "target_unit_contract_version": None}
            cand.write_text(json.dumps(value))
            reg = self.rerun(root)
            row = reg["candidates"][0]
            self.assertEqual(row["state"], "TARGET_UNIT_QUARANTINED")
            self.assertIsNone(row["matured_state_reason_v1"])
            self.assertEqual(row["scientific_score_eligible_outcome_count"], 1)
            self.assertEqual(row["matured_outcome_count"], 1)
            self.assertEqual(reg["state_counts"], {"TARGET_UNIT_QUARANTINED": 1})

    def test_input_rows_and_outcome_bytes_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.eligible_registry(root, ["MISS", "HIT", "MISS"])
            before = tree_digest(root)
            first = self.rerun(root)
            second = self.rerun(root)
            self.assertEqual(tree_digest(root), before)
            self.assertEqual(first["candidates"], second["candidates"])
            self.assert_inconclusive(first, ["MISS", "HIT", "MISS"])


class NonMatureStatesUnchangedTests(unittest.TestCase):
    """Seven non-mature controls, built directly on the real registry()."""

    def build(self, root: Path, cases: dict) -> dict:
        names = ("candidates", "observations", "forecasts", "outcomes", "receipts")
        dirs = {n: root / n for n in names}
        for d in dirs.values():
            d.mkdir(parents=True, exist_ok=True)
        for cid, case in cases.items():
            (dirs["candidates"] / f"{cid}.json").write_text(json.dumps({
                "contract": "EXPERIMENT_CANDIDATE_v1", "candidate_id": cid,
                "created_at_utc": "2026-09-01T00:00:00Z",
                "spec": {"kind": "SENSOR_COMBINATION", "title": f"control {cid}"}}))
            for j, status in enumerate(case.get("observations", [])):
                (dirs["observations"] / f"{cid}-{j}.json").write_text(json.dumps({
                    "contract": "EXPERIMENT_OBSERVATION_v1", "candidate_id": cid,
                    "observed_at_utc": f"2026-09-0{j + 1}T00:00:00Z",
                    "evaluation_status": status}))
            if case.get("forecast"):
                fid = f"FC-{cid}"
                (dirs["forecasts"] / f"{fid}.json").write_text(json.dumps({
                    "contract": "FROZEN_FORECAST_v1", "source_candidate_id": cid,
                    "forecast_id": fid}))
                if case.get("outcome"):
                    (dirs["outcomes"] / f"{fid}.json").write_text(json.dumps({
                        "contract": "MATURED_OUTCOME_v3", "forecast_id": fid,
                        **case["outcome"]}))
        before = tree_digest(root)
        reg = registry(*(dirs[n] for n in names), "2026-10-18T00:00:00Z")
        self.assertEqual(tree_digest(root), before)
        return reg

    def test_non_mature_states_are_unchanged(self):
        cases = {
            "C-proposed": ({}, "PROPOSED"),
            "C-incubating": ({"observations": ["EVALUATED"]}, "INCUBATING"),
            "C-mapping": ({"observations": ["WAITING_FOR_MAPPING"]}, "WAITING_FOR_MAPPING"),
            "C-data-obs": ({"observations": ["WAITING_FOR_DATA"]}, "WAITING_FOR_DATA"),
            "C-fired": ({"observations": ["FIRED_NO_TARGET"]}, "FIRED_NO_TARGET"),
            "C-maturity": ({"forecast": True}, "WAITING_FOR_MATURITY"),
            "C-censored": ({"forecast": True, "outcome": {
                "status": "CENSORED", "result": None,
                "scientific_score_eligible": False}}, "WAITING_FOR_DATA"),
        }
        with tempfile.TemporaryDirectory() as td:
            reg = self.build(Path(td), {k: v[0] for k, v in cases.items()})
        rows = {row["candidate_id"]: row for row in reg["candidates"]}
        self.assertEqual(len(rows), 7)
        for cid, (_, expected) in cases.items():
            with self.subTest(candidate=cid):
                self.assertEqual(rows[cid]["state"], expected)
                self.assertIsNone(rows[cid]["matured_state_reason_v1"])
                self.assertEqual(rows[cid]["matured_outcome_count"], 0)
                self.assertEqual(rows[cid]["scientific_score_eligible_outcome_count"], 0)


if __name__ == "__main__":
    unittest.main()
