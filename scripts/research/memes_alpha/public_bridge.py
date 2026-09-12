from __future__ import annotations

import argparse
import json
from pathlib import Path

from core import build_public_manifest, stable_hash, validate_public_payload


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--private-manifest", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()

    src = Path(args.private_manifest)
    raw = src.read_bytes()
    d = json.loads(raw)
    required = {"seed_sha256", "case_count", "event_counts", "chain_coverage", "health", "reason_codes"}
    missing = sorted(required - set(d))
    if missing:
        raise SystemExit(f"private bridge manifest missing fields: {missing}")

    public = build_public_manifest(
        private_manifest_hash=stable_hash(raw),
        seed_hash=d["seed_sha256"],
        case_count=d["case_count"],
        event_counts=d["event_counts"],
        chain_coverage=d["chain_coverage"],
        health=d["health"],
        reason_codes=d["reason_codes"],
        generated_at=d.get("generated_at"),
    )
    validate_public_payload(public)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(public, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"status": "PASS", "output": str(out), "manifest_sha256": stable_hash(public)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
