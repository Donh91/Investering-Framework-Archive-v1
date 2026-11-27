"""R5: no-call HOLD is not a Director analysis or new admission."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Full-repository CI uses pytest importlib collection; the sibling fixture directory
# is not implicitly on sys.path in that mode.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_forecast_fair_allocation import SCRIPT, ctx, pair, run, forecasts, snapshot, module

UTC = timezone.utc
MODE = "BUDGET_HOLD_EXISTING_ADMITTED_ONLY_v1"


def clock(minutes):
    return (datetime.now(UTC) + timedelta(minutes=minutes)).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def hold_run(repo, captured, *, attempt="1", receipt_updates=None, context_updates=None, extra=(), cap=5):
    root = repo / "research/experiment_lifecycle"
    folder = root / "budget_hold_inputs" / ("123-" + attempt)
    folder.mkdir(parents=True, exist_ok=True)
    context = ctx(captured, "hold-capture")
    context.update({"coverage": {"comparable_numeric_metrics": 2}, "delta_status": "DELTA_READY"})
    context.update(context_updates or {})
    receipt = {
        "contract": "ROUTINE_API_BUDGET_DISPOSITION_v1",
        "lane": "director", "disposition": "HOLD", "reason": "API_RESERVE_GUARD_BLOCKED",
        "run_id": "123", "run_attempt": attempt, "head_sha": "a" * 40,
        "paid_call_executed_here": False, "analysis_completed_here": False, "paid_authority": False,
        "guard_observations": [
            {"guard": "lane", "disposition": "PASS", "returncode": 0, "stdout_sha256": "b" * 64,
             "reason": "GUARD_PASS", "budget": {"status": "PASS", "remaining_usd": 3.0, "reserve_usd": 0.05}},
            {"guard": "monthly", "disposition": "HOLD", "returncode": 1, "stdout_sha256": "c" * 64,
             "reason": "API_RESERVE_GUARD_BLOCKED", "budget": {"status": "BLOCKED", "remaining_usd": 3.9, "reserve_usd": 4.0,
                "owner_global_remaining_usd_after_risk": 3.9, "owner_global_reserve_usd": 4.0}},
        ],
    }
    receipt.update(receipt_updates or {})
    cp, rp = folder / "context.json", folder / "budget_disposition.json"
    cp.write_text(json.dumps(context))
    rp.write_text(json.dumps(receipt))
    cmd = [sys.executable, str(SCRIPT), "--repo-root", str(repo),
           "--daily-context", str(cp), "--budget-hold-receipt", str(rp), "--existing-admitted-only",
           "--candidate-root", str(root / "candidates"), "--observation-root", str(root / "observations"),
           "--dispatch-root", str(root / "dispatch"), "--forecast-root", str(repo / "research/framework_memory/forecast_memory"),
           "--outcome-root", str(repo / "research/framework_memory/outcome_memory"), "--receipt-root", str(root / "receipts"),
           "--registry-output", str(root / "LATEST_EXPERIMENT_REGISTRY.json"),
           "--manifest-output", str(root / "LATEST_EXPERIMENT_DISPATCH_MANIFEST.json"),
           "--admission-root", str(root / "admission"),
           "--admission-registry-output", str(root / "LATEST_SCIENTIFIC_ADMISSION_REGISTRY.json"),
           "--max-new-forecasts", str(cap), *extra]
    env = dict(os.environ, GITHUB_RUN_ID="123", GITHUB_RUN_ATTEMPT=attempt, GITHUB_SHA="a" * 40)
    return subprocess.run(cmd, capture_output=True, text=True, env=env)


def immutable(repo):
    return {p: b for p, b in snapshot(repo).items()
            if "budget_hold_inputs" not in p and not p.endswith("LATEST_EXPERIMENT_REGISTRY.json")
            and "/observations/" not in p and "/forecast_memory/" not in p}


class ExistingOnlyHold(unittest.TestCase):
    def seed(self, repo):
        # Registration and admission are frozen now; tests backdate only their synthetic fixture
        # so the next fresh capture is strictly prospective relative to admission.
        run(repo, {"experiment_candidates": [pair(i) for i in range(8)]}, clock(-90), cap=0)
        root = repo / "research/experiment_lifecycle"
        for path in (root / "candidates").rglob("*.json"):
            row = json.loads(path.read_text())
            row["registered_at_utc"] = clock(-80)
            path.write_text(json.dumps(row))
        for path in (root / "admission").rglob("*.json"):
            row = json.loads(path.read_text())
            row["admission_frozen_at_utc"] = clock(-80)
            path.write_text(json.dumps(row))
        return root

    def test_hold_advances_existing_only_and_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            root = self.seed(repo)
            # Unknown admission and not-yet-qualified admissions are never silently admitted.
            paths = sorted((root / "admission").rglob("*.json"))
            paths[0].unlink()
            row = json.loads(paths[1].read_text())
            row["status"] = "KEEP_SHADOW"
            paths[1].write_text(json.dumps(row))
            before = immutable(repo)
            captured = clock(-1)
            result = hold_run(repo, captured)
            self.assertEqual(result.returncode, 0, result.stderr)
            summary = json.loads(result.stdout)
            self.assertEqual(summary["mode"], MODE)
            self.assertEqual(summary["new_candidate_count"], 0)
            self.assertEqual(summary["dispatch_created"], 0)
            self.assertEqual(summary["observations_created"], 6)
            self.assertEqual(summary["new_forecasts"], 5)
            self.assertIs(summary["paid_call_executed_here"], False)
            self.assertIs(summary["analysis_completed_here"], False)
            self.assertEqual(immutable(repo), before)
            observations = [json.loads(p.read_text()) for p in (root / "observations").rglob("*.json")]
            new = [r for r in observations if r["source"].get("mode") == MODE]
            self.assertEqual(len(new), 6)
            for row in new:
                source = row["source"]
                self.assertIsNone(source["daily_output_sha256"])
                self.assertIsNone(source["daily_receipt_sha256"])
                self.assertEqual(source["budget_hold_receipt_sha256"],
                                 hashlib.sha256((repo / source["budget_hold_receipt_path"]).read_bytes()).hexdigest())
            first = sorted(r["forecast_id"] for r in forecasts(repo))
            self.assertEqual(len(first), 5)
            replay = hold_run(repo, captured, attempt="2")
            self.assertEqual(replay.returncode, 0, replay.stderr)
            self.assertEqual(json.loads(replay.stdout)["new_forecasts"], 0)
            self.assertEqual(json.loads(replay.stdout)["observations_created"], 0)
            self.assertEqual(sorted(r["forecast_id"] for r in forecasts(repo)), first)
            self.assertEqual(immutable(repo), before)
            # The paid path must still process genuinely new proposals, but not double-count
            # the same capture for candidates already observed under HOLD.
            paid = run(repo, {"experiment_candidates": []}, captured, run_id="hold-capture")
            self.assertEqual(paid["new_forecasts"], 0)
            for row in new:
                matches = [json.loads(p.read_text()) for p in (root / "observations" / row["candidate_id"]).rglob("*.json")]
                self.assertEqual(sum(r["observed_at_utc"] == captured for r in matches), 1)

    def test_missing_future_or_wrong_admission_never_admitted(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            root = self.seed(repo)
            paths = sorted((root / "admission").rglob("*.json"))
            for i, path in enumerate(paths):
                row = json.loads(path.read_text())
                if i % 2:
                    row["admission_frozen_at_utc"] = clock(10)
                else:
                    row["semantic_fingerprint"] = "wrong"
                path.write_text(json.dumps(row))
            before = immutable(repo)
            result = hold_run(repo, clock(-1))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["observations_created"], 0)
            self.assertEqual(forecasts(repo), [])
            self.assertEqual(immutable(repo), before)

    def test_error_or_unverified_hold_cannot_write(self):
        variants = [
            {"disposition": "PASS"}, {"disposition": "ERROR"}, {"disposition": ""},
            {"run_attempt": "9"}, {"head_sha": "b" * 40}, {"lane": "research"},
            {"paid_authority": True}, {"analysis_completed_here": True}, {"paid_call_executed_here": True},
            {"guard_observations": []}, {"guard_observations": [{"guard": "monthly", "disposition": "HOLD", "returncode": 1}]},
        ]
        for variant in variants:
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                self.seed(repo)
                before = {p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}
                result = hold_run(repo, clock(-1), receipt_updates=variant)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual({p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}, before)

    def test_guard_arithmetic_contradiction_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            self.seed(repo)
            before = {p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}
            invalid = {"guard_observations": [{"guard": "lane", "disposition": "HOLD", "returncode": 1,
                "reason": "API_RESERVE_GUARD_BLOCKED", "stdout_sha256": "b" * 64,
                "budget": {"status": "BLOCKED", "remaining_usd": 3.0, "reserve_usd": 0.05}}]}
            result = hold_run(repo, clock(-1), receipt_updates=invalid)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual({p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}, before)

    def test_stale_future_news_only_and_extra_proposals_fail_closed(self):
        for captured, updates, extra, cap in [
            (clock(-241), {}, (), 5), (clock(2), {}, (), 5),
            (clock(-1), {"coverage": {"comparable_numeric_metrics": 0}}, (), 5),
            (clock(-1), {}, ("--legacy-sensor-catalog", "unused.json"), 5),
            (clock(-1), {}, (), 6),
        ]:
            with self.subTest(captured=captured, updates=updates, extra=extra, cap=cap), tempfile.TemporaryDirectory() as td:
                repo = Path(td)
                self.seed(repo)
                before = {p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}
                result = hold_run(repo, captured, context_updates=updates, extra=extra, cap=cap)
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual({p: b for p, b in snapshot(repo).items() if "budget_hold_inputs" not in p}, before)

    def test_hold_observation_does_not_consume_replication_episode(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            folder = root / "EC-example"
            folder.mkdir()
            row = {"contract": "EXPERIMENT_OBSERVATION_v1", "candidate_id": "EC-example",
                   "observed_at_utc": "2026-01-01T00:00:00Z", "evaluation_status": "FIRED",
                   "source": {"mode": MODE}}
            (folder / "hold.json").write_text(json.dumps(row))
            self.assertIsNone(module.prior_observation_status(root, "EC-example", "2026-01-02T00:00:00Z"))
            row["source"] = {}
            (folder / "normal.json").write_text(json.dumps(row))
            self.assertEqual(module.prior_observation_status(root, "EC-example", "2026-01-02T00:00:00Z"), "FIRED")
