from __future__ import annotations

import unittest

from scripts.api_agent.meme_alpha_url_provenance import canonicalize_url, reconcile_source_urls


class MemeAlphaUrlProvenanceTests(unittest.TestCase):
    def test_tracking_parameters_and_fragment_do_not_break_identity(self) -> None:
        observed = "https://minepi.com/blog/pi-launchpad/?utm_source=openai#section"
        claimed = "https://minepi.com/blog/pi-launchpad/"
        self.assertEqual(canonicalize_url(observed), canonicalize_url(claimed))

    def test_host_and_path_remain_strict(self) -> None:
        self.assertNotEqual(
            canonicalize_url("https://minepi.com/blog/pi-launchpad/"),
            canonicalize_url("https://example.com/blog/pi-launchpad/"),
        )
        self.assertNotEqual(
            canonicalize_url("https://minepi.com/blog/pi-launchpad/"),
            canonicalize_url("https://minepi.com/blog/other/"),
        )

    def test_non_tracking_query_parameters_remain_part_of_identity(self) -> None:
        self.assertNotEqual(
            canonicalize_url("https://example.com/page?id=1&utm_source=openai"),
            canonicalize_url("https://example.com/page?id=2"),
        )

    def test_reconcile_retains_observed_tool_url(self) -> None:
        claimed = {"https://robinhood.com/us/en/newsroom/robinhood-chain-launches-public-testnet/"}
        observed = {"https://robinhood.com/us/en/newsroom/robinhood-chain-launches-public-testnet/?utm_source=openai"}
        supported, unsupported = reconcile_source_urls(claimed, observed)
        self.assertEqual(supported, sorted(observed))
        self.assertEqual(unsupported, [])

    def test_unobserved_claim_is_still_rejected(self) -> None:
        supported, unsupported = reconcile_source_urls(
            {"https://example.com/not-retrieved"},
            {"https://example.com/retrieved"},
        )
        self.assertEqual(supported, [])
        self.assertEqual(unsupported, ["https://example.com/not-retrieved"])


if __name__ == "__main__":
    unittest.main()
