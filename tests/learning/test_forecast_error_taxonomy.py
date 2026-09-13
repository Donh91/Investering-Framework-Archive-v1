import copy
import json
from pathlib import Path
import tempfile
import unittest
from scripts.learning.forecast_error_taxonomy import explain, build_report, owner


class TaxonomyTests(unittest.TestCase):
    def pair(self, end=102, direction='UP'):
        f = dict(contract='FROZEN_FORECAST_v1', forecast_id='F1',
                 unit_contract_version='FORECAST_TARGET_UNITS_v2', direction=direction,
                 frozen_at_utc='2026-01-01T00:00:00Z', outcome_due_utc='2026-01-02T00:00:00Z',
                 start_value=100, threshold_pct=5, metric_path='price')
        o = dict(contract='MATURED_OUTCOME_v3', forecast_id='F1', forecast_sha256=owner.sha(f),
                 status='MATURED', created_at_utc='2026-01-02T00:00:00Z', result=owner.classify(f, 100, end), start_value=100, end_value=end)
        return f, o

    def test_direction_vs_magnitude_both_signs_and_no_mutation(self):
        for direction, good, bad in [('UP', 102, 98), ('DOWN', 98, 102)]:
            for end, expected in [(good, 'MAGNITUDE'), (bad, 'DIRECTION')]:
                f, o = self.pair(end, direction); old = copy.deepcopy((f, o))
                r = explain(f, o)
                self.assertEqual(r['PRIMARY_FAILURE_CLASS'], expected)
                self.assertEqual(r['TARGET_RESULT'], 'MISS')
                self.assertEqual((f, o), old)

    def test_hit_and_flat(self):
        for end, magnitude in [(110, 'SUFFICIENT'), (100, 'INSUFFICIENT')]:
            r = explain(*self.pair(end))
            self.assertEqual(r['MAGNITUDE'], magnitude)
        self.assertEqual(explain(*self.pair(100))['DIRECTION'], 'NOT_EVALUABLE')

    def test_censor_is_never_prediction_failure(self):
        f, o = self.pair(); o['status'] = 'CENSORED'
        r = explain(f, o)
        self.assertEqual(r['TARGET_RESULT'], 'CENSORED')
        self.assertEqual(r['PRIMARY_FAILURE_CLASS'], 'NOT_EVALUABLE')

    def test_binding_and_result_conflicts(self):
        for field, value in [('forecast_sha256', 'wrong'), ('result', 'HIT'), ('end_value', float('nan'))]:
            f, o = self.pair(); o[field] = value
            self.assertEqual(explain(f, o)['DIRECTION'], 'NOT_EVALUABLE')

    def test_missing_and_mismatched_ids_are_not_evaluable(self):
        for value in (None, '', 'OTHER'):
            f, o = self.pair(); o['forecast_id'] = value
            if value in (None, ''):
                f['forecast_id'] = value; o['forecast_sha256'] = owner.sha(f)
            self.assertEqual(explain(f, o)['reason'], 'FORECAST_BINDING_UNAVAILABLE')

    def test_early_missing_and_naive_outcomes_are_not_evaluable(self):
        for value in ('2025-12-31T00:00:00Z', '2026-01-01T12:00:00Z',
                      '2026-01-02T00:00:00', None, 'bad'):
            f, o = self.pair(); o['created_at_utc'] = value
            r = explain(f, o)
            self.assertEqual(r['reason'], 'CHRONOLOGY_UNAVAILABLE_OR_INVALID')
            self.assertEqual(r['PRIMARY_FAILURE_CLASS'], 'NOT_EVALUABLE')
            self.assertEqual(r['TARGET_RESULT'], 'MISS')

    def test_no_narrative_timing_or_sequence(self):
        f, o = self.pair(); o['narrative'] = 'early wrong phase and sequence'
        r = explain(f, o)
        for key in ('TIMING', 'SEQUENCE', 'STATE_OR_PHASE', 'ACTION_TRANSLATION'):
            self.assertEqual(r[key], 'NOT_EVALUABLE')
        self.assertIsNone(r['scientific_score_eligible'])

    def test_cli_immutable_output_and_source_protection(self):
        import subprocess, sys
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fr=root/'f'; out=root/'o'; fr.mkdir(); out.mkdir()
            f,o=self.pair()
            (fr/'f.json').write_text(json.dumps(f)); (out/'o.json').write_text(json.dumps(o))
            cmd=[sys.executable,'-B','-m','scripts.learning.forecast_error_taxonomy',
                 '--forecast-root',str(fr),'--outcome-root',str(out),'--output']
            result=root/'report.json'
            for _ in range(2):
                self.assertEqual(subprocess.run(cmd+[str(result)],capture_output=True).returncode,0)
            before=result.read_bytes(); o['status']='CENSORED'; (out/'o.json').write_text(json.dumps(o))
            self.assertNotEqual(subprocess.run(cmd+[str(result)],capture_output=True).returncode,0)
            self.assertEqual(result.read_bytes(),before)
            self.assertNotEqual(subprocess.run(cmd+[str(fr/'bad.json')],capture_output=True).returncode,0)
            self.assertFalse((fr/'bad.json').exists())

    def test_malformed_evidence_fails_visibly(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fr=root/'f'; out=root/'o'; fr.mkdir(); out.mkdir()
            (out/'bad.json').write_text('{')
            with self.assertRaises(json.JSONDecodeError): build_report(fr,out)

    def test_duplicate_ids_bind_exact_version_and_keep_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); fr=root/'f'; out=root/'o'; fr.mkdir(); out.mkdir()
            f,o=self.pair(); other=dict(f,threshold_pct=10)
            for name,value in [('a',f),('b',other)]:
                (fr/(name+'.json')).write_text(json.dumps(value))
            (out/'o.json').write_text(json.dumps(o))
            r=build_report(fr,out)
            self.assertEqual(len(r['source_manifest']),3)
            self.assertEqual(r['rows'][0]['PRIMARY_FAILURE_CLASS'],'MAGNITUDE')
            self.assertEqual(r['original_result_counts'],{'MISS':1})
            self.assertEqual(r,build_report(fr,out))

if __name__ == '__main__': unittest.main()
