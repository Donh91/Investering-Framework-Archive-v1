#!/usr/bin/env python3
"""EDGE Task 1.5: immutable intraday issuance/censor/baseline reconciliation.

Research-only. The independent Binance spot CSV is an EX-POST outcome tape:
it never changes the original registered scorer or proves provider PIT.

Run from repository root:
 python3 04_MARKET_LEARNING/handlekompas/research/2026-10-13__task15_forecast_reconciliation_v1.py --out /tmp/task15
 python3 04_MARKET_LEARNING/handlekompas/research/2026-10-13__task15_forecast_reconciliation_v1.py --self-test
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import tempfile
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

WINDOW_START = datetime(2026, 9, 15, 6, tzinfo=timezone.utc)
WINDOW_END = datetime(2026, 10, 13, 6, tzinfo=timezone.utc)
OCT13 = datetime(2026, 10, 13, 0, tzinfo=timezone.utc)
PRED = Path("04_MARKET_LEARNING/intraday_execution/direction_predictions")
OUTCOME = Path("04_MARKET_LEARNING/intraday_execution/direction_outcomes")
TAPE = Path("04_MARKET_LEARNING/handlekompas/research/evidence/2026-09-15_to_2026-10-13__HOURLY_SPOT_OUTCOME_CROSSCHECK_28D.csv")
HORIZONS = {"1H": 1, "4H": 4, "24H": 24}
ASSETS = ("BTC", "ETH")
COLUMNS = (
    "prediction_id", "asset", "horizon", "issue_utc", "source_cutoff_utc",
    "due_utc", "prediction_sha256", "binding_source_commit", "forecast_status",
    "direction", "original_outcome_status", "original_outcome_result",
    "original_outcome_sha256", "original_outcome_binding_sha256",
    "frozen_start", "tape_start_at_cutoff", "tape_actual_at_due",
    "tape_start_conflict", "observed_direction", "descriptive_hit",
    "prior_momentum_pct", "baseline_direction", "baseline_hit",
    "original_scoring_preserved", "pit_status", "research_admission",
)

def parse_utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC timestamp must end Z")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.utcoffset() != timedelta(0):
        raise ValueError("non UTC time")
    return dt

def utc(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")

def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def direction_change(start, end):
    if start is None or end is None:
        return None
    if end > start:
        return "UP"
    if end < start:
        return "DOWN"
    return "FLAT"

def read_tape(path: Path) -> dict[datetime, dict]:
    if not path.is_file():
        raise ValueError(f"OUTCOME_TAPE_MISSING:{path}")
    out = {}
    with path.open(newline="", encoding="utf-8") as file:
        for row in csv.DictReader(file):
            dt = parse_utc(row["close_time_utc"])
            if dt in out:
                raise ValueError(f"DUPLICATE_TAPE_CLOCK:{utc(dt)}")
            if row.get("forecast_pairing_status") != "NOT_JOINED_TO_ORIGINAL_FORECAST":
                raise ValueError("TAPE_NOT_RESEARCH_ONLY")
            out[dt] = row
    stamps = sorted(out)
    expected = [WINDOW_START + timedelta(hours=i) for i in range(1, 673)]
    if stamps != expected:
        raise ValueError(f"TAPE_GAP_OR_WRONG_WINDOW:{len(stamps)}")
    return out

def tape_value(tape: dict, dt, asset: str):
    if dt not in tape:
        return None
    value = tape[dt].get(f"{asset.lower()}_usdt_spot_close")
    if not value:
        return None
    try:
        n = float(value)
        return n if n > 0 else None
    except (ValueError, TypeError):
        return None

def tape_momentum(tape: dict, cutoff, asset, horizon):
    if cutoff not in tape:
        return None
    value = tape[cutoff].get(f"{asset.lower()}_trailing_{horizon.lower()}_return_pct")
    if value in ("", None):
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def outcome_file(root: Path, issued: datetime, slug: str, horizon: str, asset: str) -> Path:
    return root / OUTCOME / issued.strftime("%Y/%m/%d") / f"{slug}_{horizon}_{asset}.json"

def scan(root: Path, tape: dict):
    rows = []
    pred_files = sorted((root / PRED).glob("2026/*/*/*.json"))
    seen = set()
    for file in pred_files:
        p = read_json(file)
        issued = parse_utc(p["issued_at_utc"])
        if not WINDOW_START <= issued < WINDOW_END:
            continue
        if p.get("contract") != "INTRADAY_DIRECTION_PREDICTION_v1":
            raise ValueError(f"INVALID_FORECAST_CONTRACT:{file}")
        sha = digest(file)
        stem = file.stem
        for hname, hours in HORIZONS.items():
            h = (p.get("horizons") or {}).get(hname) or {}
            cutoff_text, due_text = h.get("source_cutoff_utc"), h.get("due_at_utc")
            cutoff = parse_utc(cutoff_text) if cutoff_text else None
            due = parse_utc(due_text) if due_text else None
            for asset in ASSETS:
                target = (h.get("targets") or {}).get(asset) or {}
                original = outcome_file(root, issued, stem, hname, asset)
                receipt = read_json(original) if original.is_file() else {}
                forecast_state = str(h.get("status") or "MISSING_HORIZON")
                predicted = target.get("direction")
                key = (str(file.relative_to(root)), asset, hname)
                if key in seen:
                    raise ValueError(f"DUPLICATE_FORECAST_ID:{key}")
                seen.add(key)
                valid_issued = bool(
                    cutoff and due
                    and cutoff < issued < due
                    and (due - cutoff) == timedelta(hours=hours)
                )
                matured = valid_issued and due <= WINDOW_END
                permitted = forecast_state == "ELIGIBLE" and predicted in ("UP", "DOWN")
                start_raw = target.get("start_value")
                start = float(start_raw) if isinstance(start_raw, (float, int)) and not isinstance(start_raw, bool) else None
                basis = tape_value(tape, cutoff, asset) if cutoff else None
                finish = tape_value(tape, due, asset) if matured else None
                actual = direction_change(start, finish) if matured else None
                prior = tape_momentum(tape, cutoff, asset, hname) if cutoff else None
                reference = direction_change(0, prior) if prior is not None else None
                descriptive = predicted == actual if permitted and actual in ("UP", "DOWN") else None
                baseline_hit = reference == actual if permitted and reference in ("UP", "DOWN") and actual in ("UP", "DOWN") else None
                eligible = valid_issued and matured and permitted and start is not None and finish is not None
                admission = (
                    "RESEARCH_TAPE_SENSITIVITY_ONLY" if eligible else
                    "PENDING_FUTURE_MATURITY" if permitted and valid_issued and not matured else
                    "NO_EDGE_OR_MISSING" if not permitted else
                    "CLOCK_OR_TAPE_UNAVAILABLE"
                )
                if receipt.get("status") == "CENSORED":
                    admission = "CENSORED_ORIGINAL_RESEARCH_TAPE_SENSITIVITY_ONLY" if eligible else "CENSORED_ORIGINAL_NO_RESEARCH_SCORE"
                rows.append({
                    "prediction_id": str(file.relative_to(root)) + f"#{hname}:{asset}",
                    "asset": asset, "horizon": hname,
                    "issue_utc": p["issued_at_utc"], "source_cutoff_utc": cutoff_text or "",
                    "due_utc": due_text or "",
                    "prediction_sha256": sha,
                    "binding_source_commit": (p.get("production_context") or {}).get("commit_sha") or "",
                    "forecast_status": forecast_state,
                    "direction": predicted or "",
                    "original_outcome_status": receipt.get("status") or "NO_ORIGINAL_RECEIPT",
                    "original_outcome_result": receipt.get("result") or "",
                    "original_outcome_sha256": digest(original) if original.is_file() else "",
                    "original_outcome_binding_sha256": receipt.get("prediction_sha256") or "",
                    "frozen_start": start,
                    "tape_start_at_cutoff": basis, "tape_actual_at_due": finish,
                    "tape_start_conflict": bool(start is not None and basis is not None and abs(start - basis) > 0.02),
                    "observed_direction": actual or "",
                    "descriptive_hit": descriptive,
                    "prior_momentum_pct": prior,
                    "baseline_direction": reference or "",
                    "baseline_hit": baseline_hit,
                    "original_scoring_preserved": True,
                    "pit_status": "INDEPENDENT_PROVIDER_FIRST_KNOWABLE_NOT_VERIFIED",
                    "research_admission": admission,
                })
    return rows, len(pred_files)

def summarize(rows):
    results = {}
    for cohort, subset in (
        ("ISSUED_SEP15_TO_OCT12_235959", [r for r in rows if parse_utc(r["issue_utc"]) < OCT13]),
        ("ISSUED_SEP15_TO_OCT13_055959", rows),
    ):
        entry = {}
        for h in HORIZONS:
            sub = [r for r in subset if r["horizon"] == h]
            scorable = [r for r in sub if r["research_admission"] in ("RESEARCH_TAPE_SENSITIVITY_ONLY", "CENSORED_ORIGINAL_RESEARCH_TAPE_SENSITIVITY_ONLY") and r["descriptive_hit"] is not None]
            paired = [r for r in scorable if r["baseline_hit"] is not None]
            entry[h] = {
                "forecast_slots": len(sub),
                "eligible_directional_tape_sensitivities": len(scorable),
                "directional_tape_hits": sum(r["descriptive_hit"] for r in scorable),
                "same_clock_prior_momentum_pairs": len(paired),
                "baseline_hits_on_exact_pairs": sum(r["baseline_hit"] for r in paired),
                "model_hits_on_exact_pairs": sum(r["descriptive_hit"] for r in paired),
                "original_outcome_status": dict(Counter(r["original_outcome_status"] for r in sub)),
                "admission_status": dict(Counter(r["research_admission"] for r in sub)),
                "tape_start_conflicts": sum(bool(r["tape_start_conflict"]) for r in sub),
            }
        results[cohort] = entry
    return results

def run(root: Path, out: Path):
    tape = read_tape(root / TAPE)
    rows, prediction_files = scan(root, tape)
    out.mkdir(parents=True, exist_ok=True)
    ledger = out / "TASK15_R0_FROZEN_FORECAST_TAPE_CENSOR_LEDGER.csv"
    with ledger.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "contract": "TASK15_INTRADAY_RESEARCH_RECONCILIATION_v1",
        "authority": "RESEARCH_ONLY_NOT_REGISTERED_SCORING_OR_MODEL_PROMOTION",
        "study_start_utc": utc(WINDOW_START), "study_end_utc": utc(WINDOW_END),
        "boundary_semantics": "ISSUED_START_INCLUSIVE_END_EXCLUSIVE;_DUE_END_INCLUSIVE",
        "tape_path": str(TAPE), "tape_sha256": digest(root / TAPE),
        "tape_rows": len(tape),
        "prediction_files_total_before_date_filter": prediction_files,
        "forecast_asset_horizon_slots_in_window": len(rows),
        "ledger_sha256": digest(ledger),
        "results": summarize(rows),
        "limitations": [
            "Independent Binance tape is later-retrieved ex-post outcome, not original owner-time evidence.",
            "Original CENSORED receipts are immutable and never converted to canonical HIT or MISS.",
            "No first-parent canonical publication verification, feature-source-vintage proof, or legal PIT admission in this standalone script.",
            "Forecasts overlap by horizon, time and asset; observations are not independent event families.",
            "No original Official/Shadow 12H/72H/168H comparison, trade fills, economics or site/chat delivery.",
            "Provider spot close and frozen owner close might disagree; start discrepancies remain explicit.",
            "Missing baseline clocks are excluded from paired comparison, NOT backfilled or zero-counted.",
        ],
        "closure_verdict": "PARTIAL_RESEARCH_EXECUTION_NOT_TASK_1_5_SCIENTIFIC_PASS",
    }
    (out / "TASK15_R0_RECEIPT.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return manifest

def self_test():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        tape = root / TAPE
        tape.parent.mkdir(parents=True)
        with tape.open("w", newline="", encoding="utf-8") as handle:
            w = csv.DictWriter(handle, fieldnames=["close_time_utc", "btc_usdt_spot_close", "eth_usdt_spot_close", "btc_trailing_1h_return_pct", "eth_trailing_1h_return_pct", "btc_trailing_4h_return_pct", "eth_trailing_4h_return_pct", "btc_trailing_24h_return_pct", "eth_trailing_24h_return_pct", "forecast_pairing_status"])
            w.writeheader()
            for i in range(1, 673):
                w.writerow({"close_time_utc": utc(WINDOW_START + timedelta(hours=i)), "btc_usdt_spot_close": 100 + i, "eth_usdt_spot_close": 200 + i, "btc_trailing_1h_return_pct": 1.0, "eth_trailing_1h_return_pct": 1.0, "btc_trailing_4h_return_pct": 1.0, "eth_trailing_4h_return_pct": 1.0, "btc_trailing_24h_return_pct": 1.0, "eth_trailing_24h_return_pct": 1.0, "forecast_pairing_status": "NOT_JOINED_TO_ORIGINAL_FORECAST"})
        pred_dir = root / PRED / "2026/09/15"
        pred_dir.mkdir(parents=True)
        forecast = {
            "contract": "INTRADAY_DIRECTION_PREDICTION_v1",
            "issued_at_utc": utc(WINDOW_START + timedelta(hours=1, minutes=5)),
            "production_context": {"commit_sha": "fixture"},
            "horizons": {
                "1H": {"status": "ELIGIBLE", "source_cutoff_utc": utc(WINDOW_START + timedelta(hours=1)), "due_at_utc": utc(WINDOW_START + timedelta(hours=2)), "targets": {"BTC": {"direction": "UP", "start_value": 101}, "ETH": {"direction": "DOWN", "start_value": 201}}},
                "4H": {"status": "NO_EDGE", "source_cutoff_utc": utc(WINDOW_START + timedelta(hours=1)), "due_at_utc": utc(WINDOW_START + timedelta(hours=5)), "targets": {}},
            },
        }
        pf = pred_dir / "20260915T070500Z.json"
        pf.write_text(json.dumps(forecast), encoding="utf-8")
        of = outcome_file(root, parse_utc(forecast["issued_at_utc"]), pf.stem, "1H", "BTC")
        of.parent.mkdir(parents=True)
        of.write_text(json.dumps({"status": "CENSORED", "reason": "EXACT_DUE_OWNER_CANDLE_MISSING_AFTER_GRACE"}), encoding="utf-8")
        result = run(root, root / "audit")
        cohort = result["results"]["ISSUED_SEP15_TO_OCT13_055959"]["1H"]
        assert cohort["eligible_directional_tape_sensitivities"] == 2, cohort
        assert cohort["directional_tape_hits"] == 1, cohort
        assert cohort["same_clock_prior_momentum_pairs"] == 2, cohort
        assert cohort["baseline_hits_on_exact_pairs"] == 2, cohort
        assert cohort["original_outcome_status"]["CENSORED"] == 1, cohort
        assert "CENSORED" in of.read_text(), "Original outcome mutated"
        assert result["closure_verdict"].startswith("PARTIAL"), result
        assert result["tape_rows"] == 672, result
        try:
            fake = root / "bad.csv"
            fake.write_text("close_time_utc,forecast_pairing_status\n2026-10-13T06:00:00Z,NOT_JOINED_TO_ORIGINAL_FORECAST\n")
            read_tape(fake)
        except ValueError:
            pass
        else:
            raise AssertionError("gap negative control was not rejected")
    return "SELF_TEST_PASS: original CENSORED protected, 2/2 paired baseline, 672 hourly candles, bad tape fails closed"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--out", default="/tmp/task15-compass-audit")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        print(self_test())
        return
    receipt = run(Path(args.root), Path(args.out))
    print(json.dumps(receipt, indent=2))

if __name__ == "__main__":
    main()
