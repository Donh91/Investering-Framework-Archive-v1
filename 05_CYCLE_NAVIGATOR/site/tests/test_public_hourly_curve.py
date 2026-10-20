"""Production-source hourly chart regression: pure sanitized spot evidence only."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from scripts.cycle_navigator.build_public_live_precision import public_hourly_price_path

def dt(t: str) -> datetime:
    return datetime.fromisoformat(t.replace("Z", "+00:00")).astimezone(timezone.utc)

def row(time: str, price: str = "82000", status: str = "PASS") -> dict[str, str]:
    return {
        "timestamp_utc": time, "spot_status": status,
        "btc_low": "81000", "btc_high": "83000", "btc_close": price,
        "eth_low": "2300", "eth_high": "2600", "eth_close": "2420",
        "secret_key": "THIS_PRIVATE_VALUE_MUST_NOT_LEAVE_SOURCE",
    }

cutoff = dt("2026-10-20T08:00:00Z")
now = dt("2026-10-20T09:00:00Z")
data = [
    row("2026-10-19T00:00:00Z"),
    row("2026-10-19T01:00:00Z", "82100"),
    row("2026-10-19T03:00:00Z", "82200"),  # a real missing hour, never interpolated
    row("2026-10-19T04:00:00Z", "82250", "FAIL"),
    row("2026-10-19T05:00:00Z", "-5"),    # invalid source value, other asset safe
    row("2026-10-20T11:00:00Z", "82600"), # not closed by now / cutoff
    row("2026-10-12T00:00:00Z", "82000"), # wrong week
]
output = public_hourly_price_path(data, 2026, 43, 30, cutoff, now=now)
assert output["contract"] == "CN_PUBLIC_HOURLY_PRICE_PATH_v1"
assert output["semantics"] == "OBSERVED_HOURLY_CLOSE_NOT_A_PROSPECTIVE_FORECAST"
assert output["forecast_week"] == "2026-W43"
assert output["public_issue_number"] == 30
assert output["observed_through_utc"] == "2026-10-20T08:00:00Z"
assert [r["observed_at_utc"] for r in output["BTC"]] == [
    "2026-10-19T01:00:00Z", "2026-10-19T02:00:00Z", "2026-10-19T04:00:00Z",
]
assert [r["close"] for r in output["BTC"]] == [82000, 82100, 82200]
assert len(output["ETH"]) == 4  # ETH valid even where BTC numeric is invalid
assert all(set(p) == {"observed_at_utc", "close"} for asset in ("BTC","ETH") for p in output[asset])
serialized = json.dumps(output)
assert "secret_key" not in serialized and "THIS_PRIVATE_VALUE" not in serialized
assert "expected_close" not in serialized and "forecast" not in serialized.lower().replace("prospective_forecast","")
assert not public_hourly_price_path(data, 2026, 43, 30, None, now=now)["BTC"]
assert not public_hourly_price_path([], 2026, 43, 30, cutoff, now=now)["BTC"]
assert all(r["close"] > 0 for r in output["BTC"])
print("PUBLIC_HOURLY_CHART_SOURCE_UTC_PRIVACY_GAP_PROOF_PASS")
