from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FIELDS = ["score","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"]


def canon(v: Any) -> bytes:
    return (json.dumps(v, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha(v: Any) -> str:
    return hashlib.sha256(canon(v)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_capture_rows(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows = []
    for path in root.rglob("*.json"):
        try:
            value = read(path)
        except Exception:
            continue
        if value.get("contract") == "DAILY_RAW_CAPTURE_INDEX_v2":
            rows.append((path, value))
    rows.sort(key=lambda item: item[1].get("captured_at_utc", ""))
    return rows


def load_sidecars(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    rows = []
    for path in root.rglob("*.json"):
        try:
            value = read(path)
        except Exception:
            continue
        if value.get("contract") == "PDLT_OWNER_SIDECAR_v1":
            rows.append((path, value))
    rows.sort(key=lambda item: item[1].get("created_at_utc", ""))
    return rows


def cfgi_complete(sidecar: dict[str, Any] | None) -> bool:
    if not sidecar or sidecar.get("status") != "PASS":
        return False
    cfgi = sidecar.get("cfgi")
    if not isinstance(cfgi, dict):
        return False
    symbols = cfgi.get("symbols")
    if not isinstance(symbols, dict) or set(symbols) != {"MARKET", "BTC", "ETH"}:
        return False
    for symbol in symbols.values():
        values = symbol.get("values") if isinstance(symbol, dict) else None
        if not isinstance(values, dict) or any(values.get(field) is None for field in FIELDS):
            return False
    return True


def build_cfgi_sequence(sidecars: list[tuple[Path, dict[str, Any]]], cutoff: datetime, lookback_hours: int = 30) -> dict[str, Any] | None:
    eligible = []
    for path, row in sidecars:
        ts = parse_ts(row["created_at_utc"])
        age = (cutoff - ts).total_seconds() / 3600
        if 0 <= age <= lookback_hours and cfgi_complete(row):
            eligible.append((path, row))
    if not eligible:
        return None
    recent = eligible[-8:]
    points = []
    for path, row in recent:
        points.append({
            "path": str(path),
            "created_at_utc": row["created_at_utc"],
            "timeframe": row["cfgi"].get("timeframe"),
            "source_sha256": row["cfgi"].get("source_sha256"),
            "symbols": row["cfgi"]["symbols"],
        })
    deltas: dict[str, dict[str, float | None]] = {}
    if len(points) >= 2:
        prev = points[-2]["symbols"]
        curr = points[-1]["symbols"]
        for symbol in ("MARKET", "BTC", "ETH"):
            deltas[symbol] = {}
            for field in FIELDS:
                a = prev[symbol]["values"].get(field)
                b = curr[symbol]["values"].get(field)
                deltas[symbol][field] = float(b) - float(a) if isinstance(a, (int, float)) and isinstance(b, (int, float)) else None
    return {"points": points, "latest_deltas": deltas, "point_count": len(points)}


def compact_core(capture: dict[str, Any]) -> dict[str, Any]:
    return {
        "captured_at_utc": capture.get("captured_at_utc"),
        "run_id": capture.get("run_id"),
        "status": capture.get("status"),
        "core_owners_passed": capture.get("core_owners_passed"),
        "core_owners_planned": capture.get("core_owners_planned"),
        "market_metrics": capture.get("market_metrics", {}),
    }


def build(capture_root: Path, sidecar_root: Path, frozen_model: Path | None) -> dict[str, Any]:
    captures = load_capture_rows(capture_root)
    if len(captures) < 2:
        raise ValueError("insufficient_capture_history")
    latest_path, latest = captures[-1]
    previous_path, previous = captures[-2]
    cutoff = parse_ts(latest["captured_at_utc"])
    now = datetime.now(timezone.utc)
    age_hours = (now - cutoff).total_seconds() / 3600
    core_ok = latest.get("core_owners_passed") == latest.get("core_owners_planned") and latest.get("status") == "COMPLETE"
    freshness_ok = -0.25 <= age_hours <= 12
    sidecars = load_sidecars(sidecar_root)
    sequence = build_cfgi_sequence(sidecars, cutoff)
    cfgi_ok = sequence is not None and sequence.get("point_count", 0) >= 2
    model_ready = frozen_model is not None and frozen_model.exists()

    common = {
        "experiment_id": "PDLT-v1.1-RUN",
        "cutoff_utc": latest["captured_at_utc"],
        "latest_capture_path": str(latest_path),
        "previous_capture_path": str(previous_path),
        "latest": compact_core(latest),
        "previous": compact_core(previous),
        "limitations": [
            "Only data timestamped at or before cutoff may be used.",
            "Incubation rows created before model freeze are not prospective scoring rows.",
            "Missing CFGI does not invalidate core-only Arm C, but B/D remain unavailable.",
        ],
    }
    context_c = {**common, "arm": "C", "cfgi_included": False}
    context_d = {**common, "arm": "D", "cfgi_included": True, "cfgi": sequence} if cfgi_ok else None
    status = "BLOCKED_CORE_DATA" if not core_ok or not freshness_ok else "WAITING_FOR_DISCOVERY" if not model_ready else "READY_ABCD" if cfgi_ok else "READY_AC_ONLY"
    packet = {
        "contract": "PDLT_DAILY_CENSUS_CONTEXT_v1",
        "status": status,
        "created_at_utc": now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "cutoff_utc": latest["captured_at_utc"],
        "capture_age_hours": round(age_hours, 4),
        "core_available": core_ok and freshness_ok,
        "cfgi_available": cfgi_ok,
        "model_ready": model_ready,
        "context_c": context_c,
        "context_d": context_d,
        "context_c_sha256": sha(context_c),
        "context_d_sha256": sha(context_d) if context_d else None,
        "authority": {"canonical_promotion": False, "framework_state_change": False, "model_weight_change": False, "portfolio_action": False},
    }
    return packet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-root", type=Path, required=True)
    ap.add_argument("--sidecar-root", type=Path, required=True)
    ap.add_argument("--frozen-model", type=Path)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--context-c", type=Path)
    ap.add_argument("--context-d", type=Path)
    args = ap.parse_args()
    packet = build(args.capture_root, args.sidecar_root, args.frozen_model)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canon(packet))
    if args.context_c:
        args.context_c.parent.mkdir(parents=True, exist_ok=True)
        args.context_c.write_bytes(canon(packet["context_c"]))
    if args.context_d and packet["context_d"] is not None:
        args.context_d.parent.mkdir(parents=True, exist_ok=True)
        args.context_d.write_bytes(canon(packet["context_d"]))
    print(json.dumps({k: packet[k] for k in ("status","cutoff_utc","core_available","cfgi_available","model_ready","context_c_sha256","context_d_sha256")}, sort_keys=True))


if __name__ == "__main__":
    main()
