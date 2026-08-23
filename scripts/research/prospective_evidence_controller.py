#!/usr/bin/env python3
"""Validate, freeze and ingest causally bound prospective shared rows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import core_shared_row_materializer as core

REPO_ROOT = Path(".")
ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")
LEDGER = ROOT / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv"
FNP = ROOT / "14_DIVERGENCE_FNP_LEDGER.csv"
FREEZE = ROOT / "TRANSFORM_FREEZE_REGISTRY.json"
CONTRACT = ROOT / "CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"
REG = ROOT / "03_CANDIDATE_REGISTRY.json"
CORE_IDS = (
    "C01_ETHBTC",
    "C02_BREADTH",
    "C03_BTCD",
    "C04_ETHBTC_BREADTH",
    "C05_ETHBTC_BTCD",
    "C06_BREADTH_BTCD",
    "C07_SIMPLE_3",
)
CORE_FAMILIES = {"ETHBTC_PERSISTENCE", "BREADTH_SURVIVAL", "BTCD_PATH_RECLAIM"}
EXPECTED_BINDINGS = {
    "ETHBTC_PERSISTENCE": (
        "HOURLY_SEQUENCE_CAPTURE_v2_2_DIRECT_BINANCE_SPOT",
        "Binance spot",
        "ETHBTC_0_0300_PERSISTENCE_PROSPECTIVE_v1",
    ),
    "BREADTH_SURVIVAL": (
        "C5E_TOP100_BREADTH_OWNER_v1_2",
        "CoinGecko market-cap markets endpoint",
        "BREADTH_MAJORITY_SURVIVAL_PROSPECTIVE_v1",
    ),
    "BTCD_PATH_RECLAIM": (
        "CMC_DIRECT_SOURCE_CONVENTION",
        "CoinMarketCap",
        "BTCD_CMC_THREE_PRINT_PATH_PROSPECTIVE_v1",
    ),
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_ts(value: Any) -> datetime:
    return core.parse_ts(str(value))


def canon(value: Any) -> str:
    return core.canon(value)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def append(path: Path, row: dict[str, Any]) -> None:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        fields = next(csv.reader(handle))
    with path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writerow({key: row.get(key, "") for key in fields})


def _collection_rule() -> tuple[dict[str, Any], dict[str, Any]]:
    return load_json(FREEZE), load_json(CONTRACT)


def collection_active() -> bool:
    freeze, contract = _collection_rule()
    rule = freeze.get("core_activation_rule", {})
    return bool(
        rule.get("collection_state") == core.ACTIVE_COLLECTION_STATE
        and rule.get("containment_floor_sentinel") is False
        and contract.get("prospective_eligibility_status") == "ACTIVE_POST_REPAIR_FLOOR"
    )


def ready(families: dict[str, dict[str, Any]], family_id: str) -> bool:
    item = families.get(family_id, {})
    return bool(
        item.get("status") == "READY"
        and item.get("candidate_decision_contract_status") == "READY"
        and item.get("repair_state") == "P0_REPAIRED_AWAITING_ACTIVATION_OR_ACTIVE"
    )


def candidate_families(candidate: dict[str, Any], freeze: dict[str, Any]) -> list[str]:
    candidate_id = candidate["id"]
    core_ids = set(freeze.get("core_activation_rule", {}).get("candidates", []))
    if candidate_id in core_ids:
        return list(freeze["core_activation_rule"].get("start_only_when", []))
    families = candidate.get("families")
    return families if isinstance(families, list) else []


def eligible_candidates() -> list[str]:
    if not collection_active():
        return []
    freeze = load_json(FREEZE)
    families = {item["family_id"]: item for item in freeze["families"]}
    registry = load_json(REG)["candidates"]
    rule = freeze.get("core_activation_rule", {})
    core_ids = set(rule.get("candidates", []))
    core_families = rule.get("start_only_when", [])
    core_ready = bool(core_families) and all(ready(families, family) for family in core_families)
    output = []
    for candidate in registry:
        candidate_id = candidate["id"]
        if candidate_id in core_ids:
            if core_ready:
                output.append(candidate_id)
            continue
        family_ids = candidate.get("families")
        if family_ids is None or isinstance(family_ids, str):
            continue
        if all(ready(families, family) for family in family_ids):
            output.append(candidate_id)
    return output


def eligibility_floor_for_candidate(candidate_id: str) -> datetime | None:
    freeze = load_json(FREEZE)
    families = {item["family_id"]: item for item in freeze["families"]}
    registry = {item["id"]: item for item in load_json(REG)["candidates"]}
    candidate = registry[candidate_id]
    starts = []
    for family_id in candidate_families(candidate, freeze):
        value = families.get(family_id, {}).get("prospective_eligibility_start")
        if not value:
            return None
        starts.append(parse_ts(value))
    if candidate_id in set(freeze.get("core_activation_rule", {}).get("candidates", [])):
        value = freeze.get("core_activation_rule", {}).get("prospective_eligibility_start")
        if value:
            starts.append(parse_ts(value))
    return max(starts) if starts else None


def _git_blob(commit: str, path: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPO_ROOT), "show", f"{commit}:{path}"], stderr=subprocess.DEVNULL
        )
    except Exception as exc:
        raise ValueError(f"source binding commit/path unreachable: {commit}:{path}") from exc


def _require_ancestor(commit: str) -> None:
    result = subprocess.run(
        ["git", "-C", str(REPO_ROOT), "merge-base", "--is-ancestor", commit, "HEAD"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError("source binding commit is not a reachable ancestor of HEAD")


def _bound_payloads(
    family_id: str, family: dict[str, Any], source_commit: str
) -> list[tuple[str, bytes]]:
    expected_contract, expected_provider, expected_transform = EXPECTED_BINDINGS[family_id]
    if family.get("owner_contract") != expected_contract:
        raise ValueError(f"{family_id} owner contract mismatch")
    if family.get("provider") != expected_provider:
        raise ValueError(f"{family_id} provider mismatch")
    if family.get("transform_version") != expected_transform:
        raise ValueError(f"{family_id} transform version mismatch")
    bindings = family.get("path_bindings")
    if not isinstance(bindings, list) or not bindings:
        raise ValueError(f"{family_id} path bindings missing")
    payloads = []
    seen = set()
    for binding in bindings:
        path = str(binding.get("path") or "")
        if not path or path in seen or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError(f"{family_id} source binding path invalid or duplicate")
        if family_id == "ETHBTC_PERSISTENCE" and not (
            path.startswith("03_DAILY_CAPTURE_LOGS/hourly/") and path.endswith(".csv")
        ):
            raise ValueError("ETHBTC source binding path is outside the frozen hourly owner")
        if family_id == "BREADTH_SURVIVAL" and not (
            path.startswith("03_DAILY_CAPTURE_LOGS/breadth_rich/")
            and "/LATEST" not in path
            and Path(path).name in {"owner_snapshot.json", "receipt.json", "artifact_manifest.json", "raw_source_payload.json"}
        ):
            raise ValueError("breadth source binding path is not an immutable dated owner artifact")
        if family_id == "BTCD_PATH_RECLAIM" and path != "03_DAILY_CAPTURE_LOGS/btc_d_cmc/latest/BTC_D_DIRECT_SOURCE_DAILY_2023_CURRENT.csv":
            raise ValueError("BTC.D source binding path mismatch")
        seen.add(path)
        if (
            binding.get("source_commit") != source_commit
            or binding.get("owner_contract") != expected_contract
            or binding.get("provider") != expected_provider
        ):
            raise ValueError(f"{family_id} binding metadata mismatch")
        payload = _git_blob(source_commit, path)
        if binding.get("sha256") != core.sha_bytes(payload) or binding.get("bytes") != len(payload):
            raise ValueError(f"{family_id} source binding hash mismatch")
        payloads.append((path, payload))
    return payloads


def _activation_boundary() -> datetime:
    contract = load_json(CONTRACT)
    raw = (contract.get("prospective_activation") or {}).get("post_repair_source_capture_not_before_utc")
    if not raw:
        raise ValueError("post-repair source capture boundary missing")
    return parse_ts(raw)


def _window_digest(window: list[dict[str, Any]]) -> str:
    payload = [
        {
            "timestamp_utc": core.iso(item["ts"]),
            "source_window_end_utc": core.iso(item["available"]),
            "ethbtc_close": item["ethbtc"],
            "btc_close": item["btc"],
            "eth_close": item["eth"],
            "path": item["path"],
        }
        for item in window
    ]
    return core.sha_json(payload)


def verify_source_bindings(row: dict[str, Any], cutoff: datetime) -> dict[str, Any]:
    raw = row.get("source_binding_manifest")
    manifest = raw if isinstance(raw, dict) else json.loads(str(raw))
    if manifest.get("contract") != core.SOURCE_BINDING_CONTRACT:
        raise ValueError("source binding manifest contract mismatch")
    if row.get("source_binding_manifest_sha256") != core.sha_json(manifest):
        raise ValueError("source binding manifest hash mismatch")
    source_commit = str(row.get("source_version_commit") or "")
    if not source_commit or manifest.get("source_commit") != source_commit:
        raise ValueError("source binding commit mismatch")
    _require_ancestor(source_commit)
    families = manifest.get("families")
    if not isinstance(families, dict) or set(families) != CORE_FAMILIES:
        raise ValueError("source binding core family set mismatch")
    boundary = _activation_boundary()
    for family_id, family in families.items():
        for key in ["capture_min_utc", "capture_max_utc"]:
            value = parse_ts(family.get(key))
            if value > cutoff:
                raise ValueError(f"{family_id} source timestamp after information cutoff")
            if value < boundary:
                raise ValueError(f"{family_id} source timestamp before post-repair boundary")

    eth_family = families["ETHBTC_PERSISTENCE"]
    eth_payloads = _bound_payloads("ETHBTC_PERSISTENCE", eth_family, source_commit)
    window = core.select_ethbtc_window(core.parse_hourly_payloads(eth_payloads), cutoff)
    baseline = window[-1]
    digest = _window_digest(window)
    expected_baseline = {
        "timestamp_utc": core.iso(baseline["ts"]),
        "source_window_end_utc": core.iso(baseline["available"]),
        "ethbtc_close": baseline["ethbtc"],
        "btc_close": baseline["btc"],
        "eth_close": baseline["eth"],
    }
    if (
        eth_family.get("sample_count") != 168
        or eth_family.get("capture_min_utc") != core.iso(min(item["available"] for item in window))
        or eth_family.get("capture_max_utc") != core.iso(max(item["available"] for item in window))
        or eth_family.get("window_start_utc") != core.iso(window[0]["ts"])
        or eth_family.get("window_end_utc") != core.iso(window[-1]["ts"])
        or eth_family.get("window_rows_sha256") != digest
        or eth_family.get("baseline") != expected_baseline
    ):
        raise ValueError("ETHBTC bound window or baseline mismatch")
    window_inputs = json.loads(str(row.get("ethbtc_window_inputs") or "{}"))
    if (
        window_inputs.get("sample_count") != 168
        or window_inputs.get("continuous_hours") != 168
        or window_inputs.get("window_rows_sha256") != digest
        or float(row.get("ethbtc_raw_value")) != baseline["ethbtc"]
    ):
        raise ValueError("ETHBTC row fields do not reconcile to bound source")

    breadth_family = families["BREADTH_SURVIVAL"]
    breadth_payloads = _bound_payloads("BREADTH_SURVIVAL", breadth_family, source_commit)
    breadth_parents = {str(Path(path).parent) for path, _payload in breadth_payloads}
    if len(breadth_payloads) != 4 or len(breadth_parents) != 1:
        raise ValueError("breadth binding must contain one complete immutable dated bundle")
    breadth_bundle = {Path(path).name: payload for path, payload in breadth_payloads}
    owner, retrieval = core.validate_breadth_bundle(breadth_bundle, cutoff=cutoff, not_before=boundary)
    aggregate = owner["aggregate"]
    breadth_inputs = json.loads(str(row.get("breadth_raw_inputs") or "{}"))
    breadth_state = "BROAD_MAJORITY" if aggregate["advancers"] > aggregate["decliners"] else "NON_BROAD_MAJORITY"
    if (
        breadth_family.get("run_id") != owner.get("run_id")
        or breadth_family.get("capture_min_utc") != core.iso(retrieval)
        or breadth_family.get("capture_max_utc") != core.iso(retrieval)
        or breadth_family.get("membership_hash") != aggregate.get("membership_hash")
        or row.get("breadth_membership_hash") != aggregate.get("membership_hash")
        or row.get("breadth_membership_version") != owner.get("contract")
        or breadth_inputs.get("retrieved_at_utc") != core.iso(retrieval)
        or breadth_inputs.get("run_id") != owner.get("run_id")
        or breadth_inputs.get("advancers") != aggregate.get("advancers")
        or breadth_inputs.get("decliners") != aggregate.get("decliners")
        or row.get("breadth_derived_state") != breadth_state
    ):
        raise ValueError("breadth row fields do not reconcile to bound owner")

    btcd_family = families["BTCD_PATH_RECLAIM"]
    btcd_payloads = _bound_payloads("BTCD_PATH_RECLAIM", btcd_family, source_commit)
    if len(btcd_payloads) != 1:
        raise ValueError("BTC.D binding must contain exactly one frozen source file")
    btcd_rows, _ = core.parse_btcd_payload(btcd_payloads[0][1], cutoff=cutoff, not_before=boundary)
    btcd_verified = [parse_ts(item["verified_at_utc"]) for item in btcd_rows]
    if (
        btcd_family.get("settled_dates") != [item["date"] for item in btcd_rows]
        or btcd_family.get("capture_min_utc") != core.iso(min(btcd_verified))
        or btcd_family.get("capture_max_utc") != core.iso(max(btcd_verified))
    ):
        raise ValueError("BTC.D settled-date binding mismatch")
    if json.loads(str(row.get("btcd_raw_inputs") or "[]")) != btcd_rows:
        raise ValueError("BTC.D row inputs do not reconcile to bound source")
    a, b_value, c = [item["value"] for item in btcd_rows]
    state = "FALLING_PATH" if c < b_value < a else "RISING_RECLAIM" if b_value < a and c > b_value else "MIXED_PATH"
    if row.get("btcd_provider") != "CoinMarketCap" or row.get("btcd_derived_state") != state:
        raise ValueError("BTC.D row fields do not reconcile to bound source")
    return {"manifest": manifest, "ethbtc_window": window, "baseline": expected_baseline}


def validate_core_decision_contract(
    row: dict[str, Any], decisions: dict[str, Any], eligible: set[str]
) -> None:
    core_ids = set(CORE_IDS)
    if not core_ids.issubset(eligible):
        return
    missing = sorted(core_ids - set(decisions))
    if missing:
        raise ValueError("active core candidate set incomplete: " + ",".join(missing))
    for candidate_id in CORE_IDS:
        if not isinstance(decisions[candidate_id], bool):
            raise ValueError(f"core candidate {candidate_id} decision must be boolean")
    eth_state = str(row.get("ethbtc_derived_state", "")).strip()
    breadth_state = str(row.get("breadth_derived_state", "")).strip()
    btcd_state = str(row.get("btcd_derived_state", "")).strip()
    if eth_state not in {"ABOVE", "BELOW", "AT"}:
        raise ValueError("invalid or missing ethbtc_derived_state")
    if breadth_state not in {"BROAD_MAJORITY", "NON_BROAD_MAJORITY"}:
        raise ValueError("invalid or missing breadth_derived_state")
    if btcd_state not in {"FALLING_PATH", "RISING_RECLAIM", "MIXED_PATH"}:
        raise ValueError("invalid or missing btcd_derived_state")
    expected = {
        "C01_ETHBTC": eth_state == "ABOVE",
        "C02_BREADTH": breadth_state == "BROAD_MAJORITY",
        "C03_BTCD": btcd_state == "FALLING_PATH",
    }
    expected.update(
        {
            "C04_ETHBTC_BREADTH": expected["C01_ETHBTC"] and expected["C02_BREADTH"],
            "C05_ETHBTC_BTCD": expected["C01_ETHBTC"] and expected["C03_BTCD"],
            "C06_BREADTH_BTCD": expected["C02_BREADTH"] and expected["C03_BTCD"],
            "C07_SIMPLE_3": expected["C01_ETHBTC"] and expected["C02_BREADTH"] and expected["C03_BTCD"],
        }
    )
    wrong = sorted(candidate_id for candidate_id in CORE_IDS if decisions[candidate_id] is not expected[candidate_id])
    if wrong:
        raise ValueError("core candidate decision violates frozen boolean contract: " + ",".join(wrong))


def validate_payload(row: dict[str, Any]) -> tuple[dict[str, Any], dict[str, bool]]:
    if not collection_active():
        raise ValueError("P0 repair quarantine active")
    required = [
        "event_id",
        "observation_timestamp_utc",
        "information_cutoff_utc",
        "source_version_commit",
        "row_integrity_contract",
        "source_binding_manifest",
        "source_binding_manifest_sha256",
        "prospective_context_block",
        "regime_tag",
        "catalyst_tag",
        "catalyst_evidence_id",
        "candidate_decisions",
    ]
    missing = [key for key in required if not str(row.get(key, "")).strip()]
    if missing:
        raise ValueError("missing required fields: " + ",".join(missing))
    if row.get("row_integrity_contract") != core.ROW_INTEGRITY_CONTRACT:
        raise ValueError("row integrity contract mismatch")
    observation = parse_ts(row["observation_timestamp_utc"])
    cutoff = parse_ts(row["information_cutoff_utc"])
    if cutoff != observation:
        raise ValueError("shared row observation and information cutoff must be identical")
    decisions = row["candidate_decisions"] if isinstance(row["candidate_decisions"], dict) else json.loads(row["candidate_decisions"])
    eligible = set(eligible_candidates())
    illegal = sorted(set(decisions) - eligible)
    if illegal:
        raise ValueError("decision supplied for non-eligible candidate: " + ",".join(illegal))
    if not decisions:
        raise ValueError("no eligible candidate decisions supplied")
    validate_core_decision_contract(row, decisions, eligible)
    floors = []
    for candidate_id in decisions:
        floor = eligibility_floor_for_candidate(candidate_id)
        if floor is None:
            raise ValueError(f"candidate {candidate_id} lacks frozen prospective eligibility start")
        if observation < floor:
            raise ValueError(f"candidate {candidate_id} decision predates prospective eligibility start")
        floors.append(floor)
    active_floor = max(floors)
    expected_block = core.context_block(observation, active_floor)
    if row.get("prospective_context_block") != expected_block:
        raise ValueError("prospective context block mismatch")
    verify_source_bindings(row, cutoff)
    validated = dict(row)
    validated["candidate_decisions"] = canon(decisions)
    validated["source_binding_manifest"] = canon(
        row["source_binding_manifest"]
        if isinstance(row["source_binding_manifest"], dict)
        else json.loads(row["source_binding_manifest"])
    )
    for key, value in validated.items():
        if key.endswith("_missing") and str(value).lower() in {"true", "1", "yes"}:
            prefix = key[:-8]
            for raw_key, raw_value in validated.items():
                if raw_key.startswith(prefix) and raw_key != key and str(raw_value).strip() == "0":
                    raise ValueError(f"missing family {prefix} encoded as zero")
    forbidden = [
        key
        for key in [
            "outcome_24h",
            "outcome_72h",
            "outcome_7d",
            "mae_24h",
            "mfe_24h",
            "mae_72h",
            "mfe_72h",
            "mae_7d",
            "mfe_7d",
        ]
        if str(validated.get(key, "")).strip()
    ]
    if forbidden:
        raise ValueError("decision row contains premature outcome fields: " + ",".join(forbidden))
    validated["provenance_hash"] = hashlib.sha256(
        canon({key: value for key, value in validated.items() if key != "provenance_hash"}).encode("utf-8")
    ).hexdigest()
    return validated, decisions


def ingest(path: Path) -> dict[str, Any]:
    row, decisions = validate_payload(load_json(path))
    if any(existing["event_id"] == row["event_id"] for existing in rows(LEDGER)):
        raise ValueError("event_id already frozen")
    append(LEDGER, row)
    candidate_ids = sorted(decisions)
    existing_ids = {item["divergence_id"] for item in rows(FNP)}
    frozen = 0
    for index, candidate_a in enumerate(candidate_ids):
        for candidate_b in candidate_ids[index + 1 :]:
            if decisions[candidate_a] == decisions[candidate_b]:
                continue
            divergence_id = f"{row['event_id']}__{candidate_a}__vs__{candidate_b}"
            if divergence_id in existing_ids:
                continue
            divergence = {
                "divergence_id": divergence_id,
                "event_id": row["event_id"],
                "observation_timestamp_utc": row["observation_timestamp_utc"],
                "information_cutoff_utc": row["information_cutoff_utc"],
                "candidate_a": candidate_a,
                "candidate_b": candidate_b,
                "decision_a": decisions[candidate_a],
                "decision_b": decisions[candidate_b],
                "divergence_frozen_utc": now(),
                "catalyst_tag": row["catalyst_tag"],
                "regime_tag": row["regime_tag"],
                "provenance_hash": hashlib.sha256((row["provenance_hash"] + divergence_id).encode("utf-8")).hexdigest(),
            }
            append(FNP, divergence)
            frozen += 1
    return {
        "status": "PASS",
        "event_id": row["event_id"],
        "eligible_candidates": candidate_ids,
        "divergences_frozen": frozen,
        "provenance_hash": row["provenance_hash"],
    }


def status() -> dict[str, Any]:
    candidates = eligible_candidates()
    shared_rows = rows(LEDGER)
    divergences = rows(FNP)
    floors = {
        candidate_id: (
            eligibility_floor_for_candidate(candidate_id).isoformat().replace("+00:00", "Z")
            if eligibility_floor_for_candidate(candidate_id)
            else None
        )
        for candidate_id in candidates
    }
    active = collection_active()
    return {
        "status": "PASS",
        "collection_state": "ACTIVE" if active else "QUARANTINED_P0_REPAIR",
        "eligible_candidates": candidates,
        "candidate_eligibility_floors": floors,
        "eligible_row_n": sum(item.get("row_integrity_contract") == core.ROW_INTEGRITY_CONTRACT for item in shared_rows),
        "excluded_pre_repair_row_n": sum(item.get("row_integrity_contract") != core.ROW_INTEGRITY_CONTRACT for item in shared_rows),
        "divergence_n": len(divergences),
        "ingestion_ready": active and bool(candidates),
        "note": "Market transforms remain outside this controller.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-row", type=Path)
    parser.add_argument("--status-only", action="store_true")
    args = parser.parse_args()
    print(json.dumps(ingest(args.ingest_row) if args.ingest_row else status(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
