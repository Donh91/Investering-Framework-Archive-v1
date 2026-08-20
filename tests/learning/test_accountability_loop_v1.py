"""CONTRACT / INTEGRATION / IDEMPOTENCY / FAILURE-INJECTION / BACKWARD-COMPAT tests
for the canonical accountability loop (TASK3 R3-15).

Every test here runs against synthetic fixtures in a temporary directory. No
test in this module reads or writes any tracked repository object.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "scripts" / "learning" / "outcome_maturation_engine.py"
LEDGER = ROOT / "scripts" / "learning" / "build_model_calibration_ledger.py"

AUTHORISED_CENSOR_REASONS = {
    "LEGACY_V1_TARGET_UNIT_AMBIGUOUS",
    "NO_EVIDENCE_WITHIN_MAX_LAG",
    "METRIC_UNAVAILABLE",
    "EVIDENCE_NAMESPACE_UNAVAILABLE",
    "METRIC_PATH_ROOT_AMBIGUOUS",
    "METRIC_PATH_ROOT_UNDECLARED",
}


def iso(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def frozen_forecast(**overrides):
    base = {
        "contract": "FROZEN_FORECAST_v1",
        "unit_contract_version": "FORECAST_TARGET_UNITS_v2",
        "forecast_id": "EXP-FC-test0000000000000000",
        "source_candidate_id": "EC-test000000000000",
        "frozen_at_utc": "2026-08-10T00:00:00Z",
        "outcome_due_utc": "2026-08-11T00:00:00Z",
        "metric_path": "derivatives.BTC-USDT-SWAP.mark_price.mark_price",
        "direction": "UP",
        "threshold_pct": 1.0,
        "start_value": 100.0,
    }
    base.update(overrides)
    return base


def capture(captured_at: str, **market_metrics):
    return {"contract": "DAILY_LIVE_ANCHOR_INDEX_v3", "captured_at_utc": captured_at,
            "run_id": "gh-test-1", "market_metrics": dict(market_metrics)}


def derivatives(value):
    return {"BTC-USDT-SWAP": {"mark_price": {"mark_price": value}}}


class LoopHarness(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        for name in ("f", "e", "o"):
            (self.root / name).mkdir()
        self.addCleanup(self._tmp.cleanup)

    def write_forecast(self, forecast):
        (self.root / "f" / f"{forecast['forecast_id']}.json").write_text(json.dumps(forecast))
        return forecast

    def write_evidence(self, name, value):
        (self.root / "e" / name).write_text(json.dumps(value))

    def mature(self, now_utc, max_lag="24"):
        return subprocess.run(
            [sys.executable, str(ENGINE), "--forecast-root", str(self.root / "f"),
             "--evidence-root", str(self.root / "e"), "--output-root", str(self.root / "o"),
             "--now-utc", now_utc, "--max-evidence-lag-hours", max_lag],
            capture_output=True, text=True)

    def outcome(self, forecast_id="EXP-FC-test0000000000000000"):
        path = self.root / "o" / f"{forecast_id}.json"
        return json.loads(path.read_text()) if path.exists() else None


class ContractTests(LoopHarness):
    def test_matured_outcome_carries_resolver_provenance(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        result = self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        outcome = self.outcome()
        self.assertEqual(outcome["status"], "MATURED")
        self.assertEqual(outcome["result"], "HIT")
        self.assertEqual(outcome["resolver_version"], "METRIC_PATH_RESOLVER_v1")
        self.assertEqual(outcome["metric_path_root_applied"], "MARKET_METRICS_ROOT")

    def test_pre_existing_outcome_keys_are_preserved(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        outcome = self.outcome()
        for key in ("contract", "forecast_id", "status", "result", "start_value", "end_value",
                    "return_pct", "forecast_sha256", "evidence_path", "evidence_sha256",
                    "evidence_lag_hours", "created_at_utc", "authority"):
            self.assertIn(key, outcome)
        self.assertEqual(outcome["contract"], "MATURED_OUTCOME_v3")
        self.assertEqual(outcome["authority"], {"model_weight_change": False, "portfolio_action": False})

    def test_every_emitted_censor_reason_is_authorised(self):
        cases = [
            ("a", frozen_forecast(forecast_id="a", metric_path="derivatives.absent.value")),
            ("b", frozen_forecast(forecast_id="b", metric_path="spot.BTCUSDT.close")),
            ("c", frozen_forecast(forecast_id="c", unit_contract_version=None, direction="UP")),
            ("d", frozen_forecast(forecast_id="d", source_candidate_id=None)),
        ]
        for _, forecast in cases:
            self.write_forecast(forecast)
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0), spot_legacy={}))
        self.mature("2026-08-12T12:00:00Z")
        seen = set()
        for forecast_id, _ in cases:
            outcome = self.outcome(forecast_id)
            self.assertIsNotNone(outcome, forecast_id)
            self.assertEqual(outcome["status"], "CENSORED", forecast_id)
            seen.add(outcome["reason"])
        self.assertTrue(seen <= AUTHORISED_CENSOR_REASONS, f"unauthorised reason emitted: {seen - AUTHORISED_CENSOR_REASONS}")
        self.assertIn("EVIDENCE_NAMESPACE_UNAVAILABLE", seen)
        self.assertIn("METRIC_PATH_ROOT_UNDECLARED", seen)


class IntegrationTests(LoopHarness):
    def test_metric_path_regression_freeze_then_reload_then_mature(self):
        """R3-15 required regression test, all five steps.

        1 freeze a known metric from a current-shaped capture
        2 persist its canonical metric path
        3 reload the forecast independently, from disk, in a new process
        4 mature it using the canonical resolver
        5 prove the exact expected value is returned
        """
        import importlib.util
        spec = importlib.util.spec_from_file_location("metric_resolver", ROOT / "scripts" / "lib" / "metric_resolver.py")
        mr = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mr)

        # 1 - read the metric at freeze time exactly as the producer does.
        freeze_capture = capture("2026-08-10T00:00:00Z", derivatives=derivatives(63004.9))
        relative = "derivatives.BTC-USDT-SWAP.mark_price.mark_price"
        at_freeze = mr.resolve(freeze_capture, relative, mr.MARKET_METRICS_ROOT)
        self.assertTrue(at_freeze.ok)

        # 2 - persist the canonical path plus its declared root.
        forecast = frozen_forecast(metric_path=mr.canonical_path(relative),
                                   metric_path_root=mr.CAPTURE_DOCUMENT_ROOT,
                                   start_value=at_freeze.value, direction="RANGE",
                                   threshold_pct=None, range_lower_pct=-1.0, range_upper_pct=1.0)
        self.write_forecast(forecast)

        # 3 + 4 - a separate process reloads it from disk and matures it.
        maturity_capture = capture("2026-08-11T01:00:00Z", derivatives=derivatives(63034.6))
        self.write_evidence("e1.json", maturity_capture)
        result = self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)

        # 5 - the exact value read at freeze time is the value dereferenced now.
        outcome = self.outcome()
        self.assertEqual(outcome["status"], "MATURED")
        self.assertEqual(outcome["start_value"], 63004.9)
        self.assertEqual(outcome["end_value"], 63034.6)
        self.assertEqual(outcome["metric_path_root_applied"], "CAPTURE_DOCUMENT_ROOT")
        # And the forecast file itself is untouched by maturation.
        self.assertEqual(json.loads((self.root / "f" / f"{forecast['forecast_id']}.json").read_text()), forecast)


class WindowGuardTests(LoopHarness):
    def test_no_evidence_is_not_censored_while_the_window_is_open(self):
        """F4 - the defect that permanently censored 14 real forecasts."""
        self.write_forecast(frozen_forecast())
        result = self.mature("2026-08-11T02:00:00Z")  # due + 2h, window is 24h
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIsNone(self.outcome(), "a permanent censor was written before the window closed")
        self.assertEqual(json.loads(result.stdout)["pending"], 1)

    def test_no_evidence_is_censored_once_the_window_has_closed(self):
        """F3 - the window is honoured, never enlarged."""
        self.write_forecast(frozen_forecast())
        result = self.mature("2026-08-12T00:00:01Z")  # due + 24h + 1s
        self.assertEqual(result.returncode, 0, result.stderr)
        outcome = self.outcome()
        self.assertEqual(outcome["status"], "CENSORED")
        self.assertEqual(outcome["reason"], "NO_EVIDENCE_WITHIN_MAX_LAG")

    def test_window_boundary_is_inclusive_and_not_widened(self):
        self.write_forecast(frozen_forecast())
        # Exactly at due + 24h the window is still open.
        self.assertEqual(self.mature("2026-08-12T00:00:00Z").returncode, 0)
        self.assertIsNone(self.outcome())
        # Evidence one second past the window is never selected.
        self.write_evidence("late.json", capture("2026-08-12T00:00:01Z", derivatives=derivatives(999.0)))
        self.mature("2026-08-13T00:00:00Z")
        outcome = self.outcome()
        self.assertEqual(outcome["reason"], "NO_EVIDENCE_WITHIN_MAX_LAG")
        self.assertNotIn("end_value", outcome)

    def test_present_evidence_still_matures_immediately(self):
        # The guard defers only the absence case; a deterministic earliest-eligible
        # capture is not made to wait.
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T00:30:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-11T01:00:00Z")
        self.assertEqual(self.outcome()["status"], "MATURED")


class MutablePointerTests(LoopHarness):
    def test_latest_pointer_is_never_selected_as_evidence(self):
        self.write_forecast(frozen_forecast())
        # LATEST.json is the earliest eligible file by timestamp; it must be skipped
        # in favour of the immutable dated capture.
        self.write_evidence("LATEST.json", capture("2026-08-11T00:10:00Z", derivatives=derivatives(500.0)))
        self.write_evidence("dated.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        outcome = self.outcome()
        self.assertEqual(outcome["status"], "MATURED")
        self.assertNotIn("LATEST.json", outcome["evidence_path"])
        self.assertEqual(outcome["end_value"], 102.0)

    def test_a_lone_latest_pointer_does_not_count_as_evidence(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("LATEST.json", capture("2026-08-11T00:10:00Z", derivatives=derivatives(500.0)))
        self.mature("2026-08-12T00:00:01Z")
        self.assertEqual(self.outcome()["reason"], "NO_EVIDENCE_WITHIN_MAX_LAG")


class FailureInjectionTests(LoopHarness):
    def _censor(self, forecast, evidence_metrics, now="2026-08-12T12:00:00Z"):
        self.write_forecast(forecast)
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", **evidence_metrics))
        result = self.mature(now)
        self.assertEqual(result.returncode, 0, result.stderr)
        return self.outcome(forecast["forecast_id"])

    def test_f1_metric_genuinely_absent(self):
        outcome = self._censor(frozen_forecast(metric_path="derivatives.BTC-USDT-SWAP.mark_price.absent"),
                               {"derivatives": derivatives(102.0)})
        self.assertEqual(outcome["reason"], "METRIC_UNAVAILABLE")

    def test_f2_namespace_present_but_emptied(self):
        outcome = self._censor(frozen_forecast(metric_path="spot.BTCUSDT.close"),
                               {"derivatives": derivatives(102.0), "spot_legacy": {}})
        self.assertEqual(outcome["reason"], "EVIDENCE_NAMESPACE_UNAVAILABLE")

    def test_f5_non_numeric_metric(self):
        outcome = self._censor(frozen_forecast(metric_path="meta.label"), {"meta": {"label": "one hundred"}})
        self.assertEqual(outcome["reason"], "METRIC_UNAVAILABLE")

    def test_f6_target_unit_ambiguity_still_quarantines(self):
        outcome = self._censor(frozen_forecast(unit_contract_version=None, direction="UP"),
                               {"derivatives": derivatives(102.0)})
        self.assertEqual(outcome["reason"], "LEGACY_V1_TARGET_UNIT_AMBIGUOUS")

    def test_f7_malformed_path_exits_zero_without_traceback(self):
        self.write_forecast(frozen_forecast(metric_path="a..b"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        result = self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(self.outcome()["reason"], "METRIC_UNAVAILABLE")

    def test_f8_schema_drift_between_freeze_and_maturity(self):
        # Frozen while market_metrics.spot existed; matured after the rename.
        outcome = self._censor(frozen_forecast(metric_path="spot.BTCUSDT.close"),
                               {"microstructure": {"symbols": {"BTCUSDT": {"midpoint": 64388.8}}}, "spot_legacy": {}})
        self.assertEqual(outcome["reason"], "EVIDENCE_NAMESPACE_UNAVAILABLE")
        # The neighbouring microstructure value must never be substituted.
        self.assertNotIn("end_value", outcome)

    def test_f9_unreadable_evidence_is_skipped_not_fatal(self):
        self.write_forecast(frozen_forecast())
        (self.root / "e" / "broken.json").write_text("{not json")
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        result = self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.outcome()["status"], "MATURED")

    def test_unknown_declared_root_fails_closed(self):
        self.write_forecast(frozen_forecast(metric_path_root="SOME_OTHER_ROOT"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        result = self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(result.returncode, 2, "an unsupported root contract must not be silently coerced")
        self.assertIsNone(self.outcome())


class IdempotencyTests(LoopHarness):
    def test_i1_repeated_maturation_is_byte_identical(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        first = (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes()
        self.mature("2026-08-13T18:00:00Z")  # different wall clock
        self.assertEqual(first, (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes())

    def test_f10_duplicate_invocation_creates_no_second_outcome(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        for _ in range(3):
            self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(len(list((self.root / "o").glob("*.json"))), 1)

    def test_f11_concurrent_equivalent_invocation_yields_one_canonical_outcome(self):
        """Two runs from the same base state, as a shared writer lock would serialise
        them. The second observes the first's file and writes nothing."""
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        first = self.mature("2026-08-12T12:00:00Z")
        snapshot = (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes()
        second = self.mature("2026-08-12T12:00:05Z")
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(json.loads(second.stdout)["matured"], 0)
        self.assertEqual(snapshot, (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes())
        self.assertEqual(len(list((self.root / "o").glob("*.json"))), 1)

    def test_a_censored_outcome_is_never_upgraded_in_place(self):
        self.write_forecast(frozen_forecast(metric_path="spot.BTCUSDT.close"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", spot_legacy={}))
        self.mature("2026-08-12T12:00:00Z")
        censored = (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes()
        # Even if a later capture would resolve, the recorded outcome is immutable.
        self.write_evidence("e2.json", capture("2026-08-11T02:00:00Z", spot={"BTCUSDT": {"close": 102.0}}))
        self.mature("2026-08-13T12:00:00Z")
        self.assertEqual(censored, (self.root / "o" / "EXP-FC-test0000000000000000.json").read_bytes())


class LedgerTests(LoopHarness):
    def _build_ledger(self):
        output = self.root / "MODEL_CALIBRATION_LEDGER.csv"
        result = subprocess.run(
            [sys.executable, str(LEDGER), "--forecast-root", str(self.root / "f"),
             "--outcome-root", str(self.root / "o"), "--output", str(output)],
            capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout), output.read_text()

    def test_censored_rows_are_not_counted_as_scored(self):
        self.write_forecast(frozen_forecast(forecast_id="hit"))
        self.write_forecast(frozen_forecast(forecast_id="cens", metric_path="spot.BTCUSDT.close"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0), spot_legacy={}))
        self.mature("2026-08-12T12:00:00Z")
        summary, csv_text = self._build_ledger()
        self.assertEqual(summary["scored_count"], 1)
        self.assertEqual(summary["censored_count"], 1)
        self.assertEqual(summary["ledger_row_count"], 2)
        # Censored rows stay visible in the ledger; only the counter changed.
        self.assertIn("CENSORED", csv_text)
        self.assertIn("MATURED", csv_text)

    def test_a_fully_censored_lane_reports_zero_scored(self):
        self.write_forecast(frozen_forecast(metric_path="spot.BTCUSDT.close"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", spot_legacy={}))
        self.mature("2026-08-12T12:00:00Z")
        summary, _ = self._build_ledger()
        self.assertEqual(summary["scored_count"], 0)
        self.assertEqual(summary["censored_count"], 1)

    def test_backward_compatible_ledger_columns(self):
        self.write_forecast(frozen_forecast())
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        _, csv_text = self._build_ledger()
        header = csv_text.splitlines()[0]
        self.assertEqual(header, "scored_at_utc,model,task,prompt_sha256,forecast_id,metric_path,horizon_days,"
                                 "outcome,result,hit,return_pct,forecast_sha256,evidence_sha256")

    def test_v2_and_v3_outcome_contracts_are_both_read(self):
        self.write_forecast(frozen_forecast(forecast_id="old"))
        (self.root / "o" / "old.json").write_text(json.dumps({
            "contract": "MATURED_OUTCOME_v2", "forecast_id": "old", "status": "MATURED",
            "result": "MISS", "created_at_utc": "2026-08-11T02:00:00Z"}))
        summary, _ = self._build_ledger()
        self.assertEqual(summary["scored_count"], 1)


class BackwardCompatibilityTests(LoopHarness):
    def test_legacy_forecasts_without_a_declared_root_still_mature(self):
        """The 131 forecasts already on disk carry no metric_path_root."""
        self.write_forecast(frozen_forecast())  # source_candidate_id set, no metric_path_root
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        outcome = self.outcome()
        self.assertEqual(outcome["status"], "MATURED")
        self.assertEqual(outcome["metric_path_root_applied"], "MARKET_METRICS_ROOT")

    def test_new_and_legacy_forecasts_coexist_in_one_run(self):
        self.write_forecast(frozen_forecast(forecast_id="legacy"))
        self.write_forecast(frozen_forecast(
            forecast_id="modern",
            metric_path="market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price",
            metric_path_root="CAPTURE_DOCUMENT_ROOT"))
        self.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(102.0)))
        self.mature("2026-08-12T12:00:00Z")
        self.assertEqual(self.outcome("legacy")["end_value"], 102.0)
        self.assertEqual(self.outcome("modern")["end_value"], 102.0)
        self.assertEqual(self.outcome("legacy")["metric_path_root_applied"], "MARKET_METRICS_ROOT")
        self.assertEqual(self.outcome("modern")["metric_path_root_applied"], "CAPTURE_DOCUMENT_ROOT")

    def test_classification_semantics_are_unchanged(self):
        cases = [
            ("up_hit", dict(direction="UP", threshold_pct=1.0), 102.0, "HIT"),
            ("up_miss", dict(direction="UP", threshold_pct=1.0), 100.5, "MISS"),
            ("down_hit", dict(direction="DOWN", threshold_pct=1.0), 98.0, "HIT"),
            ("down_miss", dict(direction="DOWN", threshold_pct=1.0), 99.5, "MISS"),
            ("range_hit", dict(direction="RANGE", threshold_pct=None, range_lower_pct=-1.0, range_upper_pct=1.0), 100.5, "HIT"),
            ("range_miss", dict(direction="RANGE", threshold_pct=None, range_lower_pct=-1.0, range_upper_pct=1.0), 102.0, "MISS"),
        ]
        for name, spec, end_value, expected in cases:
            with self.subTest(name=name):
                harness = LoopHarness()
                harness.setUp()
                harness.write_forecast(frozen_forecast(forecast_id=name, **spec))
                harness.write_evidence("e1.json", capture("2026-08-11T01:00:00Z", derivatives=derivatives(end_value)))
                harness.mature("2026-08-12T12:00:00Z")
                self.assertEqual(harness.outcome(name)["result"], expected)
                harness._tmp.cleanup()


if __name__ == "__main__":
    unittest.main()
