from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

USER_AGENT = "Investering-Framework-CFGI-Owner/1.1"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def parse_int_header(headers: object, name: str) -> int | None:
    try:
        value = headers.get(name)  # type: ignore[attr-defined]
        return int(value) if value is not None else None
    except (TypeError, ValueError, AttributeError):
        return None


def read_with_empty_retries(req: urllib.request.Request) -> tuple[dict, int | None, int | None, int, list[dict]]:
    """Up to two 30s retries only for truly empty successful responses.

    Malformed, quota-blocked and HTTP-error outcomes are not silently retried.
    Each attempted response's provider credit headers are kept independently.
    """
    observed_headers: list[dict] = []
    for attempt in range(1, 4):
        with urllib.request.urlopen(req, timeout=60) as response:
            raw = response.read()
            used = parse_int_header(response.headers, "X-Credits-Used")
            remaining = parse_int_header(response.headers, "X-Credits-Remaining")
        observed_headers.append({"attempt": attempt, "credits_used_header": used, "credits_remaining_header": remaining})
        if raw:
            payload = json.loads(raw)  # malformed payload is schema failure, never retry
            if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
                raise SystemExit("CFGI_SCHEMA_DRIFT")
            if payload["data"]:
                return payload, used, remaining, attempt, observed_headers
        if attempt < 3:
            time.sleep(30)
    raise SystemExit("cfgi_empty_after_2_retries")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--symbols", default="MARKET,BTC,ETH")
    parser.add_argument("--timeframe", default="4h")
    parser.add_argument("--fields", default="score")
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
        payload, credits_used, credits_remaining, attempts, credit_headers = read_with_empty_retries(req)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise SystemExit(f"CFGI_HTTP_{exc.code}:{body[:300]}") from exc
    rows = payload["data"]
    for row in rows:
        row["owner_status"] = "STALE" if row.get("stale") is True else "PASS"
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    billing = {
        "credits_used": credits_used,
        "credits_remaining": credits_remaining,
        "expected_credits": len(args.symbols.split(",")) * len(args.fields.split(",")) * args.limit,
        "attempt_count": attempts,
        "provider_credit_header_observations": credit_headers,
        "max_requested_field_units": attempts * len(args.symbols.split(",")) * len(args.fields.split(",")) * args.limit,
    }
    packet = {
        "contract": "CFGI_OWNER_SNAPSHOT_v3",
        "source": "CFGI_V3",
        "retrieved_at_utc": now,
        "symbols": args.symbols.split(","),
        "timeframe": args.timeframe,
        "fields": args.fields.split(","),
        "limit": args.limit,
        "billing": billing,
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
        "contract": "CFGI_OWNER_RECEIPT_v3",
        "retrieved_at_utc": now,
        "sha256": hashlib.sha256(body).hexdigest(),
        "row_count": len(rows),
        "timeframe": args.timeframe,
        "fields": args.fields.split(","),
        "billing": billing,
        "status": "PASS" if all(r.get("owner_status") == "PASS" for r in rows) else "DEGRADED",
    }
    (args.output_dir / "receipt.json").write_bytes(canonical(receipt))
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
