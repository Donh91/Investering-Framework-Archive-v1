#!/usr/bin/env python3
"""Build the first-class COMPLETE KOMPAS readback from already-pinned framework state.

The native Handlekompas remains the conservative action owner. This layer adds
explicit horizons, direction, the BTC→microcap capital ladder, point-in-time
provenance and one immutable Copenhagen-day benchmark for later outcome review.
It has no trade-execution or canonical-forecast authority.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Mapping
from zoneinfo import ZoneInfo

CONTRACT = "COMPLETE_KOMPAS_v1"
POINTER_CONTRACT = "COMPLETE_KOMPAS_LATEST_POINTER_v1"
DAILY_CONTRACT = "COMPLETE_KOMPAS_DAILY_FREEZE_v1"
DAILY_POINTER_CONTRACT = "COMPLETE_KOMPAS_DAILY_LATEST_POINTER_v1"
COPENHAGEN = ZoneInfo("Europe/Copenhagen")

NATIVE_POINTER = Path("04_MARKET_LEARNING/handlekompas/LATEST.json")
AUTO_POINTER = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/LATEST.json")
DAILY_CAPTURE_POINTER = Path("03_DAILY_CAPTURE_LOGS/captures/LATEST.json")
CN_POINTER = Path("05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json")
OUTPUT_ROOT = Path("04_MARKET_LEARNING/handlekompas")

AUTHORITY = {
    "binding": False,
    "portfolio_execution": False,
    "canonical_forecast_mutation": False,
    "threshold_or_weight_change": False,
    "proxy_promotion": False,
    "historical_rewrite": False,
    "purpose": "POINT_IN_TIME_ACTION_COMPASS_AND_RETROSPECTIVE_LEARNING_INPUT",
}


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def finite(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    out = float(value)
    return out if math.isfinite(out) else None


def nested(value: Any, *keys: str) -> Any:
    for key in keys:
        if not isinstance(value, Mapping):
            return None
        value = value.get(key)
    return value


def numeric_leaf_count(value: Any) -> int:
    if isinstance(value, bool):
        return 0
    if isinstance(value, (int, float)):
        return int(math.isfinite(float(value)))
    if isinstance(value, Mapping):
        return sum(numeric_leaf_count(v) for v in value.values())
    if isinstance(value, list):
        return sum(numeric_leaf_count(v) for v in value)
    return 0


def bound_packet(root: Path, pointer_rel: Path, path_key: str, hash_key: str) -> tuple[dict[str, Any], str, str]:
    pointer = read_json(root / pointer_rel)
    rel = str(pointer.get(path_key) or "")
    if not rel or ".." in rel:
        raise ValueError(f"BAD_POINTER_PATH:{pointer_rel}")
    path = root / rel
    raw = path.read_bytes()
    packet = json.loads(raw)
    expected = pointer.get(hash_key)
    actual = packet.get(hash_key) if hash_key in packet else sha256_bytes(raw)
    if expected and expected != actual and expected != sha256_bytes(raw):
        raise ValueError(f"POINTER_HASH_MISMATCH:{pointer_rel}")
    return packet, rel, sha256_bytes(raw)


def load_sources(root: Path) -> dict[str, Any]:
    native, native_rel, native_file_sha = bound_packet(root, NATIVE_POINTER, "handlekompas_path", "handlekompas_sha256")
    auto, auto_rel, auto_file_sha = bound_packet(root, AUTO_POINTER, "packet_path", "packet_sha256")

    capture_pointer = read_json(root / DAILY_CAPTURE_POINTER)
    capture_rel = str(capture_pointer.get("path") or "")
    capture_path = root / "03_DAILY_CAPTURE_LOGS" / capture_rel
    capture_raw = capture_path.read_bytes()
    capture = json.loads(capture_raw)

    cn_pointer = read_json(root / CN_POINTER)
    week_dir = str(cn_pointer.get("week_dir") or "")
    if not week_dir.startswith("05_CYCLE_NAVIGATOR/weekly/") or ".." in week_dir:
        raise ValueError("CN_POINTER_BAD_WEEK_DIR")
    cn_path = root / week_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json"
    cn_raw = cn_path.read_bytes()
    cn = json.loads(cn_raw)
    expected_cn_sha = cn_pointer.get("machine_package_sha256")
    if expected_cn_sha and sha256_bytes(cn_raw) != expected_cn_sha:
        raise ValueError("CN_MACHINE_PACKAGE_HASH_MISMATCH")

    return {
        "native": native,
        "native_path": native_rel,
        "native_file_sha256": native_file_sha,
        "auto": auto,
        "auto_path": auto_rel,
        "auto_file_sha256": auto_file_sha,
        "capture": capture,
        "capture_path": f"03_DAILY_CAPTURE_LOGS/{capture_rel}",
        "capture_sha256": sha256_bytes(capture_raw),
        "cn": cn,
        "cn_path": f"{week_dir}/CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",
        "cn_sha256": sha256_bytes(cn_raw),
    }


def breadth_context(auto: Mapping[str, Any]) -> dict[str, Any]:
    canonical_ratio = finite(nested(auto, "normalized_state", "breadth", "aggregate", "advance_ratio"))
    if canonical_ratio is not None:
        return {"advance_ratio": canonical_ratio, "role": "CANONICAL_COMPATIBLE", "constituent_count": None, "membership_hash": None}
    proxy = nested(auto, "normalized_state", "live_anchor_breadth_reference") or {}
    adv = finite(proxy.get("advancers"))
    count = finite(proxy.get("constituent_count"))
    ratio = (adv / count) if adv is not None and count and count > 0 else None
    return {
        "advance_ratio": ratio,
        "role": "PROXY_ONLY_DEFENSIVE_USE_ALLOWED" if ratio is not None else "UNAVAILABLE",
        "constituent_count": int(count) if count is not None else None,
        "membership_hash": proxy.get("membership_hash"),
    }


def altseason_score(auto: Mapping[str, Any], horizon: str) -> float | None:
    return finite(nested(auto, "normalized_state", "altseason_context", "blockchaincenter_altcoin_season", "horizons", horizon, "published_score"))


def snapshot(auto: Mapping[str, Any]) -> dict[str, Any]:
    ns = auto.get("normalized_state") or {}
    live = ns.get("live_market") or {}
    settled = ns.get("settled_etf") or {}
    stable = ns.get("stablecoin_liquidity") or {}
    sentiment = nested(ns, "sentiment", "cfgi", "symbols") or {}
    breadth = breadth_context(auto)
    return {
        "btc_usdt": finite(live.get("btc_usdt")),
        "eth_usdt": finite(live.get("eth_usdt")),
        "ethbtc": finite(live.get("ethbtc")),
        "breadth_advance_ratio": breadth["advance_ratio"],
        "breadth_role": breadth["role"],
        "breadth_constituent_count": breadth["constituent_count"],
        "btc_etf_musd": finite(settled.get("btc_reported_total_musd")),
        "eth_etf_musd": finite(settled.get("eth_reported_total_musd")),
        "stablecoin_change_1d_pct": finite(stable.get("change_1d_pct")),
        "cfgi_market": finite(nested(sentiment, "MARKET", "score")),
        "cfgi_btc": finite(nested(sentiment, "BTC", "score")),
        "cfgi_eth": finite(nested(sentiment, "ETH", "score")),
        "altseason_30d": altseason_score(auto, "30"),
        "altseason_90d": altseason_score(auto, "90"),
        "altseason_365d": altseason_score(auto, "365"),
    }


def directional_bias(market: Mapping[str, Any], degraded: bool) -> dict[str, Any]:
    votes: list[dict[str, Any]] = []

    def vote(name: str, value: float | None, polarity: int | None, note: str) -> None:
        if value is not None and polarity is not None:
            votes.append({"signal": name, "value": value, "vote": polarity, "note": note})

    b = finite(market.get("breadth_advance_ratio"))
    vote("breadth", b, -1 if b is not None and b < .40 else (1 if b is not None and b >= .50 else 0), "advancer share")
    for key in ("btc_etf_musd", "eth_etf_musd", "stablecoin_change_1d_pct"):
        v = finite(market.get(key))
        vote(key, v, -1 if v is not None and v < 0 else (1 if v is not None and v > 0 else 0), "flow/liquidity sign")
    mood = finite(market.get("cfgi_market"))
    vote("cfgi_market", mood, -1 if mood is not None and mood < 45 else (1 if mood is not None and mood >= 55 else 0), "market sentiment")

    score = sum(int(row["vote"]) for row in votes)
    negatives = sum(1 for row in votes if row["vote"] < 0)
    positives = sum(1 for row in votes if row["vote"] > 0)
    if negatives >= 3 and score <= -2:
        direction = "BEARISH"
    elif positives >= 3 and score >= 2:
        direction = "BULLISH"
    else:
        direction = "MIXED_NEUTRAL"
    confidence = "LOW" if degraded or str(market.get("breadth_role", "")).startswith("PROXY") else "MEDIUM"
    return {"direction": direction, "confidence": confidence, "vote_score": score, "positive_votes": positives, "negative_votes": negatives, "signals": votes}


def broad_altseason_status(cn: Mapping[str, Any]) -> str:
    for row in cn.get("altseason_countdown") or []:
        if "broad altseason" in str(row.get("phase", "")).lower():
            text = str(row.get("phase", "")).upper()
            for state in ("PAUSED", "INACTIVE", "ACTIVE WATCH", "ACTIVE", "UNCONFIRMED"):
                if state in text:
                    return state
    return "UNCONFIRMED"


def complete_compass(native: Mapping[str, Any], auto: Mapping[str, Any], cn: Mapping[str, Any]) -> dict[str, Any]:
    market = snapshot(auto)
    degraded = str(auto.get("decision_context_status") or "").upper() != "PASS" or bool(auto.get("blockers"))
    near = directional_bias(market, degraded)
    now = str(nested(native, "action", "NOW") or "HOLD_WAIT")
    weekly = str(cn.get("market_state") or cn.get("base_case_this_week") or "")
    weekly_l = weekly.lower()

    if "GRADUATED_TOPUP_ACTIVE" in now:
        action_1_3d = "SELECTIVE_TOPUP_ACTIVE"
    elif "PREPARE" in now:
        action_1_3d = "PREPARE_FOR_SELECTIVE_RISK"
    else:
        action_1_3d = "WAIT_FOR_CONFIRMATION"

    if near["direction"] == "BEARISH":
        dir_12h = "BEARISH_BIAS"
        dir_1_3d = "BEARISH_TO_NEUTRAL"
    elif near["direction"] == "BULLISH":
        dir_12h = "BULLISH_BIAS"
        dir_1_3d = "BULLISH_IF_CONFIRMATION_PERSISTS"
    else:
        dir_12h = "NEUTRAL_VOLATILE"
        dir_1_3d = "NEUTRAL_WAIT_FOR_BREAK"
    dir_5_7d = "NEUTRAL_TO_BEARISH" if ("pullback" in weekly_l or "volatile consolidation" in weekly_l) and near["direction"] == "BEARISH" else "NEUTRAL_VOLATILE"

    b = market.get("breadth_advance_ratio")
    ethbtc = market.get("ethbtc")
    confirmation = "ETH/BTC stabilizes or rises, participation broadens materially, and data health improves."
    invalidation = "Breadth stays weak or deteriorates, ETH/BTC weakens further, or market/data stress increases."

    lanes = {
        "lane1": {"horizon": "NEXT_12H", "direction": dir_12h, "confidence": near["confidence"], "action": now, "summary": "Defend capital and require a reclaim/participation improvement before adding risk." if "BEARISH" in dir_12h else "Hold current posture and watch the next confirmation cycle.", "confirmation": confirmation, "invalidation": invalidation},
        "lane2": {"horizon": "NEXT_1_3D", "direction": dir_1_3d, "confidence": near["confidence"], "action": action_1_3d, "summary": "Do not broaden alt exposure until ETH-relative strength and breadth confirm together.", "confirmation": confirmation, "invalidation": invalidation},
        "lane3": {"horizon": "NEXT_5_7D", "direction": dir_5_7d, "confidence": "MEDIUM_LOW" if degraded else "MEDIUM", "action": "WAIT_FOR_WEEKLY_TRANSMISSION", "summary": str(cn.get("base_case_this_week") or "Keep the weekly cycle map unchanged until its gates resolve."), "confirmation": "Weekly transmission progresses BTC → ETH → large caps → midcaps with persistent breadth.", "invalidation": "Weekly pullback/degradation deepens or transmission fails."},
    }

    ladder = [
        {"segment": "BTC", "posture": "HOLD_CORE_DEFENSIVE" if near["direction"] == "BEARISH" else "HOLD_CORE", "eta": "NOW / reassess within 12h", "eta_explanation": "BTC remains the liquidity anchor; new risk waits for short-horizon stabilization."},
        {"segment": "ETH", "posture": "HOLD_RELATIVE_WATCH", "eta": "12–48h", "eta_explanation": "ETH needs to stop losing relative strength versus BTC before rotation can progress."},
        {"segment": "LARGE_CAPS", "posture": "WAIT_PREPARE" if "PREPARE" in now else "WAIT", "eta": "1–3d earliest", "eta_explanation": "Large caps are first eligible after ETH/BTC and breadth confirm together."},
        {"segment": "MIDCAPS", "posture": "WAIT", "eta": "5–7d earliest / otherwise >7d", "eta_explanation": "Requires persistent breadth and large-cap leadership that survives pullbacks."},
        {"segment": "SMALL_CAPS", "posture": "HARD_WAIT", "eta": ">7d / after midcap confirmation", "eta_explanation": "Small caps should not lead the risk curve while midcap transmission is unconfirmed."},
        {"segment": "MICROCAPS", "posture": "HARD_WAIT", "eta": ">7d / last in sequence", "eta_explanation": "Microcaps are the final risk tier and require broad speculative expansion, not an isolated bounce."},
    ]

    alt_status = {
        "broad_altseason": broad_altseason_status(cn),
        "blockchaincenter_30d": market.get("altseason_30d"),
        "blockchaincenter_90d": market.get("altseason_90d"),
        "status": "DEFENSIVE_SELECTIVITY" if (b is not None and b < .40) else "SELECTIVE_WATCH",
        "note": "Altcoin status is derived from the same BTC→microcap ladder; no duplicate altcoin engine is created.",
    }
    conclusion = {
        "now": f"Market bias is {near['direction']} at this point in time; action is {now}.",
        "next_12h": f"{dir_12h}: watch whether ETH/BTC ({ethbtc if ethbtc is not None else 'n/a'}) and breadth ({round(b*100,1) if b is not None else 'n/a'}%) stabilize before adding risk.",
        "next_1_3d": f"{dir_1_3d}: {action_1_3d}; large caps are the first alt tier that can move from WAIT if confirmation arrives.",
        "next_5_7d": f"{dir_5_7d}: weekly path remains conditional; mid/small/micro stay behind the breadth/transmission gate.",
    }
    return {"market_snapshot": market, "direction_evidence": near, "lanes": lanes, "capital_ladder": ladder, "altcoin_status": alt_status, "conclusion": conclusion}


def evidence_manifest(sources: Mapping[str, Any]) -> dict[str, Any]:
    auto = sources["auto"]
    capture = sources["capture"]
    breadth = breadth_context(auto)
    return {
        "semantics": "POINT_IN_TIME_MULTI_SOURCE_FEATURE_MANIFEST_NOT_A_FIXED_100_FIELD_SCORE",
        "auto_market_state": {"path": sources["auto_path"], "packet_sha256": auto.get("packet_sha256"), "file_sha256": sources["auto_file_sha256"], "numeric_leaf_count": numeric_leaf_count(auto)},
        "daily_capture": {"path": sources["capture_path"], "sha256": sources["capture_sha256"], "captured_at_utc": capture.get("captured_at_utc"), "numeric_leaf_count": numeric_leaf_count(capture)},
        "breadth_universe": {"constituent_count": breadth["constituent_count"], "membership_hash": breadth["membership_hash"], "role": breadth["role"]},
        "cycle_navigator": {"path": sources["cn_path"], "sha256": sources["cn_sha256"], "issue_number": sources["cn"].get("issue_number")},
        "native_handlekompas": {"path": sources["native_path"], "sha256": sources["native"].get("handlekompas_sha256")},
    }


def build(root: Path, now: datetime | None = None) -> dict[str, Any]:
    sources = load_sources(root)
    generated = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).replace(microsecond=0)
    complete = complete_compass(sources["native"], sources["auto"], sources["cn"])
    packet = {
        "contract": CONTRACT,
        "generated_at_utc": generated.isoformat().replace("+00:00", "Z"),
        "native_handlekompas_sha256": sources["native"].get("handlekompas_sha256"),
        "source_auto_market_state_sha256": sources["auto"].get("packet_sha256"),
        "action": sources["native"].get("action"),
        **complete,
        "evidence_manifest": evidence_manifest(sources),
        "data_health": {"status": sources["auto"].get("validation_status"), "decision_context_status": sources["auto"].get("decision_context_status"), "blockers": list(sources["auto"].get("blockers") or [])},
        "authority": AUTHORITY,
    }
    packet["kompas_sha256"] = sha256_bytes(canonical({k: v for k, v in packet.items() if k != "kompas_sha256"}))
    return packet


def daily_freeze(packet: Mapping[str, Any]) -> dict[str, Any]:
    generated = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    due = {
        "12h": (generated + timedelta(hours=12)).isoformat().replace("+00:00", "Z"),
        "1_3d": (generated + timedelta(days=3)).isoformat().replace("+00:00", "Z"),
        "5_7d": (generated + timedelta(days=7)).isoformat().replace("+00:00", "Z"),
    }
    freeze = {
        "contract": DAILY_CONTRACT,
        "local_date": generated.astimezone(COPENHAGEN).date().isoformat(),
        "frozen_at_utc": packet["generated_at_utc"],
        "source_kompas_sha256": packet["kompas_sha256"],
        "evaluation_due_utc": due,
        "evaluation_dimensions": ["DIRECTION_BY_HORIZON", "ACTION_POSTURE_UTILITY", "ETHBTC_RELATIVE_STRENGTH", "BREADTH_AND_PARTICIPATION", "CAP_TIER_TRANSMISSION", "ALTSEASON_STATE", "DRAWDOWN_AVOIDANCE_VS_FOREGONE_UPSIDE"],
        "hindsight_policy": "IMMUTABLE_FORECAST; OUTCOMES_APPEND_SEPARATELY; NEVER_REWRITE_THIS_FREEZE",
        "evidence_manifest": packet["evidence_manifest"],
        "kompas": packet,
    }
    freeze["daily_freeze_sha256"] = sha256_bytes(canonical({k: v for k, v in freeze.items() if k != "daily_freeze_sha256"}))
    return freeze


def write(packet: Mapping[str, Any], root: Path) -> dict[str, Any]:
    out = root / OUTPUT_ROOT
    generated = datetime.fromisoformat(str(packet["generated_at_utc"]).replace("Z", "+00:00"))
    run = out / "complete" / "runs" / generated.strftime("%Y/%m/%d") / f"{generated:%H%M%S}_{packet['kompas_sha256'][:12]}.json"
    run.parent.mkdir(parents=True, exist_ok=True)
    run.write_bytes(canonical(packet))
    latest = {"contract": POINTER_CONTRACT, "kompas_path": run.relative_to(root).as_posix(), "kompas_sha256": packet["kompas_sha256"], "generated_at_utc": packet["generated_at_utc"], "NOW": nested(packet, "action", "NOW"), "next_12h_direction": nested(packet, "lanes", "lane1", "direction"), "next_1_3d_direction": nested(packet, "lanes", "lane2", "direction"), "next_5_7d_direction": nested(packet, "lanes", "lane3", "direction"), "authority": AUTHORITY}
    (out / "COMPLETE_LATEST.json").write_bytes(canonical(latest))

    local = generated.astimezone(COPENHAGEN)
    freeze_status = "NOT_DUE"
    daily_path = None
    if local.hour >= 12:
        target = out / "daily" / local.strftime("%Y/%m") / f"{local.date().isoformat()}.json"
        daily_path = target.relative_to(root).as_posix()
        if target.exists():
            freeze_status = "ALREADY_FROZEN"
        else:
            freeze = daily_freeze(packet)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(canonical(freeze))
            dp = {"contract": DAILY_POINTER_CONTRACT, "local_date": freeze["local_date"], "daily_freeze_path": daily_path, "daily_freeze_sha256": freeze["daily_freeze_sha256"], "source_kompas_sha256": packet["kompas_sha256"], "frozen_at_utc": freeze["frozen_at_utc"], "evaluation_due_utc": freeze["evaluation_due_utc"]}
            (out / "DAILY_LATEST.json").write_bytes(canonical(dp))
            freeze_status = "FROZEN"
    return {"kompas_path": run.relative_to(root).as_posix(), "kompas_sha256": packet["kompas_sha256"], "daily_freeze_status": freeze_status, "daily_freeze_path": daily_path}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--no-write", action="store_true")
    args = p.parse_args()
    packet = build(args.repo_root)
    result = packet if args.no_write else {**write(packet, args.repo_root), "NOW": nested(packet, "action", "NOW"), "NEXT_12H": nested(packet, "lanes", "lane1", "direction"), "NEXT_1_3D": nested(packet, "lanes", "lane2", "direction"), "NEXT_5_7D": nested(packet, "lanes", "lane3", "direction")}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
