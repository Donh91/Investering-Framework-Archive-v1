#!/usr/bin/env python3
"""Decision Economics Ledger v1.2.

Shadow-only, point-in-time economic accountability for published Compass actions.

DEL scores the explicit per-segment action frozen by Compass. It never treats the
market status field as an action and never reconstructs action from prose. Historical
freezes that predate the action field remain unscorable rather than being guessed.

Two explicit synthetic reader states are replayed:

* INCUMBENT_HOLDER starts invested and keeps exposure until an explicit BUY/DEPLOY or
  SELL/EXIT action changes it.
* FRESH_CAPITAL starts in cash and only enters on an explicit BUY/DEPLOY action.

HOLD, PREPARE, WAIT and HARD_WAIT are no-trade actions for both interpretations.

Transaction costs are charged only on actual exposure changes. Because each
interpretation defines its starting exposure, an explicit first BUY/DEPLOY or SELL/EXIT
transition is chargeable from that known starting state. A first no-trade observation
has zero turnover. No output has portfolio, threshold, model-weight or
canonical-market authority.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROW_CONTRACT = "DECISION_ECONOMICS_LEDGER_ROW_v1_2"
RUN_CONTRACT = "DECISION_ECONOMICS_LEDGER_RUN_v1_2"
SEGMENT_OWNER_CONTRACT = "GOVERNED_SEGMENT_RETURN_SERIES_v1"
SEGMENTS = ("BTC", "ETH", "LARGE_CAPS", "MID_CAPS", "SMALL_CAPS", "MICROCAPS")
HORIZON_DAYS = (1, 3, 7, 28)
INTERPRETATIONS = ("INCUMBENT_HOLDER", "FRESH_CAPITAL")
CHALLENGERS = ("BUY_HOLD", "CASH", "CORE_STATE_BTC100_5PCT")
ONE_WAY_COST = {
    "BTC": 0.0015,
    "ETH": 0.0015,
    "LARGE_CAPS": 0.0015,
    "MID_CAPS": 0.0025,
    "SMALL_CAPS": 0.0040,
    "MICROCAPS": 0.0070,
}
NO_TRADE_STATES = {"HOLD", "PREPARE", "WAIT", "HARD_WAIT"}
ENTER_STATES = {"DEPLOY", "BUY"}
EXIT_STATES = {"SELL", "EXIT"}
UNSCORABLE_STATES = {"UNAVAILABLE", "NO_EDGE"}

AUTHORITY = {
    "shadow_only": True,
    "compass_change": False,
    "portfolio_action": False,
    "threshold_change": False,
    "canonical_state_change": False,
}


class LedgerInputError(ValueError):
    """Input cannot be scored without inventing semantics."""


def canonical_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
    return hashlib.sha256(payload.encode()).hexdigest()


def parse_utc(text: str) -> datetime:
    if not isinstance(text, str) or not text.endswith("Z"):
        raise LedgerInputError("timestamps must be explicit UTC ending in Z")
    try:
        value = datetime.fromisoformat(text[:-1] + "+00:00")
    except ValueError as exc:
        raise LedgerInputError("invalid UTC timestamp") from exc
    return value.astimezone(timezone.utc)


def load_returns(path: Path) -> dict[str, dict[date, float]]:
    series: dict[str, dict[date, float]] = {segment: {} for segment in SEGMENTS}
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        if "date" not in fields:
            raise LedgerInputError("date column missing")
        missing = [segment for segment in SEGMENTS if segment not in fields]
        if missing:
            raise LedgerInputError(f"segment columns missing: {missing}")
        for row in reader:
            day = date.fromisoformat(str(row["date"]))
            for segment in SEGMENTS:
                cell = str(row.get(segment) or "").strip()
                if not cell:
                    continue
                value = float(cell)
                if not (-1.0 < value < 10.0):
                    raise LedgerInputError(f"implausible decimal return for {segment} on {day}")
                series[segment][day] = value
    return series


def require_governed_segment_owner(path: Path) -> Mapping[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if value.get("contract") != SEGMENT_OWNER_CONTRACT:
        raise LedgerInputError("segment return metadata contract is not governed")
    if value.get("status") != "GOVERNED":
        raise LedgerInputError("segment return owner is not GOVERNED")
    if value.get("portfolio_execution") is not False:
        raise LedgerInputError("segment return owner authority must be non-execution")
    return value


@dataclass(frozen=True)
class TrendHysteresis:
    source: str = "BTC"
    ma_days: int = 100
    band: float = 0.05
    name: str = "CORE_STATE_BTC100_5PCT"

    def exposure(self, returns: Mapping[str, Mapping[date, float]], decision_day: date) -> float | None:
        source = returns[self.source]
        days = sorted(day for day in source if day < decision_day)
        if len(days) < self.ma_days + 1:
            return None
        level = 1.0
        levels: list[float] = []
        for day in days:
            level *= 1.0 + source[day]
            levels.append(level)
        state = 0.0
        for index in range(self.ma_days - 1, len(levels)):
            ma = sum(levels[index - self.ma_days + 1:index + 1]) / self.ma_days
            if state == 0.0 and levels[index] > ma * (1.0 + self.band):
                state = 1.0
            elif state == 1.0 and levels[index] < ma * (1.0 - self.band):
                state = 0.0
        return state


def challenger_target(name: str, returns: Mapping[str, Mapping[date, float]], decision_day: date) -> float | None:
    if name == "BUY_HOLD":
        return 1.0
    if name == "CASH":
        return 0.0
    if name == "CORE_STATE_BTC100_5PCT":
        return TrendHysteresis().exposure(returns, decision_day)
    raise LedgerInputError(f"unregistered challenger: {name}")


def compass_ladder(compass: Mapping[str, Any]) -> dict[str, dict[str, str | None]]:
    ladder = compass.get("capitalization_ladder")
    if not isinstance(ladder, list):
        raise LedgerInputError("capitalization_ladder missing")
    out: dict[str, dict[str, str | None]] = {}
    for row in ladder:
        if not isinstance(row, Mapping):
            continue
        segment = str(row.get("segment") or "")
        if segment in SEGMENTS:
            action_raw = row.get("action")
            out[segment] = {
                "status": str(row.get("status") or "").upper(),
                "action": str(action_raw).upper() if isinstance(action_raw, str) and action_raw else None,
            }
    if set(out) != set(SEGMENTS):
        raise LedgerInputError("capitalization_ladder incomplete")
    return out


def next_compass_exposure(previous: float, compass_action: str | None) -> float | None:
    if compass_action is None:
        return None
    state = str(compass_action or "").upper()
    if state in NO_TRADE_STATES:
        return previous
    if state in ENTER_STATES:
        return 1.0
    if state in EXIT_STATES:
        return 0.0
    if state in UNSCORABLE_STATES:
        return None
    raise LedgerInputError(f"unmapped ladder action: {state}")

def realised_return(
    returns: Mapping[str, Mapping[date, float]],
    segment: str,
    decision_day: date,
    horizon_days: int,
) -> float | None:
    total = 1.0
    for offset in range(1, horizon_days + 1):
        value = returns[segment].get(decision_day + timedelta(days=offset))
        if value is None:
            return None
        total *= 1.0 + value
    return total - 1.0


def _iso_week_key(compass: Mapping[str, Any]) -> tuple[int, int]:
    issued = parse_utc(str(compass.get("issued_at_utc")))
    iso = issued.date().isocalendar()
    return int(iso.year), int(iso.week)


def _first_ok_freeze_ids(compasses: Sequence[Mapping[str, Any]]) -> set[str]:
    first: dict[tuple[int, int], tuple[datetime, str]] = {}
    for compass in compasses:
        if compass.get("data_status") != "OK":
            continue
        issued = parse_utc(str(compass.get("issued_at_utc")))
        cid = str(compass.get("compass_id") or "")
        key = _iso_week_key(compass)
        prior = first.get(key)
        if prior is None or issued < prior[0]:
            first[key] = (issued, cid)
    return {value[1] for value in first.values()}


def score_compasses(
    compasses: Sequence[Mapping[str, Any]],
    returns: Mapping[str, Mapping[date, float]],
    as_of: datetime,
) -> list[dict[str, Any]]:
    ordered = sorted(
        (c for c in compasses if c.get("data_status") == "OK"),
        key=lambda c: parse_utc(str(c.get("issued_at_utc"))),
    )
    weekly_ids = _first_ok_freeze_ids(ordered)

    compass_exposure: dict[tuple[str, str], float] = {}
    challenger_exposure: dict[tuple[str, str, str], float] = {}
    rows: list[dict[str, Any]] = []

    for compass in ordered:
        issued = parse_utc(str(compass.get("issued_at_utc")))
        decision_day = issued.date()
        ladder = compass_ladder(compass)
        compass_id = str(compass.get("compass_id") or "")
        if not compass_id:
            raise LedgerInputError("compass_id missing")

        current_compass: dict[tuple[str, str], float | None] = {}
        compass_turnover: dict[tuple[str, str], float | None] = {}
        for interpretation in INTERPRETATIONS:
            initial = 1.0 if interpretation == "INCUMBENT_HOLDER" else 0.0
            for segment in SEGMENTS:
                key = (interpretation, segment)
                previous = compass_exposure.get(key, initial)
                current = next_compass_exposure(previous, ladder[segment]["action"])
                current_compass[key] = current
                if current is None:
                    compass_turnover[key] = None
                    continue
                turnover = abs(current - previous)
                compass_turnover[key] = turnover
                compass_exposure[key] = current

        current_challenger: dict[tuple[str, str, str], float | None] = {}
        challenger_turnover: dict[tuple[str, str, str], float | None] = {}
        for interpretation in INTERPRETATIONS:
            for segment in SEGMENTS:
                for challenger in CHALLENGERS:
                    key = (interpretation, segment, challenger)
                    target = challenger_target(challenger, returns, decision_day)
                    current_challenger[key] = target
                    if target is None:
                        challenger_turnover[key] = None
                        continue
                    initial = 1.0 if interpretation == "INCUMBENT_HOLDER" else 0.0
                    previous = challenger_exposure.get(key, initial)
                    turnover = abs(target - previous)
                    challenger_turnover[key] = turnover
                    challenger_exposure[key] = target

        for horizon_days in HORIZON_DAYS:
            matures_at = datetime.combine(
                decision_day + timedelta(days=horizon_days + 1),
                datetime.min.time(),
                timezone.utc,
            )
            for segment in SEGMENTS:
                realised = realised_return(returns, segment, decision_day, horizon_days) if as_of >= matures_at else None
                base_status = (
                    "PENDING_MATURITY"
                    if as_of < matures_at
                    else ("SCORED" if realised is not None else "DATA_MISSING")
                )
                for interpretation in INTERPRETATIONS:
                    ckey = (interpretation, segment)
                    c_exp = current_compass[ckey]
                    c_turn = compass_turnover[ckey]
                    for challenger in CHALLENGERS:
                        xkey = (interpretation, segment, challenger)
                        x_exp = current_challenger[xkey]
                        x_turn = challenger_turnover[xkey]
                        status = base_status
                        if c_exp is None:
                            status = "COMPASS_ACTION_UNSCORABLE"
                        elif x_exp is None:
                            status = "CHALLENGER_INSUFFICIENT_HISTORY"

                        row: dict[str, Any] = {
                            "contract": ROW_CONTRACT,
                            "compass_id": compass_id,
                            "compass_sha256": compass.get("compass_sha256"),
                            "issued_at_utc": compass.get("issued_at_utc"),
                            "weekly_inference_unit": compass_id in weekly_ids,
                            "segment": segment,
                            "horizon_days": horizon_days,
                            "interpretation": interpretation,
                            "challenger": challenger,
                            "ladder_status": ladder[segment]["status"],
                            "compass_action": ladder[segment]["action"],
                            "compass_exposure": c_exp,
                            "challenger_exposure": x_exp,
                            "compass_turnover": c_turn,
                            "challenger_turnover": x_turn,
                            "status": status,
                            "matures_at_utc": matures_at.isoformat().replace("+00:00", "Z"),
                            "realised_return": None,
                            "compass_pnl": None,
                            "challenger_pnl": None,
                            "paired_delta": None,
                            "authority": AUTHORITY,
                        }
                        if status == "SCORED":
                            cost = ONE_WAY_COST[segment]
                            row["realised_return"] = realised
                            row["compass_pnl"] = float(c_exp) * float(realised) - float(c_turn) * cost
                            row["challenger_pnl"] = float(x_exp) * float(realised) - float(x_turn) * cost
                            row["paired_delta"] = row["compass_pnl"] - row["challenger_pnl"]

                        row["row_id"] = canonical_hash({
                            key: row[key]
                            for key in ("compass_id", "horizon_days", "segment", "interpretation", "challenger")
                        })
                        row["row_sha256"] = canonical_hash({key: value for key, value in row.items() if key != "row_sha256"})
                        rows.append(row)
    return rows


def summarise(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str, int, bool], list[float]] = {}
    for row in rows:
        if row.get("status") != "SCORED":
            continue
        delta = row.get("paired_delta")
        if not isinstance(delta, (int, float)):
            continue
        key = (
            str(row["interpretation"]),
            str(row["challenger"]),
            str(row["segment"]),
            int(row["horizon_days"]),
            bool(row.get("weekly_inference_unit")),
        )
        groups.setdefault(key, []).append(float(delta))
    out: list[dict[str, Any]] = []
    for key, values in sorted(groups.items()):
        out.append({
            "interpretation": key[0],
            "challenger": key[1],
            "segment": key[2],
            "horizon_days": key[3],
            "weekly_inference_unit": key[4],
            "n_scored": len(values),
            "mean_paired_delta": sum(values) / len(values),
            "share_compass_better": sum(value > 0 for value in values) / len(values),
            "note": (
                "Primary inference requires weekly_inference_unit=true and the pre-registered minimum sample. "
                "Other rows are descriptive only."
            ),
        })
    return out


def load_compasses(root: Path) -> list[Mapping[str, Any]]:
    values: list[Mapping[str, Any]] = []
    for path in sorted(root.rglob("CMP-*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("contract") == "OFFICIAL_DAILY_COMPASS_v1":
            values.append(value)
    return values


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Decision Economics Ledger v1.2, shadow only.")
    parser.add_argument("--compass-root", type=Path, default=Path("04_MARKET_LEARNING/handlekompas/official/daily"))
    parser.add_argument("--segment-returns", type=Path, required=True)
    parser.add_argument("--segment-return-metadata", type=Path, required=True)
    parser.add_argument("--as-of-utc", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)

    owner = require_governed_segment_owner(args.segment_return_metadata)
    returns = load_returns(args.segment_returns)
    as_of = parse_utc(args.as_of_utc)
    rows = score_compasses(load_compasses(args.compass_root), returns, as_of)
    result = {
        "contract": RUN_CONTRACT,
        "as_of_utc": args.as_of_utc,
        "segment_return_owner": owner,
        "row_count": len(rows),
        "scored_count": sum(row.get("status") == "SCORED" for row in rows),
        "summary": summarise(rows),
        "rows": rows,
        "authority": AUTHORITY,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"rows": len(rows), "scored": result["scored_count"], "shadow_only": True}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
