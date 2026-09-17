from __future__ import annotations

import unittest

from scripts.api_agent import alpha_arc_direct_new_pair as arc


class ArcRpcProvenanceTests(unittest.TestCase):
    def test_rpc_provenance_never_contains_path_query_or_credentials(self) -> None:
        url="https://user:secret@provider.example/v2/API_KEY?token=SECRET"
        self.assertEqual(arc.rpc_label(url),"provider.example")
        self.assertNotIn("secret",arc.rpc_label(url))
        self.assertNotIn("API_KEY",arc.rpc_label(url))


if __name__=="__main__":
    unittest.main()
