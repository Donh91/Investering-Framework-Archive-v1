import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.experiments import spar_v1
from scripts.experiments import sequential_research_queue as rq


def capture(ts, btc, eth, ethbtc, adv, dec, funding, oi):
    return {
        "contract": "DAILY_RAW_CAPTURE_INDEX_v2",
        "captured_at_utc": ts.isoformat().replace("+00:00", "Z"),
        "market_metrics": {
            "breadth": {"advancers": adv, "decliners": dec},
            "spot": {"BTCUSDT": {"close": btc}, "ETHUSDT": {"close": eth}, "ETHBTC": {"close": ethbtc}},
            "derivatives": {"BTC-USDT-SWAP": {"funding": {"funding_rate": funding}, "open_interest": {"open_interest_ccy": oi}}},
        },
    }


class TestSpar(unittest.TestCase):
    def test_sequence_is_detected_without_future_data(self):
        t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        rows = [
            capture(t0, 100, 10, .10, 60, 40, .001, 1000),
            capture(t0+timedelta(hours=4), 101, 10, .10, 50, 50, .001, 1000),
            capture(t0+timedelta(hours=8), 102, 10, .10, 50, 50, .002, 1100),
            capture(t0+timedelta(hours=12), 102, 9.9, .099, 50, 50, .002, 1100),
        ]
        events = spar_v1.detect_events([spar_v1.load_snapshot(self._write_one(x)) for x in rows])
        self.assertEqual(events["SPAR-P1"], [3])

    def _write_one(self, obj):
        d = Path(tempfile.mkdtemp())
        p = d / "x.json"
        p.write_text(json.dumps(obj))
        return p

    def test_replay_stays_insufficient_without_matured_events(self):
        t0 = datetime(2026, 1, 1, tzinfo=timezone.utc)
        snaps=[]
        for i in range(4):
            p=self._write_one(capture(t0+timedelta(hours=4*i),100+i,10,.1,60-i,40+i,.001,1000+i))
            snaps.append(spar_v1.load_snapshot(p))
        report=spar_v1.build_replay(snaps, min_matured_events=5)
        self.assertEqual(report["status"], "INSUFFICIENT_EVIDENCE")
        self.assertFalse(report["method"]["future_leakage"])

    def test_queue_never_authorizes_paid_calls(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"03_DAILY_CAPTURE_LOGS/captures").mkdir(parents=True)
            (root/"03_DAILY_CAPTURE_LOGS/captures/LATEST.json").write_text(json.dumps({"captured_at_utc":"2026-08-08T05:00:00Z"}))
            state=rq.decide(root,{"contract":"SEQUENTIAL_RESEARCH_QUEUE_v1"})
            self.assertEqual(state["next_action"],"RUN_SPAR_BASE")
            self.assertEqual(state["budget_decision"]["new_cfgi_credits_authorized"],0)
            self.assertEqual(state["budget_decision"]["new_openai_usd_authorized"],0.0)
            self.assertFalse(state["budget_decision"]["paid_rerun_pdlt_authorized"])

if __name__ == "__main__":
    unittest.main()
