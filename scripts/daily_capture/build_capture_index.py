from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

OWNER_DIRS = {
    "fred_macro": "fred-owner-output",
    "binance_spot": "binance-spot-owner-output",
    "binance_microstructure": "binance-spot-microstructure-output",
    "okx_swap": "okx-swap-owner-output",
    "top100_breadth": "top100-breadth-owner-output",
    "cfgi_sentiment": "cfgi-owner-output",
}
CORE_OWNER_IDS = {
    "fred_macro", "binance_spot", "binance_microstructure", "okx_swap", "top100_breadth"
}
OPTIONAL_OWNER_IDS = {"cfgi_sentiment"}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def compact_json_summary(path: Path) -> dict[str, Any]:
    data = read_json(path)
    wanted = {
        "status", "run_id", "snapshot_id", "retrieval_timestamp_utc",
        "retrieval_timestamp", "retrieved_at_utc", "freeze_timestamp_utc", "as_of_utc",
        "rows", "row_count", "constituent_count", "membership_hash",
        "capture_integrity", "freshness_status", "source", "venue",
        "advancers", "decliners", "flat", "advancer_percentage",
        "timeframe", "symbols", "fields",
    }
    if isinstance(data, dict):
        return {k: data[k] for k in wanted if k in data}
    return {}


def last_kline(path: Path) -> dict[str, Any] | None:
    data = read_json(path)
    if not isinstance(data, list) or not data:
        return None
    row = data[-1]
    if not isinstance(row, list) or len(row) < 6:
        return None
    try:
        return {
            "open_time_ms": int(row[0]),
            "open": float(row[1]),
            "high": float(row[2]),
            "low": float(row[3]),
            "close": float(row[4]),
            "volume": float(row[5]),
            "range_pct": round((float(row[2]) / float(row[3]) - 1.0) * 100.0, 6) if float(row[3]) else None,
        }
    except (TypeError, ValueError, ZeroDivisionError):
        return None


def latest_fred_values(directory: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for path in sorted((directory / "raw/source_payloads").glob("*.csv")):
        series = path.stem.split("__")[-1]
        try:
            rows = list(csv.DictReader(path.open()))
        except Exception:
            continue
        for row in reversed(rows):
            raw = next((v for k, v in row.items() if k.lower() not in {"date", "observation_date"} and v not in {None, "", "."}), None)
            date = row.get("DATE") or row.get("date") or row.get("observation_date")
            if raw is not None:
                try:
                    values[series] = {"value": float(raw), "date": date}
                except ValueError:
                    pass
                break
    return values


def extract_cfgi(directory: Path) -> dict[str, Any]:
    snapshot = read_json(directory / "owner_snapshot.json")
    if not isinstance(snapshot, dict):
        return {}
    compact: dict[str, Any] = {
        "retrieved_at_utc": snapshot.get("retrieved_at_utc"),
        "timeframe": snapshot.get("timeframe"),
        "symbols": {},
    }
    for row in snapshot.get("rows", []):
        if not isinstance(row, dict):
            continue
        symbol = str(row.get("symbol") or row.get("asset") or row.get("ticker") or "UNKNOWN")
        compact["symbols"][symbol] = {
            key: row.get(key) for key in ("score", "price", "whales", "classification", "stale", "owner_status", "timestamp") if key in row
        }
    return compact


def extract_metrics(root: Path) -> dict[str, Any]:
    metrics: dict[str, Any] = {"spot": {}, "derivatives": {}, "breadth": {}, "macro": {}, "sentiment": {}}
    for symbol in ("BTCUSDT", "ETHUSDT", "ETHBTC"):
        row = last_kline(root / "binance-spot-owner-output" / "raw" / f"{symbol}.json")
        if row:
            metrics["spot"][symbol] = row

    okx = read_json(root / "okx-swap-owner-output" / "owner_snapshot.json")
    if isinstance(okx, dict):
        for row in okx.get("rows", []):
            if not isinstance(row, dict):
                continue
            inst = str(row.get("instrument", "UNKNOWN"))
            metric = str(row.get("metric", "unknown"))
            metrics["derivatives"].setdefault(inst, {})[metric] = {
                k: v for k, v in row.items() if k not in {"instrument", "metric", "venue"}
            }

    breadth = read_json(root / "top100-breadth-owner-output" / "owner_snapshot.json")
    if isinstance(breadth, dict):
        for key in ("advancers", "decliners", "flat", "advancer_percentage", "constituent_count", "membership_hash", "retrieval_timestamp"):
            if key in breadth:
                metrics["breadth"][key] = breadth[key]
        aggregate = breadth.get("aggregate")
        if isinstance(aggregate, dict):
            for key in ("advancers", "decliners", "flat", "advancer_percentage"):
                if key in aggregate:
                    metrics["breadth"][key] = aggregate[key]

    metrics["macro"] = latest_fred_values(root / "fred-owner-output")
    metrics["sentiment"]["cfgi"] = extract_cfgi(root / "cfgi-owner-output")
    return metrics


def owner_record(root: Path, owner_id: str, relative_dir: str, exit_codes: dict[str, int]) -> dict[str, Any]:
    directory = root / relative_dir
    files: list[dict[str, Any]] = []
    if directory.exists():
        for path in sorted(p for p in directory.rglob("*") if p.is_file()):
            item: dict[str, Any] = {"path": str(path.relative_to(root)), "bytes": path.stat().st_size, "sha256": sha256(path)}
            if path.suffix.lower() == ".json":
                summary = compact_json_summary(path)
                if summary:
                    item["summary"] = summary
            files.append(item)
    code = int(exit_codes.get(owner_id, 999))
    if code == 78:
        status = "DISABLED"
    elif code == 0 and files:
        status = "PASS"
    elif code == 0:
        status = "EMPTY"
    else:
        status = "FAIL"
    return {
        "owner_id": owner_id,
        "owner_class": "CORE" if owner_id in CORE_OWNER_IDS else "OPTIONAL",
        "collector_exit_code": code,
        "status": status,
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--trigger", required=True)
    args = parser.parse_args()

    exit_codes = json.loads(args.status_file.read_text())
    captured_at = datetime.now(timezone.utc).replace(microsecond=0)
    owners = [owner_record(args.root, key, value, exit_codes) for key, value in OWNER_DIRS.items()]
    core = [owner for owner in owners if owner["owner_id"] in CORE_OWNER_IDS]
    core_passed = sum(owner["status"] == "PASS" for owner in core)
    optional_passed = sum(owner["status"] == "PASS" for owner in owners if owner["owner_id"] in OPTIONAL_OWNER_IDS)
    overall = "COMPLETE" if core_passed == len(core) else "PARTIAL" if core_passed else "FAILED"

    packet = {
        "contract": "DAILY_RAW_CAPTURE_INDEX_v2",
        "authority": "SHADOW_OBSERVATION_ONLY",
        "run_id": args.run_id,
        "captured_at_utc": captured_at.isoformat().replace("+00:00", "Z"),
        "trigger": args.trigger,
        "status": overall,
        "owners_passed": core_passed + optional_passed,
        "owners_planned": len(owners),
        "core_owners_passed": core_passed,
        "core_owners_planned": len(core),
        "optional_owners_passed": optional_passed,
        "optional_owners_planned": len(OPTIONAL_OWNER_IDS),
        "owners": owners,
        "market_metrics": extract_metrics(args.root),
        "artifact_retention_days": 7,
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
        "weekly_calibration_eligible": core_passed >= 3,
    }

    day_dir = args.output_root / captured_at.strftime("%Y/%m/%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    output = day_dir / f"{captured_at.strftime('%H%M%S')}_{args.run_id}.json"
    output.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    (args.output_root / "LATEST.json").write_text(json.dumps({
        "contract": "DAILY_RAW_CAPTURE_LATEST_POINTER_v1",
        "path": str(output.relative_to(args.output_root.parent)),
        "run_id": args.run_id,
        "captured_at_utc": packet["captured_at_utc"],
        "status": overall,
    }, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
