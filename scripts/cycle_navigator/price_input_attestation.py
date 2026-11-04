"""Authenticate a completed week's original Binance spot OHLC input before CN issuance.

Read-only reuse of the existing Hourly Sequence writer and its 14-day raw
GitHub Actions evidence. No new collector, paid model invocation or publisher.
Raw provider bytes are processed in memory, never persisted in public outputs.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Callable

SOURCE_ROOT = Path("03_DAILY_CAPTURE_LOGS")
SPOT_PAIRS = {"BTC": "BTCUSDT", "ETH": "ETHUSDT"}
CONTRACT = "CN_ORIGINAL_SPOT_OHLC_ATTESTATION_v1"


class PriceEvidenceError(RuntimeError):
    pass


def _sha(body: bytes) -> str:
    return hashlib.sha256(body).hexdigest()


def _canonical(value) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def _clock(value: str) -> datetime:
    if not isinstance(value, str):
        raise PriceEvidenceError("SOURCE_CLOCK_MISSING")
    try:
        at = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise PriceEvidenceError("SOURCE_CLOCK_INVALID") from exc
    if at.utcoffset() is None:
        raise PriceEvidenceError("SOURCE_CLOCK_UNZONED")
    return at.astimezone(timezone.utc)


def _num(value) -> Decimal:
    try:
        d = Decimal(str(value))
        if not d.is_finite() or d <= 0:
            raise ValueError()
        return d
    except (InvalidOperation, ValueError) as exc:
        raise PriceEvidenceError("ORIGINAL_PRICE_INVALID") from exc


def _ohlc(value) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    row = tuple(_num(x) for x in value)
    if len(row) != 4 or row[2] > min(row[0], row[3]) or row[1] < max(row[0], row[3]):
        raise PriceEvidenceError("ORIGINAL_OHLC_INCONSISTENT")
    return row


@dataclass(frozen=True)
class OriginalSpotPriceProof:
    """Only produced by the read-only byte-verifying attestation function."""
    completed_week: str
    completed_capture_sha256: str
    weekly_ohlc_sha256: str
    verified_assets: tuple[str, ...]
    source_run_ids: tuple[int, ...]
    attested_at_utc: str

    def quote_for(self, asset: str) -> str | None:
        return "USDT" if asset in self.verified_assets else None

    def public_summary(self) -> dict:
        return {
            "contract": CONTRACT,
            "authority": "PREMODEL_SOURCE_PRICE_AND_UNIT_ONLY_NOT_FORECAST_ACCURACY",
            "completed_week": self.completed_week,
            "completed_capture_sha256": self.completed_capture_sha256,
            "weekly_ohlc_sha256": self.weekly_ohlc_sha256,
            "quote": {a: self.quote_for(a) or "UNAVAILABLE" for a in SPOT_PAIRS},
            "source_run_ids": list(self.source_run_ids),
            "attested_at_utc": self.attested_at_utc,
            "forecast_scoring_authority": False,
        }


def _run_id_from_original_commit(repo: Path, relative: Path) -> int:
    # Exact file history, not a moving latest pointer or an issue comment.
    cp = subprocess.run(
        ["git", "-C", str(repo), "log", "-1", "--format=%H%x00%cI%x00%s", "--", relative.as_posix()],
        capture_output=True, check=False, timeout=20)
    if cp.returncode != 0:
        raise PriceEvidenceError("ORIGINAL_RUN_GIT_HISTORY_UNAVAILABLE")
    try:
        sha, _, subject = cp.stdout.decode().strip().split("\x00", 2)
    except ValueError as exc:
        raise PriceEvidenceError("ORIGINAL_RUN_COMMIT_MISSING") from exc
    match = re.fullmatch(r"data: materialize hourly sequence (\d+)", subject)
    if not match or not re.fullmatch(r"[0-9a-f]{40}", sha):
        raise PriceEvidenceError("ORIGINAL_RUN_COMMIT_IDENTITY_INVALID")
    retained = subprocess.run(
        ["git", "-C", str(repo), "show", f"{sha}:{relative.as_posix()}"],
        capture_output=True, check=False, timeout=20)
    if retained.returncode or retained.stdout != (repo / relative).read_bytes():
        raise PriceEvidenceError("ORIGINAL_RUN_MANIFEST_CHANGED")
    return int(match.group(1))


class NoCrossHostBearerRedirect(urllib.request.HTTPRedirectHandler):
    """GitHub artifact storage redirects must never receive our GitHub token."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urllib.parse.urlsplit(newurl).scheme != "https":
            raise PriceEvidenceError("SOURCE_ARTIFACT_UNSAFE_REDIRECT")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and (urllib.parse.urlsplit(newurl).netloc
                                       != urllib.parse.urlsplit(req.full_url).netloc):
            redirected.remove_header("Authorization")
            redirected.remove_header("Cookie")
        return redirected


def _github_artifact_zip(run_id: int, *, repo_full_name: str, token: str) -> bytes:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo_full_name) or not token:
        raise PriceEvidenceError("SOURCE_ARTIFACT_AUTH_UNAVAILABLE")
    base = f"https://api.github.com/repos/{repo_full_name}"
    def fetch(url: str, limit: int) -> bytes:
        request = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json", "Authorization": "Bearer " + token,
            "User-Agent": "CN-Original-OHLC-Proof/1"})
        try:
            with urllib.request.build_opener(NoCrossHostBearerRedirect()).open(request, timeout=20) as response:
                data = response.read(limit + 1)
        except Exception as exc:
            raise PriceEvidenceError("SOURCE_ARTIFACT_TRANSPORT_UNAVAILABLE") from exc
        if len(data) > limit:
            raise PriceEvidenceError("SOURCE_ARTIFACT_TOO_LARGE")
        return data
    listing = json.loads(fetch(f"{base}/actions/runs/{run_id}/artifacts?per_page=100", 500000))
    target = f"hourly-sequence-source-evidence-{run_id}-1"
    found = [a for a in listing.get("artifacts", []) if a.get("name") == target
             and not a.get("expired") and isinstance(a.get("id"), int)]
    if len(found) != 1:
        raise PriceEvidenceError("SOURCE_ARTIFACT_EXPIRED_OR_MISSING")
    return fetch(f"{base}/actions/artifacts/{found[0]['id']}/zip", 2000000)


def _original_bars(manifest: dict, zip_bytes: bytes, asset: str) -> dict[datetime, tuple[Decimal, Decimal, Decimal, Decimal]]:
    symbol = SPOT_PAIRS[asset]
    records = [r for r in manifest.get("source_records", []) if r.get("name") == symbol + "_spot"]
    if len(records) != 1:
        raise PriceEvidenceError("ORIGINAL_RAW_RECEIPT_MISSING")
    row = records[0]
    url = urllib.parse.urlsplit(str(row.get("url", "")))
    params = urllib.parse.parse_qs(url.query)
    if (row.get("status") != "PASS" or row.get("venue") != "BINANCE_SPOT"
            or url.scheme != "https" or url.netloc != "data-api.binance.vision"
            or url.path != "/api/v3/klines"
            or params.get("symbol") != [symbol] or params.get("interval") != ["1h"]):
        raise PriceEvidenceError("ORIGINAL_SPOT_PAIR_OR_QUOTE_UNVERIFIED")
    filename = symbol + "_spot.json"
    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
            raw = archive.read(filename)
    except (OSError, KeyError, zipfile.BadZipFile) as exc:
        raise PriceEvidenceError("ORIGINAL_RAW_BYTES_MISSING") from exc
    if len(raw) > 100000 or _sha(raw) != row.get("sha256") or len(raw) != row.get("bytes"):
        raise PriceEvidenceError("ORIGINAL_RAW_RESPONSE_HASH_MISMATCH")
    try:
        candles = json.loads(raw)
    except (TypeError, ValueError) as exc:
        raise PriceEvidenceError("ORIGINAL_RAW_JSON_INVALID") from exc
    if not isinstance(candles, list) or len(candles) != row.get("row_count"):
        raise PriceEvidenceError("ORIGINAL_RAW_ROWCOUNT_INVALID")
    start = _clock(manifest["window_start_utc"])
    end = _clock(manifest["window_end_utc"])
    bars = {}
    for candle in candles:
        try:
            at = datetime.fromtimestamp(int(candle[0]) / 1000, tz=timezone.utc)
            price = _ohlc(candle[1:5])
        except (IndexError, TypeError, ValueError, OverflowError) as exc:
            raise PriceEvidenceError("ORIGINAL_RAW_CANDLE_INVALID") from exc
        if at.minute or at.second or at.microsecond or not start <= at < end or at in bars:
            raise PriceEvidenceError("ORIGINAL_RAW_TIME_WINDOW_INVALID")
        bars[at] = price
    return bars


def attest_completed_week(
    repo: Path, completed_year: int, completed_week: int, capture: dict, *,
    issued_at: datetime, token: str = "", repo_full_name: str = "",
    run_lookup: Callable[[Path], int] | None = None,
    artifact_loader: Callable[[int], bytes] | None = None,
) -> OriginalSpotPriceProof:
    """Authenticate original provider bytes AND exact 168 retained price rows.

    Inject run_lookup/artifact_loader only in offline tests. Both live paths use
    Git commit history and original Actions artifacts. A failure abstains, never
    manufactures an attestation from numeric source labels.
    """
    repo = repo.resolve()
    issued = issued_at.astimezone(timezone.utc)
    monday = datetime.combine(date.fromisocalendar(completed_year, completed_week, 1),
                              datetime.min.time(), timezone.utc)
    end = monday + timedelta(days=7)
    week_id = f"{completed_year:04d}-W{completed_week:02d}"
    if issued_at.utcoffset() is None or issued < end or not isinstance(capture, dict):
        raise PriceEvidenceError("SOURCE_ISSUE_OR_CAPTURE_CLOCK_INVALID")
    if (capture.get("iso_year"), capture.get("iso_week")) != (completed_year, completed_week):
        raise PriceEvidenceError("SOURCE_COMPLETED_WEEK_MISMATCH")
    rel = SOURCE_ROOT / "weekly" / str(completed_year) / f"W{completed_week:02d}" / "WEEKLY_HOURLY_ENRICHED.csv"
    if not (repo / rel).is_file():
        raise PriceEvidenceError("ORIGINAL_WEEKLY_PRICE_CSV_MISSING")
    rows = list(csv.DictReader((repo / rel).open(newline="", encoding="utf-8")))
    expected_times = [monday + timedelta(hours=i) for i in range(168)]
    if len(rows) != 168 or [_clock(r["timestamp_utc"]) for r in rows] != expected_times:
        raise PriceEvidenceError("ORIGINAL_WEEKLY_PRICE_TIMESTAMPS_INVALID")
    expected: dict[str, dict[datetime, tuple]] = {a: {} for a in SPOT_PAIRS}
    for at, row in zip(expected_times, rows):
        if row.get("spot_status") != "PASS":
            raise PriceEvidenceError("ORIGINAL_WEEKLY_SPOT_STATUS_INVALID")
        for asset in SPOT_PAIRS:
            p = asset.lower()
            expected[asset][at] = _ohlc([row[p+"_"+key] for key in ("open", "high", "low", "close")])
    # The model receives weekly summaries, not the 168 provider candles.
    # Authenticate those numeric summaries against the same 168 raw inputs.
    for asset in SPOT_PAIRS:
        items = list(expected[asset].values())
        supplied = ((capture.get("hourly_sequence") or {}).get(asset.lower()) or {}).get("week_range") or {}
        values = {"open": items[0][0], "close": items[-1][3],
                  "high": max(x[1] for x in items), "low": min(x[2] for x in items)}
        if any(_num(supplied.get(k)) != v for k, v in values.items()):
            raise PriceEvidenceError("MODEL_INPUT_WEEKLY_PRICE_FRAME_MISMATCH")
    # Select existing 26h capture runs with maximal forward coverage, no new reader.
    manifests = []
    root = repo / SOURCE_ROOT / "hourly" / "runs"
    for day_offset in range(8):
        day = monday + timedelta(days=day_offset)
        d = root / day.strftime("%Y/%m/%d")
        for path in d.glob("*.json") if d.is_dir() else ():
            try:
                m = json.loads(path.read_bytes())
                start, stop, captured = (_clock(m[key]) for key in
                    ("window_start_utc", "window_end_utc", "retrieved_at_utc"))
            except (OSError, KeyError, ValueError, TypeError, PriceEvidenceError):
                continue
            if (m.get("contract") == "HOURLY_SEQUENCE_CAPTURE_v2_2"
                    and m.get("spot_status") == "PASS" and start < stop
                    and stop <= captured <= issued and stop > monday and start < end):
                manifests.append((start, stop, path, m))
    selected = []
    cursor = monday
    while cursor < end:
        options = [x for x in manifests if x[0] <= cursor < x[1] and x not in selected]
        if not options:
            raise PriceEvidenceError("ORIGINAL_SOURCE_RUN_COVERAGE_GAP")
        winner = max(options, key=lambda x: x[1])
        selected.append(winner)
        cursor = winner[1]
        if len(selected) > 12:
            raise PriceEvidenceError("ORIGINAL_SOURCE_RUN_EXCESS")
    evidence = {asset: {} for asset in SPOT_PAIRS}
    failed = set()
    run_ids = []
    for _, _, path, manifest in selected:
        relative = path.relative_to(repo)
        run_id = (run_lookup or (lambda p: _run_id_from_original_commit(repo, p)))(relative)
        archive = (artifact_loader or (lambda rid: _github_artifact_zip(
            rid, repo_full_name=repo_full_name, token=token)))(run_id)
        run_ids.append(run_id)
        for asset in SPOT_PAIRS:
            if asset in failed:
                continue
            try:
                raw = _original_bars(manifest, archive, asset)
                for at, ohlc in raw.items():
                    if monday <= at < end:
                        if at in evidence[asset] and evidence[asset][at] != ohlc:
                            raise PriceEvidenceError("ORIGINAL_RAW_OVERLAP_CONFLICT")
                        evidence[asset][at] = ohlc
            except PriceEvidenceError:
                failed.add(asset)
    verified = tuple(a for a in SPOT_PAIRS if a not in failed and evidence[a] == expected[a])
    if not verified:
        raise PriceEvidenceError("ORIGINAL_RAW_TO_WEEKLY_OHLC_PROOF_MISSING")
    # Value-free canonical digest of the exact price units and source-week stream.
    normalized = [{"time": at.isoformat(), "assets": {
        a: [format(v.normalize(), "f") for v in expected[a][at]]
        for a in SPOT_PAIRS}} for at in expected_times]
    return OriginalSpotPriceProof(
        completed_week=week_id,
        completed_capture_sha256=_sha(_canonical(capture)),
        weekly_ohlc_sha256=_sha(_canonical(normalized)),
        verified_assets=verified,
        source_run_ids=tuple(run_ids),
        attested_at_utc=issued.isoformat().replace("+00:00", "Z"),
    )
