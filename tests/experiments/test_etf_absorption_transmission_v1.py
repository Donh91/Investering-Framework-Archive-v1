import hashlib
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.experiments import etf_absorption_transmission_v1 as etf


def owner(session, known_at, btc=100.0, eth=50.0, *, verified=True):
    rows = [
        {"asset":"BTC","date":session,"fund_headers":["A"],"fund_values":[btc],"reported_total":btc,"calculated_total":btc,"total_parity":True,"session_final":True},
        {"asset":"ETH","date":session,"fund_headers":["A"],"fund_values":[eth],"reported_total":eth,"calculated_total":eth,"total_parity":True,"session_final":True},
    ]
    sig = hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "contract":"DAILY_SETTLED_ETF_CALIBRATION_v1",
        "authority":"SHADOW_CALIBRATION_INPUT_ONLY",
        "session_date":session,
        "retrieved_at_utc":known_at,
        "verification":{
            "retrieval_count":2 if verified else 1,
            "minimum_separation_seconds":60,
            "rows_identical_across_retrievals":True,
            "all_fund_cells_known":True,
            "total_parity_required":True,
            "source":"FARSIDE_CANONICAL_TABLES",
        },
        "rows":rows,
        "canonical_data_ping":False,
        "framework_state_change":False,
        "portfolio_action":False,
        "row_signature_sha256":sig,
    }


def current_owner(session='2026-08-07', known_at='2026-08-08T06:06:00Z', btc=100, eth=50):
    value = owner(session, known_at, btc, eth)
    value['contract'] = 'DAILY_SETTLED_ETF_CALIBRATION_v2'
    value['verification'].update(source='FARSIDE_CANONICAL_ALL_DATA_TABLES',
        unknown_cells_imputed=False, unknown_cells_fully_accounted_by_reported_total=True)
    for row in value['rows']:
        row.update(unknown_fund_cells=[], unknown_fund_cell_count=0,
                   unknown_cells_fully_accounted_by_reported_total=True)
    value['row_signature_sha256'] = etf.rows_signature(value['rows'])
    return value


class TestEtfOwnerAdapter(unittest.TestCase):
    def write(self, root, name, obj):
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj))
        return path

    def test_future_record_is_never_visible(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"future.json",owner("2026-08-07","2026-08-10T08:06:00Z"))
            result=etf.asof_join(etf.load_owner_records(root), datetime(2026,8,10,8,5,tzinfo=timezone.utc))
            self.assertEqual(result["status"],"UNAVAILABLE")

    def test_current_v2_owner_is_available_with_unchanged_research_authority(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            p = self.write(root, 'current.json', current_owner())
            before = p.read_bytes()
            records = etf.load_owner_records(root)
            self.assertEqual(len(records), 1)
            result = etf.asof_join(records, datetime(2026, 8, 9, tzinfo=timezone.utc))
            self.assertEqual(result['source_contract'], 'DAILY_SETTLED_ETF_CALIBRATION_v2')
            self.assertEqual(result['raw_reported_totals'], {'BTC': 100, 'ETH': 50})
            self.assertEqual(result['authority'], 'SHADOW_RESEARCH_INPUT_ONLY')
            self.assertFalse(result['market_interpretation'])
            self.assertEqual(p.read_bytes(), before)

    def test_late_older_session_revision_cannot_displace_newer_session(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, 'new-session.json', current_owner('2026-08-10', '2026-08-11T06:00:00Z', 120, 60))
            self.write(root, 'late-old-revision.json', current_owner('2026-08-07', '2026-08-12T06:00:00Z', 999, 999))
            result = etf.asof_join(etf.load_owner_records(root), datetime(2026, 8, 13, tzinfo=timezone.utc))
            self.assertEqual(result['session_date'], '2026-08-10')
            self.assertEqual(result['raw_reported_totals']['BTC'], 120)

    def test_conflicting_same_time_revisions_are_not_resolved_by_filename(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, 'a.json', current_owner(btc=100))
            self.write(root, 'z.json', current_owner(btc=200))
            result = etf.asof_join(etf.load_owner_records(root), datetime(2026, 8, 9, tzinfo=timezone.utc))
            self.assertEqual(result['status'], 'UNAVAILABLE')
            self.assertEqual(result['reason'], 'CONFLICTING_OWNER_REVISIONS_AT_SAME_KNOWLEDGE_TIME')

    def test_current_owner_rejects_bad_evidence_even_when_row_signature_matches(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            defects = ('wrong_source', 'future_contract', 'naive_time', 'future_session', 'unknown_cell',
                       'unknown_count', 'imputed', 'false_parity', 'wrong_calculated', 'wrong_reported',
                       'nan', 'infinity', 'boolean_value', 'boolean_total', 'boolean_verification',
                       'nonfinite_separation', 'header_mismatch', 'portfolio_authority')
            for defect in defects:
                with self.subTest(defect=defect):
                    obj = current_owner()
                    row = obj['rows'][0]
                    if defect == 'wrong_source': obj['verification']['source'] = 'FARSIDE_CANONICAL_TABLES'
                    if defect == 'future_contract': obj['contract'] = 'UNKNOWN_v9'
                    if defect == 'naive_time': obj['retrieved_at_utc'] = '2026-08-08T06:00:00'
                    if defect == 'future_session': obj['session_date'] = '2026-08-10'
                    if defect == 'unknown_cell': row['fund_values'] = [None]
                    if defect == 'unknown_count': row['unknown_fund_cell_count'] = 1
                    if defect == 'imputed': obj['verification']['unknown_cells_imputed'] = True
                    if defect == 'false_parity': row['total_parity'] = False
                    if defect == 'wrong_calculated': row['calculated_total'] = 999
                    if defect == 'wrong_reported': row['reported_total'] = 999
                    if defect == 'nan': row['reported_total'] = float('nan')
                    if defect == 'infinity': row['reported_total'] = float('inf')
                    if defect == 'boolean_value': row['fund_values'] = [True]
                    if defect == 'boolean_total': row['reported_total'] = True
                    if defect == 'boolean_verification': obj['verification']['rows_identical_across_retrievals'] = 1
                    if defect == 'nonfinite_separation': obj['verification']['minimum_separation_seconds'] = float('inf')
                    if defect == 'header_mismatch': row['fund_headers'] = ['a', 'b']
                    if defect == 'portfolio_authority': obj['portfolio_action'] = True
                    obj['row_signature_sha256'] = etf.rows_signature(obj['rows'])
                    p = self.write(root, 'invalid.json', obj)
                    with self.assertRaises(ValueError):
                        etf.validate_owner_record(p)

    def test_bad_rows_are_diagnosed_without_erasing_independent_valid_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self.write(root, 'good.json', current_owner())
            bad = self.write(root, 'bad.json', {})
            bad.write_text('{')
            diagnostics = []
            rows = etf.load_owner_records(root, diagnostics=diagnostics)
            self.assertEqual(len(rows), 1)
            self.assertEqual(diagnostics, [{'path': str(bad), 'reason': 'INVALID_JSON'}])
            self.assertTrue(etf.readiness(root)['owner_ingestion_diagnostics'])

    def test_valid_signed_negative_flows_and_owner_parity_tolerance_remain_supported(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            obj = current_owner(btc=-100, eth=0)
            obj['rows'][0]['reported_total'] = -100.5
            obj['row_signature_sha256'] = etf.rows_signature(obj['rows'])
            p = self.write(root, 'negative.json', obj)
            self.assertEqual(etf.validate_owner_record(p).btc_reported_total, -100.5)

    def test_missing_root_and_naive_cutoff_are_explicit_failures(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / 'missing'
            self.assertEqual(etf.readiness(root)['status'], 'UNAVAILABLE_OWNER_EVIDENCE')
            with self.assertRaisesRegex(ValueError, 'TIMEZONE'):
                etf.asof_join([], datetime(2026, 8, 8))

    def test_latest_known_revision_wins_only_after_known_at(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"v1.json",owner("2026-08-07","2026-08-08T06:06:00Z",100,50))
            self.write(root,"v2.json",owner("2026-08-07","2026-08-09T06:06:00Z",110,55))
            rows=etf.load_owner_records(root)
            early=etf.asof_join(rows, datetime(2026,8,8,12,tzinfo=timezone.utc))
            late=etf.asof_join(rows, datetime(2026,8,9,12,tzinfo=timezone.utc))
            self.assertEqual(early["raw_reported_totals"]["BTC"],100)
            self.assertEqual(late["raw_reported_totals"]["BTC"],110)

    def test_weekend_has_no_synthetic_sessions(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"friday.json",owner("2026-08-07","2026-08-08T06:06:00Z"))
            sunday=etf.asof_join(etf.load_owner_records(root), datetime(2026,8,9,18,tzinfo=timezone.utc))
            self.assertEqual(sunday["session_date"],"2026-08-07")
            self.assertEqual(sunday["session_age_calendar_days_at_cutoff"],2)
            self.assertFalse(sunday["synthetic_weekend_rows"])

    def test_late_publication_is_not_backdated_to_session(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            self.write(root,"late.json",owner("2026-08-07","2026-08-10T08:06:00Z"))
            rows=etf.load_owner_records(root)
            before=etf.asof_join(rows, datetime(2026,8,10,7,0,tzinfo=timezone.utc))
            after=etf.asof_join(rows, datetime(2026,8,10,9,0,tzinfo=timezone.utc))
            self.assertEqual(before["status"],"UNAVAILABLE")
            self.assertEqual(after["status"],"AVAILABLE")
            self.assertEqual(after["known_at_utc"],"2026-08-10T08:06:00Z")

    def test_incomplete_verification_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            path=self.write(root,"bad.json",owner("2026-08-07","2026-08-08T06:06:00Z",verified=False))
            with self.assertRaisesRegex(ValueError,"VERIFICATION_FAILURE"):
                etf.validate_owner_record(path)

    def test_unknown_fund_cell_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            obj=owner("2026-08-07","2026-08-08T06:06:00Z")
            obj["rows"][0]["fund_values"]=[None]
            obj["row_signature_sha256"]=etf.rows_signature(obj["rows"])
            path=self.write(root,"bad.json",obj)
            with self.assertRaisesRegex(ValueError,"UNKNOWN_FUND_CELL"):
                etf.validate_owner_record(path)

    def test_signature_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            obj=owner("2026-08-07","2026-08-08T06:06:00Z")
            obj["row_signature_sha256"]="0"*64
            path=self.write(root,"bad.json",obj)
            with self.assertRaisesRegex(ValueError,"ROW_SIGNATURE_MISMATCH"):
                etf.validate_owner_record(path)

    def test_preflight_does_not_run_experiment_or_call_sources(self):
        with tempfile.TemporaryDirectory() as td:
            result=etf.readiness(Path(td))
            self.assertEqual(result["status"],"VERIFIED_ADAPTER_PENDING_FIRST_OWNER_ROW")
            self.assertEqual(result["external_calls_performed"],0)
            self.assertFalse(result["flow_state_derived"])
            self.assertFalse(result["event_definition_applied"])
            self.assertFalse(result["experiment_executed"])


if __name__=="__main__":
    unittest.main()
