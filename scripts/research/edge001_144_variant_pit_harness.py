#!/usr/bin/env python3
"""EDGE-001 research-only PIT sensitivity manifest and guarded descriptive replay.

No market API, model call, outcome join, trade, threshold optimization or auto-promotion.
"""
import argparse
import csv
import hashlib
import itertools
import json
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

CONTRACT = "EDGE001_PIT_SENSITIVITY_144_v1"
RANK = {"NORMAL": 0, "BUILDING": 1, "ELEVATED": 2, "HIGH": 3, "CONFIRMED": 4}
FIELDS = {"asset", "timestamp_utc", "knowledge_time_utc", "pullback_risk_state",
          "source_status", "continuity_segment_id"}
ALLOWED_STATUS = {"PASS", "OK"}


def variants():
    rows = []
    for state, persistence, delay, cooldown in itertools.product(
        ("ELEVATED", "HIGH", "CONFIRMED"), (1, 2, 3, 6), (0, 1, 3), (0, 6, 24, 72)
    ):
        key = f"{state}-P{persistence}-D{delay}-C{cooldown}"
        rows.append({"id": key, "minimum_state": state,
                     "persistence_hours": persistence, "delay_hours": delay,
                     "cooldown_hours": cooldown})
    assert len(rows) == len({v["id"] for v in rows}) == 144
    return rows


def parse_time(value):
    if not value or not value.endswith("Z"):
        raise ValueError("timestamps must be explicit UTC Z")
    t = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if t.utcoffset() != timedelta(0):
        raise ValueError("UTC timestamp required")
    return t


def validated_rows(rows):
    """Fail closed for duplicate, out-of-order, future or missing PIT metadata."""
    previous = {}
    result = defaultdict(list)
    for row in rows:
        if not FIELDS.issubset(row):
            raise ValueError("required PIT columns absent")
        asset = row["asset"].strip()
        if not asset or not row["continuity_segment_id"]:
            raise ValueError("asset/continuity identity missing")
        observation = parse_time(row["timestamp_utc"])
        known = parse_time(row["knowledge_time_utc"])
        if observation > known:
            raise ValueError("future observation at knowledge time")
        if asset in previous:
            old_obs, old_known = previous[asset]
            if observation <= old_obs or known < old_known:
                raise ValueError("duplicate/out-of-order observation or knowledge time")
        previous[asset] = observation, known
        status = row["source_status"]
        state = row["pullback_risk_state"]
        if status in ALLOWED_STATUS and state not in RANK:
            raise ValueError("unknown state cannot be treated as warning")
        result[asset].append((observation, known, state, status,
                              row["continuity_segment_id"]))
    return result


def run_variant(series, variant):
    """Counts alerts, not independent episodes or successful predictions."""
    threshold = RANK[variant["minimum_state"]]
    persistence = variant["persistence_hours"]
    delay = timedelta(hours=variant["delay_hours"])
    cooldown = timedelta(hours=variant["cooldown_hours"])
    alerts = []
    for asset, rows in sorted(series.items()):
        streak = 0
        last_obs = last_segment = first_ready = last_fire = None
        for observed, known, state, status, segment in rows:
            contiguous = (last_obs is not None and
                          observed - last_obs == timedelta(hours=1) and
                          segment == last_segment)
            if not contiguous:
                streak = 0
                first_ready = None
            usable = status in ALLOWED_STATUS and state in RANK
            if not usable or RANK.get(state, -1) < threshold:
                streak = 0
                first_ready = None
            else:
                streak += 1
                if streak == persistence:
                    first_ready = known
                if (first_ready is not None and known >= first_ready + delay and
                    (last_fire is None or known >= last_fire + cooldown)):
                    alerts.append({"asset": asset, "observation_utc": observed.isoformat(),
                                   "decision_utc": known.isoformat(), "segment": segment})
                    last_fire = known
            last_obs, last_segment = observed, segment
    return alerts


def self_test():
    vs = variants()
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    def row(i, state, status="PASS", segment="s1"):
        t = base + timedelta(hours=i)
        return {"asset": "BTCUSDT", "timestamp_utc": t.isoformat().replace("+00:00", "Z"),
                "knowledge_time_utc": (t + timedelta(minutes=5)).isoformat().replace("+00:00", "Z"),
                "pullback_risk_state": state, "source_status": status,
                "continuity_segment_id": segment}
    rows = [row(0, "NORMAL"), row(1, "ELEVATED"), row(2, "HIGH"),
            row(3, "HIGH"), row(4, "HIGH"), row(5, "NORMAL")]
    series = validated_rows(rows)
    v = {"minimum_state": "HIGH", "persistence_hours": 2, "delay_hours": 1,
         "cooldown_hours": 24}
    got = run_variant(series, v)
    assert len(got) == 1 and got[0]["decision_utc"].startswith("2026-01-01T04:05")
    assert not run_variant(validated_rows([row(0, "HIGH"), row(1, "HIGH", "DEGRADED")]), v)
    assert not run_variant(validated_rows([row(0, "HIGH"), row(2, "HIGH")]), v)
    try:
        validated_rows([row(0, "HIGH"), row(0, "HIGH")])
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate must fail")
    try:
        bad = row(0, "HIGH")
        bad["knowledge_time_utc"] = "2025-12-31T23:00:00Z"
        validated_rows([bad])
    except ValueError:
        pass
    else:
        raise AssertionError("future data must fail")
    assert len(vs) == 144
    return {"status": "SYNTHETIC_TEST_PASS", "variant_count": len(vs),
            "historical_edge_tested": False, "live_authority": False}


def guarded_replay(csv_path, receipt_path):
    source = Path(csv_path).read_bytes()
    digest = hashlib.sha256(source).hexdigest()
    receipt = json.loads(Path(receipt_path).read_text(encoding="utf-8"))
    if not (receipt.get("source_sha256") == digest and
            receipt.get("evidence_class") == "A_PIT_VERIFIED" and
            receipt.get("review_status") == "APPROVED_PIT" and
            receipt.get("independent_reviewer") and
            receipt.get("review_evidence_url") and
            receipt.get("contract") == CONTRACT):
        raise ValueError("PIT provenance receipt not independently approved/bound")
    with Path(csv_path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if not FIELDS.issubset(set(reader.fieldnames or [])):
            raise ValueError("missing PIT columns")
        series = validated_rows(reader)
    output = []
    for v in variants():
        alerts = run_variant(series, v)
        output.append({"variant": v, "descriptive_alert_count": len(alerts),
                       "alerts": alerts})
    return {"contract": CONTRACT, "source_sha256": digest,
            "status": "RESEARCH_ONLY_DESCRIPTIVE_NOT_SCORED",
            "historical_edge_tested": False, "independent_episode_n": None,
            "warning_is_sell": False, "variants": output}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--self-test", action="store_true")
    mode.add_argument("--manifest", action="store_true")
    mode.add_argument("--replay", type=Path)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args()
    if args.self_test:
        output = self_test()
    elif args.manifest:
        output = {"contract": CONTRACT, "status": "PROPOSED_NOT_SCORED",
                  "variants": variants(), "historical_edge_tested": False}
    else:
        if not args.receipt:
            parser.error("--replay requires --receipt")
        output = guarded_replay(args.replay, args.receipt)
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
