"""Independent negative tests for research-only W45 forward baseline packet."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from scripts.research.verify_w45_midweek_shadow_benchmark import verify, recompute


PACKET = (Path(__file__).resolve().parents[2] /
          "06_RESEARCH_LAB/mission_packets/2026-11-05__W45_MIDWEEK_PROSPECTIVE_BENCHMARK_v1.json")


def load():
    return json.loads(PACKET.read_text())


def test_exact_frozen_shadow_packet_replays_without_originating_cn_prices():
    packet = load()
    result = verify(packet)
    assert result["status"] == "PASS_RESEARCH_ONLY"
    assert result["rows"] == 238
    assert result["forecast_points"] == 8
    assert result["official_cn_issued_points"] == 0
    for asset in ("BTC", "ETH"):
        rows = packet["forecast"]["assets"][asset]["forecast"]
        assert [r["day"] for r in rows] == [4, 5, 6, 7]
        assert [r["target_close_at_utc"] for r in rows] == [
            "2026-11-06T00:00:00Z", "2026-11-07T00:00:00Z",
            "2026-11-08T00:00:00Z", "2026-11-09T00:00:00Z",
        ]
        assert all(r["heuristic_terminal_close_low"] <
                   r["B0_persistence_expected_close"] <
                   r["heuristic_terminal_close_high"] for r in rows)


@pytest.mark.parametrize("mutation, match", [
    ("price", "RESEARCH_FORECAST_SOURCE_RECOMPUTATION_MISMATCH"),
    ("duplicate_hour", "MISSING_DUPLICATE_OR_UNSORTED_HOUR"),
    ("future_source", "CAPTURE_TIME_BEFORE_CANDLE_OR_AFTER_ISSUE"),
    ("backdated_issuance", "W45_RESEARCH_PIT_BOUNDARY_INVALID"),
    ("fake_authority", "RESEARCH_AUTHORITY_LEAK"),
    ("fake_original", "ORIGINAL_FORECAST_MISREPRESENTED"),
    ("wrong_quote", "UNVERIFIED_SOURCE_QUOTE_OR_FILES"),
])
def test_adversarial_replay_fails_closed(mutation, match):
    packet = copy.deepcopy(load())
    if mutation == "price":
        packet["observations"][-1]["BTC_USDT"] += 123
    elif mutation == "duplicate_hour":
        packet["observations"][-1]["candle_close_at_utc"] = packet["observations"][-2]["candle_close_at_utc"]
    elif mutation == "future_source":
        packet["observations"][-1]["source_window_end_utc"] = "2026-11-06T00:00:00Z"
    elif mutation == "backdated_issuance":
        packet["generated_at_utc"] = packet["forecast"]["origin_utc"] = "2026-11-04T21:00:00Z"
    elif mutation == "fake_authority":
        packet["forecast"]["site_blue_original_forecast_eligible"] = True
    elif mutation == "fake_original":
        packet["original_W45_daily_price_path_status"]["BTC"] = "PUBLISHED"
    elif mutation == "wrong_quote":
        packet["source"]["assets_quote"] = "USD"
    with pytest.raises(ValueError, match=match):
        verify(packet)


def test_true_candle_clock_is_distinct_from_capture_batch_window():
    packet = load()
    delayed = [r for r in packet["observations"]
               if r["source_window_end_utc"] != r["candle_close_at_utc"]]
    assert delayed
    assert recompute(packet)["BTC"][0]["target_close_at_utc"] == "2026-11-06T00:00:00Z"
    assert packet["source"]["provider_first_known_verified"] is False
