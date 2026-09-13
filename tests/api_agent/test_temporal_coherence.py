import copy
import unittest
from datetime import datetime,timedelta,timezone
from scripts.api_agent.augment_director_context_v2 import temporal_coherence,build_horizon,HORIZONS_HOURS

class TemporalTests(unittest.TestCase):
    def context(self):
        cutoff=datetime(2026,9,12,12,tzinfo=timezone.utc)
        ts=cutoff.isoformat()
        seq={'cutoff_utc':ts,'horizons':{str(h):{'anchor_timestamp_utc':(cutoff-timedelta(hours=h)).isoformat(),'actual_span_hours':h} for h in HORIZONS_HOURS}}
        for k in ('rich_breadth','latest_settled_etf','stablecoin_liquidity'):seq[k]={'retrieved_at_utc':ts}
        seq['pullback_forensics']={'observed_at_utc':ts}
        return {'latest_capture':{'captured_at_utc':ts},'previous_capture':{'captured_at_utc':(cutoff-timedelta(hours=24)).isoformat()},'delta_status':'DELTA_READY','api_intelligence_v2':seq}

    def test_valid_exact_spread_and_no_mutation(self):
        c=self.context();old=copy.deepcopy(c);r=temporal_coherence(c)
        self.assertEqual(r['status'],'WITHIN_EXISTING_CONTRACTS')
        self.assertEqual(r['owner_timestamp_age_spread_hours'],24)
        self.assertEqual(c,old)

    def test_unknown_and_naive_not_stale_or_local_timezone(self):
        for value in (None,'bad','2026-09-12T10:00:00'):
            c=self.context();c['api_intelligence_v2']['rich_breadth']['retrieved_at_utc']=value
            r=temporal_coherence(c)
            self.assertEqual(r['status'],'PARTIAL_UNKNOWN')
            self.assertEqual(r['owners']['rich_breadth']['timestamp_status'],'UNKNOWN')
            self.assertEqual(r['violations'],[])

    def test_existing_predecessor_gate_reused(self):
        c=self.context();c['delta_status']='DELTA_DEGRADED_STALE_PREDECESSOR'
        self.assertEqual(temporal_coherence(c)['violations'][0]['family'],'previous_capture')

    def test_existing_anchor_tolerance_boundary(self):
        c=self.context();h=c['api_intelligence_v2']['horizons']['1']
        h['anchor_timestamp_utc']='2026-09-12T09:45:00Z'
        self.assertEqual(temporal_coherence(c)['horizons']['1']['status'],'WITHIN_EXISTING_CONTRACTS')
        h['anchor_timestamp_utc']='2026-09-12T09:44:59Z'
        self.assertEqual(temporal_coherence(c)['horizons']['1']['status'],'EXISTING_CONTRACT_VIOLATION')

    def test_unavailable_anchor_preserves_existing_reason(self):
        c=self.context();c['api_intelligence_v2']['horizons']['4']={'status':'UNAVAILABLE','reason':'NO_ANCHOR_WITHIN_TOLERANCE'}
        r=temporal_coherence(c)
        self.assertEqual(r['horizons']['4']['status'],'EXISTING_CONTRACT_VIOLATION')
        self.assertEqual(r['violations'][0]['horizon_hours'],4)

    def test_after_cutoff_is_visible_not_dropped_or_new_freshness_gate(self):
        c=self.context();c['api_intelligence_v2']['rich_breadth']['retrieved_at_utc']='2026-09-12T13:00:00Z'
        report=temporal_coherence(c)
        self.assertEqual(report['status'],'AFTER_CUTOFF_TIMESTAMPS_PRESENT')
        r=report['owners']['rich_breadth']
        self.assertEqual(r['age_hours'],-1)
        self.assertEqual(r['timestamp_status'],'AFTER_CUTOFF')
        self.assertIn('NOT_ASSESSED',r['freshness_verdict'])

    def test_existing_horizon_output_unchanged_by_tolerance_extraction(self):
        cutoff=datetime(2026,9,12,12,tzinfo=timezone.utc)
        rows=[{'timestamp':cutoff-timedelta(hours=h),'btc_close':100.0+h}for h in range(80,-1,-1)]
        for hours in HORIZONS_HOURS:
            r=build_horizon(rows,cutoff,hours)
            self.assertEqual(r['actual_span_hours'],hours)
            self.assertEqual(r['status'],'READY')

if __name__=='__main__':unittest.main()
