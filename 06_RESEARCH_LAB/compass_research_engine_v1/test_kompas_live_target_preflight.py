"""Synthetic clock, price and completeness controls only."""
import datetime as dt
import unittest
from kompas_live_target_preflight import targets

ISSUED = "2026-11-25T20:25:26Z"


def fixture():
    days = [{"end_utc": (dt.date(2026, 11, 26)+dt.timedelta(days=i)).isoformat()+"T00:00:00Z",
             "lo": 98.0, "centre": 100.0+i, "hi": 110.0} for i in range(8)]
    ends = {str(i): days[i]["end_utc"] for i in (1,3,7)}
    def block():
        return {"status": "OK", "quote": "USDT", "as_of_utc": "2026-11-25T20:00:00Z",
                "p0": 99.0, "points": [["2026-11-25T19:00:00Z", 98.0],
                                       ["2026-11-25T20:00:00Z", 99.0]],
                "days": [dict(x) for x in days],
                "headline": {str(i): {"end_utc": ends[str(i)], "target": days[i]["centre"]}
                             for i in (1,3,7)}}
    return {"contract": "KOMPAS_LIVE_PATH_v1", "generated_at_utc": ISSUED,
            "status": "OK", "horizon_end_utc": ends,
            "authority": {"research_only": True, "official_forecast": False,
                          "compass_probability_claim": False, "trading": False,
                          "promotion": False, "site_synthesis": False},
            "assets": {"BTC": block(), "ETH": block()}}


class TargetTests(unittest.TestCase):
    def test_all_targets_and_baseline(self):
        r = targets(fixture())
        self.assertEqual(len(r["rows"]), 6)
        self.assertEqual(r["rows"][1]["target_utc"], "2026-11-29T00:00:00Z")
        self.assertEqual(r["rows"][1]["candidate_close"], 103)
        self.assertEqual(r["rows"][1]["baseline_close"], 99)
        self.assertGreater(r["rows"][1]["duration_from_issue_hours"], 72)
        self.assertIs(r["scoring_authorized"], False)
        self.assertEqual(r["candidate_variant"], "PRODUCER_PRIMARY_NOT_VIEWER_STATE")
        self.assertTrue(all(row["quote"] == "USDT" for row in r["rows"]))

    def test_unavailable_rows_retained(self):
        d = fixture()
        d["assets"]["ETH"] = {"status": "UNAVAILABLE", "quote": "USDT"}
        d["status"] = "PARTIAL"
        rows = targets(d)["rows"]
        self.assertEqual([r["status"] for r in rows[3:]], ["UNAVAILABLE"]*3)
        self.assertTrue(all(r["candidate_close"] is None for r in rows[3:]))

    def test_mutations(self):
        for mutate in (
                lambda d: d["authority"].update(trading=True),
                lambda d: d["horizon_end_utc"].update({"3": "2026-11-28T00:00:00Z"}),
                lambda d: d["assets"]["BTC"]["headline"]["3"].update(target=1),
                lambda d: d["assets"]["BTC"]["days"].pop(0),
                lambda d: d["assets"]["BTC"]["days"].append(d["assets"]["BTC"]["days"][0]),
                lambda d: d["assets"]["BTC"].update(quote="USD"),
                lambda d: d["assets"]["BTC"].update(as_of_utc="2026-11-25T21:00:00Z"),
                lambda d: d["assets"]["BTC"].update(p0=True),
                lambda d: d["assets"]["BTC"]["days"][0].update(lo=200),
                lambda d: d.update(status="PARTIAL")):
            d = fixture()
            mutate(d)
            with self.subTest(d=d), self.assertRaises(ValueError):
                targets(d)

    def test_reference_tail_mutations(self):
        for mutate in (
                lambda b: b.update(p0=100),
                lambda b: b["points"][-1].__setitem__(1, 100),
                lambda b: b["points"].pop(),
                lambda b: b["points"].reverse(),
                lambda b: b["points"].insert(0, ["2026-11-25T19:00:00Z", 98]),
                lambda b: b["points"][0].__setitem__(0, "2026-11-25T19:01:00Z"),
                lambda b: b["points"].append(["2026-11-25T21:00:00Z", 99]),
                lambda b: b.update(points=[]),
                lambda b: b["points"][0].__setitem__(1, True),
                lambda b: b["days"].reverse()):
            d = fixture()
            mutate(d["assets"]["BTC"])
            with self.subTest(b=d["assets"]["BTC"]), self.assertRaises(ValueError):
                targets(d)

    def test_midnight_exact_targets(self):
        d = fixture()
        d["generated_at_utc"] = "2026-11-26T00:00:00Z"
        for b in d["assets"].values():
            b["days"].pop(0)
            b["as_of_utc"] = "2026-11-26T00:00:00Z"
            b["points"] = [["2026-11-26T00:00:00Z", 99]]
        r = targets(d)
        self.assertEqual([x["duration_from_issue_hours"] for x in r["rows"][:3]], [24, 72, 168])
        self.assertFalse(r["scoring_authorized"])
