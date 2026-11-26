"""Exact target-grid preflight for rolling Kompas Live, without outcomes."""
import datetime as dt
import math
import re

DAY = dt.timedelta(days=1)
HORIZONS = (1, 3, 7)
ASSETS = ("BTC", "ETH")


def utc(value):
    if not isinstance(value, str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
        raise ValueError("explicit UTC required")
    return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))


def iso(value):
    return value.isoformat().replace("+00:00", "Z")


def ceil_day(t):
    midnight = t.replace(hour=0, minute=0, second=0, microsecond=0)
    return midnight if t == midnight else midnight + DAY


def price(x):
    if type(x) not in (int, float) or not math.isfinite(x) or x <= 0:
        raise ValueError("invalid price")
    return x


def targets(doc):
    if doc.get("contract") != "KOMPAS_LIVE_PATH_v1":
        raise ValueError("wrong source contract")
    authority = doc.get("authority", {})
    for k, expected in (("research_only", True), ("official_forecast", False),
                        ("compass_probability_claim", False), ("trading", False),
                        ("promotion", False), ("site_synthesis", False)):
        if authority.get(k) is not expected:
            raise ValueError("wrong authority")
    issued = utc(doc["generated_at_utc"])
    ends = doc["horizon_end_utc"]
    if set(ends) != set(map(str, HORIZONS)):
        raise ValueError("incomplete horizon census")
    for h in HORIZONS:
        if utc(ends[str(h)]) != ceil_day(issued + h*DAY):
            raise ValueError("target does not match producer UTC rule")
    assets = doc["assets"]
    if set(assets) != set(ASSETS):
        raise ValueError("incomplete asset census")
    rows = []
    for asset in ASSETS:
        block = assets[asset]
        if block.get("quote") != "USDT":
            raise ValueError("quote mismatch")
        if block.get("status") == "UNAVAILABLE":
            for h in HORIZONS:
                rows.append({"asset": asset, "horizon_days_label": h,
                             "target_utc": iso(utc(ends[str(h)])), "quote": "USDT", "status": "UNAVAILABLE",
                             "reference_price": None, "candidate_close": None,
                             "baseline_close": None, "range": None})
            continue
        if block.get("status") != "OK":
            raise ValueError("unknown asset status")
        asof = utc(block["as_of_utc"])
        if not dt.timedelta(0) <= issued-asof <= dt.timedelta(minutes=90):
            raise ValueError("invalid issue/reference clock")
        p0 = price(block["p0"])
        # Internal consistency, not independent price-source authentication.
        points = block.get("points")
        if not isinstance(points, list) or not points:
            raise ValueError("missing reference points")
        previous = None
        for point in points:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError("invalid reference point")
            clock, close = utc(point[0]), price(point[1])
            if clock.minute or clock.second or clock.microsecond or clock > asof:
                raise ValueError("invalid hourly reference clock")
            if previous is not None and clock <= previous:
                raise ValueError("reference points out of order")
            previous = clock
        if previous != asof or close != p0:
            raise ValueError("reference tail mismatch")
        indexed = {}
        previous = None
        for index, day in enumerate(block["days"]):
            t = utc(day["end_utc"])
            if t in indexed or t != ceil_day(t) or t <= issued:
                raise ValueError("invalid or duplicate UTC day endpoint")
            if previous is not None and t <= previous:
                raise ValueError("day endpoints out of order")
            previous = t
            # Mirror producer day_grid: first day may be partial, subsequent
            # days start at midnight; h is cumulative from the issue clock.
            expected_start = max(t - DAY, issued)
            if type(day.get("index")) is not int or day["index"] != index:
                raise ValueError("wrong day index")
            if utc(day.get("start_utc")) != expected_start:
                raise ValueError("wrong day start")
            h = day.get("h")
            if (type(h) not in (int, float) or not math.isfinite(h)
                    or h != round((t - issued).total_seconds() / 3600, 4)):
                raise ValueError("wrong day duration")
            lo, mid, hi = map(price, (day["lo"], day["centre"], day["hi"]))
            if not lo <= mid <= hi:
                raise ValueError("invalid interval")
            indexed[t] = (lo, mid, hi)
        first = issued.replace(hour=0, minute=0, second=0, microsecond=0)+DAY
        expected = set()
        while first <= ceil_day(issued + 7*DAY):
            expected.add(first)
            first += DAY
        if set(indexed) != expected:
            raise ValueError("incomplete day grid")
        heads = block["headline"]
        if set(heads) != set(map(str, HORIZONS)):
            raise ValueError("incomplete headline census")
        for h in HORIZONS:
            t = utc(ends[str(h)])
            lo, mid, hi = indexed[t]
            head = heads[str(h)]
            if utc(head["end_utc"]) != t or price(head["target"]) != mid:
                raise ValueError("headline target mismatch")
            rows.append({"asset": asset, "horizon_days_label": h, "target_utc": iso(t),
                         "status": "TARGET_PREFLIGHT_ONLY", "quote": "USDT", "reference_as_of_utc": iso(asof),
                         "reference_price": p0, "candidate_close": mid, "baseline_close": p0,
                         "range": {"lo": lo, "hi": hi, "semantics": "NOMINAL_MODEL_RANGE"},
                         "duration_from_issue_hours": (t-issued).total_seconds()/3600})
    count = sum(a.get("status") == "OK" for a in assets.values())
    if doc.get("status") != ("OK" if count == 2 else "PARTIAL" if count == 1 else "UNAVAILABLE"):
        raise ValueError("inconsistent document status")
    return {"contract": "KOMPAS_LIVE_TARGET_PREFLIGHT_v1",
            "status": "NO_OUTCOMES_NO_ADMISSION", "generated_at_utc": iso(issued),
            "rows": rows, "candidate_variant": "PRODUCER_PRIMARY_NOT_VIEWER_STATE",
            "publication_authenticated": False,
            "pit_admitted": False, "scoring_authorized": False}
