#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "research/historical_research_vault/SOURCE_REGISTRY_v1.json"
RECIPES = ROOT / "research/historical_research_vault/SOURCE_RECIPES_v1.json"
UA = {"User-Agent": "Investering-Historical-Research-Vault/1.1", "Accept": "application/json"}
AUTHORITY = {"framework_state_change": False, "model_weight_change": False, "portfolio_action": False}
SQD_MAX_BLOCKS = 5000
SQD_DATASET_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,127}$")


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def unix_seconds_to_utc(value: Any) -> str | None:
    if not isinstance(value, (int, float)):
        return None
    try:
        return datetime.fromtimestamp(float(value), tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    except (OverflowError, OSError, ValueError):
        return None


def deterministic_gzip(body: bytes) -> bytes:
    buf = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=buf, mtime=0) as gz:
        gz.write(body)
    return buf.getvalue()


def http_json(url: str, *, timeout: int = 45) -> tuple[Any, dict[str, Any], bytes]:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as response:
        raw = response.read()
        status = int(response.status)
    return json.loads(raw), {
        "url": url,
        "http_status": status,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
    }, raw


def parse_json_or_ndjson(raw: bytes) -> list[dict[str, Any]]:
    text = raw.decode("utf-8").strip()
    if not text:
        return []
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None
    if isinstance(parsed, dict):
        return [parsed]
    if isinstance(parsed, list):
        return [row for row in parsed if isinstance(row, dict)]

    out: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        item = json.loads(line)
        if isinstance(item, dict):
            out.append(item)
        elif isinstance(item, list):
            out.extend(row for row in item if isinstance(row, dict))
    return out


def http_sqd_post(url: str, payload: dict[str, Any], *, timeout: int = 60) -> tuple[list[dict[str, Any]], dict[str, Any], bytes]:
    headers = {
        "User-Agent": "Investering-Historical-Research-Vault/1.1",
        "Accept": "application/x-ndjson, application/json",
        "Content-Type": "application/json",
    }
    authorization = os.environ.get("SQD_PORTAL_AUTHORIZATION")
    if authorization:
        headers["Authorization"] = authorization
    request_body = canonical(payload)
    req = urllib.request.Request(url, data=request_body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            status = int(response.status)
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            raise RuntimeError("sqd_portal_authorization_required") from exc
        raise
    rows = parse_json_or_ndjson(raw)
    return rows, {
        "url": url,
        "http_status": status,
        "payload_sha256": sha256(raw),
        "payload_bytes": len(raw),
        "request_sha256": sha256(request_body),
        "authorization_header_supplied": bool(authorization),
    }, raw


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def registry_map() -> dict[str, dict[str, Any]]:
    doc = load_json(REGISTRY)
    return {row["source_id"]: row for row in doc["sources"]}


def validate() -> dict[str, Any]:
    registry = load_json(REGISTRY)
    recipes = load_json(RECIPES)
    sources = registry["sources"]
    recipe_rows = recipes["recipes"]
    source_ids = [row["source_id"] for row in sources]
    recipe_ids = [row["source_id"] for row in recipe_rows]
    errors: list[str] = []
    if len(source_ids) != len(set(source_ids)):
        errors.append("duplicate_source_id")
    if set(source_ids) != set(recipe_ids):
        errors.append("source_recipe_mismatch")
    for row in sources:
        if row.get("durable_capture_enabled") and "REVIEW_REQUIRED" in row.get("license_class", ""):
            errors.append(f"durable_capture_enabled_before_license_review:{row['source_id']}")
        if row.get("durable_capture_enabled") and row.get("vault_collection_mode") in {
            "QUERY_TIME_ONLY_METADATA_RECEIPT", "INDEX_ONLY_NO_DUPLICATE"
        }:
            errors.append(f"invalid_durable_mode:{row['source_id']}")
    if "THE_GRAPH_SUBGRAPH_REPLAY_v1" in source_ids:
        errors.append("the_graph_must_not_be_active_primary")
    if "SQD_PORTAL_EVM_REPLAY_v1" not in source_ids:
        errors.append("sqd_primary_source_missing")
    return {
        "contract": "HISTORICAL_RESEARCH_VAULT_VALIDATION_v1",
        "status": "PASS" if not errors else "FAIL",
        "source_count": len(source_ids),
        "recipe_count": len(recipe_ids),
        "errors": errors,
    }


def normalize_growthepie(doc: Any, *, chain: str, metric: str) -> list[dict[str, Any]]:
    try:
        daily = doc["details"]["timeseries"]["daily"]
        types = daily["types"]
        data = daily["data"]
    except (KeyError, TypeError):
        return []
    if not isinstance(types, list) or "unix" not in types or not isinstance(data, list):
        return []
    unix_index = types.index("unix")
    value_indices = [(i, str(name)) for i, name in enumerate(types) if i != unix_index]
    out: list[dict[str, Any]] = []
    for raw_row in data:
        if not isinstance(raw_row, list) or len(raw_row) <= unix_index:
            continue
        ts = raw_row[unix_index]
        if not isinstance(ts, (int, float)):
            continue
        ts_int = int(ts)
        dt = datetime.fromtimestamp(ts_int / 1000.0, tz=timezone.utc)
        values: dict[str, Any] = {}
        for idx, name in value_indices:
            values[name] = raw_row[idx] if idx < len(raw_row) else None
        out.append({
            "timestamp_ms": ts_int,
            "date": dt.date().isoformat(),
            "chain": chain,
            "metric": metric,
            "values": values,
        })
    return sorted(out, key=lambda row: row["timestamp_ms"])


def normalize_coinmetrics(doc: Any) -> list[dict[str, Any]]:
    rows = doc.get("data", []) if isinstance(doc, dict) else []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        asset = row.get("asset")
        time_value = row.get("time")
        if not asset or not time_value:
            continue
        normalized = {"asset": asset, "time": time_value}
        for key, value in sorted(row.items()):
            if key not in {"asset", "time"}:
                normalized[key] = value
        out.append(normalized)
    return sorted(out, key=lambda row: (row["time"], row["asset"]))


def normalize_sqd_blocks(items: list[dict[str, Any]], *, dataset: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        header = item.get("header")
        if not isinstance(header, dict):
            continue
        number = header.get("number")
        if not isinstance(number, int):
            continue
        logs = item.get("logs", [])
        if not isinstance(logs, list):
            logs = []
        out.append({
            "dataset": dataset,
            "block_number": number,
            "block_timestamp": header.get("timestamp"),
            "block_time_utc": unix_seconds_to_utc(header.get("timestamp")),
            "block_hash": header.get("hash"),
            "parent_hash": header.get("parentHash"),
            "logs": logs,
        })
    return sorted(out, key=lambda row: row["block_number"])


def write_capture(
    *,
    source_id: str,
    raw: bytes,
    normalized_rows: list[dict[str, Any]],
    output_root: Path,
    coverage_field: str,
    raw_filename: str = "raw.json",
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    norm_body = b"".join(canonical(row) + b"\n" for row in normalized_rows)
    compressed = deterministic_gzip(norm_body)
    (output_root / "normalized.jsonl.gz").write_bytes(compressed)
    (output_root / raw_filename).write_bytes(raw)
    coverage_values = [str(row.get(coverage_field)) for row in normalized_rows if row.get(coverage_field) is not None]
    manifest = {
        "contract": "HISTORICAL_RESEARCH_VAULT_CAPTURE_MANIFEST_v1",
        "dataset_id": f"{source_id}:{now_utc()}",
        "source_id": source_id,
        "retrieved_at_utc": now_utc(),
        "coverage": {
            "start_utc": min(coverage_values) if coverage_values else None,
            "end_utc": max(coverage_values) if coverage_values else None,
            "row_count": len(normalized_rows),
        },
        "raw": {"payload_sha256": sha256(raw), "payload_bytes": len(raw)},
        "normalized": {"format": "jsonl.gz", "payload_sha256": sha256(compressed)},
        "storage": {"class": "T2_ACTIONS_ARTIFACT", "retention_days": 14, "durable": False},
        "authority": AUTHORITY,
    }
    (output_root / "manifest.json").write_bytes(canonical(manifest) + b"\n")
    return manifest


def collect_growthepie(args: argparse.Namespace) -> dict[str, Any]:
    source_id = "GROWTHEPIE_ETH_L2_DAILY_v1"
    row = registry_map()[source_id]
    if row.get("durable_capture_enabled"):
        raise RuntimeError("unexpected_durable_capture_enabled")
    url = f"https://api.growthepie.com/v1/metrics/chains/{urllib.parse.quote(args.chain)}/{urllib.parse.quote(args.metric)}.json"
    doc, receipt, raw = http_json(url)
    rows = normalize_growthepie(doc, chain=args.chain, metric=args.metric)
    if not rows:
        raise RuntimeError("growthepie_unparseable_or_empty")
    manifest = write_capture(source_id=source_id, raw=raw, normalized_rows=rows, output_root=args.output_root, coverage_field="date")
    return {"status": "PASS", "source_receipt": receipt, "manifest": manifest}


def collect_coinmetrics(args: argparse.Namespace) -> dict[str, Any]:
    source_id = "COINMETRICS_COMMUNITY_BTC_ETH_DAILY_v1"
    metrics = ["PriceUSD", "SplyCur", "CapMrktCurUSD", "TxCnt"]
    params = urllib.parse.urlencode({
        "assets": args.assets,
        "metrics": ",".join(metrics),
        "frequency": "1d",
        "start_time": args.start_time,
        "end_time": args.end_time,
        "page_size": "10000",
    })
    next_url: str | None = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?" + params
    all_rows: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    raw_pages: list[Any] = []
    page_guard = 0
    while next_url:
        page_guard += 1
        if page_guard > 20:
            raise RuntimeError("coinmetrics_pagination_guard")
        doc, receipt, _raw = http_json(next_url)
        receipts.append(receipt)
        raw_pages.append(doc)
        all_rows.extend(normalize_coinmetrics(doc))
        next_url = doc.get("next_page_url") if isinstance(doc, dict) else None
    if not all_rows:
        raise RuntimeError("coinmetrics_empty")
    raw_bundle = canonical({"pages": raw_pages})
    manifest = write_capture(source_id=source_id, raw=raw_bundle, normalized_rows=all_rows, output_root=args.output_root, coverage_field="time")
    return {"status": "PASS", "page_count": page_guard, "source_receipts": receipts, "manifest": manifest}


def sqd_endpoint(dataset: str) -> str:
    if not SQD_DATASET_RE.fullmatch(dataset):
        raise RuntimeError("invalid_sqd_dataset_slug")
    return f"https://portal.sqd.dev/datasets/{dataset}/finalized-stream"


def sqd_filter(addresses: str | None, topic0: str | None) -> dict[str, list[str]]:
    row: dict[str, list[str]] = {}
    if addresses:
        values = [v.strip() for v in addresses.split(",") if v.strip()]
        if values:
            row["address"] = values
    if topic0:
        values = [v.strip() for v in topic0.split(",") if v.strip()]
        if values:
            row["topic0"] = values
    return row


def collect_sqd(args: argparse.Namespace) -> dict[str, Any]:
    source_id = "SQD_PORTAL_EVM_REPLAY_v1"
    registry_row = registry_map()[source_id]
    if registry_row.get("durable_capture_enabled"):
        raise RuntimeError("unexpected_durable_capture_enabled")
    if args.to_block < args.from_block:
        raise RuntimeError("sqd_invalid_block_range")
    block_count = args.to_block - args.from_block + 1
    if block_count > SQD_MAX_BLOCKS:
        raise RuntimeError(f"sqd_block_range_exceeds_{SQD_MAX_BLOCKS}")
    log_filter = sqd_filter(args.address, args.topic0)
    if not log_filter:
        raise RuntimeError("sqd_address_or_topic0_filter_required")
    payload = {
        "type": "evm",
        "fromBlock": args.from_block,
        "toBlock": args.to_block,
        "fields": {
            "block": {"number": True, "timestamp": True, "hash": True, "parentHash": True},
            "log": {
                "address": True,
                "topics": True,
                "data": True,
                "transactionHash": True,
                "transactionIndex": True,
                "logIndex": True,
            },
        },
        "logs": [log_filter],
    }
    url = sqd_endpoint(args.dataset)
    items, receipt, raw = http_sqd_post(url, payload)
    rows = normalize_sqd_blocks(items, dataset=args.dataset)
    if not rows:
        raise RuntimeError("sqd_empty_or_unparseable")
    manifest = write_capture(
        source_id=source_id,
        raw=raw,
        normalized_rows=rows,
        output_root=args.output_root,
        coverage_field="block_time_utc",
        raw_filename="raw.ndjson",
    )
    return {
        "status": "PASS",
        "dataset": args.dataset,
        "requested_block_count": block_count,
        "returned_block_rows": len(rows),
        "source_receipt": receipt,
        "manifest": manifest,
    }


def probe_sqd(args: argparse.Namespace) -> dict[str, Any]:
    source_id = "SQD_PORTAL_EVM_REPLAY_v1"
    payload = {
        "type": "evm",
        "fromBlock": args.block,
        "toBlock": args.block,
        "includeAllBlocks": True,
        "fields": {
            "block": {"number": True, "timestamp": True, "hash": True, "parentHash": True},
        },
    }
    url = sqd_endpoint(args.dataset)
    items, receipt, _raw = http_sqd_post(url, payload)
    rows = normalize_sqd_blocks(items, dataset=args.dataset)
    if not rows or args.block not in {row["block_number"] for row in rows}:
        raise RuntimeError("sqd_probe_block_missing")
    return {
        "contract": "HISTORICAL_RESEARCH_VAULT_SQD_KEYLESS_PROBE_v1",
        "status": "PASS",
        "source_id": source_id,
        "retrieved_at_utc": now_utc(),
        "dataset": args.dataset,
        "probe_block": args.block,
        "source_receipt": receipt,
        "raw_payload_persisted": False,
        "authority": AUTHORITY,
    }


def probe_coingecko(args: argparse.Namespace) -> dict[str, Any]:
    source_id = "COINGECKO_HISTORICAL_CROSSCHECK_v1"
    url = "https://api.coingecko.com/api/v3/coins/" + f"{urllib.parse.quote(args.coin)}/market_chart?vs_currency=usd&days=7&interval=daily"
    doc, receipt, _raw = http_json(url)
    shape = sorted(doc.keys()) if isinstance(doc, dict) else []
    return {
        "contract": "HISTORICAL_RESEARCH_VAULT_QUERY_TIME_PROBE_v1",
        "status": "PASS",
        "source_id": source_id,
        "retrieved_at_utc": now_utc(),
        "source_receipt": receipt,
        "response_keys": shape,
        "raw_payload_persisted": False,
        "authority": AUTHORITY,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate")

    gp = sub.add_parser("collect-growthepie")
    gp.add_argument("--chain", default="base")
    gp.add_argument("--metric", default="stables_mcap")
    gp.add_argument("--output-root", type=Path, required=True)

    cm = sub.add_parser("collect-coinmetrics")
    cm.add_argument("--assets", default="btc,eth")
    cm.add_argument("--start-time", required=True)
    cm.add_argument("--end-time", required=True)
    cm.add_argument("--output-root", type=Path, required=True)

    sqd = sub.add_parser("collect-sqd")
    sqd.add_argument("--dataset", default="ethereum-mainnet")
    sqd.add_argument("--from-block", type=int, required=True)
    sqd.add_argument("--to-block", type=int, required=True)
    sqd.add_argument("--address")
    sqd.add_argument("--topic0")
    sqd.add_argument("--output-root", type=Path, required=True)

    sqdp = sub.add_parser("probe-sqd")
    sqdp.add_argument("--dataset", default="ethereum-mainnet")
    sqdp.add_argument("--block", type=int, default=21000000)

    cg = sub.add_parser("probe-coingecko")
    cg.add_argument("--coin", default="bitcoin")

    args = parser.parse_args()
    if args.command == "validate":
        result = validate()
    elif args.command == "collect-growthepie":
        result = collect_growthepie(args)
    elif args.command == "collect-coinmetrics":
        result = collect_coinmetrics(args)
    elif args.command == "collect-sqd":
        result = collect_sqd(args)
    elif args.command == "probe-sqd":
        result = probe_sqd(args)
    elif args.command == "probe-coingecko":
        result = probe_coingecko(args)
    else:
        raise RuntimeError("unknown_command")
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
