"""Forecast-slot allocation must be fair, outcome-blind, deterministic and replay-idempotent.

Native run 44628588447 (2026-11-19) had 334 FIRED qualified candidates and a cap of 5 new
forecasts; the five lowest candidate IDs took every slot because allocation was ordered by
(kind, candidate_id) only. A perpetually firing candidate with a higher ID could never be served.
"""
import json
import re
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


def ctx(captured, run_id="fair-allocation-run"):
    metrics = {"spot": {"BTCUSDT": {"close": 64000.0}, "ETHBTC": {"close": 0.0302}}, "breadth": {"advancers": 60}}
    return {"latest_capture": {"captured_at_utc": captured, "run_id": run_id, "market_metrics": metrics},
            "previous_capture": {"captured_at_utc": "2026-08-01T00:00:00Z", "market_metrics": metrics}, "metric_deltas": []}


def run(repo: Path, output: dict, captured: str, cap: int = 5, run_id: str = "fair-allocation-run") -> dict:
    proc = run_raw(repo, output, captured, cap, run_id)
    if proc.returncode != 0:
        raise AssertionError(f"producer failed: {proc.stderr[-2000:]}")
    return json.loads(proc.stdout)


def run_raw(repo: Path, output: dict, captured: str, cap: int = 5, run_id: str = "fair-allocation-run") -> subprocess.CompletedProcess:
    daily = repo / "daily"
    daily.mkdir(parents=True, exist_ok=True)
    (daily / "output.json").write_text(json.dumps(output))
    (daily / "context.json").write_text(json.dumps(ctx(captured, run_id)))
    (daily / "receipt.json").write_text(json.dumps({"contract": "API_AGENT_RECEIPT_v3"}))
    el = repo / "research/experiment_lifecycle"
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(repo),
           "--daily-output", str(daily / "output.json"), "--daily-context", str(daily / "context.json"), "--daily-receipt", str(daily / "receipt.json"),
           "--candidate-root", str(el / "candidates"), "--observation-root", str(el / "observations"), "--dispatch-root", str(el / "dispatch"),
           "--forecast-root", str(repo / FORECAST_ROOT), "--outcome-root", str(repo / "research/framework_memory/outcome_memory"),
           "--receipt-root", str(el / "receipts"), "--registry-output", str(el / "LATEST_EXPERIMENT_REGISTRY.json"),
           "--manifest-output", str(el / "LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"), "--admission-root", str(el / "admission"),
           "--admission-registry-output", str(el / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"), "--max-new-forecasts", str(cap)]
    return subprocess.run(cmd, capture_output=True, text=True)


def snapshot(repo: Path) -> dict[str, bytes]:
    return {p.relative_to(repo).as_posix(): p.read_bytes() for p in repo.rglob("*") if p.is_file() and p.relative_to(repo).parts[0] != "daily"}


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


def fdoc(cid, window, frozen, **extra):
    return {"contract": "FROZEN_FORECAST_v1", "forecast_id": module.canonical_forecast_id(cid, window), "source_candidate_id": cid,
            "causal_event_window_id": window, "frozen_at_utc": frozen, **extra}


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
            docs = [fdoc("EC-a", "w1", "2026-08-02T20:00:00Z"), fdoc("EC-a", "w2", "2026-08-03T20:00:00Z"),
                    fdoc("EC-b", "w3", "2026-08-01T20:00:00.000+00:00"),
                    {"contract": "SOME_OTHER_INDEX_v1", "entries": 3}]
            for i, doc in enumerate(docs):
                (root / f"d{i}.json").write_text(json.dumps(doc))
            history = module.forecast_service_history(root, "2026-08-03T20:00:00Z")
            self.assertEqual(set(history), {"EC-a", "EC-b"})
            self.assertEqual(history["EC-a"][0], 1)
            self.assertTrue(history["EC-a"][1].startswith("2026-08-02T20:00:00"))
            # lookback: slots older than the window no longer count, so long-served candidates re-enter rotation
            self.assertEqual(set(module.forecast_service_history(root, "2026-08-03T20:00:00Z", lookback_days=1)), {"EC-a"})
            self.assertEqual(module.forecast_service_history(root / "missing", "2026-08-03T20:00:00Z"), {})


def window_id(captured: str) -> str:
    return module.base.sha({"run": "fair-allocation-run", "captured": captured})[:20]


def in_window(repo: Path, captured: str) -> list[dict]:
    return [r for r in forecasts(repo) if r.get("causal_event_window_id") == window_id(captured)]


def plant_window_forecast(repo: Path, template: dict, captured: str) -> Path:
    """Simulate a forecast written into ``captured``'s window by an earlier (old-policy) producer."""
    window = window_id(captured)
    value = dict(template, frozen_at_utc=captured, causal_event_window_id=window,
                 forecast_id="EXP-FC-" + module.base.sha({"candidate_id": template["source_candidate_id"], "window": window})[:20])
    path = repo / FORECAST_ROOT / "2026/08" / f"{value['forecast_id']}.json"
    path.write_text(json.dumps(value, sort_keys=True))
    return path


class ReplayContainmentRound2(unittest.TestCase):
    """D1-A: the cap is per causal event window and counts rows already occupying that window."""

    output8 = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}

    def test_replay_with_new_earlier_ordered_candidate_keeps_window_at_cap(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            run(repo, self.output8, tick(1))
            before = sorted(p.read_bytes() for p in (repo / FORECAST_ROOT).rglob("*.json"))
            grown = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(9)]}
            summary = run(repo, grown, tick(1))  # never-served newcomer sorts first
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(len(in_window(repo, tick(1))), 5)
            self.assertEqual(sorted(p.read_bytes() for p in (repo / FORECAST_ROOT).rglob("*.json")), before)

    def _old_policy_window(self, repo: Path, count: int) -> list[str]:
        run(repo, self.output8, tick(0))
        run(repo, self.output8, tick(1))
        served_counts = served(repo)
        latest = {}
        for r in forecasts(repo):
            latest[r["source_candidate_id"]] = r
        # the old ID-ordered policy would pick by candidate_id; plant the most-served ones so the
        # new least-served order would prefer entirely different candidates
        chosen = sorted(latest, key=lambda c: (-served_counts[c], c))[:count]
        for cid in chosen:
            plant_window_forecast(repo, latest[cid], tick(2))
        return chosen

    def test_pre_cutover_window_with_five_old_policy_rows_issues_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            chosen = self._old_policy_window(repo, 5)
            summary = run(repo, self.output8, tick(2))
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(sorted(r["source_candidate_id"] for r in in_window(repo, tick(2))), sorted(chosen))

    def test_historical_over_cap_window_fails_closed_for_additional_issuance(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self._old_policy_window(repo, 6)
            before = sorted(p.read_bytes() for p in (repo / FORECAST_ROOT).rglob("*.json"))
            summary = run(repo, self.output8, tick(2))
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(len(in_window(repo, tick(2))), 6)  # nothing rewritten or deleted
            self.assertEqual(sorted(p.read_bytes() for p in (repo / FORECAST_ROOT).rglob("*.json")), before)
            self.assertEqual(summary["forecast_allocation"]["available_slots"], 0)

    def test_removed_candidate_keeps_its_window_row_and_its_slot(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            holder = in_window(repo, tick(0))[0]
            removed = None
            for p in (repo / "research/experiment_lifecycle/candidates").rglob(f"{holder['source_candidate_id']}.json"):
                removed = json.loads(p.read_text())["spec"]["target_threshold_pct"]
                p.unlink()
            remaining = [c for c in self.output8["experiment_candidates"] if c["target_threshold_pct"] != removed]
            self.assertEqual(len(remaining), 7)
            summary = run(repo, {"forecast_candidates": [], "experiment_candidates": remaining}, tick(0))
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertIn(holder["forecast_id"], {r["forecast_id"] for r in in_window(repo, tick(0))})
            self.assertEqual(len(in_window(repo, tick(0))), 5)

    def test_partial_write_fills_only_the_remaining_slots(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            original = {r["forecast_id"] for r in in_window(repo, tick(0))}
            paths = sorted((repo / FORECAST_ROOT).rglob("*.json"))
            for p in paths[:3]:
                p.unlink()
            summary = run(repo, self.output8, tick(0))
            self.assertEqual(summary["new_forecasts"], 3)
            self.assertEqual({r["forecast_id"] for r in in_window(repo, tick(0))}, original)

    def test_cap_change_raises_to_the_new_cap_and_never_shrinks_existing_rows(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0), cap=5)
            self.assertEqual(run(repo, self.output8, tick(0), cap=7)["new_forecasts"], 2)
            self.assertEqual(run(repo, self.output8, tick(0), cap=3)["new_forecasts"], 0)
            self.assertEqual(len(in_window(repo, tick(0))), 7)

    def test_naive_timestamp_in_history_fails_whole_run_before_any_write(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            bad = dict(forecasts(repo)[0], frozen_at_utc="2026-08-01T20:00:00", forecast_id="EXP-FC-naive0000000000000")
            (repo / FORECAST_ROOT / "2026/08/EXP-FC-naive0000000000000.json").write_text(json.dumps(bad))
            before = snapshot(repo)
            proc = run_raw(repo, self.output8, tick(1))
            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("FORECAST_STORE_INTEGRITY_FAILURE", proc.stderr)
            self.assertEqual(snapshot(repo), before)

    def test_summary_records_policy_and_per_kind_denominators(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            output = {"forecast_candidates": [director_forecast()], "experiment_candidates": [pair(i) for i in range(8)]}
            alloc = run(repo, output, tick(0))["forecast_allocation"]
            self.assertEqual(alloc["policy_version"], module.ALLOCATION_POLICY_VERSION)
            self.assertEqual(alloc["cap"], 5)
            self.assertEqual(alloc["by_kind"]["FORECAST_TEST"], {"eligible": 1, "issued_new": 1, "held_in_window": 0})
            self.assertEqual(alloc["by_kind"]["SENSOR_COMBINATION"], {"eligible": 8, "issued_new": 4, "held_in_window": 0})


class HistoryIdentityRound2(unittest.TestCase):
    """D1-B: history counts unique forecast identities and fails closed on identity/time conflicts."""

    def _doc(self, fid, cid="EC-a", frozen="2026-08-02T20:00:00Z", **extra):
        doc = fdoc("EC-a", "w-" + fid, frozen, **extra)  # canonical ID fixed by (EC-a, window)
        doc["source_candidate_id"] = cid
        return doc

    def test_duplicate_paths_for_one_forecast_id_count_once(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc = self._doc("f1")
            for sub in ("a", "b"):
                (root / sub).mkdir()
                (root / sub / "f1.json").write_text(json.dumps(doc))
            self.assertEqual(module.forecast_service_history(root, "2026-08-03T20:00:00Z")["EC-a"][0], 1)

    def test_conflicting_content_or_owner_for_one_forecast_id_fails_closed(self):
        for other in (self._doc("f1", cid="EC-b"), self._doc("f1", frozen="2026-08-01T20:00:00Z")):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / "a.json").write_text(json.dumps(self._doc("f1")))
                (root / "b.json").write_text(json.dumps(other))
                with self.assertRaises(module.AllocationIntegrityError):
                    module.forecast_service_history(root, "2026-08-03T20:00:00Z")

    def test_naive_or_unparseable_freeze_time_fails_closed_never_host_local(self):
        for frozen in ("2026-08-02T20:00:00", "not-a-time"):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td)
                (root / "a.json").write_text(json.dumps(self._doc("f1", frozen=frozen)))
                with self.assertRaises(module.AllocationIntegrityError):
                    module.forecast_service_history(root, "2026-08-03T20:00:00Z")

    def test_naive_capture_time_is_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(module.AllocationIntegrityError):
                module.forecast_service_history(Path(td), "2026-08-03T20:00:00")


class Round3StoreIntegrityAndCaptureClock(unittest.TestCase):
    """D1 round 3: unique-ID occupancy, strict forecast-store identity, canonical capture clock."""

    output8 = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}

    def _assert_store_failure_without_writes(self, repo: Path, captured: str, code: str):
        before = snapshot(repo)
        proc = run_raw(repo, self.output8, captured)
        self.assertNotEqual(proc.returncode, 0, proc.stdout[-500:])
        self.assertIn("FORECAST_STORE_INTEGRITY_FAILURE", proc.stderr)
        self.assertIn(code, proc.stderr)
        self.assertEqual(snapshot(repo), before)  # nothing written, nothing rewritten

    def test_two_ids_for_one_candidate_window_fail_closed_instead_of_collapsing(self):
        # F1/A, F2/A, F3/B, F4/C, F5/D in one window: 5 unique IDs must never become "4 occupied, 1 free"
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            rows = sorted(in_window(repo, tick(0)), key=lambda r: r["source_candidate_id"])
            for p in (repo / FORECAST_ROOT).rglob(f"{rows[4]['forecast_id']}.json"):
                p.unlink()
            twin = dict(rows[0], forecast_id="EXP-FC-twin0000000000000000")
            (repo / FORECAST_ROOT / "2026/08/EXP-FC-twin0000000000000000.json").write_text(json.dumps(twin))
            self._assert_store_failure_without_writes(repo, tick(0), "candidate_window")

    def test_conflicting_content_for_one_forecast_id_fails_whole_run_before_any_write(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            row = forecasts(repo)[0]
            (repo / FORECAST_ROOT / "2026/07").mkdir(parents=True)
            (repo / FORECAST_ROOT / f"2026/07/{row['forecast_id']}.json").write_text(json.dumps(dict(row, start_value=1.0)))
            self._assert_store_failure_without_writes(repo, tick(1), "forecast_id_ownership_or_content_conflict")

    def test_missing_identity_or_window_fails_closed(self):
        for field in ("source_candidate_id", "forecast_id", "causal_event_window_id"):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                run(repo, self.output8, tick(0))
                row = dict(forecasts(repo)[0])
                row.pop(field)
                (repo / FORECAST_ROOT / "2026/08/EXP-FC-missing00000000000000.json").write_text(json.dumps(row))
                self._assert_store_failure_without_writes(repo, tick(1), "forecast_identity_missing")

    def test_unreadable_expected_forecast_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            (repo / FORECAST_ROOT / "2026/08/EXP-FC-broken000000000000000.json").write_text("{not json")
            self._assert_store_failure_without_writes(repo, tick(1), "forecast_file_unreadable")

    def test_known_non_forecast_contract_and_non_json_files_are_ignored(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            (repo / FORECAST_ROOT / "2026/08/INDEX.json").write_text(json.dumps({"contract": "SOME_OTHER_INDEX_v1"}))
            (repo / FORECAST_ROOT / "README.md").write_text("notes")
            self.assertEqual(run(repo, self.output8, tick(1))["new_forecasts"], 5)

    def test_equal_instant_with_different_capture_format_issues_nothing(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, "2026-08-02T20:00:00Z")
            summary = run(repo, self.output8, "2026-08-02T21:00:00+01:00")  # same instant, other spelling
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(summary["forecast_allocation"]["status"], "FAIL_CLOSED:capture_clock_noncanonical")
            self.assertEqual(len(forecasts(repo)), 5)

    def test_missing_run_id_never_synthesises_a_window(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, self.output8, tick(0), run_id="")
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(summary["forecast_allocation"]["status"], "FAIL_CLOSED:capture_run_id_missing")

    def test_window_and_forecast_ids_are_byte_identical_for_a_real_historical_capture(self):
        # Native run 44628588447: source_run_id gh-44619142868-1, captured 2026-11-19T21:29:33Z;
        # main forecast EXP-FC-99f5fcbd5182de573074 (EC-0258e3807909a4d1987f) carries window a0f4c4c5aa23545675ff.
        self.assertTrue(module.canonical_capture_clock("2026-11-19T21:29:33Z"))
        window = module.causal_event_window("gh-44619142868-1", "2026-11-19T21:29:33Z")
        self.assertEqual(window, "a0f4c4c5aa23545675ff")
        self.assertEqual(module.canonical_forecast_id("EC-0258e3807909a4d1987f", window), "EXP-FC-99f5fcbd5182de573074")
        for other in ("2026-11-19T22:29:33+01:00", "2026-11-19T21:29:33.000Z", "2026-11-19T21:29:33", "2026-11-19 21:29:33Z", ""):
            self.assertFalse(module.canonical_capture_clock(other), other)


class Round4StrictParseAndCaptureValidation(unittest.TestCase):
    """D1 round 4: strict JSON (no duplicate keys, finite numbers, exact-byte duplicates) and
    exception-safe capture clock validation before any write."""

    output8 = {"forecast_candidates": [], "experiment_candidates": [pair(i) for i in range(8)]}

    def _store_failure(self, repo: Path, code: str):
        before = snapshot(repo)
        proc = run_raw(repo, self.output8, tick(1))
        self.assertEqual(proc.returncode, 3, proc.stderr[-800:])
        self.assertIn("FORECAST_STORE_INTEGRITY_FAILURE", proc.stderr)
        self.assertIn(code, proc.stderr)
        self.assertEqual(snapshot(repo), before)

    def _first_forecast_path(self, repo: Path) -> Path:
        return sorted((repo / FORECAST_ROOT).rglob("*.json"))[0]

    def _tamper(self, repo: Path, edit) -> None:
        path = self._first_forecast_path(repo)
        text = path.read_text()
        new = edit(text)
        self.assertNotEqual(new, text)
        path.write_text(new)

    def test_duplicate_contract_key_cannot_hide_a_forecast(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            self._tamper(repo, lambda t: t.rstrip().rstrip("}") + ',"contract":"SOME_OTHER_INDEX_v1"}\n')
            self._store_failure(repo, "forecast_file_duplicate_key")

    def test_duplicate_freeze_time_and_nested_keys_are_rejected(self):
        edits = {
            "frozen": lambda t: t.replace('"frozen_at_utc":', '"frozen_at_utc":"2026-07-01T00:00:00Z","frozen_at_utc":', 1),
            "nested": lambda t: t.replace('"always_wait":', '"always_wait":"X","always_wait":', 1),
        }
        for name, edit in edits.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                run(repo, self.output8, tick(0))
                self._tamper(repo, edit)
                self._store_failure(repo, "forecast_file_duplicate_key")

    def test_non_finite_numbers_are_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity", "1e999"):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                run(repo, self.output8, tick(0))
                self._tamper(repo, lambda t: re.sub(r'"start_value":[^,}]+', f'"start_value":{token}', t, count=1))
                self._store_failure(repo, "forecast_file_non_finite_number")

    def test_forecast_shaped_row_with_other_contract_is_unclassifiable(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            self._tamper(repo, lambda t: t.replace('"FROZEN_FORECAST_v1"', '"FROZEN_FORECAST_v9"', 1))
            self._store_failure(repo, "forecast_file_unclassifiable")

    def test_semantically_equal_duplicate_with_different_bytes_is_a_conflict(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            row = json.loads(self._first_forecast_path(repo).read_text())
            (repo / FORECAST_ROOT / "2026/07").mkdir(parents=True)
            (repo / FORECAST_ROOT / f"2026/07/{row['forecast_id']}.json").write_text(json.dumps(row, indent=2))
            self._store_failure(repo, "forecast_id_ownership_or_content_conflict")

    def test_unrepresentable_store_clock_is_an_integrity_failure(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            run(repo, self.output8, tick(0))
            self._tamper(repo, lambda t: re.sub(r'"frozen_at_utc":"[^"]+"', '"frozen_at_utc":"0001-01-01T00:00:00+01:00"', t, count=1))
            self._store_failure(repo, "allocation_time_unrepresentable")

    def test_invalid_capture_clock_fails_whole_run_before_any_write(self):
        for captured in ("not-a-time", "2026-02-30T00:00:00Z", "0001-01-01T00:00:00+01:00"):
            with self.subTest(captured=captured), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                run(repo, self.output8, tick(0))
                before = snapshot(repo)
                proc = run_raw(repo, self.output8, captured)
                self.assertEqual(proc.returncode, 4, proc.stderr[-800:])
                self.assertIn("CAPTURE_CLOCK_INVALID", proc.stderr)
                self.assertEqual(snapshot(repo), before)

    def test_canonical_but_out_of_range_capture_holds_allocation(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, self.output8, "0001-01-01T00:00:00Z")
            self.assertEqual(summary["new_forecasts"], 0)
            self.assertEqual(summary["forecast_allocation"]["status"], "FAIL_CLOSED:capture_clock_noncanonical")

    def test_valid_historical_capture_still_allocates(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            summary = run(repo, self.output8, "2026-11-19T21:29:33Z", run_id="gh-44619142868-1")
            self.assertEqual(summary["forecast_allocation"]["causal_event_window_id"], "a0f4c4c5aa23545675ff")
            self.assertEqual(summary["new_forecasts"], 5)


if __name__ == "__main__":
    unittest.main()
