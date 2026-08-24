import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.data_terminal import situation_room_daily_owner as owner


class SituationRoomOwnerTests(unittest.TestCase):
    def result(self, url, body=b"<html><title>Index</title></html>", status="PASS"):
        return owner.FetchResult(
            url=url,
            status=status,
            http_status=200 if status == "PASS" else None,
            fetched_at_utc="2026-08-23T20:23:00Z",
            body=body if status == "PASS" else b"",
            error=None if status == "PASS" else "TimeoutError",
        )

    def base_sources(self):
        return (
            ("SITUATION_ROOM", "DISCOVERY_ONLY", "https://situationroom.test/briefings"),
            ("P1", "PRIMARY", "https://p1.test/news"),
            ("P2", "PRIMARY", "https://p2.test/news"),
            ("P3", "PRIMARY", "https://p3.test/news"),
        )

    def test_successful_zero_event_is_not_failure(self):
        def fake_fetch(url, timeout=15):
            return self.result(url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["daily_result"], "NO_NEW_MATERIAL_CATALYST")
            self.assertEqual(result["run_status"], "PASS")
            self.assertEqual(result["events"], [])
            self.assertFalse(result["shared_row_tournament_eligible"])

    def test_total_source_failure_is_not_no_event(self):
        def fake_fetch(url, timeout=15):
            return self.result(url, status="FAIL")
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["daily_result"], "COLLECTOR_FAILURE")
            self.assertEqual(result["run_status"], "DEGRADED")

    def test_situation_room_discovery_cannot_self_verify(self):
        landing = b'<html><a href="/briefing/item">Bitcoin liquidity shock</a></html>'
        article = b'<html><head><title>Bitcoin liquidity shock</title><meta property="article:published_time" content="2026-08-23T12:00:00Z"></head></html>'
        def fake_fetch(url, timeout=15):
            if url == "https://situationroom.test/briefings":
                return self.result(url, landing)
            if url == "https://situationroom.test/briefing/item":
                return self.result(url, article)
            return self.result(url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["events"], [])
            self.assertEqual(len(result["unverified_discoveries"]), 1)
            self.assertEqual(result["unverified_discoveries"][0]["verification_status"], "DISCOVERY_UNVERIFIED")
            self.assertEqual(result["daily_result"], "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY")
            self.assertEqual(result["run_status"], "DEGRADED")

    def test_discovery_fetch_failure_does_not_veto_clean_primary_no_event(self):
        landing = b'<html><a href="/briefing/item">Bitcoin liquidity shock</a></html>'
        def fake_fetch(url, timeout=15):
            if url == "https://situationroom.test/briefings":
                return self.result(url, landing)
            if url == "https://situationroom.test/briefing/item":
                return self.result(url, status="FAIL")
            return self.result(url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["daily_result"], "NO_NEW_MATERIAL_CATALYST")
            self.assertEqual(result["unresolved_candidates"], [])
            self.assertEqual(result["unverified_discoveries"][0]["verification_status"], "DISCOVERY_FETCH_FAILED")

    def test_old_primary_release_with_visible_month_date_does_not_block_today(self):
        landing = b'<html><a href="/crypto">SEC proposes regulation crypto assets</a></html>'
        article = b'<html><head><title>SEC proposes Regulation Crypto Assets</title></head><body>August 18, 2026</body></html>'
        def fake_fetch(url, timeout=15):
            if url == "https://p1.test/news":
                return self.result(url, landing)
            if url == "https://p1.test/crypto":
                return self.result(url, article)
            return self.result(url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["daily_result"], "NO_NEW_MATERIAL_CATALYST")
            self.assertEqual(result["unresolved_candidates"], [])
            self.assertEqual(result["events"], [])

    def test_source_specific_candidate_filter_excludes_generic_navigation(self):
        self.assertFalse(owner.source_candidate_allowed("SITUATION_ROOM", "https://situationroom.space/briefings", "https://situationroom.space/about"))
        self.assertTrue(owner.source_candidate_allowed("SITUATION_ROOM", "https://situationroom.space/briefings", "https://situationroom.space/briefing/crypto-liquidity"))
        self.assertFalse(owner.source_candidate_allowed("SEC", "https://www.sec.gov/newsroom/press-releases", "https://www.sec.gov/featured-topics/cybersecurity"))
        self.assertTrue(owner.source_candidate_allowed("SEC", "https://www.sec.gov/newsroom/press-releases", "https://www.sec.gov/newsroom/press-releases/2026-76-sec-proposes-new-regulation-crypto-assets"))
        self.assertFalse(owner.source_candidate_allowed("FEDERAL_RESERVE", "https://www.federalreserve.gov/newsevents/pressreleases.htm", "https://www.federalreserve.gov/newsevents/pressreleases/2026-press-fomc.htm"))
        self.assertTrue(owner.source_candidate_allowed("FEDERAL_RESERVE", "https://www.federalreserve.gov/newsevents/pressreleases.htm", "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"))

    def test_primary_source_can_create_timestamped_research_event(self):
        landing = b'<html><a href="/crypto">SEC proposes regulation crypto assets</a></html>'
        article = b'<html><head><title>SEC proposes Regulation Crypto Assets</title><meta property="article:published_time" content="2026-08-23T15:30:00Z"></head></html>'
        def fake_fetch(url, timeout=15):
            if url == "https://p1.test/news":
                return self.result(url, landing)
            if url == "https://p1.test/crypto":
                return self.result(url, article)
            return self.result(url)
        with tempfile.TemporaryDirectory() as tmp, patch.object(owner, "SOURCES", self.base_sources()), patch.object(owner, "fetch", fake_fetch):
            result = owner.run(Path(tmp), "2026-08-23")
            self.assertEqual(result["daily_result"], "MATERIAL_CATALYSTS_FOUND")
            self.assertEqual(len(result["events"]), 1)
            event = result["events"][0]
            self.assertEqual(event["classification"], "STRUCTURAL")
            self.assertEqual(event["catalyst_subtype"], "REGULATORY_CATALYST")
            self.assertEqual(event["causal_authority"], "NONE")

    def test_event_ledger_is_append_only_and_deduplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            event = {
                "event_id": "EVT_X",
                "event_family_id": "EVF_X",
                "title": "Test",
                "event_time_utc": "2026-08-23T00:00:00Z",
                "event_time_precision": "DATE_ONLY",
                "detection_time_utc": "2026-08-23T20:23:00Z",
                "classification": "MARKET_RELEVANT",
                "catalyst_subtype": "TEST",
                "confidence": "HIGH_PRIMARY_SOURCE",
                "expected_duration": "HOURS_TO_DAYS",
                "affected_framework_lanes": ["CATALYST_NEWS"],
                "verification_status": "PRIMARY_SOURCE_VERIFIED",
                "source_receipts": [],
                "causal_authority": "NONE",
            }
            result = {
                "observation_date_utc": "2026-08-23",
                "detection_time_utc": "2026-08-23T20:23:00Z",
                "daily_result": "MATERIAL_CATALYSTS_FOUND",
                "run_status": "PASS",
                "run_id": "R1",
                "events": [event],
            }
            owner.write_outputs(root, result)
            result["run_id"] = "R2"
            owner.write_outputs(root, result)
            rows = [json.loads(line) for line in (root / "EVENT_LEDGER.jsonl").read_text().splitlines()]
            self.assertEqual(len(rows), 1)
            self.assertFalse(rows[0]["shared_row_tournament_eligible"])


if __name__ == "__main__":
    unittest.main()
