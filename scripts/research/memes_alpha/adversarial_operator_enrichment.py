from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from scripts.api_agent.meme_alpha_blockscout import address_of, blockscout_get, normalize_address
from scripts.research.memes_alpha.adversarial_operator_counting import count_manifest, parameter_map

ENRICHMENT_CONTRACT = "ADVERSARIAL_OPERATOR_QUALIFICATION_ENRICHMENT_v1"
MANIFEST_CONTRACT = "ADVERSARIAL_OPERATOR_COUNTING_MANIFEST_v1"
PRE_T0_WINDOW_SECONDS = 3600
UNKNOWN_HUB_TX_COUNT = 10_000
MAX_HISTORY_PAGES = 6
MAX_BLOCK_PAGES = 6
MAX_COHORT_RECIPIENTS = 32

OUTCOME_KEY_FRAGMENTS = (
    "price", "market_cap", "mcap", "fdv", "ath", "return", "pnl", "mfe", "mae",
    "profit", "outcome", "future", "peak",
)

INFRA_NAME_CLASSES = (
    ("relay", "RELAY"),
    ("bridge", "BRIDGE"),
    ("router", "ROUTER"),
    ("exchange", "CEX"),
    ("binance", "CEX"),
    ("coinbase", "CEX"),
    ("kraken", "CEX"),
    ("factory", "PONS_FACTORY"),
    ("ponsv2launch", "PONS_FACTORY"),
    ("feeescrow", "PROTOCOL"),
    ("entrypoint", "PROTOCOL"),
    ("settlement", "SETTLEMENT"),
    ("depository", "SETTLEMENT"),
    ("solver", "SETTLEMENT"),
)

Fetch = Callable[..., tuple[Any, dict[str, Any]]]


def parse_iso(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        return None


def tx_timestamp(row: dict[str, Any]) -> datetime | None:
    return parse_iso(row.get("timestamp"))


def _outcome_key_present(value: Any, *, path: str = "") -> str | None:
    if isinstance(value, dict):
        for key, child in value.items():
            key_l = str(key).lower()
            if any(fragment in key_l for fragment in OUTCOME_KEY_FRAGMENTS):
                return f"{path}.{key}" if path else str(key)
            found = _outcome_key_present(child, path=f"{path}.{key}" if path else str(key))
            if found:
                return found
    elif isinstance(value, list):
        for idx, child in enumerate(value):
            found = _outcome_key_present(child, path=f"{path}[{idx}]")
            if found:
                return found
    return None


def assert_outcome_blind_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("contract") != MANIFEST_CONTRACT:
        raise ValueError("WRONG_MANIFEST_CONTRACT")
    for idx, event in enumerate(manifest.get("events") or []):
        found = _outcome_key_present(event)
        if found:
            raise ValueError(f"OUTCOME_FIELD_FORBIDDEN:event[{idx}].{found}")


def raw_and_third_party_exemptions(tx: dict[str, Any], deployer: str | None) -> dict[str, Any]:
    params = parameter_map(tx.get("decoded_input"))
    raw = params.get("snipeTaxExemptions")
    recipient = normalize_address(params.get("recipient"))
    tx_from = address_of(tx.get("from"))
    if not isinstance(raw, list):
        return {"state": "UNKNOWN", "raw": [], "third_party": [], "recipient": recipient, "tx_from": tx_from}
    raw_norm = []
    for value in raw:
        addr = normalize_address(value)
        if addr and addr not in raw_norm:
            raw_norm.append(addr)
    excluded = {v for v in (deployer, recipient, tx_from) if v}
    third_party = [addr for addr in raw_norm if addr not in excluded]
    return {"state": "PASS", "raw": raw_norm, "third_party": third_party, "recipient": recipient, "tx_from": tx_from}


def _next_page(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get("next_page_params")
    return value if isinstance(value, dict) and value else None


def _items(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        return []
    return [row for row in payload["items"] if isinstance(row, dict)]


def fetch_address_window(address: str, *, t0: datetime, fetch: Fetch = blockscout_get, max_pages: int = MAX_HISTORY_PAGES) -> dict[str, Any]:
    start = t0 - timedelta(seconds=PRE_T0_WINDOW_SECONDS)
    endpoint = f"/api/v2/addresses/{address}/transactions"
    query: dict[str, Any] = {}
    kept: list[dict[str, Any]] = []
    pages = 0
    source_health: list[dict[str, Any]] = []
    reached_before_window = False
    exhausted = False
    saw_post_t0 = False

    while pages < max_pages:
        payload, health = fetch(endpoint, query=query or None)
        source_health.append(health)
        pages += 1
        for row in _items(payload):
            ts = tx_timestamp(row)
            if ts is None:
                continue
            if ts > t0:
                saw_post_t0 = True
                continue
            if ts < start:
                reached_before_window = True
                continue
            kept.append(row)
        next_params = _next_page(payload)
        if not next_params:
            exhausted = True
            break
        if reached_before_window:
            break
        query = next_params

    complete = exhausted or reached_before_window
    kept.sort(key=lambda row: tx_timestamp(row) or datetime.min.replace(tzinfo=timezone.utc))
    return {
        "rows": kept,
        "complete": complete,
        "pages": pages,
        "history_state": "COMPLETE" if complete else "HISTORY_TRUNCATED",
        "post_t0_rows_discarded": saw_post_t0,
        "window_start_utc": start.isoformat().replace("+00:00", "Z"),
        "source_health": source_health,
    }


def _positive_native_inbound(row: dict[str, Any], address: str) -> bool:
    if address_of(row.get("to")) != address:
        return False
    try:
        return int(str(row.get("value") or "0")) > 0
    except (TypeError, ValueError):
        return False


def prep_evidence(history: dict[str, Any], *, address: str, pair_token: str | None) -> dict[str, Any]:
    evidence: list[dict[str, Any]] = []
    for row in history["rows"]:
        method = str(row.get("method") or "").lower()
        to = address_of(row.get("to"))
        if _positive_native_inbound(row, address):
            evidence.append({"kind": "NATIVE_INBOUND", "hash": row.get("hash"), "timestamp": row.get("timestamp")})
        if method == "approve" and (pair_token is None or to == pair_token):
            evidence.append({"kind": "PAIR_APPROVAL", "hash": row.get("hash"), "timestamp": row.get("timestamp")})
        if "swap" in method:
            evidence.append({"kind": "SWAP", "hash": row.get("hash"), "timestamp": row.get("timestamp")})
    if evidence:
        state: bool | None = True
    elif history["complete"]:
        state = False
    else:
        state = None
    return {"observed": state, "evidence": evidence}


def first_native_funder(history: dict[str, Any], *, address: str) -> str | None:
    inbound = [row for row in history["rows"] if _positive_native_inbound(row, address)]
    if not inbound:
        return None
    inbound.sort(key=lambda row: tx_timestamp(row) or datetime.max.replace(tzinfo=timezone.utc))
    return address_of(inbound[0].get("from"))


def _metadata_names(payload: dict[str, Any]) -> list[str]:
    info = payload.get("basic_info") if isinstance(payload.get("basic_info"), dict) else payload
    names: list[str] = []
    for key in ("name", "ens_domain_name"):
        value = info.get(key) if isinstance(info, dict) else None
        if isinstance(value, str) and value.strip():
            names.append(value.strip())
    metadata = info.get("metadata") if isinstance(info, dict) else None
    if isinstance(metadata, dict):
        for row in metadata.get("tags") or []:
            if isinstance(row, dict) and isinstance(row.get("name"), str):
                names.append(row["name"])
    for row in (info.get("public_tags") or []) if isinstance(info, dict) else []:
        if isinstance(row, dict) and isinstance(row.get("name"), str):
            names.append(row["name"])
        elif isinstance(row, str):
            names.append(row)
    return names


def _int_or_none(value: Any) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def classify_address(address: str, *, fetch: Fetch = blockscout_get) -> dict[str, Any]:
    info, info_health = fetch(f"/api/v2/addresses/{address}")
    counters, counters_health = fetch(f"/api/v2/addresses/{address}/counters")
    base = info.get("basic_info") if isinstance(info, dict) and isinstance(info.get("basic_info"), dict) else info
    is_contract = bool(base.get("is_contract")) if isinstance(base, dict) else False
    names = _metadata_names(info if isinstance(info, dict) else {})
    text = " ".join(names).lower()
    for needle, klass in INFRA_NAME_CLASSES:
        if needle in text:
            return {
                "class": klass,
                "is_contract": is_contract,
                "names": names,
                "transactions_count": _int_or_none(counters.get("transactions_count") if isinstance(counters, dict) else None),
                "source_health": [info_health, counters_health],
            }
    tx_count = _int_or_none(counters.get("transactions_count") if isinstance(counters, dict) else None)
    if not is_contract and tx_count is not None and tx_count >= UNKNOWN_HUB_TX_COUNT:
        klass = "UNKNOWN_HUB"
    elif is_contract:
        klass = "UNKNOWN_INFRA"
    else:
        klass = "NON_BENIGN"
    return {"class": klass, "is_contract": is_contract, "names": names, "transactions_count": tx_count, "source_health": [info_health, counters_health]}


def fetch_block_transactions(block_number: int, *, fetch: Fetch = blockscout_get, max_pages: int = MAX_BLOCK_PAGES) -> dict[str, Any]:
    endpoint = f"/api/v2/blocks/{block_number}/transactions"
    query: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    pages = 0
    health_rows: list[dict[str, Any]] = []
    exhausted = False
    while pages < max_pages:
        payload, health = fetch(endpoint, query=query or None)
        health_rows.append(health)
        pages += 1
        rows.extend(_items(payload))
        next_params = _next_page(payload)
        if not next_params:
            exhausted = True
            break
        query = next_params
    return {"rows": rows, "complete": exhausted, "pages": pages, "source_health": health_rows}


def token_recipients_from_blocks(token_ca: str, block_number: int, *, deployer: str | None, fetch: Fetch = blockscout_get) -> dict[str, Any]:
    candidates: list[str] = []
    health: list[dict[str, Any]] = []
    complete = True
    for block in (block_number, block_number + 1):
        payload = fetch_block_transactions(block, fetch=fetch)
        health.extend(payload["source_health"])
        complete = complete and payload["complete"]
        for tx in payload["rows"]:
            transfers = tx.get("token_transfers")
            if not isinstance(transfers, list):
                continue
            for transfer in transfers:
                if not isinstance(transfer, dict):
                    continue
                token = transfer.get("token") if isinstance(transfer.get("token"), dict) else {}
                token_addr = normalize_address(token.get("address_hash") or token.get("address"))
                if token_addr != token_ca:
                    continue
                recipient = address_of(transfer.get("to"))
                if not recipient or recipient == "0x0000000000000000000000000000000000000000" or recipient == deployer:
                    continue
                if recipient not in candidates:
                    candidates.append(recipient)
    if len(candidates) > MAX_COHORT_RECIPIENTS:
        return {"state": None, "recipients": candidates[:MAX_COHORT_RECIPIENTS], "complete": False, "reason": "COHORT_RECIPIENT_LIMIT", "source_health": health}
    eoa_recipients: list[str] = []
    for address in candidates:
        info, info_health = fetch(f"/api/v2/addresses/{address}")
        health.append(info_health)
        base = info.get("basic_info") if isinstance(info, dict) and isinstance(info.get("basic_info"), dict) else info
        if isinstance(base, dict) and base.get("is_contract") is False:
            eoa_recipients.append(address)
    if complete:
        state: bool | None = len(eoa_recipients) >= 2
    else:
        state = True if len(eoa_recipients) >= 2 else None
    return {"state": state, "recipients": eoa_recipients, "complete": complete, "reason": None, "source_health": health}


def common_funding_for_participants(participants: list[str], *, t0: datetime, fetch: Fetch = blockscout_get) -> dict[str, Any]:
    unique = []
    for address in participants:
        if address and address not in unique:
            unique.append(address)
    if len(unique) < 2:
        return {"common_funding": False, "common_funder": None, "common_funder_class": None, "histories_complete": True, "participant_funders": {}}

    participant_funders: dict[str, str | None] = {}
    complete = True
    histories: dict[str, Any] = {}
    for address in unique:
        history = fetch_address_window(address, t0=t0, fetch=fetch)
        histories[address] = {"complete": history["complete"], "history_state": history["history_state"], "pages": history["pages"]}
        complete = complete and history["complete"]
        participant_funders[address] = first_native_funder(history, address=address)

    counts = Counter(v for v in participant_funders.values() if v)
    shared = [address for address, n in counts.items() if n >= 2]
    if shared:
        shared.sort(key=lambda address: (-counts[address], address))
        funder = shared[0]
        funder_info = classify_address(funder, fetch=fetch)
        return {
            "common_funding": True,
            "common_funder": funder,
            "common_funder_class": funder_info["class"],
            "common_funder_evidence_count": counts[funder],
            "histories_complete": complete,
            "participant_funders": participant_funders,
            "participant_history_state": histories,
            "funder_info": funder_info,
        }
    return {
        "common_funding": False if complete else None,
        "common_funder": None,
        "common_funder_class": None,
        "histories_complete": complete,
        "participant_funders": participant_funders,
        "participant_history_state": histories,
    }


def reproduced_seed_addresses(registry: dict[str, Any]) -> set[str]:
    output: set[str] = set()
    for entity in registry.get("entities") or []:
        if not isinstance(entity, dict) or entity.get("state") != "PARTIALLY_REPRODUCED":
            continue
        for key in ("receiving_contract", "contract", "key"):
            addr = normalize_address(entity.get(key))
            if addr:
                output.add(addr)
        for key in ("keys", "addresses"):
            for value in entity.get(key) or []:
                addr = normalize_address(value)
                if addr:
                    output.add(addr)
    return output


def enrich_event(event: dict[str, Any], *, seed_addresses: set[str], fetch: Fetch = blockscout_get) -> dict[str, Any]:
    output = dict(event)
    token_ca = normalize_address(event.get("token_address") or event.get("token_ca"))
    deployer = normalize_address(event.get("deployer_address") or event.get("deployer"))
    tx_hash = event.get("tx_hash") or event.get("transaction_hash")
    t0 = parse_iso(event.get("block_timestamp_utc") or event.get("launch_t0") or event.get("timestamp"))
    block_number = _int_or_none(event.get("block_number"))
    unknown: list[str] = []
    source_health: list[dict[str, Any]] = []

    if not token_ca or not deployer or not isinstance(tx_hash, str) or t0 is None or block_number is None:
        output.update({
            "qualification_enrichment_state": "INVALID_IDENTITY",
            "pre_t0_prep_observed": None,
            "privileged_bundle_evidence": None,
            "common_funding": None,
            "synchronized_inventory": None,
            "residual_similarity": None,
            "direct_operator_lineage": None,
            "benign_infra_excluded": None,
            "unknown_fields": ["IDENTITY_OR_T0_INCOMPLETE"],
        })
        return output

    try:
        tx, tx_health = fetch(f"/api/v2/transactions/{tx_hash}")
        source_health.append(tx_health)
        if not isinstance(tx, dict):
            raise RuntimeError("LAUNCH_TX_PAYLOAD_INVALID")
        exemptions = raw_and_third_party_exemptions(tx, deployer)
        if exemptions["state"] != "PASS":
            unknown.append("PRIVILEGED_SURFACE_UNKNOWN")
        output["decoded_input"] = tx.get("decoded_input")
        output["raw_snipe_tax_exemptions"] = exemptions["raw"]
        output["third_party_snipe_tax_exemptions"] = exemptions["third_party"]
        output["privileged_exemptions_n"] = len(exemptions["third_party"]) if exemptions["state"] == "PASS" else None
        output["privileged_bundle_evidence"] = bool(exemptions["third_party"]) if exemptions["state"] == "PASS" else None
        output["entry_method"] = tx.get("method")
        output["tx_to"] = address_of(tx.get("to"))

        deployer_history = fetch_address_window(deployer, t0=t0, fetch=fetch)
        source_health.extend(deployer_history["source_health"])
        pair_token = normalize_address(event.get("pair_token_address")) or normalize_address(parameter_map(tx.get("decoded_input")).get("pairToken"))
        prep = prep_evidence(deployer_history, address=deployer, pair_token=pair_token)
        output["pre_t0_prep_observed"] = prep["observed"]
        output["pre_t0_prep_evidence"] = prep["evidence"]
        output["deployer_history_state"] = deployer_history["history_state"]
        output["post_t0_rows_discarded"] = deployer_history["post_t0_rows_discarded"]
        if prep["observed"] is None:
            unknown.append("PRE_T0_PREP_UNKNOWN")

        inventory = token_recipients_from_blocks(token_ca, block_number, deployer=deployer, fetch=fetch)
        source_health.extend(inventory["source_health"])
        output["synchronized_inventory"] = inventory["state"]
        output["t0_t0plus1_eoa_recipients"] = inventory["recipients"]
        output["inventory_window_complete"] = inventory["complete"]
        if inventory["state"] is None:
            unknown.append("SYNCHRONIZED_INVENTORY_UNKNOWN")

        participants = [deployer] + exemptions["third_party"] + inventory["recipients"]
        funding = common_funding_for_participants(participants, t0=t0, fetch=fetch)
        output["common_funding"] = funding["common_funding"]
        output["common_funder_address"] = funding["common_funder"]
        output["common_funder_class"] = funding["common_funder_class"]
        output["participant_funders"] = funding["participant_funders"]
        output["participant_history_state"] = funding.get("participant_history_state", {})
        if funding["common_funding"] is None:
            unknown.append("COMMON_FUNDING_UNKNOWN")
        if funding["common_funder_class"] == "UNKNOWN_HUB":
            unknown.append("COMMON_FUNDER_UNKNOWN_HUB")

        lineage_candidates = {deployer}
        lineage_candidates.update(a for a in exemptions["third_party"] if a)
        lineage_candidates.update(a for a in inventory["recipients"] if a)
        if funding["common_funder"]:
            lineage_candidates.add(funding["common_funder"])
        output["direct_operator_lineage"] = bool(lineage_candidates & seed_addresses)

        klass = funding["common_funder_class"]
        if klass in {"RELAY", "ROUTER", "BRIDGE", "CEX", "PONS_FACTORY", "PROTOCOL", "SETTLEMENT"}:
            output["benign_infra_excluded"] = False
        elif klass == "NON_BENIGN" or output["direct_operator_lineage"]:
            output["benign_infra_excluded"] = True
        else:
            output["benign_infra_excluded"] = None

        output["residual_similarity"] = None
        unknown.append("RESIDUAL_SIMILARITY_UNKNOWN")
        output["as_of_block_max"] = block_number + 1
        output["qualification_enrichment_state"] = "PASS_WITH_UNKNOWNS" if unknown else "PASS"
    except Exception as exc:
        output.update({
            "qualification_enrichment_state": "SOURCE_ERROR",
            "pre_t0_prep_observed": output.get("pre_t0_prep_observed"),
            "privileged_bundle_evidence": output.get("privileged_bundle_evidence"),
            "common_funding": output.get("common_funding"),
            "synchronized_inventory": output.get("synchronized_inventory"),
            "residual_similarity": None,
            "direct_operator_lineage": output.get("direct_operator_lineage"),
            "benign_infra_excluded": output.get("benign_infra_excluded"),
        })
        unknown.append(f"SOURCE_ERROR:{type(exc).__name__}")

    output["unknown_fields"] = sorted(set(unknown))
    output["enrichment_source_health"] = source_health
    return output


def enrich_manifest(manifest: dict[str, Any], *, seed_registry: dict[str, Any], fetch: Fetch = blockscout_get) -> dict[str, Any]:
    assert_outcome_blind_manifest(manifest)
    seeds = reproduced_seed_addresses(seed_registry)
    events = [enrich_event(event, seed_addresses=seeds, fetch=fetch) for event in manifest.get("events") or [] if isinstance(event, dict)]
    result = dict(manifest)
    result["events"] = events
    result["qualification_enrichment"] = {
        "contract": ENRICHMENT_CONTRACT,
        "status": "SHADOW_ONLY",
        "pre_t0_window_seconds": PRE_T0_WINDOW_SECONDS,
        "unknown_hub_transactions_threshold": UNKNOWN_HUB_TX_COUNT,
        "max_history_pages": MAX_HISTORY_PAGES,
        "max_block_pages": MAX_BLOCK_PAGES,
        "max_cohort_recipients": MAX_COHORT_RECIPIENTS,
        "outcome_fields_permitted": False,
        "launch_inventory_max_block_offset": 1,
        "self_exemption_filter": ["deployer", "recipient", "tx_from"],
        "direct_lineage_seed_count": len(seeds),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Outcome-blind adversarial qualification enrichment.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--seed-registry", type=Path, required=True)
    parser.add_argument("--enriched-output", type=Path, required=True)
    parser.add_argument("--counting-output", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    registry = json.loads(args.seed_registry.read_text(encoding="utf-8"))
    enriched = enrich_manifest(manifest, seed_registry=registry)
    count = count_manifest(enriched)

    args.enriched_output.parent.mkdir(parents=True, exist_ok=True)
    args.counting_output.parent.mkdir(parents=True, exist_ok=True)
    args.enriched_output.write_text(json.dumps(enriched, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.counting_output.write_text(json.dumps(count, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "contract": ENRICHMENT_CONTRACT,
        "launch_rows": len(enriched.get("events") or []),
        "stage1_gate": count["gates"]["stage1"],
        "stage2_gate": count["gates"]["stage2"],
        "qualification_unknown_rows": count["counts"]["qualification_unknown_rows"],
        "status": "PASS" if count["gates"]["stage1"] not in {"INCOMPLETE_SOURCE_EVIDENCE", "INCOMPLETE_UNKNOWN_INFRA"} else "INCOMPLETE",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
