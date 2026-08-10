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


def frag_base(counts):
    patterns = []
    for pattern_id, count in zip(spar_v1.PATTERNS, counts):
        events = []
        for i in range(count):
            events.append({
                "outcomes": {
                    "72": {
                        "status": "MATURED",
                        "btc_return_pct": 1.0 if i % 3 else -0.5,
                    }
                }
            })
        patterns.append({"pattern_id": pattern_id, "matured_72h_count": count, "events": events})
    return {"status": "READY_FOR_ROBUSTNESS_REVIEW", "patterns": patterns}


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
        self.assertEqual(report["scientific_status"], "METHODS_REQUIRES_PROSPECTIVE_HARDENING_DESCRIPTIVE_ONLY")
        self.assertFalse(report["claim_boundary"]["incremental_value_beyond_single_sensor_states_established"])

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
            self.assertEqual(snaps[0].source_contract, spar_v1.V3_CONTRACT)

    def test_v3_rejects_missing_previous_completed_hour_without_fill_and_audits_drop(self):
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
            snaps,audit=spar_v1.load_snapshots_audit(captures)
            self.assertEqual(snaps,[])
            self.assertEqual(audit["dropped_by_reason"]["V3_MISSING_EXACT_PREVIOUS_COMPLETED_HOUR_SPOT"],1)
            self.assertFalse(audit["silent_drop_policy"])

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

    def test_p3_same_transition_behavior_is_preserved_as_v1_limitation(self):
        t0=datetime(2026,1,1,tzinfo=timezone.utc)
        a=spar_v1.load_snapshot(self._write_one(capture(t0,100,10,.10,60,40,.001,1000)))
        b=spar_v1.load_snapshot(self._write_one(capture(t0+timedelta(hours=4),101,9,.09,50,50,.001,1000)))
        events=spar_v1.detect_events([a,b])
        self.assertEqual(events["SPAR-P3"],[1])

    def test_evidence_and_adapter_phases_are_explicit(self):
        self.assertEqual(spar_v1.evidence_phase(datetime(2026,8,8,7,0,tzinfo=timezone.utc)),"RETROSPECTIVE_ARCHIVE_REPLAY")
        self.assertEqual(spar_v1.evidence_phase(datetime(2026,8,8,8,0,tzinfo=timezone.utc)),"PROSPECTIVE_POST_PREREGISTRATION")
        self.assertEqual(spar_v1.adapter_phase(datetime(2026,8,9,19,0,tzinfo=timezone.utc)),"PRE_ADAPTER_V2_CUTOVER")
        self.assertEqual(spar_v1.adapter_phase(datetime(2026,8,9,20,0,tzinfo=timezone.utc)),"POST_ADAPTER_V2_CUTOVER")

    def test_top_level_base_gate_requires_all_patterns(self):
        rows=[
            {"pattern_id":"SPAR-P1","matured_72h_count":5},
            {"pattern_id":"SPAR-P2","matured_72h_count":5},
            {"pattern_id":"SPAR-P3","matured_72h_count":4},
        ]
        self.assertFalse(spar_v1.all_patterns_at_least(rows,5))
        rows[-1]["matured_72h_count"]=5
        self.assertTrue(spar_v1.all_patterns_at_least(rows,5))

    def test_fragility_does_not_emit_loo_below_ten(self):
        report=spar_v1.build_fragility(frag_base([9,10,10]),min_events=10)
        self.assertEqual(report["status"],"INSUFFICIENT_EVIDENCE")
        p1=next(p for p in report["patterns"] if p["pattern_id"]=="SPAR-P1")
        self.assertNotIn("leave_one_out_sign_stable",p1)

    def test_fragility_never_becomes_robustness_ready_from_loo_alone(self):
        report=spar_v1.build_fragility(frag_base([10,10,10]),min_events=10)
        self.assertEqual(report["status"],"METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN")
        self.assertNotEqual(report["status"],"ROBUSTNESS_REVIEW_READY")
        for row in report["patterns"]:
            self.assertIn("leave_one_out_sign_stable",row)
            self.assertEqual(row["loo_interpretation"],"SINGLE_POINT_DELETION_DIAGNOSTIC_NOT_EFFECT_EVIDENCE_NOT_NULL_TEST")

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
            self.assertFalse(state["etf_execution_authorized"])

    def test_queue_requires_all_patterns_at_ten_before_fragility(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"03_DAILY_CAPTURE_LOGS/captures").mkdir(parents=True)
            (root/"research/experiments/spar_v1").mkdir(parents=True)
            now="2026-08-10T10:00:00Z"
            (root/"03_DAILY_CAPTURE_LOGS/captures/LATEST.json").write_text(json.dumps({"captured_at_utc":now}))
            report=frag_base([10,10,9])
            report["source"]={"max_timestamp_utc":now}
            (root/"research/experiments/spar_v1/LATEST_REPORT.json").write_text(json.dumps(report))
            state=rq.decide(root,{"contract":"SEQUENTIAL_RESEARCH_QUEUE_v1"})
            self.assertEqual(state["next_action"],"WAIT")
            report=frag_base([10,10,10])
            report["source"]={"max_timestamp_utc":now}
            (root/"research/experiments/spar_v1/LATEST_REPORT.json").write_text(json.dumps(report))
            state=rq.decide(root,{"contract":"SEQUENTIAL_RESEARCH_QUEUE_v1"})
            self.assertEqual(state["next_action"],"RUN_SPAR_FRAGILITY")

    def test_queue_blocks_etf_after_methods_blocked_fragility(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            (root/"03_DAILY_CAPTURE_LOGS/captures").mkdir(parents=True)
            (root/"research/experiments/spar_v1").mkdir(parents=True)
            now="2026-08-10T10:00:00Z"
            (root/"03_DAILY_CAPTURE_LOGS/captures/LATEST.json").write_text(json.dumps({"captured_at_utc":now}))
            report=frag_base([10,10,10]); report["source"]={"max_timestamp_utc":now}
            (root/"research/experiments/spar_v1/LATEST_REPORT.json").write_text(json.dumps(report))
            (root/"research/experiments/spar_v1/LATEST_FRAGILITY_REPORT.json").write_text(json.dumps({"status":"METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN"}))
            state=rq.decide(root,{"contract":"SEQUENTIAL_RESEARCH_QUEUE_v1"})
            self.assertEqual(state["next_action"],"WAIT")
            self.assertEqual(state["reason"],"SPAR_FRAGILITY_METHODS_BLOCKED_PLACEBO_REGIME_NOT_FROZEN")
            self.assertFalse(state["etf_execution_authorized"])


if __name__=="__main__":
    unittest.main()
