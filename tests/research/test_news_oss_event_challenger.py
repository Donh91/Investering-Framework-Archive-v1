"""Pure deterministic regression cases for the OSS-inspired news challenger."""
import unittest

from scripts.research.news_oss_event_challenger import (
    canonical_article_url,
    first_known_source_census,
    relation,
)


def report(**kw):
    row = {
        "url": "https://alpha.example/story1",
        "scope": "SINGLE_EVENT",
        "actor": "SEC",
        "action": "approves",
        "target": "Bitcoin ETF",
        "event_time_utc": "2026-11-04T10:15:00Z",
        "event_time_precision": "TIMESTAMP",
    }
    row.update(kw)
    return row


def source(**kw):
    row = {
        "source_role": "PRIMARY",
        "verification_status": "PRIMARY_SOURCE_VERIFIED",
        "independent_publisher_group": "official-sec",
        "first_known_utc": "2026-11-04T10:16:00Z",
        "retrieval_end_utc": "2026-11-04T10:16:08Z",
    }
    row.update(kw)
    return row


CUTOFF = "2026-11-04T10:20:00Z"


class NewsOssEventChallengerTests(unittest.TestCase):
    def test_same_story_tracking_parameters_are_same_article_not_independent_events(self):
        a = report(url="https://alpha.example/story1?utm_campaign=A&id=9")
        b = report(url="https://alpha.example/story1/?id=9&utm_source=B#article")
        self.assertEqual(relation(a, b)["relation"], "SAME_ARTICLE")

    def test_userinfo_url_cannot_impersonate_article_host(self):
        self.assertIsNone(canonical_article_url("https://publisher.test@evil.test/story"))
        self.assertIsNone(canonical_article_url("https://user:pass@publisher.test/story"))
        self.assertEqual(
            relation(report(url="https://publisher.test@evil.test/story"),
                     report(url="https://publisher.test/story"))["relation"],
            "POSSIBLE_SAME_OCCURRENCE",
        )

    def test_meaningful_query_parameter_is_not_erased(self):
        self.assertNotEqual(
            canonical_article_url("https://agency.test/report?id=1"),
            canonical_article_url("https://agency.test/report?id=2"),
        )

    def test_unrelated_same_ticker_event_stays_distinct(self):
        a = report(url="https://one.test/x", action="approves")
        b = report(url="https://two.test/y", action="rejects")
        self.assertEqual(relation(a, b)["relation"], "RELATED_DEVELOPMENT")
        # A development is explicitly not a duplicate event.

    def test_different_actor_never_merges_just_because_title_or_target_overlap(self):
        a = report(url="https://one.test/x")
        b = report(url="https://two.test/y", actor="Treasury")
        self.assertEqual(relation(a, b)["relation"], "DIFFERENT_EVENT")

    def test_different_token_contract_remains_distinct(self):
        a = report(url="https://one.test/x", target="0xAAA@base")
        b = report(url="https://two.test/y", target="0xBBB@base")
        self.assertEqual(relation(a, b)["relation"], "DIFFERENT_EVENT")

    def test_identical_event_frame_is_only_possible_match_not_automatic_merge(self):
        a = report(url="https://one.test/x")
        b = report(url="https://two.test/y", event_time_utc="2026-11-04T10:30:00Z")
        self.assertEqual(relation(a, b)["relation"], "POSSIBLE_SAME_OCCURRENCE")

    def test_roundup_may_not_bridge_two_independent_facts(self):
        a = report(url="https://one.test/x", scope="ROUNDUP")
        b = report(url="https://two.test/y")
        self.assertEqual(relation(a, b)["relation"], "REVIEW_REQUIRED")

    def test_date_only_never_assumed_to_be_10am_event(self):
        a = report(url="https://one.test/x", event_time_precision="DATE_ONLY")
        b = report(url="https://two.test/y")
        self.assertEqual(relation(a, b)["relation"], "REVIEW_REQUIRED")

    def test_time_window_prevents_conflating_repeated_occurrences(self):
        a = report(url="https://one.test/x")
        b = report(url="https://two.test/y", event_time_utc="2026-11-04T13:30:00Z")
        self.assertEqual(relation(a, b)["relation"], "DIFFERENT_EVENT")

    def test_unknown_actor_is_not_guessed(self):
        a = report(url="https://one.test/x", actor=None)
        b = report(url="https://two.test/y")
        self.assertEqual(relation(a, b)["relation"], "REVIEW_REQUIRED")

    def test_same_original_publisher_syndication_counts_once(self):
        a = source(independent_publisher_group="original-wire")
        b = source(independent_publisher_group="ORIGINAL-WIRE")
        r = first_known_source_census([a, b], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 1)
        self.assertEqual(r["same_publisher_repeats"], 1)
        self.assertTrue(r["no_truth_or_compass_promotion"])

    def test_unverified_x_and_telegram_are_not_independent_source_verification(self):
        r = first_known_source_census([
            source(source_role="SOCIAL", independent_publisher_group="x-account1"),
            source(source_role="PUBLISHER", verification_status="DISCOVERY_UNVERIFIED", independent_publisher_group="telegram"),
        ], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 0)
        self.assertEqual(r["excluded_by_reason"]["non_verifying_source_role"], 1)
        self.assertEqual(r["excluded_by_reason"]["unverified_claim"], 1)

    def test_source_clock_missing_fails_closed(self):
        r = first_known_source_census([source(retrieval_end_utc=None)], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 0)
        self.assertEqual(r["excluded_by_reason"]["pit_clock_unknown"], 1)

    def test_source_first_seen_after_cutoff_never_backdated(self):
        r = first_known_source_census([source(first_known_utc="2026-11-04T10:25:00Z")], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 0)
        self.assertEqual(r["excluded_by_reason"]["post_cutoff_first_known"], 1)

    def test_source_response_completion_after_cutoff_never_backdated(self):
        r = first_known_source_census([source(retrieval_end_utc="2026-11-04T10:25:00Z")], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 0)

    def test_unresolved_independent_publisher_group_stays_unknown(self):
        r = first_known_source_census([source(independent_publisher_group=None)], CUTOFF)
        self.assertEqual(r["independent_eligible_groups"], 0)
        self.assertEqual(r["excluded_by_reason"]["publisher_independence_unknown"], 1)

    def test_cutoff_must_have_explicit_timezone(self):
        with self.assertRaises(ValueError):
            first_known_source_census([source()], "2026-11-04T10:20:00")

    def test_no_network_writes_or_trading_authority(self):
        r = first_known_source_census([], CUTOFF)
        self.assertEqual(r["authority"], "SHADOW_COMPARISON_ONLY")
        self.assertEqual(r["eligible_reports"], 0)
        self.assertTrue(r["no_truth_or_compass_promotion"])


if __name__ == "__main__":
    unittest.main()
