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
from datetime import datetime, timezone
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
    row = ((compass.get("horizons") or {}).get(key) or {})
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
    tactical = directions[:3]
    strategic = directions[3:]
    if all(x == "UP" for x in directions):
        return "FULL_BULL_ALIGNMENT"
    if any(x == "DOWN" for x in tactical[:2]) and any(x == "UP" for x in strategic):
        return "TACTICAL_PULLBACK_STRUCTURAL_BULL"
    if all(x == "DOWN" for x in directions):
        return "DISTRIBUTION_ALIGNMENT"
    if all(x == "DOWN" for x in tactical) and any(x in {"UP", "SIDEWAYS", "MIXED"} for x in strategic):
        return "TRANSITION_WARNING"
    return "MIXED_OR_NO_EDGE"


def build_anchor(repo: Path, now: datetime) -> dict[str, Any]:
    official_ptr_path = repo / OFFICIAL_PTR
    cn_ptr_path = repo / CN_PTR
    if not official_ptr_path.exists() or not cn_ptr_path.exists():
        raise SystemExit("required_pointer_missing")

    optr = read_json(official_ptr_path)
    cptr = read_json(cn_ptr_path)
    compass_path = repo / str(optr.get("compass_path") or "")
    cn_dir = repo / str(cptr.get("week_dir") or "")
    cn_machine_path = cn_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    if not compass_path.exists() or not cn_machine_path.exists():
        raise SystemExit("bound_source_missing")

    compass = read_json(compass_path)
    cn = read_json(cn_machine_path)

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
        "official_compass_sha256": optr.get("compass_sha256"),
        "cn_machine_package_sha256": cptr.get("machine_package_sha256"),
        "scoring_contract": SCORING_CONTRACT,
    })
    anchor_id = "SC-" + now.strftime("%Y%m%d") + "-" + source_fingerprint[:12]

    result = {
        "contract": CONTRACT,
        "scoring_contract": SCORING_CONTRACT,
        "anchor_id": anchor_id,
        "issued_at_utc": now.isoformat().replace("+00:00", "Z"),
        "source_fingerprint": source_fingerprint,
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
                "path": str(compass_path.relative_to(repo)),
                "sha256": file_sha(compass_path),
                "compass_id": compass.get("compass_id"),
            },
            "cycle_navigator": {
                "path": str(cn_machine_path.relative_to(repo)),
                "sha256": file_sha(cn_machine_path),
                "issue_number": cn.get("issue_number"),
                "public_issue_number": cn.get("public_issue_number"),
                "iso_year": cptr.get("iso_year"),
                "iso_week": cptr.get("iso_week"),
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


def materialize(repo: Path, now: datetime | None = None) -> dict[str, Any]:
    repo = repo.resolve()
    now = (now or datetime.now(timezone.utc).replace(microsecond=0)).astimezone(timezone.utc)
    anchor = build_anchor(repo, now)
    latest_path = repo / ROOT / "LATEST_STRATEGIC_COMPASS.json"
    if latest_path.exists():
        latest = read_json(latest_path)
        if latest.get("source_fingerprint") == anchor["source_fingerprint"]:
            return {"status": "NOOP_SAME_SOURCES", "anchor_id": latest.get("anchor_id"), "source_fingerprint": anchor["source_fingerprint"]}

    out = repo / ROOT / "anchors" / now.strftime("%Y/%m/%d") / f"{anchor['anchor_id']}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(canon(anchor))
    latest_path.parent.mkdir(parents=True, exist_ok=True)
    pointer = {
        "contract": "STRATEGIC_COMPASS_LATEST_POINTER_v1",
        "anchor_id": anchor["anchor_id"],
        "anchor_path": str(out.relative_to(repo)),
        "anchor_sha256": anchor["anchor_sha256"],
        "source_fingerprint": anchor["source_fingerprint"],
        "issued_at_utc": anchor["issued_at_utc"],
        "alignment_class": anchor["cross_horizon_alignment"]["class"],
        "strategic_21_30d_direction": anchor["strategic_21_30d"]["direction"],
        "cycle_4_8w_direction": anchor["cycle_4_8w"]["direction"],
    }
    latest_path.write_bytes(canon(pointer))
    return {"status": "CREATED", **pointer}


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
