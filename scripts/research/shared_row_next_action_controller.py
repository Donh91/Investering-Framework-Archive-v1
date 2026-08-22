#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path

DEFAULT_ROOT = Path("06_RESEARCH_LAB/shared_row_model_tournament_v1")


def read_csv(path: Path):
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def parse_dt(value):
    s = str(value or "").strip()
    if not s:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        d = datetime.fromisoformat(s)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d.astimezone(timezone.utc)
    except Exception:
        return None


def iso(d: datetime):
    return d.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def b(value):
    s = str(value or "").strip().lower()
    if s in {"1", "true", "yes", "positive", "signal", "permission", "above", "pass"}:
        return 1
    if s in {"0", "false", "no", "negative", "no_signal", "wait", "block", "below", "fail"}:
        return 0
    return None


def fnum(value):
    try:
        s = str(value or "").strip()
        return float(s) if s else None
    except Exception:
        return None


def wilson(k, n, z):
    if n <= 0:
        return (None, None)
    p = k / n
    den = 1 + z * z / n
    center = (p + z * z / (2 * n)) / den
    margin = z * math.sqrt((p * (1 - p) + z * z / (4 * n)) / n) / den
    return (max(0.0, center - margin), min(1.0, center + margin))


def candidate_registry(root: Path):
    reg = json.loads((root / "03_CANDIDATE_REGISTRY.json").read_text())
    return {c["id"]: c for c in reg.get("candidates", [])}


def last_action_for(history, action, target):
    for r in reversed(history):
        if r.get("primary_action") == action and r.get("target") == target:
            return r
    return None


def context_breakdown(divs, target):
    out = {}
    for d in divs:
        y = b(d.get("outcome_7d"))
        if y is None:
            continue
        if d.get("candidate_a") == target:
            dec = b(d.get("decision_a"))
        elif d.get("candidate_b") == target:
            dec = b(d.get("decision_b"))
        else:
            continue
        if dec is None:
            continue
        key = f"{d.get('regime_tag') or 'UNKNOWN'}|{d.get('catalyst_tag') or 'UNKNOWN'}"
        s = out.setdefault(key, {"n": 0, "correct": 0, "errors": 0, "false_positives": 0, "false_negatives": 0})
        s["n"] += 1
        if dec == y:
            s["correct"] += 1
        else:
            s["errors"] += 1
            if dec == 1 and y == 0:
                s["false_positives"] += 1
            elif dec == 0 and y == 1:
                s["false_negatives"] += 1
    return out


def evidence(rows, divs, policy):
    horizons = ["24h", "72h", "7d"]
    matured_rows = {h: sum(b(r.get(f"outcome_{h}")) is not None for r in rows) for h in horizons}
    matured_divs = {h: sum(b(r.get(f"outcome_{h}")) is not None for r in divs) for h in horizons}

    cstats = {}
    for d in divs:
        y = b(d.get("outcome_7d"))
        da, db = b(d.get("decision_a")), b(d.get("decision_b"))
        if y is None or da is None or db is None or da == db:
            continue
        regime = str(d.get("regime_tag") or "UNKNOWN")
        catalyst = str(d.get("catalyst_tag") or "UNKNOWN")
        context = f"{regime}|{catalyst}"
        for cid, dec, other_dec in [(d.get("candidate_a"), da, db), (d.get("candidate_b"), db, da)]:
            if not cid:
                continue
            s = cstats.setdefault(cid, {
                "resolved_divergences": 0,
                "correct": 0,
                "errors": 0,
                "unique_wins": 0,
                "unique_failures": 0,
                "error_regimes": set(),
                "error_contexts": set(),
                "false_positive_adverse_mae": [],
            })
            s["resolved_divergences"] += 1
            if dec == y:
                s["correct"] += 1
                if other_dec != y:
                    s["unique_wins"] += 1
            else:
                s["errors"] += 1
                s["error_regimes"].add(regime)
                s["error_contexts"].add(context)
                if other_dec == y:
                    s["unique_failures"] += 1
                if dec == 1 and y == 0:
                    mae = fnum(d.get("mae_7d"))
                    if mae is not None:
                        s["false_positive_adverse_mae"].append(abs(min(0.0, mae)))

    for s in cstats.values():
        s["distinct_error_regimes"] = len(s.pop("error_regimes"))
        s["distinct_error_contexts"] = len(s.pop("error_contexts"))
        vals = s.pop("false_positive_adverse_mae")
        s["false_positive_adverse_mae_mean"] = sum(vals) / len(vals) if vals else None
        s["false_positive_adverse_mae_n"] = len(vals)

    baseline = policy["trigger_floors"]["pairwise_relevance_decision"]["baseline_candidate"]
    pair = {}
    for d in divs:
        y = b(d.get("outcome_7d"))
        da, db = b(d.get("decision_a")), b(d.get("decision_b"))
        ca, cb = d.get("candidate_a"), d.get("candidate_b")
        if y is None or da is None or db is None or da == db or baseline not in {ca, cb}:
            continue
        target = cb if ca == baseline else ca
        if not target or target == baseline:
            continue
        tdec = db if ca == baseline else da
        bdec = da if ca == baseline else db
        p = pair.setdefault(target, {
            "resolved": 0,
            "target_unique_wins": 0,
            "baseline_unique_wins": 0,
            "regimes": set(),
            "target_false_positive_mae": [],
            "baseline_false_positive_mae": [],
        })
        p["resolved"] += 1
        p["regimes"].add(str(d.get("regime_tag") or "UNKNOWN"))
        if tdec == y and bdec != y:
            p["target_unique_wins"] += 1
        elif bdec == y and tdec != y:
            p["baseline_unique_wins"] += 1
        mae = fnum(d.get("mae_7d"))
        if mae is not None:
            adverse = abs(min(0.0, mae))
            if tdec == 1 and y == 0:
                p["target_false_positive_mae"].append(adverse)
            if bdec == 1 and y == 0:
                p["baseline_false_positive_mae"].append(adverse)

    z = float(policy["trigger_floors"]["pairwise_relevance_decision"]["wilson_confidence_z"])
    for p in pair.values():
        n = p["target_unique_wins"] + p["baseline_unique_wins"]
        lo, hi = wilson(p["target_unique_wins"], n, z)
        p["unique_resolution_n"] = n
        p["unique_win_share"] = p["target_unique_wins"] / n if n else None
        p["wilson_lower"] = lo
        p["wilson_upper"] = hi
        p["net_unique_wins"] = p["target_unique_wins"] - p["baseline_unique_wins"]
        p["distinct_regimes"] = len(p.pop("regimes"))
        tv = p.pop("target_false_positive_mae")
        bv = p.pop("baseline_false_positive_mae")
        p["target_false_positive_mae_mean"] = sum(tv) / len(tv) if tv else None
        p["baseline_false_positive_mae_mean"] = sum(bv) / len(bv) if bv else None
        p["target_false_positive_mae_n"] = len(tv)
        p["baseline_false_positive_mae_n"] = len(bv)
        if not tv:
            p["tail_non_deterioration"] = True
        elif not bv:
            p["tail_non_deterioration"] = False
        else:
            p["tail_non_deterioration"] = p["target_false_positive_mae_mean"] <= p["baseline_false_positive_mae_mean"] * 1.10

    return {
        "eligible_rows_total": len(rows),
        "divergences_total": len(divs),
        "matured_rows": matured_rows,
        "matured_divergences": matured_divs,
        "candidate_divergence_stats_7d": cstats,
        "pairwise_vs_baseline_7d": pair,
    }


def choose_action(root, rows, ev, policy, now, history):
    floor = None
    runtime = root / "RUNTIME_STATUS.json"
    if runtime.exists():
        try:
            floor = parse_dt(json.loads(runtime.read_text()).get("core_prospective_eligibility_start"))
        except Exception:
            floor = None

    gap_hours = float(policy["trigger_floors"]["expected_row_gap_hours"])
    if floor:
        if not rows and now >= floor + timedelta(hours=gap_hours):
            return "INVESTIGATE_DATA_GAP", "CORE_OWNER_PIPELINE", f"No eligible shared row within {gap_hours:g}h of the frozen prospective floor."
        if rows:
            stamps = [parse_dt(r.get("observation_timestamp_utc")) for r in rows]
            stamps = [x for x in stamps if x is not None]
            last_obs = max(stamps) if stamps else None
            if last_obs and now >= last_obs + timedelta(hours=gap_hours):
                return "INVESTIGATE_DATA_GAP", "CORE_OWNER_PIPELINE", f"No new eligible shared row for at least {gap_hours:g}h."

    first = policy["trigger_floors"]["first_information_review"]
    m7 = ev["matured_rows"]["7d"]
    d7 = ev["matured_divergences"]["7d"]
    if m7 < int(first["matured_7d_rows_min"]):
        return "CONTINUE_OBSERVING", "CORE_C01_C07", "Too few matured +7d rows for the first information review."
    if d7 < int(first["matured_7d_divergences_min"]):
        return "EXTEND_OBSERVATION", "CORE_C01_C07", "Matured outcomes exist, but informative candidate divergences remain too sparse."

    pairpol = policy["trigger_floors"]["pairwise_relevance_decision"]
    promotions, deprioritizations = [], []
    for target, p in ev["pairwise_vs_baseline_7d"].items():
        if p["resolved"] < int(pairpol["resolved_7d_divergences_min"]) or p["distinct_regimes"] < int(pairpol["distinct_regimes_min"]):
            continue
        net = int(p["net_unique_wins"])
        minnet = int(pairpol["net_unique_wins_or_failures_min"])
        lo, hi = p["wilson_lower"], p["wilson_upper"]
        if net >= minnet and lo is not None and lo > float(pairpol["promotion_requires_unique_win_share_lower_bound_gt"]) and (p["tail_non_deterioration"] or not pairpol["tail_error_non_deterioration_required_for_promotion"]):
            promotions.append((target, p))
        if net <= -minnet and hi is not None and hi < float(pairpol["deprioritize_requires_unique_win_share_upper_bound_lt"]):
            deprioritizations.append((target, p))
    if promotions:
        target, _ = sorted(promotions, key=lambda x: (x[1]["wilson_lower"], x[1]["net_unique_wins"]), reverse=True)[0]
        return "PROMOTE_FOR_CANONICAL_REVIEW", target, "Prospective pairwise evidence clears the frozen review gate versus C07; recommendation only."
    if deprioritizations:
        target, _ = sorted(deprioritizations, key=lambda x: (x[1]["wilson_upper"], x[1]["net_unique_wins"]))[0]
        return "DEPRIORITIZE", target, "Prospective pairwise evidence clears the frozen research-only deprioritization gate versus C07."

    cstats = ev["candidate_divergence_stats_7d"]
    if cstats:
        target, top = sorted(cstats.items(), key=lambda x: (x[1]["errors"], x[1]["distinct_error_contexts"]), reverse=True)[0]
        hp = policy["trigger_floors"]["new_hypothesis_research"]
        prior_stress = last_action_for(history, "STRESS_TEST", target)
        if top["errors"] >= int(hp["candidate_7d_errors_min"]) and top["distinct_error_regimes"] >= int(hp["distinct_regimes_min"]) and prior_stress is not None:
            before = int(prior_stress.get("matured_7d_rows") or 0)
            if m7 - before >= int(hp["new_matured_7d_rows_since_prior_stress_min"]):
                return "RESEARCH_NEW_HYPOTHESIS", target, "A previously stress-tested error pattern persists with new matured evidence across multiple regimes."
        sp = policy["trigger_floors"]["stress_test"]
        if top["errors"] >= int(sp["candidate_7d_errors_min"]) and top["distinct_error_contexts"] >= int(sp["distinct_contexts_min"]):
            return "STRESS_TEST", target, "Repeated +7d errors span multiple contexts and justify adversarial stress testing."

    return "INVESTIGATE_DIVERGENCE", "CORE_C01_C07", "The first information-review floor is met; inspect matured disagreements before changing research scope."


def packet_for(action, target, reason, ev, registry, divs, root, now):
    packet = {
        "contract": "RESEARCH_NEXT_ACTION_PACKET_v1",
        "authority": "RESEARCH_ONLY_NON_CANONICAL",
        "generated_at_utc": iso(now),
        "primary_action": action,
        "target": target,
        "reason": reason,
        "evidence_summary": ev,
        "canonical_effect": False,
        "paid_data_authorized": False,
        "deep_research_authorized": False,
    }
    if target in registry:
        packet["target_candidate_definition"] = registry[target]
    if action in {"STRESS_TEST", "RESEARCH_NEW_HYPOTHESIS"} and target in registry:
        packet["target_context_breakdown_7d"] = context_breakdown(divs, target)
    if action == "INVESTIGATE_DATA_GAP":
        try:
            matrix = json.loads((root / "OWNER_BINDING_MATRIX.json").read_text())
            packet["owner_binding_status"] = [{"family_id": x.get("family_id"), "status": x.get("status"), "candidate_decision_contract_status": x.get("candidate_decision_contract_status")} for x in matrix.get("families", [])]
        except Exception:
            packet["owner_binding_status"] = "UNAVAILABLE"
        packet["research_instruction"] = "Diagnose owner freshness, provenance, workflow execution and eligibility rejection reasons. Do not weaken the prospective floor or missingness rules."
    elif action == "INVESTIGATE_DIVERGENCE":
        packet["research_instruction"] = "Audit matured disagreement rows by candidate pair, regime and catalyst; identify unique wins, unique failures and tail-error asymmetry. Do not tune thresholds."
    elif action == "STRESS_TEST":
        packet["research_instruction"] = "Run adversarial context/regime splits and tail-error checks on the selected target. Preserve the frozen decision and outcome contracts."
    elif action == "RESEARCH_NEW_HYPOTHESIS":
        packet["research_instruction"] = "Create a bounded falsifiable hypothesis research packet explaining the persistent failure pattern. Search the existing archive first; external or paid research requires a separate VOI gate."
    elif action == "PROMOTE_FOR_CANONICAL_REVIEW":
        packet["research_instruction"] = "Prepare a canonical-review evidence packet only. Do not modify canonical rules, thresholds, weights or execution."
    elif action == "DEPRIORITIZE":
        packet["research_instruction"] = "Mark the target as a research-deprioritization candidate only; preserve historical evidence and do not delete the candidate."
    else:
        packet["research_instruction"] = "Continue prospective evidence accumulation under frozen contracts."
    return packet


def fingerprint(payload):
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def write_ledger(path: Path, state):
    fields = ["decision_fingerprint", "generated_at_utc", "primary_action", "target", "reason", "eligible_rows_total", "divergences_total", "matured_24h_rows", "matured_72h_rows", "matured_7d_rows", "matured_7d_divergences", "canonical_effect", "paid_data_authorized", "deep_research_authorized"]
    existing = read_csv(path)
    if any(r.get("decision_fingerprint") == state["decision_fingerprint"] for r in existing):
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        if new:
            w.writeheader()
        ev = state["evidence_summary"]
        w.writerow({
            "decision_fingerprint": state["decision_fingerprint"],
            "generated_at_utc": state["generated_at_utc"],
            "primary_action": state["primary_action"],
            "target": state["target"],
            "reason": state["reason"],
            "eligible_rows_total": ev["eligible_rows_total"],
            "divergences_total": ev["divergences_total"],
            "matured_24h_rows": ev["matured_rows"]["24h"],
            "matured_72h_rows": ev["matured_rows"]["72h"],
            "matured_7d_rows": ev["matured_rows"]["7d"],
            "matured_7d_divergences": ev["matured_divergences"]["7d"],
            "canonical_effect": "false",
            "paid_data_authorized": "false",
            "deep_research_authorized": "false",
        })
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(DEFAULT_ROOT))
    ap.add_argument("--now")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    now = parse_dt(args.now) if args.now else datetime.now(timezone.utc)
    if now is None:
        raise SystemExit("INVALID_NOW")

    policy = json.loads((root / "RESEARCH_NEXT_ACTION_POLICY_v1.json").read_text())
    rows = read_csv(root / "data/PROSPECTIVE_SHARED_ROW_LEDGER.csv")
    divs = read_csv(root / "14_DIVERGENCE_FNP_LEDGER.csv")
    hist_path = root / "data/NEXT_ACTION_LEDGER.csv"
    history = read_csv(hist_path)
    registry = candidate_registry(root)
    ev = evidence(rows, divs, policy)
    action, target, reason = choose_action(root, rows, ev, policy, now, history)
    packet = packet_for(action, target, reason, ev, registry, divs, root, now)
    core_fp = {"primary_action": action, "target": target, "reason": reason, "evidence_summary": ev, "policy_contract": policy["contract"]}
    state = {
        **packet,
        "decision_fingerprint": fingerprint(core_fp),
        "policy_contract": policy["contract"],
        "calendar_only_verdict_forbidden": True,
        "automatic_next_action_selection": True,
        "research_action_gate": "JUSTIFIED" if action in {"PROMOTE_FOR_CANONICAL_REVIEW", "DEPRIORITIZE", "RESEARCH_NEW_HYPOTHESIS", "STRESS_TEST", "INVESTIGATE_DIVERGENCE", "INVESTIGATE_DATA_GAP"} else "COLLECT_MORE_EVIDENCE",
        "terminal_verdict": "INSUFFICIENT_EVIDENCE",
    }

    if args.dry_run:
        print(json.dumps(state, sort_keys=True))
        return

    (root / "research_actions").mkdir(parents=True, exist_ok=True)
    (root / "NEXT_ACTION_STATE.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    (root / "research_actions" / "LATEST_ACTION_PACKET.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    if action == "PROMOTE_FOR_CANONICAL_REVIEW":
        (root / "research_actions" / "CANONICAL_REVIEW_PACKET.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    if action == "RESEARCH_NEW_HYPOTHESIS":
        (root / "research_actions" / "HYPOTHESIS_RESEARCH_REQUEST.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    if action == "DEPRIORITIZE":
        (root / "research_actions" / "DEPRIORITIZATION_PACKET.json").write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n")
    appended = write_ledger(hist_path, state)
    print(json.dumps({"status": "PASS", "primary_action": action, "target": target, "ledger_appended": appended, "eligible_rows": ev["eligible_rows_total"], "matured_7d_rows": ev["matured_rows"]["7d"], "matured_7d_divergences": ev["matured_divergences"]["7d"], "canonical_effect": False}, sort_keys=True))


if __name__ == "__main__":
    main()
