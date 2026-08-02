from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--symbols", default="MARKET,BTC,ETH")
    args = parser.parse_args()
    key = os.environ.get("CFGI_API_KEY")
    if not key:
        raise SystemExit("CFGI_API_KEY_missing")
    url = "https://cfgi.io/api/v3/scores?symbols=" + args.symbols + "&timeframe=1d&fields=score,price,whales&limit=1"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {key}", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as response:
        payload = json.loads(response.read())
    rows = payload.get("data", [])
    if not rows:
        raise SystemExit("cfgi_empty")
    for row in rows:
        if row.get("stale") is True:
            row["owner_status"] = "STALE"
        else:
            row["owner_status"] = "PASS"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    packet = {
        "contract": "CFGI_OWNER_SNAPSHOT_v1",
        "source": "CFGI_V3",
        "retrieved_at_utc": now,
        "symbols": args.symbols.split(","),
        "rows": rows,
        "authority": "SHADOW_OBSERVATION_ONLY",
        "canonical_data_ping": False,
        "framework_state_change": False,
        "portfolio_action": False,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    body = canonical(packet)
    (args.output_dir / "owner_snapshot.json").write_bytes(body)
    receipt = {
        "contract": "CFGI_OWNER_RECEIPT_v1",
        "retrieved_at_utc": now,
        "sha256": hashlib.sha256(body).hexdigest(),
        "row_count": len(rows),
        "status": "PASS" if all(r.get("owner_status") == "PASS" for r in rows) else "DEGRADED",
    }
    (args.output_dir / "receipt.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
