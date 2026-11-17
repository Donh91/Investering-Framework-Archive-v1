"""Pure, research-only matched opportunity-set primitive for EXT-ALPHA-0002.
No private data loader, I/O, model fit, API dispatch or live authority.
Call only after the existing source owner admits a cohort; no Round3 analysis.
"""
from datetime import datetime, timedelta, timezone

_FIELDS = frozenset({
    "id", "asset", "timeframe", "era", "decision_at", "features_available_at",
    "eligibility", "ledger_coverage", "action",
})

def _utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("UTC timestamp required")
    return datetime.fromisoformat(value[:-1] + "+00:00").astimezone(timezone.utc)

def match_entries(rows, *, max_prior_days=28):
    """Same-asset/timeframe/era/hour prior NONE controls; deterministic.
    Input is metadata-only from an already admitted source owner. NONE requires
    explicit eligibility and complete observation; absence from a trade ledger
    does not establish either. No features/outcomes accepted by this function.
    Controls are not assumed independent and may be reused (report reuse).
    Research design only; the source owner must separately prove coverage,
    no overlap of active positions and all admission/embargo gates.
    """
    if type(max_prior_days) is not int or not 1 <= max_prior_days <= 90:
        raise ValueError("invalid matching window")
    seen_ids, seen_keys, ordered = set(), set(), []
    for row in rows:
        if not isinstance(row, dict) or set(row) != _FIELDS:
            raise ValueError("unexpected or missing fields")
        for key in ("id", "asset", "timeframe", "era"):
            if not isinstance(row[key], str) or not row[key].strip():
                raise ValueError("missing identity")
        t, k = _utc(row["decision_at"]), _utc(row["features_available_at"])
        group = (row["asset"], row["timeframe"], row["era"])
        identity = (group, t)
        if row["id"] in seen_ids or identity in seen_keys:
            raise ValueError("duplicate opportunity")
        seen_ids.add(row["id"])
        seen_keys.add(identity)
        if row["action"] not in {"ENTRY", "NONE", "DCA", "EXIT", "UNKNOWN"}:
            raise ValueError("unknown action")
        if row["eligibility"] not in {"ELIGIBLE", "INELIGIBLE", "UNKNOWN"}:
            raise ValueError("unknown eligibility")
        if row["ledger_coverage"] not in {"COMPLETE", "INCOMPLETE", "UNKNOWN"}:
            raise ValueError("unknown coverage")
        eligible = (k <= t and row["eligibility"] == "ELIGIBLE"
                    and row["ledger_coverage"] == "COMPLETE")
        ordered.append((t, group, row["id"], row["action"], eligible))
    ordered.sort()
    by_group = {}
    matched, unmatched = [], []
    reused = {}
    excluded = 0
    for t, group, ident, action, eligible in ordered:
        if not eligible or action not in {"ENTRY", "NONE"}:
            excluded += 1
            continue
        key = (group, t.hour, t.minute)
        controls = by_group.setdefault(key, [])
        if action == "NONE":
            controls.append((t, ident))
            continue
        candidate = next(((ct, cid) for ct, cid in reversed(controls)
                          if timedelta(0) < t - ct <= timedelta(days=max_prior_days)), None)
        if candidate is None:
            unmatched.append(ident)
            continue
        cid = candidate[1]
        matched.append({"entry_id": ident, "control_id": cid})
        reused[cid] = reused.get(cid, 0) + 1
    return {"matched": matched, "unmatched_entry_ids": unmatched,
            "excluded_rows": excluded, "control_reuse": reused,
            "research_only": True}
