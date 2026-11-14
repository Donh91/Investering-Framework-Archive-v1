"""Tests for Task2 Challenger B (Kompas evidence-balance tilt). Research only."""
import datetime as dt
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "research"))
sys.path.insert(0, str(ROOT / "tests" / "research"))
import task2_challenger_a_sqrt_t_vol_band_v1 as A  # noqa: E402
import task2_challenger_b_kompas_tilt_v1 as B  # noqa: E402
from test_task2_challenger_a_sqrt_t_vol_band_v1 import synthetic_bars  # noqa: E402

PREREG = ROOT / "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/CHALLENGER_B_KOMPAS_TILT_PREREG_v1.json"


def packet(issued, b13=3, r13=7, b57=5, r57=5, s13="OK", s57="OK", semantics="EVIDENCE_BALANCE_NOT_PROBABILITY"):
    return {"issued_at_utc": issued, "compass_sha256": "x" + issued,
            "bull_bear_scale": {"contract": "OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1", "semantics": semantics,
                                "horizons": {"1_3d": {"status": s13, "bull": b13, "bear": r13},
                                             "5_7d": {"status": s57, "bull": b57, "bear": r57}}}}


class ChallengerBTest(unittest.TestCase):
    def setUp(self):
        self.monday = A.week_monday(2026, 47)
        self.bars = synthetic_bars(self.monday - 70 * A.DAY, 77 * 24)
        self.t0 = self.monday + dt.timedelta(hours=9, minutes=17)
        self.a = A.issue(self.bars, 2026, 47, self.t0)
        self.cands = [{"path": "p1", "packet": packet(A.iso(self.t0 - dt.timedelta(hours=3))), "in_main_utc": self.t0 - dt.timedelta(hours=2)}]

    def test_preregistration_pins_every_parameter(self):
        reg = json.loads(PREREG.read_text(encoding="utf-8"))
        self.assertEqual(reg["contract"], B.CONTRACT)
        self.assertEqual(reg["formula_version"], B.FORMULA_VERSION)
        self.assertEqual(reg["params"], B.PARAMS)
        self.assertEqual(reg["decision_rule"]["confirmatory_week_clusters"], B.DECISION["confirmatory_week_clusters"])
        self.assertEqual(reg["decision_rule"]["one_sided_alpha"], B.DECISION["one_sided_alpha"])

    def test_tilt_formula_matches_the_registration(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        for asset in ("BTC", "ETH"):
            sd, p0 = self.a["assets"][asset]["sigma_hourly"], self.a["assets"][asset]["P0"]
            g13 = 0.5 * (3 - 7) / 10 * sd * math.sqrt(24)
            for d in b["assets"][asset]["days"]:
                h = d["h"]
                m = g13 * min(h, 72) / 24  # 5-7d is 5/5, so no drift after 72 h
                self.assertAlmostEqual(d["centre"], round(p0 * math.exp(m), 2), places=2)
                self.assertAlmostEqual(d["p_up"], 0.5 * (1 + math.erf(m / (sd * math.sqrt(h)) / math.sqrt(2))), places=6)
            day72 = [d for d in b["assets"][asset]["days"] if d["h"] >= 72][0]
            self.assertLess(day72["p_up"], 0.5)
        self.assertAlmostEqual(B.phi(0.5 * -0.4 * math.sqrt(3)), 0.364517, places=5)  # 3/7 at exactly 72 h

    def test_no_view_is_flat_and_a_tie(self):
        flat = [{"path": "p", "packet": packet(A.iso(self.t0 - A.HOUR), b13=5, r13=5), "in_main_utc": self.t0 - A.HOUR}]
        b = B.issue(self.a, B.select_views(flat, self.t0))
        self.assertTrue(all(d["p_up"] == 0.5 for a in b["assets"].values() for d in a["days"]))
        self.assertEqual(B.score(b, self.bars)["week_winner"], "TIE")

    def test_packet_selection_is_point_in_time(self):
        t0 = self.t0
        c = [
            {"path": "old", "packet": packet(A.iso(t0 - dt.timedelta(hours=30))), "in_main_utc": t0 - dt.timedelta(hours=29)},
            {"path": "ok", "packet": packet(A.iso(t0 - dt.timedelta(hours=5)), b13=4, r13=6), "in_main_utc": t0 - dt.timedelta(hours=4)},
            {"path": "late", "packet": packet(A.iso(t0 + A.HOUR), b13=0, r13=10), "in_main_utc": t0 + A.HOUR},
            {"path": "backfill", "packet": packet(A.iso(t0 - A.HOUR), b13=10, r13=0), "in_main_utc": t0 + dt.timedelta(hours=6)},
            {"path": "bad", "packet": packet(A.iso(t0 - dt.timedelta(minutes=10)), b13=1, r13=9, semantics="PROBABILITY"), "in_main_utc": t0},
            {"path": "na", "packet": packet(A.iso(t0 - dt.timedelta(minutes=5)), s13="UNAVAILABLE", b57=2, r57=8), "in_main_utc": t0},
        ]
        v = B.select_views(c, t0)
        self.assertEqual(v["1_3d"]["path"], "ok")  # newer packets are late, backfilled, invalid or unavailable for 1-3d
        self.assertEqual((v["1_3d"]["bull"], v["1_3d"]["bear"]), (4, 6))
        self.assertEqual(v["5_7d"]["path"], "na")  # 5-7d is OK in the newest valid packet
        self.assertIsNone(B.select_views(c[:1], t0)["1_3d"])  # older than 24 h

    def test_scale_must_sum_to_ten(self):
        self.assertIsNone(B.scale_view(packet("2026-11-16T08:00:00Z", b13=3, r13=6), "1_3d"))
        self.assertIsNone(B.scale_view(packet("2026-11-16T08:00:00Z", b13=True, r13=9), "1_3d"))

    def test_b_is_bound_to_a_verified_a_issuance(self):
        bad = json.loads(json.dumps(self.a))
        bad["assets"]["BTC"]["P0"] *= 1.01
        with self.assertRaises(ValueError):
            B.issue(bad, B.select_views(self.cands, self.t0))
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        self.assertEqual(b["a_issuance_sha256"], self.a["issuance_sha256"])
        b2 = json.loads(json.dumps(b))
        b2["assets"]["BTC"]["days"][0]["p_up"] = 0.9
        with self.assertRaises(ValueError):
            B.score(b2, self.bars)

    def _bars_with_path(self, direction):
        bars = {t: r for t, r in self.bars.items() if t + A.HOUR <= self.t0}
        p0 = {k: self.a["assets"][k]["P0"] for k in ("BTC", "ETH")}
        t = max(bars) + A.HOUR
        while t < self.monday + 7 * A.DAY:
            f = math.exp(direction * 0.002 * (t - self.t0).total_seconds() / 3600)
            bars[t] = {k: (p0[k] * f, p0[k] * f * 1.001, p0[k] * f * 0.999) for k in p0}
            t += A.HOUR
        return bars

    def test_score_rewards_the_right_direction(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))  # bearish view
        down, up = B.score(b, self._bars_with_path(-1)), B.score(b, self._bars_with_path(+1))
        self.assertEqual(down["week_winner"], "B")
        self.assertLess(down["mean_brier"], 0.25)
        self.assertEqual(up["week_winner"], "BASE")
        self.assertGreater(up["mean_brier"], 0.25)
        self.assertEqual(down["n"], 14)

    def test_score_skips_immature_and_gapped_days(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        bars = self._bars_with_path(-1)
        cut = {t: r for t, r in bars.items() if t < self.monday + 3 * A.DAY + 5 * A.HOUR}
        self.assertEqual({r["day"] for r in B.score(b, cut)["rows"]}, {1, 2, 3})
        gap = dict(bars)
        del gap[self.monday + A.DAY + 7 * A.HOUR]
        self.assertNotIn(2, {r["day"] for r in B.score(b, gap)["rows"]})
        flat = dict(bars)  # a day that closes exactly at P0 has no direction outcome and is skipped
        last_bar = self.monday + 3 * A.DAY - A.HOUR
        p0 = self.a["assets"]["BTC"]["P0"]
        flat[last_bar] = {**flat[last_bar], "BTC": (p0, p0 * 1.001, p0 * 0.999)}
        rows = B.score(b, flat)["rows"]
        self.assertNotIn(("BTC", 3), {(r["asset"], r["day"]) for r in rows})
        self.assertIn(("ETH", 3), {(r["asset"], r["day"]) for r in rows})

    def test_s1_frozen_a_reader_and_consistent_abstain_denominator(self):
        self.assertTrue(callable(A.read_frozen_main_issuance))
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        a_result = A.score(self.a, self.bars,
                           issuance_first_main_utc=A.iso(self.t0 + dt.timedelta(hours=3)))
        eligible = {(r["asset"], r["day"]) for r in a_result["rows"]}
        scored = B.score(b, self.bars, eligible_days=eligible)
        self.assertEqual(scored["n"], 12)
        self.assertEqual({r["day"] for r in scored["rows"]}, set(range(2, 8)))
        self.assertEqual(len(eligible), scored["n"])

    def test_source_reader_refuses_nonmain_or_noncanonical_hourly_census(self):
        with self.assertRaisesRegex(ValueError, "canonical main ref"):
            B.git_candidates(Path("."), self.t0, "refs/heads/untrusted-pr")
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        bars = dict(self.bars)
        missing = self.monday + A.DAY + 7 * A.HOUR
        shifted = missing + dt.timedelta(minutes=30)
        bars[shifted] = bars.pop(missing)
        self.assertNotIn(2, {r["day"] for r in B.score(b, bars)["rows"]})

    def test_score_refuses_self_hashed_b_with_post_t0_or_rewritten_views(self):
        true_views = B.select_views(self.cands, self.t0)
        genuine = B.issue(self.a, true_views)
        B.verify_against_frozen_sources(genuine, self.a, true_views)
        evil = dict(true_views)
        evil["1_3d"] = {**evil["1_3d"], "bull": 10, "bear": 0}
        tampered = B.issue(self.a, evil)  # new mathematically valid self-computed digest
        with self.assertRaisesRegex(ValueError, "not identical"):
            B.verify_against_frozen_sources(tampered, self.a, true_views)
        forged = json.loads(json.dumps(genuine))
        forged["assets"]["BTC"]["days"][0]["p_up"] = 0.99
        forged["issuance_sha256"] = B._digest({k: v for k, v in forged.items() if k != "issuance_sha256"})
        with self.assertRaisesRegex(ValueError, "not identical"):
            B.verify_against_frozen_sources(forged, self.a, true_views)

    def test_unfinished_week_is_not_a_confirmatory_winner(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        bearish = self._bars_with_path(-1)
        partial = {t: r for t, r in bearish.items() if t < self.monday + A.DAY}
        mid = B.score(b, partial)
        self.assertEqual(mid["week_winner"], "PENDING")
        self.assertFalse(mid["week_mature"])
        self.assertLess(mid["n"], 8)
        self.assertEqual(B.decide(["PENDING"] * 8)["status"], "PENDING")
        full = B.score(b, bearish)
        self.assertTrue(full["week_mature"])
        self.assertEqual(full["week_winner"], "B")

    def test_mutable_worktree_cannot_change_canonical_view_selection(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            def git(*args, env=None):
                subprocess.run(["git", *args], cwd=root, env=env, check=True,
                               capture_output=True, text=True)
            git("init", "-b", "main")
            git("config", "user.name", "B-source-test")
            git("config", "user.email", "test@example.invalid")
            target = root / B.PARAMS["packet_dir"] / "2026" / "11" / "16"
            target.mkdir(parents=True)
            earlier = target / "CMP-earlier.json"
            later = target / "CMP-later.json"
            earlier.write_text(json.dumps(packet(A.iso(self.t0 - 5*A.HOUR), b13=3, r13=7)))
            later.write_text(json.dumps(packet(A.iso(self.t0 - A.HOUR), b13=7, r13=3)))
            git("add", ".")
            env = {**os.environ, "GIT_AUTHOR_DATE": "2026-11-16T07:00:00+00:00",
                   "GIT_COMMITTER_DATE": "2026-11-16T07:00:00+00:00"}
            git("commit", "-m", "canonical Compass packets", env=env)
            first = B.select_views(B.git_candidates(root, self.t0, "refs/heads/main"), self.t0)
            self.assertEqual(first["1_3d"]["bull"], 7)
            later.write_text(json.dumps(packet(A.iso(self.t0-A.HOUR), b13=0, r13=10)))
            earlier.unlink()  # absent working file must not censor a canonical source
            repeated = B.select_views(B.git_candidates(root, self.t0, "refs/heads/main"), self.t0)
            self.assertEqual(repeated, first)
            self.assertEqual(repeated["1_3d"]["bull"], 7)

    def test_decision_rule(self):
        self.assertEqual(B.decide(["B"] * 7 + ["BASE"])["status"], "B_HAS_DIRECTION")
        self.assertEqual(B.decide(["B"] * 6 + ["BASE"] * 2)["status"], "NO_PROVEN_DIRECTION")
        self.assertEqual(B.decide(["TIE"] * 5 + ["B"] * 7)["status"], "PENDING")
        self.assertEqual(B.decide(["B"] + ["BASE"] * 7)["status"], "NO_PROVEN_DIRECTION")
        self.assertEqual(B.decide(["TIE", "B", "B", "B", "B", "B", "B", "B", "BASE"])["n"], 8)


if __name__ == "__main__":
    unittest.main()
