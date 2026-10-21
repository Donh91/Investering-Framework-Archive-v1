"""Original-issue vs same-day schedule-clock diagnostic; negative causality controls."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts.research import task2_official_slot_clock_census_v1 as m

WORKFLOW_TEXT="""name: Official Daily Compass
on:
  schedule:
    # The slot gate below activates exactly one candidate per local slot.
    - cron: '17 6 * * *'
    - cron: '17 7 * * *'
    - cron: '17 18 * * *'
    - cron: '17 19 * * *'
"""
def fake(day=12,reason="SCHEDULED_MORNING",hour=11,minute=30,num=1):
    ident=f"CMP-202610{day:02d}-fixture{num:03d}"
    j={"contract":m.original.EXPECTED_CONTRACT,
       "compass_id":ident,"issued_at_utc":f"2026-10-{day:02d}T{hour:02d}:{minute:02d}:00Z",
       "compass_sha256":"a"*64,"scoring_contract":m.original.V3,
       "source_bindings":{"auto_market_state":{"packet_path":"packet.json","packet_sha256":"b"*64}},
       "outcome_maturity":{"12h":"PENDING","72h":"PENDING","168h":"PENDING"},
       "run_reason":reason}
    path=f"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/{day:02d}/{ident}.json"
    return path,json.dumps(j).encode("utf-8")

class Task2OriginalSlotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.flow=Path(self.temp.name)/"daily-compass.yml"
        self.flow.write_text(WORKFLOW_TEXT)
    def score(self,rows):
        return m.score(rows,workflow=self.flow,strict=False)
    def test_issuer_clock_not_retroassigned_to_cron(self):
        x=self.score([fake()])
        self.assertEqual(x["counts"]["observed_original_forecasts"],1)
        self.assertEqual(x["counts"]["expected_local_schedule_slot_dates"],18)
        self.assertEqual(x["counts"]["missing_same_day_declared_reason"],17)
        self.assertEqual(x["diagnostic_counts"]["ISSUED_AFTER_NOMINAL_BY_MORE_THAN_90_MINUTES"],1)
        self.assertFalse(x["same_day_schedule_assignment_proven"])
        self.assertFalse(x["clock_diagnostic_is_actual_job_delay"])
        self.assertFalse(x["first_delivery_verified"])
    def test_a_forecast_before_evening_nominal_is_not_false_delay(self):
        x=self.score([fake(day=13,reason="SCHEDULED_EVENING",hour=0,minute=49)])
        self.assertEqual(x["diagnostic_counts"]["ISSUED_BEFORE_SAME_DAY_NOMINAL_SLOT"],1)
        self.assertEqual(x["scheduled_originals"][0]["diagnostic_class"],
                         "ISSUED_BEFORE_SAME_DAY_NOMINAL_SLOT")
        self.assertFalse(x["scheduled_originals"][0]["verified_actual_schedule_lateness"])
    def test_near_nominal_still_not_public_delivery_proof(self):
        x=self.score([fake(hour=6,minute=33)])
        self.assertEqual(x["diagnostic_counts"]["ISSUED_WITHIN_90_MINUTES_OF_SAME_DAY_NOMINAL"],1)
        self.assertFalse(x["scheduled_originals"][0]["original_github_run_id_binding_verified"])
    def test_event_driven_does_not_fill_scheduled_slots(self):
        x=self.score([fake(reason="EVENT_DRIVEN")])
        self.assertEqual(x["counts"]["scheduled_reason_files"],0)
        self.assertEqual(x["counts"]["missing_same_day_declared_reason"],18)
        self.assertEqual(x["counts"]["event_driven_or_on_demand"],1)
    def test_two_scheduled_same_reason_same_day_quarantine(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SAME_DAY_SCHEDULE_REASON"):
            self.score([fake(num=1),fake(num=2)])
    def test_two_distinct_scheduled_reasons_ok(self):
        x=self.score([fake(),fake(reason="SCHEDULED_EVENING",hour=21,num=2)])
        self.assertEqual(x["counts"]["scheduled_reason_files"],2)
        self.assertEqual(x["counts"]["missing_same_day_declared_reason"],16)
    def test_duplicate_original_path_quarantine(self):
        item=fake()
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ORIGINAL_FORECAST_FILE"):
            self.score([item,item])
    def test_unknown_reason_not_counted_as_event(self):
        p,b=fake()
        j=json.loads(b);j["run_reason"]="UNVERIFIED_FUTURE"
        with self.assertRaisesRegex(ValueError,"UNKNOWN_ORIGINAL_RUN_REASON"):
            self.score([(p,json.dumps(j).encode())])
    def test_outside_cohort_fails_closed(self):
        p,b=fake(day=11)
        with self.assertRaisesRegex(ValueError,"OUTSIDE_FIXED_ARCHIVE_COHORT"):
            self.score([(p,b)])
    def test_bad_hash_does_not_gain_admission(self):
        p,b=fake();j=json.loads(b);j["compass_sha256"]="nohash"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FORECAST_PREFLIGHT_INVALID"):
            self.score([(p,json.dumps(j).encode())])
    def test_forecast_issue_folder_mismatch_fails_closed(self):
        p,b=fake(day=12)
        j=json.loads(b);j["issued_at_utc"]="2026-10-13T11:30:00Z"
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FORECAST_PREFLIGHT_INVALID"):
            self.score([(p,json.dumps(j).encode())])
    def test_unrecognised_cron_change_not_pass(self):
        self.flow.write_text(WORKFLOW_TEXT.replace("17 6","16 6"))
        with self.assertRaisesRegex(ValueError,"PRODUCER_WORKFLOW_CRON_CONTRACT_NOT_RECOGNIZED"):
            self.score([fake()])
    def test_no_scientific_alpha_from_report(self):
        x=self.score([fake()])
        self.assertFalse(x["scientific_edge_established"])
        self.assertFalse(x["provider_first_publication_verified"])
        self.assertFalse(x["clock_diagnostic_is_actual_job_delay"])
        self.assertEqual(x["counts"]["scientifically_admitted_forecast_causality"],0)
    def test_original_git_blob_identity_replay(self):
        p,b=fake()
        x=self.score([(p,b)])
        self.assertEqual(x["original_source_git_blob_manifest"][0]["original_git_blob_sha1"],
                         m.original.blob_sha(b))
    def test_full_original_70_case_evidence_if_mounted(self):
        if m.FORECAST_ROOT.is_dir() and m.WORKFLOW.is_file():
            q=m.execute()
            self.assertEqual(q["counts"]["observed_original_forecasts"],70)
            self.assertEqual(q["counts"]["scheduled_reason_files"],17)
            self.assertEqual(q["counts"]["expected_local_schedule_slot_dates"],18)
            self.assertEqual(q["counts"]["missing_same_day_declared_reason"],1)
            self.assertFalse(q["first_delivery_verified"])
            self.assertFalse(q["same_day_schedule_assignment_proven"])
if __name__=="__main__":
    unittest.main()
