from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.api_agent import check_director_freshness as freshness


NOW = datetime(2026, 9, 9, 0, 0, tzinfo=timezone.utc)


def write_context(path: Path, run_id: str = "RUN_NEW", captured_at_utc: object = "2026-09-08T23:00:00Z",
                  market_delta: bool = True) -> None:
    # Since #1734 a new owner run is Director-eligible only with a material market
    # delta (comparable numeric metrics and DELTA_READY); the fixture states it explicitly.
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"latest_capture": {"run_id": run_id, "captured_at_utc": captured_at_utc}}
    if market_delta:
        doc.update({"coverage": {"comparable_numeric_metrics": 3}, "delta_status": "DELTA_READY"})
    path.write_text(json.dumps(doc))


class DirectorFreshnessAuditTests(unittest.TestCase):
    def test_fresh_valid_unseen_owner_run_is_eligible(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context)
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "NEW_OWNER_RUN_FRESH_SOURCE")
            self.assertTrue(result["source_timestamp_valid"])
            self.assertTrue(result["identity_unseen"])

    def test_duplicate_fresh_owner_run_is_noop(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, "RUN_DUP")
            write_context(root / "outputs" / "old" / "context.json", "RUN_DUP", "2026-09-08T22:00:00Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "OWNER_RUN_AND_NEWS_ALREADY_ANALYZED")
            self.assertFalse(result["identity_unseen"])

    def test_unseen_owner_run_without_market_delta_is_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, market_delta=False)
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["identity_unseen"])
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "OWNER_RUN_AND_NEWS_ALREADY_ANALYZED")

    def test_unseen_ancient_capture_is_not_fresh(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, "SYNTHETIC_UNSEEN_OLD", "2026-08-08T14:01:34Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_SOURCE_STALE")
            self.assertGreater(result["source_age_seconds"], freshness.OWNER_CAPTURE_CADENCE.total_seconds())

    def test_missing_or_naive_source_timestamp_fails_closed(self) -> None:
        for raw_timestamp in (None, "", "2026-09-08T23:00:00", "not-a-time"):
            with self.subTest(raw_timestamp=raw_timestamp), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                context = root / "context.json"
                write_context(context, captured_at_utc=raw_timestamp)
                result = freshness.evaluate(context, root / "outputs", NOW)
                self.assertFalse(result["fresh_ready"])
                self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_TIMESTAMP_INVALID_OR_MISSING")
                self.assertFalse(result["source_timestamp_valid"])

    def test_future_source_timestamp_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, captured_at_utc="2026-09-09T00:00:01Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertFalse(result["fresh_ready"])
            self.assertEqual(result["fresh_reason"], "CURRENT_CAPTURE_TIMESTAMP_FUTURE")

    def test_owner_cadence_boundary_is_not_tightened(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context, captured_at_utc="2026-09-08T20:00:00Z")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["fresh_ready"])
            self.assertEqual(result["source_age_seconds"], 14400.0)

    def write_skip(self, path: Path, **receipt_updates):
        write_context(path, market_delta=False)
        out = {"status": "BLOCKED", "summary": "Daily Director skipped because no new eligible owner evidence required analysis.", "evidence_for": [],
               "evidence_against": [], "uncertainties": ["SKIPPED_NO_DELTA"],
               "hypotheses": [], "forecast_candidates": []}
        def digest(value):
            return hashlib.sha256((json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()).hexdigest()
        rec = {"contract": "API_AGENT_RECEIPT_v3", "task": "DAILY_DIRECTOR_SHADOW",
               "model": "gpt-5.6-luna", "reasoning_effort": "medium", "created_unix": 1788912000,
               "status": "SKIPPED_NO_DELTA", "context_hash": digest(json.loads(path.read_text())),
               "output_hash": digest(out), "response_id": None, "prompt_hash": None,
               "input_tokens": 0, "output_tokens": 0, "estimated_cost_usd": 0.0,
               "authority": {"portfolio_action": False, "framework_state_change": False,
                             "model_weight_change": False, "canonical_promotion": False}}
        rec.update(receipt_updates)
        (path.parent / "DAILY_DIRECTOR_OUTPUT.json").write_text(json.dumps(out))
        (path.parent / "DAILY_DIRECTOR_RECEIPT.json").write_text(json.dumps(rec))

    def test_documented_no_delta_skip_is_not_completed_analysis(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            write_context(context)
            self.write_skip(root / "outputs" / "skip" / "context.json")
            result = freshness.evaluate(context, root / "outputs", NOW)
            self.assertTrue(result["identity_unseen"])
            self.assertTrue(result["fresh_ready"])
            # A second, ambiguous or completed record still blocks a retry.
            write_context(root / "outputs" / "other" / "context.json")
            self.assertFalse(freshness.evaluate(context, root / "outputs", NOW)["fresh_ready"])

    def test_no_delta_skip_does_not_override_current_freshness_or_delta(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            context = root / "context.json"
            self.write_skip(root / "outputs" / "skip" / "context.json")
            write_context(context, market_delta=False)
            self.assertFalse(freshness.evaluate(context, root / "outputs", NOW)["fresh_ready"])
            write_context(context, captured_at_utc="2026-09-08T19:59:59Z")
            self.assertFalse(freshness.evaluate(context, root / "outputs", NOW)["fresh_ready"])

    def test_ambiguous_paid_or_already_analyzed_receipt_never_reopens_id(self):
        variants = [
            {"status": "SKIPPED_OWNER_RUN_ALREADY_ANALYZED"},
            {"status": "PASS"}, {"status": "SKIPPED_BUDGET_GUARD"},
            {"response_id": "resp_paid"}, {"response_ids": ["resp_paid"]}, {"attempt_count": 1},
            {"estimated_cost_usd": 0.001}, {"input_tokens": 1}, {"input_tokens": False},
            {"prompt_hash": "a" * 64}, {"context_hash": "a" * 64}, {"output_hash": "b" * 64},
            {"authority": {}}, {"task": "DAILY_CONFLICT_REVIEW"},
            {"request_hash": "a" * 64}, {"forecast_candidate_count": 2},
            {"model": "unknown"}, {"reasoning_effort": "high"}, {"created_unix": True},
            {"created_unix": 0}, {"authority": {"portfolio_action": False,
                "framework_state_change": False, "model_weight_change": False,
                "canonical_promotion": False, "automatic_trade": True}},
        ]
        for change in variants:
            with self.subTest(change=change), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                context = root / "context.json"
                write_context(context)
                self.write_skip(root / "outputs" / "skip" / "context.json", **change)
                self.assertFalse(freshness.evaluate(context, root / "outputs", NOW)["fresh_ready"])

    def test_missing_tampered_or_duplicate_receipt_keeps_seen_identity(self):
        for fault in ("missing", "tampered_output", "duplicate_json", "invalid"):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as raw:
                root = Path(raw)
                context = root / "context.json"
                write_context(context)
                path = root / "outputs" / "skip" / "context.json"
                self.write_skip(path)
                rec = path.parent / "DAILY_DIRECTOR_RECEIPT.json"
                if fault == "missing":
                    rec.unlink()
                elif fault == "tampered_output":
                    (path.parent / "DAILY_DIRECTOR_OUTPUT.json").write_text('{"status":"PASS"}')
                elif fault == "duplicate_json":
                    rec.write_text(rec.read_text()[:-1] + ', "status":"SKIPPED_NO_DELTA"}')
                else:
                    rec.write_text("{")
                self.assertFalse(freshness.evaluate(context, root / "outputs", NOW)["fresh_ready"])


if __name__ == "__main__":
    unittest.main()
