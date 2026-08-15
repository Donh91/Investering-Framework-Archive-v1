#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE = "https://stablecoins.llama.fi"
UA = {"User-Agent": "Investering-Stablecoin-Deployment-Owner/1.0", "Accept": "application/json"}
AUTHORITY = {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False}


def canonical(v: Any) -> bytes:
    return json.dumps(v, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def fetch(path: str) -> tuple[Any, dict[str, Any], bytes]:
    url = BASE + path
    req = urllib.request.Request(url, headers=UA)
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    with urllib.request.urlopen(req, timeout=30) as r:
        raw = r.read(); status = r.status
    if status != 200 or not raw:
        raise RuntimeError(f"source_error:{path}:{status}")
    value = json.loads(raw)
    return value, {"url": url, "http_status": status, "retrieved_at_utc": started, "payload_sha256": sha(raw), "payload_bytes": len(raw)}, raw


def usd(v: Any) -> float | None:
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, dict):
        for key in ("peggedUSD", "usd", "USD"):
            if isinstance(v.get(key), (int, float)):
                return float(v[key])
    return None


def chart_rows(doc: Any) -> list[tuple[int, float]]:
    if not isinstance(doc, list):
        raise RuntimeError("stablecoin_chart_schema")
    out = []
    for row in doc:
        if not isinstance(row, dict):
            continue
        try:
            ts = int(row.get("date"))
        except Exception:
            continue
        value = usd(row.get("totalCirculatingUSD"))
        if value is not None and value > 0:
            out.append((ts, value))
    if len(out) < 8:
        raise RuntimeError("stablecoin_chart_insufficient")
    return sorted(out)


def pct(a: float, b: float | None) -> float | None:
    return None if not b else round((a / b - 1.0) * 100.0, 6)


def prior(rows: list[tuple[int, float]], days: int) -> float | None:
    target = rows[-1][0] - days * 86400
    candidates = [x for x in rows if x[0] <= target]
    return candidates[-1][1] if candidates else None


def chain_rows(doc: Any) -> list[dict[str, Any]]:
    if not isinstance(doc, list):
        raise RuntimeError("stablecoin_chains_schema")
    out = []
    for row in doc:
        if not isinstance(row, dict):
            continue
        value = usd(row.get("totalCirculatingUSD"))
        if value is None:
            value = usd(row.get("mcap"))
        name = row.get("name") or row.get("gecko_id") or row.get("chain")
        if name and value is not None:
            out.append({"chain": str(name), "stablecoin_mcap_usd": round(value, 2)})
    out.sort(key=lambda x: x["stablecoin_mcap_usd"], reverse=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--output-dir", type=Path, required=True); args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    chart, chart_receipt, chart_raw = fetch("/stablecoincharts/all")
    chains, chains_receipt, chains_raw = fetch("/stablecoinchains")
    rows = chart_rows(chart); latest_ts, latest = rows[-1]
    crows = chain_rows(chains)
    observed = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    snapshot = {
        "contract": "STABLECOIN_DEPLOYMENT_OWNER_v1",
        "status": "PASS",
        "retrieved_at_utc": observed,
        "source": "DEFILLAMA_PUBLIC_STABLECOIN_API",
        "global": {
            "as_of_unix": latest_ts,
            "stablecoin_mcap_usd": round(latest, 2),
            "change_1d_pct": pct(latest, prior(rows, 1)),
            "change_7d_pct": pct(latest, prior(rows, 7)),
            "change_30d_pct": pct(latest, prior(rows, 30)),
            "history_points": len(rows)
        },
        "chains_top20": crows[:20],
        "source_receipts": {"global_history": chart_receipt, "chains": chains_receipt},
        "interpolation": False,
        "forward_fill": False,
        "authority": AUTHORITY,
        "semantic_note": "Evidence lane only. Stablecoin market-cap changes are observations, not liquidity-deployment or BUY rules by themselves."
    }
    (args.output_dir / "raw_global_history.json").write_bytes(chart_raw)
    (args.output_dir / "raw_chains.json").write_bytes(chains_raw)
    (args.output_dir / "owner_snapshot.json").write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n")
    receipt = {"contract": "STABLECOIN_DEPLOYMENT_RECEIPT_v1", "status": "PASS", "owner_sha256": sha(canonical(snapshot)), "source_receipts": snapshot["source_receipts"], "authority": AUTHORITY}
    (args.output_dir / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status":"PASS","global_mcap_usd":snapshot["global"]["stablecoin_mcap_usd"],"change_7d_pct":snapshot["global"]["change_7d_pct"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
