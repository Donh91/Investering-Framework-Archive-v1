import unittest
from decimal import localcontext
from scripts.research.vault_flow_integrity_v1 import CONTRACT, EvidenceRefused, evaluate


def fixture():
    return {
        "contract": CONTRACT,
        "evidence_class": "SYNTHETIC_FIXTURE",
        "fee_treatment": "NET_INTERNALISED",
        "as_of_utc": "2026-11-23T12:00:00Z",
        "start_at_utc": "2026-11-20T00:00:00Z",
        "start_first_known_at_utc": "2026-11-20T00:01:00Z",
        "start_equity_after_flow_usd": "100",
        "points": [
            {"event_at_utc": "2026-11-21T00:00:00Z",
             "first_known_at_utc": "2026-11-21T00:01:00Z",
             "equity_before_flow_usd": "100", "external_net_flow_usd": "900",
             "equity_after_flow_usd": "1000", "flow_boundary_complete": True,
             "valuation_evidence_complete": True},
            {"event_at_utc": "2026-11-22T00:00:00Z",
             "first_known_at_utc": "2026-11-22T00:01:00Z",
             "equity_before_flow_usd": "900", "external_net_flow_usd": "-800",
             "equity_after_flow_usd": "100", "flow_boundary_complete": True,
             "valuation_evidence_complete": True},
        ],
    }


class VaultFlowIntegrityTests(unittest.TestCase):
    def test_deposit_withdrawal_and_real_loss_do_not_inflate_return(self):
        r = evaluate(fixture())
        self.assertEqual(float(r["naive_equity_return_pct"]), 0)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), -10)
        self.assertEqual(float(r["naive_account_drawdown_pct"]), 90)
        self.assertEqual(float(r["flow_neutral_drawdown_pct"]), 10)
        self.assertEqual(float(r["net_external_flow_usd"]), 100)
        self.assertFalse(r["prospective_skill_supported"])

    def test_pure_deposit_does_not_fake_900_percent_alpha(self):
        p = fixture()
        p["points"] = p["points"][:1]
        r = evaluate(p)
        self.assertEqual(float(r["naive_equity_return_pct"]), 900)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), 0)
        self.assertEqual(float(r["flow_neutral_drawdown_pct"]), 0)

    def test_pure_redemption_does_not_fake_90_percent_drawdown(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["points"][0].update(equity_before_flow_usd="100", external_net_flow_usd="-90", equity_after_flow_usd="10")
        r = evaluate(p)
        self.assertEqual(float(r["naive_equity_return_pct"]), -90)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), 0)
        self.assertEqual(float(r["flow_neutral_drawdown_pct"]), 0)

    def test_late_backfill_cannot_be_used_as_asof_evidence(self):
        p = fixture()
        p["points"][0]["first_known_at_utc"] = "2026-11-24T00:00:00Z"
        with self.assertRaisesRegex(EvidenceRefused, "CLOCK_LEAK_OR_REORDER"):
            evaluate(p)

    def test_source_clock_before_event_refused(self):
        p = fixture()
        p["points"][0]["first_known_at_utc"] = "2026-11-20T23:59:59Z"
        with self.assertRaisesRegex(EvidenceRefused, "CLOCK_LEAK_OR_REORDER"):
            evaluate(p)

    def test_missing_flow_is_not_zero(self):
        p = fixture()
        p["points"][0].pop("external_net_flow_usd")
        with self.assertRaisesRegex(EvidenceRefused, "DECIMAL_STRING_REQUIRED"):
            evaluate(p)

    def test_missing_boundary_cannot_infer_twr(self):
        p = fixture()
        p["points"][0]["flow_boundary_complete"] = False
        with self.assertRaisesRegex(EvidenceRefused, "flow_boundary_complete:UNPROVEN"):
            evaluate(p)

    def test_wrong_flow_reconciliation_refused(self):
        p = fixture()
        p["points"][1]["equity_after_flow_usd"] = "1000"
        with self.assertRaisesRegex(EvidenceRefused, "FLOW_RECONCILIATION_FAILED"):
            evaluate(p)

    def test_duplicate_checkpoint_time_refused(self):
        p = fixture()
        p["points"][1]["event_at_utc"] = p["points"][0]["event_at_utc"]
        with self.assertRaisesRegex(EvidenceRefused, "CLOCK_LEAK_OR_REORDER"):
            evaluate(p)

    def test_unknown_fee_convention_refused(self):
        p = fixture()
        p["fee_treatment"] = "GROSS_UNKNOWN"
        with self.assertRaisesRegex(EvidenceRefused, "FEE_TREATMENT_UNVERIFIED"):
            evaluate(p)

    def test_nonfinite_and_boolean_numeric_inputs_refused(self):
        for value in ("NaN", "Infinity", True, 0.1, "bogus"):
            with self.subTest(value=value):
                p = fixture()
                p["points"][0]["external_net_flow_usd"] = value
                with self.assertRaises(EvidenceRefused):
                    evaluate(p)

    def test_start_baseline_first_known_after_first_event_is_inadmissible(self):
        p = fixture()
        p["start_first_known_at_utc"] = "2026-11-21T00:30:00Z"
        with self.assertRaisesRegex(EvidenceRefused, "START_BASELINE_NOT_KNOWN_BEFORE_FIRST_EVENT"):
            evaluate(p)

    def test_zero_equity_terminal_loss_is_reported_not_rebased(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["points"][0].update(equity_before_flow_usd="0", external_net_flow_usd="0", equity_after_flow_usd="0")
        r = evaluate(p)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), -100)
        self.assertFalse(r["eligible_to_rank_vaults"])

    def test_codex_p2_rejects_tiny_equity_reconciliation_materiality(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["start_equity_after_flow_usd"] = "0.0000001"
        p["points"][0].update(equity_before_flow_usd="0.0000001",
                              external_net_flow_usd="0", equity_after_flow_usd="0.00000001")
        with self.assertRaisesRegex(EvidenceRefused, "UNSUPPORTED_PRECISION"):
            evaluate(p)

    def test_codex_p2_rejects_1e30_rounding_and_large_amounts(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["start_equity_after_flow_usd"] = "1e30"
        p["points"][0].update(equity_before_flow_usd="1e30",
                              external_net_flow_usd="1", equity_after_flow_usd="1e30")
        with self.assertRaisesRegex(EvidenceRefused, "AMOUNT_OUT_OF_BOUNDS"):
            evaluate(p)

    def test_codex_p2_decimal_precision_invariant(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["start_equity_after_flow_usd"] = "7"
        p["points"][0].update(equity_before_flow_usd="8",
                              external_net_flow_usd="0", equity_after_flow_usd="8")
        default = evaluate(p)
        with localcontext() as context:
            context.prec = 2
            changed = evaluate(p)
        self.assertEqual(default["flow_neutral_twr_pct"], changed["flow_neutral_twr_pct"])
        self.assertTrue(default["flow_neutral_twr_pct"].startswith("14.28571428"))

    def test_codex_p2_withdraw_at_new_peak_naive_drawdown(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["points"][0].update(equity_before_flow_usd="200",
                              external_net_flow_usd="-100", equity_after_flow_usd="100")
        r = evaluate(p)
        self.assertEqual(float(r["naive_account_drawdown_pct"]), 50)
        self.assertEqual(float(r["flow_neutral_drawdown_pct"]), 0)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), 100)

    def test_codex_p2_deposit_after_loss_naive_sees_interim_drop(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["points"][0].update(equity_before_flow_usd="50",
                              external_net_flow_usd="100", equity_after_flow_usd="150")
        r = evaluate(p)
        self.assertEqual(float(r["naive_account_drawdown_pct"]), 50)
        self.assertEqual(float(r["flow_neutral_drawdown_pct"]), 50)
        self.assertEqual(float(r["flow_neutral_twr_pct"]), -50)

    def test_codex_p2_sub_micro_unit_reconciliation_rejected(self):
        p = fixture()
        p["points"] = p["points"][:1]
        p["points"][0]["equity_after_flow_usd"] = "1000.0000001"
        with self.assertRaisesRegex(EvidenceRefused, "UNSUPPORTED_PRECISION"):
            evaluate(p)

    def test_unknown_source_class_not_promoted(self):
        p = fixture()
        p["evidence_class"] = "LIVE_VERIFIED"
        with self.assertRaisesRegex(EvidenceRefused, "EVIDENCE_CLASS_NOT_ADMITTED"):
            evaluate(p)

    def test_zero_equity_recapitalization_no_fake_new_epoch(self):
        p = fixture()
        p["points"][0].update(equity_before_flow_usd="0", external_net_flow_usd="1000", equity_after_flow_usd="1000")
        with self.assertRaisesRegex(EvidenceRefused, "BANKRUPTCY_EPOCH_REQUIRES_NEW_LEDGER"):
            evaluate(p)

    def test_full_redemption_then_new_period_requires_explicit_epoch(self):
        p = fixture()
        p["points"][0].update(equity_before_flow_usd="100", external_net_flow_usd="-100", equity_after_flow_usd="0")
        with self.assertRaisesRegex(EvidenceRefused, "ZERO_EQUITY_EPOCH_UNRESOLVED"):
            evaluate(p)


if __name__ == "__main__":
    unittest.main()
