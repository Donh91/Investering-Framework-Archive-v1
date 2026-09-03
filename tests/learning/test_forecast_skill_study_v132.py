#!/usr/bin/env python3
from __future__ import annotations

import inspect
import json
import math
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "tests/learning" in str(Path(__file__)) else Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts" / "lib" if (ROOT / "scripts" / "lib").exists() else ROOT))
sys.path.insert(0, str(ROOT / "scripts" / "learning" if (ROOT / "scripts" / "learning").exists() else ROOT))

from forecast_b1_source_owner import fetch_daily_history, okx_url  # noqa: E402
from forecast_study_v1_3_2 import (  # noqa: E402
    ACTIVATION,
    ADMISSION,
    EXACT_SETTLEMENT,
    OWNER_CLASS,
    REVALIDATION,
    STUDY_ID,
    accrual_gates,
    admission_for,
    b1_climatology,
    confirmatory,
    confirmatory_readiness,
    digest,
    digest_bytes,
    iso,
    parse_dt,
    t_ppf,
    technical_revalidation,
    validate_activation,
    validate_source_candidate_binding,
    verify_self_hash,
    with_self_hash,
)

UTC = timezone.utc
HEX = "a" * 64


def fixture():
    prereg = b'{"contract":"FORECAST_SKILL_PREREGISTRATION_v1_3_1"}\n'
    erratum = b'{"contract":"FORECAST_SKILL_PREREGISTRATION_v1_3_2_ERRATUM"}\n'
    activation = {
        "contract": ACTIVATION,
        "status": "ACTIVE",
        "study_id": STUDY_ID,
        "activation_recorded_at_utc": "2026-09-03T21:00:00Z",
        "implementation_main_sha": "1" * 40,
        "implementation_readback_at_utc": "2026-09-03T20:55:00Z",
        "cohort_start_utc": "2026-09-04T00:00:00Z",
        "cohort_end_utc_exclusive": "2027-05-02T00:00:00Z",
        "preregistration_sha256": digest_bytes(prereg),
        "endpoint_erratum_sha256": digest_bytes(erratum),
        "outcome_data_read": False,
    }
    activation = with_self_hash(activation, "activation_payload_sha256")
    forecast = {
        "contract": "FROZEN_FORECAST_v1",
        "forecast_id": "ff1",
        "candidate_id": "c1",
        "frozen_at_utc": "2026-09-04T01:00:00Z",
        "outcome_due_utc": "2026-09-05T01:00:00Z",
        "horizon_days": 1,
        "metric_path": "spot.BTCUSDT.close",
        "direction": "UP",
        "threshold_pct": 1.0,
        "settlement_contract_version": EXACT_SETTLEMENT,
        "ratification_outcome_blind": True,
        "ratification_contract": "FORECAST_RATIFICATION_PACKET_v2",
        "candidate_sha256": HEX,
        "ratification_sha256": "b" * 64,
        "source_output_sha256": "c" * 64,
        "prompt_sha256": "d" * 64,
        "context_sha256": "e" * 64,
    }
    candidate = {
        "contract": "FORECAST_CANDIDATE_v1",
        "candidate_id": "c1",
        "created_at_utc": "2026-09-04T00:15:00Z",
        "source_output_sha256": "c" * 64,
        "source_receipt_sha256": "f" * 64,
        "source_freshness_contract": "FORECAST_SOURCE_TEMPORAL_PROVENANCE_v1",
        "source_freshness_cutover_commit_sha": "a64d2770e5a81549c86c8c14a4a6ca2f3e6c577b",
        "source_output_created_at_utc": "2026-09-04T00:00:00Z",
        "source_output_age_at_materialization_seconds": 900.0,
    }
    forecast["candidate_sha256"] = digest(candidate)
    b1 = {
        "contract": "B1_CLIMATOLOGY_FREEZE_v1",
        "freeze_utc": forecast["frozen_at_utc"],
        "horizon_days": 1,
        "direction": "UP",
        "threshold_pct": 1.0,
        "p_clim": 0.3,
        "admissible_event_count": 180,
        "last_event_end_close_utc": "2026-09-03T00:00:00Z",
        "no_lookahead": True,
    }
    return prereg, erratum, activation, forecast, b1, candidate


def make_200():
    activation = {"contract": ACTIVATION, "status": "ACTIVE", "cohort_start_utc": "2026-01-01T00:00:00Z", "cohort_end_utc_exclusive": "2026-08-29T00:00:00Z"}
    admissions, revalidations, outcomes = [], {}, {}
    for i in range(200):
        day = 0 if i < 10 else (i - 10) % 190
        due = datetime(2026, 1, 2, tzinfo=UTC) + timedelta(days=day)
        freeze = due - timedelta(days=1)
        fid = f"f{i}"
        forecast_hash = (f"{i:064x}")[-64:]
        admission = {"contract": ADMISSION, "status": "ADMITTED", "forecast_id": fid, "admission_id": "a" + fid, "forecast_sha256": forecast_hash, "outcome_due_utc": iso(due), "outcome_due_day_utc": due.date().isoformat(), "freeze_day_utc": freeze.date().isoformat(), "p_clim": 0.5}
        admission = with_self_hash(admission, "admission_sha256")
        admissions.append(admission)
        revalidation = {"contract": REVALIDATION, "forecast_id": fid, "admission_id": admission["admission_id"], "status": "PASS", "outcome_data_read": False}
        revalidations[fid] = with_self_hash(revalidation, "revalidation_sha256")
        outcomes[fid] = {"contract": "MATURED_OUTCOME_v3", "status": "MATURED", "scientific_score_eligible": True, "forecast_sha256": forecast_hash, "result": "HIT" if i < 10 else "MISS"}
    return activation, admissions, revalidations, outcomes


class ForecastSkillStudyV132Tests(unittest.TestCase):
    def test_source_temporal_candidate_binding(self):
        _p, _e, _a, forecast, _b1, candidate = fixture(); binding = validate_source_candidate_binding(candidate, forecast); self.assertEqual(binding["source_freshness_contract"], "FORECAST_SOURCE_TEMPORAL_PROVENANCE_v1"); self.assertEqual(binding["candidate_record_sha256"], forecast["candidate_sha256"])
    def test_source_temporal_candidate_hash_mutation_rejected(self):
        _p, _e, _a, forecast, _b1, candidate = fixture(); candidate = dict(candidate); candidate["source_output_age_at_materialization_seconds"] = 901.0
        with self.assertRaisesRegex(ValueError, "SOURCE_CANDIDATE_HASH_MISMATCH"): validate_source_candidate_binding(candidate, forecast)
    def test_source_temporal_candidate_stale_rejected(self):
        _p, _e, _a, forecast, _b1, candidate = fixture(); candidate = dict(candidate); candidate["source_output_created_at_utc"] = "2026-09-03T20:00:00Z"; candidate["source_output_age_at_materialization_seconds"] = 15300.0; forecast = dict(forecast); forecast["candidate_sha256"] = digest(candidate)
        with self.assertRaisesRegex(ValueError, "SOURCE_OUTPUT_STALE_OR_FUTURE_AT_MATERIALIZATION"): validate_source_candidate_binding(candidate, forecast)
    def test_b1_no_lookahead_and_exact_selected_input(self):
        base = datetime(2025, 1, 1, tzinfo=UTC); bars = [{"close_utc": iso(base + timedelta(days=i)), "close": 100 + i * 0.1} for i in range(250)]; freeze = iso(base + timedelta(days=250)); b1 = b1_climatology(bars, freeze, 7, "UP", 1.0); self.assertEqual(b1["admissible_event_count"], 180); self.assertEqual(b1["selected_input_bar_count"], 187); self.assertLess(parse_dt(b1["last_event_end_close_utc"]), parse_dt(freeze)); self.assertTrue(b1["daily_origin_continuity_verified"])
    def test_b1_gap_rejected(self):
        base = datetime(2025, 1, 1, tzinfo=UTC); bars = [{"close_utc": iso(base + timedelta(days=i)), "close": 100 + i} for i in range(200)]; del bars[50]
        with self.assertRaisesRegex(ValueError, "B1_DAILY_HISTORY_GAP"): b1_climatology(bars, iso(base + timedelta(days=220)), 1, "UP", 1.0)
    def test_source_fixture_excludes_post_freeze_and_raw_payload(self):
        freeze = parse_dt("2026-09-04T12:00:00Z"); base = datetime(2026, 1, 1, tzinfo=UTC); rows = []
        for i in range(250):
            open_dt = base + timedelta(days=i); close_dt = open_dt + timedelta(days=1) - timedelta(milliseconds=1); rows.append([int(open_dt.timestamp() * 1000), "1", "1", "1", str(100 + i), "1", int(close_dt.timestamp() * 1000)])
        bars, receipt = fetch_daily_history("spot.BTCUSDT.close", iso(freeze), fixture={"kind": "BINANCE", "responses": [rows]}, min_bars=190); self.assertTrue(all(parse_dt(row["close_utc"]) < freeze for row in bars)); self.assertTrue(receipt["daily_continuity_verified"]); self.assertNotIn("raw_utf8", receipt["requests"][0]); self.assertFalse(receipt["outcome_data_read"])
    def test_okx_daily_bar_is_utc_variant(self): self.assertIn("bar=1Dutc", okx_url("BTC-USDT-SWAP", 123))
    def test_activation_valid(self):
        prereg, erratum, activation, *_ = fixture(); start, end = validate_activation(activation, prereg, erratum); self.assertEqual(end - start, timedelta(days=240))
    def test_activation_hash_mutation_rejected(self):
        prereg, erratum, activation, *_ = fixture(); bad = dict(activation); bad["preregistration_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "ACTIVATION_PAYLOAD_SHA256_MISMATCH|PREREGISTRATION_HASH_MISMATCH"): validate_activation(bad, prereg, erratum)
    def test_activation_must_be_recorded_before_start(self):
        prereg, erratum, activation, *_ = fixture(); bad = dict(activation); bad.pop("activation_payload_sha256"); bad["activation_recorded_at_utc"] = bad["cohort_start_utc"]; bad = with_self_hash(bad, "activation_payload_sha256")
        with self.assertRaisesRegex(ValueError, "ACTIVATION_NOT_PROSPECTIVELY_RECORDED"): validate_activation(bad, prereg, erratum)
    def test_precohort_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture(); forecast = {**forecast, "frozen_at_utc": "2026-09-03T01:00:00Z", "outcome_due_utc": "2026-09-04T01:00:00Z"}; b1 = {**b1, "freeze_utc": forecast["frozen_at_utc"], "last_event_end_close_utc": "2026-09-02T00:00:00Z"}
        with self.assertRaisesRegex(ValueError, "OUTSIDE_COHORT"): admission_for(forecast, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-03T01:01:00Z")
    def test_postcohort_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture(); forecast = {**forecast, "frozen_at_utc": "2027-05-02T01:00:00Z", "outcome_due_utc": "2027-05-03T01:00:00Z"}; b1 = {**b1, "freeze_utc": forecast["frozen_at_utc"], "last_event_end_close_utc": "2027-05-01T00:00:00Z"}
        with self.assertRaisesRegex(ValueError, "OUTSIDE_COHORT"): admission_for(forecast, OWNER_CLASS, activation, prereg, erratum, b1, "2027-05-02T01:01:00Z")
    def test_range_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "F1_DIRECTIONAL_ONLY"): admission_for({**forecast, "direction": "RANGE"}, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_wrong_class_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "WRONG_EVIDENCE_CLASS"): admission_for(forecast, "AUTOMATED_SCIENTIFIC_EXPERIMENT_SHADOW_v1", activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_non_exact_settlement_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "EXACT_SETTLEMENT_REQUIRED"): admission_for({**forecast, "settlement_contract_version": "legacy"}, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_outcome_blind_ratification_required(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "OUTCOME_BLIND_RATIFICATION_REQUIRED"): admission_for({**forecast, "ratification_outcome_blind": False}, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_source_output_hash_required(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "SOURCE_OUTPUT_SHA256_REQUIRED"): admission_for({**forecast, "source_output_sha256": None}, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_due_mutation_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture()
        with self.assertRaisesRegex(ValueError, "DUE_TIME_HORIZON_MISMATCH"): admission_for({**forecast, "outcome_due_utc": "2026-09-06T01:00:00Z"}, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
    def test_admission_self_hash(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture(); admission = admission_for(forecast, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z"); verify_self_hash(admission, "admission_sha256")
    def test_revalidation_signature_has_no_outcome_argument(self): self.assertNotIn("outcome", inspect.signature(technical_revalidation).parameters); self.assertNotIn("evidence", inspect.signature(technical_revalidation).parameters)
    def test_revalidation_before_due_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture(); admission = admission_for(forecast, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
        with self.assertRaisesRegex(ValueError, "OUTCOME_DUE_NOT_REACHED"): technical_revalidation(admission, forecast, activation, prereg, erratum, "2026-09-04T12:00:00Z")
    def test_revalidation_forecast_drift_rejected(self):
        prereg, erratum, activation, forecast, b1, _candidate = fixture(); admission = admission_for(forecast, OWNER_CLASS, activation, prereg, erratum, b1, "2026-09-04T01:01:00Z")
        with self.assertRaisesRegex(ValueError, "FORECAST_HASH_DRIFT"): technical_revalidation(admission, {**forecast, "threshold_pct": 2.0}, activation, prereg, erratum, "2026-09-05T02:00:00Z")
    def test_before_cohort_end_never_reads_outcomes(self):
        activation, admissions, revalidations, _ = make_200(); result = confirmatory(admissions, revalidations, {"evil": object()}, activation, "2026-03-01T00:00:00Z"); self.assertEqual(result["status"], "ACCRUING"); self.assertFalse(result["outcome_data_read"])
    def test_day_weighted_endpoint_not_row_weighted(self):
        activation, admissions, revalidations, outcomes = make_200(); result = confirmatory(admissions, revalidations, outcomes, activation, "2026-09-01T00:00:00Z"); row_mean = sum((1 if i < 10 else 0) - 0.5 for i in range(200)) / 200; self.assertTrue(result["confirmatory_test_executed"]); self.assertEqual(result["endpoint_weighting"], "EACH_OBSERVED_OUTCOME_DUE_CALENDAR_DAY_EQUAL_WEIGHT"); self.assertGreater(abs(result["theta_hat"] - row_mean), 1e-3); verify_self_hash(result, "result_sha256")
    def test_missing_outcome_blocks_confirmatory(self):
        activation, admissions, revalidations, outcomes = make_200(); outcomes.pop("f0"); result = confirmatory(admissions, revalidations, outcomes, activation, "2026-09-01T00:00:00Z"); self.assertEqual(result["status"], "INSUFFICIENT_PROSPECTIVE_EVIDENCE"); self.assertEqual(result["reason"], "OUTCOME_UNAVAILABLE"); self.assertFalse(result["confirmatory_test_executed"])
    def test_wrong_outcome_forecast_hash_blocks(self):
        activation, admissions, revalidations, outcomes = make_200(); outcomes["f0"]["forecast_sha256"] = "f" * 64; result = confirmatory(admissions, revalidations, outcomes, activation, "2026-09-01T00:00:00Z"); self.assertEqual(result["reason"], "OUTCOME_FORECAST_BINDING_MISMATCH")
    def test_n_gate(self):
        _, admissions, _, _ = make_200(); gates, _ = accrual_gates(admissions[:199]); self.assertFalse(gates["min_admitted_F1_rows"])
    def test_unique_due_day_gate(self):
        _, admissions, _, _ = make_200()
        for i, admission in enumerate(admissions):
            day = datetime(2026, 1, 2, tzinfo=UTC) + timedelta(days=i % 80); admission["outcome_due_day_utc"] = day.date().isoformat(); admission["outcome_due_utc"] = iso(day)
        gates, _ = accrual_gates(admissions); self.assertFalse(gates["min_UNIQUE_OUTCOME_DUE_DAYS"])
    def test_unique_freeze_day_gate(self):
        _, admissions, _, _ = make_200()
        for i, admission in enumerate(admissions): admission["freeze_day_utc"] = (datetime(2026, 1, 1) + timedelta(days=i % 40)).date().isoformat()
        gates, _ = accrual_gates(admissions); self.assertFalse(gates["min_UNIQUE_FREEZE_DAYS"])
    def test_due_day_concentration_gate(self):
        _, admissions, _, _ = make_200(); common = admissions[0]["outcome_due_day_utc"]; common_utc = admissions[0]["outcome_due_utc"]
        for admission in admissions[:13]: admission["outcome_due_day_utc"] = common; admission["outcome_due_utc"] = common_utc
        gates, _ = accrual_gates(admissions); self.assertFalse(gates["max_share_rows_on_any_OUTCOME_DUE_calendar_day"])
    def test_28_day_concentration_gate(self):
        _, admissions, _, _ = make_200(); origin = datetime(2026, 1, 2, tzinfo=UTC)
        for i, admission in enumerate(admissions[:47]):
            day = origin + timedelta(days=i % 28); admission["outcome_due_day_utc"] = day.date().isoformat(); admission["outcome_due_utc"] = iso(day)
        gates, _ = accrual_gates(admissions); self.assertFalse(gates["max_share_rows_in_any_28_calendar_day_block"])
    def test_failed_revalidation_blocks_before_outcome_read(self):
        activation, admissions, revalidations, _ = make_200(); bad = dict(revalidations["f0"]); bad.pop("revalidation_sha256"); bad["status"] = "FAIL"; revalidations["f0"] = with_self_hash(bad, "revalidation_sha256"); result = confirmatory_readiness(admissions, revalidations, activation, "2026-09-01T00:00:00Z"); self.assertEqual(result["reason"], "TECHNICAL_REVALIDATION_FAILURE"); self.assertFalse(result["outcome_data_read"])
    def test_student_t_reference(self): self.assertAlmostEqual(t_ppf(0.975, 8), 2.3060041352, places=6)


if __name__ == "__main__": unittest.main(verbosity=2)
