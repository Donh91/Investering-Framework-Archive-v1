"""Adversarial tests for frozen W46 official issuances. All data are synthetic."""
import json
import unittest

from scripts.research import w46_official_issuance_census_v1 as m

def fixture(day, token, btc, *, risk="ELEVATED", action="HOLD_WAIT", status="OK"):
    d={
        "compass_id": "CMP-202611%s-%s"%(day,token),
        "issued_at_utc": "2026-11-%sT12:00:00Z"%day,
        "market_reference":{"btc_usdt":btc},
        "protection_tracker":{"pullback_risk_state":risk},
        "action_now":action,"data_status":status,
        "horizons":{
            "NEXT_1_3D":{"expected_direction":"DOWN"},
            "NEXT_5_7D":{"expected_direction":"MIXED"},
            "NEXT_2_3W":{"expected_direction":"UNAVAILABLE"},
        },
    }
    path="04_MARKET_LEARNING/handlekompas/official/daily/2026/11/%s/CMP-202611%s-%s.json"%(day,day,token)
    return path, (json.dumps(d,sort_keys=True)+"\n").encode()

def freeze(low=70):
    return json.dumps({"btc_range_low":low}).encode()

class W46FrozenCensusTests(unittest.TestCase):
    def test_direction_and_risk_are_not_action_or_verified_delivery(self):
        s, rows=m.summarize(
            [fixture("09","aaaaaaaaaaaa",71),
             fixture("13","bbbbbbbbbbbb",69)],freeze(),exact_count=2)
        self.assertEqual(s["risk_counts"],{"ELEVATED":2})
        self.assertEqual(s["action_counts"],{"HOLD_WAIT":2})
        self.assertEqual(s["h1_3d_counts"],{"DOWN":2})
        self.assertEqual(s["h5_7d_counts"],{"MIXED":2})
        self.assertEqual(s["issuer_reference_below_floor_count"],1)
        self.assertEqual(s["issuer_reference_below_floor_elevated"],1)
        self.assertEqual(s["first_below_floor_issue_claim_utc"],"2026-11-13T12:00:00Z")
        self.assertEqual(s["first_market_trade_breach"],"UNKNOWN")
        self.assertEqual(s["warning_skill"],"NOT_ESTABLISHED")
        self.assertEqual(s["paper_action_utility"],"NOT_MEASURED")
        self.assertEqual(rows[1]["website_delivery_verification"],"UNKNOWN")
        self.assertTrue(s["no_trade"])

    def test_degraded_risk_still_counted_separately(self):
        s,_=m.summarize([fixture("13","aaaaaaaaaaaa",69,risk="ELEVATED",
                                   status="DEGRADED")],freeze(),exact_count=1)
        self.assertEqual(s["data_status_counts"],{"DEGRADED":1})
        self.assertEqual(s["risk_counts"],{"ELEVATED":1})

    def test_incomplete_census_refused(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_ISSUANCE_CENSUS_INCOMPLETE"):
            m.summarize([],freeze(),exact_count=42)

    def test_duplicate_same_filename_refused(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        with self.assertRaisesRegex(ValueError,"SOURCE_ISSUANCE_CENSUS_INCOMPLETE"):
            m.summarize([a,a],freeze(),exact_count=2)

    def test_duplicate_identical_issuer_in_distinct_files_refused(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        b=fixture("13","bbbbbbbbbbbb",68)
        d=json.loads(b[1]);d["compass_id"]=json.loads(a[1])["compass_id"]
        with self.assertRaisesRegex(ValueError,"DUPLICATED_ISSUANCE_ID"):
            m.summarize([a,(b[0],json.dumps(d).encode())],freeze(),exact_count=2)

    def test_tampered_timezone_not_recognized_as_utc(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        d=json.loads(a[1]);d["issued_at_utc"]="2026-11-13T12:00:00+02:00"
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_ISSUANCE"):
            m.summarize([(a[0],json.dumps(d).encode())],freeze(),exact_count=1)

    def test_wrong_day_directory_refused(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        d=json.loads(a[1]);d["issued_at_utc"]="2026-11-12T12:00:00Z"
        with self.assertRaisesRegex(ValueError,"ISSUER_DATE_DIRECTORY_MISMATCH"):
            m.summarize([(a[0],json.dumps(d).encode())],freeze(),exact_count=1)

    def test_missing_protection_field_refused(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        d=json.loads(a[1]);del d["protection_tracker"]
        with self.assertRaisesRegex(ValueError,"INVALID_ORIGINAL_ISSUANCE"):
            m.summarize([(a[0],json.dumps(d).encode())],freeze(),exact_count=1)

    def test_missing_or_nonsensical_frozen_floor_refused(self):
        a=fixture("13","aaaaaaaaaaaa",69)
        for raw in [b"{}",freeze(-3),freeze(1e12)]:
            with self.assertRaisesRegex(ValueError,"FROZEN_"):
                m.summarize([a],raw,exact_count=1)

if __name__=="__main__":
    unittest.main()
