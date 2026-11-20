"""Synthetic accounting-only controls; no network or model calls."""
import contextlib
from datetime import datetime, timezone
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.api_agent import check_monthly_cost_guard as guard

OPAQUE = guard.opaque_reservations
ID = "0123456789abcdef0123456789abcdef"


def row():
    return {"reservation_id": ID, "created_month_utc": "2025-12",
            "status": "HELD_FULL_UPPER_NO_RELEASE", "upper_usd": "3",
            "one_paid_post_max": 1, "no_retry": True,
            "reconciliation_required": True}


def ledger(rows=None):
    out = {"contract": "API_PENDING_BILLING_RISK_V1",
           "no_retry_original_ids": True,
           "requires_reconciliation_before_releasing_reserve": True,
           "unresolved": []}
    if rows is not None:
        out[OPAQUE.KEY] = rows
    return out


class OpaqueApiLiabilityTests(unittest.TestCase):
    def test_defaults_no_active_pins_unchanged_existing_ledger(self):
        self.assertEqual(OPAQUE.RETAINED, {})
        self.assertEqual(OPAQUE.pending_upper(ledger()), (0, 0))
        self.assertEqual(OPAQUE.pending_upper(ledger([])), (0, 0))
        with self.assertRaisesRegex(ValueError, "PIN_MISMATCH"):
            OPAQUE.pending_upper(ledger([row()]))

    def test_full_upper_and_rollover_retention(self):
        with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}):
            self.assertEqual(OPAQUE.pending_upper(ledger([row()])), (3, 1))
            for value in (ledger(), ledger([])):
                with self.assertRaisesRegex(ValueError, "RETAINED_MISSING"):
                    OPAQUE.pending_upper(value)

    def test_no_release_retry_or_ceiling_mutation(self):
        bad = [dict(row(), status="SETTLED"), dict(row(), status="EXPIRED"),
               dict(row(), upper_usd="2"), dict(row(), upper_usd="3.000"),
               dict(row(), upper_usd="3.01"), dict(row(), upper_usd="NaN"),
               dict(row(), upper_usd=True), dict(row(), upper_usd=3),
               dict(row(), created_month_utc="2026-11"),
               dict(row(), no_retry=False), dict(row(), one_paid_post_max=True),
               dict(row(), reconciliation_required=False)]
        with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}):
            for entry in bad:
                with self.subTest(entry=entry):
                    with self.assertRaises(ValueError):
                        OPAQUE.pending_upper(ledger([entry]))

    def test_exact_pinned_over_cap_is_rejected(self):
        # Matching a reviewed pin must not hide an invalid ceiling.
        for value in ("3.000001", "5", "0"):
            with self.subTest(value=value):
                with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", value)}):
                    with self.assertRaisesRegex(ValueError, "OPAQUE_API_RESERVATION_CAP_INVALID"):
                        OPAQUE.pending_upper(ledger([dict(row(), upper_usd=value)]))

    def test_duplicate_source_pin_is_not_silently_overwritten(self):
        for second in ("3", "2"):
            with self.subTest(second=second):
                with self.assertRaisesRegex(ValueError, "OPAQUE_API_RESERVATION_DUPLICATE_PIN"):
                    OPAQUE.retained_pins(((ID, "2025-12", "3"), (ID, "2025-12", second)))
        self.assertEqual(OPAQUE.retained_pins(((ID, "2025-12", "3"),)),
                         {ID: ("2025-12", "3")})
        self.assertEqual(OPAQUE.retained_pins(()), {})

    def test_duplicate_unknown_or_extra_metadata_denied(self):
        with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}):
            for value in ([row(), row()], [dict(row(), source="synthetic")],
                          [dict(row(), reservation_id="a"*32)], {}, None):
                with self.subTest(value=value):
                    data = ledger()
                    data[OPAQUE.KEY] = value
                    with self.assertRaises(ValueError):
                        OPAQUE.pending_upper(data)

    def test_guard_includes_full_upper_in_pending_risk(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "ledger.json"
            p.write_text(json.dumps(ledger([row()])))
            with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}):
                self.assertEqual(guard.pending_risk(p), (0, 3, 1))
                p.write_text(json.dumps(ledger()))
                with self.assertRaisesRegex(ValueError, "RETAINED_MISSING"):
                    guard.pending_risk(p)

    def test_real_guard_main_enforces_normal_budget_no_exception(self):
        import sys
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            receipts = root / "receipts"
            receipts.mkdir()
            (receipts / "receipt.json").write_text(json.dumps({
                "contract": "SYNTHETIC_OWNER_COST_RECEIPT_v1",
                "response_id": "synthetic-opaque-test",
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
                "estimated_cost_usd": 34,
            }))
            p = root / "ledger.json"
            p.write_text(json.dumps(ledger([row()])))
            args = ["guard", "--receipt-root", str(receipts),
                    "--liability-ledger", str(p), "--hard-stop-usd", "40",
                    "--reserve-usd", "4"]
            out = io.StringIO()
            with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}), \
                 patch.object(sys, "argv", args), contextlib.redirect_stdout(out), \
                 self.assertRaises(SystemExit):
                guard.main()
            data = json.loads(out.getvalue())
            self.assertEqual(data["status"], "BLOCKED")
            self.assertFalse(data["paid_authority"])
            self.assertEqual(data["pending_liability_upper_usd"], 3)
            self.assertEqual(data["exposure_range_max_usd"], 37)
            self.assertEqual(data["remaining_usd"], 3)
            p.write_text(json.dumps(ledger()))
            out = io.StringIO()
            with patch.object(OPAQUE, "RETAINED", {ID: ("2025-12", "3")}), \
                 patch.object(sys, "argv", args), contextlib.redirect_stdout(out), \
                 self.assertRaises(SystemExit):
                guard.main()
            self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")
