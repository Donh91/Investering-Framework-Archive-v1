"""Adversarial original-source admission tests, all synthetic/offline.

No historical market values, provider keys, model calls, GitHub API or network.
"""
import copy
import csv
import hashlib
import io
import json
import zipfile
import pytest
import urllib.request
from scripts.cycle_navigator.price_input_attestation import NoCrossHostBearerRedirect, PriceEvidenceError
from datetime import datetime, timedelta, timezone
from pathlib import Path

from scripts.cycle_navigator.price_input_attestation import attest_completed_week
from scripts.cycle_navigator.daily_path_recovery import _source_gate, reject_unverified_initial_daily_quotes

UTC = timezone.utc
MON = datetime(2026, 11, 2, tzinfo=UTC)
ISSUED = datetime(2026, 11, 9, 10, tzinfo=UTC)
COLS = ("open", "high", "low", "close")


def iso(at):
    return at.isoformat().replace("+00:00", "Z")


def candle(asset, at):
    index = int((at - MON).total_seconds() // 3600)
    base = (80000 if asset == "BTC" else 2000) + index
    return [str(base), str(base + 5), str(base - 5), str(base + 1)]


def fixture(tmp_path):
    repo = tmp_path
    out = repo / "03_DAILY_CAPTURE_LOGS/weekly/2026/W45/WEEKLY_HOURLY_ENRICHED.csv"
    out.parent.mkdir(parents=True)
    with out.open("w", newline="") as stream:
        fields = ["timestamp_utc", "spot_status"] + [
            f"{asset}_{key}" for asset in ("btc", "eth") for key in COLS]
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for i in range(168):
            at = MON + timedelta(hours=i)
            row = {"timestamp_utc": iso(at), "spot_status": "PASS"}
            for a in ("BTC", "ETH"):
                row.update({f"{a.lower()}_{key}": value for key, value in zip(COLS, candle(a, at))})
            writer.writerow(row)

    capture = {"iso_year": 2026, "iso_week": 45, "readiness": "READY",
        "generated_at_utc": iso(ISSUED - timedelta(hours=1)),
        "hourly_gap_diagnostics": {"observed_hours": 168, "missing_hour_count": 0},
        "source_capture_paths": ["existing-original-capture"],
        "hourly_sequence": {
            "first_hour_utc": iso(MON),
            "last_hour_utc": iso(MON + timedelta(hours=167)),
            "spot_flow_readback": {
                a: {"quote_unit": "USDT", "symbol": a+"USDT", "source_rows_sha256": "UNCHANGED_FLOW_HASH"}
                for a in ("BTC", "ETH")}}}
    for asset in ("BTC", "ETH"):
        capture["hourly_sequence"][asset.lower()] = {"week_range": {
            "open": candle(asset, MON)[0], "close": candle(asset, MON + timedelta(hours=167))[3],
            "high": candle(asset, MON + timedelta(hours=167))[1],
            "low": candle(asset, MON)[2],
        }}

    archives = {}
    for i in range(7):
        day = MON + timedelta(days=i)
        start, stop = day - timedelta(hours=2), day + timedelta(days=1)
        retrieved = stop + timedelta(minutes=20)
        run_id = 90000 + i
        records = []
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as archive:
            for asset in ("BTC", "ETH"):
                symbol = asset+"USDT"
                bars = []
                for j in range(26):
                    at = start + timedelta(hours=j)
                    bars.append([int(at.timestamp() * 1000), *candle(asset, at)])
                raw = json.dumps(bars).encode()
                archive.writestr(symbol+"_spot.json", raw)
                records.append({
                    "name": symbol+"_spot", "status": "PASS", "venue": "BINANCE_SPOT",
                    "url": ("https://data-api.binance.vision/api/v3/klines?"
                            f"symbol={symbol}&interval=1h&limit=1000"),
                    "bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                    "row_count": 26,
                })
        archives[run_id] = zip_buffer.getvalue()
        relative = (Path("03_DAILY_CAPTURE_LOGS/hourly/runs") /
                    retrieved.strftime("%Y/%m/%d") / f"SOURCE_RUN_{run_id}.json")
        path = repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "contract": "HOURLY_SEQUENCE_CAPTURE_v2_2",
            "spot_status": "PASS", "window_start_utc": iso(start),
            "window_end_utc": iso(stop), "retrieved_at_utc": iso(retrieved),
            "source_records": records,
        }))
    return repo, capture, archives


def proof(repo, capture, archives):
    return attest_completed_week(
        repo, 2026, 45, capture, issued_at=ISSUED,
        run_lookup=lambda p: int(p.stem.split("_")[-1]),
        artifact_loader=lambda run_id: archives[run_id])


def context(capture):
    return {"completed_week_hourly_capture": capture,
            "master_monday_pointer": {"iso_year": 2026, "iso_week": 45, "status": "READY"},
            "master_monday_machine_package": {
                "api_status": "success", "created_at_utc": iso(ISSUED - timedelta(hours=1))},
            "weekly_envelope_quote": {"BTC": "USDT", "ETH": "USDT"}}


def candidate():
    points = [{"day": i, "date_utc": iso(datetime(2026, 11, 9, tzinfo=UTC) +
              timedelta(days=i-1))[:10], "expected_close": 80000+i}
              for i in range(1, 8)]
    return {"forecast_freeze": {"price_quote": {"BTC": "USDT", "ETH": "USDT"},
            "daily_price_path": {
                a: {"status": "PUBLISHED", "points": copy.deepcopy(points), "reason": None}
                for a in ("BTC", "ETH")}}}


def test_authenticated_original_raw_168h_unlocks_both_seven_day_assets(tmp_path):
    repo, capture, archives = fixture(tmp_path)
    source = proof(repo, capture, archives)
    assert source.verified_assets == ("BTC", "ETH")
    assert len(source.source_run_ids) == 7
    evidence, gate = _source_gate(context(capture), 2026, 46, ISSUED, source)
    assert gate == "ELIGIBLE" and evidence["envelope_quote_independently_verified"]
    assert evidence["verified_source_quotes"] == {"BTC": "USDT", "ETH": "USDT"}
    original = candidate()
    out = reject_unverified_initial_daily_quotes(
        copy.deepcopy(original), context(capture),
        year=2026, week=46, issued_at=ISSUED, trusted_price_source=source)
    assert out == original


def test_price_row_tamper_rejected_even_when_flow_hash_unchanged(tmp_path):
    repo, capture, archives = fixture(tmp_path)
    csvpath = repo / "03_DAILY_CAPTURE_LOGS/weekly/2026/W45/WEEKLY_HOURLY_ENRICHED.csv"
    rows = list(csv.DictReader(csvpath.open()))
    old_flow_hash = capture["hourly_sequence"]["spot_flow_readback"]["BTC"]["source_rows_sha256"]
    rows[80]["btc_close"] = str(float(rows[80]["btc_close"]) + 1)
    with csvpath.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    source = proof(repo, capture, archives)
    assert source.verified_assets == ("ETH",)
    assert capture["hourly_sequence"]["spot_flow_readback"]["BTC"]["source_rows_sha256"] == old_flow_hash
    out = reject_unverified_initial_daily_quotes(
        candidate(), context(capture), year=2026, week=46,
        issued_at=ISSUED, trusted_price_source=source)
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"
    assert out["forecast_freeze"]["daily_price_path"]["ETH"]["status"] == "PUBLISHED"


def test_btc_currency_mismatch_cannot_borrow_eth_attestation(tmp_path):
    repo, capture, archives = fixture(tmp_path)
    source = proof(repo, capture, archives)
    original = candidate()
    original["forecast_freeze"]["price_quote"]["BTC"] = "USD"
    ctx = context(capture)
    ctx["weekly_envelope_quote"] = original["forecast_freeze"]["price_quote"]
    out = reject_unverified_initial_daily_quotes(
        original, ctx, year=2026, week=46,
        issued_at=ISSUED, trusted_price_source=source)
    assert out["forecast_freeze"]["daily_price_path"]["BTC"]["status"] == "UNAVAILABLE"
    assert out["forecast_freeze"]["daily_price_path"]["ETH"]["status"] == "PUBLISHED"


def test_no_publication_after_first_target_day_close_even_with_valid_raw(tmp_path):
    repo, capture, archives = fixture(tmp_path)
    source = proof(repo, capture, archives)
    too_late = datetime(2026, 11, 10, tzinfo=UTC)
    _, gate = _source_gate(context(capture), 2026, 46, too_late, source)
    assert gate == "SEVEN_DAY_PROSPECTIVE_WINDOW_CLOSED_OR_NOT_STARTED"
    out = reject_unverified_initial_daily_quotes(
        candidate(), context(capture), year=2026, week=46,
        issued_at=too_late, trusted_price_source=source)
    assert all(out["forecast_freeze"]["daily_price_path"][a]["status"] == "UNAVAILABLE"
               for a in ("BTC", "ETH"))


def test_unverified_caller_boolean_never_opens_daily_path(tmp_path):
    repo, capture, archives = fixture(tmp_path)
    ctx = context(capture)
    ctx["envelope_quote_independently_verified"] = True
    out = reject_unverified_initial_daily_quotes(
        candidate(), ctx, year=2026, week=46, issued_at=ISSUED)
    assert all(out["forecast_freeze"]["daily_price_path"][a]["status"] == "UNAVAILABLE"
               for a in ("BTC", "ETH"))


def test_original_artifact_redirect_strips_bearer_and_rejects_http():
    handler = NoCrossHostBearerRedirect()
    request = urllib.request.Request(
        "https://api.github.com/repos/example/repo/actions/artifacts/123/zip",
        headers={"Authorization": "Bearer INTERNAL_SECRET"})
    redirected = handler.redirect_request(
        request, None, 302, "Found", {},
        "https://storage.example.invalid/temporary-signed-artifact")
    assert redirected.get_header("Authorization") is None
    with pytest.raises(PriceEvidenceError, match="SOURCE_ARTIFACT_UNSAFE_REDIRECT"):
        handler.redirect_request(request, None, 302, "Found", {},
                                 "http://storage.example.invalid/insecure")
