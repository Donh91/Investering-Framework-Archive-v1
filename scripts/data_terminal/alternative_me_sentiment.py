"""Collect Alternative.me's daily BTC sentiment as a separate research observation.

This is not CFGI and must never fill its MARKET/BTC/ETH fields. The daily
source timestamp is not proof of the first publication time.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

URL = "https://api.alternative.me/fng/?limit=1&format=json"
ATTRIBUTION = "Fear and Greed Index by Alternative.me: https://alternative.me/crypto/fear-and-greed-index/"


def normalize(payload: object, retrieved: datetime) -> dict:
    if retrieved.tzinfo is None or retrieved.utcoffset() is None:
        raise ValueError("RETRIEVAL_CLOCK_INVALID")
    retrieved = retrieved.astimezone(timezone.utc)
    if not isinstance(payload, dict) or not isinstance(payload.get("data"), list) or len(payload["data"]) != 1:
        raise ValueError("SOURCE_SHAPE_INVALID")
    row = payload["data"][0]
    if not isinstance(row, dict):
        raise ValueError("ROW_INVALID")
    value, timestamp = row.get("value"), row.get("timestamp")
    if not isinstance(value, str) or not value.isascii() or not value.isdigit() or not 0 <= int(value) <= 100:
        raise ValueError("SCORE_INVALID")
    if not isinstance(timestamp, str) or not timestamp.isascii() or not timestamp.isdigit():
        raise ValueError("SOURCE_CLOCK_INVALID")
    try:
        observed = datetime.fromtimestamp(int(timestamp), tz=timezone.utc)
    except (ValueError, OverflowError, OSError) as exc:
        raise ValueError("SOURCE_CLOCK_INVALID") from exc
    if observed > retrieved or retrieved - observed > timedelta(hours=48):
        raise ValueError("SOURCE_CLOCK_FUTURE_OR_STALE")
    classification = row.get("value_classification")
    if classification not in {"Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"}:
        raise ValueError("CLASSIFICATION_INVALID")
    return {"contract": "ALTERNATIVE_ME_SENTIMENT_OBSERVATION_v1", "source": "ALTERNATIVE_ME_FNG",
            "status": "PASS", "score": int(value), "classification": classification,
            "source_timestamp_utc": observed.isoformat().replace("+00:00", "Z"),
            "retrieved_at_utc": retrieved.isoformat().replace("+00:00", "Z"),
            "source_frequency": "1d", "source_first_known_at_utc": None,
            "attribution": ATTRIBUTION, "not_cfgi": True,
            "authority": "RESEARCH_ONLY_NOT_OFFICIAL_NOT_DECISION_INPUT"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    request = urllib.request.Request(URL, headers={"Accept": "application/json", "User-Agent": "Investering-Research-Sentiment/1.0"})
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read(65537)
    if len(raw) > 65536:
        raise ValueError("RESPONSE_TOO_LARGE")
    doc = normalize(json.loads(raw), datetime.now(timezone.utc))
    doc["source_response_sha256"] = hashlib.sha256(raw).hexdigest()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "owner_snapshot.json").write_text(json.dumps(doc, sort_keys=True) + "\n", encoding="utf-8")
    print("ALTERNATIVE_ME_SENTIMENT_CAPTURED_RESEARCH_ONLY")


if __name__ == "__main__":
    main()
