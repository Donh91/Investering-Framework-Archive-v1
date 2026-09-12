import copy
import json
import tempfile
from pathlib import Path
import unittest
from scripts.experiments.simplification_review import review, load_candidates

class ReviewTests(unittest.TestCase):
    def inputs(self):
        spec = dict(kind='FORECAST_TEST', hypothesis='same frozen claim', falsifier='fixed horizon miss', horizon_days=7,
                    target_metric_path='market_metrics.derivatives.BTC.mark_price', target_direction='UP', target_threshold_pct=2,
                    components=[], regime_dependency='ALL', target_unit_contract_version='v2')
        sources = {cid: {'spec': copy.deepcopy(spec)} for cid in ['a','b']}
        sources['b']['spec']['target_metric_path'] = 'latest_capture.market_metrics.derivatives.BTC.mark_price'
        reg = {'candidates': [dict(candidate_id=c, state='INCUBATING', observation_count=20, matured_outcome_count=0, forecast_ids=[]) for c in sources]}
        return reg, sources

    def test_owner_aliases_group_without_mutation(self):
        reg, src = self.inputs(); before=copy.deepcopy((reg,src))
        out=review(reg,src,10)
        self.assertEqual(out['alias_groups'][0]['candidate_ids'],['a','b'])
        self.assertFalse(out['alias_groups'][0]['automatic_merge'])
        self.assertEqual((reg,src),before)
        self.assertIn('HIGH_OBSERVATION_REVIEW_ONLY',out['candidates'][0]['flags'])

    def test_distinct_hypotheses_parameters_units_not_collapsed(self):
        for key,value in [('hypothesis','different'),('horizon_days',8),('target_threshold_pct',3),('target_unit_contract_version','v3')]:
            reg,src=self.inputs(); src['b']['spec'][key]=value
            self.assertEqual(review(reg,src)['alias_groups'],[],key)

    def test_missing_source_and_counts_are_unknown(self):
        reg,src=self.inputs(); del src['a']; del reg['candidates'][1]['forecast_ids']
        out=review(reg,src)
        self.assertEqual(out['candidates'][0]['source_status'],'UNAVAILABLE')
        self.assertEqual(out['candidates'][1]['forecast_count'],'UNKNOWN')
        self.assertEqual(out['alias_groups'],[])

    def test_inconclusive_and_zero_outcomes_separate(self):
        reg,src=self.inputs()
        for row in reg['candidates']: row['state']='MATURED_INCONCLUSIVE';row['matured_outcome_count']=3
        out=review(reg,src)
        self.assertEqual(out['alias_groups'][0]['repeated_matured_inconclusive_ids'],['a','b'])
        self.assertNotIn('ZERO_FORECAST_ZERO_OUTCOME_INCUBATION',out['candidates'][0]['flags'])

    def test_duplicate_registry_ids_preserve_provenance_without_double_count(self):
        reg,src=self.inputs();reg['candidates'].append(reg['candidates'][0])
        out=review(reg,src)
        self.assertEqual(out['candidate_count'],2)
        self.assertEqual(out['source_registry_row_count'],3)
        self.assertEqual(len(out['candidates'][0]['registry_variants']),2)

    def test_deterministic_order(self):
        reg,src=self.inputs();a=review(reg,src);reg['candidates'].reverse()
        b=review(reg,src)
        # Source identity changes with actual source ordering; presentation does not.
        self.assertEqual(a['candidates'],b['candidates']);self.assertEqual(a['alias_groups'],b['alias_groups'])

    def test_no_default_threshold_or_retirement(self):
        reg,src=self.inputs();out=review(reg,src)
        self.assertEqual(out['high_observation_review_min'],'UNSPECIFIED')
        self.assertNotIn('HIGH_OBSERVATION_REVIEW_ONLY',out['candidates'][0]['flags'])
        self.assertNotIn('RETIRE_REVIEW',str(out))

    def test_source_variants_retained_and_conflicts_fail_closed(self):
        reg,src=self.inputs()
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            for n in (1,2):
                (root/f'{n}.json').write_text(json.dumps({'contract':'EXPERIMENT_CANDIDATE_v1','candidate_id':'a','spec':src['a']['spec'],'source':{'run':n}}))
            loaded=load_candidates(root)
            self.assertEqual(len(loaded['a']['source_variants']),2)
            self.assertIsNotNone(loaded['a']['spec'])
            changed=json.loads((root/'2.json').read_text());changed['spec']['hypothesis']='conflicting'
            (root/'2.json').write_text(json.dumps(changed))
            loaded=load_candidates(root);out=review(reg,loaded)
            self.assertEqual(out['candidates'][0]['source_status'],'CONFLICTING_SPECIFICATIONS')
            self.assertEqual(len(out['candidates'][0]['source_provenance']),2)
            self.assertEqual(out['alias_groups'],[])

    def test_owner_wait_and_quarantine_remain_visible(self):
        reg,src=self.inputs()
        reg['candidates'][0]['state']='WAITING_FOR_DATA'
        reg['candidates'][1]['state']='TARGET_UNIT_QUARANTINED'
        out=review(reg,src)
        self.assertEqual(out['candidates'][0]['recommendation'],'WAIT_FOR_DATA')
        self.assertEqual(out['candidates'][1]['recommendation'],'WAIT_FOR_MAPPING')
        self.assertIn('OWNER_QUARANTINE_PRESERVED_NO_REQUALIFICATION',out['candidates'][1]['flags'])

if __name__=='__main__':unittest.main()
