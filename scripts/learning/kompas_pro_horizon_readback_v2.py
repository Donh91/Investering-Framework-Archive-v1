"""Pure source-conservative Kompas PRO horizon readback.

Presentation helpers only. This module DOES NOT read market data, admit source
custody, issue forecasts, score performance, run API calls or grant actions.
Upstream owners MUST authenticate actual source receipts and status. These
guards protect against accidental promotion of shadow or qualitative values.
"""
from __future__ import annotations

from datetime import datetime, timezone
import math
import re
from typing import Any, Mapping

CONTRACT = "KOMPAS_PRO_INTERNAL_HORIZON_IMPLEMENTATION_LEDGER_v2"
HORIZON_IDS = (
    "NOW", "H0_12H", "H24H", "H1_3D", "H5_7D", "H8_14D",
    "H15_21D", "H2_3W", "H21_30D", "H4_8W", "H1_3M",
    "H3_6M", "H6_9M", "H9_12M",
)
STATUSES = frozenset(("OBSERVED", "OFFICIAL_DIRECTION", "ISSUED_NUMERIC", "RESEARCH_ONLY", "NOT_ISSUED"))
DIRECTIONS = frozenset(("UP", "CAUTIOUS_UP", "MIXED", "CAUTIOUS_DOWN", "DOWN", "UNAVAILABLE"))
COLORS = {
    "UP": "GREEN", "CAUTIOUS_UP": "LIGHT_GREEN", "MIXED": "AMBER",
    "CAUTIOUS_DOWN": "ORANGE", "DOWN": "RED", "UNAVAILABLE": "GREY",
}
SHA = re.compile(r"[0-9a-f]{64}\Z")
UTC_STAMP = re.compile(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?Z\Z")
NUMERIC_FIELDS = ("low", "expected_close", "high")


def _utc(value: Any) -> datetime:
    if not isinstance(value, str) or not UTC_STAMP.fullmatch(value):
        raise ValueError("SOURCE_TIMESTAMP_MUST_BE_EXACT_UTC")
    return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)


def validate_route_and_ledger(route: Mapping[str, Any], ledger: Mapping[str, Any]) -> None:
    """Check static contract binding; doesn't claim source availability."""
    if ledger.get("contract") != CONTRACT or ledger.get("classification") != "ROUTING_PRESENTATION_AND_IMPLEMENTATION_PLAN_ONLY":
        raise ValueError("INVALID_KOMPAS_V2_CONTRACT")
    if route.get("contract") != "GLOBAL_ACTION_COMPASS_ROUTE_v1":
        raise ValueError("ORIGINAL_ROUTING_CONTRACT_MISSING")
    out = route.get("output") or {}
    fmt = out.get("kompas_pro_presentational_contract") or {}
    full = route.get("full_stack_compass_default") or {}
    if fmt.get("horizon_implementation_ledger") != ledger.get("canonical_prose", "").replace(
        "2026-11-02__kompas-pro-internal-output-and-forward-horizon-v2__owner-approved.md",
        "KOMPAS_PRO_HORIZON_IMPLEMENTATION_LEDGER_v2.json"):
        raise ValueError("LEDGER_REFERENCE_UNBOUND")
    if full.get("internal_horizon_contract") != CONTRACT or full.get("internal_horizon_ids") != list(HORIZON_IDS):
        raise ValueError("FULL_HORIZON_ORDER_MISMATCH")
    if fmt.get("deep_internal_analysis_required_before_visible_answer") is not True or full.get("deep_analysis_families_required_before_render") is not True:
        raise ValueError("INTERNAL_DEPTH_NOT_REQUIRED")
    if "kompas" not in (route.get("hard_triggers") or ()) or (out.get("prompt_presentation_routing") or {}).get("kompas") != "KOMPAS_PRO_CURRENT":
        raise ValueError("ONE_WORD_KOMPAS_ROUTE_MISSING")
    if (out.get("visible_output_policy") != "TEXT_ONLY" or fmt.get("no_widgets") is not True or
            not str(fmt.get("btc_graph_preference", "")).endswith("NO_DOWNLOAD_LINK")):
        raise ValueError("CHAT_VISUAL_ROUTE_CONFLICT")
    if not all(bool(ledger.get("default_visible", {}).get(k)) for k in ("render_scale_without_widget", "render_scale_without_image", "unknown_is_grey")):
        raise ValueError("VISUAL_SCALE_NOT_PERMANENT")
    if (ledger.get("default_visible", {}).get("graph_assets") != ["BTC"] or
            ledger.get("default_visible", {}).get("mandatory_tables") !=
            ["MIT_TAKTISKE_KOMPAS", "AKTIVKLASSER"]):
        raise ValueError("MOBILE_OUTPUT_CONTRACT_MISSING")
    ids = [item.get("id") for item in ledger.get("horizons", ())]
    if ids != list(HORIZON_IDS) or len(ids) != len(set(ids)):
        raise ValueError("MISSING_DUPLICATE_OR_UNORDERED_HORIZON")
    if len(ledger.get("full_internal_required_families", ())) < 14:
        raise ValueError("INTERNAL_SOURCE_AUDIT_TOO_SHALLOW")
    if [p.get("id") for p in ledger.get("release_phases", ())] != ["G0", "G1", "G2", "G3", "G4", "G5", "G6"]:
        raise ValueError("RELEASE_CHAIN_MISSING")
    if not all(h.get("numeric_publication_default") == "NOT_ISSUED" and
               h.get("require_original_issue") is True and
               h.get("require_quote_parity") is True and h.get("action_owner") == "OFFICIAL_DAILY_COMPASS_ONLY"
               for h in ledger["horizons"]):
        raise ValueError("PRICE_OR_ACTION_AUTHORITY_PROMOTED")
    gates = ledger.get("release_gates", {})
    if not all(gates.get(k) is True for k in
               ("requires_exact_head_ci", "independent_review_on_consequential_changes",
                "high_impact_requires_separate_vault_restore", "main_sha_lease_before_merge",
                "postmerge_natural_readback", "no_auto_promotion_of_shadow",
                "no_new_schedule", "no_new_API_spend")):
        raise ValueError("RELEASE_SAFETY_GATES_REMOVED")
    if not (ledger.get("graph_history", {}).get("green_actual_independent_of_blue") is True and
            ledger.get("graph_history", {}).get("missing_hours_interpolated") is False):
        raise ValueError("GRAPH_SOURCE_HONESTY_MISSING")


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (float, int)):
        raise ValueError("NUMERIC_PRICE_MUST_BE_FINITE_POSITIVE")
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("NUMERIC_PRICE_MUST_BE_FINITE_POSITIVE")
    return number


def build_visible_horizon_rows(ledger: Mapping[str, Any],
                               rows: Mapping[str, Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Project *already-authenticated* owner rows to minimal UI-safe status.

    Successful shape validation is not historical provider-first-known proof.
    No numerical forecast escapes this disconnected readback, even if a caller
    asserts 'verified' and supplies a plausible SHA. Existing Graph B or a
    future authenticated source consumer may separately render original prices.
    """
    if ledger.get("contract") != CONTRACT or [h.get("id") for h in ledger.get("horizons", [])] != list(HORIZON_IDS):
        raise ValueError("INVALID_HORIZON_LEDGER")
    if not isinstance(rows, Mapping) or set(rows) - set(HORIZON_IDS):
        raise ValueError("UNKNOWN_HORIZON_SOURCE")
    result = []
    for h in ledger["horizons"]:
        k = h["id"]
        row = rows.get(k) or {"status": "NOT_ISSUED"}
        if not isinstance(row, Mapping) or row.get("status") not in STATUSES:
            raise ValueError("INVALID_SOURCE_STATUS")
        status = row["status"]
        if status in ("NOT_ISSUED", "RESEARCH_ONLY"):
            if any(row.get(key) is not None for key in NUMERIC_FIELDS):
                raise ValueError("SHADOW_OR_NOT_ISSUED_PRICE_LEAK")
            direction = "UNAVAILABLE"
        elif status == "OBSERVED":
            if k != "NOW" or row.get("expected_close") is not None or row.get("low") is not None or row.get("high") is not None:
                raise ValueError("OBSERVED_AS_FORECAST")
            _number(row.get("observed_price"))
            _utc(row.get("observed_at_utc"))
            if not row.get("price_quote") in ("USDT", "USD"):
                raise ValueError("OBSERVED_QUOTE_MISSING")
            direction = "UNAVAILABLE"
        elif status == "OFFICIAL_DIRECTION":
            if row.get("direction_owner") != h["direction_owner"] or any(row.get(x) is not None for x in NUMERIC_FIELDS):
                raise ValueError("OFFICIAL_DIRECTION_CANNOT_MINT_PRICE")
            if h["direction_owner"] in ("STRATEGIC_COMPASS_RESEARCH", "STRATEGIC_COMPASS_LONG_RANGE_VALIDATOR", "CN_STRATEGIC_SHADOW"):
                raise ValueError("RESEARCH_DIRECTION_CANNOT_BE_OFFICIAL")
            direction = row.get("direction")
            if direction not in DIRECTIONS:
                raise ValueError("INVALID_OFFICIAL_DIRECTION")
        else:
            if k == "NOW" or row.get("price_owner") != h["price_owner"]:
                raise ValueError("NUMERIC_FORECAST_WRONG_OWNER")
            if not row.get("public_issuance_verified") is True or row.get("model_authority") not in ("ORIGINAL_CN_FORECAST", "ORIGINAL_FORWARD_PRICE_FORECAST"):
                raise ValueError("UNVERIFIED_NUMERIC_SOURCE")
            if not isinstance(row.get("original_issue_id"), str) or not row["original_issue_id"].strip():
                raise ValueError("ISSUE_ID_REQUIRED")
            if not isinstance(row.get("original_source_sha256"), str) or not SHA.fullmatch(row["original_source_sha256"]):
                raise ValueError("ORIGINAL_SOURCE_SHA_REQUIRED")
            known, issued, start, end = (_utc(row.get(key)) for key in
                                          ("source_first_known_at_utc", "issued_at_utc", "forecast_start_utc", "forecast_end_utc"))
            if not (known <= issued <= start < end):
                raise ValueError("FORECAST_NOT_PROSPECTIVE")
            quote = row.get("price_quote")
            if quote not in ("USDT", "USD"):
                raise ValueError("NUMERIC_QUOTE_MISSING")
            if quote == "USDT" and row.get("price_venue") != "BINANCE_SPOT_BTCUSDT":
                raise ValueError("USDT_PROVENANCE_MISMATCH")
            if row.get("price_semantics") not in ("terminal_close", "intraperiod_extrema", "daily_expected_close"):
                raise ValueError("PRICE_TARGET_TYPE_REQUIRED")
            values = [_number(row[key]) for key in NUMERIC_FIELDS if row.get(key) is not None]
            if not values or (row.get("low") is not None and row.get("high") is not None and
                              _number(row["low"]) > _number(row["high"])):
                raise ValueError("PRICE_BOUNDS_INVALID")
            if row.get("expected_close") is not None and row.get("low") is not None and row.get("high") is not None and not (
                    _number(row["low"]) <= _number(row["expected_close"]) <= _number(row["high"])):
                raise ValueError("EXPECTED_PRICE_OUTSIDE_BOUND")
            direction = row.get("direction", "UNAVAILABLE")
            if direction not in DIRECTIONS:
                raise ValueError("INVALID_ISSUED_DIRECTION")
            # The caller's 'verified' boolean and a correctly shaped SHA are
            # ASSERTIONS, not independent provider/source-custody proofs.
            # This disconnected projection MUST NOT publicly disclose a
            # numeric forecast. The existing original-source Graph B and any
            # future owner-certified original-issue consumer own that gate.
            direction = "UNAVAILABLE"
        result.append({
            "horizon_id": k, "label": h["label"],
            "status": "ORIGINAL_BINDING_REQUIRED" if status == "ISSUED_NUMERIC" else status,
            "direction": direction,
            "color": COLORS[direction],
            "price_status": "ORIGINAL_BINDING_REQUIRED" if status == "ISSUED_NUMERIC" else "NOT_ISSUED",
            "quote": row.get("price_quote") if status == "OBSERVED" else None,
            "observed_price": row.get("observed_price") if status == "OBSERVED" else None,
            "price_low": None,
            "price_expected_close": None,
            "price_high": None,
        })
    return result
