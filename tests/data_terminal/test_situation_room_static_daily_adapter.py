import unittest
from unittest.mock import patch

from scripts.data_terminal import situation_room_static_daily_adapter as adapter


class SituationRoomStaticDailyAdapterTests(unittest.TestCase):
    def test_daily_briefing_url_is_deterministic(self):
        self.assertEqual(
            adapter.daily_briefing_url("2026-08-27"),
            "https://situationroom.space/briefing/2026-08-27",
        )

    def test_sources_replace_only_situation_room_archive(self):
        original = (
            ("SITUATION_ROOM", "DISCOVERY_ONLY", "https://situationroom.space/briefings"),
            ("SEC", "PRIMARY", "https://www.sec.gov/newsroom/press-releases"),
        )
        with patch.object(adapter.owner, "SOURCES", original):
            sources = adapter.sources_for_date("2026-08-27")
        self.assertEqual(
            sources[0],
            ("SITUATION_ROOM", "DISCOVERY_ONLY", "https://situationroom.space/briefing/2026-08-27"),
        )
        self.assertEqual(sources[1], original[1])

    def test_direct_daily_page_is_itself_the_discovery_candidate(self):
        parser = adapter.owner.PageParser()
        parser.feed("<html><head><title>Bitcoin liquidity briefing</title></head></html>")
        rows = list(adapter.direct_daily_candidate_links(
            "SITUATION_ROOM",
            "https://situationroom.space/briefing/2026-08-27",
            parser,
        ))
        self.assertEqual(rows, [(
            "https://situationroom.space/briefing/2026-08-27",
            "Bitcoin liquidity briefing",
        )])

    def test_non_situation_room_sources_keep_v1_candidate_logic(self):
        parser = adapter.owner.PageParser()
        parser.feed('<html><a href="/newsroom/press-releases/2026-test">crypto asset regulation</a></html>')
        rows = list(adapter.direct_daily_candidate_links(
            "SEC",
            "https://www.sec.gov/newsroom/press-releases",
            parser,
        ))
        self.assertEqual(len(rows), 1)
        self.assertIn("/newsroom/press-releases/2026-test", rows[0][0])

    def test_dated_discovery_without_timestamp_cannot_be_silently_no_event(self):
        discovery = {
            "source_id": "SITUATION_ROOM",
            "source_role": "DISCOVERY_ONLY",
            "title": "Bitcoin liquidity briefing",
            "url": "https://situationroom.space/briefing/2026-08-27",
            "event_time_utc": None,
            "event_time_precision": "UNRESOLVED",
            "verification_status": "DISCOVERY_UNVERIFIED",
        }
        result = {
            "daily_result": "NO_NEW_MATERIAL_CATALYST",
            "run_status": "PASS",
            "unverified_discoveries": [discovery],
            "current_unverified_discoveries": [],
        }
        adapter.apply_dated_discovery_fail_closed(result, "2026-08-27")
        self.assertEqual(result["daily_result"], "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY")
        self.assertEqual(result["run_status"], "DEGRADED")
        self.assertEqual(len(result["current_unverified_discoveries"]), 1)
        self.assertEqual(
            result["current_unverified_discoveries"][0]["discovery_date_basis"],
            "DETERMINISTIC_DATED_SOURCE_URL",
        )
        self.assertIsNone(result["current_unverified_discoveries"][0]["event_time_utc"])

    def test_situation_room_retrieval_failure_with_healthy_primaries_matches_live_gate(self):
        result = {
            "daily_result": "NO_NEW_MATERIAL_CATALYST",
            "run_status": "PASS",
            "source_coverage": {
                "primary_pass": 5,
                "primary_total": 5,
                "receipts": [
                    {
                        "source_id": "SITUATION_ROOM",
                        "role": "DISCOVERY_ONLY",
                        "status": "FAIL",
                        "error_class": "URLError",
                    },
                    {"source_id": "SEC", "role": "PRIMARY", "status": "PASS"},
                ],
            },
        }
        adapter.apply_situation_room_retrieval_fail_closed(result)
        self.assertEqual(result["daily_result"], "REVIEW_REQUIRED_UNVERIFIED_DISCOVERY")
        self.assertEqual(result["run_status"], "DEGRADED")
        self.assertGreaterEqual(result["source_coverage"]["primary_pass"], 3)

    def test_successful_situation_room_retrieval_preserves_clean_no_event(self):
        result = {
            "daily_result": "NO_NEW_MATERIAL_CATALYST",
            "run_status": "PASS",
            "source_coverage": {
                "primary_pass": 5,
                "primary_total": 5,
                "receipts": [
                    {"source_id": "SITUATION_ROOM", "role": "DISCOVERY_ONLY", "status": "PASS"},
                ],
            },
        }
        adapter.apply_situation_room_retrieval_fail_closed(result)
        self.assertEqual(result["daily_result"], "NO_NEW_MATERIAL_CATALYST")
        self.assertEqual(result["run_status"], "PASS")

    def test_primary_source_insufficiency_remains_unknown_and_degraded(self):
        result = {
            "daily_result": "UNKNOWN_DUE_TO_SOURCE_FAILURE",
            "run_status": "DEGRADED",
            "source_coverage": {
                "primary_pass": 2,
                "primary_total": 5,
                "receipts": [
                    {"source_id": "SITUATION_ROOM", "role": "DISCOVERY_ONLY", "status": "FAIL"},
                    {"source_id": "SEC", "role": "PRIMARY", "status": "PASS"},
                    {"source_id": "TREASURY", "role": "PRIMARY", "status": "PASS"},
                ],
            },
        }
        adapter.apply_situation_room_retrieval_fail_closed(result)
        self.assertEqual(result["daily_result"], "UNKNOWN_DUE_TO_SOURCE_FAILURE")
        self.assertEqual(result["run_status"], "DEGRADED")
        self.assertLess(result["source_coverage"]["primary_pass"], 3)


if __name__ == "__main__":
    unittest.main()
