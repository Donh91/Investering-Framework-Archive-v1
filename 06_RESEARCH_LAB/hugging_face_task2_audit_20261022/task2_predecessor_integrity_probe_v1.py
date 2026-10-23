#!/usr/bin/env python3
"""Research-only reproduction of the existing predecessor-reader integrity gap.

Runs exact pinned source functions against real immutable temporary Git trees,
using the pinned real GitCliSnapshot implementation. No mocked hash/path reader,
provider data, historical modification, source fix, scoring or market action.
An expected vulnerable observation is NOT a passing production security guard.
"""
from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import types
from typing import Any

PRODUCER = "scripts/data_ping/auto_market_state.py"
INTEGRITY = "scripts/data_ping/truth_integrity.py"
PRODUCER_BLOB = "6196286539bd3e3688dc3bbcf322b15112b9ef5c"
INTEGRITY_BLOB = "d089da1f2d4bb423fa0cdb4fc3187882a1e43e98"
ROOT = "04_MARKET_LEARNING/entry_signals/auto_market_state"
POINTER = ROOT + "/LATEST.json"
TARGET = ROOT + "/runs/2026/10/01/120000_synthetic.json"
OTHER = ROOT + "/runs/2026/10/01/130000_synthetic.json"


def blob(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def source(repo: Path, commit: str, path: str) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("IMMUTABLE_SOURCE_SHA_REQUIRED")
    return subprocess.check_output(
        ["git", "--no-replace-objects", "show", f"{commit}:{path}"], cwd=repo
    )


def load_frozen(repo: Path, commit: str):
    producer = source(repo, commit, PRODUCER)
    if blob(producer) != PRODUCER_BLOB:
        raise ValueError("PRODUCER_VERSION_CHANGED_REASSESS_PROBE")
    integrity = source(repo, commit, INTEGRITY)
    if blob(integrity) != INTEGRITY_BLOB:
        raise ValueError("INTEGRITY_HELPER_VERSION_CHANGED_REASSESS_PROBE")
    name = "task2_pinned_truth_integrity_probe"
    module = types.ModuleType(name)
    sys.modules[name] = module  # dataclass resolves its actual module namespace.
    exec(compile(integrity, INTEGRITY, "exec"), module.__dict__)
    wanted = {"read_json", "prior_packet", "canon", "h", "num", "delta"}
    tree = ast.parse(producer)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    if {n.name for n in nodes} != wanted:
        raise ValueError("PINNED_SOURCE_FUNCTION_SET_MISSING")
    namespace = {"Any": Any, "hashlib": hashlib, "json": json, "math": math}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), PRODUCER, "exec"), namespace)
    return namespace, module, {
        "source_commit": commit, "producer_path": PRODUCER,
        "producer_git_blob_sha1": blob(producer), "integrity_path": INTEGRITY,
        "integrity_git_blob_sha1": blob(integrity),
        "functions_executed": sorted(wanted),
        "full_assemble_or_native_forecast_executed": False,
    }


def run(repo: Path, commit: str) -> dict:
    ns, integrity, binding = load_frozen(repo, commit)
    canon, digest = ns["canon"], ns["h"]

    def packet(value):
        result = {"contract": "AUTO_MARKET_STATE_PACKET_v1",
                  "packet_generated_at_utc": "2026-10-01T12:00:00Z",
                  "normalized_state": {"live_market": {"btc_usdt": value}}}
        result["packet_sha256"] = digest(canon(result))
        return result

    original = packet(99)
    alternate = packet(101)
    pointer = {"contract": "AUTO_MARKET_STATE_LATEST_POINTER_v1",
               "packet_path": TARGET, "packet_sha256": original["packet_sha256"]}
    scenarios = [
        ("valid_binding", "POSITIVE_CONTROL", "AVAILABLE", None),
        ("wrong_pointer_hash", "INTEGRITY_VIOLATION", "AVAILABLE", "pointer_hash"),
        ("payload_tamper_with_unchanged_self_hash", "INTEGRITY_VIOLATION", "AVAILABLE", "payload"),
        ("different_valid_target_same_pointer_hash", "INTEGRITY_VIOLATION", "AVAILABLE", "path"),
        ("wrong_packet_contract", "INTEGRITY_VIOLATION", "AVAILABLE", "contract"),
        ("missing_target", "EXISTING_FAILCLOSED_CONTROL", "UNAVAILABLE", "missing"),
        ("path_traversal", "EXISTING_FAILCLOSED_CONTROL", "UNAVAILABLE", "traversal"),
        ("absent_pointer", "EXISTING_FIRST_PACKET_CONTROL", "NOT_AVAILABLE_FIRST_PACKET", "no_pointer"),
    ]
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
               GIT_AUTHOR_NAME="Synthetic Task2 Fixture", GIT_AUTHOR_EMAIL="fixture@example.invalid",
               GIT_COMMITTER_NAME="Synthetic Task2 Fixture", GIT_COMMITTER_EMAIL="fixture@example.invalid",
               GIT_AUTHOR_DATE="2026-10-01T12:00:00Z", GIT_COMMITTER_DATE="2026-10-01T12:00:00Z")
    rows = []
    for name, kind, expected_status, mutation in scenarios:
        p, target = copy.deepcopy(pointer), copy.deepcopy(original)
        if mutation == "pointer_hash": p["packet_sha256"] = "0" * 64
        if mutation == "payload": target["normalized_state"]["live_market"]["btc_usdt"] = 101
        if mutation == "path": p["packet_path"] = OTHER
        if mutation == "contract":
            target["contract"] = "WRONG_CONTRACT"
            target["packet_sha256"] = digest(canon({
                k: v for k, v in target.items() if k != "packet_sha256"
            }))
            p["packet_sha256"] = target["packet_sha256"]
        if mutation == "traversal": p["packet_path"] = "../outside.json"
        with tempfile.TemporaryDirectory(prefix="task2-predecessor-probe-") as tmp:
            work = Path(tmp)

            def git(*args):
                return subprocess.check_output(
                    ["git", "-c", "core.hooksPath=" + os.devnull, *args],
                    cwd=work, env=env, stderr=subprocess.DEVNULL,
                )

            git("init", "--quiet")
            files = {POINTER: p, TARGET: target, OTHER: alternate}
            if mutation == "missing": del files[TARGET]
            if mutation == "no_pointer": del files[POINTER]
            for path, value in files.items():
                full = work / path
                full.parent.mkdir(parents=True, exist_ok=True)
                full.write_bytes(canon(value))
            git("add", "--all")
            git("commit", "--quiet", "-m", "Synthetic predecessor probe only")
            snapshot = integrity.GitCliSnapshot.open_repo(work, ref="HEAD")
            assert snapshot.commit_sha == git("rev-parse", "HEAD").decode().strip()
            result, health = ns["prior_packet"](snapshot)
            assert health["status"] == expected_status, (name, health)
            accepted = result is not None
            self_hash_valid = None if result is None else result.get("packet_sha256") == digest(
                canon({k: v for k, v in result.items() if k != "packet_sha256"})
            )
            pointer_matches = None if result is None else result.get("packet_sha256") == p["packet_sha256"]
            delta = None if result is None else ns["delta"](
                100, result["normalized_state"]["live_market"]["btc_usdt"]
            )["pct"]
            sign = None if delta is None else "POSITIVE" if delta > 0 else "NEGATIVE" if delta < 0 else "ZERO"
            rows.append({
                "case": name, "case_class": kind, "observed_status": health["status"],
                "packet_accepted": accepted, "pointer_matches_declared_packet_hash": pointer_matches,
                "packet_canonical_self_hash_valid": self_hash_valid,
                "synthetic_delta_sign_only": sign,
                "violation_accepted": kind == "INTEGRITY_VIOLATION" and accepted,
                "temporary_snapshot_pinned": snapshot.consistency()["all_reads_pinned_to_snapshot"],
            })
    assert rows[0]["synthetic_delta_sign_only"] == "POSITIVE"
    assert rows[2]["synthetic_delta_sign_only"] == rows[3]["synthetic_delta_sign_only"] == "NEGATIVE"
    assert sum(row["violation_accepted"] for row in rows) == 4
    return {
        "contract": "TASK2_PREDECESSOR_INTEGRITY_REPRODUCTION_v1",
        "status": "EXISTING_GUARD_GAP_REPRODUCED_NOT_REPAIRED",
        "scope": "PINNED_PRIOR_PACKET_FUNCTION_REAL_GIT_SNAPSHOT_SYNTHETIC_DATA_ONLY",
        "source_binding": binding, "cases": rows,
        "cases_executed": len(rows), "integrity_violations_accepted": 4,
        "provider_data_read": False, "historical_forecasts_modified": False,
        "production_code_modified": False, "scientific_pit_admission": False,
        "trade_or_signal_emitted": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo-root", type=Path, required=True)
    ap.add_argument("--source-commit", required=True)
    args = ap.parse_args()
    print(json.dumps(run(args.repo_root, args.source_commit), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
