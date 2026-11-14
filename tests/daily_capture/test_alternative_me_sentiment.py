import unittest
import json
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.data_terminal.alternative_me_sentiment import normalize
from scripts.daily_capture.build_capture_index import extract_metrics


class AlternativeSentimentTest(unittest.TestCase):
    def setUp(self):
        self.now = datetime(2026, 11, 14, 12, tzinfo=timezone.utc)
        self.row = {"value": "27", "value_classification": "Fear", "timestamp": str(int(self.now.timestamp()))}

    def test_valid_is_separate_and_research_only(self):
        out = normalize({"data": [self.row]}, self.now)
        self.assertTrue(out["not_cfgi"])
        self.assertEqual(out["source"], "ALTERNATIVE_ME_FNG")
        self.assertEqual(out["authority"], "RESEARCH_ONLY_NOT_OFFICIAL_NOT_DECISION_INPUT")
        self.assertIsNone(out["source_first_known_at_utc"])
        self.assertIn("alternative.me", out["attribution"])

    def test_missing_bad_numeric_and_future_or_old_fail(self):
        for change in ({"value": "101"}, {"value": True}, {"value": "NaN"},
                       {"timestamp": str(int((self.now + timedelta(seconds=1)).timestamp()))},
                       {"timestamp": str(int((self.now - timedelta(hours=49)).timestamp()))},
                       {"value_classification": "UNKNOWN"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                normalize({"data": [{**self.row, **change}]}, self.now)
        for payload in ({}, {"data": []}, {"data": [self.row, self.row]}):
            with self.subTest(payload=payload), self.assertRaises(ValueError):
                normalize(payload, self.now)

    def test_capture_never_places_alternative_in_cfgi_lane(self):
        with tempfile.TemporaryDirectory() as root:
            p = Path(root) / "alternative-me-sentiment-output" / "owner_snapshot.json"
            p.parent.mkdir()
            p.write_text(json.dumps(normalize({"data": [self.row]}, self.now)))
            metrics = extract_metrics(Path(root))
            self.assertEqual(metrics["sentiment"]["cfgi"], {})
            self.assertEqual(metrics["research_context"]["alternative_me_sentiment"]["source"], "ALTERNATIVE_ME_FNG")
            doc = json.loads(p.read_text())
            doc["not_cfgi"] = False
            p.write_text(json.dumps(doc))
            self.assertNotIn("research_context", extract_metrics(Path(root)))


if __name__ == "__main__":
    unittest.main()
