#!/usr/bin/env python3
"""Immutable quarantine manifest of AUTO_MARKET_STATE packets whose altseason health said PASS while the
BlockchainCenter 90d context was not PASS (K01, 2026-11-19). Packets are never rewritten; learning consumers
use this manifest to exclude or stratify them. The defect class was closed by #2239/#2244 (2026-11-19)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

CONTRACT = "ALTSEASON_FALSE_PASS_QUARANTINE_MANIFEST_v1"
RUNS = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/runs")
DEFAULT_OUT = Path("04_MARKET_LEARNING/entry_signals/auto_market_state/quarantine/ALTSEASON_FALSE_PASS_QUARANTINE_v1.json")
COVERAGE_END_UTC = "2026-11-19T09:21:25Z"   # last affected packet; #2239 merged 2026-11-19T09:29:32Z


def is_false_pass(packet: Mapping[str, Any]) -> bool:
    health = ((packet.get("source_health") or {}).get("altseason_context") or {})
    if health.get("status") != "PASS":
        return False
    bc = ((packet.get("normalized_state") or {}).get("altseason_context") or {}).get("blockchaincenter_altcoin_season")
    if not isinstance(bc, Mapping) or bc.get("status") != "PASS":
        return True
    score = ((bc.get("horizons") or {}).get("90") or {}).get("published_score")
    return isinstance(score, bool) or type(score) not in (int, float)


def build(root: Path, coverage_end_utc: str = COVERAGE_END_UTC) -> dict[str, Any]:
    rows = []
    for path in sorted((root / RUNS).glob("*/*/*/*.json")):
        raw = path.read_bytes()
        packet = json.loads(raw)
        generated = str(packet.get("packet_generated_at_utc") or "")
        if not generated or generated > coverage_end_utc or not is_false_pass(packet):
            continue
        bc = ((packet.get("normalized_state") or {}).get("altseason_context") or {}).get("blockchaincenter_altcoin_season")
        rows.append({
            "path": path.relative_to(root).as_posix(),
            "file_sha256": hashlib.sha256(raw).hexdigest(),
            "packet_sha256": packet.get("packet_sha256"),
            "packet_generated_at_utc": generated,
            "bc_status": bc.get("status") if isinstance(bc, Mapping) else None,
            "bc_failure_state": bc.get("failure_state") if isinstance(bc, Mapping) else "BC_CONTEXT_ABSENT",
        })
    return {
        "contract": CONTRACT,
        "rule": "source_health.altseason_context.status == PASS and the BlockchainCenter 90d context is not PASS with a numeric published_score",
        "coverage_end_utc": coverage_end_utc,
        "count": len(rows),
        "packets": rows,
        "consumer_guidance": "Exclude these packets from altseason-dependent learning, or stratify by membership; never edit them.",
        "authority": {"rewrites_packets": False, "changes_official_compass": False, "research_only": True},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    a = ap.parse_args()
    root = Path(a.root)
    manifest = build(root)
    out = root / a.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"contract": CONTRACT, "count": manifest["count"], "out": a.out}))


if __name__ == "__main__":
    main()
