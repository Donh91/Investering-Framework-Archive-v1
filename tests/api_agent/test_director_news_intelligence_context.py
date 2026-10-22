"""Regression tests for the noncanonical news -> Director readback chain."""
from __future__ import annotations

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.api_agent.augment_director_news_intelligence_context import news_intelligence
from scripts.api_agent.check_director_freshness import evaluate

NOW = datetime(2026, 10, 22, 10, 0, tzinfo=timezone.utc)


def fixture(root, *, failed=False, verified=True, future=False, forged=False):
    pointer = root / "LATEST.json"
    row_path = root / "2026-10-22.json"
    event = {
        "event_id": "EVT_OCC_GENIUS_FINAL",
        "event_family_id": "FAM_GENIUS_ACT",
        "title": "OCC finalizes GENIUS Act stablecoin rule",
        "event_time_utc": "2026-10-23T08:00:00Z" if future else "2026-10-22T08:00:00Z",
        "verification_status": "PRIMARY_SOURCE_VERIFIED",
        "classification": "STRUCTURAL",
        "source_receipts": [{
            "role": "PRIMARY", "status": "PASS",
            "url": "https://www.occ.gov/news-issuances/bulletins/2026/bulletin-2026-50.html",
        }],
    }
    row = {
        "contract": "SITUATION_ROOM_DAILY_OWNER_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "run_id": "SRDO_TEST",
        "observation_date_utc": "2026-10-22",
        "detection_time_utc": "2026-10-22T09:00:00Z",
        "run_status": "DEGRADED" if failed else "PASS",
        "daily_result": "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY" if failed else "MATERIAL_CATALYSTS_FOUND",
        "source_coverage": {
            "primary_pass": 5, "primary_total": 5,
            "receipts": [
                {"source_id": "SITUATION_ROOM", "status": "FAIL" if failed else "PASS"},
                {"source_id": "OCC", "role": "PRIMARY", "status": "PASS"},
            ],
        },
        "events": [event] if verified else [],
        "current_unverified_discoveries": [],
        "canonical_effect": forged, "market_state_effect": False,
        "portfolio_effect": False,
    }
    row_path.write_text(json.dumps(row))
    pointer.write_text(json.dumps({
        "contract": "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1",
        "run_id": "SRDO_TEST", "observation_date_utc": "2026-10-22",
        "path": str(row_path),
    }))
    return pointer


class NewsDirectorIntegrationTests(unittest.TestCase):
    def test_verified_official_event_is_context_not_trade_permission(self):
        with tempfile.TemporaryDirectory() as td:
            pointer = fixture(Path(td))
            out, paths = news_intelligence(pointer, now=NOW)
            self.assertEqual(out["status"], "READY")
            self.assertEqual(out["verified_count"], 1)
            self.assertTrue(out["news_only_review_eligible"])
            self.assertEqual(out["verified_context"][0]["verification_status"], "PRIMARY_SOURCE_VERIFIED")
            self.assertFalse(out["portfolio_effect"])
            self.assertFalse(out["market_state_effect"])
            self.assertEqual(len(paths), 2)

    def test_failed_discovery_source_is_never_clean_no_news(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(fixture(Path(td), failed=True, verified=False), now=NOW)
            self.assertEqual(out["status"], "DEGRADED_SOURCE_COVERAGE")
            self.assertEqual(out["failed_sources"], ["SITUATION_ROOM"])
            self.assertEqual(out["verified_count"], 0)
            self.assertFalse(out["news_only_review_eligible"])

    def test_independently_primary_verified_event_survives_discovery_failure(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(fixture(Path(td), failed=True), now=NOW)
            self.assertEqual(out["status"], "DEGRADED_SOURCE_COVERAGE")
            self.assertEqual(out["verified_count"], 1)

    def test_future_dated_event_does_not_trigger(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(fixture(Path(td), future=True), now=NOW)
            self.assertEqual(out["verified_count"], 0)
            self.assertFalse(out["news_only_review_eligible"])

    def test_authority_breach_blocks_entire_context(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(fixture(Path(td), forged=True), now=NOW)
            self.assertEqual(out["status"], "BLOCKED_INVALID_OWNER")
            self.assertEqual(out["verified_count"], 0)

    def test_missing_pointer_does_not_fabricate_no_event(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(Path(td) / "unknown", now=NOW)
            self.assertEqual(out["status"], "UNAVAILABLE")
            self.assertEqual(out["verified_count"], 0)

    def test_outside_path_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            pointer = fixture(root)
            (root / "LATEST.json").write_text(json.dumps({
                "contract": "SITUATION_ROOM_DAILY_OWNER_LATEST_POINTER_v1",
                "run_id": "SRDO_TEST", "observation_date_utc": "2026-10-22",
                "path": str(root.parent / "escape.json"),
            }))
            out, _ = news_intelligence(pointer, now=NOW)
            self.assertEqual(out["reason"], "NEWS_OWNER_ROW_OUTSIDE_OWNER_ROOT")

    def test_stale_coverage_stops_news_trigger(self):
        with tempfile.TemporaryDirectory() as td:
            out, _ = news_intelligence(fixture(Path(td)), now=datetime(2026, 10, 24, 10, tzinfo=timezone.utc))
            self.assertEqual(out["status"], "STALE")
            self.assertFalse(out["news_only_review_eligible"])

    def test_news_only_gate_handles_owner_already_seen(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ctx = root / "context.json"
            old = root / "outputs" / "prior"
            old.mkdir(parents=True)
            current = {
                "latest_capture": {"run_id": "CAPTURE_123", "captured_at_utc": "2026-10-22T09:00:00Z"},
                "news_intelligence": {
                    "news_only_review_eligible": True, "verified_count": 1,
                    "event_fingerprint": "a" * 64,
                    "canonical_effect": False, "portfolio_effect": False,
                },
            }
            ctx.write_text(json.dumps(current))
            (old / "context.json").write_text(json.dumps({
                "latest_capture": current["latest_capture"]
            }))
            (old / "DAILY_DIRECTOR_OUTPUT.json").write_text(json.dumps({"status": "PASS"}))
            first = evaluate(ctx, root / "outputs", now=NOW)
            self.assertFalse(first["identity_unseen"])
            self.assertTrue(first["news_review_ready"])
            self.assertEqual(first["fresh_reason"], "NEW_VERIFIED_NEWS_CONTEXT")
            # A skipped output or a previous run without news is NOT evidence of a news review.
            (old / "context.json").write_text(json.dumps(current))
            (old / "DAILY_DIRECTOR_OUTPUT.json").write_text(json.dumps({"status": "BLOCKED"}))
            self.assertTrue(evaluate(ctx, root / "outputs", now=NOW)["fresh_ready"])
            (old / "DAILY_DIRECTOR_OUTPUT.json").write_text(json.dumps({"status": "DEGRADED"}))
            last = evaluate(ctx, root / "outputs", now=NOW)
            self.assertFalse(last["fresh_ready"])
            self.assertTrue(last["news_already_analyzed"])
            # A different capture ID without numeric market delta cannot
            # monetize an old verified news event for a second time.
            current["latest_capture"]["run_id"] = "CAPTURE_124"
            ctx.write_text(json.dumps(current))
            repeated = evaluate(ctx, root / "outputs", now=NOW)
            self.assertTrue(repeated["identity_unseen"])
            self.assertFalse(repeated["fresh_ready"])

    def test_news_only_delta_gate_requires_verified_noncanonical_news(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "context.json"
            repo = Path(__file__).resolve().parents[2]
            script = repo / "scripts/api_agent/check_delta_ready.py"
            context = {
                "coverage": {"comparable_numeric_metrics": 0},
                "delta_status": "NO_DELTA",
                "news_intelligence": {
                    "news_only_review_eligible": True, "verified_count": 1,
                    "event_fingerprint": "b" * 64,
                    "canonical_effect": False, "portfolio_effect": False,
                },
            }
            source.write_text(json.dumps(context))
            result = subprocess.run(
                [sys.executable, str(script), "--context", str(source)],
                text=True, capture_output=True, check=True,
            )
            self.assertIn("delta_ready=true", result.stdout)
            context["news_intelligence"]["portfolio_effect"] = True
            source.write_text(json.dumps(context))
            blocked = subprocess.run(
                [sys.executable, str(script), "--context", str(source)],
                text=True, capture_output=True, check=True,
            )
            self.assertIn("delta_ready=false", blocked.stdout)

    def test_workflow_uses_existing_context_augmentation_and_existing_budget(self):
        repo = Path(__file__).resolve().parents[2]
        workflow = (repo / ".github/workflows/daily-director-shadow.yml").read_text()
        augmenter = (repo / "scripts/api_agent/augment_director_compounding_learning_context.py").read_text()
        self.assertIn("augment_director_compounding_learning_context.py", workflow)
        self.assertIn("check_director_freshness.py", workflow)
        self.assertIn("check_delta_ready.py", workflow)
        self.assertIn("check_monthly_cost_guard.py", workflow)
        self.assertIn('context["news_intelligence"] = news_routed', augmenter)
        self.assertIn('"news_intelligence"', augmenter)


if __name__ == "__main__":
    unittest.main()
