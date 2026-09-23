import unittest

from backtest_engine.etf_pit_replay import (
    ETF_PIT_DECISION_ID,
    build_etf_trailing_pit,
    map_etf_observation_to_pit_row,
    select_etf_pit_rows,
)


def observation(
    session_date: str,
    knowledge_at: str | None,
    total: float,
    *,
    asset: str = "BTC",
    vintage_seq: int = 1,
    knowledge_status: str = "OBSERVED",
    finality_status: str = "VERIFIED_STABLE_AT_OBSERVATION",
    completeness_status: str = "COMPLETE",
) -> dict:
    observed_at = knowledge_at or "2026-07-20T12:00:00Z"
    verification = knowledge_at if knowledge_status == "OBSERVED" else None
    return {
        "contract": "ETF_OBSERVATION_v1",
        "asset": asset,
        "session_date": session_date,
        "is_trading_session": True,
        "source_observed_at_utc": observed_at,
        "observed_at_status": "OBSERVED",
        "verification_completed_at_utc": verification,
        "knowledge_available_at_utc": knowledge_at,
        "knowledge_time_status": knowledge_status,
        "knowledge_rule_id": ETF_PIT_DECISION_ID if knowledge_status == "OBSERVED" else None,
        "schema": {
            "source_ticker_row": ["IBIT", "FBTC"],
            "schema_id": "TEST_KNOWN_SCHEMA",
            "schema_hash": "TEST",
            "schema_status": "KNOWN_SCHEMA",
        },
        "row": {
            "fund_cells": {
                "IBIT": {"raw": str(total), "value": total, "cell_status": "REPORTED"},
                "FBTC": {"raw": "0", "value": 0.0, "cell_status": "REPORTED_ZERO"},
            },
            "reported_total": total,
            "calculated_total": total,
            "parity": True,
            "unknown_cells": 0,
            "all_dash_row": False,
        },
        "completeness_status": completeness_status,
        "finality_status": finality_status,
        "revision": {
            "vintage_seq": vintage_seq,
            "supersedes_row_hash": None,
            "revision_kind": "NONE" if vintage_seq == 1 else "SOURCE_CORRECTION",
            "total_delta": None,
        },
        "provenance": {
            "producer": "TEST",
            "evidence_path": "TEST",
            "table_content_sha256": "TEST",
            "row_hash": f"TEST-{session_date}-{vintage_seq}",
        },
    }


class EtfPitReplayV2Test(unittest.TestCase):
    def test_pre_capture_session_is_mechanically_ineligible_even_if_seen_later(self):
        row = map_etf_observation_to_pit_row(
            observation("2026-07-14", "2026-07-16T06:00:00Z", 10.0)
        )
        self.assertIsNone(row)

    def test_lower_bound_or_provisional_observation_never_gets_synthetic_knowledge(self):
        lower_bound = observation(
            "2026-07-16",
            None,
            10.0,
            knowledge_status="LOWER_BOUND_ONLY",
        )
        provisional = observation(
            "2026-07-16",
            "2026-07-17T06:00:00Z",
            10.0,
            finality_status="PROVISIONAL",
        )
        self.assertIsNone(map_etf_observation_to_pit_row(lower_bound))
        self.assertIsNone(map_etf_observation_to_pit_row(provisional))

    def test_feature_knowledge_time_is_cumulative_max_across_input_rows(self):
        observations = [
            observation("2026-07-15", "2026-07-18T08:00:00Z", 10.0),
            observation("2026-07-16", "2026-07-17T06:00:00Z", 20.0),
        ]
        rows = select_etf_pit_rows(observations, "BTC", "2026-07-19T00:00:00Z")
        features = build_etf_trailing_pit(rows, "BTC")
        self.assertEqual(features[0]["feature_knowledge_available_at_utc"], "2026-07-18T08:00:00Z")
        self.assertEqual(features[1]["feature_knowledge_available_at_utc"], "2026-07-18T08:00:00Z")
        self.assertEqual(features[1]["knowledge_rule_id"], ETF_PIT_DECISION_ID)

    def test_post_cutoff_revision_cannot_enter_earlier_replay(self):
        v1 = observation("2026-07-16", "2026-07-17T06:34:00Z", 79.1, vintage_seq=1)
        v2 = observation("2026-07-16", "2026-07-18T06:00:00Z", 80.0, vintage_seq=2)

        early = select_etf_pit_rows([v1, v2], "BTC", "2026-07-17T12:00:00Z")
        late = select_etf_pit_rows([v1, v2], "BTC", "2026-07-19T00:00:00Z")

        self.assertEqual(len(early), 1)
        self.assertEqual(early[0]["total_usd_millions"], 79.1)
        self.assertEqual(early[0]["vintage_seq"], 1)
        self.assertEqual(late[0]["total_usd_millions"], 80.0)
        self.assertEqual(late[0]["vintage_seq"], 2)

    def test_unknown_schema_fails_closed(self):
        obs = observation("2026-07-16", "2026-07-17T06:34:00Z", 79.1)
        obs["schema"]["schema_status"] = "UNKNOWN_SCHEMA_REVISION"
        with self.assertRaises(ValueError):
            map_etf_observation_to_pit_row(obs)


if __name__ == "__main__":
    unittest.main()
