"""REPLAY / CANARY / IMMUTABILITY guard for the canonical accountability loop.

TASK3 R3-15 (REPLAY, CANARY families) and R3-16 (stop conditions).

This module replays the patched maturation logic against a COPY of the real
frozen forecasts and real evidence captures. It writes nothing to any tracked
path: every artefact it produces lives in a temporary directory, and the source
trees are hashed before and after to prove it.

The replay is a bounded validation, NOT a recovery. Its purpose is to prove that
the patch resolves exactly the cohort Task 3 audited as mechanically recoverable
and refuses every cohort Task 3 classified as scientifically lost.

To stay deterministic as the repository grows, the replay reconstructs the exact
snapshot Task 3 audited: forecasts frozen at or before the pinned instant, and
evidence captured at or before the same instant.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts" / "learning" / "outcome_maturation_engine.py"
FORECAST_ROOT = ROOT / "research" / "framework_memory" / "forecast_memory"
OUTCOME_ROOT = ROOT / "research" / "framework_memory" / "outcome_memory"
CAPTURE_ROOT = ROOT / "03_DAILY_CAPTURE_LOGS" / "captures"

# The instant Task 3 evaluated the population at.
PINNED_NOW = "2026-08-19T13:00:00Z"
MAX_EVIDENCE_LAG_HOURS = 24

# Task 3 R3-05 audited classification at PINNED_NOW.
TASK3_CLOSED_WINDOW_RECOVERABLE = 20      # C2 - the R3-16 stop condition ceiling
TASK3_OPEN_WINDOW_RECOVERABLE = 16        # C3
TASK3_NAMESPACE_MIGRATED = 39             # C4 - must never resolve
TASK3_LEGACY_UNIT_QUARANTINED = 8         # C1 - must never resolve

# Task 3 R3-13 provenance trace.
CANARY_ID = "EXP-FC-b4493e97c29bb54efd9f"
CANARY_EXPECTED = {
    "status": "MATURED",
    "result": "HIT",
    "start_value": 63004.9,
    "end_value": 63034.6,
    "return_pct": 0.04713919,
    "evidence_lag_hours": 0.019722,
    "forecast_sha256": "882d28991feb81308649dca95c1304c84cf98344204589cf67d777e52f24fb91",
    "evidence_sha256": "eb780a86a93a89a6cacc518ccdbbcc29e9debfcf3f510e08408ddf4f33994deb",
}
CANARY_EVIDENCE_NAME = "134745_gh-31950830851-1.json"


def parse_dt(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def tree_digest(root: Path) -> str:
    """Order-independent digest over every tracked file's path and bytes."""
    entries = []
    for path in sorted(root.rglob("*.json")):
        entries.append(f"{path.relative_to(root)}:{hashlib.sha256(path.read_bytes()).hexdigest()}")
    return hashlib.sha256("\n".join(entries).encode()).hexdigest()


@unittest.skipUnless(FORECAST_ROOT.exists() and CAPTURE_ROOT.exists(),
                     "real forecast/evidence trees unavailable")
class HistoricalReplayGuard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.now = parse_dt(PINNED_NOW)
        # Immutability proof, part 1: digest the real trees before any replay runs.
        cls.forecast_digest_before = tree_digest(FORECAST_ROOT)
        cls.capture_digest_before = tree_digest(CAPTURE_ROOT)
        cls.outcome_digest_before = tree_digest(OUTCOME_ROOT) if OUTCOME_ROOT.exists() else None

        cls._tmp = tempfile.TemporaryDirectory()
        sandbox = Path(cls._tmp.name)
        cls.fixture_forecasts = sandbox / "forecasts"
        cls.fixture_evidence = sandbox / "evidence"
        cls.replay_output = sandbox / "outcomes"
        for directory in (cls.fixture_forecasts, cls.fixture_evidence, cls.replay_output):
            directory.mkdir(parents=True)

        cls.forecasts = {}
        for path in FORECAST_ROOT.rglob("*.json"):
            value = json.loads(path.read_text())
            if value.get("contract") != "FROZEN_FORECAST_v1":
                continue
            if parse_dt(value["frozen_at_utc"]) > cls.now:
                continue
            shutil.copy(path, cls.fixture_forecasts / path.name)
            cls.forecasts[value["forecast_id"]] = value

        cls.evidence_count = 0
        for path in CAPTURE_ROOT.rglob("*.json"):
            if path.name == "LATEST.json":
                continue
            try:
                captured = json.loads(path.read_text()).get("captured_at_utc")
            except Exception:
                continue
            if not captured or parse_dt(captured) > cls.now:
                continue
            shutil.copy(path, cls.fixture_evidence / f"{path.parent.name}_{path.name}")
            cls.evidence_count += 1

        cls.result = subprocess.run(
            [sys.executable, str(ENGINE),
             "--forecast-root", str(cls.fixture_forecasts),
             "--evidence-root", str(cls.fixture_evidence),
             "--output-root", str(cls.replay_output),
             "--now-utc", PINNED_NOW,
             "--max-evidence-lag-hours", str(MAX_EVIDENCE_LAG_HOURS)],
            capture_output=True, text=True)
        cls.outcomes = {}
        for path in cls.replay_output.glob("*.json"):
            value = json.loads(path.read_text())
            cls.outcomes[value["forecast_id"]] = value

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    # ---- immutability -----------------------------------------------------

    def test_replay_does_not_modify_any_tracked_forecast(self):
        self.assertEqual(self.forecast_digest_before, tree_digest(FORECAST_ROOT))

    def test_replay_does_not_modify_any_tracked_evidence(self):
        self.assertEqual(self.capture_digest_before, tree_digest(CAPTURE_ROOT))

    def test_replay_does_not_modify_any_tracked_historical_outcome(self):
        if self.outcome_digest_before is None:
            self.skipTest("no outcome tree")
        self.assertEqual(self.outcome_digest_before, tree_digest(OUTCOME_ROOT))

    def test_forecast_sha256_is_unchanged_for_every_replayed_row(self):
        def canonical(value):
            return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
        for forecast_id, outcome in self.outcomes.items():
            with self.subTest(forecast_id=forecast_id):
                expected = hashlib.sha256(canonical(self.forecasts[forecast_id])).hexdigest()
                self.assertEqual(outcome["forecast_sha256"], expected)

    # ---- engine health ----------------------------------------------------

    def test_replay_completes_without_errors(self):
        self.assertEqual(self.result.returncode, 0, self.result.stderr)
        self.assertEqual(json.loads(self.result.stdout)["errors"], [])

    # ---- R3-16 stop conditions -------------------------------------------

    def _resolved_split(self):
        closed, still_open = [], []
        for forecast_id, outcome in self.outcomes.items():
            if outcome["status"] != "MATURED":
                continue
            due = parse_dt(self.forecasts[forecast_id]["outcome_due_utc"])
            target = closed if self.now > due + timedelta(hours=MAX_EVIDENCE_LAG_HOURS) else still_open
            target.append(forecast_id)
        return closed, still_open

    def test_closed_window_recovery_stays_within_the_audited_classification(self):
        """R3-16 primary stop condition: more than 20 closed-window rows resolving
        means the patch found a path the audit did not authorise."""
        closed, _ = self._resolved_split()
        self.assertLessEqual(len(closed), TASK3_CLOSED_WINDOW_RECOVERABLE,
                             f"recovery rate exceeds the audited classification: {sorted(closed)}")
        self.assertEqual(len(closed), TASK3_CLOSED_WINDOW_RECOVERABLE)

    def test_open_window_recovery_matches_the_audited_classification(self):
        _, still_open = self._resolved_split()
        self.assertEqual(len(still_open), TASK3_OPEN_WINDOW_RECOVERABLE)

    def test_no_legacy_unit_ambiguous_row_ever_resolves(self):
        """C1 - forbidden by FORECAST_CANDIDATE_CONTRACT_v2.legacy_policy."""
        quarantined = [fid for fid, outcome in self.outcomes.items()
                       if outcome.get("reason") == "LEGACY_V1_TARGET_UNIT_AMBIGUOUS"]
        self.assertEqual(len(quarantined), TASK3_LEGACY_UNIT_QUARANTINED)
        for forecast_id in quarantined:
            self.assertEqual(self.outcomes[forecast_id]["status"], "CENSORED")

    def test_namespace_migrated_rows_stay_censored(self):
        """C4 - the 39 rows orphaned by market_metrics.spot -> spot_legacy."""
        orphaned = [fid for fid, outcome in self.outcomes.items()
                    if outcome.get("reason") == "EVIDENCE_NAMESPACE_UNAVAILABLE"]
        self.assertEqual(len(orphaned), TASK3_NAMESPACE_MIGRATED)
        for forecast_id in orphaned:
            outcome = self.outcomes[forecast_id]
            self.assertEqual(outcome["status"], "CENSORED")
            self.assertNotIn("end_value", outcome)
            self.assertNotIn("result", outcome)

    def test_no_metric_is_ever_substituted(self):
        """Every matured value must be re-derivable from the cited evidence at the
        cited path under the cited root - never from a neighbouring metric."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("metric_resolver", ROOT / "scripts" / "lib" / "metric_resolver.py")
        mr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mr)
        for forecast_id, outcome in self.outcomes.items():
            if outcome["status"] != "MATURED":
                continue
            with self.subTest(forecast_id=forecast_id):
                forecast = self.forecasts[forecast_id]
                evidence = json.loads(Path(outcome["evidence_path"]).read_text())
                again = mr.resolve(evidence, forecast["metric_path"], outcome["metric_path_root_applied"])
                self.assertTrue(again.ok)
                self.assertEqual(again.value, outcome["end_value"])

    def test_every_resolving_spot_row_used_pre_migration_evidence(self):
        """The only spot.* rows permitted to resolve are those whose eligible
        evidence pre-dates the 2026-08-08 namespace migration."""
        for forecast_id, outcome in self.outcomes.items():
            if outcome["status"] != "MATURED":
                continue
            if not self.forecasts[forecast_id]["metric_path"].startswith("spot."):
                continue
            with self.subTest(forecast_id=forecast_id):
                evidence = json.loads(Path(outcome["evidence_path"]).read_text())
                self.assertIn("spot", evidence.get("market_metrics", {}),
                              "a spot.* row resolved against post-migration evidence")

    def test_evidence_selection_rule_is_unchanged(self):
        """Every cited evidence file lies inside the window the forecast declared,
        and is the earliest eligible capture."""
        captures = []
        for path in self.fixture_evidence.glob("*.json"):
            value = json.loads(path.read_text())
            captures.append((parse_dt(value["captured_at_utc"]), path))
        captures.sort(key=lambda row: row[0])
        for forecast_id, outcome in self.outcomes.items():
            if "evidence_path" not in outcome:
                continue
            with self.subTest(forecast_id=forecast_id):
                due = parse_dt(self.forecasts[forecast_id]["outcome_due_utc"])
                window_end = due + timedelta(hours=MAX_EVIDENCE_LAG_HOURS)
                eligible = [row for row in captures if due <= row[0] <= window_end]
                self.assertTrue(eligible)
                self.assertEqual(Path(outcome["evidence_path"]).name, eligible[0][1].name)

    def test_no_mutable_pointer_is_ever_cited_as_evidence(self):
        for outcome in self.outcomes.values():
            self.assertNotIn("LATEST.json", outcome.get("evidence_path", ""))

    # ---- R3-13 provenance canary -----------------------------------------

    def test_provenance_canary_reproduces_task3_exactly(self):
        self.assertIn(CANARY_ID, self.outcomes, "canary forecast absent from the replay")
        outcome = self.outcomes[CANARY_ID]
        for key, expected in CANARY_EXPECTED.items():
            with self.subTest(field=key):
                self.assertEqual(outcome[key], expected)
        self.assertEqual(Path(outcome["evidence_path"]).name.split("_", 1)[1], CANARY_EVIDENCE_NAME)
        self.assertEqual(outcome["resolver_version"], "METRIC_PATH_RESOLVER_v1")
        self.assertEqual(outcome["metric_path_root_applied"], "MARKET_METRICS_ROOT")

    def test_canary_forecast_bytes_are_untouched(self):
        source = next(FORECAST_ROOT.rglob(f"{CANARY_ID}.json"))
        copied = self.fixture_forecasts / f"{CANARY_ID}.json"
        self.assertEqual(source.read_bytes(), copied.read_bytes())

    # ---- replay idempotency ----------------------------------------------

    def test_second_replay_creates_no_duplicate_canonical_outcome(self):
        before = {path.name: path.read_bytes() for path in self.replay_output.glob("*.json")}
        again = subprocess.run(
            [sys.executable, str(ENGINE),
             "--forecast-root", str(self.fixture_forecasts),
             "--evidence-root", str(self.fixture_evidence),
             "--output-root", str(self.replay_output),
             "--now-utc", "2026-08-19T18:00:00Z",
             "--max-evidence-lag-hours", str(MAX_EVIDENCE_LAG_HOURS)],
            capture_output=True, text=True)
        self.assertEqual(again.returncode, 0, again.stderr)
        after = {path.name: path.read_bytes() for path in self.replay_output.glob("*.json")}
        for name, payload in before.items():
            self.assertEqual(payload, after[name], f"{name} changed on re-replay")
        self.assertEqual(json.loads(again.stdout)["matured"], 0)


if __name__ == "__main__":
    unittest.main()
