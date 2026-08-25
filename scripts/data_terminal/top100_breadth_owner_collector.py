#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import math
import re
import statistics
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

AUTHORITY = {"binding": False, "canonical_acceptance": False, "state_change": False, "portfolio_action": False}
ROTATION_AUTHORITY = {
    **AUTHORITY,
    "shadow_context_only": True,
    "shared_row_tournament_eligible": False,
    "can_create_outcome_rows": False,
}
BASE = "https://api.coingecko.com/api/v3/coins/markets"
BLOCKCHAINCENTER_URL = "https://www.blockchaincenter.net/altcoin-season-index/"
COINMARKETCAP_URL = "https://coinmarketcap.com/charts/altcoin-season-index/"
MAX_SOURCE_BYTES = 2_000_000
TIMEFRAMES = ("30", "90", "365")
STABLE_SYMBOLS = {
    "usdt", "usdc", "dai", "fdusd", "usde", "usds", "tusd", "usdd", "pyusd",
    "frax", "usdp", "gusd", "lusd", "susd", "crvusd",
}
BLOCKCHAINCENTER_METHOD = {
    "benchmark": "BTC",
    "published_score_definition": "PERCENT_OF_49_NON_BTC_CONSTITUENTS_OUTPERFORMING_BTC_ROUNDED_TO_INTEGER",
    "headline_horizon_days": 90,
    "captured_horizons_days": [30, 90, 365],
    "published_altcoin_season_threshold_inclusive": 75,
    "published_bitcoin_season_threshold_inclusive": 25,
    "published_universe_description": "TOP_50_COINS_WITH_BTC_BENCHMARK",
    "published_exclusions": ["STABLECOINS", "ASSET_BACKED_TOKENS"],
    "observation_semantics": "LIVE_POINT_IN_TIME_ROLLING_WINDOW_NOT_SETTLED_DAILY_CLOSE",
    "framework_role": "SHADOW_STATE_LABEL_AND_BREADTH_VALIDATION_ONLY",
}
COINMARKETCAP_METHOD = {
    "benchmark": "BTC",
    "published_score_definition": "PERCENT_OF_TOP_100_COINS_OUTPERFORMING_BTC_SCALED_1_TO_100",
    "headline_horizon_days": 90,
    "captured_horizons_days": [90],
    "published_altcoin_season_threshold_inclusive": 75,
    "published_bitcoin_season_threshold_inclusive": 25,
    "published_universe_description": "TOP_100_COINMARKETCAP_RANKED_COINS",
    "published_exclusions": ["STABLECOINS", "ASSET_BACKED_AND_WRAPPED_TOKENS"],
    "source_refresh_expectation": "DAILY",
    "component_returns_available_in_normalized_capture": False,
    "framework_role": "LOWER_GRADE_INDEPENDENT_METHOD_DISPERSION_CROSSCHECK_ONLY",
}


class E(RuntimeError):
    def __init__(self, status: str, msg: str):
        super().__init__(msg)
        self.status = status


class ScriptCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_script = False
        self.parts: list[str] = []
        self.scripts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.in_script = True
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.in_script:
            self.parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script" and self.in_script:
            self.scripts.append("".join(self.parts))
            self.in_script = False
            self.parts = []


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def fetch(url: str, timeout: int = 20, *, accept: str = "application/json") -> bytes:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "Investering-Breadth-Owner/1.3 shadow-research", "Accept": accept},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read(MAX_SOURCE_BYTES + 1)
    except urllib.error.HTTPError as exc:
        raise E("HTTP_ERROR", f"HTTP {exc.code}: {exc.read()[:240]!r}") from exc
    except Exception as exc:
        raise E("NETWORK_ERROR", str(exc)) from exc
    if not payload:
        raise E("EMPTY_RESPONSE", "empty response")
    if len(payload) > MAX_SOURCE_BYTES:
        raise E("SOURCE_TOO_LARGE", f"source exceeded {MAX_SOURCE_BYTES} bytes")
    return payload


def parse(payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    try:
        rows = json.loads(payload)
    except Exception as exc:
        raise E("SCHEMA_DRIFT", "invalid json") from exc
    if not isinstance(rows, list) or len(rows) < 100:
        count = len(rows) if isinstance(rows, list) else "non-list"
        raise E("INCOMPLETE_UNIVERSE", f"expected >=100 raw rows, got {count}")
    seen: set[str] = set()
    ranked: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    required = ("id", "symbol", "name", "market_cap", "current_price", "price_change_percentage_24h")
    for source_rank, row in enumerate(rows, 1):
        if not isinstance(row, dict) or any(key not in row for key in required):
            raise E("SCHEMA_DRIFT", f"row {source_rank} missing fields or is not object")
        asset_id = str(row["id"])
        symbol = str(row["symbol"]).lower()
        if asset_id in seen:
            raise E("DUPLICATE_ASSET", asset_id)
        seen.add(asset_id)
        if symbol in STABLE_SYMBOLS:
            exclusions.append({"asset_id": asset_id, "symbol": symbol, "source_rank": source_rank, "reason": "STABLECOIN"})
            continue
        change = row["price_change_percentage_24h"]
        if row["market_cap"] is None or row["current_price"] is None or change is None:
            exclusions.append({
                "asset_id": asset_id,
                "symbol": symbol,
                "source_rank": source_rank,
                "reason": "MISSING_REQUIRED_VALUE",
            })
            continue
        ranked.append({
            "asset_id": asset_id,
            "symbol": symbol,
            "name": str(row["name"]),
            "source_rank": source_rank,
            "market_cap_usd": float(row["market_cap"]),
            "price_usd": float(row["current_price"]),
            "change_24h_pct": float(change),
        })
    constituents = ranked[:100]
    if len(constituents) != 100:
        raise E("INSUFFICIENT_FILTERED_UNIVERSE", f"expected 100, got {len(constituents)}")
    for filtered_rank, row in enumerate(constituents, 1):
        row["filtered_rank"] = filtered_rank
    membership = [{"filtered_rank": row["filtered_rank"], "asset_id": row["asset_id"]} for row in constituents]
    membership_hash = sha(canonical(membership))
    changes = [row["change_24h_pct"] for row in constituents]
    advancers = sum(value > 0 for value in changes)
    decliners = sum(value < 0 for value in changes)
    btc = next((row["change_24h_pct"] for row in constituents if row["asset_id"] == "bitcoin"), None)
    eth = next((row["change_24h_pct"] for row in constituents if row["asset_id"] == "ethereum"), None)
    aggregate = {
        "constituent_count": 100,
        "advancers": advancers,
        "decliners": decliners,
        "flat": 100 - advancers - decliners,
        "advancer_pct": advancers,
        "advance_ratio": round(advancers / 100, 6),
        "median_return_24h_pct": round(float(statistics.median(changes)), 6),
        "equal_weight_mean_return_24h_pct": round(sum(changes) / len(changes), 6),
        "btc_return_24h_pct": btc,
        "eth_return_24h_pct": eth,
        "outperforming_btc_count": sum(value > btc for value in changes) if btc is not None else None,
        "outperforming_eth_count": sum(value > eth for value in changes) if eth is not None else None,
        "membership_hash": membership_hash,
    }
    return constituents, exclusions, aggregate


def _walk_for_altcoin_props(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        if {"score", "stats", "latestScores", "change"}.issubset(value):
            return value
        for child in value.values():
            found = _walk_for_altcoin_props(child)
            if found is not None:
                return found
    elif isinstance(value, list):
        for child in value:
            found = _walk_for_altcoin_props(child)
            if found is not None:
                return found
    return None


def parse_blockchaincenter(payload: bytes) -> dict[str, Any]:
    parser = ScriptCollector()
    try:
        parser.feed(payload.decode("utf-8"))
    except Exception as exc:
        raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", "invalid UTF-8/HTML") from exc
    pattern = re.compile(r"self\.__next_f\.push\(\[1,((?:\"(?:\\.|[^\"\\])*\")|null)\]\)", re.S)
    for script in parser.scripts:
        if "latestScores" not in script:
            continue
        for match in pattern.finditer(script):
            try:
                flight_payload = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
            if not isinstance(flight_payload, str) or "latestScores" not in flight_payload:
                continue
            array_start = flight_payload.find("[")
            try:
                tree, _ = json.JSONDecoder().raw_decode(flight_payload, array_start)
            except (json.JSONDecodeError, ValueError):
                continue
            props = _walk_for_altcoin_props(tree)
            if props is not None:
                return props
    raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", "Next.js Altcoin Season props not found")


def _finite_float(value: Any, field: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"{field} is not numeric") from exc
    if not math.isfinite(number):
        raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"{field} is not finite")
    return number


def _source_state(score: int) -> str:
    return "ALTCOIN_SEASON" if score >= 75 else "BITCOIN_SEASON" if score <= 25 else "BETWEEN_PUBLISHED_THRESHOLDS"


def build_rotation_context(payload: bytes, retrieval: str) -> dict[str, Any]:
    props = parse_blockchaincenter(payload)
    scores, changes, histories, stats = (props.get(key) for key in ("latestScores", "change", "score", "stats"))
    if not all(isinstance(value, dict) for value in (scores, changes, histories, stats)):
        raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", "required props are not objects")
    required_stats = {
        "altseasondays", "bitcoinseasondays", "avg_alt_run", "avg_btc_run",
        "max_alt_run", "max_btc_run", "days_since_last_alt", "days_since_last_btc",
        "longest_no_alt_streak", "longest_no_btc_streak", "current_alt_run_length", "current_btc_run_length",
    }
    horizons: dict[str, Any] = {}
    historical_series: dict[str, Any] = {}
    normalized_stats: dict[str, Any] = {}
    for horizon in TIMEFRAMES:
        if any(horizon not in value for value in (scores, changes, histories, stats)):
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"missing {horizon}-day payload")
        try:
            published_score = int(scores[horizon])
        except (TypeError, ValueError) as exc:
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"invalid {horizon}-day score") from exc
        if not 0 <= published_score <= 100:
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"out-of-range {horizon}-day score")
        source_returns = changes[horizon]
        if not isinstance(source_returns, dict) or "BTC" not in source_returns or len(source_returns) != 50:
            count = len(source_returns) if isinstance(source_returns, dict) else "non-object"
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"expected BTC plus 49 assets for {horizon}d, got {count}")
        returns = {str(symbol): _finite_float(value, f"change.{horizon}.{symbol}") for symbol, value in source_returns.items()}
        btc_return = returns["BTC"]
        alt_returns = {symbol: value for symbol, value in returns.items() if symbol != "BTC"}
        outperformers = sum(value > btc_return for value in alt_returns.values())
        recomputed_score = round(100 * outperformers / len(alt_returns))
        if recomputed_score != published_score:
            raise E("BLOCKCHAINCENTER_RECONCILIATION_FAIL", f"{horizon}d published={published_score} recomputed={recomputed_score}")
        ordered = sorted(alt_returns.items(), key=lambda item: (item[1], item[0]), reverse=True)
        values = list(alt_returns.values())
        horizons[horizon] = {
            "horizon_days": int(horizon),
            "published_score": published_score,
            "recomputed_score": recomputed_score,
            "score_reconciliation": "PASS_EXACT",
            "source_state": _source_state(published_score),
            "benchmark_symbol": "BTC",
            "benchmark_return_decimal": btc_return,
            "alt_constituent_count": len(alt_returns),
            "outperforming_btc_count": outperformers,
            "outperforming_btc_share": round(outperformers / len(alt_returns), 12),
            "positive_alt_count": sum(value > 0 for value in values),
            "negative_alt_count": sum(value < 0 for value in values),
            "flat_alt_count": sum(value == 0 for value in values),
            "equal_weight_mean_alt_return_decimal": round(statistics.fmean(values), 12),
            "median_alt_return_decimal": round(float(statistics.median(values)), 12),
            "median_alt_minus_btc_return_decimal": round(float(statistics.median(value - btc_return for value in values)), 12),
            "membership_hash": sha(canonical(sorted(alt_returns))),
            "symbols": sorted(alt_returns),
            "top_5_alt_performers": [{"symbol": symbol, "return_decimal": value} for symbol, value in ordered[:5]],
            "bottom_5_alt_performers": [{"symbol": symbol, "return_decimal": value} for symbol, value in reversed(ordered[-5:])],
            "returns_decimal": dict(sorted(returns.items())),
        }
        series = histories[horizon]
        if not isinstance(series, dict) or not series:
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"empty {horizon}d historical series")
        normalized_series: dict[str, int] = {}
        for day, value in series.items():
            try:
                parsed_score = int(value)
                datetime.strptime(str(day), "%Y-%m-%d")
            except (TypeError, ValueError) as exc:
                raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"invalid {horizon}d historical point") from exc
            if not 0 <= parsed_score <= 100:
                raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"out-of-range {horizon}d historical point")
            normalized_series[str(day)] = parsed_score
        ordered_days = sorted(normalized_series)
        historical_series[horizon] = {
            "observation_count": len(normalized_series),
            "first_date": ordered_days[0],
            "last_date": ordered_days[-1],
            "last_score": normalized_series[ordered_days[-1]],
            "series_sha256": sha(canonical(normalized_series)),
            "full_series_retained_in_compressed_raw_artifact": True,
        }
        horizon_stats = stats[horizon]
        if not isinstance(horizon_stats, dict) or not required_stats.issubset(horizon_stats):
            raise E("BLOCKCHAINCENTER_SCHEMA_DRIFT", f"incomplete {horizon}d season statistics")
        normalized_stats[horizon] = horizon_stats
    return {
        "contract": "BLOCKCHAINCENTER_ALTCOIN_SEASON_SHADOW_CONTEXT_v1",
        "status": "PASS",
        "retrieved_at_utc": retrieval,
        "observation_date_utc": retrieval[:10],
        "source": {
            "provider": "BlockchainCenter",
            "url": BLOCKCHAINCENTER_URL,
            "transport": "PUBLIC_HTML_NEXTJS_FLIGHT_PAYLOAD",
            "raw_bytes": len(payload),
            "raw_sha256": sha(payload),
            "parser_contract": "NEXTJS_FLIGHT_ALTCOIN_PROPS_v1",
        },
        "methodology": {**BLOCKCHAINCENTER_METHOD, "methodology_fingerprint_sha256": sha(canonical(BLOCKCHAINCENTER_METHOD))},
        "headline": horizons["90"],
        "horizons": horizons,
        "season_statistics": normalized_stats,
        "historical_series_metadata": historical_series,
        "interpolation": False,
        "forward_fill": False,
        "backfill_materialized_as_daily_rows": False,
        "market_interpretation": False,
        "authority": ROTATION_AUTHORITY,
    }


def degraded_rotation_context(retrieval: str, failure_state: str, message: str) -> dict[str, Any]:
    return {
        "contract": "BLOCKCHAINCENTER_ALTCOIN_SEASON_SHADOW_CONTEXT_v1",
        "status": "DEGRADED",
        "retrieved_at_utc": retrieval,
        "observation_date_utc": retrieval[:10],
        "source": {
            "provider": "BlockchainCenter", "url": BLOCKCHAINCENTER_URL,
            "transport": "PUBLIC_HTML_NEXTJS_FLIGHT_PAYLOAD", "raw_bytes": None,
            "raw_sha256": None, "parser_contract": "NEXTJS_FLIGHT_ALTCOIN_PROPS_v1",
        },
        "failure_state": failure_state,
        "failure_message": message[:500],
        "missing_semantics": "UNKNOWN_NOT_NEGATIVE_AND_NOT_NO_ROTATION",
        "methodology": {**BLOCKCHAINCENTER_METHOD, "methodology_fingerprint_sha256": sha(canonical(BLOCKCHAINCENTER_METHOD))},
        "horizons": {},
        "interpolation": False,
        "forward_fill": False,
        "backfill_materialized_as_daily_rows": False,
        "market_interpretation": False,
        "authority": ROTATION_AUTHORITY,
    }


def parse_coinmarketcap(payload: bytes) -> tuple[int, str | None]:
    parser = ScriptCollector()
    try:
        parser.feed(payload.decode("utf-8"))
    except Exception as exc:
        raise E("COINMARKETCAP_SCHEMA_DRIFT", "invalid UTF-8/HTML") from exc
    for script in parser.scripts:
        if '"altcoinIndex"' not in script:
            continue
        try:
            document = json.loads(script)
            raw_score = document["props"]["pageProps"]["pageSharedData"]["altcoinIndex"]
        except (json.JSONDecodeError, KeyError, TypeError):
            continue
        if isinstance(raw_score, bool):
            raise E("COINMARKETCAP_SCHEMA_DRIFT", "altcoinIndex is boolean")
        try:
            score = int(raw_score)
        except (TypeError, ValueError) as exc:
            raise E("COINMARKETCAP_SCHEMA_DRIFT", "altcoinIndex is not integer-like") from exc
        if str(score) != str(raw_score) and not isinstance(raw_score, int):
            raise E("COINMARKETCAP_SCHEMA_DRIFT", "altcoinIndex is not an exact integer")
        if not 0 <= score <= 100:
            raise E("COINMARKETCAP_SCHEMA_DRIFT", "altcoinIndex is out of range")
        build_id = document.get("buildId")
        return score, str(build_id) if build_id is not None else None
    raise E("COINMARKETCAP_SCHEMA_DRIFT", "__NEXT_DATA__ Altcoin Season score not found")


def build_coinmarketcap_context(payload: bytes, retrieval: str) -> dict[str, Any]:
    score, build_id = parse_coinmarketcap(payload)
    return {
        "contract": "COINMARKETCAP_ALTCOIN_SEASON_SHADOW_CROSSCHECK_v1",
        "status": "PASS",
        "retrieved_at_utc": retrieval,
        "observation_date_utc": retrieval[:10],
        "published_score": score,
        "source_state": _source_state(score),
        "horizon_days": 90,
        "source": {
            "provider": "CoinMarketCap", "url": COINMARKETCAP_URL,
            "transport": "PUBLIC_HTML_NEXT_DATA_PAYLOAD", "raw_bytes": len(payload),
            "raw_sha256": sha(payload), "source_build_id": build_id,
            "parser_contract": "NEXT_DATA_CMC_ALTCOIN_INDEX_v1",
        },
        "methodology": {**COINMARKETCAP_METHOD, "methodology_fingerprint_sha256": sha(canonical(COINMARKETCAP_METHOD))},
        "component_reconciliation": "NOT_AVAILABLE_FROM_CAPTURED_PAGE",
        "evidence_grade": "PUBLISHED_LABEL_ONLY",
        "interpolation": False,
        "forward_fill": False,
        "backfill_materialized_as_daily_rows": False,
        "market_interpretation": False,
        "authority": ROTATION_AUTHORITY,
    }


def degraded_coinmarketcap_context(retrieval: str, failure_state: str, message: str) -> dict[str, Any]:
    return {
        "contract": "COINMARKETCAP_ALTCOIN_SEASON_SHADOW_CROSSCHECK_v1",
        "status": "DEGRADED",
        "retrieved_at_utc": retrieval,
        "observation_date_utc": retrieval[:10],
        "published_score": None,
        "source_state": "UNKNOWN",
        "horizon_days": 90,
        "source": {
            "provider": "CoinMarketCap", "url": COINMARKETCAP_URL,
            "transport": "PUBLIC_HTML_NEXT_DATA_PAYLOAD", "raw_bytes": None,
            "raw_sha256": None, "source_build_id": None,
            "parser_contract": "NEXT_DATA_CMC_ALTCOIN_INDEX_v1",
        },
        "methodology": {**COINMARKETCAP_METHOD, "methodology_fingerprint_sha256": sha(canonical(COINMARKETCAP_METHOD))},
        "failure_state": failure_state,
        "failure_message": message[:500],
        "missing_semantics": "UNKNOWN_NOT_NEGATIVE_AND_NOT_NO_ROTATION",
        "component_reconciliation": "NOT_AVAILABLE_FROM_CAPTURED_PAGE",
        "evidence_grade": "PUBLISHED_LABEL_ONLY",
        "interpolation": False,
        "forward_fill": False,
        "backfill_materialized_as_daily_rows": False,
        "market_interpretation": False,
        "authority": ROTATION_AUTHORITY,
    }


def verify(root: Path) -> dict[str, Any]:
    try:
        manifest = json.loads((root / "artifact_manifest.json").read_text())
        owner = json.loads((root / "owner_snapshot.json").read_text())
    except Exception:
        return {"status": "FAIL", "member_count": 0, "failures": [{"path": "metadata", "error": "INVALID_JSON"}]}
    failures: list[dict[str, str]] = []
    for member in manifest["members"]:
        path = root / member["path"]
        if not path.is_file():
            failures.append({"path": member["path"], "error": "MISSING"})
            continue
        payload = path.read_bytes()
        if len(payload) != member["bytes"] or sha(payload) != member["sha256"]:
            failures.append({"path": member["path"], "error": "HASH_OR_SIZE"})
    replay_hash = sha(canonical([
        {"filtered_rank": row["filtered_rank"], "asset_id": row["asset_id"]}
        for row in owner.get("constituents", [])
    ]))
    aggregate = owner.get("aggregate", {})
    if aggregate.get("membership_hash") != replay_hash or aggregate.get("constituent_count") != 100:
        failures.append({"path": "owner_snapshot.json", "error": "MEMBERSHIP_REPLAY_MISMATCH"})
    checks = (
        ("rotation_context", "rotation_context_snapshot.json", "raw_blockchaincenter_altcoin_season.html.gz", build_rotation_context),
        ("rotation_method_crosscheck", "rotation_method_crosscheck_snapshot.json", "raw_coinmarketcap_altcoin_season.html.gz", build_coinmarketcap_context),
    )
    for owner_key, snapshot_name, raw_name, builder in checks:
        context = owner.get(owner_key)
        snapshot_path = root / snapshot_name
        if not isinstance(context, dict) or not snapshot_path.is_file():
            failures.append({"path": snapshot_name, "error": "MISSING_CONTEXT"})
            continue
        try:
            stored = json.loads(snapshot_path.read_text())
        except Exception:
            stored = None
        if stored != context:
            failures.append({"path": snapshot_name, "error": "OWNER_CONTEXT_MISMATCH"})
        if context.get("status") == "PASS":
            try:
                replay = builder(gzip.decompress((root / raw_name).read_bytes()), str(context.get("retrieved_at_utc")))
            except Exception:
                replay = None
            if replay != context:
                failures.append({"path": raw_name, "error": "CONTEXT_REPLAY_MISMATCH"})
    return {"status": "PASS" if not failures else "FAIL", "member_count": len(manifest["members"]), "failures": failures}


def _materialize_context(
    payload: bytes | None,
    error: dict[str, str] | None,
    retrieval: str,
    output: Path,
    raw_name: str,
    builder: Any,
    degraded_builder: Any,
    fixture_label: str,
) -> dict[str, Any]:
    if payload is not None:
        (output / raw_name).write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
        try:
            return builder(payload, retrieval)
        except E as exc:
            context = degraded_builder(retrieval, exc.status, str(exc))
            context["source"]["raw_bytes"] = len(payload)
            context["source"]["raw_sha256"] = sha(payload)
            return context
    if error:
        return degraded_builder(
            retrieval,
            error.get("failure_state", "SOURCE_UNAVAILABLE"),
            error.get("message", "source unavailable"),
        )
    return degraded_builder(
        retrieval,
        "FIXTURE_NOT_SUPPLIED",
        f"{fixture_label} fixture was not supplied; no live call was made in deterministic fixture mode.",
    )


def run(
    payload: bytes,
    output: Path,
    retrieval: str,
    rotation_payload: bytes | None = None,
    rotation_error: dict[str, str] | None = None,
    coinmarketcap_payload: bytes | None = None,
    coinmarketcap_error: dict[str, str] | None = None,
) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=True)
    for name in (
        "artifact_manifest.json", "owner_snapshot.json", "raw_blockchaincenter_altcoin_season.html.gz",
        "raw_coinmarketcap_altcoin_season.html.gz", "raw_source_payload.json", "receipt.json",
        "rotation_method_crosscheck_snapshot.json", "rotation_context_snapshot.json",
    ):
        (output / name).unlink(missing_ok=True)
    (output / "raw_source_payload.json").write_bytes(payload)
    constituents, exclusions, aggregate = parse(payload)
    rotation_context = _materialize_context(
        rotation_payload, rotation_error, retrieval, output, "raw_blockchaincenter_altcoin_season.html.gz",
        build_rotation_context, degraded_rotation_context, "BlockchainCenter",
    )
    coinmarketcap_context = _materialize_context(
        coinmarketcap_payload, coinmarketcap_error, retrieval, output, "raw_coinmarketcap_altcoin_season.html.gz",
        build_coinmarketcap_context, degraded_coinmarketcap_context, "CoinMarketCap",
    )
    run_id = "DT_TOP100_" + retrieval.replace("-", "").replace(":", "")[:15] + "_" + aggregate["membership_hash"][:12]
    owner = {
        "contract": "C5E_TOP100_BREADTH_OWNER_v1_2", "run_id": run_id,
        "retrieval_timestamp": retrieval, "freeze_timestamp": retrieval,
        "source": "COINGECKO_MARKET_CAP", "raw_rank_depth": 150,
        "ranking_metric": "market_cap_usd", "method_version": "TOP100_FILTERED_STABLE_EXCLUSION_RICH_BREADTH_v1_2",
        "constituents": constituents, "exclusions": exclusions, "aggregate": aggregate,
        "rotation_context": rotation_context, "rotation_method_crosscheck": coinmarketcap_context,
        "interpolation": False, "forward_fill": False, "authority": AUTHORITY,
    }
    receipt = {
        "run_id": run_id, "raw_sha256": sha(payload), "membership_hash": aggregate["membership_hash"],
        "constituent_count": 100, "aggregate_replay": "PASS",
        "rotation_context_status": rotation_context["status"],
        "rotation_context_failure_state": rotation_context.get("failure_state"),
        "rotation_crosscheck_status": coinmarketcap_context["status"],
        "rotation_crosscheck_failure_state": coinmarketcap_context.get("failure_state"),
        "status": "PASS", "authority": AUTHORITY,
    }
    (output / "owner_snapshot.json").write_text(json.dumps(owner, indent=2, sort_keys=True) + "\n")
    (output / "rotation_context_snapshot.json").write_text(json.dumps(rotation_context, indent=2, sort_keys=True) + "\n")
    (output / "rotation_method_crosscheck_snapshot.json").write_text(json.dumps(coinmarketcap_context, indent=2, sort_keys=True) + "\n")
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    members = []
    for path in sorted(candidate for candidate in output.rglob("*") if candidate.is_file()):
        member_payload = path.read_bytes()
        members.append({"path": path.relative_to(output).as_posix(), "bytes": len(member_payload), "sha256": sha(member_payload)})
    (output / "artifact_manifest.json").write_text(json.dumps({
        "contract": "C5E_ARTIFACT_MANIFEST_v1", "run_id": run_id, "members": members,
    }, indent=2, sort_keys=True) + "\n")
    return owner


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path)
    parser.add_argument("--blockchaincenter-fixture", type=Path)
    parser.add_argument("--coinmarketcap-fixture", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("top100-breadth-owner-output"))
    parser.add_argument("--retrieval-timestamp")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()
    retrieval = args.retrieval_timestamp or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    try:
        if args.fixture:
            payload = args.fixture.read_bytes()
        else:
            query = {
                "vs_currency": "usd", "order": "market_cap_desc", "per_page": 150, "page": 1,
                "sparkline": "false", "price_change_percentage": "24h",
            }
            payload = fetch(BASE + "?" + urllib.parse.urlencode(query), timeout=args.timeout)
        contexts: dict[str, bytes | dict[str, str] | None] = {
            "rotation_payload": args.blockchaincenter_fixture.read_bytes() if args.blockchaincenter_fixture else None,
            "rotation_error": None,
            "coinmarketcap_payload": args.coinmarketcap_fixture.read_bytes() if args.coinmarketcap_fixture else None,
            "coinmarketcap_error": None,
        }
        if not args.fixture:
            for payload_key, error_key, url in (
                ("rotation_payload", "rotation_error", BLOCKCHAINCENTER_URL),
                ("coinmarketcap_payload", "coinmarketcap_error", COINMARKETCAP_URL),
            ):
                if contexts[payload_key] is None:
                    try:
                        contexts[payload_key] = fetch(url, timeout=args.timeout, accept="text/html,application/xhtml+xml")
                    except E as exc:
                        contexts[error_key] = {"failure_state": exc.status, "message": str(exc)}
        owner = run(payload, args.output_dir, retrieval, **contexts)
        readback = verify(args.output_dir)
        print(json.dumps({
            "status": readback["status"], "run_id": owner["run_id"], "constituents": 100,
            "membership_hash": owner["aggregate"]["membership_hash"],
            "rotation_context_status": owner["rotation_context"]["status"],
            "rotation_context_failure_state": owner["rotation_context"].get("failure_state"),
            "rotation_crosscheck_status": owner["rotation_method_crosscheck"]["status"],
            "rotation_crosscheck_failure_state": owner["rotation_method_crosscheck"].get("failure_state"),
        }, sort_keys=True))
        return 0 if readback["status"] == "PASS" else 3
    except E as exc:
        print(json.dumps({"status": exc.status, "error": str(exc), "authority": AUTHORITY}, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
