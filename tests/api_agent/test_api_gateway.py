import json
import os
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.api_agent.api_gateway import blocked_output, build_request, estimate_cost, extract_output, load_registry, validate_output
from scripts.api_agent.advance_deep_research_queue import build_task_packet, retained_providers, select_next
from scripts.api_agent.advance_mcp_connection_scorecard import apply_evaluation
from scripts.api_agent.evaluate_mcp_connection_receipt import classify, score_receipt
from scripts.api_agent.mcp_research_gateway import build_probe_payload, build_research_payload, load_contract, resolve_headers, select_allowed_tools
from scripts.api_agent.validate_coingecko_mcp_boundary import validate_boundary
from scripts.api_agent.validate_deep_research_queue import validate_queue
from scripts.api_agent.validate_mcp_connection_program import validate_program

REGISTRY = Path('research/api_agent/API_TASK_REGISTRY_v1.json')


def valid_output():
    return {'status':'READY','summary':'x','evidence_for':[],'evidence_against':[],'uncertainties':[],'hypotheses':[],'forecast_candidates':[]}


def directional_pct():
    return {'metric_path':'market_metrics.BTC.close','direction':'UP','target_mode':'PCT_MOVE','threshold_pct':1.0,'target_value':None,'range_low':None,'range_high':None,'horizon_days':7,'rationale':'test'}


def good_mcp_receipt(provider='Dune'):
    return {
        'contract':'MCP_CONNECTION_PILOT_RECEIPT_v1','provider':provider,'provider_contract':'x','stage':'BOUNDED_RESEARCH_CHALLENGE','status':'PASS','created_at_utc':'2026-08-11T18:00:00Z',
        'official_server_verified':True,'auth_secret_present':True,'auth_secret_persisted':False,'tool_discovery_status':'PASS','discovered_tool_count':5,'allowed_read_only_tool_count':3,
        'mcp_call_count':3,'successful_mcp_call_count':3,'failed_mcp_call_count':0,'mutating_tool_called':False,'provenance_complete':True,
        'research_questions_total':3,'research_questions_answered':3,'unique_value_items':4,'overlap_items':1,'crosscheck_status':'PASS','repeat_consistency_status':'PASS',
        'manual_intervention_count':0,'provider_cost_status':'WITHIN_BUDGET','production_dependency':False,'canonical_owner_replaced':False,'hard_blockers':[],
        'authority':{'framework_state_change':False,'portfolio_action':False,'market_rule_change':False,'canonical_promotion':False}
    }


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
    def test_mcp_connection_program_boundary(self):
        self.assertEqual(validate_program(Path('.')), [])
    def test_dune_tool_filter_requires_read_only_and_denies_mutating(self):
        contract=json.loads(Path('research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json').read_text())
        inventory=[
            {'name':'execute_query','description':'Run a read-only query','annotations':{'readOnlyHint':True}},
            {'name':'create_query','description':'Create query','annotations':{'readOnlyHint':False}},
            {'name':'dashboard_get','description':'Read dashboard','annotations':{'readOnlyHint':True}},
            {'name':'unknown','description':'No annotation','annotations':{}},
        ]
        self.assertEqual(select_allowed_tools(contract,inventory),['execute_query'])
    def test_mcp_probe_never_executes_provider_tool(self):
        contract=load_contract(Path('research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json'))
        payload=build_probe_payload(contract,{'x-dune-api-key':'secret'})
        self.assertEqual(payload['tool_choice'],'none');self.assertEqual(payload['tools'][0]['require_approval'],'always');self.assertFalse(payload['store'])
    def test_mcp_research_payload_uses_explicit_allowlist(self):
        contract=load_contract(Path('research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json'))
        payload=build_research_payload(contract,{'x-dune-api-key':'secret'},['execute_query'],'test')
        self.assertEqual(payload['tools'][0]['allowed_tools'],['execute_query']);self.assertEqual(payload['tools'][0]['require_approval'],'never');self.assertEqual(payload['tool_choice'],'required');self.assertIn('Do not give portfolio actions',payload['instructions'])
    def test_mcp_auth_secret_loaded_from_environment_not_contract(self):
        contract=load_contract(Path('research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json'))
        with patch.dict(os.environ,{'DUNE_API_KEY':'abc'},clear=False):headers,present=resolve_headers(contract)
        self.assertTrue(present);self.assertEqual(headers,{'x-dune-api-key':'abc'});self.assertNotIn('abc',Path('research/api_agent/mcp/DUNE_MCP_RESEARCH_RECOVERY_v1.json').read_text())
    def test_good_mcp_receipt_scores_keep_for_dune(self):
        scored=score_receipt(good_mcp_receipt());self.assertGreaterEqual(scored['score'],80);self.assertEqual(scored['hard_blockers'],[]);self.assertEqual(classify(scored['score'],scored['hard_blockers'],scored['shape_errors'],'RESEARCH_ACTIVE'),'KEEP_RESEARCH_ACTIVE')
    def test_mcp_mutating_call_is_killed(self):
        receipt=good_mcp_receipt();receipt['mutating_tool_called']=True;scored=score_receipt(receipt);self.assertIn('MUTATING_TOOL_CALLED',scored['hard_blockers']);self.assertEqual(classify(scored['score'],scored['hard_blockers'],scored['shape_errors'],'RESEARCH_ACTIVE'),'KILL')
    def test_ai_cannot_exceed_lunarcrush_ceiling(self):
        program=json.loads(Path('research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json').read_text());scorecard=json.loads(Path('research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json').read_text());evaluation={'provider':'LunarCrush','deterministic_verdict':'SHADOW_OBSERVATION','deterministic_score':85,'ai_red_team_required':True,'promotion_ceiling':'SHADOW_OBSERVATION'}
        with self.assertRaisesRegex(ValueError,'ai_verdict_exceeds_promotion_ceiling'):apply_evaluation(program,scorecard,evaluation,'KEEP_RESEARCH_ACTIVE')
    def test_terminal_dune_verdict_advances_lunarcrush(self):
        program=json.loads(Path('research/api_agent/mcp/MCP_CONNECTION_EVALUATION_PROGRAM_v1.json').read_text());scorecard=json.loads(Path('research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json').read_text());evaluation={'provider':'Dune','deterministic_verdict':'KEEP_RESEARCH_ACTIVE','deterministic_score':88,'ai_red_team_required':True,'promotion_ceiling':'RESEARCH_ACTIVE'};updated=apply_evaluation(program,scorecard,evaluation,'KEEP_RESEARCH_ACTIVE');self.assertEqual(updated['active_provider'],'LunarCrush');lunar=next(r for r in updated['providers'] if r['provider']=='LunarCrush');self.assertEqual(lunar['state'],'READY_FOR_TOOL_DISCOVERY')
    def test_binance_runner_refuses_unverified_surface(self):
        with self.assertRaisesRegex(ValueError,'provider_not_executable'):load_contract(Path('research/api_agent/mcp/BINANCE_AGENT_NATIVE_RESEARCH_v1.json'))
    def test_deep_research_queue_boundary(self):
        self.assertEqual(validate_queue(Path('.')), [])
    def test_deep_research_current_provider_gate_is_coingecko_only(self):
        scorecard=json.loads(Path('research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json').read_text())
        self.assertEqual(retained_providers(scorecard), {'CoinGecko'})
    def test_deep_research_initial_task_is_cross_horizon_baseline(self):
        queue=json.loads(Path('research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json').read_text());state=json.loads(Path('research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json').read_text());scorecard=json.loads(Path('research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json').read_text());updated,item=select_next(queue,state,scorecard);self.assertEqual(item['id'],'DRQ-001');packet=build_task_packet(item,updated);self.assertEqual(packet['output_authority'],'RESEARCH_EVIDENCE_ONLY');self.assertIn('CROSS_HORIZON',packet['horizons'])
    def test_deep_research_skips_blocked_provider_dependency(self):
        queue=json.loads(Path('research/api_agent/deep_research/DEEP_RESEARCH_QUEUE_v1.json').read_text());state=json.loads(Path('research/api_agent/deep_research/LATEST_DEEP_RESEARCH_STATE.json').read_text());scorecard=json.loads(Path('research/api_agent/mcp/evaluations/LATEST_MCP_CONNECTION_SCORECARD.json').read_text());state['active_research_id']=None;state['item_states']['DRQ-001']['state']='COMPLETE';updated,item=select_next(queue,state,scorecard);self.assertEqual(item['id'],'DRQ-006');self.assertEqual(updated['item_states']['DRQ-002']['state'],'WAIT_PROVIDER')


if __name__=='__main__':unittest.main()
