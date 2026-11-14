"""Tests for Task2 Challenger B (Kompas evidence-balance tilt). Research only."""
import datetime as dt
import json
import math
import sys
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

    def test_s1_a_reader_and_late_first_main_abstain(self):
        self.assertTrue(callable(A.read_frozen_main_issuance))
        self.assertIsNone(A.verify_issuance_digest(self.a))
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        scored = B.score(b, self.bars, a_issuance_first_main_utc=A.iso(self.t0 + dt.timedelta(hours=3)))
        self.assertEqual(scored["n"], 12)
        self.assertEqual({r["day"] for r in scored["rows"]}, set(range(2, 8)))
        self.assertEqual({r["day"] for r in scored["abstentions"] if r["status"] == "ABSTAIN_PRE_ISSUANCE"}, {1})

    def test_noncanonical_main_ref_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "canonical main"):
            B.git_candidates(ROOT, self.t0, "feature/late-backfill")

    def _weekly(self, winners, matured=True):
        result = []
        for i, winner in enumerate(winners):
            cal = (self.monday + dt.timedelta(days=7*i)).isocalendar()
            result.append({"week": f"{cal.year}-W{cal.week:02d}",
                           "week_winner": winner, "weekly_matured": matured})
        return result

    def test_decision_rule(self):
        self.assertEqual(B.decide(self._weekly(["B"] * 7 + ["BASE"]))["status"], "B_HAS_DIRECTION")
        self.assertEqual(B.decide(self._weekly(["B"] * 6 + ["BASE"] * 2))["status"], "NO_PROVEN_DIRECTION")
        self.assertEqual(B.decide(self._weekly(["TIE"] * 5 + ["B"] * 7))["status"], "PENDING")
        self.assertEqual(B.decide(self._weekly(["B"] + ["BASE"] * 7))["status"], "NO_PROVEN_DIRECTION")
        self.assertEqual(B.decide(self._weekly(["TIE", "B", "B", "B", "B", "B", "B", "B", "BASE"]))["n"], 8)

    def test_duplicate_and_nonprospective_weeks_cannot_win(self):
        one = self._weekly(["B"])[0]
        self.assertEqual(B.decide([one] * 8)["status"], "INCONCLUSIVE_DUPLICATE_WEEK")
        self.assertEqual(B.decide([dict(one, week="2026-W46")] + self._weekly(["B"] * 8))["status"], "INCONCLUSIVE_NONPROSPECTIVE_WEEK")
        self.assertEqual(B.decide(["B"] * 8)["status"], "INCONCLUSIVE_INVALID_WEEK_INPUT")
        self.assertEqual(B.decide([dict(one, week="2026-W99")])["status"], "INCONCLUSIVE_INVALID_WEEK_ID")

    def test_immature_week_cannot_qualify_as_a_win(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        partial = {t:r for t,r in self.bars.items() if t < self.monday + 3 * A.DAY}
        r = B.score(b, partial)
        self.assertFalse(r["weekly_matured"])
        self.assertEqual(r["week_winner"], "PENDING")
        self.assertEqual(B.decide([dict(x, weekly_matured=False) for x in self._weekly(["B"] * 8)])["status"], "PENDING")

    def test_mature_week_with_fewer_than_eight_paired_days_is_missing(self):
        b = B.issue(self.a, B.select_views(self.cands, self.t0))
        # Keep the final hour so the week is complete by clock, but remove the
        # second-to-last source day: missing census must not become a winner.
        partial = {t:r for t,r in self.bars.items()
                   if t < self.monday + 7 * A.DAY and
                   not (self.monday + 2*A.DAY <= t < self.monday + 7*A.DAY - A.HOUR)}
        result = B.score(b, partial)
        self.assertTrue(result["weekly_matured"])
        self.assertLess(result["n"], A.DECISION["min_paired_rows_per_week"])
        self.assertEqual(result["week_winner"], "MISSING")
        self.assertEqual(B.decide([dict(week="2026-W47", weekly_matured=True,
                                        week_winner=result["week_winner"])])["status"], "PENDING")

    def test_forged_b_views_with_self_digest_cannot_be_scored(self):
        proof = {"first_main_commit":"a"*40, "first_main_blob_sha":"b"*40,
                 "issuance_first_main_utc":A.iso(self.t0 + dt.timedelta(hours=3))}
        views = B.select_views(self.cands, self.t0)
        original = B.bind_frozen_a_source(self.a, views, proof)
        B.require_frozen_source_binding(original, self.a, views, proof)
        forged = json.loads(json.dumps(original))
        forged["views"]["1_3d"]["bull"] = 10
        forged["issuance_sha256"] = B._digest({k:v for k,v in forged.items() if k != "issuance_sha256"})
        B.verify_issuance(forged)
        with self.assertRaisesRegex(ValueError, "point-in-time"):
            B.require_frozen_source_binding(forged, self.a, views, proof)

    def test_canonical_packet_missing_from_worktree_refuses_instead_of_flattening(self):
        from unittest.mock import Mock, patch
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            day = self.t0.date()
            rel = (Path(B.PARAMS["packet_dir"]) / f"{day:%Y}" / f"{day:%m}" / f"{day:%d}" / "CMP-valid-but-missing.json").as_posix()
            with patch.object(B.subprocess, "run", return_value=Mock(returncode=0, stdout=rel+"\n")):
                with self.assertRaisesRegex(ValueError, "missing from working tree"):
                    B.git_candidates(root, self.t0, "main")

    def test_unresolved_earlier_week_cannot_be_skipped_by_later_winners(self):
        rows = self._weekly(["BASE", "BASE"] + ["B"] * 7)
        rows[0]["weekly_matured"] = False
        self.assertEqual(B.decide(rows)["status"], "PENDING")
        self.assertEqual(B.decide(rows)["blocked_week"], "2026-W47")
        self.assertEqual(B.decide(rows[1:])["status"], "PENDING")
        rows[0]["weekly_matured"] = True
        self.assertEqual(B.decide(rows)["status"], "NO_PROVEN_DIRECTION")

    def test_modified_original_packet_is_fatal_instead_of_skipped(self):
        from unittest.mock import Mock, patch
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            day = self.t0.date()
            folder = root / B.PARAMS["packet_dir"] / f"{day:%Y}" / f"{day:%m}" / f"{day:%d}"
            folder.mkdir(parents=True)
            (folder/"CMP-corrupt.json").write_text("{}")
            rel=(folder/"CMP-corrupt.json").relative_to(root).as_posix()
            with patch.object(B.subprocess, "run", return_value=Mock(returncode=0, stdout=rel+"\n")):
                with patch.object(B.A, "first_in_main", side_effect=ValueError("original main source path was changed after first issue")):
                    with self.assertRaisesRegex(ValueError, "changed after first issue"):
                        B.git_candidates(root, self.t0, "main")


if __name__ == "__main__":
    unittest.main()
