from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from .validation import ContractViolation, parse_timestamp

ETF_PIT_DECISION_ID = "ISSUE_1211_D1_D7"
ETF_PIT_FIRST_TIMED_CAPTURE_UTC = "2026-07-15T20:48:00Z"
ETF_PIT_FIRST_TIMED_SESSION = "2026-07-15"
ETF_PIT_TRAILING_METHOD_ID = "ETF_TRAILING_ONLY_FEATURES_PIT_v2"
ETF_PIT_DIVERGENCE_METHOD_ID = "BTC_ETH_ETF_FLOW_DIVERGENCE_PIT_v2"

_ALLOWED_SCHEMA_STATUS = {"KNOWN_SCHEMA", "KNOWN_ADDITIVE_SCHEMA_REVISION"}
_ALLOWED_COMPLETE = {"COMPLETE", "COMPLETE_WITH_STRUCTURAL_DASH"}
_ALLOWED_VERIFIED_FINALITY = {"VERIFIED_STABLE_AT_OBSERVATION", "SUPERSEDED"}
_VALUE_CELL_STATUS = {"REPORTED", "REPORTED_ZERO"}
_EMPTY_CELL_STATUS = {"DASH_STRUCTURAL", "ABSENT_COLUMN"}


def _iso(value: str) -> str:
    return parse_timestamp(value).isoformat().replace("+00:00", "Z")


def _sign(value: float) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def _require_observation_shape(observation: dict[str, Any]) -> None:
    if observation.get("contract") != "ETF_OBSERVATION_v1":
        raise ContractViolation("ETF PIT replay requires ETF_OBSERVATION_v1")
    if observation.get("asset") not in {"BTC", "ETH"}:
        raise ContractViolation(f"unsupported ETF asset: {observation.get('asset')!r}")
    schema_status = (observation.get("schema") or {}).get("schema_status")
    if schema_status not in _ALLOWED_SCHEMA_STATUS:
        raise ContractViolation(f"ETF PIT replay refuses schema status: {schema_status!r}")


def map_etf_observation_to_pit_row(observation: dict[str, Any]) -> dict[str, Any] | None:
    """Map one observed ETF vintage into the official #1211 PIT replay row.

    Ineligibility is fail-closed and returns None. No timestamp is synthesized.
    A SUPERSEDED vintage remains eligible for an earlier as-of cutoff because it
    was verified at that time; cutoff selection decides whether a later revision
    is visible.
    """
    _require_observation_shape(observation)

    if not observation.get("is_trading_session", False):
        return None
    session_date = str(observation["session_date"])
    if session_date < ETF_PIT_FIRST_TIMED_SESSION:
        return None
    if observation.get("knowledge_time_status") != "OBSERVED":
        return None

    knowledge_raw = observation.get("knowledge_available_at_utc")
    verification_raw = observation.get("verification_completed_at_utc")
    observed_raw = observation.get("source_observed_at_utc")
    if not knowledge_raw or not verification_raw or not observed_raw:
        return None

    knowledge = parse_timestamp(str(knowledge_raw))
    verification = parse_timestamp(str(verification_raw))
    first_capture = parse_timestamp(ETF_PIT_FIRST_TIMED_CAPTURE_UTC)
    if knowledge < first_capture:
        return None
    if knowledge != verification:
        raise ContractViolation(
            "official ETF PIT knowledge time must equal verification_completed_at_utc "
            f"under {ETF_PIT_DECISION_ID}"
        )

    if observation.get("finality_status") not in _ALLOWED_VERIFIED_FINALITY:
        return None
    if observation.get("completeness_status") not in _ALLOWED_COMPLETE:
        return None

    schema = observation["schema"]
    row = observation.get("row") or {}
    if row.get("all_dash_row") is True:
        return None
    if row.get("parity") is not True or row.get("reported_total") is None:
        return None

    fund_cells = row.get("fund_cells")
    if not isinstance(fund_cells, dict) or not fund_cells:
        raise ContractViolation("ETF PIT observation has no fund_cells")

    mapped_funds: dict[str, float | str] = {}
    for fund, cell in fund_cells.items():
        status = cell.get("cell_status")
        if status in _VALUE_CELL_STATUS:
            value = cell.get("value")
            if value is None:
                raise ContractViolation(f"{fund}: {status} requires numeric value")
            mapped_funds[fund] = float(value)
        elif status in _EMPTY_CELL_STATUS:
            mapped_funds[fund] = ""
        elif status == "DASH_UNRESOLVED":
            return None
        else:
            raise ContractViolation(f"{fund}: unsupported cell_status {status!r}")

    return {
        "asset": observation["asset"],
        "date": session_date,
        **mapped_funds,
        "total_usd_millions": float(row["reported_total"]),
        "knowledge_available_at_utc": _iso(str(knowledge_raw)),
        "knowledge_time_status": "OBSERVED",
        "knowledge_rule_id": ETF_PIT_DECISION_ID,
        "source_observed_at_utc": _iso(str(observed_raw)),
        "verification_completed_at_utc": _iso(str(verification_raw)),
        "schema_id": schema["schema_id"],
        "schema_status": schema["schema_status"],
        "vintage_seq": int((observation.get("revision") or {}).get("vintage_seq", 1)),
        "source": (observation.get("provenance") or {}).get("producer", "ETF_OBSERVATION_v1"),
        "method_id": "ETF_OBSERVATION_v1_TO_PIT_REPLAY_v2",
    }


def select_etf_pit_rows(
    observations: Iterable[dict[str, Any]],
    asset: str,
    cutoff_utc: str,
) -> list[dict[str, Any]]:
    """Bind each session to the latest eligible vintage knowable at cutoff."""
    if asset not in {"BTC", "ETH"}:
        raise ContractViolation(f"unsupported ETF asset: {asset!r}")
    cutoff = parse_timestamp(cutoff_utc)
    latest: dict[str, tuple[tuple[datetime, int, datetime], dict[str, Any]]] = {}

    for observation in observations:
        if observation.get("asset") != asset:
            continue
        mapped = map_etf_observation_to_pit_row(observation)
        if mapped is None:
            continue
        knowledge = parse_timestamp(mapped["knowledge_available_at_utc"])
        if knowledge > cutoff:
            continue
        observed = parse_timestamp(mapped["source_observed_at_utc"])
        order = (knowledge, int(mapped["vintage_seq"]), observed)
        previous = latest.get(mapped["date"])
        if previous is None or order > previous[0]:
            latest[mapped["date"]] = (order, mapped)

    return [latest[day][1] for day in sorted(latest)]


def build_etf_trailing_pit(rows: list[dict[str, Any]], asset: str) -> list[dict[str, Any]]:
    """Build official PIT trailing features without touching frozen W30 v1 outputs."""
    seen: set[str] = set()
    flows: list[float] = []
    streak = 0
    output: list[dict[str, Any]] = []
    feature_knowledge: datetime | None = None
    metadata_fields = {
        "asset", "date", "total_usd_millions", "knowledge_available_at_utc",
        "knowledge_time_status", "knowledge_rule_id", "source_observed_at_utc",
        "verification_completed_at_utc", "schema_id", "schema_status", "vintage_seq",
        "source", "method_id",
    }

    for index, row in enumerate(sorted(rows, key=lambda r: r["date"])):
        if row.get("asset") != asset:
            raise ContractViolation(f"ETF PIT row asset mismatch: expected {asset}, got {row.get('asset')!r}")
        date_text = str(row["date"])
        if date_text in seen:
            raise ContractViolation(f"duplicate ETF PIT session: {date_text}")
        if datetime.fromisoformat(date_text).date().weekday() >= 5:
            raise ContractViolation(f"weekend ETF PIT row forbidden: {date_text}")
        seen.add(date_text)
        if row.get("knowledge_time_status") != "OBSERVED":
            raise ContractViolation(f"ETF PIT row lacks observed knowledge time: {date_text}")
        if row.get("knowledge_rule_id") != ETF_PIT_DECISION_ID:
            raise ContractViolation(f"ETF PIT row lacks owner decision {ETF_PIT_DECISION_ID}: {date_text}")

        row_knowledge = parse_timestamp(str(row["knowledge_available_at_utc"]))
        feature_knowledge = row_knowledge if feature_knowledge is None else max(feature_knowledge, row_knowledge)

        flow = float(row["total_usd_millions"])
        flows.append(flow)
        sign = _sign(flow)
        if sign == 0:
            streak = 0
        elif index == 0 or _sign(flows[index - 1]) != sign:
            streak = sign
        else:
            streak += sign

        rolling = {
            window: sum(flows[-window:]) if len(flows) >= window else None
            for window in (1, 3, 5, 10, 20)
        }
        previous_3 = sum(flows[-4:-1]) if len(flows) >= 4 else None
        acceleration_3 = (
            rolling[3] - previous_3
            if rolling[3] is not None and previous_3 is not None
            else None
        )
        acceleration_1 = flow - flows[-2] if len(flows) >= 2 else None
        previous_sign = _sign(flows[-2]) if len(flows) >= 2 else 0

        fund_columns = [column for column in row if column not in metadata_fields]
        fund_abs = [
            abs(float(row[column]))
            for column in fund_columns
            if row[column] not in (None, "")
        ]
        concentration = max(fund_abs) / sum(fund_abs) if fund_abs and sum(fund_abs) else None

        output.append({
            "asset": asset,
            "date": date_text,
            "total_usd_millions": flow,
            "knowledge_available_at_utc": row["knowledge_available_at_utc"],
            "feature_knowledge_available_at_utc": feature_knowledge.isoformat().replace("+00:00", "Z"),
            "knowledge_rule_id": ETF_PIT_DECISION_ID,
            "rolling_net_flow_1s_usd_millions": rolling[1],
            "rolling_net_flow_3s_usd_millions": rolling[3],
            "rolling_net_flow_5s_usd_millions": rolling[5],
            "rolling_net_flow_10s_usd_millions": rolling[10],
            "rolling_net_flow_20s_usd_millions": rolling[20],
            "rolling_1s_complete": rolling[1] is not None,
            "rolling_3s_complete": rolling[3] is not None,
            "rolling_5s_complete": rolling[5] is not None,
            "rolling_10s_complete": rolling[10] is not None,
            "rolling_20s_complete": rolling[20] is not None,
            "signed_flow_streak_sessions": streak,
            "flow_acceleration_1s_usd_millions": acceleration_1,
            "flow_acceleration_3s_usd_millions": acceleration_3,
            "reversal_flag": sign != 0 and previous_sign != 0 and sign != previous_sign,
            "issuer_concentration_abs_share": concentration,
            "feature_method_id": ETF_PIT_TRAILING_METHOD_ID,
        })
    return output


def build_etf_divergence_pit(
    btc_rows: list[dict[str, Any]],
    eth_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    btc = {row["date"]: row for row in btc_rows}
    eth = {row["date"]: row for row in eth_rows}
    output: list[dict[str, Any]] = []
    for day in sorted(set(btc).intersection(eth)):
        btc_row = btc[day]
        eth_row = eth[day]
        btc_flow = float(btc_row["total_usd_millions"])
        eth_flow = float(eth_row["total_usd_millions"])
        knowledge = max(
            parse_timestamp(str(btc_row["knowledge_available_at_utc"])),
            parse_timestamp(str(eth_row["knowledge_available_at_utc"])),
        )
        output.append({
            "date": day,
            "total_usd_millions_btc": btc_flow,
            "total_usd_millions_eth": eth_flow,
            "btc_minus_eth_flow_usd_millions": btc_flow - eth_flow,
            "opposite_sign_divergence": _sign(btc_flow) * _sign(eth_flow) == -1,
            "feature_knowledge_available_at_utc": knowledge.isoformat().replace("+00:00", "Z"),
            "knowledge_rule_id": ETF_PIT_DECISION_ID,
            "method_id": ETF_PIT_DIVERGENCE_METHOD_ID,
        })
    return output


def replay_etf_pit_as_of(
    observations: Iterable[dict[str, Any]],
    cutoff_utc: str,
) -> dict[str, Any]:
    observations = list(observations)
    btc_rows = select_etf_pit_rows(observations, "BTC", cutoff_utc)
    eth_rows = select_etf_pit_rows(observations, "ETH", cutoff_utc)
    return {
        "contract": "ETF_PIT_REPLAY_v2",
        "owner_decision_id": ETF_PIT_DECISION_ID,
        "cutoff_utc": _iso(cutoff_utc),
        "btc_rows": btc_rows,
        "eth_rows": eth_rows,
        "btc_trailing": build_etf_trailing_pit(btc_rows, "BTC"),
        "eth_trailing": build_etf_trailing_pit(eth_rows, "ETH"),
        "divergence": build_etf_divergence_pit(btc_rows, eth_rows),
        "legacy_w30_outputs_modified": False,
    }
