"""Historical Reality Engine pilot: source integrity and outcome-blind benchmark regression."""
import copy
import csv
import hashlib
import importlib.util
import io
import math
import tempfile
import unittest
import zipfile
import datetime as dt
from pathlib import Path
from scripts.research import arp02_hre_price_control_cost_sensitivity_v1 as arp02

ROOT=Path(__file__).resolve().parents[2]
SPEC=importlib.util.spec_from_file_location("hre_pilot",ROOT/"scripts/research/hre_native_replay_pilot_v1.py")
hre=importlib.util.module_from_spec(SPEC)
import sys
sys.modules[SPEC.name]=hre
SPEC.loader.exec_module(hre)
UTC=dt.timezone.utc

def make_zip(symbol="BTCUSDT",month="2020-03", missing=None):
    yy,mm=map(int,month.split("-"))
    start=dt.datetime(yy,mm,1,tzinfo=UTC)
    end=dt.datetime(yy+(mm==12),1 if mm==12 else mm+1,1,tzinfo=UTC)
    count=int((end-start).total_seconds()//3600)
    out=io.StringIO()
    w=csv.writer(out)
    for i in range(count):
        if i==missing or (isinstance(missing, set) and i in missing):
            continue
        ts=int(start.timestamp()*1000)+i*3_600_000
        val=100+i*0.015
        w.writerow([ts,val,val*1.012,val*.99,val*1.001,10,ts+3_599_999,100,4,6,6,0])
    name=f"{symbol}-1h-{month}.csv"
    buf=io.BytesIO()
    with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr(name,out.getvalue())
    return buf.getvalue()

class SourceIntegrity(unittest.TestCase):
    def test_parse_month_complete(self):
        x=hre.parse_binance_hourly(make_zip(),"BTCUSDT-1h-2020-03.csv","2020-03")
        self.assertEqual(len(x),31*24)
        self.assertEqual(x[0].close_ms+1,x[1].open_ms)

    def test_missing_hour_is_preserved_not_filled(self):
        entries=hre.parse_binance_hourly(make_zip(missing=7),"BTCUSDT-1h-2020-03.csv","2020-03")
        self.assertEqual(len(entries),743)
        self.assertFalse(hre.consecutive_hourly(entries))
        self.assertEqual(entries[7].open_ms-entries[6].open_ms,7_200_000)

    def test_excessive_missing_hours_rejected(self):
        with self.assertRaisesRegex(ValueError,"unacceptable hourly source coverage"):
            hre.parse_binance_hourly(make_zip(missing=set(range(90,150))),"BTCUSDT-1h-2020-03.csv","2020-03")

    def test_wrong_quote_and_zip_path_fail(self):
        with self.assertRaises(ValueError):
            hre.parse_binance_hourly(make_zip(),"ETHUSDT-1h-2020-03.csv","2020-03")

    def test_unallowlisted_source(self):
        with self.assertRaises(ValueError):
            hre.load_month("BADCOIN","2020-03",fetch=lambda *a:b"")

    def test_real_checksum_match_required(self):
        blob=make_zip()
        name="BTCUSDT-1h-2020-03.zip"
        good=hashlib.sha256(blob).hexdigest()
        def fetch(url,max_size):
            return (good+"  "+name+"\n").encode() if url.endswith(".CHECKSUM") else blob
        data,receipt=hre.load_month("BTCUSDT","2020-03",fetch=fetch)
        self.assertEqual(receipt["sha256"],good)
        self.assertEqual(len(data),744)
        self.assertIsNone(receipt["source_first_known_at_original_market_time"])

    def test_tampered_checksum_fails(self):
        blob=make_zip()
        name="BTCUSDT-1h-2020-03.zip"
        def fetch(url,max_size):
            return ("0"*64+"  "+name+"\n").encode() if url.endswith(".CHECKSUM") else blob
        with self.assertRaisesRegex(ValueError,"SHA256"):
            hre.load_month("BTCUSDT","2020-03",fetch=fetch)

    def test_binance_microsecond_precision(self):
        opened=1735689600000000
        ended=opened+3_600_000_000-1
        self.assertEqual(hre._decode_epoch(str(opened)),1735689600000)
        self.assertEqual(hre._decode_epoch(str(ended)),1735693199999)

    def test_real_source_intrabar_last_trade_never_unfreezes_candle(self):
        blob=make_zip()
        name="BTCUSDT-1h-2020-03.csv"
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            original=z.read(name).decode()
        lines=original.splitlines()
        chosen=lines[12].split(",")
        opened=int(chosen[0])
        chosen[6]=str(opened+2_132_286)
        lines[12]=",".join(chosen)
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(name,"\n".join(lines))
        entries=hre.parse_binance_hourly(buf.getvalue(),name,"2020-03")
        self.assertEqual(entries[12].provider_last_trade_ms,opened+2_132_286)
        self.assertEqual(entries[12].close_ms,opened+3_599_999)
        self.assertNotIn(entries[12],hre.closed_as_of(entries,opened+2_132_287))
        self.assertIn(entries[12],hre.closed_as_of(entries,opened+3_600_000))

    def test_microsecond_last_trade_arbitrary_submillisecond(self):
        opened=1735689600000000
        self.assertEqual(hre._decode_epoch(str(opened+2_132_286_123)),1735691732286)

    def test_closed_before_cutoff(self):
        x=hre.parse_binance_hourly(make_zip(),"BTCUSDT-1h-2020-03.csv","2020-03")
        ref=x[15].open_ms
        eligible=hre.closed_as_of(x,ref)
        self.assertEqual(len(eligible),15)
        self.assertNotIn(x[15],eligible)

    def test_crisis_no_trivial_original_claim(self):
        rows=hre.parse_binance_hourly(make_zip(),"BTCUSDT-1h-2020-03.csv","2020-03")
        p=hre.score_crisis(rows)
        self.assertGreater(p["daily_cutoffs"],0)
        self.assertTrue(p["not_original_framework_warning"])
        self.assertIn("non_independent",p["rules"]["sample"])

    def test_cannot_hindsight_weekly_forecast(self):
        rows=hre.parse_binance_hourly(make_zip(month="2021-03"),"BTCUSDT-1h-2021-03.csv","2021-03")
        days=list(hre.daily_candles(rows).items())
        # March 2021 has enough complete prior days and 7 future days for last Monday March 29? 
        # Use April 2021 Monday 5 with a full preceding 29-day input window.
        extra=hre.parse_binance_hourly(make_zip(month="2021-04"),"BTCUSDT-1h-2021-04.csv","2021-04")
        ds=list(hre.daily_candles(rows+extra).items())
        ix=next(i for i,(d,_) in enumerate(ds) if str(d)=="2021-04-05")
        original=hre.frozen_week_forecast(ds,ix)
        changed=copy.deepcopy(ds)
        for j in range(ix,len(changed)):
            d,v=changed[j]
            v["c"]*=10
            v["h"]*=10
            v["l"]*=10
        again=hre.frozen_week_forecast(changed,ix)
        self.assertEqual([d["frozen_expected_close"] for d in original["days"]],
                         [d["frozen_expected_close"] for d in again["days"]])
        self.assertEqual([d["naive_low"] for d in original["days"]],
                         [d["naive_low"] for d in again["days"]])
        self.assertEqual([d["alternative_high"] for d in original["days"]],
                         [d["alternative_high"] for d in again["days"]])
        self.assertNotEqual(original["days"][0]["actual_close"],again["days"][0]["actual_close"])

    def test_extended_episode_predefined_and_no_future_original_claim(self):
        self.assertEqual(len(hre.EXTENDED_EPISODES),5)
        self.assertEqual(hre.EXTENDED_EPISODES["terra_2022"]["months"],["2022-04","2022-05","2022-06"])
        self.assertIn("original",hre.SOURCE_CLASS.lower())
        self.assertIn("NOT_OFFICIAL",hre.INFERENCE_CLASS)

    def test_extended_requires_preselected_case(self):
        with self.assertRaisesRegex(ValueError,"requires preselected"):
            hre.run("extended")
        with self.assertRaisesRegex(ValueError,"unsupported"):
            hre.run("source","terra_2022")

    def test_case_context_only_contains_preanchor_information(self):
        rows=hre.parse_binance_hourly(make_zip(month="2021-03"),"BTCUSDT-1h-2021-03.csv","2021-03")
        x=hre.score_crisis(rows,event_anchor_utc="2021-03-20T00:00:00Z")
        cases=x["preselected_case_context"]["pre_anchor_7d_eligible_cutoffs"]
        self.assertGreater(len(cases),0)
        self.assertTrue(all(d["cutoff_utc"] <= "2021-03-20T00:00:00+00:00" for d in cases))
        self.assertIn("ex-post",x["preselected_case_context"]["warning"])

    def test_weekly_fail_insufficient_history(self):
        with self.assertRaisesRegex(ValueError,"insufficient"):
            hre.frozen_week_forecast([],0)

    def test_inverted_or_corrupt_ohlc_fails(self):
        blob=make_zip()
        bad_name="BTCUSDT-1h-2020-03.csv"
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            csv_text=z.read(bad_name).decode()
        lines=csv_text.splitlines()
        row=lines[12].split(",")
        row[2]="0"
        lines[12]=",".join(row)
        buf=io.BytesIO()
        with zipfile.ZipFile(buf,"w",compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr(bad_name,"\n".join(lines))
        with self.assertRaisesRegex(ValueError,"invalid OHLC"):
            hre.parse_binance_hourly(buf.getvalue(),bad_name,"2020-03")
        

class ARP02HREOriginalControlLossSensitivity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = arp02.read_source(ROOT)
        cls.result = arp02.evaluate(cls.source)

    def test_source_frozen_original_418_cutoffs_not_418_crises(self):
        out = self.result
        self.assertEqual(out["market_event_families_selected_retrospectively"], 5)
        self.assertTrue(out["overlapping_cutoffs_are_not_independent"])
        self.assertIsNone(out["number_of_independent_market_shocks_certified"])
        self.assertEqual(out["historical_source_class"],
                         "POSTHOC_PRICE_TRUTH_TAPE_NOT_ORIGINAL_PROVIDER_FIRST_KNOWN")
        self.assertEqual([r["daily_cutoffs_per_asset"] for r in out["per_era"]],
                         [85, 86, 77, 86, 84])

    def test_btc_original_source_reproduces_extra_alarms_and_cost_crossover(self):
        btc = self.result["assets"]["BTCUSDT"]
        self.assertEqual(btc["baseline"], {"tp":8, "fp":16, "fn":38, "tn":356})
        self.assertEqual(btc["challenger"], {"tp":11, "fp":25, "fn":35, "tn":347})
        self.assertEqual(btc["overlapping_daily_cutoff_count"], 418)
        self.assertEqual((btc["fewer_missed_outcome_windows"], btc["extra_false_alarms"]), (3, 9))
        self.assertEqual(btc["miss_to_false_alarm_cost_ratio_to_break_even"], 3.0)
        self.assertEqual(btc["candidate_minus_baseline_loss_at_miss_cost_1"], 6)
        self.assertEqual(btc["candidate_minus_baseline_loss_at_miss_cost_5"], -6)

    def test_eth_original_source_reproduces_extra_alarms_and_cost_crossover(self):
        eth = self.result["assets"]["ETHUSDT"]
        self.assertEqual(eth["baseline"], {"tp":15, "fp":24, "fn":73, "tn":306})
        self.assertEqual(eth["challenger"], {"tp":22, "fp":39, "fn":66, "tn":291})
        self.assertEqual((eth["fewer_missed_outcome_windows"], eth["extra_false_alarms"]), (7, 15))
        self.assertAlmostEqual(eth["miss_to_false_alarm_cost_ratio_to_break_even"], 15/7, places=5)
        self.assertEqual(eth["candidate_minus_baseline_loss_at_miss_cost_1"], 8)
        self.assertEqual(eth["candidate_minus_baseline_loss_at_miss_cost_5"], -20)

    def test_no_profit_or_warning_delivery_fabricated(self):
        self.assertTrue(self.result["unit_loss_is_not_trade_cost"])
        self.assertFalse(self.result["actual_issued_warning_or_delivery_proven"])
        self.assertFalse(self.result["economic_paper_outcome_proven"])
        self.assertFalse(self.result["official_threshold_or_model_change_authorized"])
        self.assertEqual(self.result["scientific_status"],
                         "RETROSPECTIVE_DESCRIPTIVE_DIAGNOSTIC_ONLY")

    def test_corrupted_matrix_or_missing_episode_fails_closed(self):
        altered = copy.deepcopy(self.source)
        altered["episodic_results"][0]["BTCUSDT"]["price_baseline"]["fp"] = -1
        with self.assertRaisesRegex(ValueError, "INVALID_ORIGINAL_CONFUSION"):
            arp02.evaluate(altered)
        altered = copy.deepcopy(self.source)
        altered["episodic_results"].pop(0)
        with self.assertRaisesRegex(ValueError, "HRE_EPISODE_ROSTER"):
            arp02.evaluate(altered)

    def test_hindsight_source_class_cannot_be_upgraded(self):
        altered = copy.deepcopy(self.source)
        altered["historical_source_class"] = "ORIGINAL_ISSUED_2022"
        with self.assertRaisesRegex(ValueError, "HRE_SOURCE_AUTHORITY"):
            arp02.evaluate(altered)

    def test_revised_source_file_cannot_silently_replace_original(self):
        import json
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / arp02.SOURCE_PATH
            target.parent.mkdir(parents=True)
            target.write_text(json.dumps(self.source, sort_keys=True), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "HRE_NATIVE_SOURCE_BLOB_DRIFT"):
                arp02.read_source(Path(tmp))

if __name__ == "__main__":
    unittest.main()
