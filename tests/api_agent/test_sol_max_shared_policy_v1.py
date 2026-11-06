"""Shared Sol-only selection, no Astra and no cross-thread paid bypass."""
import copy
import json
import unittest
from pathlib import Path
from scripts.api_agent import sol_max_shared_policy_v1 as m

ROOT = Path(__file__).resolve().parents[2]
POLICY = json.loads((ROOT / m.POLICY_PATH).read_text())
PRICE = {"gpt-6.1-sol": {"input": 2, "output": 10}}


def future_policy():
    policy = copy.deepcopy(POLICY)
    policy["available_verified_sol_models"].append({
        "id": "gpt-6.2-sol",
        "version": [6, 2],
        "verified_available": True,
        "official_model_spec":
            "https://developers.openai.com/api/docs/models/gpt-6.2-sol",
        "verified_utc_date": "2027-01-01",
        "max_output_tokens": 128000,
        "standard_input_usd_per_million": 3,
        "standard_output_usd_per_million": 12,
    })
    return policy


class SharedSolOwnerPolicyTests(unittest.TestCase):
    def test_today_verifies_exactly_six_one(self):
        self.assertEqual(m.choose_model(POLICY, PRICE)["id"], "gpt-6.1-sol")
        self.assertFalse(POLICY["unverified_next_candidate_enabled"])
        self.assertIn("gpt-6-astra", POLICY["forbidden_auto_models"])
        self.assertTrue(POLICY["manual_astra_only"].startswith("Astra requires"))

    def test_future_verified_six_two_preferred_only_if_project_available(self):
        policy = future_policy()
        prices = dict(PRICE, **{"gpt-6.2-sol": {"input": 3, "output": 12}})
        observed = []
        def model_available(name):
            observed.append(name)
            return name == "gpt-6.2-sol"
        self.assertEqual(m.choose_model(policy, prices, available=model_available)["id"],
                         "gpt-6.2-sol")
        self.assertEqual(observed, ["gpt-6.2-sol"])
        self.assertEqual(m.choose_model(policy, prices)["id"], "gpt-6.1-sol")
        self.assertEqual(m.choose_model(policy, prices, available=lambda _: False)["id"],
                         "gpt-6.1-sol")

    def test_unverified_version_price_or_astra_is_never_selected(self):
        policy = future_policy()
        with self.assertRaisesRegex(ValueError, "PRICE_NOT_PINNED"):
            m.choose_model(policy, PRICE, available=lambda _: True)
        for attack in ("gpt-6-astra", "gpt-6.2-astra",
                       "gpt-6.2-sol-but-private"):
            fake = future_policy()
            fake["available_verified_sol_models"][-1]["id"] = attack
            with self.assertRaisesRegex(ValueError, "NOT_OFFICIALLY_VERIFIED"):
                m.choose_model(fake, dict(PRICE, **{"gpt-6.2-sol": {
                    "input": 3, "output": 12}}), available=lambda _: True)

    def test_max_output_and_money_bound_without_new_paid_post(self):
        row = m.choose_model(POLICY, PRICE)
        self.assertLess(m.quoted_upper_usd(120000, 128000, row), 3)
        for ctx, output in ((180001, 48000), (20000, 128001),
                            (20000, 200000), (0, 48000)):
            with self.assertRaisesRegex(ValueError, "BOUND_INVALID"):
                m.quoted_upper_usd(ctx, output, row)
        expensive = dict(row, standard_output_usd_per_million=30)
        with self.assertRaisesRegex(ValueError, "PRICE_CAP_EXCEEDED"):
            m.quoted_upper_usd(140000, 128000, expensive)

    def test_unsafe_policy_flags_and_unverified_status_fail(self):
        fake = copy.deepcopy(POLICY)
        fake["forbidden_auto_models"] = []
        with self.assertRaisesRegex(ValueError, "POLICY_INVALID"):
            m.choose_model(fake, PRICE)
        fake = copy.deepcopy(POLICY)
        fake["available_verified_sol_models"][0]["verified_available"] = False
        with self.assertRaisesRegex(ValueError, "NOT_OFFICIALLY_VERIFIED"):
            m.choose_model(fake, PRICE)


if __name__ == "__main__":
    unittest.main()
