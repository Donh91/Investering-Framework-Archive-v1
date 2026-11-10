"""Synthetic QA for research-only Hyperliquid listing-decay study."""
from pathlib import Path
import importlib.util
import unittest
import pandas as pd

SCRIPT=Path(__file__).resolve().parents[2]/"scripts/research/hyperliquid_listing_decay_v1.py"
spec=importlib.util.spec_from_file_location("listing_decay_v1",SCRIPT)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic():
    first=pd.Timestamp("2025-05-01",tz="UTC")
    last=pd.Timestamp("2025-09-30",tz="UTC")
    hours=pd.date_range(first,last,freq="h")
    rows=[]
    entries=[
        ("OLD",first,100,0.010,None),
        ("OLD2",first,100,0.015,None),
        ("OLD_DIE",first,10,-0.005,pd.Timestamp("2025-08-01",tz="UTC")),
        ("NEW",pd.Timestamp("2025-07-15T12:00:00Z"),10,-0.005,None),
        ("DELIST",pd.Timestamp("2025-08-01T10:00:00Z"),20,-0.008,pd.Timestamp("2025-08-10",tz="UTC"))
    ]
    for coin,begin,base,perday,stop in entries:
        seq=[t for t in hours if t>=begin and (stop is None or t<stop)]
        for j,t in enumerate(seq):
            px=base*(1+perday)**(j/24)
            rows.append({"timestamp":t,"coin":coin,"dex":"","market_class":"perp",
                         "open":px,"high":px*1.005,"low":px*0.995,
                         "close":px,"volume":1000})
    return pd.DataFrame(rows)


class ListingDecayResearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=synthetic()
        cls.bars=m.grouped_bars(cls.data)
        cls.result=m.study(cls.data,minimum_first="2025-07-01",
                           latest_first="2025-08-31")

    def test_future_entry_excluded_and_30d_due_clock(self):
        r=next(x for x in self.result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["entry_target_utc"],"2025-07-17T00:00:00+00:00")
        self.assertEqual(r["due_utc"],"2025-08-16T00:00:00+00:00")
        self.assertAlmostEqual(r["return"],(0.995)**30-1,places=5)

    def test_delisted_missing_exit_kept_in_denominator(self):
        r=next(x for x in self.result["rows"] if x["coin"]=="DELIST")
        self.assertEqual(r["status"],"NO_EXECUTABLE_30D_EXIT")
        self.assertEqual(r["horizons"]["1"]["status"],"OBSERVED")
        self.assertEqual(r["horizons"]["14"]["status"],"CENSORED")
        self.assertEqual(self.result["n_censored"],1)

    def test_control_selection_does_not_filter_future_delistings(self):
        r=next(x for x in self.result["rows"] if x["coin"]=="NEW")
        matches={x["coin"]:x for x in r["controls"]}
        self.assertIn("OLD_DIE",matches)
        self.assertEqual(matches["OLD_DIE"]["status"],"CONTROL_EXIT_CENSORED")
        self.assertEqual(r["control_exit_count"],2)
        self.assertLess(r["paired_excess"],0)

    def test_same_clock_horizons_and_cost_sensitivity(self):
        r=next(x for x in self.result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["horizons"]["30"]["return"],r["return"])
        self.assertEqual(self.result["horizon_days_summary"]["30"]["observed"],1)
        self.assertEqual(self.result["horizon_days_summary"]["1"]["observed"],2)
        high=m.study(self.data,minimum_first="2025-07-01",latest_first="2025-08-31",
                     fee_bps_roundtrip=100,slippage_bps_roundtrip=100)
        rr=next(x for x in high["rows"] if x["coin"]=="NEW")
        self.assertLess(rr["short_unit_net_ex_funding"],r["short_unit_net_ex_funding"])

    def test_control_age_gate(self):
        entry=pd.Timestamp("2025-07-17",tz="UTC")
        f=m.window_features(self.bars["NEW"],entry,entry-m.DAY)
        cs=m.matched_controls("NEW",self.bars,
                             {c:b["timestamp"][0] for c,b in self.bars.items()},
                             entry,entry+30*m.DAY,f)
        self.assertTrue(all(x["coin"].startswith("OLD") for x in cs))

    def test_missing_month_rejected_before_data_read(self):
        with self.assertRaisesRegex(ValueError,"MISSING_MONTH_BETWEEN"):
            m.ingest([Path("/tmp/2025-05.parquet"),Path("/tmp/2025-07.parquet")])


if __name__=="__main__":
    unittest.main()
