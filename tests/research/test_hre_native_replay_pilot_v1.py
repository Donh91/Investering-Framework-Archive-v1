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
        if i==missing:
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

    def test_missing_candle_fails(self):
        with self.assertRaisesRegex(ValueError,"incomplete hourly"):
            hre.parse_binance_hourly(make_zip(missing=7),"BTCUSDT-1h-2020-03.csv","2020-03")

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
        # Use March 2021 Monday 29 with a longer synthetic April tail.
        extra=hre.parse_binance_hourly(make_zip(month="2021-04"),"BTCUSDT-1h-2021-04.csv","2021-04")
        ds=list(hre.daily_candles(rows+extra).items())
        ix=next(i for i,(d,_) in enumerate(ds) if str(d)=="2021-03-29")
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
        
if __name__ == "__main__":
    unittest.main()
