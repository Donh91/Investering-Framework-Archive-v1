import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.experiments import etf_absorption_transmission_v1 as etf


def owner(session, known_at, btc=100.0, eth=50.0, *, verified=True):
    rows = [
        {"asset":"BTC","date":session,"fund_headers":["A"],"fund_values":[btc],"reported_total":btc,"calculated_total":btc,"total_parity":True,"session_final":True},
        {"asset":"ETH","date":session,"fund_headers":["A"],"fund_values":[eth],"reported_total":eth,"calculated_total":eth,"total_parity":True,"session_final":True},
    ]
    sig = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "contract":"DAILY_SETTLED_ETF_CALIBRATION_v1",
        "authority":"SHADOW_CALIBRATION_INPUT_ONLY",
        "session_date":session,
        "retrieved_at_utc":known_at,
        "verification":{
            "retrieval_count":2 if verified else 1,
            "minimum_separation_seconds":60,
            "rows_identical_across_retrievals":True,
            "all_fund_cells_known":True,
            "total_parity_required":True,
            "source":"FARSIDE_CANONICAL_TABLES",
        },
        "rows":rows,
        "canonical_data_ping":False,
        "framework_state_change":False,
        "portfolio_action":False,
        "row_signature_sha256":sig,
    }


class TestEtfOwnerAdapter(unittest.TestCase):
    def write(self, root, name, obj):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj))
        return path

    def test_future_record_is_never_visible(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"future.json",owner("2026-08-07","2026-08-10T08:06:00Z"))
            result=etf.asof_join(etf.load_owner_records(root), datetime(2026,8,10,8,5,tzinfo=timezone.utc))
            self.assertEqual(result["status"],"UNAVAILABLE")

    def test_latest_known_revision_wins_only_after_known_at(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"v1.json",owner("2026-08-07","2026-08-08T06:06:00Z",100,50))
            self.write(root,"v2.json",owner("2026-08-07","2026-08-09T06:06:00Z",110,55))
            rows=etf.load_owner_records(root)
            early=etf.asof_join(rows, datetime(2026,8,8,12,tzinfo=timezone.utc))
            late=etf.asof_join(rows, datetime(2026,8,9,12,tzinfo=timezone.utc))
            self.assertEqual(early["raw_reported_totals"]["BTC"],100)
            self.assertEqual(late["raw_reported_totals"]["BTC"],110)

    def test_weekend_has_no_synthetic_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"friday.json",owner("2026-08-07","2026-08-08T06:06:00Z"))
            sunday=etf.asof_join(etf.load_owner_records(root), datetime(2026,8,9,18,tzinfo=timezone.utc))
            self.assertEqual(sunday["session_date"],"2026-08-07")
            self.assertEqual(sunday["session_age_calendar_days_at_cutoff"],2)
            self.assertFalse(sunday["synthetic_weekend_rows"])

    def test_late_publication_is_not_backdated_to_session(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"late.json",owner("2026-08-07","2026-08-10T08:06:00Z"))
            rows=etf.load_owner_records(root)
            before=etf.asof_join(rows, datetime(2026,8,10,7,0,tzinfo=timezone.utc))
            after=etf.asof_join(rows, datetime(2026,8,10,9,0,tzinfo=timezone.utc))
            self.assertEqual(before["status"],"UNAVAILABLE")
            self.assertEqual(after["status"],"AVAILABLE")
            self.assertEqual(after["known_at_utc"],"2026-08-10T08:06:00Z")

    def test_incomplete_verification_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=self.write(root,"bad.json",owner("2026-08-07","2026-08-08T06:06:00Z",verified=False))
            with self.assertRaisesRegex(ValueError,"VERIFICATION_FAILURE"):
                etf.validate_owner_record(path)

    def test_unknown_fund_cell_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            obj=owner("2026-08-07","2026-08-08T06:06:00Z")
            obj["rows"][0]["fund_values"]=[None]
            obj["row_signature_sha256"]=etf.rows_signature(obj["rows"])
            path=self.write(root,"bad.json",obj)
            with self.assertRaisesRegex(ValueError,"UNKNOWN_FUND_CELL"):
                etf.validate_owner_record(path)

    def test_signature_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            obj=owner("2026-08-07","2026-08-08T06:06:00Z")
            obj["row_signature_sha256"]="0"*64
            path=self.write(root,"bad.json",obj)
            with self.assertRaisesRegex(ValueError,"ROW_SIGNATURE_MISMATCH"):
                etf.validate_owner_record(path)

    def test_preflight_does_not_run_experiment_or_call_sources(self):
        with tempfile.TemporaryDirectory() as td:
            result=etf.readiness(Path(td))
            self.assertEqual(result["status"],"VERIFIED_ADAPTER_PENDING_FIRST_OWNER_ROW")
            self.assertEqual(result["external_calls_performed"],0)
            self.assertFalse(result["flow_state_derived"])
            self.assertFalse(result["event_definition_applied"])
            self.assertFalse(result["experiment_executed"])


if __name__=="__main__":
    unittest.main()
