"""Opaque API liabilities: accounting only, no dispatch authority.

Each future admission requires a separately reviewed retained pin and ledger
row. This version has ZERO retained pins and accepts ZERO active reservations.
No automatic release, expiry, settlement, retry or payment capability.
"""
from decimal import Decimal
import re

KEY = "opaque_api_reservations"
MAX_OUTSTANDING = 12
MAX_SINGLE_USD = Decimal("3")
# Append exact reviewed ID, original UTC month and full ceiling in the same
# future release as the canonical ledger row. Never delete or lower a pin.
RETAINED_ROWS = ()
FIELDS = {"reservation_id", "created_month_utc", "status", "upper_usd",
          "one_paid_post_max", "no_retry", "reconciliation_required"}
ID = re.compile(r"[0-9a-f]{32}\Z")
MONTH = re.compile(r"20[0-9]{2}-(0[1-9]|1[0-2])\Z")
USD = re.compile(r"(?:0|[1-9][0-9]*)(?:\.[0-9]{1,6})?\Z")


def retained_pins(rows):
    """Reject duplicate reviewed IDs before converting source rows to a map."""
    pins = {}
    for ident, month, upper in rows:
        if ident in pins:
            raise ValueError("OPAQUE_API_RESERVATION_DUPLICATE_PIN")
        pins[ident] = (month, upper)
    return pins


RETAINED = retained_pins(RETAINED_ROWS)


def pending_upper(ledger: dict) -> tuple[float, int]:
    """Full outstanding liability, including previous UTC months."""
    rows = ledger.get(KEY, [])
    if type(rows) is not list or len(rows) > MAX_OUTSTANDING:
        raise ValueError("OPAQUE_API_RESERVATION_LEDGER_INVALID")
    seen, total = set(), Decimal("0")
    for row in rows:
        if type(row) is not dict or set(row) != FIELDS:
            raise ValueError("OPAQUE_API_RESERVATION_ROW_INVALID")
        ident, month, upper = (row["reservation_id"], row["created_month_utc"],
                               row["upper_usd"])
        if (type(ident) is not str or not ID.fullmatch(ident) or ident in seen
                or type(month) is not str or not MONTH.fullmatch(month)
                or type(upper) is not str or not USD.fullmatch(upper)
                or len(upper) > 8
                or row["status"] != "HELD_FULL_UPPER_NO_RELEASE"
                or type(row["one_paid_post_max"]) is not int
                or row["one_paid_post_max"] != 1
                or row["no_retry"] is not True
                or row["reconciliation_required"] is not True):
            raise ValueError("OPAQUE_API_RESERVATION_UNVERIFIED")
        amount = Decimal(upper)
        if not 0 < amount <= MAX_SINGLE_USD:
            raise ValueError("OPAQUE_API_RESERVATION_CAP_INVALID")
        if RETAINED.get(ident) != (month, upper):
            raise ValueError("OPAQUE_API_RESERVATION_PIN_MISMATCH")
        seen.add(ident)
        total += amount
    if seen != set(RETAINED):
        raise ValueError("OPAQUE_API_RESERVATION_RETAINED_MISSING")
    return float(total), len(seen)
