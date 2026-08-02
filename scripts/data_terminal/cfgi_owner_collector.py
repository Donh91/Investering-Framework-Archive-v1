from __future__ import annotations

import argparse
import hashlib
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "Investering-Framework-CFGI-Owner/1.0"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--symbols", default="MARKET,BTC,ETH")
    parser.add_argument("--timeframe", default="4h")
    parser.add_argument("--fields", default="score,price,whales")
    parser.add_argument("--limit", type=int, default=1)
    args = parser.parse_args()
    key = os.environ.get("CFGI_API_KEY")
    if not key:
        raise SystemExit("CFGI_API_KEY_missing")
    query = urllib.parse.urlencode({
        "api_key": key,
        "symbols": args.symbols,
        "timeframe": args.timeframe,
        "fields": args.fields,
        "limit": args.limit,
    })
    url = "https://cfgi.io/api/v3/scores?" + query
    req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise SystemExit(f"CFGI_HTTP_{exc.code}:{body[:300]}") from exc
    rows = payload.get("data", [])
    if not rows:
        raise SystemExit("cfgi_empty")
    for row in rows:
        row["owner_status"] = "STALE" if row.get("stale") is True else "PASS"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    packet = {
        "contract": "CFGI_OWNER_SNAPSHOT_v2",
        "source": "CFGI_V3",
        "retrieved_at_utc": now,
        "symbols": args.symbols.split(","),
        "timeframe": args.timeframe,
        "fields": args.fields.split(","),
        "limit": args.limit,
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
        "contract": "CFGI_OWNER_RECEIPT_v2",
        "retrieved_at_utc": now,
        "sha256": hashlib.sha256(body).hexdigest(),
        "row_count": len(rows),
        "timeframe": args.timeframe,
        "status": "PASS" if all(r.get("owner_status") == "PASS" for r in rows) else "DEGRADED",
    }
    (args.output_dir / "receipt.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
