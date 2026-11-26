"""Forecast-slot allocation must be fair, outcome-blind, deterministic and replay-idempotent.

Native run 44628588447 (2026-11-19) had 334 FIRED qualified candidates and a cap of 5 new
forecasts; the five lowest candidate IDs took every slot because allocation was ordered by
(kind, candidate_id) only. A perpetually firing candidate with a higher ID could never be served.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).parents[2]
SCRIPT = REPO / "scripts" / "experiments" / "experiment_lifecycle_scientific_admission.py"
if str(SCRIPT.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPT.parent))
import experiment_lifecycle_scientific_admission as module  # noqa: E402

FORECAST_ROOT = "research/framework_memory/forecast_memory"


def pair(index, fires=True):
    return {
        "kind": "SENSOR_COMBINATION", "title": f"Fair allocation pair {index}",
        "hypothesis": "The pair may add forward information beyond either component alone.",
        "falsifier": "It fails to beat the strongest single component on prospective independent windows.",
        "horizon_days": 7,
        "components": [
            {"metric_path": "breadth.advancers", "operator": "GT" if fires else "LT", "threshold": 55},
            {"metric_path": "spot.ETHBTC.close", "operator": "GT", "threshold": 0.03},
        ],
        "target_metric_path": "spot.BTCUSDT.close", "target_direction": "UP",
        "target_threshold_pct": round(1.0 + index / 10, 2),
        "target_unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        "regime_dependency": "ROTATION_WATCH", "novelty_reason": "FAIR_ALLOCATION_TEST",
        "revisit_conditions": [], "evidence_basis": [],
    }


def director_forecast():
    return {"metric_path": "spot.BTCUSDT.close", "direction": "UP", "target_mode": "PCT_MOVE", "threshold_pct": 3.0,
            "target_value": None, "range_low": None, "range_high": None, "horizon_days": 5, "rationale": "priority"}


def ctx(captured):
    metrics = {"spot": {"BTCUSDT": {"close": 64000.0}, "ETHBTC": {"close": 0.0302}}, "breadth": {"advancers": 60}}
    return {"latest_capture": {"captured_at_utc": captured, "run_id": "fair-allocation-run", "market_metrics": metrics},
            "previous_capture": {"captured_at_utc": "2026-08-01T00:00:00Z", "market_metrics": metrics}, "metric_deltas": []}


def run(repo: Path, output: dict, captured: str, cap: int = 5) -> dict:
    daily = repo / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    (daily / "output.json").write_text(json.dumps(output))
    (daily / "context.json").write_text(json.dumps(ctx(captured)))
    (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
    el = repo / "research/experiment_lifecycle"
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(repo),
           "--daily-output", str(daily / "output.json"), "--daily-context", str(daily / "context.json"), "--daily-receipt", str(daily / "receipt.json"),
           "--candidate-root", str(el / "candidates"), "--observation-root", str(el / "observations"), "--dispatch-root", str(el / "dispatch"),
           "--forecast-root", str(repo / FORECAST_ROOT), "--outcome-root", str(repo / "research/framework_memory/outcome_memory"),
           "--receipt-root", str(el / "receipts"), "--registry-output", str(el / "LATEST_EXPERIMENT_REGISTRY.json"),
           "--manifest-output", str(el / "LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"), "--admission-root", str(el / "admission"),
           "--admission-registry-output", str(el / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"), "--max-new-forecasts", str(cap)]
    return json.loads(subprocess.run(cmd, check=True, capture_output=True, text=True).stdout)


def forecasts(repo: Path) -> list[dict]:
    root = repo / FORECAST_ROOT
    return [json.loads(p.read_text()) for p in sorted(root.rglob("*.json"))] if root.exists() else []


def served(repo: Path) -> Counter:
    return Counter(row["source_candidate_id"] for row in forecasts(repo))


def tick(i: int) -> str:
    return f"2026-08-{2 + i:02d}T20:00:00Z"


class FairForecastAllocationEndToEnd(unittest.TestCase):
    def test_perpetually_eligible_candidates_all_receive_slots_and_spread_is_bounded(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}
            for i in range(10):
                summary = run(repo, output, tick(i))
                self.assertEqual(summary["new_forecasts"], 5)  # cap is respected and fully used every tick
            counts = served(repo)
            self.assertEqual(sum(counts.values()), 50)
            self.assertEqual(len(counts), 8, counts)  # nobody starves (fixed ID order gives 5 of 8)
            self.assertLessEqual(max(counts.values()) - min(counts.values()), 1, counts)

    def test_same_capture_replay_is_idempotent_and_does_not_spill_to_next_candidates(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}
            run(repo, output, tick(0))
            first = sorted(p.name for p in (repo / FORECAST_ROOT).rglob("*.json"))
            replay = run(repo, output, tick(0))
            self.assertEqual(replay["new_forecasts"], 0)
            self.assertEqual(sorted(p.name for p in (repo / FORECAST_ROOT).rglob("*.json")), first)

    def test_forecast_test_kind_priority_is_preserved_even_after_being_served(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [director_forecast()], "experiment_candidates": [pair(i) for i in range(8)]}
            for i in range(3):
                run(repo, output, tick(i))
            director = [row for row in forecasts(repo) if row["metric_path"].endswith("BTCUSDT.close") and row["threshold_pct"] == 3.0]
            self.assertEqual(len(director), 3)  # served every tick despite being most recently served

    def test_negative_control_non_firing_candidates_never_take_slots(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [], "experiment_candidates": [pair(i, fires=(i % 2 == 0)) for i in range(8)]}
            for i in range(3):
                run(repo, output, tick(i), cap=2)
            counts = served(repo)
            self.assertEqual(sum(counts.values()), 6)
            self.assertEqual(len(counts), 4)  # only the four firing candidates; rotation covers them all
            self.assertTrue(all(1 <= v <= 2 for v in counts.values()), counts)

    def test_positive_control_capacity_above_demand_serves_everyone_every_tick(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(4)]}
            for i in range(3):
                run(repo, output, tick(i), cap=10)
            self.assertEqual(sorted(served(repo).values()), [3, 3, 3, 3])

    def test_allocation_is_independent_of_outcome_records(self):
        output = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}
        allocations = []
        for poison in (False, True):
            with tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                run(repo, output, tick(0))
                if poison:  # every first-tick forecast "missed"; a score-aware allocator would react
                    for row in forecasts(repo):
                        path = repo / "research/framework_memory/outcome_memory" / f"{row['forecast_id']}.json"
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text(json.dumps({"contract": "FORECAST_OUTCOME_v1", "forecast_id": row["forecast_id"],
                                                    "status": "MATURED", "result": "MISS", "score_eligible": True}))
                run(repo, output, tick(1))
                allocations.append(sorted((r["frozen_at_utc"], r["source_candidate_id"]) for r in forecasts(repo)))
        self.assertEqual(allocations[0], allocations[1])


def row(cid, kind="SENSOR_COMBINATION"):
    return (Path(f"{cid}.json"), {"candidate_id": cid, "spec": {"kind": kind}})


class FairForecastAllocationOrderUnit(unittest.TestCase):
    def test_order_is_kind_then_fewest_recent_slots_then_least_recently_served_then_id(self):
        rows = [row("EC-c"), row("EC-a"), row("EC-b"), row("EC-d"), row("EC-z", "FORECAST_TEST")]
        hist = {"EC-a": (1, "2026-08-03T00:00:00Z"), "EC-b": (1, "2026-08-02T00:00:00Z"), "EC-d": (2, "2026-08-01T00:00:00Z"),
                "EC-z": (9, "2026-08-03T00:00:00Z")}
        ordered = [r[1]["candidate_id"] for r in sorted(rows, key=lambda r: module.forecast_allocation_key(r[1], hist))]
        self.assertEqual(ordered, ["EC-z", "EC-c", "EC-b", "EC-a", "EC-d"])

    def test_order_does_not_depend_on_input_order(self):
        rows = [row(f"EC-{i:02d}") for i in range(20)]
        last = {f"EC-{i:02d}": (i % 3, f"2026-08-{1 + i % 5:02d}T00:00:00Z") for i in range(0, 20, 3)}
        a = sorted(rows, key=lambda r: module.forecast_allocation_key(r[1], last))
        b = sorted(list(reversed(rows)), key=lambda r: module.forecast_allocation_key(r[1], last))
        self.assertEqual(a, b)

    def test_service_history_ignores_current_and_future_windows_and_other_contracts(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            docs = [
                {"contract": "FROZEN_FORECAST_v1", "forecast_id": "f1", "source_candidate_id": "EC-a", "frozen_at_utc": "2026-08-02T20:00:00Z"},
                {"contract": "FROZEN_FORECAST_v1", "forecast_id": "f2", "source_candidate_id": "EC-a", "frozen_at_utc": "2026-08-03T20:00:00Z"},
                {"contract": "FROZEN_FORECAST_v1", "forecast_id": "f3", "source_candidate_id": "EC-b", "frozen_at_utc": "2026-08-01T20:00:00.000+00:00"},
                {"contract": "FROZEN_FORECAST_v1", "forecast_id": "f4", "frozen_at_utc": "2026-08-01T20:00:00Z"},
                {"contract": "FORECAST_OUTCOME_v1", "forecast_id": "f5", "source_candidate_id": "EC-c", "frozen_at_utc": "2026-08-01T20:00:00Z"},
            ]
            for doc in docs:
                (root / f"{doc['forecast_id']}.json").write_text(json.dumps(doc))
            history = module.forecast_service_history(root, "2026-08-03T20:00:00Z")
            self.assertEqual(set(history), {"EC-a", "EC-b"})
            self.assertEqual(history["EC-a"][0], 1)
            self.assertTrue(history["EC-a"][1].startswith("2026-08-02T20:00:00"))
            # lookback: slots older than the window no longer count, so long-served candidates re-enter rotation
            self.assertEqual(set(module.forecast_service_history(root, "2026-08-03T20:00:00Z", lookback_days=1)), {"EC-a"})
            self.assertEqual(module.forecast_service_history(root / "missing", "2026-08-03T20:00:00Z"), {})


if __name__ == "__main__":
    unittest.main()
