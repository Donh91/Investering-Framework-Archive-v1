from __future__ import annotations
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.learning.compass_rolling_14d_audit import run, stamp, main, CONTRACT


START = datetime(2026,10,20,tzinfo=timezone.utc)
ASOF = datetime(2026,10,23,tzinfo=timezone.utc)


def put(root: Path, path: str, content: str):
    target=root/path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content,encoding="utf-8")


def sample_freeze(issue: datetime, name: str, signal="UP", risk="ELEVATED",
                  contract="OFFICIAL_DAILY_COMPASS_SCORING_v3", action="HOLD_WAIT",
                  hours_old=1, h72="MIXED", h168="MIXED"):
    open_at=issue-timedelta(hours=hours_old+1)
    return {
        "contract":"OFFICIAL_DAILY_COMPASS_v1",
        "scoring_contract":contract,
        "compass_id":name, "issued_at_utc":issue.isoformat().replace("+00:00","Z"),
        "market_reference":{
            "observation_open_utc":open_at.isoformat().replace("+00:00","Z"),
            "btc_usdt":100, "eth_usdt":200,
        },
        "data_status":"OK","run_reason":"EVENT_DRIVEN",
        "action_now":action,
        "protection_tracker":{"pullback_risk_state":risk},
        "horizons":{
            "NEXT_12H":{"expected_direction":signal},
            "NEXT_1_3D":{"expected_direction":h72},
            "NEXT_5_7D":{"expected_direction":h168},
        },
    }


def seed(root: Path):
    # 14-day step tested against real sequences with complete hourly candle closes.
    for day in range(19,24):
        d=datetime(2026,10,day,tzinfo=timezone.utc)
        p=f"03_DAILY_CAPTURE_LOGS/hourly/2026/10/{d:%Y-%m-%d}.csv"
        lines=["timestamp_utc,source_window_end_utc,btc_close,eth_close,spot_status"]
        for i in range(24):
            opened=d+timedelta(hours=i)
            end=opened+timedelta(hours=1)
            lines.append(f"{opened:%Y-%m-%dT%H:%M:%SZ},{end:%Y-%m-%dT%H:%M:%SZ},{100+i/100:.2f},{200+i/100:.2f},PASS")
        put(root,p,"\n".join(lines)+"\n")
    for t,name,sig in [
        (START+timedelta(hours=3),"a","UP"),
        (START+timedelta(hours=5),"b","DOWN"),
        (START+timedelta(hours=14),"c","MIXED"),
        (START+timedelta(days=1,hours=15),"d","DOWN"),
    ]:
        put(root,f"04_MARKET_LEARNING/handlekompas/official/daily/{t:%Y/%m/%d}/CMP-{name}.json",
            json.dumps(sample_freeze(t,name,signal=sig),sort_keys=True))


class RollingCompassAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        seed(self.root)

    def test_recover_every_frozen_release_and_deduplicate_independent_slots(self):
        report=run(self.root,ASOF,"rolling14")
        self.assertEqual(report["contract"],CONTRACT)
        self.assertEqual(report["all_issuances"]["forecasts"],4)
        self.assertEqual(report["deduplicated_12h_slots"]["forecasts"],3)
        self.assertEqual(len(report["all_issuance_rows"]),4)
        self.assertFalse(report["automatic_model_reweighting"])
        self.assertEqual(report["trade_permission"],"NONE")
        self.assertIsNone(report["certified_predictive_skill"])

    def test_12h_up_and_down_only_count_actual_direction_calls(self):
        r=run(self.root,ASOF,"rolling14")
        h=r["all_issuances"]["horizons"]["12h"]
        self.assertEqual(h["issuances"],4)
        self.assertEqual(h["directional_testable_n"],3)
        self.assertEqual(h["abstention_count"],1)
        self.assertIsNone(h["point_in_time_certified_edge"])

    def test_mixed_is_abstention_not_accuracy_win(self):
        r=run(self.root,ASOF,"rolling14")
        mixed=next(x for x in r["all_issuance_rows"] if x["id"]=="c")
        self.assertEqual(mixed["horizons"]["12h"]["descriptive_direction_result"],
                         "ABSTAIN_NO_DIRECTIONAL_CLAIM")

    def test_6h_and_24h_followups_are_not_scored_as_issued_forecasts(self):
        r=run(self.root,ASOF,"rolling14")
        item=r["all_issuance_rows"][0]
        self.assertEqual(item["additional_expost_6_24_72h"]["6h"]["status"],
                         "EXPOST_OBSERVED_NOT_ISSUED_FORECAST")
        self.assertEqual(item["horizons"]["12h"]["expected_direction"],"UP")
        self.assertNotIn("6h",r["all_issuances"]["horizons"])

    def test_future_horizon_is_pending_never_claimed_matured(self):
        r=run(self.root,ASOF,"rolling14")
        self.assertEqual(r["all_issuances"]["horizons"]["168h"]["matured_expost_n"],0)
        self.assertTrue(r["all_issuances"]["horizons"]["168h"]["status_counts"].get("PENDING_NOT_MATURE",0)>0)

    def test_future_observation_reference_is_quarantined(self):
        t=START+timedelta(hours=4)
        f=sample_freeze(t,"future",hours_old=-2)
        put(self.root,f"04_MARKET_LEARNING/handlekompas/official/daily/{t:%Y/%m/%d}/CMP-future.json",
            json.dumps(f))
        r=run(self.root,ASOF,"rolling14")
        item=next(x for x in r["all_issuance_rows"] if x["id"]=="future")
        self.assertEqual(item["horizons"]["12h"]["status"],
                         "QUARANTINE_INVALID_REFERENCE_OR_FUTURE_REFERENCE")

    def test_legacy_contract_not_silently_rescored(self):
        t=START+timedelta(hours=6)
        f=sample_freeze(t,"legacy",contract="OFFICIAL_DAILY_COMPASS_SCORING_v2")
        put(self.root,f"04_MARKET_LEARNING/handlekompas/official/daily/{t:%Y/%m/%d}/CMP-legacy.json",
            json.dumps(f))
        r=run(self.root,ASOF,"rolling14")
        item=next(x for x in r["all_issuance_rows"] if x["id"]=="legacy")
        self.assertEqual(item["horizons"]["12h"]["status"],"LEGACY_SCORING_CONTRACT_NOT_REINTERPRETED")

    def test_missing_target_candle_remains_unavailable(self):
        path=self.root/"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-20.csv"
        raw=path.read_text()
        raw=raw.replace("2026-10-20T13:00:00Z,2026-10-20T14:00:00Z","2026-10-20T13:30:00Z,2026-10-20T14:30:00Z")
        path.write_text(raw)
        r=run(self.root,ASOF,"rolling14")
        item=next(x for x in r["all_issuance_rows"] if x["id"]=="a")
        self.assertEqual(item["horizons"]["12h"]["status"],"UNAVAILABLE_TARGET_CANDLE")

    def test_all_history_includes_old_freezes_excluded_by_14d(self):
        old=datetime(2026,9,1,tzinfo=timezone.utc)
        put(self.root,"04_MARKET_LEARNING/handlekompas/official/daily/2026/09/01/CMP-old.json",
            json.dumps(sample_freeze(old,"old")))
        new=run(self.root,ASOF,"rolling14")
        old_report=run(self.root,ASOF,"all")
        self.assertEqual(new["all_issuances"]["forecasts"],4)
        self.assertEqual(old_report["all_issuances"]["forecasts"],5)
        self.assertTrue(old_report["data_inventory"]["all_discovered_files"]>=5)
        self.assertFalse(old_report["first_known_publication_verified"])

    def test_source_manifest_is_sha256_bound_not_just_filename(self):
        r=run(self.root,ASOF,"rolling14")
        self.assertEqual(len(r["source_manifest"]["official_freezes"]),4)
        self.assertTrue(all(len(x["sha256"])==64 for x in r["source_manifest"]["official_freezes"]))
        self.assertGreater(len(r["source_manifest"]["hourly_csv"]),0)

    def test_no_automatic_recalibration_even_if_success_rate_is_high(self):
        r=run(self.root,ASOF,"rolling14")
        s=r["scientific_decision"]
        self.assertEqual(s["admissible_automatic_calibration_changes"],[])
        self.assertEqual(s["status"],"HOLD_UNTIL_ORIGINAL_PIT_RECEIPTS_AND_PRE_REGISTERED_HOLDOUT")
        self.assertFalse(r["research_only"] is False)

    def test_frozen_momentum_baseline_is_matched_only_on_same_matured_slot(self):
        t=START+timedelta(hours=22)
        f=sample_freeze(t,"with_momentum",signal="UP")
        f["market_now"]={"btc_delta_pct":0.4}
        put(self.root,f"04_MARKET_LEARNING/handlekompas/official/daily/{t:%Y/%m/%d}/CMP-mom.json",
            json.dumps(f))
        report=run(self.root,ASOF,"rolling14")
        row=next(r for r in report["all_issuance_rows"] if r["id"]=="with_momentum")
        h=row["horizons"]["12h"]
        self.assertEqual(h["frozen_momentum_baseline_direction"],"UP")
        self.assertIn(h["momentum_baseline_result"],("CORRECT","INCORRECT"))
        paired=report["all_issuances"]["horizons"]["12h"]["matched_momentum_control"]
        self.assertEqual(paired["matched_n"],1)
        self.assertIsNone(paired["incremental_certified_edge"])

    def test_daily_risk_and_calibration_flags_never_change_parameters(self):
        report=run(self.root,ASOF,"rolling14")
        daily=report["all_issuances"]["by_copenhagen_day"]
        self.assertTrue(any("2026-10-20" in d for d in daily))
        self.assertTrue(all("12h_direction_correct_n" in d for d in daily.values()))
        self.assertTrue(all(not flag["automatic_weight_change"]
                            for flag in report["nonbinding_calibration_research_flags"]))
        self.assertFalse(report["descriptive_market_path"]["point_in_time_prediction_or_performance"])

    def test_no_future_files_are_read_into_historical_replay(self):
        r1=run(self.root,ASOF,"rolling14")
        put(self.root,"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-30.csv",
            "timestamp_utc,source_window_end_utc,btc_close,eth_close,spot_status\n"
            "2026-10-30T00:00:00Z,2026-10-30T01:00:00Z,1000000,999999,PASS\n")
        r2=run(self.root,ASOF,"rolling14")
        self.assertEqual(r1["all_issuances"]["horizons"],
                         r2["all_issuances"]["horizons"])

    def test_late_collection_window_is_not_admitted_by_earlier_analysis_asof(self):
        path=self.root/"03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-20.csv"
        raw=path.read_text().replace("2026-10-20T13:00:00Z,2026-10-20T14:00:00Z",
                                     "2026-10-20T13:00:00Z,2026-10-24T14:00:00Z")
        path.write_text(raw)
        r=run(self.root,ASOF,"rolling14")
        item=next(x for x in r["all_issuance_rows"] if x["id"]=="a")
        self.assertEqual(item["horizons"]["12h"]["status"],"UNAVAILABLE_TARGET_CANDLE")


if __name__ == "__main__":
    unittest.main()
