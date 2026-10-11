from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/cycle_navigator"
sys.path.insert(0, str(SCRIPT))
from build_v2_edge_forecast_freeze import build, canon, fmt, utc

UTC = timezone.utc
FROZEN = datetime(2026,10,12,7,5,tzinfo=UTC)
NOW = datetime(2026,10,12,7,20,tzinfo=UTC)


def add(root, path, obj):
    file = root / path
    file.parent.mkdir(parents=True,exist_ok=True)
    blob=canon(obj)
    file.write_bytes(blob)
    return hashlib.sha256(blob).hexdigest()


def fixture(root, *, risk="NORMAL", week=42, issue=29, stale=False):
    wd=f"05_CYCLE_NAVIGATOR/weekly/2026/W{week:02d}"
    freeze={
        "scoring_contract":"CN_PUBLIC_CONTINUITY_v1",
        "ethbtc_condition":"ETH/BTC close <= open, conditional.",
        "breadth_condition":"Multi-horizon breadth not confirmed.",
        "structural_calls":["Regime", "ETHBTC", "Rotation", "Breadth", "Flow"],
        "market_structure_analysis":{"dimensions":[{"id":"LEADERSHIP","analysis":"Unconfirmed"}]},
        "intraday_map":{"day_1_2":"BTC price range", "day_3_4":"Range", "day_5_7":"Range"},
        "btc_range_low":81000,"btc_range_high":92000,
        "eth_range_low":2500,"eth_range_high":2900,
    }
    fsha=add(root,f"{wd}/CYCLE_NAVIGATOR_FORECAST_FREEZE.json",freeze)
    add(root,f"{wd}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",{
        "public_issue_number":issue,"base_case_2_3_weeks":"Selective rotation only",
        "base_case_4_8_weeks":"No verified long-range signal",
    })
    add(root,f"{wd}/CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json",{
        "public_issue_number":issue,"forecast_week":f"2026-W{week:02d}",
        "source_forecast_freeze_sha256":fsha,"score_window_policy":"FIRST_COMPLETE_UTC_HOUR_AT_OR_AFTER_FREEZE_v1",
        "scoring_valid_from_utc":"2026-10-12T07:00:00Z",
        "frozen_unix":int(FROZEN.timestamp()),
    })
    add(root,f"{wd}/CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json",{
        "public_issue_number":issue,"forecast_week":f"2026-W{week:02d}"
    })
    add(root,"05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json",{
        "week_dir":wd,"iso_year":2026,"iso_week":week,"public_issue_number":issue,
    })
    issued=FROZEN-timedelta(days=2 if stale else 0)
    c={
        "contract":"PUBLIC_COMPASS_PROJECTION_v1","data_status":"OK",
        "issued_at_utc":fmt(issued),"compass_id":"CMP-TEST",
        "protection_tracker":{
            "pullback_risk_state":risk,"distribution_risk":"UNKNOWN",
            "eta_window":"UNKNOWN","reentry_state":"INACTIVE"
        }
    }
    path="04_MARKET_LEARNING/handlekompas/official/public/2026/10/12/CMP-TEST.json"
    sha=add(root,path,c)
    add(root,"04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json",{
        "public_projection_path":path,"compass_id":"CMP-TEST",
        "public_projection_content_sha256":sha
    })


class EdgeSourceFreezeTests(unittest.TestCase):
    def build_case(self, risk="NORMAL", week=42, issue=29, stale=False):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fixture(root,risk=risk,week=week,issue=issue,stale=stale)
            result=build(root,NOW)
            if result is None:return None
            bundle,rel=result
            return bundle,rel

    def test_first_week_must_be_w42_issue_29(self):
        self.assertIsNone(self.build_case(week=41,issue=28))

    def test_normal_is_explicit_no_warning_one_eligible_claim(self):
        bundle,path=self.build_case()
        self.assertEqual(bundle["contract"],"CN_V2_FROZEN_CLAIMS_v1")
        self.assertEqual(bundle["public_issue_number"],29)
        self.assertTrue(path.endswith("CYCLE_NAVIGATOR_V2_EDGE_FREEZE.json"))
        risk=[c for c in bundle["claims"] if c["kind"]=="EVENT_OCCURRENCE"]
        self.assertEqual(len(risk),1)
        self.assertEqual(risk[0]["declared_state"],"ELIGIBLE")
        self.assertIs(risk[0]["expected_event"],False)
        self.assertEqual(risk[0]["threshold_pct"],5)
        self.assertEqual(risk[0]["evaluation_end_utc"],"2026-10-13T08:00:00Z")
        self.assertEqual(bundle["scoring_valid_from_utc"],"2026-10-12T08:00:00Z")

    def test_building_is_watch_abstention_not_false_numeric_alert(self):
        bundle,_=self.build_case(risk="BUILDING")
        risk=bundle["claims"][-1]
        self.assertEqual(risk["declared_state"],"ABSTAIN")
        self.assertNotIn("expected_event",risk)
        self.assertEqual(bundle["compass_risk_snapshot"]["risk_state"],"BUILDING")

    def test_high_is_scored_material_warning_not_sell_instruction(self):
        bundle,_=self.build_case(risk="HIGH")
        risk=bundle["claims"][-1]
        self.assertTrue(risk["expected_event"])
        self.assertEqual(bundle["authority"],"ACCOUNTABILITY_ONLY_NO_PORTFOLIO_EXECUTION")

    def test_stale_compass_never_reinterpreted_as_no_warning(self):
        bundle,_=self.build_case(risk="NORMAL",stale=True)
        self.assertEqual(bundle["claims"][-1]["declared_state"],"ABSTAIN")

    def test_multiple_horizons_persist_as_source_bound_abstentions(self):
        bundle,_=self.build_case()
        claims=bundle["claims"]
        self.assertEqual(len(claims),10)
        for offset in (14,21,28,56):
            item=next(x for x in claims if x["claim_id"].endswith(f"DIRECTION_{offset}D"))
            self.assertEqual(item["declared_state"],"ABSTAIN")
            self.assertEqual(utc(item["evaluation_end_utc"])-utc(item["evaluation_start_utc"]),timedelta(days=offset))

    def test_original_source_hash_binding(self):
        bundle,_=self.build_case()
        self.assertEqual(bundle["source_sha256"],hashlib.sha256(canon(bundle["source_manifest"])).hexdigest())
        self.assertTrue(all(c["source_sha256"]==bundle["source_sha256"] for c in bundle["claims"]))

    def test_mismatched_forecast_freeze_hash_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            fixture(root)
            file=root/"05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json"
            obj=json.loads(file.read_text());obj["source_forecast_freeze_sha256"]="a"*64
            file.write_bytes(canon(obj))
            with self.assertRaisesRegex(ValueError,"forecast_source_digest_mismatch"):
                build(root,NOW)

    def test_issuance_before_source_freeze_forbidden(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            with self.assertRaisesRegex(ValueError,"cannot_issue_claims_before_source_was_frozen"):
                build(root,FROZEN-timedelta(seconds=1))

    def test_mismatched_public_cn_binding_forbidden(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            file=root/"05_CYCLE_NAVIGATOR/weekly/2026/W42/CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json"
            obj=json.loads(file.read_text());obj["public_issue_number"]=30;file.write_bytes(canon(obj))
            with self.assertRaisesRegex(ValueError,"public_cn_identity_mismatch"):
                build(root,NOW)

    def test_compass_pointer_digest_tampering_not_accepted(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);fixture(root)
            file=root/"04_MARKET_LEARNING/handlekompas/official/PUBLIC_LATEST_COMPASS.json"
            obj=json.loads(file.read_text());obj["public_projection_content_sha256"]="0"*64;file.write_bytes(canon(obj))
            bundle,_=build(root,NOW)
            self.assertEqual(bundle["compass_risk_snapshot"]["availability"],"UNVERIFIABLE_SOURCE")
            self.assertEqual(bundle["claims"][-1]["declared_state"],"ABSTAIN")


if __name__=="__main__":
    unittest.main()
