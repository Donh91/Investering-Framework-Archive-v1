from __future__ import annotations

import argparse
import collections
import hashlib
import itertools
import json
import zipfile
from pathlib import Path

from red_earliest_first_buy_reconstruction_v1 import h, member_by_basename, rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        intra = list(rows(zf, member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")))

    by_pair = collections.defaultdict(dict)
    for row in intra:
        wallets = sorted({str(x) for x in row.get("wallets") or []})
        sigs = [str(x) for x in row.get("tx_sigs") or []]
        if not (3 <= len(wallets) <= 4 and len(wallets) == len(sigs)):
            continue
        mint = str(row.get("mint", ""))
        for pair in itertools.combinations(wallets, 2):
            by_pair[pair][mint] = row

    candidates = []
    for pair, by_mint in by_pair.items():
        n = len(by_mint)
        if 4 <= n <= 6:
            candidates.append({
                "pair_identity_sha256": h("|".join(pair)),
                "distinct_launches": n,
                "first_buy_occurrences_launch3_plus": (n - 2) * 2,
                "prediction_launches_launch4_plus": n - 3,
            })
    candidates.sort(key=lambda x: x["pair_identity_sha256"])

    manifest_text = "\n".join(f"{x['pair_identity_sha256']}:{x['distinct_launches']}" for x in candidates)
    distribution = collections.Counter(x["distinct_launches"] for x in candidates)
    prefix = {}
    for n in (2, 5, 10, 25, 50, 100):
        selected = candidates[:n]
        prefix[str(n)] = {
            "pairs": len(selected),
            "first_buy_occurrences_launch3_plus": sum(x["first_buy_occurrences_launch3_plus"] for x in selected),
            "prediction_launches_launch4_plus": sum(x["prediction_launches_launch4_plus"] for x in selected),
        }

    result = {
        "experiment": "RED_RECURRING_PAIR_SCALE_CENSUS_v1",
        "source": "RED-COHORT-2026-v1.1.1",
        "selection_rule": "all unordered wallet pairs from rows with 3-4 wallets and equal wallet/signature counts, retaining pairs observed on 4-6 distinct mints; order ascending by sha256(walletA|walletB)",
        "counts": {
            "intra_rows": len(intra),
            "candidate_pairs": len(candidates),
            "launch_count_distribution": {str(k): v for k, v in sorted(distribution.items())},
            "all_candidate_first_buy_occurrences_launch3_plus": sum(x["first_buy_occurrences_launch3_plus"] for x in candidates),
            "all_candidate_prediction_launches_launch4_plus": sum(x["prediction_launches_launch4_plus"] for x in candidates),
        },
        "ordered_manifest_sha256": hashlib.sha256(manifest_text.encode("utf-8")).hexdigest(),
        "prefix_compute_census": prefix,
        "first_50_pair_hashes": [x["pair_identity_sha256"] for x in candidates[:50]],
        "first_50_launch_counts": [x["distinct_launches"] for x in candidates[:50]],
        "invariants": {
            "raw_identifiers_logged": False,
            "qualification_launch_ordinal": 3,
            "first_prediction_eligible_launch_ordinal": 4,
            "selection_does_not_use_outcomes": True,
        },
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "portfolio_execution": False,
            "buy_now_promotion": False,
            "live_threshold_change": False,
        },
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
