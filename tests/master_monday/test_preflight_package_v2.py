from __future__ import annotations
import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SCRIPT=ROOT/'scripts/master_monday/build_preflight_package_v2.py'
REG=ROOT/'research/master_monday_preflight/MASTER_MONDAY_ACTION_REGISTRY_v1.json'
PRED=ROOT/'research/master_monday_preflight/CANONICAL_PREDECESSOR_REGISTRY_v1.json'

def run_builder(root:Path):
    out=root/'out.json'
    p=subprocess.run(['python',str(SCRIPT),'--repo-root',str(root),'--registry',str(REG),'--predecessor-registry',str(PRED),'--output',str(out)],capture_output=True,text=True)
    if p.returncode: raise AssertionError(p.stderr)
    return json.loads(out.read_text())

def owner(owner_id,data): return {'owner_id':owner_id,'status':'PASS','data':data}

class PreflightV2Tests(unittest.TestCase):
    def test_empty_package_has_complete_missing_ledger(self):
        with tempfile.TemporaryDirectory() as d:
            v=run_builder(Path(d))
            self.assertEqual(v['packet']['status'],'PARTIAL_WITH_EXPLICIT_GAPS')
            self.assertEqual(v['meta']['attempted_core_actions'],60)
            self.assertEqual(len(v['source_ledgers']),60)
            nonpass=[r for r in v['source_ledgers'] if r['status']!='PASS']
            self.assertEqual(len(v['missing']),len(nonpass))

    def test_breadth_owner_is_not_blanket_pass(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); p=r/'03_DAILY_CAPTURE_LOGS/captures/x'; p.mkdir(parents=True)
            cap={'captured_at_utc':'2026-08-02T20:00:00Z','owners':[owner('top100_breadth',{'advance_ratio':0.51})]}
            (p/'capture.json').write_text(json.dumps(cap))
            v=run_builder(r)
            rows={x['action_id']:x for x in v['source_ledgers']}
            self.assertEqual(rows['A20']['status'],'PASS')
            self.assertEqual(rows['A21']['status'],'UNAVAILABLE')
            self.assertEqual(rows['A22']['status'],'UNAVAILABLE')

    def test_full_fixture_can_reach_full(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d); p=r/'03_DAILY_CAPTURE_LOGS/captures/x'; p.mkdir(parents=True)
            spot={'BTCUSDT':1,'ETHUSDT':1,'ETHBTC':1,'order_book':{},'ticker_24h':{},'server_time':1}
            breadth={'advance_ratio':.6,'membership_hash':'h','constituent_sidecar':[1],'exclusion_sidecar':[],'median_return_24h_pct':1,'gates':{},'scored_gate_permission':'AUTHORIZED'}
            deriv={'BTC':{'funding':1},'ETH':{'funding':1},'funding_history':[],'oi_anchors':{},'global_long_short':1,'top_account_long_short':1,'top_position_long_short':1,'taker_flow':{},'multiwindow_price':{},'close_location':1}
            okx={'BTC':{'ticker':{}},'ETH':{'ticker':{}},'funding':{},'open_interest':{},'basis_divergence':{}}
            cap={'captured_at_utc':'2026-08-02T20:00:00Z','freeze_count':1,'settled_sessions':{'BTCUSDT':{},'ETHUSDT':{},'ETHBTC':{},'threshold_tests':{},'session_type':'COPENHAGEN'},'auxiliary_owners':{'stablecoins':{'global':1,'chains':{},'method_compatible_delta':0},'chain_tvl':{},'dex_qa':{'pools':[],'anomalies':[]}},'owners':[owner('binance_spot',spot),owner('top100_breadth',breadth),owner('binance_microstructure',deriv),owner('okx_swap',okx),owner('cfgi_sentiment',{'MARKET':{'score':50},'BTC':{'score':50},'ETH':{'score':50}}),owner('fred_macro',{k:{'latest':1} for k in ('DGS2','DGS10','VIXCLS','DTWEXBGS')})]}
            (p/'capture.json').write_text(json.dumps(cap))
            wp=r/'03_DAILY_CAPTURE_LOGS/weekly_close'; wp.mkdir(parents=True)
            pkg={'daily_ranges':{'BTCUSDT':[1],'ETHUSDT':[1]},'weekly_daily_tieout':{'BTCUSDT':'PASS','ETHUSDT':'PASS'},'gap_duplicate_qa':{}}
            (wp/'week.json').write_text(json.dumps(pkg)); (wp/'LATEST_WEEKLY_MARKET_CLOSE.json').write_text(json.dumps({'path':'03_DAILY_CAPTURE_LOGS/weekly_close/week.json'}))
            ep=r/'research/etf_owner/x'; ep.mkdir(parents=True)
            etf={'retrieved_at_utc':'2026-08-02T21:00:00Z','status':'PASS','assets':{'BTC':{'sessions':[1]},'ETH':{'sessions':[1]}},'rolling_sums':{},'stale_no_zero_protection':True}
            (ep/'etf.json').write_text(json.dumps(etf))
            v=run_builder(r)
            self.assertEqual(v['packet']['status'],'FULL_MASTER_MONDAY_INPUT')
            self.assertTrue(all(v['quality']['required_capabilities'].values()))
            self.assertEqual(v['quality']['UNAVAILABLE'],0)

if __name__=='__main__': unittest.main()
