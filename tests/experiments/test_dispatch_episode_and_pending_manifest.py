"""P0 (Archive #2152): one dispatch request per fire EPISODE, and a LATEST manifest of pending requests only.

Base behaviour (before the fix) re-dispatched a persistent sensor condition at every observation
(~4 per candidate per day: 63,219 requests for 319 candidates) and listed the whole history in
LATEST_EXPERIMENT_DISPATCH_MANIFEST.json (26.3 MB > the 25 MiB storage-health hard limit).
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "experiments" / "experiment_lifecycle_scientific_admission.py"
ROOT = "research/experiment_lifecycle"


def context(captured, advancers):
    return {
        "latest_capture": {"captured_at_utc": captured, "run_id": "run-" + captured,
                           "market_metrics": {"spot": {"BTCUSDT": {"close": 64000.0}, "ETHBTC": {"close": 0.0302}},
                                              "breadth": {"advancers": advancers}}},
        "previous_capture": {"captured_at_utc": "2026-08-23T00:00:00Z",
                             "market_metrics": {"spot": {"BTCUSDT": {"close": 63000.0}, "ETHBTC": {"close": 0.0298}},
                                                "breadth": {"advancers": 52}}},
        "metric_deltas": [],
    }


PAIR = {
    "kind": "SENSOR_COMBINATION", "title": "Episode pair",
    "hypothesis": "The pair may add forward information beyond either component alone.",
    "falsifier": "It fails to beat the strongest single component on prospective independent windows.",
    "horizon_days": 7,
    "components": [{"metric_path": "breadth.advancers", "operator": "GT", "threshold": 55},
                   {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.03}],
    "target_metric_path": "spot.BTCUSDT.close", "target_direction": "UP", "target_threshold_pct": 1.0,
    "target_unit_contract_version": "FORECAST_TARGET_UNITS_v2", "regime_dependency": "ROTATION_WATCH",
    "novelty_reason": "EPISODE_TEST", "revisit_conditions": [], "evidence_basis": [],
}


def run(repo: Path, captured: str, advancers: int) -> dict:
    daily = repo / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    (daily / "output.json").write_text(json.dumps({"forecast_candidates": [], "experiment_candidates": [PAIR]}))
    (daily / "context.json").write_text(json.dumps(context(captured, advancers)))
    (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(repo),
           "--daily-output", str(daily / "output.json"), "--daily-context", str(daily / "context.json"),
           "--daily-receipt", str(daily / "receipt.json"),
           "--candidate-root", str(repo / f"{ROOT}/candidates"), "--observation-root", str(repo / f"{ROOT}/observations"),
           "--dispatch-root", str(repo / f"{ROOT}/dispatch"), "--forecast-root", str(repo / "research/framework_memory/forecast_memory"),
           "--outcome-root", str(repo / "research/framework_memory/outcome_memory"), "--receipt-root", str(repo / f"{ROOT}/receipts"),
           "--registry-output", str(repo / f"{ROOT}/LATEST_EXPERIMENT_REGISTRY.json"),
           "--manifest-output", str(repo / f"{ROOT}/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"),
           "--admission-root", str(repo / f"{ROOT}/admission"),
           "--admission-registry-output", str(repo / f"{ROOT}/LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json")]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def requests(repo: Path) -> list[dict]:
    return [json.loads(p.read_text()) for p in sorted((repo / f"{ROOT}/dispatch").rglob("*.json"))]


def manifest(repo: Path) -> dict:
    return json.loads((repo / f"{ROOT}/LATEST_EXPERIMENT_DISPATCH_MANIFEST.json").read_text())


class DispatchEpisodeTest(unittest.TestCase):
    def test_persistent_fire_is_one_episode_not_one_request_per_observation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            for i, captured in enumerate(["2026-08-23T04:00:00Z", "2026-08-23T10:00:00Z",
                                          "2026-08-23T16:00:00Z", "2026-08-23T22:00:00Z"]):
                summary = run(repo, captured, advancers=60)  # condition stays true
                self.assertEqual(summary["episode_continuations_not_dispatched"], 0 if i == 0 else 1)
            self.assertEqual(len(requests(repo)), 1)  # base: 4
            self.assertEqual(len(list((repo / f"{ROOT}/observations").rglob("*.json"))), 4)  # evidence kept

    def test_missing_data_does_not_rearm_an_unresolved_fire_episode(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, "2026-08-23T04:00:00Z", advancers=60)  # definitively FIRED
            run(repo, "2026-08-23T10:00:00Z", advancers=None)  # UNKNOWN, not NOT_FIRED
            summary = run(repo, "2026-08-23T16:00:00Z", advancers=60)  # still same episode
            self.assertEqual(summary["episode_continuations_not_dispatched"], 1)
            self.assertEqual(len(requests(repo)), 1)
            observed = sorted((repo / f"{ROOT}/observations").rglob("*.json"))
            self.assertEqual(len(observed), 3)  # all immutable observations retained
            statuses = [json.loads(path.read_text())["evaluation_status"] for path in observed]
            self.assertCountEqual(statuses, ["FIRED", "WAITING_FOR_DATA", "FIRED"])

    def test_unknown_chain_then_observed_false_rearms_exactly_once(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, "2026-08-23T04:00:00Z", advancers=60)
            run(repo, "2026-08-23T08:00:00Z", advancers=None)
            run(repo, "2026-08-23T12:00:00Z", advancers=None)
            run(repo, "2026-08-23T16:00:00Z", advancers=50)  # genuine NOT_FIRED
            run(repo, "2026-08-23T20:00:00Z", advancers=None)
            run(repo, "2026-08-23T22:00:00Z", advancers=60)
            self.assertEqual(len(requests(repo)), 2)
            self.assertEqual(len(list((repo / f"{ROOT}/observations").rglob("*.json"))), 6)

    def test_fire_stop_fire_starts_a_new_episode(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, "2026-08-23T04:00:00Z", advancers=60)
            run(repo, "2026-08-23T10:00:00Z", advancers=60)
            run(repo, "2026-08-23T16:00:00Z", advancers=50)  # not fired
            run(repo, "2026-08-23T22:00:00Z", advancers=60)  # fires again: new episode
            types = [r["request_type"] for r in requests(repo)]
            self.assertEqual(len(types), 2)
            self.assertTrue(all(t == "SENSOR_FIRE_REPLICATION" for t in types))

    def test_latest_manifest_lists_only_unreceipted_qualified_requests(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, "2026-08-23T04:00:00Z", advancers=60)
            m = manifest(repo)
            self.assertEqual(m["contract"], "EXPERIMENT_DISPATCH_MANIFEST_v2_SCIENTIFIC_ADMISSION")  # consumer contract unchanged
            self.assertEqual((m["request_count"], m["total_qualified_request_count"], m["receipted_request_count"]), (1, 1, 0))
            row = m["requests"][0]
            self.assertTrue(row["raw_url"].endswith(row["path"]))  # raw_url kept for the consumer
            receipt = {"contract": "EXPERIMENT_EXECUTION_RECEIPT_v1", "receipt_id": "XR-test", "request_id": row["request_id"],
                       "candidate_id": row["candidate_id"], "replication_status": "REPLICATED_FIRED"}
            (repo / f"{ROOT}/receipts").mkdir(parents=True, exist_ok=True)
            (repo / f"{ROOT}/receipts/XR-test.json").write_text(json.dumps(receipt))
            run(repo, "2026-08-23T10:00:00Z", advancers=60)  # continuation: no new request
            m = manifest(repo)
            self.assertEqual((m["request_count"], m["total_qualified_request_count"], m["receipted_request_count"]), (0, 1, 1))
            self.assertEqual(m["listing_rule"], "PENDING_UNRECEIPTED_QUALIFIED_ONLY")
            self.assertEqual(len(requests(repo)), 1)  # history file untouched


if __name__ == "__main__":
    unittest.main()
