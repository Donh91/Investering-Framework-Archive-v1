import copy
import math
import unittest
from scripts.research import task2_challenger_a_sqrt_t_vol_band_v1 as A
from scripts.research.cn_mm_c2_relative_tilt_fixture_v1 import fixture_projection

def fixture():
    bands={family:{"0.5":[90.,110.],"0.8":[80.,120.],"0.95":[70.,130.]} for family in ("close","range")}
    day={"day":1,"h":24.,"scored_from_utc":"2026-11-30T00:00:00Z","end_utc":"2026-12-01T00:00:00Z","band":bands}
    body={"contract":A.CONTRACT,"formula_version":A.FORMULA_VERSION,"source":{"clock_class":"FIXTURE_NOT_MAIN_ATTESTED"},
          "assets":{"BTC":{"P0":100.,"sigma_hourly":.01,"days":[copy.deepcopy(day)]},
                    "ETH":{"P0":100.,"sigma_hourly":.02,"days":[copy.deepcopy(day)]}}}
    return seal(body)

def seal(body):
    body.pop("issuance_sha256",None)
    body["issuance_sha256"]=A._digest(body)
    return body

class C2FixtureTests(unittest.TestCase):
    def test_symmetric_relative_tilt_and_log_width(self):
        f=fixture()
        out=fixture_projection(f,True)
        b,e=(out["assets"][a]["days"][0] for a in ("BTC","ETH"))
        self.assertAlmostEqual(b["centre"]*e["centre"],10000.)
        self.assertAlmostEqual(math.log(e["centre"]/b["centre"]),.5*.01*math.sqrt(24))
        self.assertAlmostEqual(e["bands"]["close"]["0.8"][1]/e["bands"]["close"]["0.8"][0],1.5)
        self.assertFalse(out["authority"]["forecast_authority"])
        self.assertFalse(out["interval_coverage_recalibrated"])
    def test_false_is_neutral_unknown_abstains(self):
        f=fixture()
        out=fixture_projection(f,False)
        self.assertEqual(out["assets"]["ETH"]["days"][0]["centre"],100.)
        self.assertEqual(out["assets"]["ETH"]["days"][0]["bands"],f["assets"]["ETH"]["days"][0]["band"])
        self.assertEqual(fixture_projection(f,None)["assets"],{})
        with self.assertRaisesRegex(ValueError,"PERMISSION_INVALID"):
            fixture_projection(f,1)
    def test_live_source_and_tampered_digest_rejected(self):
        f=fixture()
        f["source"]={"clock_class":"MAIN_FIRST_PARENT_COMMITTER_CLOCK_NOT_HTTP_DELIVERY"}
        with self.assertRaisesRegex(ValueError,"REAL_ISSUANCE_FORBIDDEN"):
            fixture_projection(seal(f),True)
        f=fixture()
        f["assets"]["ETH"]["P0"]=90.
        with self.assertRaisesRegex(ValueError,"digest"):
            fixture_projection(f,True)
    def test_mismatched_window_and_invalid_band(self):
        f=fixture()
        f["assets"]["ETH"]["days"][0]["h"]=25.
        with self.assertRaisesRegex(ValueError,"MATCHED_WINDOWS"):
            fixture_projection(seal(f),True)
        f=fixture()
        f["assets"]["ETH"]["days"][0]["band"]["close"]["0.8"]=[95.,105.]
        with self.assertRaisesRegex(ValueError,"BAND_INVALID"):
            fixture_projection(seal(f),True)
