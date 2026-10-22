"""Task2 R1 original issuer scientific gate: deterministic source-only negative controls."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.research import task2_official_r1_original_evidence_gate_v1 as m

ISSUE="2026-10-12T12:00:00Z"
CASE="CMP-20261012-synthetic-original"
REL="04_MARKET_LEARNING/handlekompas/official/daily/2026/10/12/"+CASE+".json"

def forecast(version=m.V3):
    return {"contract":m.EXPECTED_CONTRACT,"compass_id":CASE,"issued_at_utc":ISSUE,
            "compass_sha256":"a"*64,"scoring_contract":version,
            "source_bindings":{"auto_market_state":{"packet_path":"source.json","packet_sha256":"c"*64}},
            "outcome_maturity":{"12h":"PENDING_MATURITY","72h":"PENDING_MATURITY","168h":"PENDING_MATURITY"}}

def outcome(version=m.V3):
    return {"contract":m.EXPECTED_OUTCOME,"horizon":"12h","compass_id":CASE,
            "compass_sha256":"a"*64,"forecast_path":REL,
            "scoring_contract":version,"issued_at_utc":ISSUE,
            "target_at_utc":"2026-10-13T00:00:00Z",
            "target_observation_at_utc":"2026-10-13T00:00:00Z",
            "matured_at_utc":"2026-10-13T01:00:00Z",
            "direction_accuracy":{"btc":{"result":"ABSTAINED"},"eth":{"result":"INCORRECT"}}}

class OriginalEvidenceTests(unittest.TestCase):
    def test_base_source_witness_structurally_consistent(self):
        a=m.preflight_forecast(forecast(),Path(CASE+".json"),m.FIRST)
        self.assertEqual(a,[])
        r,labels=m.original_outcome_assessment(forecast(),REL,outcome(),Path("unused.json"),"12h")
        self.assertEqual(r,[])
        self.assertEqual(labels,{"ABSTAINED":1,"INCORRECT":1})
    def test_future_outcome_not_relabelled_as_correct(self):
        x=outcome();x["direction_accuracy"]["btc"]["result"]="ABSTAINED"
        r,labels=m.original_outcome_assessment(forecast(),REL,x,Path("a"),"12h")
        self.assertEqual(labels["ABSTAINED"],1)
        self.assertEqual(labels["INCORRECT"],1)
    def test_target_mismatch_quarantines(self):
        x=outcome();x["target_observation_at_utc"]="2026-10-13T01:00:00Z"
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("TARGET_OBSERVATION_CLOCK_MISMATCH",a)
    def test_late_maturity_not_backdated(self):
        x=outcome();x["matured_at_utc"]="2026-10-22T01:00:00Z"
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("OUTCOME_MATURITY_AFTER_FROZEN_CUTOFF",a)
    def test_maturity_before_target(self):
        x=outcome();x["matured_at_utc"]="2026-10-12T23:00:00Z"
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("MATURITY_BEFORE_OUTCOME_TARGET",a)
    def test_forecast_content_hash_identity_required(self):
        x=outcome();x["compass_sha256"]="b"*64
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("ORIGINAL_FORECAST_HASH_MISMATCH",a)
    def test_outcome_forecast_path_identity_required(self):
        x=outcome();x["forecast_path"]="fake.json"
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("ORIGINAL_FORECAST_PATH_MISMATCH",a)
    def test_version_upgrade_never_silent(self):
        x=outcome();x["scoring_contract"]="OFFICIAL_DAILY_COMPASS_SCORING_v2"
        a,_=m.original_outcome_assessment(forecast(),REL,x,Path("x"),"12h")
        self.assertIn("ORIGINAL_SCORING_CONTRACT_MISMATCH",a)
    def test_forecast_bad_utc_timezone_cannot_pass(self):
        x=forecast();x["issued_at_utc"]="2026-10-12T12:00:00+00:00"
        a=m.preflight_forecast(x,Path(CASE+".json"),m.FIRST)
        self.assertIn("ORIGINAL_ISSUE_CLOCK_INVALID",a)
    def test_empty_source_binding_does_not_crash_silent(self):
        x=forecast();x["source_bindings"]={}
        a=m.preflight_forecast(x,Path(CASE+".json"),m.FIRST)
        self.assertIn("ORIGINAL_UPSTREAM_PACKET_BINDING_MISSING",a)
    def test_missing_outcome_keeps_exclusion_denominator(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for day in m.days():
                directory=root/"daily"/day.strftime("%Y/%m/%d")
                directory.mkdir(parents=True)
                for j in range(3):
                    ff=forecast()
                    ff["compass_id"]="CMP-"+day.strftime("%Y%m%d")+f"-fixture{j}"
                    ff["issued_at_utc"]=day.strftime("%Y-%m-%dT12:00:00Z")
                    ff["compass_sha256"]=m.original_compass_self_digest(ff)
                    (directory/(ff["compass_id"]+".json")).write_text(json.dumps(ff))
            y=m.census(root)
            self.assertEqual(y["counts"]["original_forecasts"],27)
            self.assertEqual(y["counts"]["missing_original_outcome_files"],81)
            self.assertEqual(len(y["original_records"]),81)
            self.assertEqual(y["per_horizon_receipt_states"]["12h::NO_ORIGINAL_OUTCOME_FILE_AT_SNAPSHOT"],27)
            self.assertEqual(y["per_horizon_receipt_states"]["72h::NO_ORIGINAL_OUTCOME_FILE_AT_SNAPSHOT"],27)
            self.assertEqual(y["per_horizon_receipt_states"]["168h::NO_ORIGINAL_OUTCOME_FILE_AT_SNAPSHOT"],27)
            self.assertEqual(y["original_integrity_exception_counts"],{})
            self.assertEqual(y["forecasts_by_scoring_contract"][m.V3],27)
            self.assertFalse(y["model_skill_or_return_estimated"])
            self.assertEqual(y["independent_shock_families_certified"],0)
    def test_shuffled_fake_outcome_without_original_is_reported_not_filled(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for day in m.days():
                directory=root/"daily"/day.strftime("%Y/%m/%d")
                directory.mkdir(parents=True)
                for j in range(3):
                    ff=forecast()
                    ff["compass_id"]="CMP-"+day.strftime("%Y%m%d")+f"-fixture{j}"
                    ff["issued_at_utc"]=day.strftime("%Y-%m-%dT12:00:00Z")
                    ff["compass_sha256"]=m.original_compass_self_digest(ff)
                    (directory/(ff["compass_id"]+".json")).write_text(json.dumps(ff))
            extra=root/"outcomes"/"2026/10/12"
            extra.mkdir(parents=True)
            (extra/"CMP-unregistered_12h.json").write_text(json.dumps(outcome()))
            y=m.census(root)
            self.assertEqual(y["counts"]["unmatched_outcome_files"],1)
            self.assertEqual(len(y["unmatched_outcome_files"]),1)
    def test_score_version_counts_not_absolute_accuracy(self):
        self.assertEqual(m.HORIZONS,("12h","72h","168h"))
        self.assertFalse(m.census.__doc__=="SCIENTIFIC_EDGE_PROVED")
    def test_full_original_frozen_week_if_repo_files_available(self):
        if m.BASE.exists():
            q=m.census()
            self.assertGreater(q["counts"]["original_forecasts"],20)
            self.assertEqual(len(q["original_records"]),q["counts"]["original_forecasts"]*3)
            self.assertEqual(sum(q["per_horizon_receipt_states"].values()),3*q["counts"]["original_forecasts"])
            self.assertFalse(q["provider_first_publication_verified"])
            self.assertFalse(q["actual_delivery_first_known_verified"])
            self.assertFalse(q["first_known_market_value_eligibility_unlocked"])
            self.assertEqual(q["private_round3_gate"],"ROUND3_COLLECTION_ONLY_ANALYSIS_OFF")
    def test_frozen_forecast_content_digest_detects_tampering(self):
        doc=forecast()
        doc["compass_sha256"]=m.original_compass_self_digest(doc)
        self.assertEqual(m.original_compass_self_digest(doc),doc["compass_sha256"])
        doc["outcome_maturity"]["12h"]="RETROACTIVE_TAMPER"
        self.assertNotEqual(m.original_compass_self_digest(doc),doc["compass_sha256"])
        self.assertIsNone(m.original_compass_self_digest({"invalid":float("nan")}))

    def test_census_quarantines_one_corrupted_forecast_all_three_horizons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for day in m.days():
                sub=day.strftime("%Y/%m/%d")
                (root/"daily"/sub).mkdir(parents=True)
                (root/"outcomes"/sub).mkdir(parents=True)
            for i in range(21):
                doc=forecast()
                doc["compass_id"]=f"CMP-20261012-SYNTH{i:03d}"
                doc["compass_sha256"]=m.original_compass_self_digest(doc)
                if i==7:
                    doc["outcome_maturity"]["12h"]="FORGED_AFTER_FREEZE"
                (root/"daily"/"2026/10/12"/(doc["compass_id"]+".json")).write_text(
                    json.dumps(doc,sort_keys=True)+"\n",encoding="utf-8")
            report=m.census(root)
            self.assertEqual(report["counts"]["original_forecasts"],21)
            self.assertEqual(report["original_integrity_exception_counts"]["ORIGINAL_FORECAST_SELF_HASH_MISMATCH"],3)
            self.assertEqual(report["counts"]["ORIGINAL_FORECAST_QUARANTINED_NO_OUTCOME"],3)
            self.assertFalse(report["first_known_market_value_eligibility_unlocked"])

if __name__=="__main__":
    unittest.main()
