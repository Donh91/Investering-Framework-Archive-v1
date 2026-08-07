from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FIELDS = ["score","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"]


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def component(row: dict[str, Any], field: str) -> Any:
    if field == "score":
        return row.get("score")
    nested = row.get("components")
    if isinstance(nested, dict) and nested.get(field) is not None:
        return nested.get(field)
    return row.get(field)


def compact_cfgi(snapshot: dict[str, Any]) -> tuple[str, dict[str, Any], list[str]]:
    rows = snapshot.get("rows", [])
    symbols: dict[str, Any] = {}
    problems: list[str] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or row.get("asset") or row.get("ticker") or "UNKNOWN")
        values = {field: component(row, field) for field in FIELDS}
        missing = [field for field, value in values.items() if value is None]
        if missing:
            problems.append(f"{symbol}:missing:{','.join(missing)}")
        if row.get("stale") is True or row.get("owner_status") == "STALE":
            problems.append(f"{symbol}:stale")
        symbols[symbol] = {
            "timestamp": row.get("timestamp"),
            "classification": row.get("classification"),
            "stale": row.get("stale"),
            "owner_status": row.get("owner_status"),
            "values": values,
        }
    expected = {"MARKET", "BTC", "ETH"}
    if set(symbols) != expected:
        problems.append(f"symbols:{sorted(symbols)}")
    status = "PASS" if not problems else "DEGRADED"
    return status, symbols, problems


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--capture-latest", type=Path, required=True)
    ap.add_argument("--cfgi-snapshot", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args()

    now = datetime.now(timezone.utc).replace(microsecond=0)
    latest = read(args.capture_latest)
    capture_path = latest.get("path")
    base = {
        "contract": "PDLT_OWNER_SIDECAR_v1",
        "run_id": args.run_id,
        "created_at_utc": now.isoformat().replace("+00:00", "Z"),
        "capture_pointer": latest,
        "capture_path": capture_path,
        "authority": "SHADOW_OBSERVATION_ONLY",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }

    if not args.cfgi_snapshot.exists():
        packet = {**base, "status": "CFGI_UNAVAILABLE", "cfgi": None, "problems": ["snapshot_missing"]}
    else:
        snapshot = read(args.cfgi_snapshot)
        status, symbols, problems = compact_cfgi(snapshot)
        packet = {
            **base,
            "status": status,
            "cfgi": {
                "source_contract": snapshot.get("contract"),
                "source_sha256": digest(snapshot),
                "retrieved_at_utc": snapshot.get("retrieved_at_utc"),
                "timeframe": snapshot.get("timeframe"),
                "fields": snapshot.get("fields"),
                "billing": snapshot.get("billing"),
                "symbols": symbols,
            },
            "problems": problems,
        }

    day = args.output_root / now.strftime("%Y/%m/%d")
    day.mkdir(parents=True, exist_ok=True)
    out = day / f"{now.strftime('%H%M%S')}_{args.run_id}.json"
    out.write_bytes(canonical(packet))
    pointer = {
        "contract": "PDLT_OWNER_SIDECAR_LATEST_v1",
        "path": str(out.relative_to(args.output_root.parent)),
        "run_id": args.run_id,
        "created_at_utc": packet["created_at_utc"],
        "status": packet["status"],
        "sha256": digest(packet),
    }
    (args.output_root / "LATEST.json").write_bytes(canonical(pointer))
    print(json.dumps({"status": packet["status"], "path": str(out), "problems": packet["problems"]}, sort_keys=True))


if __name__ == "__main__":
    main()
