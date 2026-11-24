#!/usr/bin/env python3
"""Validate, freeze and ingest causally bound prospective shared rows."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import core_shared_row_materializer as core
from ethbtc_persistence_replay_v1 import verify_window_inputs

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
PROVENANCE_MUTABLE_FIELDS = {
    "outcome_24h", "outcome_72h", "outcome_7d",
    "mae_24h", "mfe_24h", "mae_72h", "mfe_72h", "mae_7d", "mfe_7d",
}
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


def frozen_provenance_hash(row: dict[str, Any], *, fields=None) -> str:
    """Hash the exact immutable projection as it is persisted in the CSV ledger."""
    if fields is None:
        with LEDGER.open(newline="", encoding="utf-8-sig") as handle:
            fields = next(csv.reader(handle))
    projection = {
        key: "" if row.get(key) is None else str(row.get(key, ""))
        for key in fields
        if key != "provenance_hash" and key not in PROVENANCE_MUTABLE_FIELDS
    }
    return hashlib.sha256(canon(projection).encode("utf-8")).hexdigest()


def verify_frozen_provenance(row: dict[str, Any]) -> None:
    declared = str(row.get("provenance_hash") or "")
    if not declared or declared != frozen_provenance_hash(row):
        raise ValueError("frozen row provenance hash mismatch")


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
    family_id: str, family: dict[str, Any], source_commit: str, *, read_blob=None
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
        payload = (read_blob or _git_blob)(source_commit, path)
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


def verify_source_bindings(row: dict[str, Any], cutoff: datetime, *, context=None) -> dict[str, Any]:
    raw = row.get("source_binding_manifest")
    manifest = raw if isinstance(raw, dict) else json.loads(str(raw))
    if manifest.get("contract") != core.SOURCE_BINDING_CONTRACT:
        raise ValueError("source binding manifest contract mismatch")
    if row.get("source_binding_manifest_sha256") != core.sha_json(manifest):
        raise ValueError("source binding manifest hash mismatch")
    source_commit = str(row.get("source_version_commit") or "")
    if not source_commit or manifest.get("source_commit") != source_commit:
        raise ValueError("source binding commit mismatch")
    if context is None:
        _require_ancestor(source_commit)
    else:
        context.require_ancestor(source_commit)
    families = manifest.get("families")
    if not isinstance(families, dict) or set(families) != CORE_FAMILIES:
        raise ValueError("source binding core family set mismatch")
    boundary = _activation_boundary() if context is None else context.boundary
    reader = None if context is None else context.read_blob
    for family_id, family in families.items():
        for key in ["capture_min_utc", "capture_max_utc"]:
            value = parse_ts(family.get(key))
            if value > cutoff:
                raise ValueError(f"{family_id} source timestamp after information cutoff")
            if value < boundary:
                raise ValueError(f"{family_id} source timestamp before post-repair boundary")

    eth_family = families["ETHBTC_PERSISTENCE"]
    eth_payloads = _bound_payloads("ETHBTC_PERSISTENCE", eth_family, source_commit, read_blob=reader)
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
    expected_eth_state = "ABOVE" if baseline["ethbtc"] > 0.03 else "BELOW" if baseline["ethbtc"] < 0.03 else "AT"
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
        or row.get("ethbtc_derived_state") != expected_eth_state
    ):
        raise ValueError("ETHBTC row fields do not reconcile to bound source")

    breadth_family = families["BREADTH_SURVIVAL"]
    breadth_payloads = _bound_payloads("BREADTH_SURVIVAL", breadth_family, source_commit, read_blob=reader)
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
    btcd_payloads = _bound_payloads("BTCD_PATH_RECLAIM", btcd_family, source_commit, read_blob=reader)
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
    # Replay precisely the issuance-time source age guard, so even a
    # correctly hashed but late-submitted/stale row cannot reach any consumer.
    core.require_fresh_sources(
        cutoff,
        ethbtc_hour=baseline["ts"],
        breadth_capture=retrieval,
        btcd_verified=max(btcd_verified),
        btcd_last_settled_print=core.parse_ts(btcd_rows[-1]["source_timestamp_utc"]),
    )
    return {"manifest": manifest, "ethbtc_window": window, "baseline": expected_baseline}


def verify_persistence_source_bindings(row: dict[str, Any], cutoff: datetime, *, context=None) -> dict[str, Any]:
    """Strict opt-in extension of the original source verifier.

    The existing C01-C07 admission semantics remain unchanged until the
    historical cohort has been replayed and reviewed. New persistence-aware
    consumers must call this function, not trust the row's duration field.
    """
    verified = (verify_source_bindings(row, cutoff) if context is None else
                verify_source_bindings(row, cutoff, context=context))

    def unique_object(pairs):
        obj = {}
        for key, value in pairs:
            if key in obj:
                raise ValueError("ETHBTC_PERSISTENCE_DUPLICATE_KEY")
            obj[key] = value
        return obj

    raw = row.get("ethbtc_window_inputs")
    if not isinstance(raw, str):
        raise ValueError("ETHBTC_PERSISTENCE_INPUT_INVALID")
    inputs = json.loads(raw, object_pairs_hook=unique_object)
    if not isinstance(inputs, dict):
        raise ValueError("ETHBTC_PERSISTENCE_INPUT_INVALID")
    return {**verified, "persistence_replay": verify_window_inputs(
        verified["ethbtc_window"], cutoff, inputs)}


def _strict_object(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("PINNED_JSON_DUPLICATE_KEY")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError("PINNED_JSON_NONFINITE")

    result = json.loads(raw, object_pairs_hook=unique, parse_constant=reject_constant)
    if not isinstance(result, dict):
        raise ValueError("PINNED_JSON_OBJECT_REQUIRED")
    return result


class PinnedSourceReplay:
    """Read evidence at a fixed Git commit using current verifier code, no checkout.

    No historical code execution, writes, global rebinding, outcome access or
    independent first-known claim. Source commits must precede the producer
    checkout in Git ancestry, not merely be present at current HEAD.
    """
    BASE = "06_RESEARCH_LAB/shared_row_model_tournament_v1"

    def __init__(self, repo: Path, checkout: str):
        self.repo = Path(repo).resolve()
        self.checkout = self._sha(checkout)
        self._git("merge-base", "--is-ancestor", self.checkout, "HEAD")
        self.ledger_raw = self.read_blob(self.checkout, self.BASE + "/data/PROSPECTIVE_SHARED_ROW_LEDGER.csv")
        reader = csv.DictReader(io.StringIO(self.ledger_raw.decode("utf-8-sig"), newline=""), strict=True)
        self.fields = tuple(reader.fieldnames or ())
        if (not self.fields or len(set(self.fields)) != len(self.fields) or
                not {"event_id", "provenance_hash", "candidate_decisions",
                     "information_cutoff_utc", "source_binding_manifest"}.issubset(self.fields)):
            raise ValueError("PINNED_LEDGER_HEADER_INVALID")
        self.registry_raw = self.read_blob(self.checkout, self.BASE + "/TRANSFORM_FREEZE_REGISTRY.json")
        freeze = _strict_object(self.registry_raw)
        contract = _strict_object(self.read_blob(self.checkout, self.BASE + "/CORE_FAMILY_PROSPECTIVE_CONTRACT_v1.json"))
        registry = _strict_object(self.read_blob(self.checkout, self.BASE + "/03_CANDIDATE_REGISTRY.json"))
        rule = freeze["core_activation_rule"]
        family_list = freeze["families"]
        families = {item["family_id"]: item for item in family_list}
        candidates = registry["candidates"]
        ids = {item["id"] for item in candidates}
        if (len(families) != len(family_list) or len(ids) != len(candidates) or
                set(rule["candidates"]) != set(CORE_IDS) or set(rule["start_only_when"]) != CORE_FAMILIES or
                not set(CORE_IDS).issubset(ids) or
                rule.get("collection_state") != core.ACTIVE_COLLECTION_STATE or
                rule.get("containment_floor_sentinel") is not False or
                contract.get("prospective_eligibility_status") != "ACTIVE_POST_REPAIR_FLOOR" or
                not all(ready(families, family) for family in CORE_FAMILIES)):
            raise ValueError("PINNED_CORE_INACTIVE")
        self.floor = max(parse_ts(rule["prospective_eligibility_start"]),
                         *(parse_ts(families[k]["prospective_eligibility_start"]) for k in CORE_FAMILIES))
        if parse_ts(contract["prospective_eligibility_start"]) != self.floor:
            raise ValueError("PINNED_CORE_FLOOR_MISMATCH")
        self.boundary = parse_ts(contract["prospective_activation"]["post_repair_source_capture_not_before_utc"])
        if self.boundary >= self.floor:
            raise ValueError("PINNED_SOURCE_BOUNDARY_INVALID")

    @staticmethod
    def _sha(value):
        if not isinstance(value, str) or not re.fullmatch("[0-9a-f]{40}", value):
            raise ValueError("PINNED_COMMIT_INVALID")
        return value

    def _git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       stderr=subprocess.DEVNULL, timeout=30)

    def require_ancestor(self, commit):
        self._git("merge-base", "--is-ancestor", self._sha(commit), self.checkout)

    def read_blob(self, commit, path):
        return self._git("show", f"{self._sha(commit)}:{path}")

    def verify(self, row, cutoff, decisions):
        if (parse_ts(row["observation_timestamp_utc"]) != cutoff or
                parse_ts(row["information_cutoff_utc"]) != cutoff or cutoff < self.floor or
                row["event_id"] != "PSR_" + cutoff.strftime("%Y%m%dT%H%M%SZ") or
                row["row_integrity_contract"] != core.ROW_INTEGRITY_CONTRACT):
            raise ValueError("PINNED_ROW_IDENTITY_INVALID")
        if row.get("provenance_hash") != frozen_provenance_hash(row, fields=self.fields):
            raise ValueError("PINNED_ROW_PROVENANCE_INVALID")
        if _strict_object(row["candidate_decisions"]) != decisions:
            raise ValueError("PINNED_DECISION_MISMATCH")
        _strict_object(row["source_binding_manifest"])
        validate_core_decision_contract(row, decisions, set(CORE_IDS))
        return verify_persistence_source_bindings(row, cutoff, context=self)["persistence_replay"]


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
    validated["provenance_hash"] = frozen_provenance_hash(validated)
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


def audit_persistence_cohort(*, context=None) -> dict[str, Any]:
    """Read-only full post-floor replay, using the original source owner.

    No historical writes, outcome consumption, threshold tuning, or authority.
    Repeated observations of one observed crossing share an episode key.
    Left-censored runs never receive a fabricated start or episode identity.
    """
    from collections import Counter
    eligible = set(eligible_candidates()) if context is None else set(CORE_IDS)
    result = {
        "contract": "SHARED_ROW_PERSISTENCE_AUDIT_v1",
        "checkout_sha": None if context is None else context.checkout,
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "scientific_pit_eligible": False,
        "forecast_authority": False,
        "status": "UNKNOWN",
        "raw_row_n": 0, "post_floor_row_n": 0, "excluded_pre_floor_n": 0,
        "verified_n": 0, "rejected_n": 0, "left_censored_n": 0,
        "above_observation_n": 0, "observed_above_episode_n": 0,
        "rows": [], "reason": None,
    }
    if context is None:
        if not collection_active() or not set(CORE_IDS).issubset(eligible):
            return {**result, "reason": "CORE_COLLECTION_INACTIVE"}
        floors = [eligibility_floor_for_candidate(k) for k in CORE_IDS]
        if any(floor is None for floor in floors):
            return {**result, "reason": "CORE_FLOOR_UNAVAILABLE"}
        floor = max(floors)
        source_rows = rows(LEDGER)
    else:
        floor = context.floor
        reader = csv.DictReader(io.StringIO(context.ledger_raw.decode("utf-8-sig"), newline=""), strict=True)
        source_rows = list(reader)
        if any(None in row or any(value is None for value in row.values()) for row in source_rows):
            return {**result, "status": "REPLAY_BLOCKED", "reason": "PINNED_LEDGER_ROW_SHAPE_INVALID"}
    result["raw_row_n"] = len(source_rows)
    identities = Counter(r.get("event_id") for r in source_rows)
    episodes = set()
    for row in source_rows:
        event = row.get("event_id")
        item = {"event_id": event, "status": "REJECTED"}
        try:
            cutoff = parse_ts(row["information_cutoff_utc"])
            at = parse_ts(row["observation_timestamp_utc"])
            if cutoff != at:
                raise ValueError("ROW_CUTOFF_MISMATCH")
            if at < floor:
                result["excluded_pre_floor_n"] += 1
                continue
            result["post_floor_row_n"] += 1
            if (not event or identities[event] != 1 or
                    event != "PSR_" + at.strftime("%Y%m%dT%H%M%SZ") or
                    row.get("row_integrity_contract") != core.ROW_INTEGRITY_CONTRACT):
                raise ValueError("ROW_IDENTITY_INVALID")
            if context is None:
                verify_frozen_provenance(row)
                decisions = json.loads(row["candidate_decisions"])
                validate_core_decision_contract(row, decisions, eligible)
                replay = verify_persistence_source_bindings(row, cutoff)["persistence_replay"]
            else:
                decisions = _strict_object(row["candidate_decisions"])
                replay = context.verify(row, cutoff, decisions)
            item.update(status="VERIFIED", persistence=replay)
            result["verified_n"] += 1
            result["left_censored_n"] += int(replay["left_censored"])
            if replay["side"] == "ABOVE":
                result["above_observation_n"] += 1
                if replay["first_above_bar_utc"]:
                    episodes.add(replay["first_above_bar_utc"])
        except (ValueError, TypeError, KeyError, AttributeError, RuntimeError, OSError,
                OverflowError, subprocess.SubprocessError) as exc:
            item["reason"] = str(exc)
            result["rejected_n"] += 1
        result["rows"].append(item)
    result["observed_above_episode_n"] = len(episodes)
    result["status"] = ("REPLAY_COMPLETE" if result["verified_n"] and not result["rejected_n"]
                        else "REPLAY_BLOCKED")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ingest-row", type=Path)
    parser.add_argument("--status-only", action="store_true")
    parser.add_argument("--audit-persistence", action="store_true",
                        help="Read-only full original owner replay; no ledger write")
    args = parser.parse_args()
    if args.audit_persistence:
        if args.ingest_row or args.status_only:
            parser.error("--audit-persistence cannot be combined with other modes")
        head = subprocess.check_output(["git", "-C", str(REPO_ROOT), "rev-parse", "HEAD"],
                                       text=True, timeout=30).strip()
        report = audit_persistence_cohort(context=PinnedSourceReplay(REPO_ROOT, head))
        print(json.dumps(report, indent=2, sort_keys=True))
        if report["status"] != "REPLAY_COMPLETE":
            raise SystemExit(1)
        return
    print(json.dumps(ingest(args.ingest_row) if args.ingest_row else status(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
