"""One-shot W46 original-owner correction of UNISSUED daily closes.

Owner explicitly approved a same-Monday revision on 2026-11-09. Existing
W46 0/7 source freeze is preserved byte-for-byte as an immutable revision.
The only allowed replacement is its missing 7 BTC/ETH daily expected closes
before the first UTC daily outcome. Forecast window/bands/scoring are held
identical. No model API, secret persistence or new workflow required.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import re
import subprocess
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from scripts.cycle_navigator.daily_path_recovery import reject_unverified_initial_daily_quotes
from scripts.cycle_navigator.daily_price_journey import (
    daily_product_acceptance, validate_daily_path, validate_daily_range_plan)
from scripts.cycle_navigator.price_input_attestation import attest_completed_week, PriceEvidenceError
from scripts.cycle_navigator.weekly_offline_issuer import build_offline_value

CONTRACT = "CN_OWNER_APPROVED_W46_SAME_DAY_REISSUE_v1"
REQUEST = "05_CYCLE_NAVIGATOR/weekly/2026/W46/W46_OWNER_REISSUE_REQUEST.json"
BEFORE = "05_CYCLE_NAVIGATOR/weekly/2026/W46/revisions/2026-11-09-first-unavailable"
MISSING = "OWNER_W46_REVISION_PENDING"
OUTPUT_FILES = (
    "CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
    "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json",
    "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json",
    "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json",
    "CYCLE_NAVIGATOR_PUBLIC_SERIES_BINDING.json",
    "CYCLE_NAVIGATOR_DELIVERY_POINTER.json",
    "CYCLE_NAVIGATOR_API_RECEIPT.json",
    "CYCLE_NAVIGATOR_READABLE.md",
    "CYCLE_NAVIGATOR_X_READY.md",
    "CYCLE_NAVIGATOR_SCORECARD.json",
)


def _read(path: Path):
    return json.loads(path.read_text())


def _canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n").encode()


def _sha(body):
    return hashlib.sha256(body).hexdigest()


def _checkout_read_token(repo: Path):
    """Reuse only this Actions checkout's already authorized token, in memory.

    A legacy weekly job's YAML may omit the GITHUB_TOKEN env variable. Checkout
    v4 stores an ephemeral scoped HTTP extraheader for its own git push. Read
    it ONLY on GitHub Actions in this exact repository. Never log/tokenize,
    persist, broaden or print credentials. Do not use non-Actions machines.
    """
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        return token
    if (os.environ.get("GITHUB_ACTIONS") != "true"
            or os.environ.get("GITHUB_REPOSITORY") != "Donh91/Investering-Framework-Archive-v1"):
        raise PriceEvidenceError("SOURCE_ARTIFACT_AUTH_UNAVAILABLE")
    try:
        p = subprocess.run(
            ["git", "-C", str(repo), "config", "--local", "--get",
             "http.https://github.com/.extraheader"],
            capture_output=True, check=False, timeout=8, text=True)
        if p.returncode:
            raise ValueError("MISSING_CHECKOUT_CREDENTIAL")
        for line in p.stdout.splitlines():
            m = re.fullmatch(r"AUTHORIZATION:\s*basic\s+([A-Za-z0-9+/=]+)",
                             line.strip(), flags=re.I)
            if m:
                decoded = base64.b64decode(m.group(1), validate=True).decode("ascii")
                if decoded.startswith("x-access-token:") and len(decoded) > 20:
                    return decoded.split(":", 1)[1]
    except (OSError, UnicodeError, ValueError, subprocess.TimeoutExpired):
        pass
    raise PriceEvidenceError("SOURCE_ARTIFACT_AUTH_UNAVAILABLE")


def _guard(repo, pointer, mm_ptr, *, now):
    """Fail closed except the original W46 missing 0/7 published today."""
    target = repo / "05_CYCLE_NAVIGATOR/weekly/2026/W46"
    req_path = repo / REQUEST
    if (now.tzinfo is None or now.astimezone(timezone.utc).date() != date(2026, 11, 9)
            or not (datetime(2026, 11, 9, tzinfo=timezone.utc) <= now
                    < datetime(2026, 11, 10, tzinfo=timezone.utc))
            or (mm_ptr.get("iso_year"), mm_ptr.get("iso_week")) != (2026, 45)
            or pointer.get("contract") != "CYCLE_NAVIGATOR_DELIVERY_POINTER_v1"
            or (pointer.get("iso_year"), pointer.get("iso_week")) != (2026, 46)
            or (pointer.get("completed_source_year"), pointer.get("completed_source_week")) != (2026, 45)
            or (pointer.get("issue_number"), pointer.get("public_issue_number")) != (34, 33)
            or pointer.get("master_monday_pointer_sha256") != MISSING
            or pointer.get("owner_reissue_request") != REQUEST
            or not req_path.is_file()
            or (repo / BEFORE).exists()):
        raise ValueError("W46_OWNER_REISSUE_NOT_AUTHORIZED_FOR_THIS_CLOCK_OR_STATE")
    request = _read(req_path)
    old_bytes = (target / OUTPUT_FILES[0]).read_bytes()
    old = json.loads(old_bytes)
    original_pointer = _read(target / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
    original_receipt = _read(target / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json")
    source = _read(target / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json")
    if (request.get("contract") != CONTRACT
            or request.get("owner_scope") != "2026-W46"
            or request.get("original_forecast_sha256") != _sha(_canonical(old))
            or request.get("original_issue_unix") != original_receipt.get("frozen_unix")
            or request.get("keep_original_revision") is not True
            or original_pointer.get("forecast_freeze_sha256") != request["original_forecast_sha256"]
            or original_pointer.get("master_monday_pointer_sha256") !=
                _sha((repo / "research/api_agent/outputs/weekly/LATEST_MASTER_MONDAY_DELIVERY_POINTER.json").read_bytes())
            or original_receipt.get("daily_product_acceptance", {}).get("status") != "INCOMPLETE"
            or not (date.fromtimestamp(original_receipt.get("frozen_unix"),tz=timezone.utc) == date(2026,11,9))
            or _read(target / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").get("public_issue_number") != 33
            or source.get("original_price_product_diagnostic", {}).get(
                "pre_model_original_price_attestation", {}).get("reason") != "SOURCE_ARTIFACT_AUTH_UNAVAILABLE"):
        raise ValueError("W46_ORIGINAL_INCOMPLETE_SOURCE_RECEIPT_MISMATCH")
    for asset in ("BTC", "ETH"):
        if (old.get("daily_price_path",{}).get(asset,{}).get("status") != "UNAVAILABLE"
                or old.get("daily_price_path",{}).get(asset,{}).get("points") != []
                or old.get("daily_range_plan",{}).get(asset,{}).get("status") != "PUBLISHED"
                or len(old["daily_range_plan"][asset].get("points", [])) != 7):
            raise ValueError("W46_ORIGINAL_IS_NOT_DAILY_SOURCE_MISSING")
    if len(old_bytes) == 0 or any(not (target / x).is_file() for x in OUTPUT_FILES):
        raise ValueError("W46_BEFORE_ARCHIVE_SOURCE_MISSING")
    return target, request, old, original_pointer, original_receipt


def repair(repo: Path, mm_ptr: dict, pointer: dict, now: datetime | None = None):
    """Only the existing weekly GitHub Actions main writer calls this function."""
    from scripts.cycle_navigator import build_weekly_cycle_navigator as builder

    now = (now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    target, request, before, original_pointer, original_receipt = _guard(
        repo, pointer, mm_ptr, now=now)

    weekly = _read(repo / "03_DAILY_CAPTURE_LOGS/weekly/2026/W45.json")
    mm_machine = _read(repo / "research/api_agent/outputs/weekly/2026/W45/MASTER_MONDAY_MACHINE_PACKAGE.json")
    prior_dir = repo / "05_CYCLE_NAVIGATOR/weekly/2026/W45"
    prior = _read(prior_dir / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    prior["forecast_freeze"] = _read(prior_dir / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json")
    baseline = _read(repo / "05_CYCLE_NAVIGATOR/range_baselines/forecasts/2026/W46.json")
    context = {
        "completed_week_hourly_capture": weekly,
        "master_monday_pointer": mm_ptr,
        "master_monday_machine_package": mm_machine,
        "weekly_envelope_quote": {"BTC":"USDT","ETH":"USDT"},
    }

    token = _checkout_read_token(repo)
    proof = attest_completed_week(
        repo, 2026, 45, weekly, issued_at=now,
        token=token, repo_full_name="Donh91/Investering-Framework-Archive-v1")
    # No source shortcut: prove BOTH assets from the original GitHub Actions
    # raw 1h artifacts AND W45 168-row CSV/weekly machine summaries.
    if set(proof.verified_assets) != {"BTC", "ETH"}:
        raise ValueError("W46_BOTH_RAW_ASSETS_NOT_PROVEN")
    context["pre_model_original_price_attestation"] = proof.public_summary()
    candidate = build_offline_value(context, baseline, prior, 2026, 46, 34, 33)
    candidate = reject_unverified_initial_daily_quotes(
        candidate, context, year=2026, week=46,
        issued_at=now, trusted_price_source=proof)
    computed = candidate["forecast_freeze"]
    # The prior first-issue weekly bands and seven per-day uncertainty bands
    # remain immutable. Only the explicitly missing expected closes change.
    for key in ("btc_range_low", "btc_range_high", "eth_range_low",
                "eth_range_high", "intraday_map", "price_quote",
                "daily_range_plan"):
        if before.get(key) != computed.get(key):
            raise ValueError("W46_OWNER_REISSUE_RANGE_OR_UNIT_REWRITE_REFUSED:" + key)
    for asset in ("BTC", "ETH"):
        if (computed["daily_price_path"][asset]["status"] != "PUBLISHED"
                or len(computed["daily_price_path"][asset]["points"]) != 7):
            raise ValueError("W46_NEW_CLOSES_NOT_SOURCE_QUALIFIED")
    amended = dict(before)
    amended["daily_price_path"] = computed["daily_price_path"]
    validate_daily_path(amended["daily_price_path"], amended, 2026, 46)
    validate_daily_range_plan(amended["daily_range_plan"], amended, 2026, 46)
    product = daily_product_acceptance(amended, 2026, 46, now)
    if product["status"] != "COMPLETE":
        raise ValueError("W46_SAME_DAY_PRODUCT_NOT_COMPLETE")

    archive_dir = repo / BEFORE
    if archive_dir.exists():
        raise ValueError("W46_PREVIOUS_REVISION_ALREADY_ARCHIVED")
    old_bytes = {name:(target / name).read_bytes() for name in OUTPUT_FILES}
    old_sha = _sha(_canonical(before))
    new_sha = _sha(_canonical(amended))
    metadata = {
        "contract": CONTRACT, "forecast_week":"2026-W46",
        "public_issue_number":33, "machine_issue_number":34,
        "before_issued_utc":datetime.fromtimestamp(
            original_receipt["frozen_unix"],timezone.utc).isoformat().replace("+00:00","Z"),
        "after_issued_utc":now.isoformat().replace("+00:00","Z"),
        "before_forecast_sha256":old_sha,"after_forecast_sha256":new_sha,
        "before_daily_expected_close_points":{"BTC":0,"ETH":0},
        "after_daily_expected_close_points":{"BTC":7,"ETH":7},
        "after_daily_ranges":{"BTC":7,"ETH":7},
        "reason":"Same-Monday explicit owner-authorized repair of missing raw-source attestation; no prior daily forecast was issued.",
        "source_attestation":proof.public_summary(),
        "scoring_policy":"FIRST_KNOWN_AMENDED_ISSUANCE_NO_HINDSIGHT_OR_RESCORING",
        "review_requirement":"Prior immutable issued-unavailable version archived byte-for-byte.",
        "no_api_request":True,
        "no_portfolio_execution":True,
    }
    # Finish every source gate before changing anything. Then archive first.
    archive_dir.mkdir(parents=True, exist_ok=False)
    for name, data in old_bytes.items():
        (archive_dir / name).write_bytes(data)
    (archive_dir / "BEFORE_INTEGRITY_MANIFEST.json").write_bytes(
        _canonical({"contract":"CN_W46_BEFORE_ARCHIVE_v1",
                    "original_revision_sha256":old_sha,
                    "files":{k:_sha(v) for k,v in old_bytes.items()},
                    "amendment":metadata}))

    machine = _read(target / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json")
    manifest = _read(target / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json")
    receipt = _read(target / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json")
    pointer_record = _read(target / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json")
    series_path=repo/"05_CYCLE_NAVIGATOR/public_series/CN_PUBLIC_SERIES_INDEX.json"
    series = _read(series_path)

    manifest["daily_path_issuance"] = builder.daily_path_issue_summary(
        amended["daily_price_path"], amended, 2026, 46)
    manifest["daily_product_acceptance"] = product
    manifest["original_price_product_diagnostic"] = builder.build_weekly_price_product_diagnostic(
        context, amended, product, manifest.get("daily_path_recovery") or {})
    manifest["source_first_known_attestation"] = proof.public_summary()
    manifest["owner_approved_same_day_revision"] = metadata
    machine["forecast_freeze"] = amended
    machine["generated_unix"] = int(now.timestamp())
    machine["source_manifest_sha256"] = _sha(_canonical(manifest))
    machine["owner_approved_same_day_revision"] = metadata
    # No change to evaluation/scorecard, prior frozen ranges, previous week or
    # settlement. This is the first actual DAILY expected-close issuance.
    machine_sha = _sha(_canonical(machine))
    pointer_record["forecast_freeze_sha256"] = new_sha
    pointer_record["machine_package_sha256"] = machine_sha
    pointer_record["owner_approved_same_day_revision"] = metadata
    pointer_record["master_monday_pointer_sha256"] = original_pointer["master_monday_pointer_sha256"]

    receipt["frozen_unix"] = int(now.timestamp())
    receipt["source_forecast_freeze_sha256"] = new_sha
    receipt["daily_path_issuance"] = manifest["daily_path_issuance"]
    receipt["daily_product_acceptance"] = product
    receipt["owner_approved_same_day_revision"] = metadata
    receipt["scoring_valid_from_utc"] = datetime.fromtimestamp(
        ((int(now.timestamp())+3599)//3600)*3600,timezone.utc).isoformat().replace("+00:00","Z")
    for row in (series.get("recent_lineage") or []):
        if row.get("forecast_week") == "2026-W46":
            row["owner_revision"] = "2026-11-09-SAME_DAY"
    if (series.get("latest_site_freeze") or {}).get("forecast_week") != "2026-W46":
        raise ValueError("W46_SITE_SERIES_TARGET_MOVED")
    series["latest_site_freeze"].update({
        "source_forecast_freeze_sha256":new_sha,
        "frozen_unix":int(now.timestamp()),
        "owner_revision":"2026-11-09-SAME_DAY"})

    (target / "CYCLE_NAVIGATOR_FORECAST_FREEZE.json").write_bytes(_canonical(amended))
    (target / "CYCLE_NAVIGATOR_SOURCE_MANIFEST.json").write_bytes(_canonical(manifest))
    (target / "CYCLE_NAVIGATOR_MACHINE_PACKAGE.json").write_bytes(_canonical(machine))
    (target / "CYCLE_NAVIGATOR_DELIVERY_POINTER.json").write_bytes(_canonical(pointer_record))
    (repo / "05_CYCLE_NAVIGATOR/LATEST_CYCLE_NAVIGATOR_POINTER.json").write_bytes(
        _canonical(pointer_record))
    (target / "CYCLE_NAVIGATOR_SITE_PUBLIC_FREEZE_RECEIPT.json").write_bytes(
        _canonical(receipt))
    series_path.write_bytes(_canonical(series))

    note = (
        "\n\n## Same-day revision · 9 November 2026\n"
        "The first W46 issue at " + metadata["before_issued_utc"] +
        " had seven daily high/low intervals but **NO source-admitted BTC/ETH daily expected closes**. "
        "The owner approved a same-day amendment, issued " + metadata["after_issued_utc"] +
        ", now with 7 BTC and 7 ETH source-attested expected closes. "
        "Original 0/7 freeze and every original artifact remain available in " +
        BEFORE + ". There is no backdating, duplicate week, reassignment of prior precision, "
        "model certainty, calibrated probabilities or trading authority. "
        "New first-known clock governs future daily precision.\n")
    for name in ("CYCLE_NAVIGATOR_READABLE.md","CYCLE_NAVIGATOR_X_READY.md"):
        p=target/name
        p.write_text(p.read_text().rstrip()+note)
    api_path=target/"CYCLE_NAVIGATOR_API_RECEIPT.json"
    api=_read(api_path)
    if api.get("api_request_performed") is not False:
        raise ValueError("W46_REISSUE_API_NOT_FREE")
    api["owner_approved_same_day_revision"]=metadata
    api["output_sha256"]=_sha(_canonical(candidate))
    api_path.write_bytes(_canonical(api))
    return {"status":"AMENDED_SOURCE_ATTESTED_7_7_BOTH",
            "public_issue_number":33,"issue_number":34,
            "forecast_week":"2026-W46","forecasts_per_asset":7,
            "prior_freeze_sha256":old_sha,"new_freeze_sha256":new_sha,
            "no_api_request":True,
            "issued_at_utc":metadata["after_issued_utc"]}
