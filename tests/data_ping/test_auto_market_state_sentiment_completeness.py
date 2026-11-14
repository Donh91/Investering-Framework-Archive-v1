"""Fail-closed CFGI source-health checks for original Auto Market State producer.

Research/Codex candidate: codex-research-compass-sentiment-false-pass-v1.
Archived packets are read-only evidence of a historical false PASS and a
genuinely complete positive control, not prospective market predictions.
No provider calls, no historical packet writes and no score/policy updates.
"""
from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from scripts.data_ping.auto_market_state import sentiment_source_health

ROOT = Path(__file__).resolve().parents[2]
NEGATIVE = ROOT / "04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/11/09/224533_3b8c80cbc645.json"
POSITIVE = ROOT / "04_MARKET_LEARNING/entry_signals/auto_market_state/runs/2026/11/13/132734_4bf307cd2027.json"


class SentimentSourceCompletenessTests(unittest.TestCase):
    @staticmethod
    def complete():
        return {"cfgi": {"symbols": {
            "MARKET": {"classification": "Fear", "score": 36.5},
            "BTC": {"classification": "Fear", "score": 26.5},
            "ETH": {"classification": "Fear", "score": 35.5},
        }}}

    def test_archived_false_pass_is_now_unavailable_without_rewrite(self):
        packet = json.loads(NEGATIVE.read_text(encoding="utf-8"))
        self.assertEqual(packet["source_health"]["sentiment"]["status"], "PASS")
        sentiment = packet["normalized_state"]["sentiment"]
        self.assertEqual(sentiment, {"cfgi": {}})
        self.assertEqual(sentiment_source_health(sentiment), {
            "status": "UNAVAILABLE",
            "classification": "LIVE_ANCHOR_SENTIMENT_CFGI_REQUIRED_FIELDS_MISSING",
        })

    def test_archived_complete_positive_remains_pass(self):
        packet = json.loads(POSITIVE.read_text(encoding="utf-8"))
        self.assertEqual(packet["source_health"]["sentiment"]["status"], "PASS")
        result = sentiment_source_health(packet["normalized_state"]["sentiment"])
        self.assertEqual(result, {
            "status": "PASS",
            "classification": "LIVE_ANCHOR_SENTIMENT",
        })

    def test_empty_truthy_wrappers_and_missing_symbols_never_pass(self):
        examples = [None, {}, [], {"cfgi": {}}, {"cfgi": []},
                    {"other": 1}, {"cfgi": {"symbols": {}}},
                    {"cfgi": {"symbols": {"MARKET": {"score": 40, "classification": "Fear"}}}}]
        for example in examples:
            with self.subTest(value=example):
                self.assertEqual(sentiment_source_health(example)["status"], "UNAVAILABLE")

    def test_malformed_required_symbol_values_fail_closed(self):
        cases = [
            ("no_btc", lambda p: p["cfgi"]["symbols"].pop("BTC")),
            ("market_class_missing", lambda p: p["cfgi"]["symbols"]["MARKET"].pop("classification")),
            ("market_class_blank", lambda p: p["cfgi"]["symbols"]["MARKET"].update(classification="  ")),
            ("market_class_not_string", lambda p: p["cfgi"]["symbols"]["MARKET"].update(classification=1)),
            ("btc_bool", lambda p: p["cfgi"]["symbols"]["BTC"].update(score=True)),
            ("eth_nan", lambda p: p["cfgi"]["symbols"]["ETH"].update(score=float("nan"))),
            ("market_inf", lambda p: p["cfgi"]["symbols"]["MARKET"].update(score=float("inf"))),
            ("btc_numeric_string", lambda p: p["cfgi"]["symbols"]["BTC"].update(score="26.5")),
            ("eth_not_mapping", lambda p: p["cfgi"]["symbols"].update(ETH=[])),
        ]
        for label, mutate in cases:
            with self.subTest(case=label):
                p = self.complete()
                mutate(p)
                self.assertEqual(sentiment_source_health(p)["status"], "UNAVAILABLE")

    def test_healthy_fields_are_only_presence_and_finiteness_not_new_thresholds(self):
        p = self.complete()
        p["cfgi"]["symbols"]["MARKET"]["score"] = 0
        p["cfgi"]["symbols"]["BTC"]["score"] = 100
        self.assertEqual(sentiment_source_health(p)["status"], "PASS")
        unchanged = copy.deepcopy(p)
        self.assertEqual(sentiment_source_health(p)["status"], "PASS")
        self.assertEqual(p, unchanged)


if __name__ == "__main__":
    unittest.main()
