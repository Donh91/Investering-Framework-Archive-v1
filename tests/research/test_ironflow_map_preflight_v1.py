import json
import unittest
from scripts.research.ironflow_map_preflight_v1 import preflight


def fixture():
    return dict(market="BTC-PERP", side="both", stale=False, mark_px=100, bucket_size=2,
                range_pct=10, as_of="2026-11-24T12:01:00Z",
                snapshot=dict(height=123, time="2026-11-24T12:00:00Z"),
                coverage=dict(with_liq_px_pct=98, notional_usd=10000),
                levels=[dict(price_lo=94, price_hi=96, long_usd=100, short_usd=0,
                             long_positions=2, short_positions=0),
                        dict(price_lo=104, price_hi=106, long_usd=0, short_usd=50,
                             long_positions=0, short_positions=1)])


def run(p, received="2026-11-24T12:02:00Z", cutoff="2026-11-24T12:03:00Z"):
    return preflight(json.dumps(p).encode(), "BTC-PERP", received, cutoff)


class TestMap(unittest.TestCase):
    def test_partial_never_promoted(self):
        x = run(fixture())
        self.assertEqual(x["coverage_class"], "TOP10_PARTIAL_MODELLED_MAP")
        self.assertIsNone(x["full_map_features"])
        self.assertIsNone(x["signal"])
        self.assertFalse(x["first_known_verified"])

    def test_clock(self):
        for r, c in [("2026-11-24T12:00:00Z", "2026-11-24T12:03:00Z"),
                     ("2026-11-24T12:02:00Z", "2026-11-24T12:02:00Z"),
                     ("2026-11-24T12:02:00Z", "2026-11-24T12:31:00Z")]:
            with self.subTest(r=r, c=c), self.assertRaises(ValueError):
                run(fixture(), r, c)

    def test_scope_and_health(self):
        for key, value in [("market", "ETH-PERP"), ("stale", True), ("side", "long"), ("range_pct", 50)]:
            p = fixture(); p[key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                run(p)

    def test_numeric_and_overlap(self):
        for key, value in [("long_usd", float("nan")), ("short_usd", -1),
                           ("long_positions", True), ("price_hi", 95)]:
            p = fixture(); p["levels"][0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                run(p)
        p = fixture(); p["levels"].append(dict(p["levels"][0]))
        with self.assertRaises(ValueError):
            run(p)

    def test_empty_and_duplicate_json(self):
        p = fixture(); p["levels"] = []
        with self.assertRaises(ValueError):
            run(p)
        with self.assertRaisesRegex(ValueError, "duplicate_json_key"):
            preflight(b'{"market":"BTC-PERP","market":"ETH-PERP"}', "BTC-PERP",
                      "2026-11-24T12:02:00Z", "2026-11-24T12:03:00Z")


if __name__ == "__main__":
    unittest.main()
