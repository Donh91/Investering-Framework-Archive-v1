import json
import unittest
from pathlib import Path

from scripts.api_agent.api_gateway import blocked_output, build_request, estimate_cost, extract_output, load_registry, validate_output
from scripts.api_agent.validate_coingecko_mcp_boundary import validate_boundary

REGISTRY = Path('research/api_agent/API_TASK_REGISTRY_v1.json')


def valid_output():
    return {'status':'READY','summary':'x','evidence_for':[],'evidence_against':[],'uncertainties':[],'hypotheses':[],'forecast_candidates':[]}


def directional_pct():
    return {'metric_path':'market_metrics.BTC.close','direction':'UP','target_mode':'PCT_MOVE','threshold_pct':1.0,'target_value':None,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'test'}


class ApiGatewayTests(unittest.TestCase):
    def test_registry_is_shadow_only(self):
        data=load_registry(REGISTRY);self.assertEqual(data['status'],'ACTIVE_SHADOW_ONLY');self.assertFalse(data['authority']['portfolio_action']);self.assertFalse(data['authority']['framework_state_change'])
    def test_daily_output_budget_can_hold_strict_schema(self):
        data=load_registry(REGISTRY);self.assertGreaterEqual(data['tasks']['DAILY_DIRECTOR_SHADOW']['max_output_tokens'],2000)
    def test_cost_estimate(self):
        self.assertEqual(estimate_cost('gpt-5.6-luna',1000000,1000000),7.0);self.assertEqual(estimate_cost('gpt-5.6-terra',1000000,1000000),17.5)
    def test_valid_output(self):validate_output(valid_output())
    def test_valid_forecast_candidate_pct_move(self):
        value=valid_output();value['forecast_candidates']=[directional_pct()];validate_output(value)
    def test_valid_forecast_candidate_absolute_target(self):
        value=valid_output();candidate=directional_pct();candidate.update(target_mode='ABSOLUTE_VALUE',threshold_pct=None,target_value=63000.0);value['forecast_candidates']=[candidate];validate_output(value)
    def test_valid_forecast_candidate_absolute_range(self):
        value=valid_output();value['forecast_candidates']=[{'metric_path':'market_metrics.BTC.close','direction':'RANGE','target_mode':'ABSOLUTE_RANGE','threshold_pct':None,'target_value':None,'range_low':63000.0,'range_high':65000.0,'horizon_days':1,'rationale':'test'}];validate_output(value)
    def test_legacy_ambiguous_threshold_is_rejected(self):
        value=valid_output();value['forecast_candidates']=[{'metric_path':'market_metrics.BTC.close','direction':'UP','threshold':64000.0,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'legacy ambiguous'}]
        with self.assertRaises(ValueError):validate_output(value)
    def test_conflicting_target_fields_are_rejected(self):
        value=valid_output();candidate=directional_pct();candidate['target_value']=65000.0;value['forecast_candidates']=[candidate]
        with self.assertRaisesRegex(ValueError,'directional_pct_fields_conflict'):validate_output(value)
    def test_forbidden_authority_rejected(self):
        value=valid_output();value['portfolio_action']='BUY'
        with self.assertRaises(ValueError):validate_output(value)
    def test_request_is_store_false_and_current_turn(self):
        data=load_registry(REGISTRY);cfg=data['tasks']['DAILY_DIRECTOR_SHADOW'];request=build_request('DAILY_DIRECTOR_SHADOW',cfg,'test',{'a':1});self.assertFalse(request['store']);self.assertEqual(request['reasoning']['context'],'current_turn');self.assertEqual(request['model'],'gpt-5.6-luna');item=request['text']['format']['schema']['properties']['forecast_candidates']['items'];self.assertIn('target_mode',item['properties']);self.assertNotIn('threshold',item['properties']);self.assertIn('Never encode an absolute target in a percent field',request['instructions'])
    def test_incomplete_response_is_rejected_before_json_parse(self):
        with self.assertRaisesRegex(ValueError,'response_incomplete'):extract_output({'status':'incomplete','incomplete_details':{'reason':'max_output_tokens'},'output_text':'{"status":'})
    def test_unterminated_json_is_rejected(self):
        with self.assertRaises(json.JSONDecodeError):extract_output({'output_text':'{"status":"READY"'})
    def test_failure_marker_is_valid_but_has_no_forecasts(self):
        value=blocked_output('API_OUTPUT_INVALID_AFTER_BOUNDED_RETRY');validate_output(value);self.assertEqual(value['status'],'BLOCKED');self.assertEqual(value['forecast_candidates'],[])
    def test_coingecko_mcp_research_boundary(self):
        self.assertEqual(validate_boundary(Path('.')), [])


if __name__=='__main__':unittest.main()
