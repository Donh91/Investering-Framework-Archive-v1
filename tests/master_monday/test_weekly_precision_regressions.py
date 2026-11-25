from __future__ import annotations
import importlib.util
import copy
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

preflight = load_module('mm_preflight_v3_precision', ROOT / 'scripts/master_monday/build_preflight_package_v3.py')
publisher = load_module('mm_publisher_precision', ROOT / 'scripts/master_monday/publish_master_monday_outputs.py')

class WeeklyPrecisionRegressionTests(unittest.TestCase):
    def test_labor_day_week_has_four_expected_sessions(self):
        self.assertEqual(
            preflight.expected_nyse_sessions(2026, 37),
            ['2026-09-08', '2026-09-09', '2026-09-10', '2026-09-11'],
        )

    def test_normal_week_has_five_expected_sessions(self):
        sessions = preflight.expected_nyse_sessions(2026, 36)
        self.assertEqual(len(sessions), 5)
        self.assertEqual(sessions[0], '2026-08-31')
        self.assertEqual(sessions[-1], '2026-09-04')

    def test_available_registry_with_incomplete_outcomes_is_not_called_unavailable(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'AVAILABLE',
                'matured_outcome_evidence_available': False,
                'outcome_ingestion_status': 'INCOMPLETE',
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['experiment_registry_status'], 'AVAILABLE')
        self.assertEqual(score['status'], 'INCOMPLETE_EXPERIMENT_OUTCOME_INGESTION')
        self.assertEqual(score['outcome_ingestion_status'], 'INCOMPLETE')

    def test_missing_registry_still_fails_closed(self):
        score = publisher.fallback_scorecard({
            'experiment_learning': {
                'status': 'UNAVAILABLE_REGISTRY_MISSING',
                'matured_outcome_evidence_available': False,
                'new_matured_outcomes': None,
            }
        })
        self.assertEqual(score['status'], 'UNAVAILABLE_EXPERIMENT_REGISTRY')

    def test_delivery_health_is_independent_of_expected_translation_and_scorecard_limits(self):
        c,f,a,r=self.translation_fixture()
        self.assertEqual(publisher.analytical_translation(c,f,a,r,'success')['status'],'DEGRADED')
        for status in ('READY','DEGRADED','BLOCKED'):
            with self.subTest(status=status):
                a['status']=status
                r['output_hash']=publisher.sha(a)
                self.assertEqual(publisher.effective_delivery_status('success',a,r,c,f,True),'READY')
        a['status']='READY'
        a['forecast_candidates'].append(dict(a['forecast_candidates'][0]))
        r.update(output_hash=publisher.sha(a),forecast_candidate_count=2)
        self.assertEqual(publisher.analytical_translation(c,f,a,r,'success')['reason'],'DUPLICATE_OR_CONFLICTING_CANDIDATE')
        self.assertEqual(publisher.effective_delivery_status('success',a,r,c,f,True),'READY')
        for status, output, receipt, freeze, verified in (
            ('failure',a,r,f,True),
            ('success',{'status':'BLOCKED'},r,f,True),
            ('success',a,r,f,False),
            ('success',a,{**r,'output_hash':'0'*64},f,True),
            ('success',a,{**r,'forecast_candidate_count':1},f,True),
            ('success',a,{**r,'status':'FAIL'},f,True),
            ('success',a,r,{**f,'iso_week':46},True),
        ):
            with self.subTest(status=status,receipt=receipt,verified=verified):
                self.assertEqual(publisher.effective_delivery_status(status,output,receipt,c,freeze,verified),'DEGRADED')

    def scorecard_fixture(self):
        rows=[]
        for i,result in enumerate(('HIT','MISS','CENSORED')):
            rows.append({'source_contract':'MATURED_OUTCOME_v3','forecast_id':f'F{i}',
                'forecast_sha256':str(i)*64,'outcome_sha256':str(i+3)*64,'evidence_sha256':str(i+6)*64,
                'source_binding_verification':'CURRENT_FILE_CANONICAL_JSON_SHA256',
                'created_at_utc':'2026-11-20T12:00:00Z',
                'status':'CENSORED' if result=='CENSORED' else 'MATURED',
                'result':None if result=='CENSORED' else result,
                'return_pct':None if result=='CENSORED' else 1.0,
                'reason':'no target' if result=='CENSORED' else None,
                'path':'MUST_NOT_ESCAPE','evidence_path':'MUST_NOT_ESCAPE'})
        context={'contract':'WEEKLY_API_CALIBRATION_CONTEXT_v6','authority':'SHADOW_ONLY',
                 'freeze_sha256':'a'*64,'window_start_utc':'2026-11-16T00:00:00Z',
                 'window_end_utc':'2026-11-23T00:00:00Z','experiment_learning':{
                 'status':'AVAILABLE','authority':'SHADOW_ONLY_NO_AUTOMATIC_PROMOTION',
                 'registry_sha256':'b'*64,'matured_outcome_evidence_available':True,
                 'outcome_ingestion_status':'COMPLETE','outcome_ingestion_diagnostics':[],
                 'new_matured_outcomes':rows}}
        context['context_hash']=publisher.sha(context)
        return context

    def test_owner_outcome_counts_are_restored_but_not_full_readiness(self):
        context=self.scorecard_fixture()
        before=copy.deepcopy(context)
        score=publisher.fallback_scorecard(context)
        counts=score['analysis_layer']['experiment_outcome_counts']
        self.assertEqual(score['status'],'DEGRADED')
        self.assertEqual((counts['outcome_record_count'],counts['matured_outcome_count'],
                          counts['hit_count'],counts['miss_count'],counts['censored_count']),(3,2,1,1,1))
        self.assertNotIn('hit_fraction',counts)
        self.assertIsNone(counts['independent_sample_size'])
        self.assertIsNone(counts['matched_baseline_skill'])
        self.assertFalse(counts['portfolio_action'])
        self.assertNotIn('MUST_NOT_ESCAPE',str(counts))
        self.assertNotIn('return_pct',str(counts))
        self.assertEqual(context,before)
        c,f,a,r=self.translation_fixture()
        typed=publisher.analytical_translation(c,f,a,r,'success')
        self.assertEqual(publisher.effective_delivery_status('success',a,r,c,f,True),'READY')

    def test_scorecard_rejects_rehashed_bad_owner_rows_and_tampered_context(self):
        def reseal(c):
            c.pop('context_hash',None);c['context_hash']=publisher.sha(c)
        for mutate in (
            lambda r:r[0].update(return_pct=True),
            lambda r:r[0].update(result='UNKNOWN'),
            lambda r:r[0].update(created_at_utc='2026-11-23T00:00:00Z'),
            lambda r:r[0].update(source_binding_verification='UNVERIFIED'),
            lambda r:r[0].update(evidence_sha256='bad'),
            lambda r:r[1].update(forecast_id=r[0]['forecast_id']),
            lambda r:r[1].update(outcome_sha256=r[0]['outcome_sha256']),
            lambda r:r[2].update(return_pct=0),
            lambda r:r[2].update(evidence_path=None),
            lambda r:r[2].update(evidence_sha256=None),
        ):
            with self.subTest(mutation=mutate):
                c=self.scorecard_fixture()
                mutate(c['experiment_learning']['new_matured_outcomes'])
                reseal(c)
                self.assertEqual(publisher.fallback_scorecard(c)['analysis_layer'],{})
        c=self.scorecard_fixture()
        c['experiment_learning']['new_matured_outcomes'][0]['result']='MISS'
        self.assertEqual(publisher.fallback_scorecard(c)['analysis_layer'],{})

    def test_censored_only_is_not_a_zero_outcome_success(self):
        c=self.scorecard_fixture()
        c['experiment_learning']['new_matured_outcomes']=c['experiment_learning']['new_matured_outcomes'][2:]
        c['experiment_learning']['new_matured_outcomes'][0].update(evidence_path=None,evidence_sha256=None)
        c.pop('context_hash');c['context_hash']=publisher.sha(c)
        score=publisher.fallback_scorecard(c)
        self.assertEqual(score['status'],'DEGRADED')
        self.assertNotIn('hit_fraction',score['analysis_layer']['experiment_outcome_counts'])
        self.assertEqual(score['matured_outcome_count'],0)

    def translation_fixture(self):
        c=self.scorecard_fixture()
        c.pop('context_hash');c.update(iso_year=2026,iso_week=47);c['context_hash']=publisher.sha(c)
        f={k:c[k] for k in ('iso_year','iso_week','freeze_sha256')}
        a={'status':'READY','summary':'PRIVATE_SUMMARY_NOT_PROJECTED','evidence_for':['e'],
           'evidence_against':[],'uncertainties':[],'hypotheses':[],
           'forecast_candidates':[{'metric_path':'PRIVATE_METRIC_NOT_PROJECTED','direction':'UP',
             'target_mode':'PCT_MOVE','threshold_pct':2.0,'target_value':None,
             'range_low':None,'range_high':None,'horizon_days':7,'rationale':'PRIVATE_RATIONALE'}]}
        r={'contract':'API_AGENT_RECEIPT_v3','task':'WEEKLY_CALIBRATION_SHADOW','status':'PASS',
           'response_id':'fixture','untrusted_input_envelope':True,'context_hash':publisher.sha(c),
           'output_hash':publisher.sha(a),'forecast_candidate_count':1}
        return c,f,a,r

    def test_typed_translation_preserves_shadow_candidate_counts_without_authority(self):
        c,f,a,r=self.translation_fixture()
        t=publisher.analytical_translation(c,f,a,r,'success')
        self.assertEqual(t['candidate_status'],'VALIDATED_UNADMITTED')
        self.assertEqual(t['candidate_horizon_counts'],{'7':1})
        self.assertNotIn('candidate_direction_counts',t)
        self.assertNotIn('spot_candidate_directions',t)
        self.assertEqual(t['status'],'DEGRADED')
        self.assertFalse(t['forecast_authority'])
        self.assertNotIn('PRIVATE_',str(t))
        a['forecast_candidates'][0]['direction']='DOWN';r['output_hash']=publisher.sha(a)
        changed=publisher.analytical_translation(c,f,a,r,'success')
        self.assertEqual(changed['candidate_horizon_counts'],t['candidate_horizon_counts'])
        self.assertNotIn('candidate_direction_counts',changed)
        self.assertNotIn('spot_candidate_directions',changed)

    def test_translation_uses_original_settlement_aliases_without_conflating_mark_and_spot(self):
        c,f,a,r=self.translation_fixture()
        candidate=a['forecast_candidates'][0]
        candidate['metric_path']='market_metrics.spot.BTCUSDT.close'
        a['forecast_candidates'].append({**candidate,'metric_path':'market_metrics.derivatives.BTC-USDT-SWAP.mark_price.mark_price'})
        r.update(output_hash=publisher.sha(a),forecast_candidate_count=2)
        t=publisher.analytical_translation(c,f,a,r,'success')
        self.assertNotIn('spot_candidate_directions',t)
        self.assertEqual(t['candidate_horizon_counts'],{'7':2})
        self.assertEqual(t['candidate_count'],2)
        a['forecast_candidates'].append({**candidate,'metric_path':'spot.BTCUSDT.close'})
        r.update(output_hash=publisher.sha(a),forecast_candidate_count=3)
        self.assertEqual(publisher.analytical_translation(c,f,a,r,'success')['reason'],
                         'DUPLICATE_OR_CONFLICTING_CANDIDATE')

    def test_translation_rejects_receipt_mismatch_and_rehashed_invalid_candidates(self):
        for mutate in (
            lambda c,f,a,r:r.update(task='DAILY_DIRECTOR_SHADOW'),
            lambda c,f,a,r:r.update(context_hash='x'*64),
            lambda c,f,a,r:f.update(iso_week=46),
            lambda c,f,a,r:a.update(operational_translation={'status':'READY'}),
            lambda c,f,a,r:a['forecast_candidates'][0].update(horizon_days=True),
            lambda c,f,a,r:a['forecast_candidates'][0].update(threshold_pct=True),
            lambda c,f,a,r:a['forecast_candidates'][0].update(threshold_pct=float('nan')),
            lambda c,f,a,r:a['forecast_candidates'][0].update(portfolio_action=True),
            lambda c,f,a,r:a['forecast_candidates'].append(dict(a['forecast_candidates'][0])),
        ):
            with self.subTest(mutation=mutate):
                c,f,a,r=self.translation_fixture()
                mutate(c,f,a,r)
                r['output_hash']=publisher.sha(a)
                r['forecast_candidate_count']=len(a['forecast_candidates'])
                t=publisher.analytical_translation(c,f,a,r,'success')
                self.assertEqual(t['candidate_status'],'UNAVAILABLE')
                self.assertEqual(t['candidate_horizon_counts'],{})
        c,f,a,r=self.translation_fixture()
        a['summary']='mutated without receipt'
        self.assertEqual(publisher.analytical_translation(c,f,a,r,'success')['reason'],'GATEWAY_RECEIPT_MISMATCH')
        self.assertEqual(publisher.analytical_translation(c,f,a,r,'failure')['reason'],'API_FAILED')

if __name__ == '__main__':
    unittest.main()
