from __future__ import annotations
import json
import tempfile
import subprocess
import sys
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

    def test_direct_script_cli_import_and_publication(self):
        # Regression for CI failure: "python scripts/learning/...py" has no
        # top-level scripts package in its default sys.path.
        script=Path(__file__).resolve().parents[2]/"scripts/learning/compass_rolling_14d_audit.py"
        output="04_MARKET_LEARNING/handlekompas/research/rolling_14d/daily/2026/10/23/check_ROLLING14.json"
        ran=subprocess.run([sys.executable,str(script),"--repo",str(self.root),
                            "--scope","rolling14","--asof","2026-10-23T00:00:00Z",
                            "--output",output],capture_output=True,text=True,timeout=30)
        self.assertEqual(ran.returncode,0,ran.stderr)
        report=json.loads((self.root/output).read_text())
        self.assertEqual(report["contract"],CONTRACT)
        self.assertFalse(report["automatic_model_reweighting"])

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

    def test_identical_recollected_candle_with_later_batch_clock_is_not_conflicting(self):
        # source_window_end_utc is a batch collection time, not the candle's
        # identity. An identical-price row may be recollected later.
        before = run(self.root, ASOF, "rolling14")
        path = self.root / "03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-20.csv"
        with path.open("a", encoding="utf-8") as handle:
            handle.write("2026-10-20T13:00:00Z,2026-10-20T15:00:00Z,100.13,200.13,PASS\n")
        after = run(self.root, ASOF, "rolling14")
        self.assertEqual(after["complete_spot_close_rows"], before["complete_spot_close_rows"])
        self.assertEqual(after["price_source_quality"].get("conflicting_candle_clocks"), 0)
        self.assertEqual(after["price_source_quality"].get("matching_recollected_hour_rows"), 1)
        row = next(x for x in after["all_issuance_rows"] if x["id"] == "a")
        self.assertEqual(row["horizons"]["12h"]["status"], "MATURED_EXPOST_ONLY")

    def test_distinct_prices_for_same_candle_still_quarantined(self):
        path = self.root / "03_DAILY_CAPTURE_LOGS/hourly/2026/10/2026-10-20.csv"
        with path.open("a", encoding="utf-8") as handle:
            handle.write("2026-10-20T13:00:00Z,2026-10-20T15:00:00Z,103.13,200.13,PASS\n")
        report = run(self.root, ASOF, "rolling14")
        self.assertEqual(report["price_source_quality"]["conflicting_candle_clocks"], 1)
        item = next(x for x in report["all_issuance_rows"] if x["id"] == "a")
        self.assertEqual(item["horizons"]["12h"]["status"], "UNAVAILABLE_TARGET_CANDLE")

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

    def test_official_sideways_is_scored_not_abstention(self):
        # Official scoring v3 awards a SIDEWAYS prediction inside the 1.5%
        # band. Task2 legacy and abstention controls must not erase this call.
        t=START+timedelta(hours=22)
        f=sample_freeze(t,"sideways",signal="SIDEWAYS")
        put(self.root,f"04_MARKET_LEARNING/handlekompas/official/daily/{t:%Y/%m/%d}/CMP-sideways.json",
            json.dumps(f))
        report=run(self.root,ASOF,"rolling14")
        row=next(x for x in report["all_issuance_rows"] if x["id"]=="sideways")
        self.assertEqual(row["horizons"]["12h"]["descriptive_direction_result"],"CORRECT")
        self.assertEqual(row["horizons"]["12h"]["official_sideways_tolerance_pct"],1.5)
        summary=report["all_issuances"]["horizons"]["12h"]
        self.assertEqual(summary["sideways_testable_n"],1)
        self.assertEqual(summary["sideways_correct_n"],1)
        self.assertEqual(summary["abstention_count"],1)

    def test_source_age_thresholds_are_diagnostic_not_a_data_gate(self):
        result=run(self.root,ASOF,"rolling14")
        d=result["all_issuances"]["reference_age_at_issuance"]
        self.assertEqual(d["available_n"],4)
        self.assertEqual(d["over_30m_n"],4)
        self.assertGreaterEqual(d["over_60m_n"],0)
        self.assertIn("NOT_PROVIDER_FIRST_KNOWN",d["clock_type"])
        self.assertEqual(result["all_issuances"]["horizons"]["12h"]["directional_testable_n"],3)
        self.assertFalse(result["automatic_model_reweighting"])

    def test_oversized_report_fails_before_any_publication(self):
        from unittest.mock import patch
        from scripts.learning.compass_rolling_14d_audit import main as cli_main
        output="04_MARKET_LEARNING/handlekompas/research/rolling_14d/daily/2026/10/23/test.json"
        with patch("sys.argv",["audit","--repo",str(self.root),"--asof",
                               "2026-10-23T00:00:00Z","--scope","rolling14","--output",output]):
            with patch("scripts.learning.compass_rolling_14d_audit.run",
                       return_value={"payload":"x"*8_000_001}):
                with self.assertRaisesRegex(ValueError,"RESEARCH_REPORT_TOO_LARGE"):
                    cli_main()
        self.assertFalse((self.root/output).exists())

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



class PullbackTimeboxResearchTests(unittest.TestCase):
    """Adversarial policy controls. They are NOT historical edge claims."""

    @staticmethod
    def freeze(when, state="ELEVATED", quality="OK", path=None):
        f=sample_freeze(when,str(when.timestamp()),risk=state)
        f["protection_tracker"]["data_quality"]=quality
        return {"issued":when,"path":path or f"CMP-{int(when.timestamp())}.json",
                "sha256":"a"*64,"data":f}

    @staticmethod
    def tape(start, hours=90, base=100.0, fall_at=None, fall_to=96.0):
        from scripts.learning.pullback_warning_timeliness_shadow import target_close_after
        anchor=target_close_after(start)
        return {anchor+timedelta(hours=i):
                {"btc":fall_to if fall_at is not None and i >= fall_at else base,
                 "eth":200.0,
                 "source_window_end_utc":(anchor+timedelta(hours=i)).isoformat()}
                for i in range(hours)}

    def test_repeated_elevated_is_not_six_months_of_forecast_credit(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate, CONTRACT
        t=START+timedelta(hours=3)
        items=[self.freeze(t+timedelta(hours=i),"ELEVATED") for i in (0,12,24,48,72,96)]
        result=evaluate(items,self.tape(t,110,fall_at=100),t+timedelta(hours=110))
        self.assertEqual(result["contract"],CONTRACT)
        self.assertEqual(result["new_warning_or_escalation_events"],0)
        self.assertEqual(result["warning_state_counts"]["LEFT_CENSORED_NO_TRANSITION_PROOF"],1)
        self.assertEqual(result["warning_state_counts"]["REPEAT_STATE_NOT_NEW_WARNING"],5)
        self.assertIsNone(result["horizons"]["72h"]["hit_rate_descriptive"])
        self.assertTrue(result["expired_alert_cannot_be_credited_from_later_drop"])

    def test_fresh_transition_counted_once_and_timeboxed(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        freezes=[self.freeze(t,"NORMAL"),self.freeze(t+timedelta(hours=1),"ELEVATED"),
                 self.freeze(t+timedelta(hours=3),"ELEVATED")]
        market=self.tape(t,90)
        r=evaluate(freezes,market,t+timedelta(hours=90))
        self.assertEqual(r["new_warning_or_escalation_events"],1)
        self.assertEqual(r["warning_state_counts"]["NEW_WARNING"],1)
        self.assertEqual(r["warning_state_counts"]["REPEAT_STATE_NOT_NEW_WARNING"],1)
        self.assertEqual(r["horizons"]["12h"]["false_alarm_n"],1)
        self.assertEqual(r["horizons"]["24h"]["false_alarm_n"],1)
        self.assertEqual(r["horizons"]["72h"]["false_alarm_n"],1)
        self.assertIsNone(r["horizons"]["24h"]["warning_skill_or_edge"])
        self.assertFalse(r["automatic_model_reweighting"])
        self.assertEqual(r["trade_permission"],"NONE")

    def test_dip_inside_24h_counts_but_post_expiry_dip_does_not(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        issued=t+timedelta(hours=1)
        freezes=[self.freeze(t,"NORMAL"),self.freeze(issued,"ELEVATED")]
        # First full post-issue anchor starts after issuance.
        market=self.tape(issued,90,fall_at=16,fall_to=96.0)
        r=evaluate(freezes,market,issued+timedelta(hours=80))
        self.assertEqual(r["horizons"]["12h"]["false_alarm_n"],1)
        self.assertEqual(r["horizons"]["24h"]["hit_n"],1)
        self.assertEqual(r["horizons"]["72h"]["hit_n"],1)
        self.assertGreater(r["alerts"][0]["outcomes"]["24h"]["lead_hours"],0)
        # Late decline after the 72h expiry is not retrospectively credited.
        late=evaluate(freezes,self.tape(issued,100,fall_at=80,fall_to=60.0),
                      issued+timedelta(hours=99))
        self.assertEqual(late["horizons"]["72h"]["hit_n"],0)
        self.assertEqual(late["horizons"]["72h"]["false_alarm_n"],1)

    def test_no_lookahead_in_partially_completed_hour(self):
        from scripts.learning.pullback_warning_timeliness_shadow import target_close_after, evaluate_path
        t=START+timedelta(hours=3,minutes=59)
        anchor=target_close_after(t)
        self.assertEqual(anchor,t.replace(minute=0)+timedelta(hours=2))
        market={t.replace(minute=0)+timedelta(hours=1):{"btc":50},
                anchor:{"btc":100}}
        for i in range(1,13):
            market[anchor+timedelta(hours=i)]={"btc":100}
        r=evaluate_path(t,t+timedelta(hours=14),market,12,-1.5)
        self.assertEqual(r["maturity"],"MATURED_EXPOST_ONLY")
        self.assertFalse(r["hit_within_window"])
        self.assertEqual(r["anchor_close_utc"],anchor.isoformat().replace("+00:00","Z"))

    def test_missing_candle_quarantines_entire_horizon_not_false_alarm(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        freezes=[self.freeze(t,"NORMAL"),self.freeze(t+timedelta(hours=1),"HIGH")]
        issued=t+timedelta(hours=1)
        market=self.tape(issued,90)
        del market[next(k for k in sorted(market) if k > issued+timedelta(hours=4))]
        r=evaluate(freezes,market,issued+timedelta(hours=80))
        for h in ("12h","24h","72h"):
            self.assertEqual(r["horizons"][h]["unknown_n"],1)
            self.assertEqual(r["horizons"][h]["false_alarm_n"],0)
            self.assertIsNone(r["horizons"][h]["hit_rate_descriptive"])

    def test_pending_window_cannot_become_false_alarm(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        freezes=[self.freeze(t,"NORMAL"),self.freeze(t+timedelta(hours=1),"HIGH")]
        issued=t+timedelta(hours=1)
        r=evaluate(freezes,self.tape(issued,100),issued+timedelta(hours=13))
        self.assertEqual(r["horizons"]["24h"]["pending_n"],1)
        self.assertEqual(r["horizons"]["24h"]["false_alarm_n"],0)
        self.assertEqual(r["horizons"]["72h"]["pending_n"],1)

    def test_stale_previous_state_never_authorizes_alert(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        r=evaluate([self.freeze(t,"NORMAL"),
                    self.freeze(t+timedelta(hours=25),"HIGH")],
                   self.tape(t,120),t+timedelta(hours=120))
        self.assertEqual(r["new_warning_or_escalation_events"],0)
        self.assertEqual(r["warning_state_counts"]["LEFT_CENSORED_NO_TRANSITION_PROOF"],1)

    def test_real_escalation_not_unlimited_repeats(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        freeze=[self.freeze(t,"BUILDING"),
                self.freeze(t+timedelta(hours=1),"ELEVATED"),
                self.freeze(t+timedelta(hours=2),"HIGH"),
                self.freeze(t+timedelta(hours=3),"HIGH")]
        r=evaluate(freeze,self.tape(t,110),t+timedelta(hours=100))
        self.assertEqual(r["new_warning_or_escalation_events"],2)
        self.assertEqual(r["warning_state_counts"]["ESCALATION"],1)
        self.assertEqual(r["warning_state_counts"]["REPEAT_STATE_NOT_NEW_WARNING"],1)

    def test_data_degradation_cannot_be_used_as_prior_normal_state(self):
        from scripts.learning.pullback_warning_timeliness_shadow import evaluate
        t=START+timedelta(hours=3)
        freeze=[self.freeze(t,"NORMAL"),
                self.freeze(t+timedelta(hours=1),"UNAVAILABLE","BAD"),
                self.freeze(t+timedelta(hours=2),"ELEVATED")]
        r=evaluate(freeze,self.tape(t,100),t+timedelta(hours=100))
        self.assertEqual(r["new_warning_or_escalation_events"],0)
        self.assertEqual(r["warning_state_counts"]["SOURCE_UNAVAILABLE_OR_UNQUALIFIED"],1)
        self.assertEqual(r["warning_state_counts"]["LEFT_CENSORED_NO_TRANSITION_PROOF"],1)

    def test_no_embedded_research_result_can_change_original_forecast(self):
        result=run(self.root,ASOF,"rolling14")
        radar=result["pullback_warning_timebox_shadow"]
        self.assertEqual(radar["trade_permission"],"NONE")
        self.assertFalse(radar["first_known_publication_verified"])
        self.assertFalse(radar["prospective_holdout_completed"])
        self.assertFalse(radar["automatic_model_reweighting"])
        self.assertEqual(result["scientific_decision"]["admissible_automatic_calibration_changes"],[])

if __name__ == "__main__":
    unittest.main()
