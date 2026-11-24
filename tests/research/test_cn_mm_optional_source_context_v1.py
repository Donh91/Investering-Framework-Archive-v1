import copy
import hashlib
import json
import unittest
from datetime import datetime, timezone
from scripts.research.cn_mm_optional_source_context_v1 import forensics_context, ROOT, AUTHORITY, canonical_bytes

AT="2026-11-04T15:00:00Z"
SHA="a"*40

class FakeReplay:
    def __init__(self, obj):
        self.obj=obj
        self.path=ROOT+"/runs/2026/11/04/pfr-123-1/PULLBACK_FORENSICS.json"
        self.drift=False
    def require_ancestor(self, commit):
        if commit!=SHA: raise ValueError("NOT_ANCESTOR")
    def read_blob(self, commit, path):
        if path not in (ROOT+"/LATEST.json",self.path): raise ValueError("MISSING")
        if self.drift and path==self.path: return b"{}"
        return canonical_bytes(self.obj)+b"\n"

def fixture():
    lanes={}
    for asset in ("BTC","ETH"):
        agg={"aggregates_are_lower_bound":True,"source_completeness":"UNVERIFIED_LEGACY_REST_WINDOW",
             "basis":"DEDUPED_PERSISTED_EVENTS_FROM_ALL_PILOT_CAPTURES"}
        for n in (1,6,24):
            agg[f"event_count_{n}h"]=n
            agg[f"long_liq_usd_{n}h"]=n*10
            agg[f"short_liq_usd_{n}h"]=n*5
        receipt={"http_status":200,"payload_sha256":"b"*64,"payload_bytes":10,"retrieved_at_utc":AT}
        lanes[asset]={"status":"PASS","source_class":"EXECUTED_LIQUIDATIONS",
                      "instrument_metadata":{"instId":asset+"-USDT-SWAP","ctType":"linear","ctMult":"1","ctValCcy":asset},
                      "source_receipts":{"instrument":dict(receipt),"liquidations":dict(receipt)},
                      "persisted_rolling_aggregates":agg}
    return {"contract":"PULLBACK_FORENSICS_PASSIVE_CAPTURE_v1","authority":AUTHORITY,
            "status":"PASS","observed_at_utc":AT,"run_id":"pfr-123-1","lane1_liquidations":lanes}

def seal(obj):
    obj.pop("payload_sha256",None)
    obj["payload_sha256"]=hashlib.sha256(canonical_bytes(obj)).hexdigest()
    return FakeReplay(obj)

class ForensicsContextTests(unittest.TestCase):
    def run_context(self,r,cutoff="2026-11-04T15:01:00Z",commit=SHA):
        return forensics_context(r,commit,datetime.fromisoformat(cutoff.replace("Z","+00:00")))
    def test_lower_bound_not_clearance(self):
        result=self.run_context(seal(fixture()))
        self.assertEqual(result["status"],"ARCHIVED_LOWER_BOUND_CONTEXT_ONLY")
        self.assertEqual(result["assets"]["BTC"]["event_count_24h"],24)
        self.assertIsNone(result["liquidation_clearance"])
        self.assertIsNone(result["capture_completion_utc"])
        self.assertFalse(result["scientific_pit_eligible"])
    def test_future_and_nonancestor(self):
        r=seal(fixture())
        self.assertEqual(self.run_context(r,cutoff="2026-11-04T14:59:59Z")["status"],"UNAVAILABLE")
        self.assertEqual(self.run_context(r,commit="c"*40)["status"],"UNAVAILABLE")
    def test_rehashed_bad_owner_and_dated_drift(self):
        for field,value in [("aggregates_are_lower_bound",False),("event_count_6h",0),("long_liq_usd_1h",True)]:
            obj=fixture(); obj["lane1_liquidations"]["BTC"]["persisted_rolling_aggregates"][field]=value
            self.assertEqual(self.run_context(seal(obj))["status"],"UNAVAILABLE")
        r=seal(fixture()); r.drift=True
        self.assertEqual(self.run_context(r)["status"],"UNAVAILABLE")
    def test_future_receipt_and_missing_asset(self):
        obj=fixture(); obj["lane1_liquidations"]["BTC"]["source_receipts"]["instrument"]["retrieved_at_utc"]="2026-11-04T15:02:00Z"
        self.assertEqual(self.run_context(seal(obj))["status"],"UNAVAILABLE")
        obj=fixture(); obj["lane1_liquidations"]["BTC"]={"status":"UNKNOWN"}
        r=self.run_context(seal(obj))
        self.assertEqual(r["assets"]["BTC"]["status"],"UNAVAILABLE")
        self.assertEqual(r["status"],"ARCHIVED_LOWER_BOUND_CONTEXT_ONLY")
