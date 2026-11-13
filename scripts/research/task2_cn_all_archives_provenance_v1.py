#!/usr/bin/env python3
"""Research-only full CN/Master-Monday/Task2 historical provenance census.

Never treats a recovered file, current blob or past price as proof of an
original issue, provider first-known or user first-delivered forecast.
All outputs are reproducible offline from the checked-out Archive repository.
"""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1"
SOURCE_INDEX = PROGRAM + "/ASTRA_HIGH_COMPLETE_RESEARCH_CN_SOURCE_INDEX_20261113_v1.json"
OUTCOME_INDEX = PROGRAM + "/ASTRA_HIGH_OUTCOME_AND_EARLY_WEEK_SOURCE_INDEX_20261113_v1.json"
ISO_RE = re.compile(r"W(\d\d)$")
RANGE_ASSETS = {"BTC": "btc", "ETH": "eth"}

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load_json(path: Path):
    if not path.is_file() or path.is_symlink():
        return None
    return json.loads(path.read_text(encoding="utf-8"))

def git_blob_sha(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


@lru_cache(maxsize=8)
def pinned_source_map(root: str) -> dict[str, str]:
    base = Path(root)
    src = load_json(base / SOURCE_INDEX)
    result = load_json(base / OUTCOME_INDEX)
    if not isinstance(src, dict) or not isinstance(result, dict):
        raise ValueError("PINNED_SOURCE_INDEX_UNAVAILABLE")
    if git_blob_sha((base / SOURCE_INDEX).read_bytes()) != "9027def6ed9db61b607841acaf046330a3a2c6e7":
        raise ValueError("SOURCE_INDEX_BLOB_CHANGED")
    if git_blob_sha((base / OUTCOME_INDEX).read_bytes()) != "9e3abc0d03709f033c091e9068a49d1edf474665":
        raise ValueError("OUTCOME_INDEX_BLOB_CHANGED")
    if src.get("source_tree_sha_at_inventory") != result.get("source_main_tree"):
        raise ValueError("SOURCE_TREE_IDENTITY_MISMATCH")
    values = {}
    for row in src.get("entries", []):
        key, blob = row["path"], row["blob"]
        if key in values: raise ValueError("DUPLICATE_SOURCE_PATH")
        values[key] = blob
    for row in result.get("entries", []):
        if row.get("type") != "file": continue
        key, blob = row["path"], row["blob_or_tree"]
        if key in values and values[key] != blob:
            raise ValueError("CONFLICTED_SOURCE_BLOB")
        values[key] = blob
    return values


def pinned_bytes(path: Path, repo_root: Path) -> bytes | None:
    rel = path.relative_to(repo_root).as_posix()
    expected = pinned_source_map(str(repo_root.resolve())).get(rel)
    if expected is None:
        if path.exists():
            raise ValueError("CURRENT_FILE_NOT_IN_FROZEN_INDEX:" + rel)
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("FROZEN_SOURCE_MISSING_OR_UNSAFE:" + rel)
    raw = path.read_bytes()
    if git_blob_sha(raw) != expected:
        raise ValueError("FROZEN_SOURCE_BYTES_DRIFT:" + rel)
    return raw


def pinned_json(path: Path, repo_root: Path):
    raw = pinned_bytes(path, repo_root)
    return json.loads(raw) if raw is not None else None


def next_monday(year: int, week: int) -> dt.datetime:
    d = dt.date.fromisocalendar(year, week, 1) + dt.timedelta(days=7)
    return dt.datetime.combine(d, dt.time(0), dt.timezone.utc)

def valid_number(value) -> bool:
    return type(value) in (int, float) and value == value and abs(value) < 1e12

def check_inventory(repo_root: Path) -> dict:
    index = load_json(repo_root / SOURCE_INDEX)
    outcomes = load_json(repo_root / OUTCOME_INDEX)
    if not isinstance(index, dict) or not isinstance(outcomes, dict):
        raise ValueError("ARCHIVE_INDEX_UNAVAILABLE")
    records = index.get("entries")
    if not isinstance(records, list) or len(records) != index.get("scan_total"):
        raise ValueError("SOURCE_INDEX_COUNT_DRIFT")
    paths = [x["path"] for x in records]
    if len(paths) != len(set(paths)):
        raise ValueError("DUPLICATE_SOURCE_PATH")
    if any(x.startswith("/") or ".." in Path(x).parts or ".github/secrets" in x
           for x in paths):
        raise ValueError("SOURCE_PATH_UNSAFE")
    if not all(re.fullmatch(r"[0-9a-f]{40}", x.get("blob", "")) for x in records):
        raise ValueError("SOURCE_BLOB_SHA_MISSING")
    if not any("research/historical_reality_engine/CROSS_ERA_NATIVE_RESULTS" in x for x in paths):
        raise ValueError("HRE_MISSING")
    if not any("06_RESEARCH_LAB/shared_row_model_tournament_v1" in x for x in paths):
        raise ValueError("TASK2_MODEL_NULL_MISSING")
    if not any("05_CYCLE_NAVIGATOR/published/2026" in x for x in paths):
        raise ValueError("LEGACY_CN_MISSING")
    return {"source_file_count": len(records),
            "source_file_categories": index.get("counts", {}),
            "source_index_sha256": sha256(repo_root / SOURCE_INDEX),
            "weekly_outcome_source_count": outcomes.get("entry_count"),
            "weekly_outcome_index_sha256": sha256(repo_root / OUTCOME_INDEX)}

def week_census(repo_root: Path, asof: dt.datetime) -> list[dict]:
    weeks_dir = repo_root / "05_CYCLE_NAVIGATOR/weekly"
    result = []
    for year_dir in sorted(weeks_dir.glob("[0-9][0-9][0-9][0-9]")):
        year = int(year_dir.name)
        for wdir in sorted(year_dir.glob("W[0-9][0-9]")):
            m = ISO_RE.fullmatch(wdir.name)
            if not m:
                continue
            week = int(m.group(1))
            forecast_file = wdir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
            forecast = pinned_json(forecast_file, repo_root)
            if forecast is None:
                continue
            internal_path = wdir / "CYCLE_NAVIGATOR_INTERNAL_PRECISION_FREEZE.json"
            internal = pinned_json(internal_path, repo_root)
            source_file = wdir / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json"
            source = pinned_json(source_file, repo_root)
            pointer_file = wdir / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json"
            delivery = pinned_json(pointer_file, repo_root)
            actual_file = repo_root / f"03_DAILY_CAPTURE_LOGS/weekly/{year}/{wdir.name}.json"
            actual = pinned_json(actual_file, repo_root)
            seq = (actual or {}).get("hourly_sequence") or {}
            observed = seq.get("observed_hourly_rows")
            expected = seq.get("expected_hourly_rows")
            complete = (
                next_monday(year, week) <= asof
                and observed == 168 and expected == 168
                and bool((actual or {}).get("generated_at_utc"))
            )
            claims = (internal or {}).get("claims") or []
            if not isinstance(claims, list):
                raise ValueError("INTERNAL_CLAIMS_INVALID:" + wdir.name)
            issued = {}
            for asset, prefix in RANGE_ASSETS.items():
                lo = forecast.get(prefix + "_range_low")
                hi = forecast.get(prefix + "_range_high")
                numeric_range = valid_number(lo) and valid_number(hi) and lo < hi
                daily = ((forecast.get("daily_price_path") or {}).get(asset) or {})
                pack = (seq.get(prefix) or {}).get("week_range") or {}
                issued[asset] = {
                    "range_issued": bool(numeric_range),
                    "low": lo if numeric_range else None,
                    "high": hi if numeric_range else None,
                    "daily_status": daily.get("status", "NOT_ISSUED"),
                    "daily_count": len(daily.get("points") or []),
                    "matured_actual_week": bool(complete and valid_number(pack.get("close"))),
                    "weekly_realized": {
                        k: pack.get(k) if complete and valid_number(pack.get(k)) else None
                        for k in ("open", "high", "low", "close")
                    },
                }
            result.append({
                "iso_week": f"{year}-W{week:02d}",
                "source_forecast_sha256": sha256(forecast_file),
                "source_internal_sha256": sha256(internal_path) if internal_path.exists() else None,
                "source_manifest_sha256": sha256(source_file) if source_file.exists() else None,
                "source_actual_sha256": sha256(actual_file) if actual_file.exists() else None,
                "issue_number": (source or {}).get("issue_number"),
                "source_master_monday_dir": (source or {}).get("master_monday_dir"),
                "delivery_status": (delivery or {}).get("status", "UNKNOWN"),
                "provider_first_published": "UNKNOWN",
                "model_original_first_issue": "UNKNOWN",
                "consumer_first_delivered": "UNKNOWN",
                "recovered_or_amended_original_provenance": "REQUIRES_HISTORY_PROOF",
                "maturity": "MATURED_168H_RETROSPECTIVE" if complete else "UNMATURED_OR_GAPPED",
                "observed_hours": observed,
                "expected_hours": expected,
                "internal_claim_count": len(claims),
                "internal_non_alias_count": sum(not item.get("alias_of") for item in claims),
                "internal_alias_count": sum(bool(item.get("alias_of")) for item in claims),
                "assets": issued,
                "statistical_claim": "NONE_PIT_UNVERIFIED",
            })
    return result

def legacy_census(repo_root: Path) -> list[dict]:
    root = repo_root / "05_CYCLE_NAVIGATOR/published/2026"
    result = []
    expected = {p for p in pinned_source_map(str(repo_root.resolve()))
                if p.startswith("05_CYCLE_NAVIGATOR/published/2026/")}
    current = {p.relative_to(repo_root).as_posix() for p in root.glob("*")
               if p.is_file() and p.suffix in {".md", ".json"}}
    if current != expected:
        raise ValueError("LEGACY_ARCHIVE_SOURCE_SET_DRIFT")
    for path in sorted(root.glob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json"}:
            continue
        name = path.name
        pinned_raw = pinned_bytes(path, repo_root)
        result.append({
            "path": path.relative_to(repo_root).as_posix(),
            "sha256": hashlib.sha256(pinned_raw).hexdigest(),
            "recovered": "_RECOVERED" in name or "RECOVERY" in name,
            "publication_issue_time": "UNKNOWN_NOT_PROVEN",
            "numeric_forecast_eligible": False,
            "reason": "RECOVERED_NOT_ISSUED" if "_RECOVERED" in name else "ORIGINAL_DELIVERY_PROOF_REQUIRED",
        })
    return result

def archive_membership(repo_root: Path) -> dict:
    def members(pat):
        return sorted(p.relative_to(repo_root).as_posix()
                      for p in repo_root.glob(pat) if p.is_file())
    return {
        "original_monday_documents": members("03_WEEKLY_OPERATIONS/master_monday/**/*"),
        "older_official_forecast_ledgers": members("03_WEEKLY_OPERATIONS/forecast_ledger/**/*"),
        "2026_weekly_raw_outcome_packs": members("03_DAILY_CAPTURE_LOGS/weekly/2026/W*.json"),
        "historical_reality_engine_files": members("research/historical_reality_engine/*"),
        "research_parallel_lanes_files": members(".agents/skills/research-parallel-lanes/**/*"),
        "cn_internal_parameter_ledgers": members("05_CYCLE_NAVIGATOR/track_record/*"),
        "cn_forward_range_ledgers": members("05_CYCLE_NAVIGATOR/forward_range_ledger/*"),
    }

def optional_realdata(extra: Path | None) -> dict:
    expected = {
        "forecast_rows.csv": ("50cfcf031b788a9105b7867d43271fa0a3b1206c1949626421311ddd253c89f0", 112),
        "risk_rows.csv": ("325912c52444893cb7c2d6821a7d98212418c22345162e9e1facdfcd40f54f57", 96),
    }
    result = {}
    for name, (digest, nrows) in expected.items():
        p = extra / name if extra else None
        if p is None or not p.exists():
            result[name] = {"status": "NOT_ATTACHED", "required_sha256": digest}
            continue
        if sha256(p) != digest:
            raise ValueError("REALDATA_ARTIFACT_HASH_MISMATCH:" + name)
        with p.open(newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        if len(rows) != nrows:
            raise ValueError("REALDATA_ROW_COUNT_MISMATCH:" + name)
        result[name] = {"status": "VERIFIED", "sha256": digest, "rows": nrows}
    return result

def generate(repo_root: Path, asof: dt.datetime, extra: Path | None = None):
    index = check_inventory(repo_root)
    weekly = week_census(repo_root, asof)
    legacy = legacy_census(repo_root)
    membership = archive_membership(repo_root)
    if not weekly:
        raise ValueError("CN_WEEKLY_CENSUS_EMPTY")
    eligible = [x for x in weekly if x["maturity"] == "MATURED_168H_RETROSPECTIVE"]
    return {
        "contract": "TASK2_ASTYRA_ALL_ARCHIVES_PROVENANCE_CENSUS_v1",
        "authority": "RESEARCH_NO_MODEL_OR_PORTFOLIO_PROMOTION",
        "asof_utc": asof.isoformat().replace("+00:00", "Z"),
        "source_index": index,
        "coverage": {
            "cn_weekly_freezes": len(weekly),
            "cn_weekly_mature_168h": len(eligible),
            "cn_weekly_unmature_or_gapped": len(weekly)-len(eligible),
            "cn_internal_precision_weeks": sum(x["internal_claim_count"]>0 for x in weekly),
            "cn_legacy_published_files": len(legacy),
            "cn_legacy_recovered_files": sum(x["recovered"] for x in legacy),
            "cn_numeric_forecast_btc_weeks": sum(x["assets"]["BTC"]["range_issued"] for x in weekly),
            "cn_numeric_mature_btc_weeks": sum(x["assets"]["BTC"]["range_issued"] and x["maturity"]=="MATURED_168H_RETROSPECTIVE" for x in weekly),
            "legacy_monday_files": len(membership["original_monday_documents"]),
            "weekly_raw_outcome_packs": len(membership["2026_weekly_raw_outcome_packs"]),
        },
        "source_membership": membership,
        "legacy_published": legacy,
        "weekly": weekly,
        "realdata_verified": optional_realdata(extra),
        "scientific_nulls": [
            "CN range coverage without first-known and user delivery is NOT verified forecast skill",
            "W46 not mature before Monday 2026-11-16",
            "Recovered May-Aug historical reports are NOT automatically ex-ante",
            "Overlapping 14 claims and alias families are NOT independent observations",
            "Fable R5 W47 is prospectively data-gated and not copied",
            "W39-W45 PR2113 row-level comparison and 1176h risk replay remain separate source artifacts",
            "A price-only -3% 24h condition is NOT an original 3/5/4/5 Kompas warning",
        ],
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--asof", default="2026-11-13T12:59:00Z")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--extra-artifacts", type=Path)
    args = ap.parse_args()
    when = dt.datetime.fromisoformat(args.asof.replace("Z", "+00:00"))
    if when.tzinfo is None:
        raise ValueError("ASOF_OFFSET_REQUIRED")
    output = generate(ROOT, when, args.extra_artifacts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    c=output["coverage"]
    print("TASK2_CN_ALL_ARCHIVES_PASS", json.dumps(c, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
