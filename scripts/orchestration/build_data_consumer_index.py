from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# This file is invoked both as a module and directly from the production workflow.
# Direct script execution puts scripts/orchestration on sys.path, not the repo root.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scripts.orchestration.build_framework_handoff_manifest import load

CONTRACT = "DATA_CONSUMER_INDEX_v1"


def build_index(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = load(manifest_path)
    if not manifest or manifest.get("contract") != "FRAMEWORK_HANDOFF_MANIFEST_v2":
        raise ValueError("HANDOFF_MANIFEST_UNAVAILABLE_OR_INVALID")
    evidence = manifest.get("evidence") if isinstance(manifest.get("evidence"), dict) else {}
    consumers = manifest.get("consumers") if isinstance(manifest.get("consumers"), dict) else {}
    reverse: dict[str, list[str]] = {name: [] for name in evidence}
    for consumer, names in consumers.items():
        if not isinstance(names, list):
            continue
        for name in names:
            if name in reverse:
                reverse[name].append(str(consumer))
    rows = []
    for name in sorted(evidence):
        ref = evidence[name] if isinstance(evidence[name], dict) else {}
        path = root / str(ref.get("path") or "")
        current = path.is_file()
        observed_sha256 = None
        if current:
            try:
                observed_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
            except OSError:
                pass
        declared_sha256 = ref.get("sha256")
        if not current:
            binding_state = "MISSING"
        elif observed_sha256 is None:
            binding_state = "UNREADABLE"
        elif not isinstance(declared_sha256, str) or not (
            len(declared_sha256) == 64 and all(c in "0123456789abcdef" for c in declared_sha256)
        ):
            binding_state = "INVALID_DECLARED_DIGEST"
        elif observed_sha256 != declared_sha256:
            binding_state = "DIGEST_MISMATCH"
        else:
            binding_state = "MATCH"
        consumer_names = sorted(set(reverse[name]))
        rows.append({
            "artifact": name,
            "path": ref.get("path"),
            "producer_state": "PRESENT" if current else "MISSING",
            "consumer_count": len(consumer_names),
            "consumers": consumer_names,
            # Registered routes alone do not prove that runtime consumption occurred.
            "use_state": "REGISTERED_CONSUMER" if consumer_names else "NO_REGISTERED_CONSUMER",
            "freshness_use_state": "CURRENT_BINDING" if binding_state == "MATCH" else "STALE_OR_MISSING_POINTER",
            "binding_state": binding_state,
            "sha256": declared_sha256,
            "observed_sha256": observed_sha256,
        })
    return {
        "contract": CONTRACT,
        "generated_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_manifest_path": str(manifest_path.relative_to(root)),
        "source_manifest_generated_at_utc": manifest.get("generated_at_utc"),
        "source_manifest_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "rows": rows,
        "summary": {
            "artifact_count": len(rows),
            "no_registered_consumer": sum(r["use_state"] == "NO_REGISTERED_CONSUMER" for r in rows),
            "stale_or_missing_pointer": sum(r["freshness_use_state"] == "STALE_OR_MISSING_POINTER" for r in rows),
        },
        "authority": {
            "automatic_suppression": False,
            "canonical_promotion": False,
            "model_weight_change": False,
            "portfolio_action": False,
        },
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    ap.add_argument("--manifest", type=Path, default=Path("research/framework_handoffs/LATEST_FRAMEWORK_HANDOFF_MANIFEST.json"))
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.repo_root.resolve()
    manifest = args.manifest if args.manifest.is_absolute() else root / args.manifest
    result = build_index(root, manifest)
    output = args.output if args.output.is_absolute() else root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))


if __name__ == "__main__":
    main()
