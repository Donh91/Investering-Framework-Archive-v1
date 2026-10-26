import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.daily_capture.build_weekly_calibration import hourly_sequence_summary, weekly_spot_flow
from scripts.api_agent.build_weekly_calibration_context import load_weekly_owned_context


class WeeklySpotFlowReadbackTests(unittest.TestCase):
    def rows(self):
        rows = []
        for hour, total, buy in ((0, 100, 90), (1, 900, 90)):
            row = {'timestamp_utc': f'2026-10-19T{hour:02d}:00:00Z', 'spot_status': 'PASS'}
            for asset in ('btc', 'eth'):
                row.update({f'{asset}_quote_volume': str(total),
                            f'{asset}_taker_buy_quote_volume': str(buy),
                            f'{asset}_taker_sell_quote_volume': str(total-buy),
                            f'{asset}_taker_buy_quote_share': str(buy/total)})
            rows.append(row)
        return rows

    def test_weighted_flow_survives_existing_weekly_context_handoff(self):
        sequence = hourly_sequence_summary(self.rows())
        flow = sequence['spot_flow_readback']['BTC']
        self.assertEqual(flow['status'], 'COMPLETE_FOR_OBSERVED_ROWS')
        self.assertEqual(flow['taker_buy_quote_share_weighted'], .18)
        self.assertEqual(flow['net_aggressive_quote_flow_sum'], -640)
        self.assertEqual(flow['quote_unit'], 'USDT')
        self.assertFalse(flow['market_interpretation'])
        # Two valid rows are never asserted to be a complete 168-hour week.
        self.assertEqual(sequence['hourly_coverage_pct'], 1.19)
        with tempfile.TemporaryDirectory() as tmp:
            capture = Path(tmp)
            package = capture/'pack.json'
            package.write_text(json.dumps({'hourly_sequence': sequence}))
            pointer = capture/'LATEST.json'
            pointer.write_text(json.dumps({'path': 'pack.json'}))
            preflight = capture/'preflight.json'
            preflight.write_text('{}')
            context = load_weekly_owned_context(pointer,capture,preflight)
            self.assertEqual(context['weekly_capture_pack']['hourly_sequence']['spot_flow_readback'], sequence['spot_flow_readback'])

    def test_unusable_rows_never_produce_partial_full_window_total(self):
        for field, value in (('btc_quote_volume','NaN'), ('btc_quote_volume', '0'),
                             ('btc_taker_buy_quote_volume','101'), ('btc_taker_sell_quote_volume', '-1'),
                             ('btc_taker_buy_quote_share', '.1'), ('btc_taker_buy_quote_share',True),
                             ('btc_taker_buy_quote_volume',''), ('spot_status','UNAVAILABLE')):
            with self.subTest(field=field,value=value):
                rows=self.rows();rows[0][field]=value
                flow=weekly_spot_flow(rows,'btc')
                self.assertEqual(flow['status'],'UNAVAILABLE_INVALID_OR_MISSING_FLOW')
                self.assertIsNone(flow['net_aggressive_quote_flow_sum'])
                self.assertIsNone(flow['taker_buy_quote_share_weighted'])

    def test_identity_and_evidence_digest(self):
        rows=self.rows();original=copy.deepcopy(rows)
        first=weekly_spot_flow(rows,'btc')
        self.assertEqual(rows,original)
        for stamp in ('2026-10-19T00:00:00Z','2026-10-26T01:00:00Z','2026-10-19T01:30:00Z','invalid'):
            changed=copy.deepcopy(rows);changed[1]['timestamp_utc']=stamp
            self.assertIsNone(weekly_spot_flow(changed,'btc')['net_aggressive_quote_flow_sum'])
        changed=copy.deepcopy(rows);changed[0]['btc_taker_buy_quote_share']='.1'
        self.assertNotEqual(weekly_spot_flow(changed,'btc')['source_rows_sha256'],first['source_rows_sha256'])
        self.assertIsNone(weekly_spot_flow([],'btc')['net_aggressive_quote_flow_sum'])

if __name__ == '__main__':
    unittest.main()
