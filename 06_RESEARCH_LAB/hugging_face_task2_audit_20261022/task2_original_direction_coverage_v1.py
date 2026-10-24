#!/usr/bin/env python3
"""Recompute original Compass as-issued label coverage from immutable Git objects.

Research only. No market outcomes, prices, provider secrets, model scoring, PIT
promotion, first-delivery claims, trading authority or billable data access.
A source Git snapshot proves object membership, not provider first-known.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Callable

CONTRACT = "TASK2_ORIGINAL_DIRECTION_COVERAGE_REPLAY_v1"
HORIZONS = ("NEXT_12H", "NEXT_1_3D", "NEXT_5_7D")
DIRECTIONS = {"UP", "DOWN", "MIXED", "UNAVAILABLE", "SIDEWAYS", "NO_EDGE"}
SOURCE = re.compile(r"04_MARKET_LEARNING/handlekompas/official/daily/2026/10/(1[2-9]|20)/(CMP-202610\d{2}-[0-9a-f]{12})\.json\Z")
SHA40 = re.compile(r"[0-9a-f]{40}\Z")

def sha_blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

def utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("ISSUE_NOT_EXACT_UTC")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def read_git(repo: Path, ref: str, path: str) -> bytes:
    if not SHA40.fullmatch(ref):
        raise ValueError("REF_NOT_IMMUTABLE_SHA40")
    if path.startswith("/") or ".." in Path(path).parts or "\\" in path or ":" in path:
        raise ValueError("UNSAFE_GIT_PATH")
    return subprocess.run(
        ["git", "--no-replace-objects", "show", f"{ref}:{path}"],
        cwd=repo, check=True, capture_output=True
    ).stdout

def audit(census: dict, loader: Callable[[str, str], bytes], *, expected_originals: int = 70) -> dict:
    ref = census.get("execution_source_commit_sha")
    if not isinstance(ref, str) or not SHA40.fullmatch(ref):
        raise ValueError("ORIGINAL_SOURCE_PIN_MISSING")
    records = census.get("original_records")
    if not isinstance(records, list):
        raise ValueError("ORIGINAL_CENSUS_ROWS_MISSING")
    grouped = defaultdict(dict)
    for record in records:
        path = record.get("original_forecast_path")
        horizon = record.get("horizon")
        if not isinstance(path, str) or not SOURCE.fullmatch(path):
            raise ValueError("UNEXPECTED_ORIGINAL_PATH")
        if horizon not in {"12h", "72h", "168h"} or horizon in grouped[path]:
            raise ValueError("DUPLICATE_OR_INVALID_ORIGINAL_HORIZON")
        grouped[path][horizon] = record
    if len(grouped) != expected_originals or any(
        set(row) != {"12h", "72h", "168h"} for row in grouped.values()
    ):
        raise ValueError("ORIGINAL_DENOMINATOR_INCOMPLETE")
    per_day = defaultdict(lambda: {"original_forecasts": 0, **{h: Counter() for h in HORIZONS}})
    horizon_counts = {h: Counter() for h in HORIZONS}
    freshness = Counter()
    versions = Counter()
    cn_packages = Counter()
    causes = Counter()
    receipts = []
    for path, attempts in sorted(grouped.items()):
        match = SOURCE.fullmatch(path)
        raw = loader(ref, path)
        blob = sha_blob(raw)
        if {row.get("original_forecast_git_blob_sha1") for row in attempts.values()} != {blob}:
            raise ValueError("ORIGINAL_FORECAST_GIT_BLOB_MISMATCH")
        original = json.loads(raw)
        if original.get("compass_id") != match.group(2):
            raise ValueError("ORIGINAL_ISSUE_ID_MISMATCH")
        issued = utc(original.get("issued_at_utc"))
        if issued.strftime("%Y%m%d") != "202610" + match.group(1):
            raise ValueError("ORIGINAL_ISSUE_DAY_MISMATCH")
        version = original.get("scoring_contract")
        if {row.get("scoring_contract") for row in attempts.values()} != {version}:
            raise ValueError("ORIGINAL_SCORING_VERSION_MISMATCH")
        bindings = original.get("source_bindings") or {}
        market = bindings.get("auto_market_state") or {}
        cn = (bindings.get("cycle_navigator") or {}).get("machine_package") or {}
        # CN is loaded by the original Official producer from its own checkout,
        # independently of the older auto-packet's upstream input snapshot.
        # In the first Oct12 issue, W42 does not yet exist in the auto snapshot.
        cn_ref = original.get("bound_main_sha")
        cn_path = cn.get("path")
        cn_blob = cn.get("git_blob_sha")
        if (not isinstance(cn_ref, str) or not SHA40.fullmatch(cn_ref)
                or not isinstance(cn_path, str)
                or not cn_path.startswith("05_CYCLE_NAVIGATOR/weekly/")
                or not isinstance(cn_blob, str) or not SHA40.fullmatch(cn_blob)):
            raise ValueError("ORIGINAL_CN_BINDING_INVALID")
        cn_raw = loader(cn_ref, cn_path)
        if sha_blob(cn_raw) != cn_blob:
            raise ValueError("CN_INPUT_SOURCE_SNAPSHOT_BLOB_MISMATCH")
        cn_doc = json.loads(cn_raw)
        if cn_doc.get("contract") != "CYCLE_NAVIGATOR_MACHINE_PACKAGE_v1":
            raise ValueError("ORIGINAL_CN_CONTRACT_MISMATCH")
        cn_generated = cn_doc.get("generated_unix")
        if not isinstance(cn_generated, int) or cn_generated > issued.timestamp():
            raise ValueError("ORIGINAL_CN_GENERATION_AFTER_ISSUE")
        fresh = (market.get("freshness") or {}).get("status")
        if fresh not in {"PASS", "STALE_OR_UNAVAILABLE"}:
            raise ValueError("UNKNOWN_ORIGINAL_FRESHNESS")
        original_directions = {}
        day = issued.strftime("%Y-%m-%d")
        for key in HORIZONS:
            direction = ((original.get("horizons") or {}).get(key) or {}).get("expected_direction")
            if direction not in DIRECTIONS:
                raise ValueError("UNKNOWN_ORIGINAL_DIRECTION")
            original_directions[key] = direction
            horizon_counts[key][direction] += 1
            per_day[day][key][direction] += 1
        if fresh == "STALE_OR_UNAVAILABLE":
            if any(v != "UNAVAILABLE" for v in original_directions.values()):
                raise ValueError("STALE_FORECAST_FAILED_TO_ABSTAIN")
            causes["STALE_FAILCLOSED"] += 1
        elif original_directions["NEXT_12H"] == "UNAVAILABLE":
            if (original.get("market_now") or {}).get("directional_state") != "UNCHANGED_NO_NEW_OBSERVATION":
                raise ValueError("FRESH_UNAVAILABLE_UNEXPLAINED")
            causes["NO_NEW_OBSERVATION"] += 1
        per_day[day]["original_forecasts"] += 1
        freshness[fresh] += 1
        versions[version] += 1
        cn_packages[cn_blob] += 1
        receipts.append({"path": path, "git_blob_sha1": blob,
                         "cn_source_commit": cn_ref, "cn_source_blob_sha1": cn_blob})
    return {
        "contract": CONTRACT,
        "status": "RESEARCH_ONLY_NOT_R1_ADMITTED",
        "original_source_commit": ref,
        "original_forecasts": len(grouped),
        "original_horizon_attempts": len(records),
        "label_counts": {h: dict(v) for h, v in horizon_counts.items()},
        "directional_counts": {h: v["UP"] + v["DOWN"] for h, v in horizon_counts.items()},
        "freshness_counts": dict(freshness),
        "source_failclosed_causes": dict(causes),
        "scoring_versions": dict(versions),
        "original_cn_blob_counts": dict(cn_packages),
        "per_day": {
            day: {k: dict(v) if isinstance(v, Counter) else v for k, v in data.items()}
            for day, data in sorted(per_day.items())
        },
        "forecast_receipts": receipts,
        "original_outcomes_read": False,
        "first_known_certified": False,
        "independent_events_certified": False,
        "scoring_or_portfolio_actions_performed": False,
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--expected-count", type=int, default=70)
    args = parser.parse_args()
    source = json.loads(args.census.read_text(encoding="utf-8"))
    result = audit(source, lambda ref, path: read_git(args.repo_root, ref, path),
                   expected_originals=args.expected_count)
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
