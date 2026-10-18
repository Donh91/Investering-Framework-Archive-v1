#!/usr/bin/env python3
"""Reproduce Task2 original-MATURED 314-row development diagnostics offline.

Read the *actual* frozen Actions ZIP supplied by its existing owner, not a late
API re-fetch. Public output contains aggregate counts only. Never score CENSORED
or NO_ORIGINAL_RECEIPT as original MATURED; no trading/performance authority.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import random
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ORIGINAL_ZIP_SHA = "4bce43736374b8fcff7aa9ffd1fdac18c303d8b2264b8291bb6e0b80fcde23ae"
ORIGINAL_LEDGER_SHA = "616e70fd87a79acf126591c1f8e704c74da7a2bd3b3aa181838ac5f861fea5d9"
LEDGER_MEMBER = "TASK15_R0_FROZEN_FORECAST_TAPE_CENSOR_LEDGER.csv"
PUBLICATION_MEMBER = "TASK15_R1_OWNER_PUBLICATION_FULL_CENSUS.json"
PUBLICATION_SHA = "b30d8e515221314a217b5add128f0918f9eeaf6d99d2c682d142482a9f3d4776"
RESEARCH_ONLY = "EX_POST_DEVELOPMENT_ONLY_NOT_CERTIFIED_PROVIDER_PIT_OR_INVESTOR_ACTION"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_original(zip_path: Path) -> list[dict]:
    outer = zip_path.read_bytes()
    if sha256(outer) != ORIGINAL_ZIP_SHA:
        raise ValueError("ORIGINAL_ACTIONS_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(outer)) as archive:
        inner = archive.read(LEDGER_MEMBER)
    if sha256(inner) != ORIGINAL_LEDGER_SHA:
        raise ValueError("ORIGINAL_LEDGER_SHA_MISMATCH")
    rows = list(csv.DictReader(io.StringIO(inner.decode("utf-8-sig"))))
    if len(rows) != 1140 or len({r["prediction_id"] for r in rows}) != 1140:
        raise ValueError("ORIGINAL_FORECAST_DENOMINATOR_MISMATCH")
    return rows


def publication_metrics(cases: list[dict]) -> dict:
    """Classify original Git-first-archival delay, never vendor publication."""
    if len(cases) != 814 or len({x["prediction_id"] for x in cases}) != 814:
        raise ValueError("ORIGINAL_PUBLICATION_CENSUS_MISMATCH")
    counts = Counter(x["original_outcome_status"] for x in cases)
    if counts != {"MATURED": 314, "CENSORED": 500}:
        raise ValueError("PUBLICATION_OUTCOME_CLASS_DRIFT")
    if any(
        x["scorer_would_have_received_source"] != "UNVERIFIED_EXECUTION_CONTEXT"
        or (x["original_outcome_status"] == "MATURED") != (x["publication_minutes_from_due"] <= 90)
        or (x["original_outcome_status"] == "MATURED") != (x["archive_publication_class"] == "PRESENT_BY_90_MIN_CUTOFF")
        for x in cases
    ):
        raise ValueError("PUBLICATION_CLOCK_FALSE_EVIDENCE")
    def lower_median(group):
        delays = sorted(x["publication_minutes_from_due"] for x in group)
        return round(delays[(len(delays)-1)//2], 3)
    return {
        "cases":len(cases),"matured":counts["MATURED"],"censored":counts["CENSORED"],
        "matured_lower_median_minutes":lower_median([x for x in cases if x["original_outcome_status"]=="MATURED"]),
        "censored_lower_median_minutes":lower_median([x for x in cases if x["original_outcome_status"]=="CENSORED"]),
        "distinct_archived_commits":len({x["first_present_main_commit"] for x in cases}),
        "distinct_archived_source_paths":len({x["source_path"] for x in cases}),
        "scorer_visibility":"UNVERIFIED_EXECUTION_CONTEXT",
    }


def load_publication(zip_path: Path) -> dict:
    outer=zip_path.read_bytes()
    if sha256(outer)!=ORIGINAL_ZIP_SHA:
        raise ValueError("ORIGINAL_ACTIONS_ZIP_SHA_MISMATCH")
    with zipfile.ZipFile(io.BytesIO(outer)) as archive:
        data=archive.read(PUBLICATION_MEMBER)
    if sha256(data)!=PUBLICATION_SHA:
        raise ValueError("ORIGINAL_PUBLICATION_MEMBER_SHA_MISMATCH")
    document=json.loads(data)
    if (document["input_ledger_sha256"]!=ORIGINAL_LEDGER_SHA
            or document["coverage_mode"]!="FULL_RESEARCH_COHORT"):
        raise ValueError("PUBLICATION_NOT_BOUND_TO_ORIGINAL_LEDGER")
    return publication_metrics(document["cases"])


def paired(rows: list[dict]) -> list[dict]:
    return [r for r in rows if r["descriptive_hit"] in {"True", "False"}
            and r["baseline_hit"] in {"True", "False"}]


def stats(rows: list[dict]) -> dict:
    n = len(rows)
    c = sum(r["descriptive_hit"] == "True" for r in rows)
    p = sum(r["baseline_hit"] == "True" for r in rows)
    return {
        "n": n, "compass_hits": c, "price_hits": p,
        "disagree": sum(r["direction"] != r["baseline_direction"] for r in rows),
        "compass_only": sum(r["descriptive_hit"] == "True" and r["baseline_hit"] == "False" for r in rows),
        "price_only": sum(r["descriptive_hit"] == "False" and r["baseline_hit"] == "True" for r in rows),
        "lift_pp": round(100 * (c - p) / n, 4) if n else None,
    }


def cluster_interval(rows: list[dict], field: str, replicates: int = 8000) -> tuple[int, float, float]:
    groups = defaultdict(list)
    for r in rows:
        groups[r["issue_utc"] if field == "clock" else r["issue_utc"][:10]].append(r)
    keys = sorted(groups)
    rng = random.Random(3142026)
    results = []
    for _ in range(replicates):
        sample = [groups[keys[rng.randrange(len(keys))]] for _ in keys]
        numerator = sum((r["descriptive_hit"] == "True") - (r["baseline_hit"] == "True") for g in sample for r in g)
        denominator = sum(len(g) for g in sample)
        results.append(100 * numerator / denominator)
    results.sort()
    return len(keys), round(results[int(0.025*replicates)], 3), round(results[int(0.975*replicates)-1], 3)


def analyze(rows: list[dict]) -> dict:
    matched = paired(rows)
    mature = [r for r in matched if r["original_outcome_status"] == "MATURED"]
    if len(matched) != 824 or len(mature) != 314:
        raise ValueError("MATURED_VS_RETROSPECTIVE_COHORT_MISMATCH")
    if Counter(r["original_outcome_status"] for r in matched) != {
        "MATURED": 314, "CENSORED": 500, "NO_ORIGINAL_RECEIPT": 10
    }:
        raise ValueError("MISSING_OR_CENSORED_DENOMINATOR_DRIFT")
    if Counter(r["original_outcome_status"] for r in rows) != {
        "MATURED": 358, "CENSORED": 570, "NO_ORIGINAL_RECEIPT": 212
    }:
        raise ValueError("COMPLETE_ORIGINAL_STATUS_CENSUS_DRIFT")
    abstained = [r for r in rows if r["original_outcome_status"] == "MATURED" and r not in mature]
    if len(abstained) != 44 or any(r["direction"] != "NO_EDGE" or r["original_outcome_result"] != "ABSTAINED" for r in abstained):
        raise ValueError("ABSTENTION_WAS_DROPPED_OR_REWRITTEN")
    for r in mature:
        if (r["original_outcome_result"] not in {"HIT","MISS"}
                or (r["original_outcome_result"] == "HIT") != (r["descriptive_hit"] == "True")):
            raise ValueError("ORIGINAL_OUTCOME_TAPE_MISMATCH")
    whole = stats(mature)
    if [whole[k] for k in ("compass_hits","price_hits","disagree","compass_only","price_only")] != [145,142,111,57,54]:
        raise ValueError("824_PARENT_REPLAY_INVARIANT_BROKEN")
    cells = [dict(asset=a, horizon=h, **stats([r for r in mature if r["asset"] == a and r["horizon"] == h]))
             for a in ("BTC", "ETH") for h in ("1H","4H","24H")]
    return {
        "status": RESEARCH_ONLY, "original_total": len(rows), "original_matured_status": 358,
        "original_matured_paired": len(mature), "original_matured_abstained": len(abstained),
        "original_censored_paired_excluded": 500, "original_no_receipt_paired_excluded": 10,
        "paired": whole, "by_asset_horizon": cells,
        "issue_clock_cluster_interval": cluster_interval(mature, "clock"),
        "issue_date_cluster_interval": cluster_interval(mature, "date"),
        "dependent_market_event_families_certified": 0,
        "source_reconstruction_class": "ORIGINAL_ACTIONS_LEDGER_WITH_LATER_PRICE_PAIRING_EXPOST",
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", required=True, type=Path)
    ap.add_argument("--published-receipt", type=Path)
    args = ap.parse_args()
    found = analyze(load_original(args.artifact))
    found["original_archival_publication"] = load_publication(args.artifact)
    if args.published_receipt:
        receipt = json.loads(args.published_receipt.read_text())
        assert receipt["status"] == RESEARCH_ONLY
        for r in found["by_asset_horizon"]:
            expected = next(c for c in receipt["by_asset_horizon"] if c["asset"] == r["asset"] and c["horizon"] == r["horizon"])
            for key in ("n", "compass_hits","price_hits","disagree","compass_only","price_only","lift_pp"):
                if r[key] != expected[key]:
                    raise ValueError("PUBLISHED_RECEIPT_MISMATCH:"+r["asset"]+":"+r["horizon"]+":"+key)
        pub = receipt["original_archive_publication_clock"]
        observed = found["original_archival_publication"]
        for got, want in (
            ("cases",pub["all_original_publication_cases"]),
            ("matured",pub["first_archived_by_90min_cutoff"]),
            ("censored",pub["first_archived_after_90min_cutoff"]),
            ("matured_lower_median_minutes",pub["original_matured_314_minutes_from_due"]["median_lower"]),
            ("censored_lower_median_minutes",pub["original_censored_500_minutes_from_due"]["median_lower"]),
            ("distinct_archived_commits",pub["distinct_archived_commits"]),
            ("distinct_archived_source_paths",pub["distinct_archived_source_paths"]),
        ):
            if observed[got] != want:
                raise ValueError("PUBLISHED_ARCHIVAL_DELAY_MISMATCH:"+got)
        assert found["issue_clock_cluster_interval"] == (
            receipt["exploratory_cluster_bootstrap"]["by_exact_issue_utc"]["clusters"],
            receipt["exploratory_cluster_bootstrap"]["by_exact_issue_utc"]["lower_pp"],
            receipt["exploratory_cluster_bootstrap"]["by_exact_issue_utc"]["upper_pp"]
        )
        assert found["issue_date_cluster_interval"] == (
            receipt["exploratory_cluster_bootstrap"]["by_utc_issue_date"]["clusters"],
            receipt["exploratory_cluster_bootstrap"]["by_utc_issue_date"]["lower_pp"],
            receipt["exploratory_cluster_bootstrap"]["by_utc_issue_date"]["upper_pp"]
        )
    print(json.dumps(found, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
