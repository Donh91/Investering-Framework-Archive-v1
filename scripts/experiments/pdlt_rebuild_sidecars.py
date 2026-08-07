from __future__ import annotations

import argparse
import hashlib
import json
import tarfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FIELDS = ["score","volatility","volume","impulse","technical","social","dominance","trends","whales","orders"]
MEMBER = "cfgi-owner-output/owner_snapshot.json"
PREFIX = "cfgi-owner-output-"
SUFFIX = ".tar.gz"


def canonical(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def component(row: dict[str, Any], field: str) -> Any:
    if field == "score":
        return row.get("score")
    nested = row.get("components")
    if isinstance(nested, dict) and nested.get(field) is not None:
        return nested.get(field)
    return row.get(field)


def compact(snapshot: dict[str, Any]) -> tuple[str, dict[str, Any], list[str]]:
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


def run_id(path: Path) -> str:
    name = path.name
    if not name.startswith(PREFIX) or not name.endswith(SUFFIX):
        raise ValueError(f"unexpected_archive_name:{name}")
    return name[len(PREFIX):-len(SUFFIX)]


def read_snapshot(path: Path) -> dict[str, Any] | None:
    try:
        with tarfile.open(path, "r:gz") as tar:
            member = tar.getmember(MEMBER)
            handle = tar.extractfile(member)
            if handle is None:
                return None
            return json.loads(handle.read())
    except (KeyError, tarfile.TarError, json.JSONDecodeError, OSError):
        return None


def materialize(path: Path, output_root: Path) -> tuple[Path | None, dict[str, Any] | None]:
    snapshot = read_snapshot(path)
    if not snapshot:
        return None, None
    retrieved = snapshot.get("retrieved_at_utc")
    if not isinstance(retrieved, str) or not retrieved:
        return None, None
    when = parse_ts(retrieved)
    rid = run_id(path)
    status, symbols, problems = compact(snapshot)
    packet = {
        "contract": "PDLT_OWNER_SIDECAR_v1",
        "run_id": rid,
        "created_at_utc": when.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_archive": str(path),
        "status": status,
        "cfgi": {
            "source_contract": snapshot.get("contract"),
            "source_sha256": digest(snapshot),
            "retrieved_at_utc": retrieved,
            "timeframe": snapshot.get("timeframe"),
            "fields": snapshot.get("fields"),
            "billing": snapshot.get("billing"),
            "symbols": symbols,
        },
        "problems": problems,
        "authority": "SHADOW_OBSERVATION_ONLY",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }
    dest_dir = output_root / when.strftime("%Y/%m/%d")
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / f"{when.strftime('%H%M%S')}_{rid}.json"
    if not dest.exists():
        dest.write_bytes(canonical(packet))
    return dest, packet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-root", type=Path, required=True)
    ap.add_argument("--output-root", type=Path, required=True)
    ap.add_argument("--max-archives", type=int, default=40)
    args = ap.parse_args()

    archives = sorted(args.raw_root.rglob("cfgi-owner-output-*.tar.gz"))[-args.max_archives:]
    created = 0
    materialized: list[tuple[Path, dict[str, Any]]] = []
    for archive in archives:
        dest, packet = materialize(archive, args.output_root)
        if dest is not None and packet is not None:
            materialized.append((dest, packet))
            created += 1
    if not materialized:
        print(json.dumps({"status":"NO_CFGI_ARCHIVES","archives_scanned":len(archives),"materialized":0}, sort_keys=True))
        return
    materialized.sort(key=lambda item: item[1]["created_at_utc"])
    latest_path, latest = materialized[-1]
    pointer = {
        "contract": "PDLT_OWNER_SIDECAR_LATEST_v1",
        "path": str(latest_path.relative_to(args.output_root.parent)),
        "run_id": latest["run_id"],
        "created_at_utc": latest["created_at_utc"],
        "status": latest["status"],
        "sha256": digest(latest),
    }
    args.output_root.mkdir(parents=True, exist_ok=True)
    (args.output_root / "LATEST.json").write_bytes(canonical(pointer))
    four_h = sum(1 for _, packet in materialized if packet.get("status") == "PASS" and packet.get("cfgi", {}).get("timeframe") == "4h")
    print(json.dumps({"status":"PASS","archives_scanned":len(archives),"materialized":created,"valid_4h":four_h,"latest":pointer["path"]}, sort_keys=True))


if __name__ == "__main__":
    main()
