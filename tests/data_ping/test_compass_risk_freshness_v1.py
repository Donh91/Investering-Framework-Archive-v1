"""AUDIT-04b: source_freshness, cn_band_status (forecast_floor_status) and risk_freshness.

The fixtures are REAL bytes: the issued W47 official packets, the owner packets they are bound to, the W44-W48
weekly machine packages and the hourly daily CSVs. They are copied into a throwaway Git repository so the
production reader runs against real Git; `git hash-object` is the independent blob oracle. Only the snapshot
commit id is re-bound (a test repository cannot contain the production commit).
"""
import csv
import hashlib
import io
import json
import subprocess
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from scripts.data_ping import compass_release_receipt_v1 as receipt
from scripts.data_ping import native_handlekompas as nh
from scripts.learning import action_compass_exit_calibration as exit_calibration

REPO = Path(__file__).resolve().parents[2]
UTC = timezone.utc
OFFICIAL = "04_MARKET_LEARNING/handlekompas/official"
# Issued 2026-11-22T00:26:11Z with data_status OK, one day after the W47 weekly floor broke on a completed close.
REAL_BREACH = f"{OFFICIAL}/daily/2026/11/22/CMP-20261122-f6f301fb5d2c.json"
WEEK_START = datetime(2026, 11, 16, tzinfo=UTC)          # 2026-W47, issue 35
BTC_FLOOR, ETH_FLOOR = 61770.42, 1687.16                  # frozen weekly floors of issue 35
BTC_DAY = {1: 63802.55, 2: 63133.65, 3: 63449.13, 4: 62891.71, 5: 63803.6, 6: 64454.88, 7: 64055.43}
NEW_KEYS = {"source_freshness", "cn_band_status", "risk_freshness"}
IDENTITY = {"schema_version", "compass_id", "compass_sha256", "bound_main_sha"}
GIT = ["git", "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgsign=false"]


def stamp(value):
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def real_json(rel):
    return json.loads((REPO / rel).read_text())


def csv_rel(day):
    return f"03_DAILY_CAPTURE_LOGS/hourly/{day:%Y/%m/%Y-%m-%d}.csv"


def week_rel(week):
    return f"05_CYCLE_NAVIGATOR/weekly/2026/{week}"


class Sandbox:
    """A real Git repository holding real fixture bytes."""

    def __init__(self, tmp):
        self.root = Path(tmp)
        subprocess.check_call(GIT + ["init", "-q", str(self.root)])

    def write(self, rel, data):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def commit(self):
        subprocess.check_call(GIT + ["add", "-A"], cwd=self.root)
        subprocess.check_call(GIT + ["commit", "-q", "--allow-empty", "-m", "fixture"], cwd=self.root)
        return subprocess.check_output(GIT + ["rev-parse", "HEAD"], cwd=self.root, text=True).strip()

    def hash_object(self, rel):
        """Independent oracle: Git itself hashes the file. Not the producer's SHA-1 and not rev-parse."""
        return subprocess.check_output(GIT + ["hash-object", str(self.root / rel)], text=True).strip()

    def add_weeks(self, weeks=("W44", "W45", "W46", "W47"), edit=None):
        for week in weeks:
            raw = (REPO / week_rel(week) / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes()
            pointer = real_json(f"{week_rel(week)}/CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
            if edit and week in edit:
                package = json.loads(raw)
                edit[week](package)
                raw = json.dumps(package, sort_keys=True).encode()
                pointer["machine_package_sha256"] = hashlib.sha256(raw).hexdigest()
            self.write(f"{week_rel(week)}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json", raw)
            self.write(f"{week_rel(week)}/CYCLE_NAVIGATOR_DELIVERY_POINTER.json", json.dumps(pointer).encode())

    def add_hourly(self, bar, *, override=None, drop=(), first_day=WEEK_START, extra_rows=None):
        """Real rows up to the bound bar: what Git held when the owner packet was built."""
        day = first_day
        while day <= bar:
            lines = (REPO / csv_rel(day)).read_bytes().splitlines(keepends=True)
            fields = lines[0].decode("utf-8-sig").strip().split(",")
            ending = lines[0][len(lines[0].rstrip(b"\r\n")):]
            out = [lines[0]]
            for line in lines[1:]:
                label = line.split(b",", 1)[0].decode()
                if datetime.fromisoformat(label.replace("Z", "+00:00")) > bar or label in drop:
                    continue
                edits = [(override or {}).get(label)] + list((extra_rows or {}).get(label, []))
                if edits[0] is None:
                    out.append(line)                       # an untouched production row stays byte-identical
                row = dict(zip(fields, line.decode().strip().split(",")))
                for index, edit in enumerate(edits):
                    if edit is not None:
                        out.append(",".join({**row, **(edits[0] or {}), **edit}[f] for f in fields).encode() + ending)
                    elif index:
                        raise AssertionError("unreachable")
            self.write(csv_rel(day), b"".join(out))
            day += timedelta(days=1)

    def close_at(self, bar):
        rows = list(csv.DictReader(io.StringIO((self.root / csv_rel(bar)).read_text())))
        row = [r for r in rows if r["timestamp_utc"] == stamp(bar)][-1]
        return float(row["btc_close"]), float(row["eth_close"])


def bound_auto(box, commit, bar, *, available=None, template=None):
    """The real healthy owner packet, re-bound to the fixture commit and (when the bar moves) to that bar."""
    auto = rebind(template or real_json(real_json(REAL_BREACH)["source_bindings"]["auto_market_state"]["packet_path"]), commit)
    available = available or bar + timedelta(hours=1, minutes=23, seconds=33)
    btc, eth = box.close_at(bar)
    auto["packet_generated_at_utc"] = stamp(available)
    auto["normalized_state"]["live_market"].update({"observation_open_utc": stamp(bar), "btc_usdt": btc, "eth_usdt": eth})
    lane = auto["source_health"]["hourly_market"]
    lane["row"]["timestamp_utc"] = stamp(bar)
    lane["row"]["provenance"].update({
        "exact_commit_sha": commit, "exact_path": csv_rel(bar), "git_blob_sha": box.hash_object(csv_rel(bar)),
    })
    fresh = lane["freshness"]
    for key in ("pointer_freshness", "retrieval_freshness"):
        fresh[key]["timestamp"] = stamp(available - timedelta(minutes=11))
    for key in ("session_coverage_freshness", "source_observation_freshness"):
        fresh[key]["timestamp"] = stamp(bar + timedelta(hours=1))
    return auto


def rebind(template, commit):
    """Every provenance entry of the real owner packet names one production commit; move them all to the fixture's."""
    production = template["source_snapshot"]["exact_commit_sha"]
    return json.loads(json.dumps(template).replace(production, commit))


def binding_for(box, week="W47", issue=35, iso_week=47):
    raw = (box.root / week_rel(week) / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes()
    return json.loads(raw), {
        "status": "PASS", "issue_number": issue, "iso_week": iso_week, "iso_year": 2026,
        "decision_projection_source": "MACHINE_PACKAGE",
        "machine_package": {"path": f"{week_rel(week)}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",
                            "content_sha256": hashlib.sha256(raw).hexdigest(), "git_blob_sha": None},
    }


class Case:
    """One issuance: real W47 forecast, real rows up to `bar`, optional edits."""

    def __init__(self, tmp, *, bar, as_of=None, available=None, override=None, drop=(), extra_rows=None,
                 week_edit=None, auto_edit=None, weeks=("W44", "W45", "W46", "W47")):
        self.box = Sandbox(tmp)
        self.box.add_weeks(weeks, edit=week_edit)
        self.box.add_hourly(bar, override=override, drop=drop, extra_rows=extra_rows)
        self.commit = self.box.commit()
        self.auto = bound_auto(self.box, self.commit, bar, available=available)
        self.as_of = as_of or _parse(self.auto["packet_generated_at_utc"]) + timedelta(minutes=3)
        if auto_edit:
            auto_edit(self.auto)
        self.cn, self.binding = binding_for(self.box)

    def build(self, *, run_reason="EVENT_DRIVEN", **kwargs):
        return nh.build_official_compass(
            self.auto, packet_path=Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs/fixture.json"),
            cn_package=kwargs.pop("cn", self.cn), cn_binding=kwargs.pop("binding", self.binding),
            repo_root=self.box.root, issued_at=self.as_of, run_reason=run_reason, **kwargs)


def _parse(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def at(day, hour=23):
    """Candle open on forecast day 1..7 (8 = the Monday after)."""
    return WEEK_START + timedelta(days=day - 1, hours=hour)


def close(day, btc=None, eth=None):
    """Override the completed daily close (the 23:00 UTC candle) of a forecast day."""
    values = {}
    if btc is not None:
        values["btc_close"] = repr(float(btc))
    if eth is not None:
        values["eth_close"] = repr(float(eth))
    return {stamp(at(day)): values}


# Closes that keep every completed day above both the weekly and that day's own floor.
SAFE = {}
for _day in range(1, 8):
    SAFE.update(close(_day, btc=66000.0 + _day, eth=1850.0 + _day))


def merged(*overrides):
    out = {label: dict(values) for label, values in SAFE.items()}
    for item in overrides:
        for label, values in item.items():
            out[label] = {**out.get(label, {}), **values}
    return out


class RealW47PacketTest(unittest.TestCase):
    """Fail-before / pass-after on the packets that were actually issued."""

    def real_case(self, tmp, rel):
        real = real_json(rel)
        template = real_json(real["source_bindings"]["auto_market_state"]["packet_path"])
        bar = _parse(template["normalized_state"]["live_market"]["observation_open_utc"])
        box = Sandbox(tmp)
        box.add_weeks()
        box.add_hourly(bar)
        commit = box.commit()
        auto = rebind(template, commit)
        recorded_blob = auto["source_health"]["hourly_market"]["row"]["provenance"]["git_blob_sha"]
        if bar.hour == 23:
            # A complete day: the fixture file is byte-identical to production, proven by Git's own hash.
            self.assertEqual(box.hash_object(csv_rel(bar)), recorded_blob)
        else:
            auto["source_health"]["hourly_market"]["row"]["provenance"]["git_blob_sha"] = box.hash_object(csv_rel(bar))
        day_dirs = sorted({Path(rel).parent, Path(rel).parent.parent / f"{int(Path(rel).parent.name) - 1:02d}"})
        earlier = [c for d in day_dirs for c in map(real_json, sorted(str(p.relative_to(REPO)) for p in (REPO / d).glob("CMP-*.json")))
                   if c["issued_at_utc"] < real["issued_at_utc"]]
        prior = max(earlier, key=lambda c: c["issued_at_utc"])
        cn = json.loads((box.root / week_rel("W47") / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes())
        with mock.patch.object(nh, "head_sha", return_value=real["bound_main_sha"]):
            built = nh.build_official_compass(
                auto, packet_path=Path(real["source_bindings"]["auto_market_state"]["packet_path"]), cn_package=cn,
                cn_binding=real["source_bindings"]["cycle_navigator"], repo_root=box.root,
                issued_at=_parse(real["issued_at_utc"]), run_reason=real["run_reason"], prior_compass=prior)
        # Undo the one re-binding, so the comparison with the issued packet is exact.
        production_commit = template["source_snapshot"]["exact_commit_sha"]
        return real, json.loads(json.dumps(built).replace(commit, production_commit))

    def test_issued_packet_after_the_breach_carried_no_marker(self):
        raw = (REPO / REAL_BREACH).read_text()
        real = json.loads(raw)
        self.assertEqual((real["data_status"], real["action_now"]), ("OK", "HOLD_WAIT"))
        self.assertEqual(real["protection_tracker"]["pullback_risk_state"], "ELEVATED")
        self.assertEqual(real["protection_tracker"]["data_quality"], "OK")
        # Its own bound completed close was already below the frozen weekly floor ...
        self.assertEqual(real["market_reference"]["observation_open_utc"], "2026-11-21T23:00:00Z")
        self.assertLess(real["market_reference"]["btc_usdt"], BTC_FLOOR)
        # ... and nothing in the packet said so, nor since when the risk state had been carried.
        self.assertFalse(NEW_KEYS & set(real))
        for word in ("breach", "floor", "stale"):
            self.assertNotIn(word, raw.lower())
        public = (REPO / REAL_BREACH.replace("/daily/", "/public/")).read_text()
        self.assertNotIn("INHERITED", public)

    def test_same_inputs_now_state_breach_inheritance_and_freshness_separately(self):
        with tempfile.TemporaryDirectory() as tmp:
            real, built = self.real_case(tmp, REAL_BREACH)
            band, risk, source = built["cn_band_status"], built["risk_freshness"], built["source_freshness"]
            self.assertEqual(source["status"], "FRESH")
            self.assertEqual(band["forecast_floor_status"], "BREACHED")
            self.assertEqual(band["first_weekly_floor_breach"]["BTC"], {
                "day_utc": "2026-11-20", "breach_at_utc": "2026-11-21T00:00:00Z", "close": 58951.51, "floor": BTC_FLOOR})
            self.assertEqual(band["first_weekly_floor_breach"]["ETH"]["close"], 1623.09)
            self.assertEqual(band["first_daily_floor_breach"]["BTC"]["day_utc"], "2026-11-18")
            self.assertEqual(band["evaluated_through_day_utc"], "2026-11-21")
            self.assertEqual(band["pending_days_utc"], ["2026-11-22"])
            self.assertEqual(band["original_freeze"]["issue_number"], 35)
            self.assertEqual(band["quote"], "USDT")
            self.assertEqual(risk["status"], "INHERITED")
            self.assertEqual(risk["since"]["issue_number"], 33)
            self.assertEqual(risk["since"]["forecast_week"], "2026-W45")
            self.assertEqual(risk["since"]["at_utc"], "2026-11-02T08:19:08Z")
            self.assertEqual(risk["inheritance"]["origin"]["chain_issue_numbers"], [35, 34, 33])
            self.assertIn("FORECAST_WEEKLY_FLOOR_BREACHED:BTC@2026-11-21T00:00:00Z", risk["basis"])
            # Descriptive only: the issued decision is reproduced field for field.
            for key in real:
                if key not in IDENTITY:
                    self.assertEqual(built[key], real[key], key)
            self.assertEqual(set(built) - set(real), NEW_KEYS | {"cycle_participation"})

    def test_real_sunday_close_observed_on_monday_of_the_next_iso_week(self):
        rel = f"{OFFICIAL}/daily/2026/11/23/CMP-20261123-" + self._id_issued_at("2026/11/23", "2026-11-23T00:21:12Z")
        with tempfile.TemporaryDirectory() as tmp:
            real, built = self.real_case(tmp, rel)
            self.assertEqual(_parse(real["issued_at_utc"]).isocalendar()[1], 48)
            band = built["cn_band_status"]
            self.assertEqual(band["forecast_week"], "2026-W47")
            self.assertEqual(band["evaluated_through_day_utc"], "2026-11-22")
            self.assertEqual(band["pending_days_utc"], [])
            sunday = band["days"][6]
            self.assertEqual((sunday["state"], sunday["candle_close_utc"]), ("OBSERVED", "2026-11-23T00:00:00Z"))
            self.assertEqual(sunday["assets"]["BTC"]["close"], 61271.08)
            self.assertTrue(sunday["assets"]["BTC"]["close_below_weekly_floor"])
            self.assertFalse(sunday["assets"]["ETH"]["close_below_weekly_floor"])
            for key in real:
                if key not in IDENTITY:
                    self.assertEqual(built[key], real[key], key)

    def test_real_w46_packet_with_backfilled_rows_states_the_first_break(self):
        # First W46 packet issued after a completed close broke the weekly floor (71,289.02): 2026-11-14T03:24:08Z.
        rel = f"{OFFICIAL}/daily/2026/11/14/CMP-20261114-a542e3de587e.json"
        real = real_json(rel)
        self.assertEqual((real["data_status"], real["protection_tracker"]["pullback_risk_state"]), ("OK", "ELEVATED"))
        self.assertNotIn("cn_protection_state_basis", real)
        template = real_json(real["source_bindings"]["auto_market_state"]["packet_path"])
        bar = _parse(template["normalized_state"]["live_market"]["observation_open_utc"])
        with tempfile.TemporaryDirectory() as tmp:
            box = Sandbox(tmp)
            box.add_weeks(("W44", "W45", "W46"))
            box.add_hourly(bar, first_day=datetime(2026, 11, 9, tzinfo=UTC))
            commit = box.commit()
            auto = rebind(template, commit)
            auto["source_health"]["hourly_market"]["row"]["provenance"]["git_blob_sha"] = box.hash_object(csv_rel(bar))
            as_of = _parse(real["issued_at_utc"])
            binding = real["source_bindings"]["cycle_navigator"]
            cn = json.loads((box.root / week_rel("W46") / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes())
            source = nh.source_freshness(auto, as_of)
            band = nh.cn_band_status(auto, cn, binding, box.root, as_of, source_status=source["status"])
            self.assertEqual(source["status"], "FRESH")
            self.assertEqual([day["state"] for day in band["days"]], ["OBSERVED"] * 5 + ["PENDING"] * 2)
            self.assertEqual(band["forecast_floor_status"], "BREACHED")
            self.assertEqual(band["first_weekly_floor_breach"]["BTC"], {
                "day_utc": "2026-11-13", "breach_at_utc": "2026-11-14T00:00:00Z", "close": 68314.0, "floor": 71289.02})
            self.assertEqual(band["first_daily_floor_breach"]["ETH"]["day_utc"], "2026-11-10")
            origin = nh.cn_protection_origin(cn, binding, box.root)
            self.assertEqual((origin["issue_number"], origin["chain_issue_numbers"]), (33, [34, 33]))

    def _id_issued_at(self, day, issued):
        for path in sorted((REPO / OFFICIAL / "daily" / day).glob("CMP-*.json")):
            if json.loads(path.read_text())["issued_at_utc"] == issued:
                return path.name.split("CMP-20261123-")[1]
        self.fail("real packet not found: " + issued)


class CountercaseTest(unittest.TestCase):
    """The eight synthetic countercases of Archive #2294, on real bytes."""

    def test_1_fresh_source_with_inherited_risk(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE).build()
            self.assertEqual(out["source_freshness"]["status"], "FRESH")
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "NOT_BREACHED")
            self.assertEqual(out["cn_band_status"]["daily_floor_status"], "NOT_BREACHED")
            self.assertEqual(out["risk_freshness"]["status"], "INHERITED")
            self.assertEqual(out["risk_freshness"]["basis"], ["INHERITED_FROM_PRIOR_ISSUE"])

    def test_2_fresh_source_with_breach_and_inherited_risk_changes_no_decision_field(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            calm = Case(a, bar=at(5), override=SAFE).build()
            broken = Case(b, bar=at(5), override=merged(close(3, btc=BTC_FLOOR - 0.01))).build()
            self.assertEqual(broken["source_freshness"]["status"], "FRESH")
            self.assertEqual(broken["cn_band_status"]["forecast_floor_status"], "BREACHED")
            self.assertEqual(broken["risk_freshness"]["status"], "INHERITED")
            self.assertEqual(broken["risk_freshness"]["basis"], [
                "INHERITED_FROM_PRIOR_ISSUE",
                "FORECAST_WEEKLY_FLOOR_BREACHED:BTC@2026-11-19T00:00:00Z",
                "FORECAST_DAILY_FLOOR_BREACHED:BTC@2026-11-19T00:00:00Z",
            ])
            # No severity, no action, no SELL: every pre-existing field is identical to the calm week.
            for key in calm:
                if key not in NEW_KEYS | IDENTITY | {"source_bindings", "decision_context_fingerprint", "evidence_snapshot"}:
                    self.assertEqual(broken[key], calm[key], key)
            self.assertEqual(broken["action_now"], "HOLD_WAIT")
            self.assertEqual(broken["sell_assessment"]["state"], "UNAVAILABLE")
            self.assertEqual(broken["protection_tracker"], calm["protection_tracker"])

    def test_3_stale_source_is_untestable_not_no_breach(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            case.as_of = _parse(case.auto["packet_generated_at_utc"]) + timedelta(hours=5)
            out = case.build()
            self.assertEqual(out["source_freshness"]["status"], "STALE")
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "UNTESTABLE")
            self.assertEqual(out["cn_band_status"]["reason"], "DAILY_SOURCE_NOT_FRESH")
            self.assertEqual(out["risk_freshness"]["status"], "STALE")
            self.assertTrue(out["risk_freshness"]["basis"][0].startswith("DAILY_SOURCE_STALE:"))
            self.assertEqual(out["protection_tracker"]["pullback_risk_state"], "UNAVAILABLE")

    def test_4_future_incomplete_wrong_quote_pre_issue_or_byte_mismatched_input_is_untestable(self):
        def future(auto):
            auto["packet_generated_at_utc"] = "2026-11-21T09:00:00Z"   # after issuance

        def wrong_quote(package):
            package["forecast_freeze"]["price_quote"]["BTC"] = "USD"

        def issued_late(package):
            package["generated_unix"] = int(at(5, hour=23).timestamp()) + 1   # frozen after every observed candle opened

        def byte_mismatch(auto):
            auto["source_health"]["hourly_market"]["row"]["provenance"]["git_blob_sha"] = "0" * 40

        def owner_close(auto):
            auto["normalized_state"]["live_market"]["btc_usdt"] += 1.0

        breach = merged(close(2, btc=BTC_FLOOR - 500))
        cases = {
            "future": (dict(auto_edit=future), "BAR_FUTURE_INCOMPLETE_OR_CLOCK_UNAVAILABLE"),
            "incomplete_missing_close": (dict(drop=(stamp(at(4)),)), "COMPLETED_DAY_ROW_UNTESTABLE"),
            "incomplete_not_pass": (dict(extra_override={stamp(at(4)): {"spot_status": "PARTIAL"}}), "COMPLETED_DAY_ROW_UNTESTABLE"),
            "incomplete_window": (dict(extra_override={stamp(at(4)): {"source_window_end_utc": stamp(at(4))}}), "COMPLETED_DAY_ROW_UNTESTABLE"),
            "wrong_quote": (dict(week_edit={"W47": wrong_quote}), "QUOTE_MISMATCH_OR_UNSTATED"),
            "pre_issue": (dict(week_edit={"W47": issued_late}), "NO_ELIGIBLE_COMPLETED_CLOSE"),
            "byte_mismatch": (dict(auto_edit=byte_mismatch), "HOURLY_ROW_BLOB_MISMATCH"),
            "owner_close_mismatch": (dict(auto_edit=owner_close), "OWNER_CLOSE_MISMATCH"),
        }
        for name, (kwargs, reason) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                override = dict(SAFE if name.startswith("incomplete") else breach)
                for label, values in kwargs.pop("extra_override", {}).items():
                    override[label] = {**override.get(label, {}), **values}
                out = Case(tmp, bar=at(5), override=override, **kwargs).build()
                band = out["cn_band_status"]
                self.assertEqual(band["forecast_floor_status"], "UNTESTABLE", name)
                self.assertEqual(band["reason"], reason, name)
                self.assertNotIn("FORECAST_WEEKLY_FLOOR_BREACHED", json.dumps(out["risk_freshness"]["basis"]), name)

    def test_5_sunday_close_in_the_next_iso_week_inside_a_bounded_window(self):
        sunday_break = merged(close(7, btc=BTC_FLOOR - 1))
        monday = {stamp(at(8, hour=h)): {"btc_close": "50000.0", "eth_close": "1500.0"} for h in range(0, 3)}
        with tempfile.TemporaryDirectory() as tmp:
            # Monday 02:xx of W48: the Sunday candle is known, and three Monday candles sit far below the floor.
            case = Case(tmp, bar=at(8, hour=2), override={**sunday_break, **monday})
            self.assertEqual(case.as_of.isocalendar()[1], 48)
            out = case.build()
            band = out["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "BREACHED")
            self.assertEqual(band["first_weekly_floor_breach"], {"BTC": {
                "day_utc": "2026-11-22", "breach_at_utc": "2026-11-23T00:00:00Z", "close": BTC_FLOOR - 1, "floor": BTC_FLOOR}})
            self.assertEqual(len(band["days"]), 7)                       # a next-week candle is never compared
            self.assertEqual(out["risk_freshness"]["status"], "INHERITED")
        with tempfile.TemporaryDirectory() as tmp:
            # 24 hours after the week ended the frozen week is no longer comparable.
            case = Case(tmp, bar=at(8, hour=23), override={**sunday_break, **monday})
            case.as_of = WEEK_START + timedelta(days=8, minutes=30)
            case.auto = bound_auto(case.box, case.commit, at(8, hour=23), available=case.as_of - timedelta(minutes=5))
            out = case.build()
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "UNTESTABLE")
            self.assertEqual(out["cn_band_status"]["reason"], "FORECAST_WEEK_EXPIRED_BEYOND_SUNDAY_CLOSE_WINDOW")
            self.assertEqual(out["risk_freshness"]["status"], "STALE")
            self.assertEqual(out["risk_freshness"]["basis"][0], "CN_FORECAST_WEEK_EXPIRED")

    def test_6_pre_upgrade_slot_is_regenerated_without_a_rewrite(self):
        old = real_json(REAL_BREACH)
        old_public = (REPO / REAL_BREACH.replace("/daily/", "/public/")).read_bytes()
        self.assertEqual(old["schema_version"], 4)
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as repo:
            root = Path(tmp) / "official"
            first = nh.write_official_compass(old, root)
            frozen = Path(first["path"]).read_bytes()
            self.assertEqual(Path(first["public_path"]).read_bytes(), old_public)     # byte-identical re-projection
            again = nh.write_official_compass(old, root)                               # the retry that crashed in #2276
            self.assertEqual(again["status"], "EXISTING_DAILY_FREEZE")
            self.assertEqual(Path(first["path"]).read_bytes(), frozen)
            self.assertEqual(Path(first["public_path"]).read_bytes(), old_public)
            # A schema-4 scheduled slot of the day is never reused or rewritten by a schema-6 issuance.
            case = Case(repo, bar=at(6))
            case.as_of = _parse(old["issued_at_utc"]) + timedelta(minutes=1)
            case.auto = bound_auto(case.box, case.commit, at(6), available=case.as_of - timedelta(minutes=1))
            slot = dict(old, run_reason="SCHEDULED_MORNING")
            slot["compass_id"] = "CMP-20261122-aaaaaaaaaaaa"
            slot["compass_sha256"] = nh.digest(nh.canon({k: v for k, v in slot.items() if k != "compass_sha256"}))
            written_slot = nh.write_official_compass(slot, root)
            result = nh.write_official_compass(case.build(run_reason="SCHEDULED_MORNING"), root)
            self.assertEqual(result["status"], "WRITTEN")
            self.assertNotEqual(result["path"], written_slot["path"])
            self.assertEqual(json.loads(Path(written_slot["path"]).read_text())["schema_version"], 4)
            self.assertEqual(json.loads(Path(result["path"]).read_text())["schema_version"], 6)
            self.assertNotIn("cycle_participation", json.loads(Path(written_slot["public_path"]).read_text()))
            self.assertIn("cycle_participation", json.loads(Path(result["public_path"]).read_text()))
            self.assertNotIn("risk_freshness", json.loads(Path(written_slot["public_path"]).read_text()))
            self.assertIn("risk_freshness", json.loads(Path(result["public_path"]).read_text()))

    def test_7_valid_packet_that_is_not_served_is_merged_but_not_served(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE).build()
            public = nh.build_public_projection(out)
            sha = "a" * 40
            for key in NEW_KEYS:                                                  # the producer claims no delivery
                for word in ("deliver", "consumer", "pages_served", "user_visible"):
                    self.assertNotIn(word, json.dumps(out[key]).lower())
            state = lambda **kw: receipt.classify(**kw)["state"]  # noqa: E731
            self.assertEqual(state(merged_squash_sha=None, emitted_packet=out, served_packet=public), "NOT_MERGED")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=real_json(REAL_BREACH), served_packet=None), "MERGED_NOT_EMITTED")
            forged = dict(real_json(REAL_BREACH), **{key: out[key] for key in NEW_KEYS})    # fields on a schema-4 packet
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=forged, served_packet=public), "MERGED_NOT_EMITTED")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=None), "MERGED_BUT_NOT_SERVED")
            stale_bundle = nh.build_public_projection(real_json(REAL_BREACH))
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=stale_bundle), "MERGED_BUT_NOT_SERVED")
            other = dict(public, compass_id="CMP-20261120-000000000000")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=other), "MERGED_BUT_NOT_SERVED")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=public), "SERVED_NOT_USER_VISIBLE")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=public,
                                   browser_readback_widths=(390,)), "SERVED_NOT_USER_VISIBLE")
            self.assertEqual(state(merged_squash_sha=sha, emitted_packet=out, served_packet=public,
                                   browser_readback_widths=(390, 1280)), "USER_VISIBLE")

    def test_8_stale_and_breached_at_once_shows_both_channels(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=merged(close(2, eth=ETH_FLOOR - 0.5)))
            case.as_of = _parse(case.auto["packet_generated_at_utc"]) + timedelta(hours=5)
            out = case.build()
            self.assertEqual(out["source_freshness"]["status"], "STALE")
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "BREACHED")
            self.assertEqual(out["risk_freshness"]["status"], "STALE")
            basis = out["risk_freshness"]["basis"]
            self.assertTrue(basis[0].startswith("DAILY_SOURCE_STALE:"))
            self.assertIn("FORECAST_WEEKLY_FLOOR_BREACHED:ETH@2026-11-18T00:00:00Z", basis)
            self.assertEqual(out["risk_freshness"]["forecast_floor_status"], "BREACHED")
            self.assertEqual(out["risk_freshness"]["source_freshness_status"], "STALE")


class CompletedCloseSourceTest(unittest.TestCase):
    """Addendum 1: git-bound 23:00 UTC closes at the snapshot, exact boundaries, ties and a real Git oracle."""

    def test_close_is_read_from_git_at_the_snapshot_not_from_the_working_tree_or_capture_window(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Day 2 breaks the floor; the bound bar is the afternoon of day 6, far outside an eight-row window.
            case = Case(tmp, bar=at(6, hour=15), override=merged(close(2, btc=BTC_FLOOR - 100)))
            out = case.build()
            self.assertEqual(out["cn_band_status"]["first_weekly_floor_breach"]["BTC"]["day_utc"], "2026-11-17")
            self.assertEqual(out["cn_band_status"]["evaluated_through_day_utc"], "2026-11-20")
            self.assertEqual(out["cn_band_status"]["pending_days_utc"], ["2026-11-21", "2026-11-22"])
            # Rows that changed in the working tree after the snapshot commit are not evidence.
            path = case.box.root / csv_rel(at(2))
            path.write_text(path.read_text().replace(repr(BTC_FLOOR - 100), "66002.0"))
            self.assertEqual(case.build()["cn_band_status"], out["cn_band_status"])

    def test_every_source_blob_matches_git_hash_object(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            band = case.build()["cn_band_status"]
            observed = [day for day in band["days"] if day["state"] == "OBSERVED"]
            self.assertEqual(len(observed), 5)
            for day in observed:
                self.assertEqual(day["source"]["git_blob_sha"], case.box.hash_object(day["source"]["path"]))
            self.assertEqual(band["source"]["bound_bar_csv"]["git_blob_sha"], case.box.hash_object(csv_rel(at(5))))
            self.assertEqual(band["source"]["snapshot_commit_sha"], case.commit)

    def test_unreadable_snapshot_commit_is_untestable(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=merged(close(2, btc=1.0)))
            case.auto["source_snapshot"]["exact_commit_sha"] = "1" * 40
            case.auto["source_health"]["hourly_market"]["row"]["provenance"]["exact_commit_sha"] = "1" * 40
            band = case.build()["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "UNTESTABLE")
            self.assertEqual(band["reason"], "HOURLY_ROW_BINDING_UNAVAILABLE:ROW_SOURCE_UNREADABLE_AT_SNAPSHOT")

    def test_bytes_that_do_not_hash_to_the_git_blob_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            real_check_output = subprocess.check_output

            def tampered(cmd, *args, **kwargs):
                out = real_check_output(cmd, *args, **kwargs)
                if cmd[:2] == ["git", "show"] and cmd[2].endswith(csv_rel(at(2))):
                    return out.replace(repr(66002.0).encode(), b"1.0")     # a breach Git never committed
                return out

            with mock.patch.object(nh.subprocess, "check_output", side_effect=tampered):
                band = case.build()["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "UNTESTABLE")
            self.assertEqual(band["days"][1]["reason"], "ROW_SOURCE_UNREADABLE_AT_SNAPSHOT")
            self.assertEqual(band["first_weekly_floor_breach"], {})

    def test_an_unbound_or_inconsistent_forecast_or_row_binding_is_untestable(self):
        def other_week(package):
            package["forecast_freeze"]["daily_price_path"]["forecast_week"] = "2026-W46"

        def six_points(package):
            package["forecast_freeze"]["daily_price_path"]["BTC"]["points"].pop()

        def duplicate_day(package):
            package["forecast_freeze"]["daily_price_path"]["ETH"]["points"][6]["day"] = 6

        def no_snapshot(auto):
            auto["source_snapshot"]["exact_commit_sha"] = "HEAD"

        def other_row(auto):
            auto["source_health"]["hourly_market"]["row"]["timestamp_utc"] = stamp(at(5, hour=22))

        def other_path(auto):
            auto["source_health"]["hourly_market"]["row"]["provenance"]["exact_path"] = csv_rel(at(4))

        def half_hour(auto):
            auto["normalized_state"]["live_market"]["observation_open_utc"] = stamp(at(5) + timedelta(minutes=30))

        def no_semantics(auto):
            auto["normalized_state"]["live_market"].pop("observation_semantics")

        breach = merged(close(2, btc=1.0))
        cases = {
            "week": (dict(week_edit={"W47": other_week}), "CN_DAILY_PATH_UNAVAILABLE"),
            "six_points": (dict(week_edit={"W47": six_points}), "CN_FLOOR_UNAVAILABLE"),
            "duplicate_day": (dict(week_edit={"W47": duplicate_day}), "CN_FLOOR_UNAVAILABLE"),
            "snapshot": (dict(auto_edit=no_snapshot), "SNAPSHOT_COMMIT_UNBOUND"),
            "row_timestamp": (dict(auto_edit=other_row), "HOURLY_ROW_BINDING_UNAVAILABLE"),
            "row_path": (dict(auto_edit=other_path), "HOURLY_ROW_BINDING_UNAVAILABLE"),
            "half_hour": (dict(auto_edit=half_hour), "BAR_FUTURE_INCOMPLETE_OR_CLOCK_UNAVAILABLE"),
            "semantics": (dict(auto_edit=no_semantics), "BAR_FUTURE_INCOMPLETE_OR_CLOCK_UNAVAILABLE"),
        }
        for name, (kwargs, reason) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                band = Case(tmp, bar=at(5), override=breach, **kwargs).build()["cn_band_status"]
                self.assertEqual((band["forecast_floor_status"], band["reason"]), ("UNTESTABLE", reason), name)
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=breach)
            band = case.build(binding=dict(case.binding, issue_number=34))["cn_band_status"]
            self.assertEqual((band["forecast_floor_status"], band["reason"]), ("UNTESTABLE", "CN_BINDING_UNAVAILABLE"))
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(1, hour=6))                               # Monday 07:26, before the 08:35 issue
            self.assertLess(case.as_of, _parse("2026-11-16T08:35:53Z"))
            band = case.build()["cn_band_status"]
            self.assertEqual((band["forecast_floor_status"], band["reason"]), ("UNTESTABLE", "AS_OF_BEFORE_FORECAST_ISSUE"))

    def test_a_tie_with_the_floor_is_not_a_breach(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=merged(close(2, btc=BTC_FLOOR, eth=ETH_FLOOR))).build()
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "NOT_BREACHED")
            self.assertFalse(out["cn_band_status"]["days"][1]["assets"]["BTC"]["close_below_weekly_floor"])
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=merged(close(2, btc=BTC_DAY[2]))).build()
            self.assertEqual(out["cn_band_status"]["daily_floor_status"], "NOT_BREACHED")

    def test_each_day_is_compared_with_its_own_frozen_daily_floor(self):
        # 63,500 is above the day-2 low (63,133.65) and below the day-5 low (63,803.60).
        with tempfile.TemporaryDirectory() as tmp:
            band = Case(tmp, bar=at(6), override=merged(close(2, btc=63500.0))).build()["cn_band_status"]
            self.assertEqual(band["daily_floor_status"], "NOT_BREACHED")
            self.assertEqual(band["days"][1]["assets"]["BTC"]["daily_floor"], BTC_DAY[2])
        with tempfile.TemporaryDirectory() as tmp:
            band = Case(tmp, bar=at(6), override=merged(close(5, btc=63500.0))).build()["cn_band_status"]
            self.assertEqual(band["daily_floor_status"], "BREACHED")
            self.assertEqual(band["forecast_floor_status"], "NOT_BREACHED")
            self.assertEqual(band["first_daily_floor_breach"]["BTC"], {
                "day_utc": "2026-11-20", "breach_at_utc": "2026-11-21T00:00:00Z", "close": 63500.0, "floor": BTC_DAY[5]})

    def test_first_breach_is_the_earliest_and_is_stamped_with_the_candle_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            override = merged(close(3, btc=BTC_FLOOR - 10), close(5, btc=BTC_FLOOR - 999))
            band = Case(tmp, bar=at(6), override=override).build()["cn_band_status"]
            self.assertEqual(band["first_weekly_floor_breach"]["BTC"]["day_utc"], "2026-11-18")
            self.assertEqual(band["first_weekly_floor_breach"]["BTC"]["breach_at_utc"], "2026-11-19T00:00:00Z")
            self.assertEqual(band["days"][2]["candle_open_utc"], "2026-11-18T23:00:00Z")

    def test_a_close_from_before_the_forecast_was_frozen_is_not_a_forecast_outcome(self):
        def issued_wednesday(package):
            package["generated_unix"] = int(at(3, hour=9).timestamp())

        with tempfile.TemporaryDirectory() as tmp:
            override = merged(close(1, btc=1.0), close(2, btc=1.0))
            band = Case(tmp, bar=at(5), override=override, week_edit={"W47": issued_wednesday}).build()["cn_band_status"]
            self.assertEqual([day["state"] for day in band["days"][:5]], ["PRE_ISSUE", "PRE_ISSUE", "OBSERVED", "OBSERVED", "OBSERVED"])
            self.assertEqual(band["forecast_floor_status"], "NOT_BREACHED")
            self.assertEqual(band["observed_days"], 3)

    def test_an_intraday_low_below_the_floor_is_not_a_completed_close(self):
        with tempfile.TemporaryDirectory() as tmp:
            override = merged({stamp(at(3, hour=12)): {"btc_close": "50000.0", "btc_low": "49000.0"}})
            band = Case(tmp, bar=at(5), override=override).build()["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "NOT_BREACHED")

    def test_a_backfilled_close_row_counts_and_a_row_from_the_future_does_not(self):
        late = {stamp(at(2)): {"source_window_end_utc": stamp(at(2) + timedelta(hours=3)), "btc_close": repr(BTC_FLOOR - 5)}}
        with tempfile.TemporaryDirectory() as tmp:
            # Production backfills a missed hour in a later capture window (W46: 2026-11-10, -11, -13, -14).
            band = Case(tmp, bar=at(5), override=merged(late)).build()["cn_band_status"]
            self.assertEqual((band["days"][1]["state"], band["forecast_floor_status"]), ("OBSERVED", "BREACHED"))
        future = {stamp(at(5)): {"source_window_end_utc": stamp(at(5) + timedelta(hours=9))}}
        with tempfile.TemporaryDirectory() as tmp:
            band = Case(tmp, bar=at(5), override=merged(future)).build()["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "UNTESTABLE")
            self.assertEqual(band["reason"], "HOURLY_ROW_BINDING_UNAVAILABLE:ROW_CAPTURED_AFTER_OWNER_PACKET")

    def test_a_duplicated_close_row_is_untestable(self):
        with tempfile.TemporaryDirectory() as tmp:
            extra = {stamp(at(3)): [{"btc_close": "1.0"}]}
            band = Case(tmp, bar=at(5), override=SAFE, extra_rows=extra).build()["cn_band_status"]
            self.assertEqual((band["forecast_floor_status"], band["days"][2]["reason"]), ("UNTESTABLE", "ROW_DUPLICATE"))

    def test_a_proven_breach_survives_a_later_unreadable_day(self):
        with tempfile.TemporaryDirectory() as tmp:
            band = Case(tmp, bar=at(5), override=merged(close(2, btc=BTC_FLOOR - 1)), drop=(stamp(at(4)),)).build()["cn_band_status"]
            self.assertEqual(band["forecast_floor_status"], "BREACHED")
            self.assertEqual(band["days"][3]["state"], "UNTESTABLE")


class RiskFreshnessTest(unittest.TestCase):
    def evaluated(self, package):
        """A weekly issue that evaluated protection itself (not the carry-forward issuer)."""
        package["issuer_method"] = "CN_WEEKLY_MODEL_FIXTURE"
        package["decision_projection"]["issuer_method"] = "CN_WEEKLY_MODEL_FIXTURE"
        package["readable_markdown"] = "# Cycle Navigator 2026-W47"

    def test_no_breach_and_evaluated_state_is_fresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE, week_edit={"W47": self.evaluated}).build()
            risk = out["risk_freshness"]
            self.assertEqual((risk["status"], risk["basis"]), ("FRESH", ["EVALUATED_IN_BOUND_WEEKLY_ISSUE"]))
            self.assertEqual(risk["since"]["issue_number"], 35)
            self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "NOT_BREACHED")

    def test_a_breach_never_changes_the_provenance_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=merged(close(2, btc=1.0)), week_edit={"W47": self.evaluated}).build()
            self.assertEqual(out["risk_freshness"]["status"], "FRESH")
            self.assertIn("FORECAST_WEEKLY_FLOOR_BREACHED:BTC@2026-11-18T00:00:00Z", out["risk_freshness"]["basis"])

    def test_degraded_evidence_is_degraded_and_a_live_state_on_it_is_named(self):
        def blocker(auto):
            auto["blockers"] = ["sentiment"]
            auto["decision_context_status"] = "DEGRADED"

        def missing_value(auto):
            auto["normalized_state"]["altseason_context"] = {}

        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE, auto_edit=blocker).build()
            self.assertEqual(out["protection_tracker"]["pullback_risk_state"], "UNAVAILABLE")
            self.assertEqual((out["risk_freshness"]["status"], out["risk_freshness"]["basis"]), ("DEGRADED", ["CORE_BLOCKERS=sentiment", "INHERITED_FROM_PRIOR_ISSUE"]))
        with tempfile.TemporaryDirectory() as tmp:
            # G1: a value missing in a PASS lane makes the packet DEGRADED while the tracker stays live.
            out = Case(tmp, bar=at(5), override=SAFE, auto_edit=missing_value).build()
            self.assertEqual((out["data_status"], out["protection_tracker"]["pullback_risk_state"]), ("DEGRADED", "ELEVATED"))
            self.assertEqual(out["protection_tracker"]["data_quality"], "OK")
            self.assertEqual(out["risk_freshness"]["status"], "DEGRADED")
            self.assertIn("LIVE_RISK_STATE_DISPLAYED_ON_NON_OK_EVIDENCE", out["risk_freshness"]["basis"])
            self.assertTrue(out["risk_freshness"]["basis"][0].startswith("MAPPING_INTEGRITY_"))
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            out = case.build(binding={"status": "DEGRADED", "reason": "CN_POINTER_PACKAGE_HASH_MISMATCH"})
            self.assertEqual((out["risk_freshness"]["status"], out["risk_freshness"]["basis"]), ("DEGRADED", ["CN_BINDING_DEGRADED"]))
            self.assertIsNone(out["risk_freshness"]["since"])
            self.assertEqual(out["cn_band_status"]["reason"], "CN_BINDING_UNAVAILABLE")

    def test_unknown_source_clock_is_unknown_not_stale_and_not_fresh(self):
        def no_clock(auto):
            auto["source_health"]["hourly_market"]["freshness"]["retrieval_freshness"]["timestamp"] = None

        def future_clock(auto):
            auto["source_health"]["hourly_market"]["freshness"]["retrieval_freshness"]["timestamp"] = "2026-11-25T00:00:00Z"

        for edit in (no_clock, future_clock):
            with self.subTest(edit.__name__), tempfile.TemporaryDirectory() as tmp:
                out = Case(tmp, bar=at(5), override=SAFE, auto_edit=edit).build()
                self.assertEqual(out["source_freshness"]["status"], "UNKNOWN")
                self.assertEqual(out["source_freshness"]["stale_lanes"], [])
                self.assertEqual(out["risk_freshness"]["status"], "DEGRADED")
                self.assertEqual(out["risk_freshness"]["basis"][0], "DAILY_SOURCE_FRESHNESS_UNKNOWN")
                self.assertEqual(out["cn_band_status"]["forecast_floor_status"], "UNTESTABLE")

    def test_source_freshness_carries_its_clock_and_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            source = case.build()["source_freshness"]
            self.assertEqual(source["clock"]["evaluated_at_utc"], stamp(case.as_of))
            self.assertEqual(source["clock"]["observation_open_utc"], stamp(at(5)))
            self.assertEqual(source["binding"]["source_snapshot_commit_sha"], case.commit)
            self.assertEqual(source["binding"]["auto_market_state_packet_sha256"], case.auto["packet_sha256"])
            case.as_of += timedelta(hours=5)
            stale = case.build()["source_freshness"]
            self.assertEqual(stale["status"], "STALE")
            self.assertIn("auto_market_state_packet", stale["stale_lanes"])
            self.assertGreater(stale["clock"]["oldest_age_seconds"], stale["clock"]["oldest_max_age_seconds"])


class InheritanceOriginTest(unittest.TestCase):
    def origin(self, box, week="W48", issue=36, iso_week=48):
        cn, binding = binding_for(box, week, issue, iso_week)
        return nh.cn_protection_origin(cn, binding, box.root)

    def test_real_w48_declares_issue_35_but_the_state_was_last_evaluated_in_issue_33(self):
        w48 = real_json(f"{week_rel('W48')}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
        self.assertEqual(w48["decision_projection"]["protection"]["inherited_from_issue_number"], 35)
        with tempfile.TemporaryDirectory() as tmp:
            box = Sandbox(tmp)
            box.add_weeks(("W44", "W45", "W46", "W47", "W48"))
            origin = self.origin(box)
            self.assertEqual(origin["status"], "RESOLVED")
            self.assertEqual((origin["issue_number"], origin["public_issue_number"], origin["forecast_week"]), (33, 32, "2026-W45"))
            self.assertEqual(origin["chain_issue_numbers"], [36, 35, 34, 33])
            self.assertEqual(origin["issues_carried"], 3)
            raw = (REPO / week_rel("W45") / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").read_bytes()
            self.assertEqual(origin["machine_package_sha256"], hashlib.sha256(raw).hexdigest())

    def test_an_unprovable_chain_is_unresolved_never_guessed(self):
        def other_state(package):
            package["decision_projection"]["protection"]["pullback_risk_state"] = "HIGH"

        def later_clock(package):
            package["generated_unix"] = 1999999999

        cases = {
            "missing_week": (dict(weeks=("W45", "W47", "W48")), "PRIOR_ISSUE_NOT_FOUND_HASH_BOUND"),
            "state_differs": (dict(weeks=("W45", "W46", "W47", "W48"), edit={"W46": other_state}), "PRIOR_ISSUE_STATE_OR_CLOCK_MISMATCH"),
            "clock_not_earlier": (dict(weeks=("W45", "W46", "W47", "W48"), edit={"W46": later_clock}), "PRIOR_ISSUE_STATE_OR_CLOCK_MISMATCH"),
        }
        for name, (kwargs, reason) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                box = Sandbox(tmp)
                box.add_weeks(**kwargs)
                origin = self.origin(box)
                self.assertEqual((origin["status"], origin["reason"]), ("UNRESOLVED", reason), name)
        with tempfile.TemporaryDirectory() as tmp:
            box = Sandbox(tmp)
            box.add_weeks(("W45", "W46", "W47", "W48"))
            pointer = box.root / week_rel("W46") / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json"
            pointer.write_text(pointer.read_text().replace(json.loads(pointer.read_text())["machine_package_sha256"], "0" * 64))
            self.assertEqual(self.origin(box)["reason"], "PRIOR_ISSUE_NOT_FOUND_HASH_BOUND")

    def test_unresolved_origin_is_named_and_since_is_null(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE, weeks=("W45", "W47")).build()
            risk = out["risk_freshness"]
            self.assertEqual(risk["status"], "INHERITED")
            self.assertIsNone(risk["since"])
            self.assertEqual(risk["basis"], ["INHERITED_FROM_PRIOR_ISSUE", "INHERITANCE_ORIGIN_UNRESOLVED:PRIOR_ISSUE_NOT_FOUND_HASH_BOUND"])


class SchemaAndConsumerTest(unittest.TestCase):
    def test_schema_is_6_and_feeds_the_compass_id(self):
        self.assertEqual(nh.OFFICIAL_COMPASS_SCHEMA_VERSION, 6)
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=SAFE)
            new = case.build()
            with mock.patch.object(nh, "OFFICIAL_COMPASS_SCHEMA_VERSION", 4):
                old = case.build()
            self.assertEqual(new["schema_version"], 6)
            self.assertNotEqual(new["compass_id"], old["compass_id"])

    def test_consumer_census_every_schema_reader_accepts_6(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Case(tmp, bar=at(5), override=SAFE).build()
        # scripts/learning/action_compass_exit_calibration.py: minimum schema 3.
        _, reason = exit_calibration.eligible_typed_protection(out)
        self.assertNotEqual(reason, "PRE_DECISION_INTEGRITY_SCHEMA")
        _, legacy_reason = exit_calibration.eligible_typed_protection(dict(out, schema_version=2))
        self.assertEqual(legacy_reason, "PRE_DECISION_INTEGRITY_SCHEMA")
        # .github/workflows/daily-compass.yml: the PR dry run asserts the exact constant.
        workflow = (REPO / ".github/workflows/daily-compass.yml").read_text()
        self.assertIn(f"assert d['schema_version']=={nh.OFFICIAL_COMPASS_SCHEMA_VERSION}\n", workflow)
        self.assertEqual(workflow.count("d['schema_version']=="), 1)
        # write_official_compass slot reuse compares schema on both sides (covered by countercase 6).
        self.assertIn("tests.data_ping.test_compass_risk_freshness_v1", workflow)

    def test_public_projection_carries_statuses_but_no_internal_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=merged(close(2, btc=1.0)))
            out = case.build()
            public = nh.build_public_projection(out)
            text = json.dumps(public)
            self.assertEqual(public["risk_freshness"], out["risk_freshness"])
            self.assertEqual(public["cycle_participation"], out["cycle_participation"])
            self.assertFalse(public["cycle_participation"]["rotation_confirmed"])
            self.assertEqual(public["cn_band_status"]["forecast_floor_status"], "BREACHED")
            self.assertEqual(public["source_freshness"]["status"], "FRESH")
            for needle in (case.commit, "git_blob_sha", "03_DAILY_CAPTURE_LOGS", "auto_market_state_packet_sha256", "snapshot_commit_sha"):
                self.assertNotIn(needle, text)
            self.assertNotIn("source_bindings", public)
            for key in NEW_KEYS:
                self.assertEqual(out[key]["authority"], "DESCRIPTIVE_ONLY_NO_SCORE_RISK_OR_ACTION")
                self.assertEqual(out[key]["release_stage"], "SHADOW")

    def test_issuance_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            case = Case(tmp, bar=at(5), override=merged(close(2, btc=1.0)))
            self.assertEqual(case.build(), case.build())


if __name__ == "__main__":
    unittest.main()
