from __future__ import annotations

import unittest

from scripts.research.memes_alpha import adversarial_operator_counting as m


def make_calldata(exemptions: list[str]) -> str:
    selector = b"\x12\x34\x56\x78"

    def word(value: int) -> bytes:
        return int(value).to_bytes(32, "big")

    def address(value: str) -> bytes:
        return bytes.fromhex("00" * 12 + value[2:])

    args = bytearray(7 * 32)
    args[2 * 32:3 * 32] = address("0x" + "11" * 20)
    args[3 * 32:4 * 32] = word(123)
    args[5 * 32:6 * 32] = address("0x" + "22" * 20)
    offset = 7 * 32
    args[6 * 32:7 * 32] = word(offset)
    tail = word(len(exemptions)) + b"".join(address(value) for value in exemptions)
    return "0x" + (selector + bytes(args) + tail).hex()


def base_event(**kwargs):
    event = {
        "token_ca": "0xd5520D9D777a42D85f94834fbea162B17A197CfB",
        "launch_t0": "2026-10-01T01:00:00Z",
        "raw_tx_input": make_calldata(["0x" + "33" * 20]),
        "pre_t0_prep_observed": True,
        "common_funding": True,
        "common_funder_class": "NON_BENIGN",
        "synchronized_inventory": True,
        "residual_similarity": True,
    }
    event.update(kwargs)
    return event


class AdversarialOperatorCountingTests(unittest.TestCase):
    def test_raw_calldata_decodes_exemption_surface(self) -> None:
        row = m.decode_launch_and_buy_calldata(make_calldata(["0x" + "33" * 20, "0x" + "44" * 20]))
        self.assertEqual(row["state"], "PASS")
        self.assertEqual(row["snipe_exemption_count"], 2)
        self.assertEqual(row["recipient"], "0x" + "22" * 20)

    def test_benign_infra_cannot_qualify(self) -> None:
        row = m.classify_event(base_event(common_funder_class="RELAY"))
        self.assertTrue(row["raw_fire"])
        self.assertFalse(row["stage1_qualified"])
        self.assertEqual(row["classification"], "FALSE_POSITIVE_INFRA")

    def test_unknown_infra_stays_unknown(self) -> None:
        event = base_event()
        event.pop("common_funder_class")
        row = m.classify_event(event)
        self.assertEqual(row["classification"], "UNKNOWN_INFRA")
        self.assertFalse(row["stage1_qualified"])

    def test_shared_factory_or_relaunch_alone_do_not_fire(self) -> None:
        row = m.classify_event({
            "token_ca": "0x" + "55" * 20,
            "launch_t0": "2026-10-01T01:00:00Z",
            "raw_tx_input": make_calldata([]),
            "pre_t0_prep_observed": True,
            "same_pons_factory": True,
            "relaunch_retry": True,
            "common_quote_asset": True,
            "benign_infra_excluded": True,
        })
        self.assertFalse(row["raw_fire"])
        self.assertFalse(row["stage1_qualified"])

    def test_direct_non_benign_lineage_qualifies_stage2(self) -> None:
        row = m.classify_event(base_event(direct_operator_lineage=True, privileged_bundle_evidence=False))
        self.assertTrue(row["stage1_qualified"])
        self.assertTrue(row["stage2_qualified"])
        self.assertEqual(row["stage2_reason"], "DIRECT_OPERATOR_LINEAGE")

    def test_manifest_preserves_every_row_and_overlap_counts(self) -> None:
        manifest = {
            "contract": m.MANIFEST_CONTRACT,
            "interval_start_utc": "2026-10-01T00:00:00Z",
            "interval_end_utc": "2026-10-02T00:00:00Z",
            "events": [
                base_event(),
                base_event(token_ca="0x" + "66" * 20, ordinary_control=True, common_funder_class="RELAY"),
                {"token_ca": "0x" + "77" * 20, "launch_t0": "2026-10-01T03:00:00Z"},
            ],
        }
        out = m.count_manifest(manifest)
        self.assertEqual(out["launch_rows"], 3)
        self.assertEqual(out["counts"]["known_seed_overlap"], 1)
        self.assertEqual(out["counts"]["ordinary_control_overlap"], 0)
        self.assertEqual(out["counts"]["benign_infra_false_positives"], 1)
        self.assertFalse(out["source_health"]["missing_is_negative_evidence"])
        self.assertEqual(len(out["input_sha256"]), 64)
        self.assertEqual(len(out["output_sha256"]), 64)

    def test_decoded_input_is_supported_without_raw_calldata(self) -> None:
        event = base_event()
        event.pop("raw_tx_input")
        event["decoded_input"] = {
            "parameters": [
                {"name": "pairToken", "value": "0x" + "11" * 20},
                {"name": "recipient", "value": "0x" + "22" * 20},
                {"name": "snipeTaxExemptions", "value": ["0x" + "33" * 20]},
            ]
        }
        row = m.classify_event(event)
        self.assertEqual(row["privileged_surface"]["source"], "DECODED_INPUT")
        self.assertEqual(row["privileged_surface"]["snipe_exemption_count"], 1)

    def test_stage1_over_budget_triggers_stage2_gate(self) -> None:
        events = []
        for i in range(11):
            events.append(base_event(token_ca="0x" + f"{i + 1:040x}", direct_operator_lineage=False))
        out = m.count_manifest({
            "contract": m.MANIFEST_CONTRACT,
            "interval_start_utc": "2026-10-01T00:00:00Z",
            "interval_end_utc": "2026-10-02T00:00:00Z",
            "events": events,
        })
        self.assertEqual(out["gates"]["stage1"], "STAGE2_REQUIRED")
        self.assertEqual(out["gates"]["stage2"], "AUTONOMOUS_TIME_SENSITIVE_REVIEW_OPERATIONALLY_UNVIABLE")


if __name__ == "__main__":
    unittest.main()
