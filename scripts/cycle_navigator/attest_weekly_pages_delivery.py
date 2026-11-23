#!/usr/bin/env python3
"""One durable original Monday source -> GitHub Pages CDN release receipt.

The existing native Pages workflow invokes this only AFTER its actual CDN
SHA-256 parity checker succeeds. No new Actions trigger, forecast, paid API,
GitHub main writer, portfolio action or mutation of original frozen sources.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

REPO = "Donh91/Investering-Framework-Archive-v1"
ISSUE = 1593
RECEIPT_CONTRACT = "CN_MONDAY_PAGES_DELIVERY_v1"


class ReleaseError(ValueError):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ReleaseError(code)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "CN_RELEASE_JSON_OBJECT_REQUIRED")
    return value


def parse_utc(value: str) -> dt.datetime:
    result = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None, "CN_RELEASE_TIMEZONE_REQUIRED")
    return result.astimezone(dt.timezone.utc)


def make_proof(doc: dict, root: Path, checked_at: dt.datetime | None = None) -> dict | None:
    """Pure evidence reconciliation; None means an old release, not new Monday PASS."""
    require(doc.get("contract") == "CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1" and doc.get("status") == "PASS",
            "CN_RELEASE_CDN_PARITY_NOT_PASS")
    original = doc.get("original_weekly_product") or {}
    week = original.get("forecast_week")
    require(isinstance(week, str) and re.fullmatch(r"20\d{2}-W\d{2}", week),
            "CN_RELEASE_WEEK_INVALID")
    year, w = map(int, week.split("-W"))
    try:
        monday = dt.datetime.combine(dt.date.fromisocalendar(year, w, 1),
                                     dt.time.min, dt.timezone.utc)
    except ValueError as exc:
        raise ReleaseError("CN_RELEASE_WEEK_INVALID") from exc
    require(original.get("seven_day_product") == "COMPLETE", "CN_RELEASE_ORIGINAL_NOT_COMPLETE")
    require(re.fullmatch(r"[a-f0-9]{64}", original.get("source_forecast_freeze_sha256") or "")
            is not None, "CN_RELEASE_ORIGINAL_SHA_INVALID")
    issued = parse_utc(str(original.get("issued_at_utc") or ""))
    checked = checked_at or parse_utc(doc["checked_at_utc"])
    require(monday <= issued < monday + dt.timedelta(days=1),
            "CN_RELEASE_FIRST_ORIGINAL_ISSUANCE_OUTSIDE_MONDAY")
    require(checked >= issued, "CN_RELEASE_CDN_BEFORE_ORIGINAL")
    if checked - issued > dt.timedelta(hours=36):
        return None  # A late site rebuild is NOT a new weekly release.

    path = "data/public-freezes/" + str(year) + "/W" + f"{w:02d}" + "/CN"
    require(type(original.get("public_issue_number")) is int and original["public_issue_number"] > 0,
            "CN_RELEASE_PUBLIC_ISSUE_INVALID")
    path += str(original["public_issue_number"]) + "_PUBLIC_FREEZE.json"
    require(original.get("path") == path, "CN_RELEASE_FREEZE_PUBLIC_PATH_MISMATCH")
    rows = doc.get("files")
    require(isinstance(rows, list) and len(rows) >= 25, "CN_RELEASE_CDN_CENSUS_INCOMPLETE")
    required = ("data/latest.json", "data/publication-lineage.json", path)
    matched = {}
    for row in rows:
        if row.get("path") in required:
            require(row.get("status") == "PASS" and row.get("http_status") == 200 and
                    isinstance(row.get("expected_sha256"), str) and
                    row.get("expected_sha256") == row.get("served_sha256"),
                    "CN_RELEASE_SELECTED_CDN_BYTES_MISMATCH")
            require(row["path"] not in matched, "CN_RELEASE_DUPLICATE_CDN_ASSET")
            matched[row["path"]] = row["served_sha256"]
    require(len(matched) == len(required), "CN_RELEASE_REQUIRED_CDN_ASSET_MISSING")

    source_path = (root / "05_CYCLE_NAVIGATOR/weekly" / str(year) /
                   f"W{w:02d}" / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    source_bytes = source_path.read_bytes()
    source_sha = hashlib.sha256(source_bytes).hexdigest()
    require(source_sha == original["source_forecast_freeze_sha256"],
            "CN_RELEASE_ORIGINAL_REPO_SHA_MISMATCH")
    source = json.loads(source_bytes)
    snapshot = read_json(root / "05_CYCLE_NAVIGATOR/site/dist/data/latest.json")
    precision = snapshot.get("public_live_precision") or {}
    require(precision.get("forecast_week") == week and
            precision.get("public_issue_number") == original["public_issue_number"] and
            precision.get("freeze_sha256") == source_sha,
            "CN_RELEASE_SITE_ORIGINAL_IDENTITY_MISMATCH")
    public_receipt = read_json(root / "05_CYCLE_NAVIGATOR/site/dist" / path)
    require(public_receipt.get("source_forecast_freeze_sha256") == source_sha,
            "CN_RELEASE_PUBLIC_RECEIPT_ORIGINAL_SHA_MISMATCH")
    require(precision.get("daily_product_acceptance") ==
            public_receipt.get("daily_product_acceptance"),
            "CN_RELEASE_ACCEPTANCE_SOURCE_MISMATCH")
    for name in ("daily_price_path", "daily_range_plan"):
        require(precision.get(name) == source.get(name),
                "CN_RELEASE_ORIGINAL_DAILY_VALUES_DIVERGED_" + name.upper())
        for asset in ("BTC", "ETH"):
            points = (precision.get(name) or {}).get(asset, {}).get("points")
            require(isinstance(points, list) and len(points) == 7 and
                    [p.get("day") for p in points] == list(range(1, 8)),
                    "CN_RELEASE_ORIGINAL_DAILY_POINTS_INVALID_" + name.upper() + "_" + asset)

    return {
        "contract": RECEIPT_CONTRACT,
        "status": "COMPLETE_VERIFIED",
        "week": week,
        "original_issued_at_utc": issued.isoformat().replace("+00:00", "Z"),
        "cdn_checked_at_utc": checked.isoformat().replace("+00:00", "Z"),
        "source_freeze_sha256": source_sha,
        "public_issue_number": original["public_issue_number"],
        "site_checkout_sha": doc.get("built_checkout_sha"),
        "pages_run_id": int(os.environ.get("GITHUB_RUN_ID") or "0"),
        "source_to_cdn_sha256": matched,
        "asset_count_verified": len(rows),
        "authority": "PUBLIC_DELIVERY_ONLY_NO_FORECAST_SKILL_OR_PORTFOLIO_AUTHORITY",
        "source_owner": "Archive #1516",
        "closure_owner": "Archive #1593",
    }


def gh(*args: str) -> str:
    return subprocess.run(["gh", "api", *args], check=True,
                          capture_output=True, text=True).stdout


def publish(proof: dict) -> None:
    require(os.environ.get("GITHUB_REPOSITORY") == REPO, "CN_RELEASE_REPOSITORY_NOT_ALLOWED")
    require(bool(os.environ.get("GH_TOKEN")), "CN_RELEASE_TOKEN_MISSING")
    week = proof["week"]
    marker = f"<!-- {RECEIPT_CONTRACT}:{week} -->"
    body = marker + "\n\n~~~json\n" + json.dumps(proof, sort_keys=True, separators=(",", ":")) + "\n~~~\n"
    comments = gh(f"repos/{REPO}/issues/{ISSUE}/comments?per_page=100", "--paginate", "--jq",
                  '.[] | select(.user.login=="github-actions[bot]") | .body')
    if marker in comments:
        found = re.findall(re.escape(marker) + r"\s*~~~json\s*(\{[^\n]+\})\s*~~~", comments)
        require(len(found) == 1, "CN_RELEASE_EXISTING_COMMENT_AMBIGUOUS")
        old = json.loads(found[0])
        require(old.get("status") == "COMPLETE_VERIFIED" and
                old.get("source_freeze_sha256") == proof["source_freeze_sha256"] and
                old.get("public_issue_number") == proof["public_issue_number"],
                "CN_RELEASE_FROZEN_WEEK_CONFLICT")
        print(f"CN_MONDAY_PAGES_ALREADY_PERSISTED week={week}")
        return
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump({"body": body}, f)
        temp_path = f.name
    try:
        created = json.loads(gh("-X", "POST", f"repos/{REPO}/issues/{ISSUE}/comments",
                               "--input", temp_path))
    finally:
        Path(temp_path).unlink(missing_ok=True)
    comment_id = created.get("id")
    require(type(comment_id) is int and created.get("body") == body,
            "CN_RELEASE_POST_NOT_VERIFIED")
    readback = json.loads(gh(f"repos/{REPO}/issues/comments/{comment_id}"))
    require(readback.get("body") == body, "CN_RELEASE_COMMENT_READBACK_MISMATCH")
    print(f"CN_MONDAY_PAGES_DELIVERY_PERSISTED week={week} issue={ISSUE} comment_id={comment_id}")


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        week = "2026-W48"
        public = "data/public-freezes/2026/W48/CN35_PUBLIC_FREEZE.json"
        src = root / "05_CYCLE_NAVIGATOR/weekly/2026/W48/CYCLE_NAVIGATOR_FORECAST_FREEZE.json"
        src.parent.mkdir(parents=True)
        source = {
            "daily_price_path": {a: {"points": [{"day": d, "expected_close": 100.0+d}
                for d in range(1, 8)]} for a in ("BTC", "ETH")},
            "daily_range_plan": {a: {"points": [{"day": d, "low": 90+d, "high": 110+d}
                for d in range(1, 8)]} for a in ("BTC", "ETH")},
        }
        src.write_text(json.dumps(source, sort_keys=True, separators=(",", ":")) + "\n")
        digest = hashlib.sha256(src.read_bytes()).hexdigest()
        acceptance = {"contract": "CN_MONDAY_SEVEN_DAY_PRODUCT_ACCEPTANCE_v1",
                      "status": "COMPLETE", "forecast_week": week}
        precision = {"forecast_week": week, "public_issue_number": 35,
                     "freeze_sha256": digest, "daily_product_acceptance": acceptance,
                     **source}
        dist = root / "05_CYCLE_NAVIGATOR/site/dist"
        (dist / "data").mkdir(parents=True)
        (dist / public).parent.mkdir(parents=True)
        (dist / "data/latest.json").write_text(json.dumps({"public_live_precision": precision}))
        (dist / public).write_text(json.dumps({"source_forecast_freeze_sha256": digest,
                                              "daily_product_acceptance": acceptance}))
        original = {"seven_day_product": "COMPLETE", "forecast_week": week,
                    "source_forecast_freeze_sha256": digest, "public_issue_number": 35,
                    "path": public, "issued_at_utc": "2026-11-23T09:46:18Z"}
        expected = ["data/latest.json", "data/publication-lineage.json", public]
        rows = [{"path": p, "status": "PASS", "http_status": 200,
                 "expected_sha256": "a"*64, "served_sha256": "a"*64}
                for p in expected + [f"next/{i}.js" for i in range(22)]]
        doc = {"contract": "CN_PAGES_ARTIFACT_TO_CDN_PARITY_v1", "status": "PASS",
               "checked_at_utc": "2026-11-23T09:50:34Z", "built_checkout_sha": "b"*40,
               "original_weekly_product": original, "files": rows}
        assert make_proof(doc, root)["status"] == "COMPLETE_VERIFIED"
        for field, changed, code in [
            ("status", "DEGRADED", "CN_RELEASE_CDN_PARITY_NOT_PASS"),
            ("original_weekly_product", {**original, "source_forecast_freeze_sha256": "b"*64},
             "CN_RELEASE_ORIGINAL_REPO_SHA_MISMATCH"),
            ("original_weekly_product", {**original, "forecast_week": "2026-W49"},
             "CN_RELEASE_FIRST_ORIGINAL_ISSUANCE_OUTSIDE_MONDAY"),
            ("original_weekly_product", {**original, "seven_day_product": "INCOMPLETE"},
             "CN_RELEASE_ORIGINAL_NOT_COMPLETE"),
            ("files", rows[:-1], "CN_RELEASE_CDN_CENSUS_INCOMPLETE"),
            ("files", [{**rows[0], "status": "MISMATCH"}]+rows[1:],
             "CN_RELEASE_SELECTED_CDN_BYTES_MISMATCH"),
        ]:
            sample = {**doc, field: changed}
            try:
                make_proof(sample, root)
            except ReleaseError as exc:
                assert str(exc) == code, (code, str(exc))
            else:
                raise AssertionError("MISSING_NEGATIVE_GUARD " + code)
        changed = copy.deepcopy(doc)
        changed["files"] = [x for x in rows if x["path"] != public]
        try:
            make_proof(changed, root)
        except ReleaseError as exc:
            assert str(exc) == "CN_RELEASE_CDN_CENSUS_INCOMPLETE"
        else:
            raise AssertionError("MISSING_CDN_FREEZE_GUARD")
        changed = copy.deepcopy(doc)
        changed["files"] = [*rows, {**rows[0], "path": "additional"}]
        changed["files"][2]["served_sha256"] = "f"*64
        try:
            make_proof(changed, root)
        except ReleaseError as exc:
            assert str(exc) == "CN_RELEASE_SELECTED_CDN_BYTES_MISMATCH"
        else:
            raise AssertionError("MISSING_EXACT_CDN_BYTE_GUARD")
        assert make_proof(doc, root,
            dt.datetime(2026, 11, 25, 9, 50, tzinfo=dt.timezone.utc)) is None
    print("CN_MONDAY_DELIVERY_SELF_TEST_PASS positive+replay+8_negative")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--receipt", type=Path, default=Path("runtime_cn_pages_release_receipt.json"))
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    doc = read_json(args.receipt)
    proof = make_proof(doc, args.root)
    if proof is None:
        print("CN_MONDAY_RELEASE_OLDER_THAN_WINDOW: no new producer receipt")
        return
    publish(proof)


if __name__ == "__main__":
    main()
