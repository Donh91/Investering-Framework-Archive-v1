#!/usr/bin/env python3
"""Materialize immutable 21-30D Strategic Compass anchors and 4-8W CN overlays.

This module is deterministic and source-call-free. It does not invent a long-horizon
forecast: 21-30D is consumed only from an eligible Cycle Navigator decision projection,
and 4-8W remains owned by Cycle Navigator. Missing inputs fail closed to UNAVAILABLE.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "STRATEGIC_COMPASS_ANCHOR_v1"
SCORING_CONTRACT = "STRATEGIC_COMPASS_SCORING_v1_1"
ROOT = Path("04_MARKET_LEARNING/handlekompas/strategic")
OFFICIAL_PTR = Path("04_MARKET_LEARNING/handlekompas/official/LATEST_COMPASS.json")
CN_PTR = Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")

VALID_DIRECTIONS = {"UP", "DOWN", "SIDEWAYS", "MIXED", "NO_EDGE", "UNAVAILABLE"}
POSITIVE = {"UP"}
NEGATIVE = {"DOWN"}
NEUTRAL = {"SIDEWAYS", "MIXED", "NO_EDGE", "UNAVAILABLE"}


def canon(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canon(value)).hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_direction(value: Any) -> str:
    value = str(value or "UNAVAILABLE").upper()
    return value if value in VALID_DIRECTIONS else "UNAVAILABLE"


def official_horizon(compass: Mapping[str, Any], key: str) -> dict[str, Any]:
    """Read existing horizons; never turn observed 12h momentum into a forecast.

    The original frozen 12h sign remains available only as a descriptive
    nowcast field under its explicit v4.1 marker. Legacy markerless freezes
    are NOT presumed to be modern, verified forward predictions either.
    """
    horizons = compass.get("horizons")
    horizons = horizons if isinstance(horizons, Mapping) else {}
    row = horizons.get(key)
    row = row if isinstance(row, Mapping) else {}
    if key == "NEXT_12H":
        nowcast = (
            compass.get("decision_policy_version")
            == "2026-10-31_OBSERVED_MOMENTUM_SOURCE_SEPARATION_V4_1"
            and row.get("semantics") == "OBSERVED_MOMENTUM_NOT_FORECAST"
            and row.get("predictive_edge_status") == "NOT_PROVEN"
        )
        return {
            "direction": "UNAVAILABLE",
            "observed_momentum_direction": clean_direction(row.get("expected_direction")) if nowcast else "UNAVAILABLE",
            "semantics": "OBSERVED_MOMENTUM_NOT_FORECAST" if nowcast else "LEGACY_UNVERIFIED_NOT_FORWARD",
            "path": "Observed momentum only; no separately verified 12h forward forecast.",
            "action_posture": "NO_EDGE",
            "confidence": None,
            "eta": None,
        }
    return {
        "direction": clean_direction(row.get("expected_direction")),
        "path": row.get("expected_path"),
        "action_posture": row.get("action_posture"),
        "confidence": row.get("confidence"),
        "eta": row.get("eta"),
    }


def cn_projection(machine: Mapping[str, Any], key: str) -> dict[str, Any]:
    row = ((machine.get("decision_projection") or {}).get(key) or {})
    return dict(row) if isinstance(row, Mapping) else {}


def thesis_state(direction: str, source_status: str) -> str:
    if source_status in {"DEGRADED", "BLOCKED"} or direction == "UNAVAILABLE":
        return "DATA_DEGRADED"
    return "ON_TRACK"


def alignment_class(directions: list[str]) -> str:
    """Classify four governed forward horizons; observed 12h is never a vote.

    Input remains [12h, 72h, 168h, 21_30d, 4_8w] for source readback.
    Incomplete or unqualified forward evidence must not imply alignment.
    """
    if len(directions) != 5:
        return "MIXED_OR_NO_EDGE"
    forward = directions[1:]
    if any(x not in {"UP", "DOWN", "SIDEWAYS", "MIXED"} for x in forward):
        return "MIXED_OR_NO_EDGE"
    tactical = forward[:2]
    strategic = forward[2:]
    if all(x == "UP" for x in forward):
        return "FULL_BULL_ALIGNMENT"
    if any(x == "DOWN" for x in tactical) and any(x == "UP" for x in strategic):
        return "TACTICAL_PULLBACK_STRUCTURAL_BULL"
    if all(x == "DOWN" for x in forward):
        return "DISTRIBUTION_ALIGNMENT"
    if all(x == "DOWN" for x in tactical) and any(x in {"UP", "SIDEWAYS", "MIXED"} for x in strategic):
        return "TRANSITION_WARNING"
    return "MIXED_OR_NO_EDGE"



FORWARD_RANGE_PREFLIGHT = "COMPASS_14_21D_RANGE_PREFLIGHT_v1"
FORWARD_RANGE_AUTHORITY = {"public_issuance": False, "score_allowed": False, "portfolio_action": False}


def validate_forward_range_candidate(value: Any) -> dict[str, Any]:
    """Source-clock preflight ONLY for #1516's proposed 14/21D envelopes.

    No forecast generation, original source custody attestation, publication,
    scoring, public conversion or automation. Caller supplies the original
    source receipt; a syntactically valid source hash is NOT proof of custody.
    Existing <=7-day and 21-30D/4-8W forecasts are never rewritten.
    """
    def required(obj: Any, keys: set[str], where: str) -> Mapping[str, Any]:
        if not isinstance(obj, dict) or set(obj) != keys:
            raise ValueError(f"{where}_contract_invalid")
        return obj

    def stamp(value: Any, where: str) -> datetime:
        if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", value
        ):
            raise ValueError(f"{where}_utc_required")
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError(f"{where}_invalid") from exc

    def nonempty(value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    row = required(value, {
        "contract", "authority", "forecast_id", "forecast_week",
        "public_issue_number", "issued_at_utc", "source", "revision_of",
        "BTC", "ETH"
    }, "forward_range")
    if row["contract"] != FORWARD_RANGE_PREFLIGHT or row["authority"] != FORWARD_RANGE_AUTHORITY:
        raise ValueError("research_only_authority_required")
    if not nonempty(row["forecast_id"]) or type(row["public_issue_number"]) is not int or row["public_issue_number"] <= 0:
        raise ValueError("forecast_identity_invalid")
    if row["revision_of"] is not None:
        # Original issued receipt not supplied here; never overwrite the old call.
        raise ValueError("revision_requires_independently_attested_original")
    forecast_week = row["forecast_week"]
    if not isinstance(forecast_week, str) or not re.fullmatch(r"\d{4}-W\d{2}", forecast_week):
        raise ValueError("forecast_week_invalid")
    try:
        year, week = int(forecast_week[:4]), int(forecast_week[6:])
        monday = datetime.combine(date.fromisocalendar(year, week, 1),
                                  datetime.min.time(), timezone.utc)
    except ValueError as exc:
        raise ValueError("forecast_week_invalid") from exc

    issued = stamp(row["issued_at_utc"], "issued_at")
    first_interval = monday + timedelta(days=7)
    if not monday <= issued < first_interval:
        raise ValueError("late_or_preweek_issuance_not_original_monday_forecast")

    source = row["source"]
    if source is not None:
        source = required(source, {
            "owner", "source_contract_id", "sha256",
            "first_known_at_utc", "cutoff_utc"
        }, "source")
        if source["owner"] != "CYCLE_NAVIGATOR_WEEKLY" or not nonempty(source["source_contract_id"]):
            raise ValueError("unknown_source_owner")
        if not isinstance(source["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise ValueError("unbound_source_hash")
        first_known = stamp(source["first_known_at_utc"], "source_first_known")
        cutoff = stamp(source["cutoff_utc"], "source_cutoff")
        if not first_known <= cutoff <= issued:
            raise ValueError("source_known_after_cutoff_or_issuance")

    for asset in ("BTC", "ETH"):
        series = required(row[asset], {"windows"}, asset)
        windows = series["windows"]
        if not isinstance(windows, list) or len(windows) != 2:
            raise ValueError(f"{asset}_window_count_invalid")
        for ix, (label, days_a, days_b) in enumerate(
            (("D8_14", 7, 14), ("D15_21", 14, 21))
        ):
            bucket = required(windows[ix], {
                "window", "start_utc", "end_utc", "status",
                "low_usd", "high_usd", "reason"
            }, f"{asset}_{label}")
            if (bucket["window"] != label or
                stamp(bucket["start_utc"], "window_start") != monday + timedelta(days=days_a) or
                stamp(bucket["end_utc"], "window_end") != monday + timedelta(days=days_b)):
                raise ValueError(f"{asset}_{label}_clock_incorrect")
            if bucket["status"] == "CANDIDATE":
                if source is None:
                    raise ValueError("candidate_price_requires_original_source_receipt")
                lo, hi = bucket["low_usd"], bucket["high_usd"]
                if not all(
                    type(num) in (float, int) and math.isfinite(num) and num > 0
                    for num in (lo, hi)
                ) or not lo < hi or bucket["reason"] is not None:
                    raise ValueError(f"{asset}_{label}_invalid_price_band")
            elif bucket["status"] in ("UNAVAILABLE", "ABSTAIN"):
                if (bucket["low_usd"] is not None or bucket["high_usd"] is not None or
                    not nonempty(bucket["reason"])):
                    raise ValueError(f"{asset}_{label}_unavailable_requires_null_prices")
            else:
                raise ValueError(f"{asset}_{label}_unsupported_status")
    return value


def strict_object(raw: bytes) -> dict[str, Any]:
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("STRATEGIC_DUPLICATE_KEY")
            result[key] = value
        return result

    def reject_constant(_):
        raise ValueError("STRATEGIC_NONFINITE_JSON")

    def finite_float(value):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("STRATEGIC_NONFINITE_JSON")
        return parsed

    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                       parse_constant=reject_constant, parse_float=finite_float)
    if not isinstance(value, dict):
        raise ValueError("STRATEGIC_JSON_OBJECT_REQUIRED")
    return value


def bound_source_bytes(repo: Path, path: Path):
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(repo.resolve()):
        raise ValueError("STRATEGIC_SOURCE_PATH_INVALID")
    raw = path.read_bytes()
    return strict_object(raw), hashlib.sha256(raw).hexdigest()


def bound_official_source(repo: Path, optr: Mapping[str, Any]):
    if optr.get("contract") != "OFFICIAL_DAILY_COMPASS_LATEST_POINTER_v1":
        raise ValueError("STRATEGIC_OFFICIAL_POINTER_CONTRACT_INVALID")
    relative = optr.get("compass_path")
    if not isinstance(relative, str) or not re.fullmatch(
            r"04_MARKET_LEARNING/handlekompas/official/daily/\d{4}/\d{2}/\d{2}/CMP-[A-Za-z0-9-]+\.json", relative):
        raise ValueError("STRATEGIC_OFFICIAL_PATH_INVALID")
    path = repo / relative
    compass, raw_sha = bound_source_bytes(repo, path)
    official_digest = digest({k: v for k, v in compass.items() if k != "compass_sha256"})
    if (compass.get("contract") != "OFFICIAL_DAILY_COMPASS_v1"
            or not isinstance(compass.get("compass_id"), str)
            or path.stem != compass["compass_id"]
            or compass.get("compass_id") != optr.get("compass_id")
            or compass.get("issued_at_utc") != optr.get("issued_at_utc")
            or compass.get("compass_sha256") != official_digest
            or optr.get("compass_sha256") != official_digest):
        raise ValueError("STRATEGIC_OFFICIAL_SOURCE_BINDING_MISMATCH")
    if not isinstance(compass.get("horizons"), dict):
        raise ValueError("STRATEGIC_OFFICIAL_PROJECTION_INVALID")
    return path, compass, raw_sha


def bound_cn_source(repo: Path, cptr: Mapping[str, Any]):
    if cptr.get("contract") != "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1":
        raise ValueError("STRATEGIC_CN_POINTER_CONTRACT_INVALID")
    year, week = cptr.get("iso_year"), cptr.get("iso_week")
    if type(year) is not int or type(week) is not int:
        raise ValueError("STRATEGIC_SOURCE_WEEK_INVALID")
    try:
        datetime.fromisocalendar(year, week, 1)
    except ValueError:
        raise ValueError("STRATEGIC_SOURCE_WEEK_INVALID") from None
    relative = f"05_CYCLE_NAVIGATOR/weekly/{year}/W{week:02d}"
    if cptr.get("week_dir") != relative:
        raise ValueError("STRATEGIC_CN_WEEK_PATH_MISMATCH")
    path = repo / relative / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    cn, raw_sha = bound_source_bytes(repo, path)
    if (cn.get("contract") != "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1"
            or any(type(cptr.get(k)) is not int or cn.get(k) != cptr[k]
                   for k in ("issue_number", "public_issue_number"))
            or cn.get("status") != cptr.get("status")
            or raw_sha != cptr.get("machine_package_sha256")):
        raise ValueError("STRATEGIC_CN_SOURCE_BINDING_MISMATCH")
    if not isinstance(cn.get("decision_projection"), dict):
        raise ValueError("STRATEGIC_CN_PROJECTION_INVALID")
    return path, cn, raw_sha


def build_anchor(repo: Path, now: datetime) -> dict[str, Any]:
    official_ptr_path = repo / OFFICIAL_PTR
    cn_ptr_path = repo / CN_PTR
    optr, cptr = {}, {}
    pointer_hashes = {}
    failures = {}
    # Read each pointer independently so an invalid Official pointer cannot
    # hide the intended CN package identity from the degraded receipt.
    for name, path in (("official", official_ptr_path), ("cn", cn_ptr_path)):
        try:
            if path.is_symlink() or not path.resolve().is_relative_to(repo.resolve()):
                raise ValueError("STRATEGIC_SOURCE_PATH_INVALID")
            raw = path.read_bytes()
            pointer_hashes[name] = hashlib.sha256(raw).hexdigest()
            obj = strict_object(raw)
            if name == "official":
                optr = obj
            else:
                cptr = obj
        except (OSError, ValueError, RecursionError):
            failures[name] = "STRATEGIC_POINTER_UNREADABLE"
    expected_cn_sha = cptr.get("machine_package_sha256")
    if not isinstance(expected_cn_sha, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_cn_sha):
        expected_cn_sha = None
    compass_path = cn_machine_path = None
    compass, cn = {}, {}
    official_raw_sha = cn_raw_sha = None
    # Each source owns its own horizons. Official outages must not invalidate
    # independently verified CN bytes or abort weekly CN publication.
    for name, pointer, bind in (("official", optr, bound_official_source),
                                ("cn", cptr, bound_cn_source)):
        if name in failures:
            continue
        try:
            path, payload, raw_sha = bind(repo, pointer)
            if name == "official":
                compass_path, compass, official_raw_sha = path, payload, raw_sha
            else:
                cn_machine_path, cn, cn_raw_sha = path, payload, raw_sha
        except (OSError, ValueError, RecursionError) as exc:
            code = str(exc)
            failures[name] = code if re.fullmatch(r"STRATEGIC_[A-Z_]+", code) else "STRATEGIC_SOURCE_UNREADABLE"
    reason = failures.get("official") or failures.get("cn")
    binding_status = "DEGRADED" if failures else "VERIFIED"

    tactical = {
        "12h": official_horizon(compass, "NEXT_12H"),
        "72h": official_horizon(compass, "NEXT_1_3D"),
        "168h": official_horizon(compass, "NEXT_5_7D"),
    }

    # 21-30D must be explicitly produced by the weekly CN decision projection.
    # Never stretch NEXT_2_3W into a month forecast.
    month = cn_projection(cn, "next_21_30d")
    month_direction = clean_direction(month.get("direction"))
    if not month:
        month = {
            "direction": "UNAVAILABLE",
            "summary": "No prospectively governed 21-30D decision projection exists in this Cycle Navigator package.",
            "regime_destination": "UNAVAILABLE",
            "expected_path": "UNAVAILABLE",
            "action_posture": "NO_EDGE",
            "falsification": [],
            "confidence": None,
        }
        month_direction = "UNAVAILABLE"

    cycle = cn_projection(cn, "weeks_4_8")
    cycle_direction = clean_direction(cycle.get("direction"))
    if not cycle:
        cycle = {
            "direction": "UNAVAILABLE",
            "summary": "No eligible Cycle Navigator 4-8W projection exists.",
            "state": "UNCLEAR",
            "action_posture": "UNAVAILABLE",
            "warning": "SOURCE_MISSING",
        }
        cycle_direction = "UNAVAILABLE"

    directions = [
        tactical["12h"]["direction"],
        tactical["72h"]["direction"],
        tactical["168h"]["direction"],
        month_direction,
        cycle_direction,
    ]
    source_fingerprint = digest({
        "official_compass_sha256": official_raw_sha,
        "cn_machine_package_sha256": expected_cn_sha,
        "cn_verified_raw_sha256": cn_raw_sha,
        "pointer_hashes": pointer_hashes,
        "binding_status": binding_status,
        "reason_code": reason,
        "scoring_contract": SCORING_CONTRACT,
    })
    anchor_id = "SC-" + now.strftime("%Y%m%d") + "-" + source_fingerprint[:12]

    result = {
        "contract": CONTRACT,
        "scoring_contract": SCORING_CONTRACT,
        "anchor_id": anchor_id,
        "issued_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_fingerprint": source_fingerprint,
        "source_binding_status": binding_status,
        "source_binding_reason_code": reason,
        "market_reference": compass.get("market_reference"),
        "tactical_context": tactical,
        "strategic_21_30d": {
            **month,
            "direction": month_direction,
            "btc_direction": clean_direction(month.get("btc_direction")),
            "eth_direction": clean_direction(month.get("eth_direction")),
            "ethbtc_direction": clean_direction(month.get("ethbtc_direction")),
            "thesis_state": thesis_state(month_direction, str(cn.get("status") or "UNKNOWN")),
            "source_owner": "CYCLE_NAVIGATOR_DECISION_PROJECTION",
            "derived_from_2_3w": False,
        },
        "cycle_4_8w": {
            **cycle,
            "direction": cycle_direction,
            "thesis_state": thesis_state(cycle_direction, str(cn.get("status") or "UNKNOWN")),
            "source_owner": "CYCLE_NAVIGATOR",
            "parallel_engine": False,
        },
        "cross_horizon_alignment": {
            "directions": {
                "12h": directions[0],
                "72h": directions[1],
                "168h": directions[2],
                "21_30d": directions[3],
                "4_8w": directions[4],
            },
            "class": alignment_class(directions),
            "note": "Descriptive alignment only. Horizon disagreement is preserved and has no execution authority.",
        },
        "checkpoints": {
            "21_30d": ["T+7D", "T+14D", "T+21D", "T+30D"],
            "4_8w": ["T+14D", "T+28D", "T+42D", "T+56D"],
        },
        "source_bindings": {
            "official_compass": {
                "path": str(compass_path.relative_to(repo)) if compass_path is not None else None,
                "sha256": official_raw_sha,
                "compass_id": compass.get("compass_id"),
            },
            "cycle_navigator": {
                "path": str(cn_machine_path.relative_to(repo)) if cn_machine_path is not None else None,
                "expected_package_sha256": expected_cn_sha,
                "sha256": cn_raw_sha,
                "issue_number": cn.get("issue_number"),
                "public_issue_number": cn.get("public_issue_number"),
                "iso_year": cptr.get("iso_year") if type(cptr.get("iso_year")) is int else None,
                "iso_week": cptr.get("iso_week") if type(cptr.get("iso_week")) is int else None,
            },
        },
        "authority": {
            "classification": "OFFICIAL_NAVIGATION_OUTPUT",
            "portfolio_execution": False,
            "source_override": False,
            "forecast_rewrite": False,
            "market_threshold_change": False,
            "model_weight_change": False,
        },
    }
    result["anchor_sha256"] = digest({k: v for k, v in result.items() if k != "anchor_sha256"})
    return result


def anchor_pointer(repo: Path, out: Path, anchor: Mapping[str, Any]) -> dict[str, Any]:
    pointer = {
        "contract": "STRATEGIC_COMPASS_LATEST_POINTER_v1",
        "anchor_id": anchor["anchor_id"],
        "anchor_path": str(out.relative_to(repo)),
        "anchor_sha256": anchor["anchor_sha256"],
        "source_fingerprint": anchor["source_fingerprint"],
        "source_binding_status": anchor["source_binding_status"],
        "source_binding_reason_code": anchor["source_binding_reason_code"],
        "cn_expected_package_sha256": anchor["source_bindings"]["cycle_navigator"]["expected_package_sha256"],
        "issued_at_utc": anchor["issued_at_utc"],
        "alignment_class": anchor["cross_horizon_alignment"]["class"],
        "strategic_21_30d_direction": anchor["strategic_21_30d"]["direction"],
        "cycle_4_8w_direction": anchor["cycle_4_8w"]["direction"],
    }
    return pointer


def verified_existing_anchor(repo: Path, path: Path, candidate: Mapping[str, Any], now: datetime) -> dict[str, Any]:
    """Reconcile immutable bytes with the freshly verified source projection.

    A self-digest alone cannot detect a coherently rehashed modification.
    Preserve the original issue clock, but rederive every other field.
    """
    if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(repo):
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_PATH_INVALID")
    raw = path.read_bytes()
    existing = strict_object(raw)
    stamp = existing.get("issued_at_utc")
    if not isinstance(stamp, str) or not stamp.endswith("Z"):
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_CLOCK_INVALID")
    try:
        issued = datetime.fromisoformat(stamp[:-1] + "+00:00")
    except ValueError:
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_CLOCK_INVALID") from None
    if issued > now or stamp != issued.isoformat().replace("+00:00", "Z"):
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_CLOCK_INVALID")
    expected = dict(candidate)
    expected["issued_at_utc"] = stamp
    expected["anchor_id"] = "SC-" + issued.strftime("%Y%m%d") + "-" + candidate["source_fingerprint"][:12]
    expected["anchor_sha256"] = digest({k: v for k, v in expected.items() if k != "anchor_sha256"})
    expected_path = repo / ROOT / "anchors" / issued.strftime("%Y/%m/%d") / f"{expected['anchor_id']}.json"
    if path != expected_path or raw != canon(expected):
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_INTEGRITY_FAILURE")
    return existing


def materialize(repo: Path, now: datetime | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    now = (now or datetime.now(timezone.utc).replace(microsecond=0)).astimezone(timezone.utc)
    anchor = build_anchor(repo, now)
    latest_path = repo / ROOT / "LATEST_STRATEGIC_COMPASS.json"
    if latest_path.is_symlink() or not latest_path.resolve().is_relative_to(repo):
        raise ValueError("STRATEGIC_LATEST_POINTER_PATH_INVALID")
    if latest_path.exists():
        latest = strict_object(latest_path.read_bytes())
        if latest.get("source_fingerprint") == anchor["source_fingerprint"]:
            rel = latest.get("anchor_path")
            if not isinstance(rel, str) or not re.fullmatch(
                    r"04_MARKET_LEARNING/handlekompas/strategic/anchors/\d{4}/\d{2}/\d{2}/SC-\d{8}-[0-9a-f]{12}\.json", rel):
                raise ValueError("STRATEGIC_EXISTING_ANCHOR_PATH_INVALID")
            out = repo / rel
            existing = verified_existing_anchor(repo, out, anchor, now)
            if latest != anchor_pointer(repo, out, existing):
                raise ValueError("STRATEGIC_LATEST_POINTER_INTEGRITY_FAILURE")
            return {"status": "DEGRADED" if anchor["source_binding_status"] == "DEGRADED" else "NOOP_SAME_SOURCES",
                    "write_status": "NOOP_SAME_SOURCES", "anchor_id": existing["anchor_id"],
                    "source_fingerprint": anchor["source_fingerprint"],
                    "source_binding_status": anchor["source_binding_status"],
                    "source_binding_reason_code": anchor["source_binding_reason_code"]}

    out = repo / ROOT / "anchors" / now.strftime("%Y/%m/%d") / f"{anchor['anchor_id']}.json"
    if out.is_symlink() or not out.resolve().is_relative_to(repo):
        raise ValueError("STRATEGIC_EXISTING_ANCHOR_PATH_INVALID")
    out.parent.mkdir(parents=True, exist_ok=True)
    # Recovery may return to a previously issued source fingerprint on the
    # same UTC day. Preserve the original anchor bytes and issue timestamp.
    try:
        with out.open("xb") as handle:
            handle.write(canon(anchor))
    except FileExistsError:
        anchor = verified_existing_anchor(repo, out, anchor, now)
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    pointer = anchor_pointer(repo, out, anchor)
    latest_path.write_bytes(canon(pointer))
    return {"status": "DEGRADED" if anchor["source_binding_status"] == "DEGRADED" else "CREATED",
            "write_status": "CREATED", **pointer}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path.cwd())
    ap.add_argument("--now-utc")
    args = ap.parse_args()
    now = datetime.fromisoformat(args.now_utc.replace("Z", "+00:00")) if args.now_utc else None
    if now is not None and now.utcoffset() is None:
        now = now.replace(tzinfo=timezone.utc)
    print(json.dumps(materialize(args.repo_root, now), sort_keys=True))


if __name__ == "__main__":
    main()
