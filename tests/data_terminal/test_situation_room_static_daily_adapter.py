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


if __name__ == "__main__":
    unittest.main()
