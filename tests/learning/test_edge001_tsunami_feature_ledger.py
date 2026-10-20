import csv,json,tempfile,unittest
from datetime import datetime,timezone
from pathlib import Path
from scripts.learning.edge001_tsunami_feature_ledger import breadth_context,build,hourly_row

class Edge001FeatureLedgerTests(unittest.TestCase):
    def test_empty_repo_is_safe(self):
        with tempfile.TemporaryDirectory() as d:
            j=build(Path(d))
            self.assertEqual(j["row_count"],0)
            self.assertFalse(j["outcome_joined"])
            self.assertFalse(j["scoring_ready"])
            self.assertFalse(j["warning_is_sell"])
            self.assertEqual(j["live_exit_rule"],"NONE")

    def _freeze(self,root,state="ELEVATED",btc=1.0,eth=1.0):
        p=root/"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/07";p.mkdir(parents=True,exist_ok=True)
        f={"contract":"OFFICIAL_DAILY_COMPASS_v1","compass_id":"x","issued_at_utc":"2026-10-07T08:17:00Z",
           "market_reference":{"observation_open_utc":"2026-10-07T07:00:00Z","btc_usdt":btc,"eth_usdt":eth},
           "protection_tracker":{"contract":"COMPASS_PROTECTION_TRACKER_v1","data_quality":"OK","pullback_risk_state":state}}
        (p/"CMP-x.json").write_text(json.dumps(f))

    def test_building_is_not_primary_event(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root,"BUILDING")
            self.assertEqual(build(root)["row_count"],0)

    def test_numeric_strings_do_not_create_cohort_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root,"ELEVATED","1.0",1.0)
            self.assertEqual(build(root)["row_count"],0)

    def test_primary_without_hourly_history_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);self._freeze(root)
            j=build(root)
            self.assertEqual(j["row_count"],1)
            row=j["rows"][0]
            self.assertEqual(row["features"]["state"],"UNKNOWN_NO_LEGAL_HOURLY_ROW")
            self.assertFalse(row["scoring_eligible"])
            self.assertFalse(row["outcome_joined"])

    def test_breadth_context_skips_other_valid_json_artifact_shapes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base=root/"03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/07"
            base.mkdir(parents=True,exist_ok=True)
            (base/"raw_source_payload.json").write_text(json.dumps([{"symbol":"BTC"}]))
            (base/"other_artifact.json").write_text(json.dumps({"observation":["not","a","mapping"],"retrieved_at_utc":"2026-10-07T07:00:00Z"}))
            valid={
                "observation":{"cutoff_utc":"2026-10-07T07:00:00Z"},
                "retrieved_at_utc":"2026-10-07T07:00:00Z",
                "evidence_semantics":{"canonical_compatible":False,"evidence_role":"PROXY_ONLY","registered_threshold_compatibility":"UNCONFIRMED"},
                "aggregate":{"advancers":26,"decliners":72}
            }
            (base/"valid_owner.json").write_text(json.dumps(valid))
            row=breadth_context(root,datetime(2026,10,7,8,0,tzinfo=timezone.utc))
            self.assertIn(row["status"],{"CONTEXT_ONLY_PIT_UNVERIFIED","CONTEXT_ONLY_PIT_VERIFIED"})
            self.assertEqual(row["path"],"03_DAILY_CAPTURE_LOGS/breadth_rich/2026/10/07/valid_owner.json")
            self.assertEqual(row["aggregate"],{"advancers":26,"decliners":72})

    def test_breadth_context_with_only_non_owner_shapes_is_unavailable(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            base=root/"03_DAILY_CAPTURE_LOGS/breadth_rich"
            base.mkdir(parents=True,exist_ok=True)
            (base/"raw_source_payload.json").write_text(json.dumps([1,2,3]))
            (base/"wrong_observation.json").write_text(json.dumps({"observation":[],"retrieved_at_utc":"2026-10-07T07:00:00Z"}))
            row=breadth_context(root,datetime(2026,10,7,8,0,tzinfo=timezone.utc))
            self.assertEqual(row["status"],"UNAVAILABLE")
            self.assertFalse(row["scoring_eligible"])


    def _hourly_fixture(self,root,rows):
        p=root/"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-07.csv"
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open("w",newline="") as fh:
            w=csv.DictWriter(fh,fieldnames=["timestamp_utc","source_window_end_utc","spot_status","btc_close"])
            w.writeheader()
            w.writerows(rows)

    def test_missing_malformed_premature_or_future_source_clock_fails_closed(self):
        # A one-hour candle close is not a replacement for missing
        # independently supplied source-window availability.
        cutoff=datetime(2026,10,7,8,17,tzinfo=timezone.utc)
        for source_end in (None,"","invalid-time","2026-10-07T07:30:00Z","2026-10-07T09:00:00Z"):
            with self.subTest(source_end=source_end),tempfile.TemporaryDirectory() as d:
                root=Path(d)
                self._hourly_fixture(root,[{
                    "timestamp_utc":"2026-10-07T07:00:00Z",
                    "source_window_end_utc":source_end,
                    "spot_status":"PASS","btc_close":"100.0"
                }])
                row,path,meta=hourly_row(root,cutoff)
                self.assertIsNone(row)
                self.assertIsNone(path)
                self.assertEqual(meta["status"],"UNKNOWN_NO_LEGAL_HOURLY_ROW")

    def test_valid_source_clock_retained_and_exposes_exact_legal_availability(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self._hourly_fixture(root,[{
                "timestamp_utc":"2026-10-07T06:00:00Z",
                "source_window_end_utc":"2026-10-07T07:05:00Z",
                "spot_status":"PASS","btc_close":"100.0"
            }])
            row,path,meta=hourly_row(root,datetime(2026,10,7,8,17,tzinfo=timezone.utc))
            self.assertIsNotNone(row)
            self.assertIsNotNone(path)
            self.assertEqual(meta["status"],"OBSERVED")
            self.assertEqual(meta["candle_close_utc"],"2026-10-07T07:00:00Z")
            self.assertEqual(meta["legal_availability_utc"],"2026-10-07T07:05:00Z")
            # No Git provenance in the temporary repo: never declare PIT PASS.
            self.assertFalse(meta["point_in_time_feature_capture_eligible"])

    def test_invalid_latest_row_cannot_displace_older_legally_available_row(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self._hourly_fixture(root,[
                {"timestamp_utc":"2026-10-07T06:00:00Z",
                 "source_window_end_utc":"2026-10-07T07:00:00Z",
                 "spot_status":"PASS","btc_close":"100.0"},
                {"timestamp_utc":"2026-10-07T07:00:00Z",
                 "source_window_end_utc":"",
                 "spot_status":"PASS","btc_close":"110.0"}
            ])
            row,_,meta=hourly_row(root,datetime(2026,10,7,8,17,tzinfo=timezone.utc))
            self.assertEqual(row["timestamp_utc"],"2026-10-07T06:00:00Z")
            self.assertEqual(meta["legal_availability_utc"],"2026-10-07T07:00:00Z")

if __name__=="__main__":unittest.main()
