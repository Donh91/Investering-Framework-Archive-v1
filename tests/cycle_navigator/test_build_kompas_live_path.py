"""KOMPAS_LIVE_PATH_v1 producer: synthetic fixtures only (no repository data, no network)."""
from __future__ import annotations

import datetime as dt
import io
import json
import math
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest import mock

from scripts.cycle_navigator import build_kompas_live_path as K

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 13, 18, 0, tzinfo=UTC)  # Friday; the 17:00 bar closes at 18:00
WEEK = dt.datetime(2026, 11, 9, tzinfo=UTC)
H = dt.timedelta(hours=1)
HEADER = "timestamp_utc,btc_open,btc_high,btc_low,btc_close,eth_open,eth_high,eth_low,eth_close,spot_status\n"


_X, _S = [0.0], [12345]


def walk(close_time: dt.datetime, base: float) -> float:
    """Deterministic pseudo-random walk (LCG), so sigma is non-trivial and fully reproducible."""
    n = int((close_time - dt.datetime(2026, 10, 1, tzinfo=UTC)) / H)
    while len(_X) <= n:
        seed = (1103515245 * _S[-1] + 12345) % 2 ** 31
        _S.append(seed)
        _X.append(_X[-1] + (seed / 2 ** 31 - 0.5) * 0.008)
    return round(base * math.exp(_X[n]), 2)


class Repo:
    def __init__(self, root: Path):
        self.root = root

    def hourly(self, start: dt.datetime, end: dt.datetime, btc=None, eth=None, skip=()):
        """Bars whose CLOSE time is in (start, end]; btc/eth: f(close_time) -> price."""
        btc = btc or (lambda t: walk(t, 70000.0))
        eth = eth or (lambda t: walk(t, 2000.0) * 1.0001)
        rows: dict[str, list[str]] = {}
        t = start + H
        while t <= end:
            if t not in skip:
                opened = t - H
                b, e = btc(t), eth(t)
                rows.setdefault(opened.strftime("%Y-%m-%d"), []).append(
                    f"{opened:%Y-%m-%dT%H:%M:%SZ},{b},{b * 1.002:.2f},{b * 0.998:.2f},{b},"
                    f"{e},{e * 1.002:.2f},{e * 0.998:.2f},{e},PASS\n")
            t += H
        for day, lines in rows.items():
            p = self.root / K.HOURLY_DIR / day[:4] / day[5:7] / f"{day}.csv"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(HEADER + "".join(lines), encoding="utf-8")

    def packet(self, issued: dt.datetime, b13=(3, 7), b57=(5, 5), d13="DOWN", d57="MIXED",
               semantics=K.PACKET_SEMANTICS, contract=K.PACKET_CONTRACT, name=None):
        def h(v):
            return {"status": "OK", "bull": v[0], "bear": v[1]} if v else {"status": "UNAVAILABLE", "bull": None, "bear": None}
        doc = {"contract": "OFFICIAL_DAILY_COMPASS_v1", "issued_at_utc": issued.strftime("%Y-%m-%dT%H:%M:%SZ"),
               "compass_sha256": f"sha-{issued:%d%H%M}",
               "bull_bear_scale": {"contract": contract, "semantics": semantics,
                                   "horizons": {"1_3d": h(b13), "5_7d": h(b57), "2_3w": h(None)}},
               "horizons": {"NEXT_1_3D": {"expected_direction": d13}, "NEXT_5_7D": {"expected_direction": d57}}}
        p = (self.root / K.PACKET_DIR / f"{issued:%Y}" / f"{issued:%m}" / f"{issued:%d}" /
             (name or f"CMP-{issued:%Y%m%d}-{issued:%H%M%S}.json"))
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding="utf-8")
        return p

    def prereg(self, **over):
        doc = {"contract": K.B_CONTRACT, "formula_version": "B1",
               "params": {"tilt": 0.5, "short_horizon_hours": 72, "packet_contract": K.PACKET_CONTRACT,
                          "packet_semantics": K.PACKET_SEMANTICS, "packet_lookback_hours": 24}}
        doc["params"].update(over.pop("params", {}))
        doc.update(over)
        p = self.root / K.B_PREREG_PATH
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding="utf-8")

    def latest(self, year=2026, week=46, btc=(69000.0, 71000.0), eth=(1900.0, 2100.0)) -> Path:
        doc = {"pointer": {"iso_year": year, "iso_week": week},
               "package": {"forecast_freeze": {"btc_range_low": btc[0], "btc_range_high": btc[1],
                                               "eth_range_low": eth[0], "eth_range_high": eth[1]}}}
        p = self.root / "dist" / "latest.json"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(doc), encoding="utf-8")
        return p


def returns(prices):
    return [math.log(prices[i] / prices[i - 1]) for i in range(1, len(prices))]


class KompasLivePathTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Repo(Path(tmp.name))
        self.repo.hourly(dt.datetime(2026, 10, 13, tzinfo=UTC), NOW)
        self.latest = self.repo.latest()

    def build(self, now=NOW, latest="default"):
        return K.build(self.repo.root, self.latest if latest == "default" else latest, now)

    def closes(self, asset="BTC"):
        doc_series, _ = K.load_hourly(self.repo.root, NOW - 800 * H, NOW)
        return doc_series[asset]

    # ---- the B formula -------------------------------------------------
    def test_tilt_equals_challenger_b_formula_including_after_72h(self):
        self.repo.prereg()
        self.repo.packet(NOW - 2 * H, b13=(3, 7), b57=(8, 2), d57="UP")
        doc = self.build()
        self.assertEqual(doc["status"], "OK")
        bars = self.closes()
        p0 = bars[-1][1]
        rets = returns([c for _, c in bars[-169:]])
        mean = sum(rets) / len(rets)
        # sample std (ddof 1): Challenger A's sigma_hourly definition, B's registered input
        sd = math.sqrt(sum((x - mean) ** 2 for x in rets) / (len(rets) - 1))
        self.assertEqual(K.SIGMA_DDOF, 1)
        g13 = 0.5 * (3 - 7) / 10 * sd * math.sqrt(24)
        g57 = 0.5 * (8 - 2) / 10 * sd * math.sqrt(24)
        a = doc["assets"]["BTC"]
        self.assertAlmostEqual(a["sigma_hourly"], sd, places=9)
        self.assertAlmostEqual(a["drift_per_day"]["g13"], g13, places=9)
        self.assertAlmostEqual(a["drift_per_day"]["g57"], g57, places=9)
        self.assertEqual(len(a["days"]), 8)
        self.assertTrue(any(d["h"] > 72 for d in a["days"]))
        p_up = {x["end_utc"]: x["p_up"] for x in a["challenger_b"]["p_up_by_day"]}
        self.assertEqual(list(p_up), [d["end_utc"] for d in a["days"]])
        for d in a["days"]:
            self.assertNotIn("p_up", d)
            h = (K.utc(d["end_utc"]) - NOW).total_seconds() / 3600
            m = g13 * min(h, 72) / 24 + g57 * max(h - 72, 0) / 24
            centre = p0 * math.exp(m)
            self.assertAlmostEqual(d["h"], h, places=4)
            self.assertAlmostEqual(d["centre"], centre, places=2)
            self.assertAlmostEqual(p_up[d["end_utc"]], 0.5 * (1 + math.erf(m / (sd * math.sqrt(h)) / math.sqrt(2))), places=6)
            w = K.A_SEED_Z_RANGE_50 * sd * math.sqrt(h)
            self.assertAlmostEqual(d["lo"], centre * math.exp(-w), places=2)
            self.assertAlmostEqual(d["hi"], centre * math.exp(w), places=2)
        self.assertEqual(doc["models"]["line"]["line"], "TILTED")
        self.assertEqual(doc["models"]["frames"]["z_source"], "REGISTERED_SEED")
        head = a["headline"]["3"]
        self.assertEqual((head["direction"], head["strength"], head["end_weekday"]), ("DOWN", "moderat", "MON"))
        self.assertEqual(head["end_utc"], "2026-11-17T00:00:00Z")
        # Monday's close is 78 h ahead: 72 h of the 1-3 d drift, then 6 h of the (opposite) 5-7 d drift.
        self.assertAlmostEqual(head["pct"], (math.exp(g13 * 3 + g57 * 6 / 24) - 1) * 100, places=3)
        self.assertEqual(head["tilting_views"], ["1_3d", "5_7d"])
        self.assertEqual(head["balance"], {"horizon": "1_3d", "bull": 3, "bear": 7})
        self.assertEqual(head["target_display"] % 100, 0)
        self.assertEqual(doc["horizon_end_utc"], {"1": "2026-11-15T00:00:00Z", "3": "2026-11-17T00:00:00Z",
                                                  "7": "2026-11-21T00:00:00Z"})

    def test_strength_and_eth_display_rounding(self):
        self.repo.prereg()
        self.repo.packet(NOW - H, b13=(1, 9))
        a = self.build()["assets"]["ETH"]
        self.assertEqual(a["headline"]["1"]["strength"], "tydelig")
        self.assertEqual(a["headline"]["1"]["target_display"] % 10, 0)
        self.assertEqual([K.strength(d) for d in (0, 2, -2, 4, -4, 6, 8, 10)],
                         [None, "svag", "svag", "moderat", "moderat", "tydelig", "tydelig", "tydelig"])

    def test_balanced_5_5_is_flat_and_none(self):
        self.repo.prereg()
        self.repo.packet(NOW - H, b13=(5, 5), b57=(5, 5), d13="MIXED")
        a = self.build()["assets"]["BTC"]
        self.assertTrue(all(d["centre"] == a["p0"] for d in a["days"]))
        self.assertTrue(all(x["p_up"] == 0.5 for x in a["challenger_b"]["p_up_by_day"]))
        for k in ("1", "3", "7"):
            self.assertEqual(a["headline"][k]["direction"], "NONE")
            self.assertEqual(a["headline"][k]["reason"], "BALANCED")

    def test_packets_issued_after_now_or_older_than_24h_are_ignored(self):
        self.repo.prereg()
        self.repo.packet(NOW + 10 * dt.timedelta(minutes=1), b13=(1, 9), name="CMP-future.json")
        self.repo.packet(NOW - 25 * H, b13=(1, 9), name="CMP-old.json")
        kept = self.repo.packet(NOW - 3 * H, b13=(5, 5), d13="MIXED", name="CMP-kept.json")
        doc = self.build()
        self.assertEqual(doc["kompas_views"]["1_3d"]["path"], kept.relative_to(self.repo.root).as_posix())
        self.assertEqual(doc["assets"]["BTC"]["headline"]["3"]["reason"], "BALANCED")
        # selection itself (not only the loader) enforces (now-24h, now]
        future = self.repo.root / K.PACKET_DIR / "2026/11/13/CMP-future.json"
        old = self.repo.root / K.PACKET_DIR / "2026/11/12/CMP-old.json"
        cands = [{"path": p.relative_to(self.repo.root).as_posix(), "sha256": "x", "issued": t, "packet": json.loads(p.read_text())}
                 for p, t in ((future, NOW + 10 * dt.timedelta(minutes=1)), (old, NOW - 25 * H), (kept, NOW - 3 * H))]
        self.assertEqual(K.select_views(cands, NOW)["1_3d"]["bull"], 5)

    def test_older_than_24h_view_is_not_used_when_the_window_has_no_view(self):
        self.repo.prereg()
        self.repo.packet(NOW - 25 * H, b13=(1, 9), name="CMP-old.json")
        self.repo.packet(NOW - 2 * H, b13=None, b57=None, d13="UNAVAILABLE", name="CMP-new.json")
        doc = self.build()
        self.assertIsNone(doc["kompas_views"]["1_3d"])
        self.assertEqual(doc["assets"]["BTC"]["headline"]["3"]["reason"], "NO_VIEW")

    def test_invalid_semantics_or_contract_or_sum_is_ignored(self):
        self.repo.prereg()
        older = self.repo.packet(NOW - 5 * H, b13=(3, 7), name="CMP-a.json")
        self.repo.packet(NOW - 2 * H, b13=(0, 10), semantics="PROBABILITY", name="CMP-b.json")
        self.repo.packet(NOW - 1 * H, b13=(0, 10), contract="OTHER", name="CMP-c.json")
        self.repo.packet(NOW - 30 * dt.timedelta(minutes=1), b13=(2, 7), name="CMP-d.json")  # sums to 9
        doc = self.build()
        self.assertEqual(doc["kompas_views"]["1_3d"]["path"], older.relative_to(self.repo.root).as_posix())
        self.assertEqual(doc["kompas_views"]["1_3d"]["bull"], 3)

    def test_no_valid_packet_in_window_is_unavailable(self):
        self.repo.prereg()
        self.repo.packet(NOW - 30 * H, b13=(3, 7))
        self.repo.packet(NOW - H, semantics="PROBABILITY")
        doc = self.build()
        self.assertEqual(doc["status"], "UNAVAILABLE")
        self.assertEqual(doc["reasons"], ["NO_VALID_OFFICIAL_PACKET_24H"])
        self.assertNotIn("days", doc["assets"]["BTC"])

    def test_valid_packet_without_ok_view_is_no_view_not_outage(self):
        self.repo.prereg()
        self.repo.packet(NOW - H, b13=None, b57=None, d13="UNAVAILABLE")
        a = self.build()["assets"]["BTC"]
        self.assertEqual(a["status"], "OK")
        self.assertEqual(a["headline"]["3"]["reason"], "NO_VIEW")
        self.assertTrue(all(d["centre"] == a["p0"] for d in a["days"]))

    # ---- fail closed ---------------------------------------------------
    def test_stale_hourly_is_unavailable_and_90_minutes_is_fresh(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        later = NOW + dt.timedelta(minutes=91)
        self.repo.packet(later - H, name="CMP-later.json")
        stale = self.build(now=later)
        self.assertEqual(stale["status"], "UNAVAILABLE")
        self.assertEqual(stale["assets"]["BTC"]["reason"], "HOURLY_STALE")
        self.assertNotIn("days", stale["assets"]["BTC"])
        self.assertEqual(self.build(now=NOW + dt.timedelta(minutes=90))["status"], "OK")

    def test_gap_in_sigma_window_is_unavailable(self):
        self.repo.hourly(dt.datetime(2026, 10, 13, tzinfo=UTC), NOW, skip={NOW - 50 * H})
        self.repo.prereg()
        self.repo.packet(NOW - H)
        doc = self.build()
        self.assertEqual(doc["status"], "UNAVAILABLE")
        self.assertEqual({a["reason"] for a in doc["assets"].values()}, {"SIGMA_WINDOW_GAP"})

    def test_prereg_absent_is_flat_with_reason(self):
        self.repo.packet(NOW - H, b13=(1, 9))
        doc = self.build()
        self.assertEqual(doc["status"], "OK")
        line = doc["models"]["line"]
        self.assertEqual((line["applied"], line["line"], line["reason"], line["tilt"]), (False, "FLAT", "PREREG_ABSENT", None))
        a = doc["assets"]["BTC"]
        self.assertTrue(all(d["centre"] == a["p0"] for d in a["days"]))
        self.assertEqual((a["challenger_b"]["applied"], a["challenger_b"]["p_up_by_day"], a["challenger_b"]["reason"]),
                         (False, None, "PREREG_ABSENT"))  # no B, so no B probability at all
        self.assertEqual(a["drift_per_day"], {"g13": 0.0, "g57": 0.0})
        self.assertEqual({h["reason"] for h in a["headline"].values()}, {"PREREG_ABSENT"})
        self.assertIn("ikke registreret", a["events"][0]["text"]["da"])

    def test_prereg_invalid_is_flat(self):
        self.repo.prereg(params={"tilt": "0.5"})
        self.repo.packet(NOW - H, b13=(1, 9))
        doc = self.build()
        self.assertEqual(doc["models"]["line"]["reason"], "PREREG_INVALID")
        self.assertEqual(doc["assets"]["BTC"]["headline"]["3"]["direction"], "NONE")
        self.repo.prereg(params={"packet_lookback_hours": 48})
        self.assertEqual(self.build()["models"]["line"]["reason"], "PREREG_INVALID")

    def test_prereg_tilt_is_read_from_the_file(self):
        self.repo.prereg(params={"tilt": 0.25, "short_horizon_hours": 48})
        self.repo.packet(NOW - H, b13=(3, 7), b57=(5, 5))
        doc = self.build()
        a = doc["assets"]["BTC"]
        self.assertEqual((doc["models"]["line"]["tilt"], doc["models"]["line"]["short_horizon_hours"]), (0.25, 48))
        g13 = 0.25 * (3 - 7) / 10 * a["sigma_hourly"] * math.sqrt(24)
        self.assertAlmostEqual(a["drift_per_day"]["g13"], g13, places=8)
        last = a["days"][-1]
        self.assertAlmostEqual(last["log_shift"], g13 * 48 / 24, places=8)  # flat after 48 h with 5/5

    # ---- frames z --------------------------------------------------------
    def test_frames_use_current_week_challenger_a_issuance_when_parseable(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        p = self.repo.root / K.A_ISSUANCE_PATH.format(year=2026, week=46)
        p.parent.mkdir(parents=True)
        p.write_text(json.dumps({"contract": K.A_CONTRACT, "week": "2026-W46",
                                 "calibration": {"z": {"range": {"0.5": 0.8}}}}), encoding="utf-8")
        doc = self.build()
        frames = doc["models"]["frames"]
        self.assertEqual((frames["z"], frames["z_source"]), (0.8, "CHALLENGER_A_FROZEN_ISSUANCE"))
        d = doc["assets"]["BTC"]["days"][2]
        self.assertAlmostEqual(d["hi"], d["centre"] * math.exp(0.8 * doc["assets"]["BTC"]["sigma_hourly"] * math.sqrt(d["h"])), places=1)
        p.write_text(json.dumps({"contract": K.A_CONTRACT, "week": "2026-W45", "calibration": {"z": {"range": {"0.5": 0.8}}}}))
        frames = self.build()["models"]["frames"]
        self.assertEqual((frames["z"], frames["z_source"], frames["reason"]),
                         (K.A_SEED_Z_RANGE_50, "REGISTERED_SEED", "A_ISSUANCE_UNPARSEABLE"))

    # ---- comment track ---------------------------------------------------
    def zone_repo(self, path):
        """Flat BTC inside the zone [69000, 71000] except where `path` overrides by close time."""
        def btc(t):
            return path.get(t, 70000.0) if t >= WEEK else walk(t, 70000.0)
        self.repo.hourly(dt.datetime(2026, 10, 13, tzinfo=UTC), NOW, btc=btc)

    def test_zone_break_needs_three_consecutive_closes(self):
        t1 = WEEK + 10 * H
        flicker = {t1 + i * H: 68000.0 for i in range(2)}                      # 2 closes below: no event
        t2 = WEEK + 30 * H
        below = {t2 + i * H: 68000.0 for i in range(4)}                        # 4 closes below: one event at t2
        t3 = WEEK + 40 * H
        above = {t3 + i * H: 72000.0 for i in range(3)}                        # 3 closes above: one event at t3
        self.zone_repo({**flicker, **below, **above})
        self.repo.prereg()
        self.repo.packet(NOW - H)
        events = self.build()["assets"]["BTC"]["events"]
        zone = [(e["t_utc"], e["deviation"]["state"]) for e in events if e["kind"] == "ZONE_BREAK"]
        self.assertEqual(zone, [(K.iso(t3 + 3 * H), "INSIDE"), (K.iso(t3), "ABOVE"),
                                (K.iso(t2 + 4 * H), "INSIDE"), (K.iso(t2), "BELOW")])
        below_event = next(e for e in events if e["t_utc"] == K.iso(t2))
        self.assertAlmostEqual(below_event["deviation"]["pct"], (68000 / 69000 - 1) * 100, places=3)
        self.assertIn("3 timer i træk", below_event["text"]["da"])
        self.assertAlmostEqual(below_event["since_pct"], (70000 / 68000 - 1) * 100, places=3)

    def test_zone_break_run_interrupted_by_a_gap_is_not_confirmed(self):
        t2 = WEEK + 30 * H
        below = {t2 + i * H: 68000.0 for i in range(4)}  # 4 closes below, but the 2nd hour is missing
        self.repo.hourly(dt.datetime(2026, 10, 13, tzinfo=UTC), NOW,
                         btc=lambda t: below.get(t, 70000.0) if t >= WEEK else walk(t, 70000.0), skip={t2 + H})
        events = K.comment_events("BTC", self.closes(), WEEK, NOW, {"low": 69000.0, "high": 71000.0, "week": "2026-W46"},
                                  [], {k: {"direction": "NONE", "reason": "PREREG_ABSENT", "end_weekday": "MON",
                                           "official_direction": {}, "pct": 0.0} for k in ("1", "3", "7")}, 70000.0, 0.004)
        self.assertFalse([e for e in events if e["kind"] == "ZONE_BREAK"])

    def test_comment_track_order_kinds_and_fields(self):
        self.zone_repo({WEEK + 30 * H + i * H: 68000.0 for i in range(5)})
        self.repo.prereg()
        self.repo.packet(WEEK - 3 * H, b13=(5, 5), d13="MIXED", name="CMP-pre.json")
        self.repo.packet(WEEK + 12 * H, b13=None, b57=None, d13="UNAVAILABLE", name="CMP-u.json")
        self.repo.packet(WEEK + 13 * H, b13=(3, 7), d13="DOWN", name="CMP-down.json")
        self.repo.packet(WEEK + 20 * H, b13=None, b57=None, d13="UNAVAILABLE", name="CMP-u2.json")
        self.repo.packet(NOW - H, b13=(3, 7), d13="DOWN", name="CMP-now.json")
        events = self.build()["assets"]["BTC"]["events"]
        self.assertEqual(events[0]["kind"], "NOW")
        self.assertEqual(events[-1]["kind"], "WEEK_START")
        times = [e["t_utc"] for e in events]
        self.assertEqual(times, sorted(times, reverse=True))
        changes = [e for e in events if e["kind"] == "KOMPAS_1_3D_CHANGE"]
        self.assertEqual(len(changes), 1)  # UNAVAILABLE packets are not a direction change
        self.assertEqual(changes[0]["text"]["da"], "Kompas 1–3 d skiftede fra Blandet til Faldende.")
        self.assertEqual(changes[0]["text"]["en"], "Compass 1–3 d changed from Mixed to Falling.")
        for e in events:
            self.assertEqual((e["author"], e["ai_text"]), ("AUTOMATIC", None))
            self.assertTrue(e["text"]["da"] and e["text"]["en"])
            self.assertIn(e["deviation"]["state"], {"BELOW", "INSIDE", "ABOVE"})
            self.assertEqual(e["since_pct"] is None, e["kind"] == "NOW")
        self.assertEqual(set(events[0]["text_by_horizon"]), {"1", "3", "7"})
        start = events[-1]
        self.assertEqual(start["t_utc"], "2026-11-09T00:00:00Z")
        self.assertIn("inde i ugens frosne prognose (69.000–71.000)", start["text"]["da"])
        for e in events:
            for text in (e["text"]["da"], e["text"]["en"]):
                self.assertNotIn("Kompas siger", text)
                self.assertNotRegex(text, r"(?i)(?<!ikke )sandsynlighed|(?<!not a )probability")

    def test_now_text_attributes_direction_to_kompas_and_tilt_to_challenger_b(self):
        self.repo.prereg()
        self.repo.packet(NOW - H, b13=(3, 7), d13="DOWN", b57=(4, 6), d57="DOWN")
        now = self.build()["assets"]["BTC"]["events"][0]
        self.assertRegex(now["text"]["da"], r"^Kompas 1–3 d: Faldende · 5–7 d: Faldende\. Challenger B \(forsøg\) hælder derfor kursbanen ned mod ca\. [\d.]+ ved mandagens lukning \(−\d+,\d %\)\.")
        self.assertRegex(now["text_by_horizon"]["7"]["en"], r"^Compass 1–3 d: Falling · 5–7 d: Falling\. Challenger B \(trial\) therefore tilts the path down")
        self.assertRegex(now["text_by_horizon"]["1"]["da"], r"^Kompas 1–3 d: Faldende\. Challenger B")

    def test_frozen_zone_from_another_week_is_not_used(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        doc = self.build(latest=self.repo.latest(week=45))
        self.assertEqual(doc["inputs"]["frozen_zone"]["reason"], "FROZEN_WEEK_NOT_CURRENT")
        a = doc["assets"]["BTC"]
        self.assertIsNone(a["frozen_zone"])
        self.assertEqual({e["deviation"]["state"] for e in a["events"]}, {"NO_ZONE"})
        self.assertFalse([e for e in a["events"] if e["kind"] == "ZONE_BREAK"])

    def test_chips_and_points(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        a = self.build()["assets"]["BTC"]
        bars = dict(self.closes())
        self.assertAlmostEqual(a["chips"]["change_24h_pct"], (a["p0"] / bars[NOW - 24 * H] - 1) * 100, places=3)
        self.assertAlmostEqual(a["chips"]["change_week_pct"], (a["p0"] / bars[WEEK] - 1) * 100, places=3)
        self.assertEqual(a["points"][-1], ["2026-11-13T18:00:00Z", a["p0"]])
        self.assertEqual(K.utc(a["points"][0][0]), NOW - 96 * H)
        self.assertEqual(len(a["points"]), 97)
        self.assertIn(a["daily_move_level"], {"HIGH", "NORMAL", "LOW"})

    def test_p_up_lives_only_under_challenger_b_with_its_own_authority(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        doc = K.seal(self.build())
        paths = []

        def walk_keys(node, path):
            if isinstance(node, dict):
                for k, v in node.items():
                    if k.startswith("p_up"):
                        paths.append(path + (k,))
                    walk_keys(v, path + (k,))
            elif isinstance(node, list):
                for v in node:
                    walk_keys(v, path + ("[]",))
        walk_keys(doc, ())
        self.assertTrue(paths)
        for p in paths:
            self.assertEqual(p[:3], ("assets", p[1], "challenger_b"), p)
        b = doc["assets"]["BTC"]["challenger_b"]
        self.assertEqual(b["authority"], {"research_only": True, "compass_probability_claim": False,
                                          "official_compass": False, "rendered_on_site": False,
                                          "trading": False, "promotion": False})
        self.assertEqual((b["model"], b["status"], b["contract"]), ("Challenger B", "TRIAL", K.B_CONTRACT))
        self.assertIn("NOT_A_KOMPAS_FIELD", b["semantics"])
        self.assertNotIn("p_up", json.dumps(doc["kompas_views"]) + json.dumps(doc["authority"]))

    # ---- contract --------------------------------------------------------
    def test_authority_flags_and_no_private_strings(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        doc = K.seal(self.build())
        self.assertEqual(doc["contract"], "KOMPAS_LIVE_PATH_v1")
        auth = doc["authority"]
        self.assertEqual((auth["research_only"], auth["official_forecast"], auth["compass_probability_claim"],
                          auth["trading"], auth["promotion"], auth["site_synthesis"]),
                         (True, False, False, False, False, False))
        self.assertEqual((auth["line_label"], auth["frames_label"]), ("Challenger B (forsøg)", "Challenger A (forsøg)"))
        text = json.dumps(doc, ensure_ascii=False)
        for word in ("Donh91", "Investering-Framework-Archive-v1", "week_dir", "wallet", str(self.repo.root)):
            self.assertNotIn(word, text)
        self.assertEqual(doc["comment_track"]["ai_text"], None)
        body = {k: v for k, v in doc.items() if k != "path_sha256"}
        self.assertEqual(doc["path_sha256"], K.digest(body))

    def test_deterministic_cli_output_and_always_writes_a_file(self):
        self.repo.prereg()
        self.repo.packet(NOW - H)
        out = self.repo.root / "out" / "kompas-live.json"
        args = ["--repo-root", str(self.repo.root), "--latest-json", str(self.latest), "--output", str(out),
                "--now", "2026-11-13T18:00:00Z"]
        with redirect_stdout(io.StringIO()):
            self.assertEqual(K.main(args), 0)
            first = out.read_bytes()
            self.assertEqual(K.main(args), 0)
        self.assertEqual(first, out.read_bytes())
        self.assertEqual(json.loads(first)["status"], "OK")
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as err, \
                mock.patch.object(K, "build", side_effect=RuntimeError("boom")):
            self.assertEqual(K.main(args), 0)
        failed = json.loads(out.read_text())
        self.assertEqual((failed["status"], failed["reasons"]), ("UNAVAILABLE", ["PRODUCER_ERROR:RuntimeError"]))
        self.assertIn("KOMPAS_LIVE_PRODUCER_ERROR", err.getvalue())
        self.assertNotIn("boom", out.read_text())

    def test_empty_repository_is_unavailable_not_a_crash(self):
        with tempfile.TemporaryDirectory() as empty:
            doc = K.build(Path(empty), None, NOW)
        self.assertEqual(doc["status"], "UNAVAILABLE")
        self.assertEqual(doc["inputs"]["frozen_zone"]["reason"], "LATEST_JSON_ABSENT")
        self.assertEqual(doc["inputs"]["challenger_b_prereg"]["status"], "ABSENT")


if __name__ == "__main__":
    unittest.main()
