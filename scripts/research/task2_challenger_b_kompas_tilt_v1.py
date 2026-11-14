#!/usr/bin/env python3
"""Task2 Challenger B: does the official Kompas evidence balance carry direction? (research only)

B turns the Official Compass bull/bear evidence balance into a tilted price path and a
probability that each day closes above the issue price. The balance itself is NOT a
probability (contract OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1, semantics
EVIDENCE_BALANCE_NOT_PROBABILITY). B is a separate, pre-registered model that USES it as an
input and is scored for it. It never writes to, or speaks for, the Official Compass.

B issuance = f(frozen Challenger A issuance, point-in-time Kompas packet). Both inputs are
committed before T0, so a B issuance is fully determined before any outcome exists.

  g_h   = TILT * (bull_h - bear_h) / 10 * sigma_hourly * sqrt(24)     (log drift per day)
  m(h)  = g_13 * min(h, 72) / 24 + g_57 * max(h - 72, 0) / 24
  centre_k = P0 * exp(m(h_k))
  p_up_k   = Phi(m(h_k) / (sigma_hourly * sqrt(h_k)))

A horizon with no OK status in the packet window contributes zero drift (no view).
Score: Brier of p_up against 1[close_k > P0] per asset-day; the no-direction baseline is 0.25.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import subprocess
import sys
from pathlib import Path
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))
import task2_challenger_a_sqrt_t_vol_band_v1 as A  # noqa: E402

CONTRACT = "TASK2_CHALLENGER_B_KOMPAS_TILT_v1"
FORMULA_VERSION = "B1"
PARAMS = {
    "tilt": 0.5,
    "short_horizon_hours": 72,
    "packet_dir": "04_MARKET_LEARNING/handlekompas/official/daily",
    "packet_contract": "OFFICIAL_COMPASS_BULL_BEAR_DISPLAY_v1",
    "packet_semantics": "EVIDENCE_BALANCE_NOT_PROBABILITY",
    "packet_lookback_hours": 24,
    "horizons": {"1_3d": "g13", "5_7d": "g57"},
    "baseline_brier": 0.25,
}
DECISION = {"confirmatory_week_clusters": 8, "one_sided_alpha": 0.05,
            "ties": "excluded; a week where B has no view (all p_up = 0.5) is a tie"}


def phi(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def scale_view(packet: dict, horizon: str) -> tuple[int, int] | None:
    """(bull, bear) for one horizon of a valid official packet, else None (no view)."""
    s = packet.get("bull_bear_scale") or {}
    if s.get("contract") != PARAMS["packet_contract"] or s.get("semantics") != PARAMS["packet_semantics"]:
        return None
    h = (s.get("horizons") or {}).get(horizon) or {}
    bull, bear = h.get("bull"), h.get("bear")
    if h.get("status") != "OK" or not isinstance(bull, int) or not isinstance(bear, int):
        return None
    if isinstance(bull, bool) or isinstance(bear, bool) or bull + bear != 10 or min(bull, bear) < 0:
        return None
    return bull, bear


def select_views(candidates: list[dict], t0: dt.datetime) -> dict:
    """Per horizon: the latest packet issued in (T0-24h, T0] that was ALSO in main by T0 and has an OK view.

    candidates: [{"path", "packet", "in_main_utc"}]. A packet backfilled into main after T0 is ignored.
    """
    lo = t0 - dt.timedelta(hours=PARAMS["packet_lookback_hours"])
    out = {}
    for horizon in PARAMS["horizons"]:
        best = None
        for c in candidates:
            issued = A.utc(c["packet"]["issued_at_utc"])
            if not (lo < issued <= t0 and c["in_main_utc"] <= t0):
                continue
            view = scale_view(c["packet"], horizon)
            if view and (best is None or issued > best[0]):
                best = (issued, c["path"], view, c["packet"].get("compass_sha256"))
        out[horizon] = None if best is None else {"issued_at_utc": A.iso(best[0]), "path": best[1],
                                                   "bull": best[2][0], "bear": best[2][1], "compass_sha256": best[3]}
    return out


def issue(a_issuance: dict, views: dict) -> dict:
    """B issuance bound to a verified A issuance and the selected packet views."""
    A.verify_issuance_digest(a_issuance)
    tilt, short = PARAMS["tilt"], PARAMS["short_horizon_hours"]
    assets = {}
    for asset, a in a_issuance["assets"].items():
        sd, p0 = a["sigma_hourly"], a["P0"]
        g = {key: 0.0 for key in PARAMS["horizons"].values()}
        for horizon, key in PARAMS["horizons"].items():
            v = views.get(horizon)
            if v:
                g[key] = tilt * (v["bull"] - v["bear"]) / 10 * sd * math.sqrt(24)
        days = []
        for d in a["days"]:
            h = d["h"]
            m = g["g13"] * min(h, short) / 24 + g["g57"] * max(h - short, 0.0) / 24
            p_up = phi(m / (sd * math.sqrt(h))) if h > 0 else 0.5
            days.append({"day": d["day"], "scored_from_utc": d["scored_from_utc"], "end_utc": d["end_utc"], "h": h,
                         "centre": round(p0 * math.exp(m), 2), "p_up": round(p_up, 6)})
        assets[asset] = {"P0": p0, "drift_per_day": {k: round(v, 10) for k, v in g.items()}, "days": days}
    body = {"contract": CONTRACT, "formula_version": FORMULA_VERSION, "week": a_issuance["week"],
            "issue_clock_utc": a_issuance["issue_clock_utc"], "a_issuance_sha256": a_issuance["issuance_sha256"],
            "views": views, "params": PARAMS, "assets": assets,
            "authority": {"research_only": True, "official_compass": False, "probability_claim_by_compass": False,
                          "trading": False, "promotion": False}}
    body["issuance_sha256"] = _digest(body)
    return body


def verify_issuance(b: dict) -> None:
    body = {k: v for k, v in b.items() if k != "issuance_sha256"}
    if b.get("contract") != CONTRACT or _digest(body) != b.get("issuance_sha256"):
        raise ValueError("B issuance digest mismatch or wrong contract")


def bind_frozen_a_source(a_issuance: dict, views: dict, proof: dict) -> dict:
    """Bind signed B output to S1's independently verified original A provenance."""
    out = issue(a_issuance, views)
    out["a_main_proof"] = {
        "first_main_commit": proof["first_main_commit"],
        "first_main_blob_sha": proof["first_main_blob_sha"],
        "issuance_first_main_utc": proof["issuance_first_main_utc"],
    }
    out["issuance_sha256"] = _digest({k:v for k,v in out.items() if k != "issuance_sha256"})
    return out


def require_frozen_source_binding(b: dict, a_issuance: dict, views: dict, proof: dict) -> None:
    """Reject forged B forecasts even when their self-generated digest is valid."""
    verify_issuance(b)
    if b != bind_frozen_a_source(a_issuance, views, proof):
        raise ValueError("B issuance differs from original A and point-in-time main Compass views")


def score(b: dict, bars: dict, *, a_issuance_first_main_utc: str | None = None) -> dict:
    """Brier per matured asset-day. A day counts only with its full hourly census and a close != P0."""
    verify_issuance(b)
    rows = []
    abstentions = []
    available = A.utc(a_issuance_first_main_utc) if a_issuance_first_main_utc is not None else None
    for asset, a in b["assets"].items():
        for d in a["days"]:
            start, end = A.utc(d["scored_from_utc"]), A.utc(d["end_utc"])
            if available is not None and start < available:
                abstentions.append({"asset": asset, "day": d["day"], "status": "ABSTAIN_PRE_ISSUANCE"})
                continue
            realized = A.realized(bars, asset, start, end)
            if realized is None:
                abstentions.append({"asset": asset, "day": d["day"], "status": "ABSTAIN_INCOMPLETE_HOURLY_CENSUS"})
                continue
            close = realized["close"]
            if close == a["P0"]:
                abstentions.append({"asset": asset, "day": d["day"], "status": "TIE_CLOSE_AT_P0"})
                continue
            y = 1.0 if close > a["P0"] else 0.0
            rows.append({"asset": asset, "day": d["day"], "p_up": d["p_up"], "up": int(y),
                         "brier": round((d["p_up"] - y) ** 2, 8)})
    base = PARAMS["baseline_brier"]
    mean = sum(r["brier"] for r in rows) / len(rows) if rows else None
    year, week = A._parse_week(b["week"])
    final_closed_hour = A.week_monday(year, week) + 7 * A.DAY - A.HOUR
    weekly_matured = final_closed_hour in bars and all(
        asset in bars[final_closed_hour] for asset in b["assets"])
    if not weekly_matured:
        winner = "PENDING"
    elif len(rows) < A.DECISION["min_paired_rows_per_week"]:
        # The pre-registered 8-week sample is by mature and adequately paired
        # weekly clusters, never by two unusually favorable asset-days.
        winner = "MISSING"
    elif mean is None or all(r["p_up"] == 0.5 for r in rows):
        winner = "TIE"
    else:
        winner = "B" if mean < base - 1e-12 else "BASE" if mean > base + 1e-12 else "TIE"
    return {"contract": CONTRACT + "_SCORE", "week": b["week"], "issuance_sha256": b["issuance_sha256"],
            "rows": rows, "abstentions": abstentions, "n": len(rows), "mean_brier": None if mean is None else round(mean, 8),
            "baseline_brier": base, "weekly_matured": weekly_matured, "week_winner": winner}


def decide(weekly: list[dict]) -> dict:
    """First 8 *resolved* distinct ISO week clusters, no future-winner lookahead."""
    n = DECISION["confirmatory_week_clusters"]
    if not isinstance(weekly, list):
        return {"status": "INCONCLUSIVE_INVALID_WEEK_INPUT"}
    by_date = {}
    for row in weekly:
        if not isinstance(row, dict) or not isinstance(row.get("week"), str):
            return {"status": "INCONCLUSIVE_INVALID_WEEK_INPUT"}
        week_id = row["week"]
        if not re.fullmatch(r"\d{4}-W\d{2}", week_id):
            return {"status": "INCONCLUSIVE_INVALID_WEEK_ID"}
        try:
            year, week = A._parse_week(week_id)
            monday = A.week_monday(year, week)
        except (ValueError, TypeError):
            return {"status": "INCONCLUSIVE_INVALID_WEEK_ID"}
        if monday < A.week_monday(2026, 47):
            return {"status": "INCONCLUSIVE_NONPROSPECTIVE_WEEK"}
        if monday in by_date:
            return {"status": "INCONCLUSIVE_DUPLICATE_WEEK"}
        by_date[monday] = row
    chosen = []
    first = A.week_monday(2026, 47)
    latest = max(by_date, default=first)
    current = first
    while current <= latest:
        row = by_date.get(current)
        # Missing or immature earlier weeks can still alter the registered FIRST
        # eight non-tied clusters, so later victories cannot yield a decision.
        if row is None or row.get("weekly_matured") is not True:
            return {"status": "PENDING", "reason": "EARLIER_WEEK_UNRESOLVED",
                    "non_tied_weeks": len(chosen), "required": n,
                    "blocked_week": f"{current.isocalendar().year}-W{current.isocalendar().week:02d}"}
        winner = row.get("week_winner")
        if winner in ("B", "BASE"):
            chosen.append((current, winner, row["week"]))
            if len(chosen) == n:
                wins = sum(item[1] == "B" for item in chosen)
                p = A.sign_test_one_sided_p(wins, n - wins)
                return {"status": "B_HAS_DIRECTION" if wins >= 7 and p < DECISION["one_sided_alpha"] else "NO_PROVEN_DIRECTION",
                        "b_wins": wins, "n": n, "weeks": [item[2] for item in chosen],
                        "one_sided_p": round(p, 6)}
        elif winner not in ("TIE", "MISSING"):
            return {"status": "INCONCLUSIVE_INVALID_WINNER"}
        current += A.DAY * 7
    return {"status": "PENDING", "non_tied_weeks": len(chosen), "required": n,
            "weeks": [item[2] for item in chosen]}



def git_candidates(root: Path, t0: dt.datetime, main_ref: str) -> list[dict]:
    """Enumerate historically introduced main packets, including deleted or renamed paths."""
    if main_ref not in ("main", "refs/heads/main"):
        raise ValueError("B packet evidence must come from local canonical main")
    shallow = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
        check=True, capture_output=True, text=True).stdout.strip()
    if shallow != "false":
        raise ValueError("shallow main history cannot establish frozen Compass packet census")
    out, lo = [], t0 - dt.timedelta(hours=PARAMS["packet_lookback_hours"])
    for day in {lo.date(), t0.date()}:
        folder_rel = (Path(PARAMS["packet_dir"]) / f"{day:%Y}" / f"{day:%m}" / f"{day:%d}").as_posix()
        listing = subprocess.run(
            # A current-tree census overlooks a source deleted after publication.
            ["git", "-C", str(root), "log", "--first-parent", "-m",
             "--diff-filter=A", "--name-only", "--format=",
             "refs/heads/main", "--", folder_rel],
            check=True, capture_output=True, text=True).stdout
        for rel in sorted(set(listing.splitlines())):
            if not rel.startswith(folder_rel + "/"):
                continue
            filename = Path(rel).name
            if not (filename.startswith("CMP-") and filename.endswith(".json")):
                continue
            p = root / rel
            if not p.is_file():
                raise ValueError("canonical main Compass packet missing from working tree: " + rel)
            proof = A.first_in_main(root, rel)
            if proof["current_main_blob_sha"] != proof["first_main_blob_sha"]:
                raise ValueError("official packet changed after first-main; refuse B point-in-time selection")
            original = subprocess.run(
                ["git", "-C", str(root), "show", proof["first_main_commit"] + ":" + rel],
                check=True, capture_output=True).stdout
            if p.read_bytes() != original:
                raise ValueError("working packet differs from canonical first-main bytes")
            out.append({"path": rel, "packet": json.loads(original),
                        "in_main_utc": A.utc(proof["first_main_utc"])})
    return out


def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("issue")
    i.add_argument("--a-issuance", required=True)
    i.add_argument("--repo-root", default=".")
    i.add_argument("--main-ref", required=True)
    i.add_argument("--output", required=True)
    s = sub.add_parser("score")
    s.add_argument("--issuance", required=True)
    s.add_argument("--repo-root", default=".")
    s.add_argument("--output", required=True)
    args = ap.parse_args(list(argv) if argv is not None else None)
    root = Path(args.repo_root)
    if args.cmd == "issue":
        requested = json.loads(Path(args.a_issuance).read_text(encoding="utf-8"))
        year, week = A._parse_week(requested["week"])
        canonical = (root / A.ISSUANCE_PATH.format(year=year, week=week)).resolve()
        if Path(args.a_issuance).resolve() != canonical:
            raise ValueError("B requires S1's canonical frozen main A issuance")
        a, proof = A.read_frozen_main_issuance(root, year, week)
        if requested["issuance_sha256"] != a["issuance_sha256"]:
            raise ValueError("A issuance differs from S1 first-main verification")
        t0 = A.utc(a["issue_clock_utc"])
        out = bind_frozen_a_source(a, select_views(git_candidates(root, t0, args.main_ref), t0), proof)
    else:
        b = json.loads(Path(args.issuance).read_text(encoding="utf-8"))
        year, week = A._parse_week(b["week"])
        a, proof = A.read_frozen_main_issuance(root, year, week)
        if b.get("a_issuance_sha256") != a["issuance_sha256"]:
            raise ValueError("B score not bound to S1 original A issuance")
        t0 = A.utc(a["issue_clock_utc"])
        require_frozen_source_binding(b, a, select_views(git_candidates(root, t0, "main"), t0), proof)
        monday = A.week_monday(year, week)
        out = score(b, A.load_hourly(root, monday, monday + 7 * A.DAY),
                    a_issuance_first_main_utc=proof["issuance_first_main_utc"])
        out["scientific_admissibility"] = "SHADOW_DESCRIPTIVE_PENDING_B_FIRST_MAIN_ISSUANCE_VERIFICATION"
    Path(args.output).write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract": out["contract"], "week": out["week"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
