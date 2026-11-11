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
        self.assertFalse(r["complete_control_cohort"])
        self.assertIsNone(r["paired_excess_complete"])
        self.assertEqual(self.result["n_paired"],1)
        self.assertEqual(self.result["n_paired_complete_controls"],0)
        self.assertEqual(self.result["n_paired_partial_controls"],1)
        self.assertEqual(self.result["n_missing_control_exits"],1)
        self.assertIsNone(self.result["median_paired_excess_strict_complete_controls"])
        self.assertIsNone(self.result["month_cluster_bootstrap_ci_complete_controls"])

    def test_same_clock_horizons_and_cost_sensitivity(self):
        r=next(x for x in self.result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["horizons"]["30"]["return"],r["return"])
        self.assertEqual(self.result["horizon_days_summary"]["30"]["observed"],1)
        self.assertEqual(self.result["horizon_days_summary"]["1"]["observed"],2)
        high=m.study(self.data,minimum_first="2025-07-01",latest_first="2025-08-31",
                     fee_bps_roundtrip=100,slippage_bps_roundtrip=100)
        rr=next(x for x in high["rows"] if x["coin"]=="NEW")
        self.assertLess(rr["short_unit_net_ex_funding"],r["short_unit_net_ex_funding"])

    def test_complete_control_cohort_recovers_without_rematching(self):
        # Remove the control that stops trading AFTER the primary's entry.
        # The retained old controls must be selected ex ante; the complete cohort
        # now admits strict comparison without changing the eligible primary.
        data=self.data[self.data["coin"]!="OLD_DIE"].copy()
        result=m.study(data,minimum_first="2025-07-01",latest_first="2025-08-31")
        r=next(x for x in result["rows"] if x["coin"]=="NEW")
        self.assertTrue(r["complete_control_cohort"])
        self.assertEqual(result["n_paired_complete_controls"],1)
        self.assertEqual(result["n_paired_partial_controls"],0)
        self.assertEqual(r["paired_excess"],r["paired_excess_complete"])

    def test_exit_hour_future_high_low_not_counted_as_holding_risk(self):
        start=pd.Timestamp("2025-06-01",tz="UTC")
        b={"timestamp":[start,start+pd.Timedelta(hours=1),
                         start+pd.Timedelta(hours=2)],
           "open":[100.0,110.0,112.0],
           "high":[105.0,120.0,10000.0],
           "low":[95.0,100.0,1.0],
           "close":[103.0,111.0,113.0],
           "volume":[100.0,100.0,100.0]}
        p=m.score_path(b,start,start+pd.Timedelta(hours=2))
        self.assertAlmostEqual(p["return"],0.12)
        # Exit is at the +2h OPEN. The +2h candle's extreme does not belong
        # to the held path, and must not manufacture a >99x short squeeze.
        self.assertAlmostEqual(p["mae_short"],0.20)
        self.assertAlmostEqual(p["mfe_short"],0.05)


    def test_one_hour_late_entry_preserves_price_and_matching(self):
        target=pd.Timestamp("2025-07-17T00:00:00Z")
        mask=(self.data["coin"]=="NEW") & (self.data["timestamp"]==target)
        result=m.study(self.data.loc[~mask].copy(),minimum_first="2025-07-01",latest_first="2025-08-31")
        r=next(x for x in result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["status"],"OK")
        self.assertEqual(r["entry_time"],"2025-07-17T01:00:00+00:00")
        self.assertEqual(result["n_30d_exit_observable"],1)
        self.assertEqual(result["n_paired"],1)
        self.assertEqual(result["n_censored"],1)

    def test_missing_entry_features_cannot_censor_observable_price(self):
        start=pd.Timestamp("2025-07-16T05:00:00Z")
        end=pd.Timestamp("2025-07-17T00:00:00Z")
        mask=(self.data["coin"]=="NEW") & (self.data["timestamp"]>=start) & (self.data["timestamp"]<end)
        result=m.study(self.data.loc[~mask].copy(),minimum_first="2025-07-01",latest_first="2025-08-31")
        r=next(x for x in result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["status"],"INSUFFICIENT_ENTRY_FEATURES")
        self.assertIsNotNone(r["return"])
        self.assertIn("short_unit_net_ex_funding",r)
        self.assertEqual(result["n_30d_exit_observable"],1)
        self.assertEqual(result["n_censored"],1)
        self.assertEqual(result["n_paired"],0)

    def test_all_selected_control_exits_censored_are_counted(self):
        cutoff=pd.Timestamp("2025-07-30T00:00:00Z")
        mask=self.data["coin"].isin(["OLD","OLD2","OLD_DIE"]) & (self.data["timestamp"]>=cutoff)
        result=m.study(self.data.loc[~mask].copy(),minimum_first="2025-07-01",latest_first="2025-08-31")
        r=next(x for x in result["rows"] if x["coin"]=="NEW")
        self.assertEqual(r["match_count"],3)
        self.assertEqual(r["control_exit_count"],0)
        self.assertIsNone(r["paired_excess"])
        self.assertEqual(result["n_paired"],0)
        self.assertEqual(result["n_missing_control_exits"],3)
        self.assertEqual(result["n_30d_exit_observable"],1)


    def test_0d_vs_7d_delay_keep_identical_frozen_entrants(self):
        # A later entrant near the Oct 31 source maturity cutoff can mature
        # at delay 0 but not at delay 7. Such an entrant must belong to
        # neither cohort in the published comparison.
        source=self.data.copy()
        late=source.loc[(source["coin"]=="OLD") &
                        (source["timestamp"]>=pd.Timestamp("2025-08-25T00:00:00Z"))].copy()
        late["coin"]="LATE_COUPLED"
        source=pd.concat([source,late],ignore_index=True)
        base=m.study(source,minimum_first="2025-07-01",latest_first="2025-08-31",
                     delay_days=0)
        delayed=m.study(source,minimum_first="2025-07-01",latest_first="2025-08-31",
                        delay_days=7)
        entries0={r["coin"] for r in base["rows"]}
        entries7={r["coin"] for r in delayed["rows"]}
        self.assertEqual(entries0,entries7)
        self.assertNotIn("LATE_COUPLED",entries0)
        self.assertIn("NEW",entries0)
        self.assertEqual(base["cohort_max_comparison_delay_days"],7)
        self.assertEqual(delayed["cohort_max_comparison_delay_days"],7)
        self.assertEqual(base["cohort_last_first_trade_utc"],
                         delayed["cohort_last_first_trade_utc"])

    def test_unregistered_entry_delay_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"UNREGISTERED_ENTRY_DELAY"):
            m.study(self.data,delay_days=10)



    def test_study_counts_gapped_risk_paths_without_censoring_endpoints(self):
        # Remove one intermediate NEW candle, retaining executable entry and exit.
        gap=pd.Timestamp("2025-07-30T12:00:00Z")
        source=self.data.loc[~((self.data["coin"]=="NEW") &
                               (self.data["timestamp"]==gap))].copy()
        out=m.study(source,minimum_first="2025-07-01",latest_first="2025-08-31")
        row=next(r for r in out["rows"] if r["coin"]=="NEW")
        self.assertIsNotNone(row["return"])
        self.assertEqual(row["path_coverage_status"],"GAPPED_NO_EXCURSION_CLAIM")
        self.assertIsNone(row["mae_short"])
        self.assertEqual(out["n_30d_exit_observable"],1)
        self.assertEqual(out["n_30d_complete_hourly_paths"],0)
        self.assertEqual(out["n_30d_gapped_hourly_paths"],1)
        self.assertIsNone(out["median_mae_short_complete_paths"])
        self.assertEqual(out["n_complete_paths_short_adverse_gt25pct"],0)

    def test_complete_path_coverage_receipt_matches_observed_returns(self):
        out=self.result
        self.assertEqual(out["n_30d_complete_hourly_paths"]+
                         out["n_30d_gapped_hourly_paths"],
                         out["n_30d_exit_observable"])
        self.assertEqual(out["short_excursion_population"],
                         "COMPLETE_HOURLY_PATHS_ONLY")
        self.assertEqual(out["n_30d_gapped_hourly_paths"],0)
        self.assertIsNotNone(out["median_mae_short_complete_paths"])

    def test_gapped_hourly_holding_path_cannot_claim_full_excursions(self):
        start=pd.Timestamp("2025-06-01T00:00:00Z")
        finish=start+30*m.DAY
        bars={"timestamp":[start,finish],
              "open":[100.0,90.0],
              "high":[110.0,95.0],
              "low":[95.0,85.0],
              "close":[101.0,91.0],
              "volume":[1000.0,1000.0]}
        p=m.score_path(bars,start,finish)
        self.assertAlmostEqual(p["return"],-0.10)
        self.assertIsNone(p["mae_short"])
        self.assertIsNone(p["mfe_short"])
        self.assertFalse(p["path_coverage_complete"])
        self.assertEqual(p["path_coverage_status"],"GAPPED_NO_EXCURSION_CLAIM")
        self.assertEqual(p["path_observed_hourly"],2)
        self.assertEqual(p["path_expected_hourly"],721)

    def test_contiguous_hourly_path_keeps_excursions_available(self):
        start=pd.Timestamp("2025-06-01T00:00:00Z")
        hours=pd.date_range(start,periods=25,freq="h")
        bars={"timestamp":list(hours),
              "open":[100.0]*25,
              "high":[120.0]*25,
              "low":[80.0]*25,
              "close":[100.0]*25,
              "volume":[1000.0]*25}
        p=m.score_path(bars,start,start+m.DAY)
        self.assertTrue(p["path_coverage_complete"])
        self.assertEqual(p["path_observed_hourly"],25)
        self.assertEqual(p["path_expected_hourly"],25)
        self.assertAlmostEqual(p["mae_short"],0.2)
        self.assertAlmostEqual(p["mfe_short"],0.2)

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
