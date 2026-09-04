#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from compounding_learning_engine import build_state
from compounding_learning_utils import enrich_registry_with_candidate_specs, parse_utc, read_json, write_json

UTC = timezone.utc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--candidate-root", type=Path, required=True)
    ap.add_argument("--registry", type=Path, required=True)
    ap.add_argument("--admission-registry", type=Path, required=True)
    ap.add_argument("--adjudication", type=Path, required=True)
    ap.add_argument("--monthly-learning", type=Path, required=True)
    ap.add_argument("--policy", type=Path, required=True)
    ap.add_argument("--previous-state", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--next-best-output", type=Path, required=True)
    ap.add_argument("--as-of-utc")
    args = ap.parse_args()
    registry = enrich_registry_with_candidate_specs(read_json(args.registry, {}), args.candidate_root)
    state, nxt, changed = build_state(
        registry,
        read_json(args.admission_registry, {}),
        read_json(args.adjudication, {}),
        read_json(args.monthly_learning, {}),
        read_json(args.policy, {}),
        read_json(args.previous_state, {}),
        parse_utc(args.as_of_utc) if args.as_of_utc else datetime.now(UTC),
    )
    if changed or not args.output.exists():
        write_json(args.output, state)
        write_json(args.next_best_output, nxt)
    print(json.dumps({
        "status": state.get("status"), "changed": changed,
        "new_checkpoint_candidate_count": state.get("new_checkpoint_candidate_count", 0),
        "primary_action": state.get("primary_action"), "target": state.get("target"),
        "authority": state.get("authority"),
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
