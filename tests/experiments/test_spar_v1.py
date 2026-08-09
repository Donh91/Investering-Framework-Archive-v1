import csv
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


def capture_v3(ts, adv, dec, funding, oi):
    return {
        "contract": "DAILY_LIVE_ANCHOR_INDEX_v3",
        "captured_at_utc": ts.isoformat().replace("+00:00", "Z"),
        "market_metrics": {
            "breadth": {"advancers": adv, "decliners": dec},
            "derivatives": {"BTC-USDT-SWAP": {"funding": {"funding_rate": funding}, "open_interest": {"open_interest_ccy": oi}}},
        },
    }


def write_hourly(root: Path, rows):
    root.mkdir(parents=True, exist_ok=True)
    p = root / "2026-01-01.csv"
    fields = ["timestamp_utc", "btc_close", "eth_close", "ethbtc_close", "spot_status"]
    with p.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    return p


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

    def test_v3_uses_exact_previous_completed_hour_not_current_hour(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            captures=root/"captures"
            hourly=root/"hourly"
            captures.mkdir()
            t=datetime(2026,1,1,10,15,tzinfo=timezone.utc)
            (captures/"a.json").write_text(json.dumps(capture_v3(t,60,40,.001,1000)))
            write_hourly(hourly,[
                {"timestamp_utc":"2026-01-01T09:00:00Z","btc_close":"100","eth_close":"10","ethbtc_close":"0.1","spot_status":"PASS"},
                {"timestamp_utc":"2026-01-01T10:00:00Z","btc_close":"999","eth_close":"99","ethbtc_close":"0.9","spot_status":"PASS"},
            ])
            snaps=spar_v1.load_snapshots(captures)
            self.assertEqual(len(snaps),1)
            self.assertEqual(snaps[0].btc,100.0)
            self.assertEqual(snaps[0].t,t)

    def test_v3_rejects_missing_previous_completed_hour_without_fill(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            captures=root/"captures"
            hourly=root/"hourly"
            captures.mkdir()
            t=datetime(2026,1,1,10,15,tzinfo=timezone.utc)
            (captures/"a.json").write_text(json.dumps(capture_v3(t,60,40,.001,1000)))
            write_hourly(hourly,[
                {"timestamp_utc":"2026-01-01T08:00:00Z","btc_close":"100","eth_close":"10","ethbtc_close":"0.1","spot_status":"PASS"},
                {"timestamp_utc":"2026-01-01T10:00:00Z","btc_close":"999","eth_close":"99","ethbtc_close":"0.9","spot_status":"PASS"},
            ])
            self.assertEqual(spar_v1.load_snapshots(captures),[])

    def test_mixed_v2_v3_history_advances_source_with_versioned_adapter(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            captures=root/"captures"
            hourly=root/"hourly"
            captures.mkdir()
            t0=datetime(2026,1,1,8,0,tzinfo=timezone.utc)
            t1=datetime(2026,1,1,10,15,tzinfo=timezone.utc)
            (captures/"old.json").write_text(json.dumps(capture(t0,100,10,.1,60,40,.001,1000)))
            (captures/"new.json").write_text(json.dumps(capture_v3(t1,59,41,.002,1100)))
            write_hourly(hourly,[
                {"timestamp_utc":"2026-01-01T09:00:00Z","btc_close":"101","eth_close":"10.1","ethbtc_close":"0.099","spot_status":"PASS"},
            ])
            snaps=spar_v1.load_snapshots(captures)
            report=spar_v1.build_replay(snaps,min_matured_events=5)
            self.assertEqual(report["source"]["snapshot_count"],2)
            self.assertEqual(report["source"]["max_timestamp_utc"],"2026-01-01T10:15:00Z")
            self.assertEqual(report["method"]["input_adapter"],"SPAR_INPUT_ADAPTER_v2")
            self.assertFalse(report["method"]["interpolation"])
            self.assertFalse(report["method"]["forward_fill"])

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
