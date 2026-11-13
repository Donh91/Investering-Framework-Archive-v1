"""Regression and point-in-time tests for Task2 Challenger A (sqrt-time volatility band)."""
import csv
import datetime as dt
import json
import math
import random
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "research"))
import task2_challenger_a_sqrt_t_vol_band_v1 as A  # noqa: E402

PREREG = ROOT / "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/CHALLENGER_A_SQRT_T_VOL_BAND_PREREG_v1.json"
FIELDS = ["timestamp_utc", "btc_close", "btc_high", "btc_low", "eth_close", "eth_high", "eth_low"]


def synthetic_bars(start, hours, seed=7, vol=0.004):
    rnd = random.Random(seed)
    bars, px = {}, {"BTC": 70000.0, "ETH": 2000.0}
    for i in range(hours):
        t = start + i * A.HOUR
        rec = {}
        for asset in ("BTC", "ETH"):
            o = px[asset]
            c = o * math.exp(rnd.gauss(0, vol))
            hi, lo = max(o, c) * (1 + abs(rnd.gauss(0, vol / 3))), min(o, c) * (1 - abs(rnd.gauss(0, vol / 3)))
            rec[asset] = (c, hi, lo)
            px[asset] = c
        bars[t] = rec
    return bars


def write_repo(root, bars):
    days = {}
    for t, r in bars.items():
        days.setdefault(t.date(), []).append((t, r))
    for d, rows in days.items():
        p = root / A.HOURLY_DIR / f"{d:%Y}" / f"{d:%m}" / f"{d:%Y-%m-%d}.csv"
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(FIELDS)
            for t, r in sorted(rows):
                w.writerow([A.iso(t), *r["BTC"], *r["ETH"]])


class ChallengerATest(unittest.TestCase):
    YEAR, WEEK = 2026, 47

    def setUp(self):
        self.monday = A.week_monday(self.YEAR, self.WEEK)
        self.bars = synthetic_bars(self.monday - 70 * A.DAY, 77 * 24)
        self.t0 = self.monday + dt.timedelta(hours=9, minutes=17)

    def test_preregistration_pins_every_parameter(self):
        reg = json.loads(PREREG.read_text(encoding="utf-8"))
        self.assertEqual(reg["contract"], A.CONTRACT)
        self.assertEqual(reg["formula_version"], A.FORMULA_VERSION)
        self.assertEqual(reg["params"], A.PARAMS)
        self.assertEqual(reg["seed_z"], A.SEED_Z)

    def test_band_width_grows_with_sqrt_time(self):
        out = A.issue(self.bars, self.YEAR, self.WEEK, self.t0)
        days = out["assets"]["BTC"]["days"]
        p0 = out["assets"]["BTC"]["P0"]
        for d in days:
            lo, hi = d["band"]["range"]["0.8"]
            z = out["calibration"]["z"]["range"]["0.8"]
            expected = 2 * z * out["assets"]["BTC"]["sigma_hourly"] * math.sqrt(d["h"])
            self.assertAlmostEqual(math.log(hi / lo), expected, delta=1e-4)
        for d in days:  # horizon computed independently: hours from T0 to the end of UTC day k
            end = self.monday + d["day"] * A.DAY
            self.assertAlmostEqual(d["h"], (end - self.t0).total_seconds() / 3600, places=3)
        widths = [math.log(d["band"]["range"]["0.8"][1] / d["band"]["range"]["0.8"][0]) for d in days]
        self.assertEqual(widths, sorted(widths))
        self.assertAlmostEqual(days[-1]["band"]["close"]["0.5"][0] * days[-1]["band"]["close"]["0.5"][1], p0 * p0, delta=p0)

    def test_future_bars_cannot_change_the_issuance(self):
        base = A.issue(self.bars, self.YEAR, self.WEEK, self.t0)["issuance_sha256"]
        tampered = dict(self.bars)
        for t in list(tampered):
            if t + A.HOUR > self.t0:
                c, h, lo = tampered[t]["BTC"]
                tampered[t] = {**tampered[t], "BTC": (c * 0.5, h * 0.5, lo * 0.5)}
        self.assertEqual(A.issue(tampered, self.YEAR, self.WEEK, self.t0)["issuance_sha256"], base)

    def test_calibration_uses_only_the_four_prior_weeks(self):
        cal = A.calibrate(self.bars, self.YEAR, self.WEEK)
        self.assertEqual(cal["source"], "ROLLING_4W")
        self.assertGreaterEqual(cal["rows"], A.PARAMS["calibration_min_rows"])
        older = dict(self.bars)
        cutoff = self.monday - 4 * 7 * A.DAY - 9 * A.DAY  # before the window and before any sigma lookback
        for t in list(older):
            if t < cutoff:
                c, h, lo = older[t]["ETH"]
                older[t] = {**older[t], "ETH": (c * 3, h * 3, lo * 3)}
        self.assertEqual(A.calibrate(older, self.YEAR, self.WEEK)["z"], cal["z"])
        inweek = dict(self.bars)  # bars inside the issue week must never reach the calibration
        for t in list(inweek):
            if t >= self.monday:
                c, h, lo = inweek[t]["BTC"]
                inweek[t] = {**inweek[t], "BTC": (c * 1.9, h * 1.9, lo * 1.9)}
        self.assertEqual(A.calibrate(inweek, self.YEAR, self.WEEK)["z"], cal["z"])

    def test_registered_seed_when_history_is_short(self):
        short = {t: r for t, r in self.bars.items() if t >= self.monday - 9 * A.DAY}
        cal = A.calibrate(short, self.YEAR, self.WEEK)
        self.assertEqual(cal["source"], "REGISTERED_SEED")
        self.assertEqual(cal["z"], A.SEED_Z)

    def test_gap_in_sigma_window_fails_closed(self):
        gap = {t: r for t, r in self.bars.items() if t != self.t0.replace(minute=0) - 30 * A.HOUR}
        with self.assertRaises(ValueError):
            A.sigma_at(gap, "BTC", self.t0)

    def test_issue_clock_must_be_inside_the_week(self):
        with self.assertRaises(ValueError):
            A.issue(self.bars, self.YEAR, self.WEEK, self.monday - A.HOUR)

    def test_interval_score(self):
        self.assertAlmostEqual(A.interval_score(90, 110, 100, 0.2), 20)
        self.assertAlmostEqual(A.interval_score(90, 110, 80, 0.2), 20 + 10 * 10)
        self.assertAlmostEqual(A.interval_score(90, 110, 115, 0.2), 20 + 10 * 5)
        with self.assertRaises(ValueError):
            A.interval_score(110, 90, 100, 0.2)

    def test_score_pairs_cn_and_skips_immature_days(self):
        out = A.issue(self.bars, self.YEAR, self.WEEK, self.t0)
        partial = {t: r for t, r in self.bars.items() if t < self.monday + 3 * A.DAY + 12 * A.HOUR}  # day 4 half-done
        freeze = {"daily_range_plan": {"BTC": {"points": [{"day": k, "low": 1.0, "high": 2.0} for k in range(1, 8)]}}}
        s = A.score(out, partial, freeze)
        self.assertEqual({r["day"] for r in s["rows"]}, {1, 2, 3})
        self.assertEqual(s["paired_rows"], 3)
        self.assertTrue(all(r["CN_range_covered"] == 0 for r in s["rows"] if r["asset"] == "BTC"))
        self.assertEqual(s["week_winner_interval_score"], "A")

    def test_range_containment_uses_the_day_extremes_not_the_close(self):
        day0 = self.monday
        bars = {day0 + i * A.HOUR: {"BTC": (100.0, 100.5, 99.5 if i != 5 else 95.0)} for i in range(24)}
        band = {"range": {q: [99.0, 101.0] for q in ("0.5", "0.8", "0.95")}, "close": {q: [99.0, 101.0] for q in ("0.5", "0.8", "0.95")}}
        iss = {"week": "2026-W47", "issuance_sha256": "x", "assets": {"BTC": {"P0": 100.0, "days": [
            {"day": 1, "scored_from_utc": A.iso(day0), "end_utc": A.iso(day0 + A.DAY), "h": 24.0, "band": band}]}}}
        row = A.score(iss, bars)["rows"][0]
        self.assertEqual(row["A_range_covered"], 0)
        self.assertEqual(row["A_range_0.8_covered"], 0)
        self.assertEqual(row["A_close_0.8_covered"], 1)

    def test_sign_test(self):
        self.assertAlmostEqual(A.sign_test_p(8, 0), 2 / 256)
        self.assertEqual(A.sign_test_p(0, 0), 1.0)
        self.assertAlmostEqual(A.sign_test_p(4, 4), 1.0)

    def test_cli_round_trip_on_synthetic_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_repo(root, self.bars)
            out = root / "o.json"
            self.assertEqual(A.main(["issue", "--repo-root", d, "--week", "2026-W47", "--t0", A.iso(self.t0), "--output", str(out)]), 0)
            j = json.loads(out.read_text())
            self.assertEqual(j["issuance_sha256"], A.issue(A.load_hourly(root, self.monday - 70 * A.DAY, self.monday + 7 * A.DAY), 2026, 47, self.t0)["issuance_sha256"])


class NativeW46Test(unittest.TestCase):
    """Real public bars from this repository (W46 is the pre-registration's out-of-calibration check)."""

    def setUp(self):
        mon = A.week_monday(2026, 46)
        self.bars = A.load_hourly(ROOT, mon - 70 * A.DAY, mon + 7 * A.DAY)
        if len(self.bars) < 24 * 50:
            self.skipTest("hourly capture not present in this checkout")
        fp = ROOT / A.FREEZE_PATH.format(year=2026, week=46)
        self.freeze = json.loads(fp.read_text(encoding="utf-8"))

    def test_w46_issuance_and_score(self):
        out = A.issue(self.bars, 2026, 46, A.utc("2026-11-09T10:33:42Z"))
        self.assertEqual(out["calibration"]["source"], "ROLLING_4W")
        self.assertEqual(out["assets"]["BTC"]["P0"], 74288.01)
        s = A.score(out, self.bars, self.freeze)
        first4 = [r for r in s["rows"] if r["day"] <= 4]
        self.assertEqual(len(first4), 8)
        self.assertEqual(sum(r["CN_range_covered"] for r in first4), 0)
        self.assertEqual(sum(r["A_range_covered"] for r in first4), 8)


if __name__ == "__main__":
    unittest.main()
