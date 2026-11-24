import hashlib
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[2] / "research/s1_root_v2"
with patch.object(sys, "path", [str(ROOT), *sys.path]):
    import replay
    import simulator

class ReplayTest(unittest.TestCase):
    def run_row(self, **changes):
        row = dict(schema="S1_REPLAY_FIXTURE_v1", kind="SYNTHETIC",
                   observed_at="2026-01-01T00:00:00Z",
                   available_at="2026-01-01T00:01:00Z",
                   evidence=dict.fromkeys(simulator.GATES, True))
        row.update(changes)
        raw = json.dumps(row).encode()
        return replay.replay(raw, hashlib.sha256(raw).hexdigest(), "2026-01-01T00:02:00Z")
    def test_synthetic(self):
        r = self.run_row()
        self.assertEqual(r["decision"], "SIMULATE_MERGE")
        self.assertFalse(r["comparable"])
    def test_future(self):
        self.assertEqual(self.run_row(available_at="2026-01-01T00:03:00Z")["reason"], "future_evidence")
    def test_historical_claim(self):
        self.assertEqual(self.run_row(kind="HISTORICAL")["status"], "UNKNOWN")
    def test_bad_hash(self):
        self.assertEqual(replay.replay(b"{}", "wrong", "2026-01-01T00:02:00Z")["reason"], "hash")
    def test_duplicate(self):
        raw = b'{"schema":1,"schema":2}'
        self.assertEqual(replay.replay(raw, hashlib.sha256(raw).hexdigest(), "2026-01-01T00:02:00Z")["reason"], "malformed")
