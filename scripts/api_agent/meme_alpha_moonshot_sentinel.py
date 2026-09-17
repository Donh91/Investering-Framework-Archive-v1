from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any

GECKO_BASE = "https://api.geckoterminal.com/api/v2"
GECKO_ACCEPT = "application/json;version=20230203"
STABLE_OR_WRAPPED = {
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
    "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "0x6b175474e89094c44da98b954eedeac495271d0f",
}
FAMILIES = ("M", "W", "S", "P", "N")
MUTABLE_PATHS = {
    "birth_cohort_percentile_thresholds.buyer_velocity",
    "birth_cohort_percentile_thresholds.transaction_velocity",
    "birth_cohort_percentile_thresholds.volume_to_liquidity",
    "scanner.minimum_liquidity_usd_for_deep_dive",
    "convergence.minimum_signal_families_for_deep_dive",
    "convergence.minimum_signal_families_for_gamble_alert",
    "alert.default_expiry_minutes",
}


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_object(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text())
    if not isinstance(value, dict):
        raise ValueError(f"object_required:{path}")
    return value


def _number(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _parse_time(value: Any) -> int:
    if isinstance(value, (int, float)):
        return int(value)
    if not isinstance(value, str) or not value:
        return 0
    try:
        return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return 0


def _token_address_from_id(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    tail = value.split("_", 1)[-1].lower()
    return tail if tail.startswith("0x") and len(tail) == 42 else None


def _included_map(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        item["id"]: item
        for item in payload.get("included", [])
        if isinstance(item, dict) and isinstance(item.get("id"), str)
    }


def _choose_candidate_token(resource: dict[str, Any], included: dict[str, dict[str, Any]]) -> tuple[str | None, str | None, str | None]:
    rel = resource.get("relationships") if isinstance(resource.get("relationships"), dict) else {}
    ids: list[str] = []
    for key in ("base_token", "quote_token"):
        data = rel.get(key, {}).get("data") if isinstance(rel.get(key), dict) else None
        if isinstance(data, dict) and isinstance(data.get("id"), str):
            ids.append(data["id"])
    rows: list[tuple[str, dict[str, Any]]] = []
    for token_id in ids:
        address = _token_address_from_id(token_id)
        if address:
            rows.append((address, included.get(token_id, {})))
    preferred = [row for row in rows if row[0] not in STABLE_OR_WRAPPED]
    selected = preferred[0] if preferred else (rows[0] if rows else None)
    if not selected:
        return None, None, None
    address, meta = selected
    attrs = meta.get("attributes") if isinstance(meta.get("attributes"), dict) else {}
    return address, str(attrs.get("symbol") or "") or None, str(attrs.get("name") or "") or None


def normalize_gecko_pool(resource: dict[str, Any], included: dict[str, dict[str, Any]], *, now_unix: int | None = None) -> dict[str, Any] | None:
    attrs = resource.get("attributes") if isinstance(resource.get("attributes"), dict) else {}
    token_ca, symbol, name = _choose_candidate_token(resource, included)
    if not token_ca:
        return None
    created = _parse_time(attrs.get("pool_created_at"))
    now = int(now_unix or time.time())
    age_minutes = max(0.1, (now - created) / 60.0) if created else 999999.0
    txns = attrs.get("transactions") if isinstance(attrs.get("transactions"), dict) else {}
    volumes = attrs.get("volume_usd") if isinstance(attrs.get("volume_usd"), dict) else {}
    changes = attrs.get("price_change_percentage") if isinstance(attrs.get("price_change_percentage"), dict) else {}
    h1 = txns.get("h1") if isinstance(txns.get("h1"), dict) else {}
    m5 = txns.get("m5") if isinstance(txns.get("m5"), dict) else {}
    buys_h1, sells_h1 = _int(h1.get("buys")), _int(h1.get("sells"))
    buys_m5, sells_m5 = _int(m5.get("buys")), _int(m5.get("sells"))
    liq = _number(attrs.get("reserve_in_usd"))
    vol_h1, vol_m5 = _number(volumes.get("h1")), _number(volumes.get("m5"))
    fdv = _number(attrs.get("fdv_usd"))
    market_cap = _number(attrs.get("market_cap_usd")) or fdv
    denom_age = max(1.0, min(age_minutes, 60.0))
    return {
        "contract": "MOONSHOT_STAGE0_EVENT_v1",
        "network": "eth",
        "pool_id": resource.get("id"),
        "pool_address": str(attrs.get("address") or resource.get("id") or ""),
        "dex_id": (resource.get("relationships", {}).get("dex", {}).get("data", {}) or {}).get("id"),
        "token_ca": token_ca,
        "symbol": symbol,
        "name": name,
        "pool_created_at": attrs.get("pool_created_at"),
        "observed_at_unix": now,
        "age_minutes": round(age_minutes, 3),
        "liquidity_usd": liq,
        "market_cap_usd": market_cap,
        "fdv_usd": fdv,
        "volume_m5_usd": vol_m5,
        "volume_h1_usd": vol_h1,
        "buys_m5": buys_m5,
        "sells_m5": sells_m5,
        "buys_h1": buys_h1,
        "sells_h1": sells_h1,
        "buyer_velocity_per_minute": buys_h1 / denom_age,
        "transaction_velocity_per_minute": (buys_h1 + sells_h1) / denom_age,
        "volume_to_liquidity_h1": vol_h1 / liq if liq > 0 else 0.0,
        "liquidity_to_market_cap_pct": (100.0 * liq / market_cap) if market_cap > 0 else None,
        "price_change_h1_pct": _number(changes.get("h1")),
        "price_change_h6_pct": _number(changes.get("h6")),
        "raw_sha256": sha256_bytes(canonical_bytes(resource)),
    }


def fetch_gecko_new_pools(network: str = "eth", pages: int = 2, timeout: int = 20) -> list[dict[str, Any]]:
    resources: list[dict[str, Any]] = []
    seen: set[str] = set()
    for page in range(1, max(1, pages) + 1):
        url = f"{GECKO_BASE}/networks/{urllib.parse.quote(network)}/new_pools?page={page}&include=base_token,quote_token,dex"
        req = urllib.request.Request(url, headers={"Accept": GECKO_ACCEPT, "User-Agent": "Investering-Framework-Moonshot-Sentinel/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read())
        included = _included_map(payload)
        for item in payload.get("data", []):
            if not isinstance(item, dict):
                continue
            normalized = normalize_gecko_pool(item, included)
            if not normalized:
                continue
            identity = normalized["network"] + ":" + normalized["token_ca"] + ":" + normalized["pool_address"]
            if identity not in seen:
                seen.add(identity)
                resources.append(normalized)
    return resources


def percentile_rank(values: list[float], value: float) -> float:
    finite = [x for x in values if math.isfinite(x)]
    if not finite:
        return 0.0
    less = sum(1 for x in finite if x < value)
    equal = sum(1 for x in finite if x == value)
    return 100.0 * (less + 0.5 * equal) / len(finite)


def add_birth_cohort_percentiles(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    fields = {
        "buyer_velocity": "buyer_velocity_per_minute",
        "transaction_velocity": "transaction_velocity_per_minute",
        "volume_to_liquidity": "volume_to_liquidity_h1",
        "liquidity_resilience": "liquidity_usd",
    }
    values = {name: [_number(e.get(source)) for e in events] for name, source in fields.items()}
    output: list[dict[str, Any]] = []
    for event in events:
        row = copy.deepcopy(event)
        row["birth_cohort_percentiles"] = {
            name: round(percentile_rank(values[name], _number(event.get(source))), 3)
            for name, source in fields.items()
        }
        output.append(row)
    return output


def execution_gate(event: dict[str, Any], config: dict[str, Any]) -> tuple[bool, list[str]]:
    reasons: list[str] = []
    minimum = _number(config["scanner"].get("absolute_minimum_liquidity_usd"), 5000)
    if not str(event.get("token_ca") or "").startswith("0x"):
        reasons.append("IDENTITY_UNRESOLVED")
    if _number(event.get("liquidity_usd")) < minimum:
        reasons.append("NO_EXECUTABLE_LIQUIDITY")
    if _int(event.get("sells_h1")) < _int(config["microstructure"].get("minimum_successful_sells"), 3):
        reasons.append("INSUFFICIENT_SUCCESSFUL_SELL_EVIDENCE")
    return not reasons, reasons


def microstructure_signal(event: dict[str, Any], config: dict[str, Any]) -> tuple[bool, list[str]]:
    p = event.get("birth_cohort_percentiles") if isinstance(event.get("birth_cohort_percentiles"), dict) else {}
    thresholds = config["birth_cohort_percentile_thresholds"]
    passed = [key for key in ("buyer_velocity", "transaction_velocity", "volume_to_liquidity") if _number(p.get(key)) >= _number(thresholds.get(key), 100)]
    if _number(event.get("liquidity_usd")) < _number(config["scanner"].get("minimum_liquidity_usd_for_deep_dive"), 12000):
        return False, passed
    if abs(_number(event.get("price_change_h1_pct"))) > _number(config["microstructure"].get("maximum_one_hour_price_expansion_pct_for_fresh_alert"), 500):
        return False, passed + ["H1_ALREADY_EXTENDED"]
    if abs(_number(event.get("price_change_h6_pct"))) > _number(config["microstructure"].get("maximum_six_hour_price_expansion_pct_for_fresh_alert"), 1500):
        return False, passed + ["H6_ALREADY_EXTENDED"]
    return len(passed) >= 2, passed


def initial_triage(event: dict[str, Any], config: dict[str, Any], enrichment: dict[str, Any] | None = None) -> dict[str, Any]:
    enrichment = enrichment or {}
    exec_pass, exec_reasons = execution_gate(event, config)
    m_pass, m_evidence = microstructure_signal(event, config)
    families = {family: False for family in FAMILIES}
    families["M"] = bool(m_pass)
    for family in ("W", "S", "P", "N"):
        families[family] = bool(enrichment.get("families", {}).get(family)) if isinstance(enrichment.get("families"), dict) else False
    family_count = sum(1 for value in families.values() if value)
    deep_required = _int(config["convergence"].get("minimum_signal_families_for_deep_dive"), 2)
    percentiles = event.get("birth_cohort_percentiles") or {}
    exceptional_m = min(_number(percentiles.get("buyer_velocity")), _number(percentiles.get("transaction_velocity"))) >= 99.0 and m_pass
    state = "DEEP_DIVE" if exec_pass and (family_count >= deep_required or exceptional_m) else "SILENT"
    return {
        "contract": "MOONSHOT_TRIAGE_v1",
        "alert_state": state,
        "candidate_id": f"eth:{event.get('token_ca')}",
        "execution_gate_pass": exec_pass,
        "execution_gate_reasons": exec_reasons,
        "families": families,
        "family_count": family_count,
        "microstructure_evidence": m_evidence,
        "exceptional_microstructure_override": exceptional_m,
        "event": event,
    }


def assessor_schema() -> dict[str, Any]:
    family = {
        "type": "object",
        "additionalProperties": False,
        "required": ["state", "confidence", "evidence"],
        "properties": {
            "state": {"type": "string", "enum": ["PASS", "FAIL", "UNKNOWN"]},
            "confidence": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"]},
            "evidence": {"type": "array", "maxItems": 3, "items": {"type": "string"}},
        },
    }
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["archetype", "M", "W", "S", "P", "N", "fatal_risks", "remaining_convexity_multiple", "hundred_x_feasibility", "recommendation", "invalidate_if", "summary"],
        "properties": {
            "archetype": {"type": "string", "enum": ["PRODUCT_STEALTH", "PURE_MEME_CULTURE", "CABAL_WALLET_PROPAGATION", "ECOSYSTEM_NATIVE_EASTER_EGG", "LAUNCHPAD_NETWORK_EFFECT", "UNCLASSIFIED"]},
            "M": family, "W": family, "S": family, "P": family, "N": family,
            "fatal_risks": {"type": "array", "maxItems": 5, "items": {"type": "string"}},
            "remaining_convexity_multiple": {"type": "number", "minimum": 0},
            "hundred_x_feasibility": {"type": "string", "enum": ["PLAUSIBLE", "REMOTE", "UNSUPPORTED", "UNKNOWN"]},
            "recommendation": {"type": "string", "enum": ["REJECT", "WATCH", "GAMBLE_CANDIDATE"]},
            "invalidate_if": {"type": "array", "maxItems": 6, "items": {"type": "string"}},
            "summary": {"type": "string"},
        },
    }


def build_assessor_request(model: str, candidate: dict[str, Any], research: dict[str, Any]) -> dict[str, Any]:
    instructions = (
        "You are the final research-only Moonshot Sentinel adjudicator. The token can go to zero. "
        "Do not recommend position size, leverage, buy execution, averaging down or certainty. Judge only point-in-time evidence. "
        "Price appreciation by itself is not alpha. M=market microstructure, W=wallet quality/pre-social entries, "
        "S=independent exact-CA social propagation, P=authenticated live product/provenance/execution velocity, "
        "N=narrative novelty plus remaining convexity. Use PASS only with positive evidence available by the research timestamp; "
        "UNKNOWN is preferred to invention. GAMBLE_CANDIDATE means only that a fully disposable-risk manual gamble may deserve attention."
    )
    return {
        "model": model,
        "reasoning": {"effort": "medium", "context": "current_turn"},
        "store": False,
        "max_output_tokens": 1400,
        "instructions": instructions,
        "input": [{"role": "user", "content": [{"type": "input_text", "text": json.dumps({"candidate": candidate, "research_packet": research}, sort_keys=True)}]}],
        "text": {"format": {"type": "json_schema", "name": "moonshot_sentinel_assessment_v1", "strict": True, "schema": assessor_schema()}},
    }


def call_responses_api(payload: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("OPENAI_API_KEY_missing")
    req = urllib.request.Request("https://api.openai.com/v1/responses", data=canonical_bytes(payload), headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read())


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str) and response["output_text"]:
        return response["output_text"]
    parts: list[str] = []
    for item in response.get("output", []):
        if not isinstance(item, dict):
            continue
        for content in item.get("content", []):
            if isinstance(content, dict) and content.get("type") == "output_text":
                parts.append(str(content.get("text") or ""))
    return "".join(parts)


def assess(candidate: dict[str, Any], research: dict[str, Any], *, model: str = "gpt-5.6-luna", dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {
            "archetype": "UNCLASSIFIED",
            **{family: {"state": "UNKNOWN", "confidence": "LOW", "evidence": []} for family in FAMILIES},
            "fatal_risks": ["DRY_RUN"],
            "remaining_convexity_multiple": 0,
            "hundred_x_feasibility": "UNKNOWN",
            "recommendation": "WATCH",
            "invalidate_if": [],
            "summary": "Dry run",
        }
    response = call_responses_api(build_assessor_request(model, candidate, research))
    if response.get("status") == "incomplete":
        raise ValueError("assessor_output_incomplete")
    value = json.loads(extract_output_text(response))
    if not isinstance(value, dict):
        raise ValueError("assessment_must_be_object")
    return value


def final_alert_decision(triage: dict[str, Any], assessment: dict[str, Any], config: dict[str, Any], *, alerts_last_24h: int = 0) -> dict[str, Any]:
    passed = {family for family in FAMILIES if isinstance(assessment.get(family), dict) and assessment[family].get("state") == "PASS"}
    required = _int(config["convergence"].get("minimum_signal_families_for_gamble_alert"), 3)
    accepted_sets = [set(row) for row in config["convergence"].get("accepted_gamble_family_sets", [])]
    accepted_combo = any(combo <= passed for combo in accepted_sets) if accepted_sets else len(passed) >= required
    fatal = bool(assessment.get("fatal_risks"))
    convexity = _number(assessment.get("remaining_convexity_multiple"))
    min_convexity = _number(config["convexity"].get("minimum_remaining_convexity_multiple_for_gamble_alert"), 10)
    daily_cap = _int(config["alert"].get("daily_cap"), 3)
    if not triage.get("execution_gate_pass"):
        state = "SILENT"
    elif assessment.get("recommendation") == "GAMBLE_CANDIDATE" and len(passed) >= required and accepted_combo and not fatal and convexity >= min_convexity and alerts_last_24h < daily_cap:
        state = "MOONSHOT_GAMBLE_ALERT"
    elif assessment.get("recommendation") in {"WATCH", "GAMBLE_CANDIDATE"} and len(passed) >= 2:
        state = "MOONSHOT_WATCH"
    else:
        state = "SILENT"
    now = int(time.time())
    alert_id = "MS-" + sha256_bytes(canonical_bytes({"candidate": triage.get("candidate_id"), "state": state, "t": now // 300}))[:16]
    return {
        "contract": "MOONSHOT_ALERT_DECISION_v1",
        "alert_id": alert_id,
        "state": state,
        "lifecycle": "ACTIVE" if state in {"MOONSHOT_WATCH", "MOONSHOT_GAMBLE_ALERT"} else "EXPIRED",
        "created_unix": now,
        "expires_unix": now + 60 * _int(config["alert"].get("default_expiry_minutes"), 45),
        "candidate_id": triage.get("candidate_id"),
        "token_ca": (triage.get("event") or {}).get("token_ca"),
        "symbol": (triage.get("event") or {}).get("symbol"),
        "archetype": assessment.get("archetype"),
        "passed_families": sorted(passed),
        "remaining_convexity_multiple": assessment.get("remaining_convexity_multiple"),
        "hundred_x_feasibility": assessment.get("hundred_x_feasibility"),
        "summary": assessment.get("summary"),
        "invalidate_if": assessment.get("invalidate_if") or [],
        "risk_notice": "Experimental research alert. Total loss is plausible. No automatic execution or position-size recommendation."
    }


def _get_path(obj: dict[str, Any], path: str) -> Any:
    cur: Any = obj
    for part in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
    return cur


def _set_path(obj: dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    cur = obj
    for part in parts[:-1]:
        cur = cur.setdefault(part, {})
    cur[parts[-1]] = value


def _utility(metrics: dict[str, Any]) -> float:
    return 0.35 * _number(metrics.get("precision")) + 0.20 * _number(metrics.get("recall")) + 0.20 * _number(metrics.get("sellability_rate")) + 0.10 * min(1.0, _number(metrics.get("lead_time_score"))) + 0.15 * (1.0 - _number(metrics.get("false_positive_rate")))


def compare_challenger(champion_metrics: dict[str, Any], challenger_metrics: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    champion_u, challenger_u = _utility(champion_metrics), _utility(challenger_metrics)
    improvement_pct = 100.0 * (challenger_u - champion_u) / max(abs(champion_u), 1e-9)
    precision_ok = _number(challenger_metrics.get("precision")) >= _number(champion_metrics.get("precision"))
    sellability_ok = _number(challenger_metrics.get("sellability_rate")) >= _number(champion_metrics.get("sellability_rate"))
    fp_ok = _number(challenger_metrics.get("false_positive_rate")) <= _number(champion_metrics.get("false_positive_rate"))
    promote = improvement_pct >= _number(policy.get("requires_validation_utility_improvement_pct"), 5) and precision_ok and sellability_ok and fp_ok
    return {"champion_utility": round(champion_u, 6), "challenger_utility": round(challenger_u, 6), "utility_improvement_pct": round(improvement_pct, 3), "precision_non_degradation": precision_ok, "sellability_non_degradation": sellability_ok, "false_positive_non_increase": fp_ok, "promote_window": promote}


def propose_challengers(champion: dict[str, Any], error_ledger: dict[str, Any]) -> list[dict[str, Any]]:
    suggestions: list[tuple[str, float]] = []
    missed, false_pos, late = _int(error_ledger.get("missed_winners")), _int(error_ledger.get("false_positives")), _int(error_ledger.get("late_alerts"))
    if missed > false_pos:
        suggestions.extend([("birth_cohort_percentile_thresholds.buyer_velocity", -1.0), ("birth_cohort_percentile_thresholds.transaction_velocity", -1.0)])
    elif false_pos > missed:
        suggestions.extend([("birth_cohort_percentile_thresholds.buyer_velocity", 1.0), ("birth_cohort_percentile_thresholds.volume_to_liquidity", 1.0)])
    if late > 0:
        suggestions.append(("alert.default_expiry_minutes", -5.0))
    if not suggestions:
        return []
    challenger = copy.deepcopy(champion)
    changes: list[dict[str, Any]] = []
    for path, delta in suggestions[: min(2, _int(champion.get("evolution", {}).get("mutation_budget"), 2))]:
        if path not in MUTABLE_PATHS:
            continue
        old = _number(_get_path(challenger, path))
        new = old + delta
        if "percentile" in path:
            new = min(99.9, max(90.0, new))
        elif path.endswith("default_expiry_minutes"):
            new = min(120.0, max(15.0, new))
        _set_path(challenger, path, new)
        changes.append({"path": path, "old": old, "new": new})
    challenger["status"] = "SHADOW_CHALLENGER"
    evo = challenger.setdefault("evolution", {})
    evo["generation"] = _int(evo.get("generation")) + 1
    evo["parent_version"] = champion.get("version")
    challenger["version"] = f"{champion.get('version','1.0.0')}-g{evo['generation']}"
    challenger["autonomous_mutations"] = changes
    return [challenger] if changes else []


def promotion_decision(champion: dict[str, Any], challenger: dict[str, Any], windows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    policy = contract["adaptive_evolution"]["auto_promotion"]
    matured = sum(_int(w.get("matured_observations")) for w in windows)
    days = len({str(w.get("date")) for w in windows if w.get("date")})
    events = sum(_int(w.get("alerted_or_control_events")) for w in windows)
    comparisons = [compare_challenger(w["champion"], w["challenger"], policy) for w in windows if isinstance(w.get("champion"), dict) and isinstance(w.get("challenger"), dict)]
    consecutive_required = 2 if policy.get("requires_two_consecutive_validation_windows") else 1
    consecutive = best = 0
    for row in comparisons:
        consecutive = consecutive + 1 if row["promote_window"] else 0
        best = max(best, consecutive)
    guards = {
        "matured_observations": matured >= _int(policy.get("minimum_matured_observations"), 50),
        "distinct_calendar_days": days >= _int(policy.get("minimum_distinct_calendar_days"), 14),
        "alerted_or_control_events": events >= _int(policy.get("minimum_alerted_or_control_events"), 10),
        "consecutive_validation_windows": best >= consecutive_required,
        "mutation_budget": len(challenger.get("autonomous_mutations") or []) <= 2,
        "authority_unchanged": challenger.get("risk") == champion.get("risk"),
    }
    promote = all(guards.values())
    return {"contract": "MOONSHOT_EVOLUTION_DECISION_v1", "champion_version": champion.get("version"), "challenger_version": challenger.get("version"), "guards": guards, "window_comparisons": comparisons, "decision": "AUTO_PROMOTE_RESEARCH_CHAMPION" if promote else "KEEP_CHAMPION", "production_execution_authority_created": False}


def main() -> int:
    parser = argparse.ArgumentParser(description="Moonshot Sentinel scanner, triage, adjudication and research-rule evolution")
    sub = parser.add_subparsers(dest="command", required=True)
    p_scan = sub.add_parser("scan-gecko"); p_scan.add_argument("--network", default="eth"); p_scan.add_argument("--pages", type=int, default=2); p_scan.add_argument("--output", type=Path, required=True)
    p_triage = sub.add_parser("triage"); p_triage.add_argument("--events", type=Path, required=True); p_triage.add_argument("--config", type=Path, required=True); p_triage.add_argument("--output", type=Path, required=True)
    p_assess = sub.add_parser("assess"); p_assess.add_argument("--candidate", type=Path, required=True); p_assess.add_argument("--research", type=Path, required=True); p_assess.add_argument("--output", type=Path, required=True); p_assess.add_argument("--model", default="gpt-5.6-luna"); p_assess.add_argument("--dry-run", action="store_true")
    p_alert = sub.add_parser("alert"); p_alert.add_argument("--triage", type=Path, required=True); p_alert.add_argument("--assessment", type=Path, required=True); p_alert.add_argument("--config", type=Path, required=True); p_alert.add_argument("--alerts-last-24h", type=int, default=0); p_alert.add_argument("--output", type=Path, required=True)
    p_prop = sub.add_parser("propose-challenger"); p_prop.add_argument("--champion", type=Path, required=True); p_prop.add_argument("--error-ledger", type=Path, required=True); p_prop.add_argument("--output", type=Path, required=True)
    p_promote = sub.add_parser("promotion-decision"); p_promote.add_argument("--champion", type=Path, required=True); p_promote.add_argument("--challenger", type=Path, required=True); p_promote.add_argument("--evaluation", type=Path, required=True); p_promote.add_argument("--contract", type=Path, required=True); p_promote.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "scan-gecko":
        payload = {"contract": "MOONSHOT_SCAN_BATCH_v1", "created_unix": int(time.time()), "events": add_birth_cohort_percentiles(fetch_gecko_new_pools(args.network, args.pages))}
    elif args.command == "triage":
        raw = json.loads(args.events.read_text()); events = raw.get("events", raw) if isinstance(raw, dict) else raw
        if not isinstance(events, list): raise SystemExit("events_must_be_list")
        config = load_object(args.config); ranked = [initial_triage(e, config) for e in events if isinstance(e, dict)]
        ranked.sort(key=lambda r: (0 if r["alert_state"] == "DEEP_DIVE" else 1, -_number((r["event"].get("birth_cohort_percentiles") or {}).get("buyer_velocity")), str(r["candidate_id"])))
        payload = {"contract": "MOONSHOT_TRIAGE_BATCH_v1", "candidates": ranked[: _int(config["scanner"].get("max_candidates_per_scan"), 5)]}
    elif args.command == "assess":
        payload = assess(load_object(args.candidate), load_object(args.research), model=args.model, dry_run=args.dry_run)
    elif args.command == "alert":
        triage = load_object(args.triage); payload = final_alert_decision(triage, load_object(args.assessment), load_object(args.config), alerts_last_24h=args.alerts_last_24h)
        event = triage.get("event") or {}; payload["market_cap_usd_at_alert"] = event.get("market_cap_usd"); payload["liquidity_usd_at_alert"] = event.get("liquidity_usd")
    elif args.command == "propose-challenger":
        payload = {"challengers": propose_challengers(load_object(args.champion), load_object(args.error_ledger))}
    else:
        evaluation = json.loads(args.evaluation.read_text())
        if not isinstance(evaluation, list): raise SystemExit("evaluation_must_be_list")
        payload = promotion_decision(load_object(args.champion), load_object(args.challenger), evaluation, load_object(args.contract))
    args.output.parent.mkdir(parents=True, exist_ok=True); args.output.write_bytes(canonical_bytes(payload)); print(json.dumps(payload, sort_keys=True)); return 0


if __name__ == "__main__":
    raise SystemExit(main())
