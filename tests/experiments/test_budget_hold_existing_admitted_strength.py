import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import test_budget_hold_existing_admitted as h
from test_forecast_fair_allocation import run


class ExistingOnlyHoldStrength(unittest.TestCase):
    def seed(self, repo):
        return h.ExistingOnlyHold.seed(self, repo)

    def test_hold_never_dispatches_even_when_an_episode_would_start(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td); root = self.seed(repo)
            for p in (root / "observations").rglob("*.json"):
                p.unlink()  # no prior observation: a FIRED observation would start an episode
            before = sorted((root / "dispatch").rglob("*.json"))
            result = h.hold_run(repo, h.clock(-1))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertGreater(json.loads(result.stdout)["observations_created"], 0)
            self.assertEqual(json.loads(result.stdout)["dispatch_created"], 0)
            self.assertEqual(sorted((root / "dispatch").rglob("*.json")), before)

    def test_hold_after_paid_observation_of_same_capture_is_a_noop(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td); root = self.seed(repo)
            captured = h.clock(-1)
            run(repo, {"experiment_candidates": []}, captured, cap=5, run_id="hold-capture")
            obs = sorted((root / "observations").rglob("*.json"))
            result = h.hold_run(repo, captured)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["observations_created"], 0)
            self.assertEqual(sorted((root / "observations").rglob("*.json")), obs)

    def test_conflicting_duplicate_admission_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td); root = self.seed(repo)
            path = sorted((root / "admission").rglob("*.json"))[0]
            row = json.loads(path.read_text()); row["status"] = "KEEP_SHADOW"
            dup = path.parent / "zz-duplicate" / path.name
            dup.parent.mkdir(); dup.write_text(json.dumps(row))
            before = h.immutable(repo)
            result = h.hold_run(repo, h.clock(-1))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("existing_only_evidence_unverified", result.stderr)
            self.assertEqual(h.immutable(repo), before)

    def test_owner_global_reserve_hold_is_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td); self.seed(repo)
            guards = [
                {"guard": "lane", "disposition": "PASS", "returncode": 0, "stdout_sha256": "b" * 64,
                 "reason": "GUARD_PASS", "budget": {"status": "PASS", "remaining_usd": 3.0, "reserve_usd": 0.05}},
                {"guard": "monthly", "disposition": "HOLD", "returncode": 1, "stdout_sha256": "c" * 64,
                 "reason": "API_RESERVE_GUARD_BLOCKED", "budget": {"status": "BLOCKED", "remaining_usd": 10.0, "reserve_usd": 4.0,
                    "owner_global_remaining_usd_after_risk": 3.0, "owner_global_reserve_usd": 4.0}}]
            result = h.hold_run(repo, h.clock(-1), receipt_updates={"guard_observations": guards})
            self.assertEqual(result.returncode, 0, result.stderr)
