import unittest

from scripts.research.etf_pit_edge_replay_v1 import (
    build_session_events,
    evaluate_endpoint,
    state_a2,
)


def row(day, observed, total, *, verified=None, unknown=0, final=True, parity=True, key=None):
    return {
        "asset":"BTC",
        "session_date":day,
        "is_nyse_session":True,
        "not_source_revision":False,
        "reported_total":total,
        "parity":parity,
        "unknown_cell_count":unknown,
        "session_final_claim":final,
        "verification_completed_at_utc":verified,
        "observed_at_utc":observed,
        "ledger_key":key or f"{day}-{observed}",
    }


class EtfPitEdgeReplayV1Test(unittest.TestCase):
    def test_missing_middle_session_never_bridges_a2(self):
        rows=[
            row("2026-07-15","2026-07-16T08:00:00Z",-10,verified="2026-07-16T08:05:00Z"),
            row("2026-07-16","2026-07-17T08:00:00Z",-20,verified=None),
            row("2026-07-17","2026-07-20T08:00:00Z",-30,verified="2026-07-20T08:05:00Z"),
        ]
        events=build_session_events(rows,"VERIFIED_ONLY")
        result=evaluate_endpoint(["2026-07-15","2026-07-16","2026-07-17"],2,events,3,state_a2)
        self.assertEqual(result["status"],"UNAVAILABLE_MISSING_ADMISSIBLE_SESSION")
        self.assertEqual(result["missing_sessions"],["2026-07-16"])

    def test_revision_before_first_eval_prevents_false_a2(self):
        rows=[
            row("2026-07-15","2026-07-16T08:00:00Z",-10,verified="2026-07-16T08:05:00Z",key="a"),
            row("2026-07-16","2026-07-17T08:00:00Z",-20,verified="2026-07-17T08:05:00Z",key="b"),
            row("2026-07-16","2026-07-17T09:00:00Z",5,verified=None,key="b2"),
            row("2026-07-17","2026-07-20T08:00:00Z",-30,verified="2026-07-20T08:05:00Z",key="c"),
        ]
        events=build_session_events(rows,"D1_START_D4_COMPLETE_REVISIONS")
        result=evaluate_endpoint(["2026-07-15","2026-07-16","2026-07-17"],2,events,3,state_a2)
        self.assertEqual(result["status"],"EVALUABLE")
        self.assertFalse(result["first_state"])

    def test_revision_after_first_eval_records_state_change(self):
        rows=[
            row("2026-07-15","2026-07-16T08:00:00Z",-10,verified="2026-07-16T08:05:00Z",key="a"),
            row("2026-07-16","2026-07-17T08:00:00Z",-20,verified="2026-07-17T08:05:00Z",key="b"),
            row("2026-07-17","2026-07-20T08:00:00Z",-30,verified="2026-07-20T08:05:00Z",key="c"),
            row("2026-07-16","2026-07-21T09:00:00Z",5,verified=None,key="b2"),
        ]
        events=build_session_events(rows,"D1_START_D4_COMPLETE_REVISIONS")
        result=evaluate_endpoint(["2026-07-15","2026-07-16","2026-07-17"],2,events,3,state_a2)
        self.assertTrue(result["first_state"])
        self.assertFalse(result["final_state"])
        self.assertTrue(result["state_changed_after_first_eval"])

    def test_unresolved_unknown_is_not_admissible(self):
        rows=[
            row("2026-07-15","2026-07-16T08:00:00Z",-10,verified="2026-07-16T08:05:00Z"),
            row("2026-07-16","2026-07-17T08:00:00Z",-20,verified="2026-07-17T08:05:00Z",unknown=1),
            row("2026-07-17","2026-07-20T08:00:00Z",-30,verified="2026-07-20T08:05:00Z"),
        ]
        events=build_session_events(rows,"VERIFIED_ONLY")
        result=evaluate_endpoint(["2026-07-15","2026-07-16","2026-07-17"],2,events,3,state_a2)
        self.assertEqual(result["status"],"UNAVAILABLE_MISSING_ADMISSIBLE_SESSION")


if __name__=="__main__":
    unittest.main()
