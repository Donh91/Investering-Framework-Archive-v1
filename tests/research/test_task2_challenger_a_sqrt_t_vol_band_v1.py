"""Regression and point-in-time tests for Task2 Challenger A (sqrt-time volatility band)."""
import csv
import datetime as dt
import json
import math
import random
import sys
import os
import subprocess
import copy
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
        self.assertEqual(reg["decision_rule"], A.DECISION)

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

    def test_latest_expected_closed_hour_is_mandatory_even_with_older_history(self):
        t0=self.t0
        expected=(t0-A.HOUR).replace(minute=0,second=0,microsecond=0)
        no_latest={t:r for t,r in self.bars.items() if t<expected}
        self.assertGreater(len(no_latest),169)
        with self.assertRaisesRegex(ValueError,"last expected closed hour"):
            A.sigma_at(no_latest,"BTC",t0)
        with self.assertRaisesRegex(ValueError,"last expected closed hour"):
            A.issue(no_latest,self.YEAR,self.WEEK,t0)
        self.assertEqual(A.sigma_at(self.bars,"BTC",t0)[2],A.iso(expected))

    def test_duplicate_csv_hour_rejected_before_it_can_hide_outlier(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            full_day=self.monday + A.DAY
            bars={t:r for t,r in self.bars.items() if full_day<=t<full_day+A.DAY}
            write_repo(root,bars)
            file=root/A.HOURLY_DIR/f"{full_day:%Y}"/f"{full_day:%m}"/f"{full_day:%Y-%m-%d}.csv"
            with file.open("a",newline="") as fh:
                w=csv.writer(fh)
                r=bars[full_day+5*A.HOUR]
                w.writerow([A.iso(full_day+5*A.HOUR),r["BTC"][0],
                            999999.0,r["BTC"][2],*r["ETH"]])
            with self.assertRaisesRegex(ValueError,"duplicate hourly source timestamp"):
                A.load_hourly(root,full_day,full_day+A.DAY)
            # A malformed first row followed by a repaired same-hour duplicate
            # is also a duplicate, never an accepted source revision.
            fcontents=file.read_text()
            fcontents=fcontents.replace("999999.0","1.0",1)
            file.write_text(fcontents)
            with self.assertRaisesRegex(ValueError,"duplicate hourly"):
                A.load_hourly(root,full_day,full_day+A.DAY)

    def test_offgrid_interior_timestamp_never_counts_as_an_hourly_return(self):
        expected=(self.t0-A.HOUR).replace(minute=0,second=0,microsecond=0)
        interior=expected-30*A.HOUR
        moved=dict(self.bars)
        moved[interior+dt.timedelta(minutes=30)]=moved.pop(interior)
        # Count, total span and last expected bar still appear valid.
        selected=sorted(t for t in moved if t+A.HOUR<=self.t0)[-169:]
        self.assertEqual(len(selected),169)
        self.assertEqual(selected[-1],expected)
        self.assertEqual(selected[-1]-selected[0],168*A.HOUR)
        with self.assertRaisesRegex(ValueError,"exact UTC hourly slots"):
            A.sigma_at(moved,"BTC",self.t0)
        with self.assertRaisesRegex(ValueError,"exact UTC hourly slots"):
            A.issue(moved,self.YEAR,self.WEEK,self.t0)

    def test_offgrid_csv_source_is_not_silently_rounded_to_hour(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            day=self.monday+A.DAY
            bars={t:r for t,r in self.bars.items() if day<=t<day+A.DAY}
            write_repo(root,bars)
            path=root/A.HOURLY_DIR/f"{day:%Y}"/f"{day:%m}"/f"{day:%Y-%m-%d}.csv"
            text=path.read_text()
            expected=A.iso(day+3*A.HOUR)
            offgrid=A.iso(day+3*A.HOUR+dt.timedelta(minutes=30))
            self.assertEqual(text.count(expected),1)
            path.write_text(text.replace(expected,offgrid,1))
            with self.assertRaisesRegex(ValueError,"off-grid hourly source"):
                A.load_hourly(root,day,day+A.DAY)

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
        self.assertEqual(s["week_winner_interval_score"], "MISSING")

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
        self.assertAlmostEqual(A.sign_test_one_sided_p(7, 1), 9 / 256)
        self.assertEqual(A.sign_test_one_sided_p(0, 0), 1.0)
        self.assertAlmostEqual(A.sign_test_one_sided_p(6, 2), 37 / 256)

    def test_gapped_ranges_never_score_or_calibrate(self):
        first=self.monday+10*A.HOUR
        complete={t:r for t,r in self.bars.items() if first<=t<self.monday+A.DAY}
        self.assertEqual(A.realized(complete,"BTC",first,self.monday+A.DAY)["bars"],14)
        gapped=dict(complete)
        del gapped[first+5*A.HOUR]  # still 13 bars, still the final hour: must ABSTAIN
        self.assertIsNone(A.realized(gapped,"BTC",first,self.monday+A.DAY))
        a=A.issue(self.bars,self.YEAR,self.WEEK,self.t0)
        all_gaps=dict(self.bars)
        del all_gaps[first+5*A.HOUR]
        scored=A.score(a,all_gaps)
        self.assertFalse(any(x["day"]==1 and x["asset"]=="BTC" for x in scored["rows"]))
        prior_week=self.monday-A.DAY*7
        cal_gap=dict(self.bars)
        for k in range(7):
            # Make every calibration day fail independently, not a false 80% range hit.
            del cal_gap[prior_week+k*A.DAY+12*A.HOUR]
        before=A.needed_z_rows(self.bars,*(prior_week.isocalendar()[:2]))
        after=A.needed_z_rows(cal_gap,*(prior_week.isocalendar()[:2]))
        self.assertLess(len(after),len(before))

    def test_primary_comparison_uses_identical_paired_denominator(self):
        a=A.issue(self.bars,self.YEAR,self.WEEK,self.t0)
        f={"daily_range_plan":{"BTC":{"points":[{"day":k,"low":1.0,"high":2.0} for k in range(1,8)]}}}
        scored=A.score(a,self.bars,f)
        self.assertEqual(scored["paired_rows"],7)
        self.assertEqual(scored["aggregate_primary_paired"]["A_interval_score"]["n"],7)
        self.assertEqual(scored["aggregate_primary_paired"]["CN_interval_score"]["n"],7)
        self.assertEqual(scored["aggregate_challenger_all"]["A_interval_score"]["n"],14)
        self.assertNotIn("CN_interval_score",scored["aggregate_challenger_all"])

    def test_equal_width_prior_control_is_source_issued_not_posthoc(self):
        a=A.issue(self.bars,self.YEAR,self.WEEK,self.t0)
        original=a["assets"]["BTC"]["prior_week_close"]
        self.assertGreater(original,0)
        f={"daily_range_plan":{"BTC":{"points":[{"day":k,"low":100.0,"high":200.0} for k in range(1,8)]}}}
        scored=A.score(a,self.bars,f)
        b=[x for x in scored["rows"] if x["asset"]=="BTC"]
        self.assertEqual(scored["aggregate_primary_paired"]["EQW_PRIOR_width"]["n"],7)
        self.assertAlmostEqual(b[0]["EQW_PRIOR_width"],b[0]["CN_width"])
        # Erasing the originally issued prior close removes the control, it may
        # NOT substitute the observed future close or newly queried bars.
        missing=copy.deepcopy(a)
        missing["assets"]["BTC"]["prior_week_close"]=None
        s=A.score(missing,self.bars,f)
        self.assertFalse(any("EQW_PRIOR_interval_score" in x for x in s["rows"] if x["asset"]=="BTC"))

    def _confirmatory_rows(self, n=9):
        return [{"week": f"{(self.monday+k*7*A.DAY).isocalendar().year}-W{(self.monday+k*7*A.DAY).isocalendar().week:02d}",
                 "week_winner_interval_score": "A", "paired_rows": 8, "matured_rows": 8}
                for k in range(n)]

    def test_confirmatory_seven_of_eight_one_sided_passes(self):
        rows = self._confirmatory_rows()
        rows[7]["week_winner_interval_score"] = "CN"
        self.assertEqual(A.confirmatory_decision(rows[:7])["status"], "PENDING")
        decision = A.confirmatory_decision(rows)
        self.assertEqual(decision["status"], "A_PASSES_SHADOW_CONFIRMATORY")
        self.assertEqual(decision["weeks"], [r["week"] for r in rows[:8]])
        self.assertAlmostEqual(decision["one_sided_p"], 9/256)
        self.assertFalse(decision["promotion_allowed"])

    def test_confirmatory_six_of_eight_does_not_pass(self):
        rows = self._confirmatory_rows(8)
        for row in rows[-2:]:
            row["week_winner_interval_score"] = "CN"
        decision = A.confirmatory_decision(rows)
        self.assertEqual(decision["wins_A"], 6)
        self.assertEqual(decision["status"], "A_NOT_PROVEN")
        self.assertAlmostEqual(decision["one_sided_p"], 37/256)

    def test_confirmatory_opposite_sign_cannot_pass(self):
        rows = self._confirmatory_rows(8)
        for row in rows[1:]:
            row["week_winner_interval_score"] = "CN"
        decision = A.confirmatory_decision(rows)
        self.assertEqual(decision["wins_A"], 1)
        self.assertEqual(decision["status"], "A_NOT_PROVEN")

    def test_missing_and_tied_weeks_skipped_then_ninth_and_tenth_complete(self):
        rows = self._confirmatory_rows(10)
        rows[2]["paired_rows"] = 7
        rows[4]["week_winner_interval_score"] = "TIE"
        self.assertEqual(A.confirmatory_decision(rows[:9])["status"], "PENDING")
        decision = A.confirmatory_decision(rows)
        self.assertEqual(decision["status"], "A_PASSES_SHADOW_CONFIRMATORY")
        self.assertEqual(decision["weeks"], [r["week"] for r in rows if r not in (rows[2],rows[4])][:8])
        # The original first valid eight are immutable even if later outcomes lose.
        rows += [{**rows[-1], "week": "2027-W12", "week_winner_interval_score": "CN"}]
        self.assertEqual(A.confirmatory_decision(rows)["weeks"], decision["weeks"])

    def test_duplicate_week_fails_closed(self):
        rows = self._confirmatory_rows(8)
        self.assertEqual(A.confirmatory_decision(rows + [dict(rows[0])])["status"],
                         "INCONCLUSIVE_DUPLICATE_WEEK")

    def test_late_issuance_abstains_day_one_but_scores_days_two_to_seven(self):
        issue = A.issue(self.bars,self.YEAR,self.WEEK,self.t0)
        freeze = {"daily_range_plan": {a: {"points": [
            {"day": k, "low": 1.0, "high": 2.0} for k in range(1,8)]}
            for a in ("BTC","ETH")}}
        scored = A.score(issue,self.bars,freeze,
                         issuance_first_main_utc=A.iso(self.t0+dt.timedelta(hours=3)))
        self.assertEqual(scored["paired_rows"],12)
        self.assertEqual(scored["matured_rows"],12)
        self.assertEqual({r["day"] for r in scored["rows"]},set(range(2,8)))
        self.assertEqual(len(scored["abstentions"]),2)
        self.assertEqual({x["status"] for x in scored["abstentions"]},
                         {"ABSTAIN_PRE_ISSUANCE"})

    def test_post_week_issuance_makes_week_missing(self):
        issue = A.issue(self.bars,self.YEAR,self.WEEK,self.t0)
        scored = A.score(issue,self.bars,
                         issuance_first_main_utc=A.iso(self.monday+8*A.DAY))
        self.assertEqual(scored["matured_rows"],0)
        self.assertEqual(scored["paired_rows"],0)
        self.assertEqual(scored["week_winner_interval_score"],"MISSING")
        self.assertEqual(len(scored["abstentions"]),14)
        self.assertEqual(A.confirmatory_decision([scored])["status"],"PENDING")

    def test_decision_pre_registration_is_exact_code_constant(self):
        reg = json.loads(PREREG.read_text(encoding="utf-8"))
        self.assertEqual(reg["decision_rule"],A.DECISION)
        self.assertEqual(A.DECISION["confirmatory_valid_weeks"],8)
        self.assertEqual(A.DECISION["min_paired_rows_per_week"],8)
        self.assertEqual(A.DECISION["first_week"],"2026-W47")
        self.assertEqual(A.DECISION["one_sided_alpha"],0.05)

    @staticmethod
    def _git(root,*args,date=None):
        env=os.environ.copy()
        if date:
            env.update({"GIT_AUTHOR_DATE":date,"GIT_COMMITTER_DATE":date})
        return subprocess.run(["git","-C",str(root),*args],
                              capture_output=True,text=True,check=True,env=env).stdout.strip()

    def test_first_main_history_and_persisted_issuance_integrity(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self._git(root,"init","-b","main")
            self._git(root,"config","user.name","Task2 CI")
            self._git(root,"config","user.email","task2-tests@example.invalid")
            (root/"README").write_text("source fixture\n")
            self._git(root,"add","README")
            self._git(root,"commit","-m","init",date="2026-11-15T00:00:00+00:00")
            self._git(root,"checkout","-b","draft")
            freeze_rel=A.FREEZE_PATH.format(year=self.YEAR,week=self.WEEK)
            freeze_path=root/freeze_rel
            freeze_path.parent.mkdir(parents=True,exist_ok=True)
            freeze_path.write_text('{"daily_range_plan":{}}\n')
            self._git(root,"add",freeze_rel)
            self._git(root,"commit","-m","branch source not yet in main",date="2026-11-16T08:00:00+00:00")
            with self.assertRaises(ValueError):
                A.first_in_main(root,freeze_rel)
            self._git(root,"checkout","main")
            freeze_path.parent.mkdir(parents=True,exist_ok=True)
            freeze_path.write_text('{"daily_range_plan":{}}\n')
            self._git(root,"add",freeze_rel)
            self._git(root,"commit","-m","actual main freeze",date="2026-11-16T09:17:00+00:00")
            info=A.first_in_main(root,freeze_rel)
            self.assertEqual(info["first_main_utc"],"2026-11-16T09:17:00Z")
            self.assertNotEqual(info["first_main_commit"],self._git(root,"rev-parse","draft"))
            self.assertEqual(A.t0_from_git(root,self.YEAR,self.WEEK),self.t0)
            provenance={"clock_class":info["clock_class"],"freeze_first_main_commit":info["first_main_commit"],
                        "freeze_blob_sha":info["first_main_blob_sha"],"freeze_first_main_utc":info["first_main_utc"],
                        "first_http_delivery":"UNKNOWN"}
            issued=A.issue(self.bars,self.YEAR,self.WEEK,self.t0,provenance)
            issue_rel=A.ISSUANCE_PATH.format(year=self.YEAR,week=self.WEEK)
            fp=root/issue_rel
            fp.parent.mkdir(parents=True,exist_ok=True)
            fp.write_text(json.dumps(issued,sort_keys=True)+"\n")
            with self.assertRaises(ValueError):
                A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)
            self._git(root,"add",issue_rel)
            self._git(root,"commit","-m","immutable issue first in main",date="2026-11-16T09:30:00+00:00")
            read,proof=A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)
            self.assertEqual(read["issuance_sha256"],issued["issuance_sha256"])
            self.assertEqual(proof["first_main_utc"],"2026-11-16T09:30:00Z")
            fp.write_text(json.dumps({**issued,"week":"2099-W47"})+"\n")
            with self.assertRaises(ValueError):
                A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)
            fp.write_text(json.dumps(issued,sort_keys=True)+"\n")
            # Original first-main bytes remain equal without introducing a new commit.
            self.assertEqual(A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)[0]["week"],"2026-W47")
            freeze_path.write_text('{"daily_range_plan":{"BTC":{}}}\n')
            with self.assertRaises(ValueError):
                A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)
            # Even a later revert to identical bytes is a real revision of
            # an immutable first-main original. Reject it, never relabel.
            self._git(root,"add",freeze_rel)
            self._git(root,"commit","-m","illicit original freeze edit",date="2026-11-16T09:45:00+00:00")
            freeze_path.write_text('{"daily_range_plan":{}}\n')
            self._git(root,"add",freeze_rel)
            self._git(root,"commit","-m","restored original after edit",date="2026-11-16T09:50:00+00:00")
            with self.assertRaises(ValueError):
                A.read_frozen_main_issuance(root,self.YEAR,self.WEEK)

    def test_prospective_source_must_reach_main_before_first_outcome(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            self._git(root,"init","-b","main")
            self._git(root,"config","user.name","Task2 CI")
            self._git(root,"config","user.email","task2-tests@example.invalid")
            rel=A.FREEZE_PATH.format(year=2026,week=47)
            freeze=root/rel
            freeze.parent.mkdir(parents=True,exist_ok=True)
            freeze.write_text("{}\n")
            self._git(root,"add",rel)
            self._git(root,"commit","-m","freeze",date="2026-11-16T09:17:00+00:00")
            info=A.first_in_main(root,rel)
            issued=A.issue(self.bars,2026,47,self.t0,{
                "clock_class":info["clock_class"],"freeze_first_main_commit":info["first_main_commit"],
                "freeze_blob_sha":info["first_main_blob_sha"],"freeze_first_main_utc":info["first_main_utc"]})
            rel=A.ISSUANCE_PATH.format(year=2026,week=47)
            fp=root/rel
            fp.parent.mkdir(parents=True,exist_ok=True)
            fp.write_text(json.dumps(issued,sort_keys=True)+"\n")
            self._git(root,"add",rel)
            self._git(root,"commit","-m","published after day1 started",date="2026-11-16T11:30:00+00:00")
            saved, proof = A.read_frozen_main_issuance(root,2026,47)
            self.assertEqual(proof["issuance_first_main_utc"],"2026-11-16T11:30:00Z")
            self.assertEqual(saved["issuance_sha256"],issued["issuance_sha256"])
            scored = A.score(saved,self.bars,issuance_first_main_utc=proof["issuance_first_main_utc"])
            self.assertEqual({r["day"] for r in scored["abstentions"]},{1})
            self.assertEqual(scored["matured_rows"],12)

    def test_existing_cn_weekly_writer_issues_only_original_main_shadow_source(self):
        workflow = (ROOT / ".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
        step_name = "Publish optional immutable Challenger A SHADOW issue after original CN main readback"
        self.assertEqual(workflow.count(step_name), 1)
        self.assertEqual(workflow.count("cron: '5 9 * * 1'"), 1)
        start = workflow.index("      - name: " + step_name)
        end = workflow.index("      - name: Refresh Official Compass from newly published weekly CN", start)
        source_readback = workflow.index("      - name: Durable readback of complete Cycle Navigator package")
        self.assertLess(source_readback, start)
        self.assertLess(start, end)
        step = workflow[start:end]
        self.assertIn("continue-on-error: true", step)
        self.assertIn("if: steps.precheck.outputs.skip != 'true'", step)
        self.assertIn("CHALLENGER_ISSUE_OUTSIDE_ORIGINAL_MONDAY_NO_BACKFILL", step)
        self.assertIn("git cat-file -e \"origin/main:${ISSUE_REL}\"", step)
        self.assertIn("CHALLENGER_A_ALREADY_ON_MAIN_NOOP", step)
        self.assertIn("CHALLENGER_A_LOCAL_UNATTESTED_FILE_NO_OVERWRITE", step)
        self.assertIn("scripts/research/task2_challenger_a_sqrt_t_vol_band_v1.py issue", step)
        self.assertIn('--week "${ISO_WEEK}" --output "${ISSUE_REL}"', step)
        self.assertNotIn("--t0", step)
        self.assertNotIn("--synthetic-fixture-clock", step)
        self.assertNotIn("OPENAI_API_KEY", step)
        self.assertIn("git add -- \"${ISSUE_REL}\"", step)
        self.assertIn("git pull --rebase origin main && git push origin HEAD:main", step)
        self.assertIn("read_frozen_main_issuance(Path('.'),y,w)", step)
        self.assertIn("local!=remote", step)
        self.assertIn("CHALLENGER_A_FIRST_MAIN_ISSUE_SOURCE_READBACK_PASS", step)
        # No failure of this advisory research lane can block existing
        # official CN publication or final Official Compass handoff.

    def test_late_hourly_capture_requires_pre_t0_bar_then_abstains_day_one(self):
        expected=(self.t0-A.HOUR).replace(minute=0,second=0,microsecond=0)
        incomplete={t:r for t,r in self.bars.items() if t!=expected}
        with self.assertRaisesRegex(ValueError,"last expected closed hour"):
            A.issue(incomplete,self.YEAR,self.WEEK,self.t0)
        late=dict(incomplete)
        late[expected]=self.bars[expected]
        issued=A.issue(late,self.YEAR,self.WEEK,self.t0)
        scored=A.score(issued,self.bars,issuance_first_main_utc=A.iso(self.t0+dt.timedelta(hours=3)))
        self.assertEqual(scored["matured_rows"],12)
        self.assertEqual({r["day"] for r in scored["rows"]},set(range(2,8)))
        self.assertEqual({r["day"] for r in scored["abstentions"]},{1})
        self.assertEqual({r["status"] for r in scored["abstentions"]},{"ABSTAIN_PRE_ISSUANCE"})

    def test_hourly_catchup_is_monday_only_and_source_gated(self):
        weekly=(ROOT/".github/workflows/cycle-navigator-weekly-publication.yml").read_text()
        hourly=(ROOT/".github/workflows/hourly-sequence-capture.yml").read_text()
        step_name="Catch up immutable Challenger A SHADOW after hourly main readback"
        self.assertEqual(hourly.count(step_name),1)
        start=hourly.index("      - name: "+step_name)
        end=hourly.index("      - name: Preflight actual newly completed owner hour",start)
        self.assertLess(hourly.index("      - name: Commit compact hourly sequence with verified readback"),start)
        step=hourly[start:end]
        for guard in ("continue-on-error: true","git pull --ff-only origin main",
                      "CHALLENGER_ISSUE_OUTSIDE_ORIGINAL_MONDAY_NO_BACKFILL",
                      "CHALLENGER_A_NOT_MONDAY_NOOP",
                      "CHALLENGER_ISSUE_NO_ORIGINAL_CN_FREEZE",
                      "CHALLENGER_A_ALREADY_ON_MAIN_NOOP",
                      "git cat-file -e \"origin/main:${ISSUE_REL}\"",
                      "read_frozen_main_issuance(Path('.'),y,w)",
                      "CHALLENGER_A_FIRST_MAIN_ISSUE_SOURCE_READBACK_PASS"):
            self.assertIn(guard,step)
        self.assertNotIn("steps.precheck.outputs.skip",step)
        self.assertNotIn("--synthetic-fixture-clock",step)
        self.assertNotIn("--t0",step)
        self.assertNotIn("OPENAI_API_KEY",step)
        self.assertIn("git pull --ff-only origin main",weekly)
        self.assertEqual(hourly.count("cron: '12 * * * *'"),1)
        self.assertEqual(weekly.count("cron: '5 9 * * 1'"),1)

    def test_cli_round_trip_on_synthetic_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            write_repo(root, self.bars)
            out = root / "o.json"
            self.assertEqual(A.main(["issue", "--repo-root", d, "--week", "2026-W47", "--t0", A.iso(self.t0), "--synthetic-fixture-clock", "--output", str(out)]), 0)
            j = json.loads(out.read_text())
            expected=A.issue(A.load_hourly(root, self.monday - 70 * A.DAY, self.monday + 7 * A.DAY), 2026, 47, self.t0, {"clock_class":"SYNTHETIC_FIXTURE_ONLY"})
            self.assertEqual(j["issuance_sha256"], expected["issuance_sha256"])
            self.assertEqual(j["source"]["clock_class"], "SYNTHETIC_FIXTURE_ONLY")
            with self.assertRaises(ValueError):
                A.main(["score", "--repo-root", d, "--week", "2026-W47", "--t0", A.iso(self.t0), "--output", str(root/"score.json")])


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
        # W46 is selection-exposed; incomplete source days are now ABSTAIN.
        self.assertLessEqual(len(first4), 8)
        self.assertTrue(all(r["bars"] >= 6 for r in first4))
        for r in first4:
            day=int(r["day"])
            monday=A.week_monday(2026,46)
            start=max(monday+(day-1)*A.DAY,
                      A.utc("2026-11-09T10:33:42Z").replace(minute=0,second=0,microsecond=0)+A.HOUR)
            expected=int(((monday+day*A.DAY)-start).total_seconds()/3600)
            self.assertEqual(r["bars"],expected)
        self.assertTrue(all(r["CN_range_covered"]==0 for r in first4))


if __name__ == "__main__":
    unittest.main()
