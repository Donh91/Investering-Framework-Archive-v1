"""Offline, synthetic-data-only tests for the CoinGecko Shadow comparison probe."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from datetime import datetime, timezone

from scripts.research.coingecko_news_shadow_probe import compare, timestamp, validate_coingecko, validate_situation

ASOF = datetime(2026, 10, 10, 15, tzinfo=timezone.utc)


def cg(items, **extra):
    return {"provider": "CoinGecko", "source_status": "PASS",
            "captured_at_utc": "2026-10-10T14:00:00Z", "articles": items, **extra}


def sr(events=None, unverified=None):
    # Synthetic owner-shaped receipts, not real provider evidence. The owner's
    # run-start detection stamp predates these source retrievals.
    events = events or []
    unverified = unverified or []
    for event in events:
        receipts = event.setdefault("source_receipts", [{"url": event.get("url", "https://example.test/event")}])
        for receipt in receipts:
            receipt.setdefault("fetched_at_utc", "2026-10-10T13:05:00Z")
    for item in unverified:
        item.setdefault("source_receipt", {"url": item.get("url"), "fetched_at_utc": "2026-10-10T13:05:00Z"})
    return {"contract": "SITUATION_ROOM_DAILY_OWNER_v1",
            "observation_date_utc": "2026-10-10", "daily_result": "NO_NEW_MATERIAL_CATALYST",
            "run_status": "PASS", "detection_time_utc": "2026-10-10T13:00:00Z",
            "source_coverage": {"receipts": [{"url": "https://example.test/landing", "fetched_at_utc": "2026-10-10T13:05:00Z"}]},
            "events": events, "current_unverified_discoveries": unverified}


def article(title, url, time="2026-10-10T12:00:00Z", kind="news"):
    return {"title": title, "url": url, "posted_at": time, "type": kind,
            "source_name": "Synthetic Source"}


class ShadowComparisonTests(unittest.TestCase):
    def test_future_baseline_receipts_block_despite_earlier_detection(self):
        for lane in ("coverage", "event", "discovery"):
            baseline = sr(events=[{"title": "Synthetic event", "url": "https://example.test/primary"}],
                          unverified=[{"title": "Synthetic discovery", "url": "https://example.test/discovery"}])
            receipt = {"coverage": baseline["source_coverage"]["receipts"][0],
                       "event": baseline["events"][0]["source_receipts"][0],
                       "discovery": baseline["current_unverified_discoveries"][0]["source_receipt"]}[lane]
            receipt["fetched_at_utc"] = "2026-10-10T16:00:00Z"
            with self.subTest(lane=lane), self.assertRaises(ValueError):
                compare(cg([article("Synthetic primary event", "https://example.test/primary")]), baseline, ASOF)

    def test_missing_baseline_receipt_time_blocks_pit_comparison(self):
        for lane in ("coverage", "event", "discovery"):
            baseline = sr(events=[{"title": "Synthetic event", "url": "https://example.test/primary"}],
                          unverified=[{"title": "Synthetic discovery", "url": "https://example.test/discovery"}])
            receipt = {"coverage": baseline["source_coverage"]["receipts"][0],
                       "event": baseline["events"][0]["source_receipts"][0],
                       "discovery": baseline["current_unverified_discoveries"][0]["source_receipt"]}[lane]
            del receipt["fetched_at_utc"]
            with self.subTest(lane=lane), self.assertRaises(ValueError):
                compare(cg([]), baseline, ASOF)

    def test_missing_baseline_availability_receipts_block(self):
        for lane in ("coverage", "event", "discovery"):
            baseline = sr(events=[{"title": "Synthetic event", "url": "https://example.test/primary"}],
                          unverified=[{"title": "Synthetic discovery", "url": "https://example.test/discovery"}])
            if lane == "coverage":
                del baseline["source_coverage"]
            elif lane == "event":
                baseline["events"][0]["source_receipts"] = []
            else:
                del baseline["current_unverified_discoveries"][0]["source_receipt"]
            with self.subTest(lane=lane), self.assertRaises(ValueError):
                compare(cg([]), baseline, ASOF)

    def test_failed_baselines_cannot_create_incremental_coverage(self):
        for state in ("COLLECTOR_FAILURE", "UNKNOWN_DUE_TO_SOURCE_FAILURE", None, "UNKNOWN"):
            baseline = sr()
            baseline["daily_result"] = state
            with self.subTest(state=state), self.assertRaises(ValueError):
                compare(cg([article("Synthetic article", "https://example.test/1")]), baseline, ASOF)

    def test_baseline_date_and_detection_must_match_cutoff_date(self):
        for date, detection in ((None, "2026-10-10T13:00:00Z"),
                                ("2026-10-09", "2026-10-10T13:00:00Z"),
                                ("2026-10-10", "2026-10-09T13:00:00Z")):
            baseline = sr()
            baseline.update(observation_date_utc=date, detection_time_utc=detection)
            with self.subTest(date=date, detection=detection), self.assertRaises(ValueError):
                compare(cg([]), baseline, ASOF)

    def test_provider_capture_must_be_same_daily_window(self):
        with self.assertRaises(ValueError):
            compare(cg([], captured_at_utc="2026-10-09T23:00:00Z"), sr(), ASOF)

    def test_archive_unverified_rows_are_not_current_baseline(self):
        item = article("Synthetic current article", "https://example.test/current")
        baseline = sr()
        baseline["unverified_discoveries"] = [{"title": item["title"], "url": item["url"]}]
        result, _ = compare(cg([item]), baseline, ASOF)
        self.assertEqual(result["metrics"]["new_discoveries_unverified"], 1)

    def test_verified_source_receipt_url_is_same_source(self):
        item = article("Synthetic primary event", "https://example.test/primary")
        baseline = sr(events=[{"title": "Different title", "source_receipts": [{"url": item["url"]}]}])
        result, candidates = compare(cg([item]), baseline, ASOF)
        self.assertEqual(result["metrics"]["same_url_in_situation_room"], 1)
        self.assertEqual(candidates[0]["discovery_status"], "SAME_URL_DISCOVERY_ONLY")

    def test_candidate_capture_time_is_not_first_discovery_or_latency_proof(self):
        result, candidates = compare(cg([article("Synthetic event", "https://example.test/timing")]), sr(), ASOF)
        self.assertEqual(candidates[0]["observed_at_utc"], "2026-10-10T14:00:00Z")
        self.assertEqual(result["latency_evidence_status"], "UNKNOWN_NO_PRIOR_CAPTURE_POPULATION")
        self.assertNotIn("first_observed_at_utc", candidates[0])

    def test_unique_is_unverified_and_never_prospective_credit(self):
        row = article("Council publishes detailed proposed blockchain compliance schedule",
                      "https://example.test/news/1")
        result, candidates = compare(cg([row]), sr(), ASOF)
        self.assertEqual(result["metrics"]["new_discoveries_unverified"], 1)
        self.assertEqual(candidates[0]["verification_status"], "UNVERIFIED")
        self.assertEqual(result["prospective_news_test_credit"], 0)
        self.assertFalse(result["canonical_effect"])
        self.assertFalse(result["market_state_effect"])
        self.assertFalse(result["portfolio_effect"])
        self.assertFalse(result["execution_authority"])
        self.assertNotIn("Council publishes", json.dumps(result))

    def test_tracking_url_is_same_source_not_primary_verification(self):
        row = article("Agency issues significant new exchange guidance today",
                      "http://www.example.test/news/2?utm_source=feed")
        baseline = sr(events=[{"title": "Agency notice", "url": "https://example.test/news/2"}])
        result, candidates = compare(cg([row]), baseline, ASOF)
        self.assertEqual(result["metrics"]["same_url_in_situation_room"], 1)
        self.assertEqual(candidates[0]["discovery_status"], "SAME_URL_DISCOVERY_ONLY")
        self.assertEqual(result["verified_news_cards_created"], 0)

    def test_title_overlap_is_not_fact_verification(self):
        title = "Treasury announces new digital asset reporting consultation deadline"
        row = article(title, "https://first.test/news/3")
        baseline = sr(unverified=[{"title": title, "url": "https://second.test/story/9"}])
        result, candidates = compare(cg([row]), baseline, ASOF)
        self.assertEqual(result["metrics"]["possible_headline_overlap_unverified"], 1)
        self.assertEqual(candidates[0]["verification_status"], "UNVERIFIED")

    def test_duplicate_stale_future_guide_and_invalid_filtered(self):
        fresh = article("Company publishes detailed quarterly financial results",
                        "https://example.test/news/4")
        items = [fresh, fresh,
                 article("Old story", "https://example.test/news/5", "2026-10-01T12:00:00Z"),
                 article("Future leak", "https://example.test/news/6", "2026-10-11T12:00:00Z"),
                 article("Educational content", "https://example.test/guide", kind="guide"),
                 article("", "https://example.test/news/7")]
        result, candidates = compare(cg(items), sr(), ASOF)
        self.assertEqual(result["metrics"]["news_valid"], 1)
        self.assertEqual(result["metrics"]["duplicate_provider_url"], 1)
        self.assertEqual(result["metrics"]["stale"], 1)
        self.assertEqual(result["metrics"]["invalid_or_future"], 2)
        self.assertEqual(result["metrics"]["guides_skipped"], 1)
        self.assertEqual(len(candidates), 1)

    def test_missing_licensed_source_is_unknown_not_zero_events(self):
        with self.assertRaises(ValueError):
            validate_coingecko({"provider": "CoinGecko", "articles": []}, ASOF)
        with self.assertRaises(ValueError):
            validate_coingecko(cg([], captured_at_utc="2026-10-12T00:00:00Z"), ASOF)

    def test_situation_room_future_observation_refused(self):
        row = sr()
        row["detection_time_utc"] = "2026-10-11T00:00:00Z"
        with self.assertRaises(ValueError):
            validate_situation(row, ASOF)

    def test_timezone_required(self):
        with self.assertRaises(ValueError):
            timestamp("2026-10-10T12:00:00")

    def test_empty_input_is_not_claimed_as_no_market_catalyst(self):
        summary, rows = compare(cg([]), sr(), ASOF)
        self.assertEqual(summary["source_status"], "EMPTY_SNAPSHOT_NO_COVERAGE_INFERENCE")
        self.assertEqual(rows, [])
        self.assertEqual(summary["primary_corrob_events_created"], 0)

    def test_provider_article_cannot_be_published_after_capture(self):
        item = article("Agency schedules consultations for new market regulations",
                       "https://example.test/future-capture",
                       "2026-10-10T14:30:00Z")
        summary, candidates = compare(cg([item]), sr(), ASOF)
        self.assertEqual(summary["metrics"]["invalid_or_future"], 1)
        self.assertEqual(candidates, [])

    def test_stale_first_does_not_hide_fresh_same_url(self):
        stale = article("Older commentary", "https://example.test/same-url",
                        "2026-10-01T10:00:00Z")
        fresh = article("Fresh regulatory decision published", "https://example.test/same-url",
                        "2026-10-10T12:00:00Z")
        summary, candidates = compare(cg([stale, fresh]), sr(), ASOF)
        self.assertEqual(summary["metrics"]["new_discoveries_unverified"], 1)
        self.assertEqual(summary["metrics"]["stale"], 1)
        self.assertEqual(len(candidates), 1)

    def test_cli_private_candidates_file_is_0600_and_repo_path_is_refused(self):
        script = Path(__file__).resolve().parents[1] / "scripts/research/coingecko_news_shadow_probe.py"
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            input_cg, input_sr = folder / "cg.json", folder / "sr.json"
            input_cg.write_text(json.dumps(cg([article(
                "Regulator announces formal new custody consultation timeline",
                "https://example.test/announcement")])) + "\n")
            input_sr.write_text(json.dumps(sr()) + "\n")
            cmd = [sys.executable, str(script), "--coingecko-snapshot", str(input_cg),
                   "--situation-room-daily", str(input_sr), "--as-of-utc",
                   "2026-10-10T15:00:00Z", "--private-candidates-output"]
            private_result = folder / "private.json"
            completed = subprocess.run(cmd + [str(private_result)], text=True,
                                       capture_output=True, check=False)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertTrue(private_result.exists())
            self.assertEqual(os.stat(private_result).st_mode & 0o777, 0o600)
            self.assertNotIn("Regulator announces", completed.stdout)
            # Try to place provider-value-containing candidates in the public control repo.
            forbidden_path = Path(__file__).resolve().parents[1] / "do-not-create-news-candidates.json"
            blocked = subprocess.run(cmd + [str(forbidden_path)], text=True,
                                     capture_output=True, check=False)
            self.assertEqual(blocked.returncode, 2)
            self.assertFalse(forbidden_path.exists())


if __name__ == "__main__":
    unittest.main()

