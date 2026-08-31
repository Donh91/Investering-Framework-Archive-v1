"""Generate explicit missing-evidence matrices; no inferred market observations."""
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def write(name, rows):
    with (ROOT / name).open("w", newline="") as f:
        out = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        out.writeheader()
        out.writerows(rows)


def build():
    m = json.loads((ROOT / "METHODS.json").read_text())["primary"]
    events, horizons, leads, sensitivity = [], [], [], []
    axes = ["ETHBTC_persistence", "BTC_D_rollover", "breadth_survival", "deployment_improvement",
            "large_cap_rotation", "broad_alt_expansion", "smallcap_acceleration"]
    for day in m["annotation_dates"]:
        d = date.fromisoformat(day)
        close = date(d.year, d.month + 2, 1)
        event_id = f"ANNOTATION_{d.year}"
        events.append({"event_id": event_id, "chart_annotation_date": day,
            "hypothetical_standard_2M_bar_close_only": close.isoformat(),
            "bar_open_to_hypothetical_close_days": (close - d).days,
            "verified_original_signal_available_at": None,
            "claim_publication_utc": m["publication_utc"],
            "retrospective_annotation": True,
            "exact_trigger_reproduced": False,
            "is_complete_historical_event_inventory": False})
        for h in m["horizons_calendar_days"]:
            horizons.append({"event_id": event_id, "horizon_calendar_days": h,
                "status": "NOT_EVALUABLE_ORIGINAL_TRIGGER_AND_OUTCOME_BINDING_MISSING",
                "return": None, "MAE": None, "MFE": None, "drawdown": None,
                "time_to_payoff_days": None, "false_positive": None,
                "forward_row": False, "score": None})
        for axis in axes:
            leads.append({"event_id": event_id, "confirmation_axis": axis,
                "trigger_available_at": None, "first_confirmation_known_at": None,
                "signed_lead_days": None, "confirmation_already_true_at_trigger": None,
                "status": "UNKNOWN_NOT_ZERO",
                "blocker": "ORIGINAL_TRIGGER_AVAILABILITY_AND_MATCHED_OWNER_HISTORY_MISSING"})
    for period in m["candidate_sensitivity_only_if_inputs_recovered"]["periods"]:
        for triple in m["candidate_sensitivity_only_if_inputs_recovered"]["sar_triples"]:
            sensitivity.append({"family": "SAR_RECONSTRUCTED_CHALLENGER_NOT_ORIGINAL_TECHDEV",
                "definition": f"period={period};start={triple[0]};increment={triple[1]};max={triple[2]}",
                "status": "NOT_RUN_OHLC_AND_MEMBERSHIP_VINTAGES_MISSING", "n_events": None, "edge": None})
    for family, items in {
        "BASELINE": m["candidate_sensitivity_only_if_inputs_recovered"]["baselines"],
        "ALTERNATIVE_PROXY": ["point_in_time_ranks_11_125_share", "stablecoin_excluded_ex_top10_share", "fixed_inception_basket_sensitivity_not_original"],
        "NULL": m["candidate_sensitivity_only_if_inputs_recovered"]["controls"],
    }.items():
        for item in items:
            sensitivity.append({"family": family, "definition": item,
                "status": "NOT_RUN_COMPARABLE_SIGNAL_HISTORY_MISSING", "n_events": None, "edge": None})
    write("EVENT_INVENTORY.csv", events)
    write("EVENT_HORIZONS.csv", horizons)
    write("LEAD_LAG.csv", leads)
    write("SENSITIVITY_STATUS.csv", sensitivity)
    print(json.dumps({"annotations": len(events), "horizon_slots": len(horizons),
        "lead_lag_slots": len(leads), "sensitivity_plans_not_runs": len(sensitivity),
        "valid_original_signal_events": 0, "numeric_leads": 0}))


if __name__ == "__main__":
    build()
