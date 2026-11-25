import copy
import math
import unittest
from scripts.research import task2_challenger_a_sqrt_t_vol_band_v1 as A
from scripts.research.cn_mm_c2_relative_tilt_fixture_v1 import fixture_projection, fixture_evaluation

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

    def evaluation_fixture(self):
        f=fixture()
        f["week"]="2026-W49"
        f["issue_clock_utc"]="2026-11-30T00:00:00Z"
        for a in f["assets"].values():
            template=a["days"][0]
            a["days"]=[dict(copy.deepcopy(template),day=k,h=h,
                            scored_from_utc=A.iso(start),end_utc=A.iso(end))
                       for k,start,end,h in A.day_windows(A.utc(f["issue_clock_utc"]),A.utc(f["issue_clock_utc"]))]
        bars={}
        for h in range(7*24):
            t=A.utc(f["issue_clock_utc"])+h*A.HOUR
            bars[t]={"BTC":(98.,99.,97.),"ETH":(102.,103.,101.)}
        return seal(f),bars

    def evaluate(self,f,bars,permission=True,delivery="2026-11-30T00:00:00Z",mature="2026-12-07T00:00:00Z"):
        return fixture_evaluation(f,permission,bars,first_delivery_utc=delivery,evaluated_at_utc=mature)

    def test_matched_evaluation_has_exact_common_denominator_and_relative_direction(self):
        f,bars=self.evaluation_fixture()
        result=self.evaluate(f,bars)
        self.assertEqual(result["paired_day_count"],7)
        self.assertEqual(result["paired_asset_day_count"],14)
        self.assertEqual(result["relative"]["n"],7)
        self.assertEqual(result["by_asset"]["BTC"]["n"],7)
        self.assertEqual(result["relative"]["metrics"]["C2_direction_correct"],1.)
        self.assertEqual(result["relative"]["metrics"]["C1_direction_correct"],0.)
        self.assertFalse(result["edge_established"])
        self.assertFalse(result["first_delivery_verified"])
        self.assertIsNone(result["independent_sample_size"])
        self.assertFalse(result["authority"]["forecast_authority"])

    def test_neutral_is_exact_baseline_for_every_metric(self):
        f,bars=self.evaluation_fixture()
        r=self.evaluate(f,bars,False)
        for panel in (r["all"],r["by_asset"]["BTC"],r["by_asset"]["ETH"],r["relative"]):
            for k,v in panel["metrics"].items():
                if k.startswith("C1_"):
                    self.assertEqual(v,panel["metrics"]["C2_"+k[3:]])
        self.assertEqual(self.evaluate(f,bars,None)["paired_asset_day_count"],0)

    def test_late_delivery_unmatured_and_one_asset_gap_exclude_both(self):
        f,bars=self.evaluation_fixture()
        del bars[A.utc("2026-12-01T05:00:00Z")]["ETH"]
        r=self.evaluate(f,bars,delivery="2026-11-30T00:01:00Z",mature="2026-12-03T00:00:00Z")
        self.assertEqual(r["paired_asset_day_count"],2)
        self.assertEqual([v["day"] for v in r["rows"]],[3,3])
        self.assertEqual(r["abstentions"][0]["reason"],"ABSTAIN_PRE_DELIVERY")
        self.assertEqual(r["abstentions"][1]["reason"],"ABSTAIN_INCOMPLETE_MATCHED_HOURLY")
        self.assertEqual(r["abstentions"][2]["reason"],"ABSTAIN_NOT_MATURE")

    def test_invalid_ohlc_and_resealed_clock_attack_rejected(self):
        f,bars=self.evaluation_fixture()
        bars[A.utc(f["issue_clock_utc"])]["BTC"]=(98.,97.,96.)
        with self.assertRaisesRegex(ValueError,"OHLC_ORDER"):
            self.evaluate(f,bars)
        f,bars=self.evaluation_fixture()
        for asset in f["assets"].values():
            asset["days"][0]["h"]=25.
        with self.assertRaisesRegex(ValueError,"WINDOWS_DO_NOT_MATCH"):
            self.evaluate(seal(f),bars)
        f,bars=self.evaluation_fixture()
        with self.assertRaisesRegex(ValueError,"CLOCK_ORDER"):
            self.evaluate(f,bars,delivery="2026-11-29T23:59:00Z")

    def test_losing_signal_is_not_suppressed_or_retuned(self):
        f,bars=self.evaluation_fixture()
        for row in bars.values():
            row.update(BTC=(102.,103.,101.),ETH=(98.,99.,97.))
        r=self.evaluate(f,bars)
        self.assertEqual(r["relative"]["metrics"]["C2_direction_correct"],0.)
        self.assertGreater(r["relative"]["metrics"]["C2_abs_error_fraction"],
                           r["relative"]["metrics"]["C1_abs_error_fraction"])
        self.assertFalse(r["edge_established"])
