"""Adversarial Task2 CFGI source metadata tests (never score or price outputs)."""
import copy
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from scripts.research import task2_cfgi_capture_clock_audit_v1 as m

def z(t):
    return t.isoformat(timespec='seconds').replace('+00:00','Z')
T=datetime(2026,10,18,12,37,19,tzinfo=timezone.utc)

def fixture(*, clock_split=False):
    times={"MARKET":T-timedelta(minutes=16,seconds=53) if clock_split else T-timedelta(minutes=3),
           "BTC":T-timedelta(minutes=1,seconds=19) if clock_split else T-timedelta(minutes=3),
           "ETH":T-timedelta(minutes=1,seconds=19) if clock_split else T-timedelta(minutes=3)}
    rows=[]
    for symbol,t in times.items():
        rows.append({"symbol":symbol,"timestamp":z(t),"age_seconds":int((T-t).total_seconds()),
                     "owner_status":"PASS","stale":False,
                     # Values purposely poison-tested for absence from public report.
                     "score":987.65,"price":999.9,"components":{"orders":-777.7}})
    fields=sorted(m.EXPECTED_FIELDS)
    return {"contract":"DAILY_LIVE_ANCHOR_INDEX_v3","run_id":"gh-3-1",
            "captured_at_utc":z(T+timedelta(seconds=1)),
            "owners":[{"owner_id":"cfgi_sentiment","status":"PASS","collector_exit_code":0,
                       "files":[{"path":"cfgi-owner-output/owner_snapshot.json","sha256":"a"*64,
                                 "summary":{"source":"CFGI_V3","timeframe":"4h","fields":fields,
                                            "retrieved_at_utc":z(T),"rows":rows}},
                                {"path":"cfgi-owner-output/receipt.json","sha256":"b"*64,
                                 "summary":{"timeframe":"4h","fields":fields,"retrieved_at_utc":z(T),
                                            "row_count":3,"status":"PASS"}}]}]}

class CFGIReadbackScienceTests(unittest.TestCase):
    def test_authorized_metadata_no_provider_values(self):
        out=m.permitted_metadata(fixture(),source_name="2026.json")
        self.assertEqual(out["clock_quality"],"SYMBOL_CLOCKS_EQUAL")
        self.assertNotIn("score",str(out))
        self.assertNotIn("987.65",str(out))
        self.assertNotIn("price",str(out).lower())
        self.assertNotIn("components",str(out))
        self.assertFalse(out["provider_first_publication_verified"])
        self.assertEqual(set(out["source_symbol_times"]),{"BTC","ETH","MARKET"})
    def test_symbol_clock_split_cannot_be_silently_synchronized(self):
        out=m.permitted_metadata(fixture(clock_split=True),source_name="2026.json")
        self.assertEqual(out["within_capture_symbol_clock_skew_seconds"],934)
        self.assertEqual(out["clock_quality"],"SYMBOL_CLOCKS_NOT_IDENTICAL")
    def test_source_clock_future_is_rejected(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][0]["timestamp"]=z(T+timedelta(seconds=1))
        with self.assertRaisesRegex(ValueError,"ORIGINAL_ROW_FROM_THE_FUTURE"):
            m.permitted_metadata(x,source_name="a.json")
    def test_retrieval_clock_cannot_be_after_capture(self):
        x=fixture();x["captured_at_utc"]=z(T-timedelta(seconds=5))
        with self.assertRaisesRegex(ValueError,"RETRIEVAL_CLOCK_CONFLICT"):
            m.permitted_metadata(x,source_name="a.json")
    def test_negative_age_fails_closed(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][0]["age_seconds"]=-1
        with self.assertRaisesRegex(ValueError,"ROW_AGE_NOT_RECONCILED"):
            m.permitted_metadata(x,source_name="a.json")
    def test_replayed_old_age_fails(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][1]["age_seconds"]+=100
        with self.assertRaisesRegex(ValueError,"ROW_AGE_NOT_RECONCILED"):
            m.permitted_metadata(x,source_name="a.json")
    def test_stale_or_unavailable_row_is_not_assessable(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][0]["stale"]=True
        with self.assertRaisesRegex(ValueError,"STALE_CFGI_ROW"):
            m.permitted_metadata(x,source_name="a.json")
    def test_missing_symbol_not_three(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"].pop()
        with self.assertRaisesRegex(ValueError,"CFGI_SYMBOL_POPULATION_MISMATCH"):
            m.permitted_metadata(x,source_name="a.json")
    def test_duplicate_symbol_not_three(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][2]["symbol"]="BTC"
        with self.assertRaisesRegex(ValueError,"CFGI_SYMBOL_POPULATION_MISMATCH"):
            m.permitted_metadata(x,source_name="a.json")
    def test_fake_1h_not_accepted_as_original_4h(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["timeframe"]="1h"
        with self.assertRaisesRegex(ValueError,"TIMEFRAME_CHANGED"):
            m.permitted_metadata(x,source_name="a.json")
    def test_synthetic_price_field_not_authorized_by_source_metadata(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["rows"][0]["price"]=0
        self.assertNotIn("price",str(m.permitted_metadata(x,source_name="a.json")).lower())
    def test_no_original_owner_receipt_fails(self):
        x=fixture();x["owners"][0]["files"][0]["sha256"]=""
        with self.assertRaisesRegex(ValueError,"UNBOUND_ORIGINAL_OWNER_FILE_SHA256"):
            m.permitted_metadata(x,source_name="a.json")
    def test_no_replacement_with_latest_source(self):
        x=fixture();x["owners"][0]["files"][0]["summary"]["source"]="CFGI_V2"
        with self.assertRaisesRegex(ValueError,"SOURCE_ERA_OR_TIMEFRAME_CHANGED"):
            m.permitted_metadata(x,source_name="a.json")
    def test_hard_fixed_week_not_selectable_by_data(self):
        with self.assertRaisesRegex(ValueError,"WINDOW_NOT_FROZEN"):
            m.audit(root=Path('/nonexistent'),start=m.START_DAY,end=m.END_DAY+timedelta(days=1))
    def test_missing_daily_capture_cannot_be_false_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError,"DAY_MISSING_OR_DUPLICATED"):
                m.audit(root=Path(tmp))
    def test_original_git_blob_hash_not_contents(self):
        self.assertEqual(len(m.git_blob(b"test")),40)
    def test_authority_denies_scoring_and_trading(self):
        self.assertFalse(m.AUTHORITY["hypothesis_testing"])
        self.assertFalse(m.AUTHORITY["outcome_scoring"])
        self.assertFalse(m.AUTHORITY["trading"])
    def test_real_original_archive_week_if_repo_available(self):
        if m.CAPTURE.exists():
            report=m.audit()
            self.assertEqual(report["original_capture_count"],42)
            self.assertEqual(report["original_symbol_rows_count"],126)
            self.assertGreater(report["symbol_clock_skewed_captures"],0)
            self.assertEqual(report["source_timeframe"],"4h")
            self.assertFalse(report["cfgi_predictive_edge_tested"])
            self.assertFalse(report["future_outcomes_used"])

if __name__ == "__main__":
    unittest.main()
