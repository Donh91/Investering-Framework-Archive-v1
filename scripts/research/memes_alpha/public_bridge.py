from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import build_public_manifest, stable_hash, validate_public_payload


def _sha256_text(value: object, field: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise ValueError(f"{field} must be a SHA-256 hex digest")
    return value.lower()


def convert_private_bridge(d: dict, raw: bytes) -> dict:
    required = {
        "seed_sha256",
        "private_manifest_sha256",
        "case_count",
        "event_counts",
        "chain_coverage",
        "health",
        "reason_codes",
    }
    missing = sorted(required - set(d))
    if missing:
        raise ValueError(f"private bridge manifest missing fields: {missing}")

    private_run_hash = _sha256_text(d["private_manifest_sha256"], "private_manifest_sha256")
    seed_hash = _sha256_text(d["seed_sha256"], "seed_sha256")
    public = build_public_manifest(
        private_manifest_hash=private_run_hash,
        seed_hash=seed_hash,
        case_count=d["case_count"],
        event_counts=d["event_counts"],
        chain_coverage=d["chain_coverage"],
        health=d["health"],
        reason_codes=d["reason_codes"],
        generated_at=d.get("generated_at"),
    )
    public["private_bridge_sha256"] = stable_hash(raw)
    if "observation_counts" in d:
        counts = d["observation_counts"]
        if not isinstance(counts, dict):
            raise ValueError("observation_counts must be an object")
        public["observation_counts"] = {str(k): int(v) for k, v in sorted(counts.items())}
    validate_public_payload(public)
    return public


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--private-manifest", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    src = Path(args.private_manifest)
    raw = src.read_bytes()
    d = json.loads(raw)
    try:
        public = convert_private_bridge(d, raw)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "output": str(out), "manifest_sha256": stable_hash(public)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
