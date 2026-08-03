from __future__ import annotations
import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

class PreflightTests(unittest.TestCase):
    def test_partial_package_reconciles_all_60_actions(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            (r/'research/master_monday_preflight').mkdir(parents=True)
            reg=json.loads((ROOT/'research/master_monday_preflight/MASTER_MONDAY_ACTION_REGISTRY_v1.json').read_text())
            pred=json.loads((ROOT/'research/master_monday_preflight/CANONICAL_PREDECESSOR_REGISTRY_v1.json').read_text())
            (r/'reg.json').write_text(json.dumps(reg)); (r/'pred.json').write_text(json.dumps(pred))
            out=r/'out.json'
            p=subprocess.run(['python',str(ROOT/'scripts/master_monday/build_preflight_package.py'),'--repo-root',str(r),'--registry',str(r/'reg.json'),'--predecessor-registry',str(r/'pred.json'),'--output',str(out)],text=True,capture_output=True)
            self.assertEqual(p.returncode,0,p.stderr)
            v=json.loads(out.read_text())
            self.assertEqual(v['root_contract'],'MASTER_MONDAY_GAP_FILL_PACKAGE_v1')
            self.assertEqual(v['meta']['planned_core_actions'],60)
            self.assertEqual(v['meta']['attempted_core_actions'],60)
            self.assertTrue(v['meta']['counts_reconciled'])
            self.assertEqual(len(v['source_ledgers']),60)
            self.assertEqual(v['packet']['status'],'PARTIAL_WITH_EXPLICIT_GAPS')
            self.assertFalse(v['authority']['portfolio_action'])

    def test_bounded_observation_never_becomes_predecessor(self):
        pred=json.loads((ROOT/'research/master_monday_preflight/CANONICAL_PREDECESSOR_REGISTRY_v1.json').read_text())
        self.assertEqual(pred['predecessor_scope'],'CANONICAL_ACCEPTED_MARKET_PREDECESSOR')
        self.assertFalse(pred['bounded_observations_are_predecessors'])

if __name__=='__main__': unittest.main()
