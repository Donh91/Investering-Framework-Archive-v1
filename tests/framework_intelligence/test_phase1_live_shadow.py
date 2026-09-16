import unittest
from pathlib import Path

class Phase1FirewallTest(unittest.TestCase):
    def test_contract_forbids_live_influence(self):
        text=Path('research/framework_intelligence/PHASE1_LIVE_PARALLEL_SHADOW_CONTRACT_v1.md').read_text()
        self.assertIn('Live Master Monday influence: NONE',text)
        self.assertIn('Cycle Navigator influence: NONE',text)
        self.assertIn('ZERO_CANONICAL_PROMOTION',text)
        self.assertIn('ZERO_PORTFOLIO_AUTHORITY',text)

    def test_builder_hardcodes_shadow_authority(self):
        text=Path('scripts/framework_intelligence/build_phase1_live_shadow.py').read_text()
        self.assertIn("'live_master_monday_influence':False",text)
        self.assertIn("'cycle_navigator_influence':False",text)
        self.assertIn("'canonical_promotion':False",text)
        self.assertIn("'portfolio_authority':False",text)
        self.assertIn("'live_consumed':False",text)

if __name__=='__main__': unittest.main()
