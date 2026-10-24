"""Synthetic source-health cases only; no provider values or network calls."""
import copy
import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from email.utils import format_datetime

from scripts.learning.forward_price_source_custody import inspect_custody


def fixture():
    now = datetime(2026, 10, 24, 13, 30, tzinfo=timezone.utc)
    stamp = lambda t: t.isoformat().replace('+00:00', 'Z')
    payloads = {'pair': {'error': [], 'result': {
        'XXBTZUSD': {'base': 'XXBT', 'quote': 'ZUSD'}}}}
    for name, step, count in [('daily', 86400, 253), ('hourly', 3600, 73)]:
        final = int(now.timestamp()) // step * step
        rows = [[final - step * (count - i), '100', '110', '90', '100', '100', '1', 1]
                for i in range(count + 1)]
        payloads[name] = {'error': [], 'result': {'XXBTZUSD': rows, 'last': final}}
    blobs = {k: json.dumps(v).encode() for k, v in payloads.items()}
    manifest = {'contract': 'FORWARD_PRICE_SOURCE_CUSTODY_RESEARCH_RECEIPT_v1',
        'private_repository': 'Donh91/secrets', 'provider': 'KRAKEN',
        'status': 'CAPTURED_NOT_ADMITTED', 'validation_status': 'CAPTURED_NOT_ADMITTED',
        'original_historical_provider_first_known_verified': False,
        'collector_commit_sha': None, 'new_forecast_issued': False,
        'outcome_scoring_performed': False, 'round3_access': False, 'items': []}
    for name in blobs:
        item = {'name': name, 'exact_relative_path': name + '.json',
            'bytes': len(blobs[name]), 'sha256': hashlib.sha256(blobs[name]).hexdigest(),
            'retrieval_start_utc': stamp(now), 'retrieval_end_utc': stamp(now + timedelta(seconds=5)),
            'response_headers': {'date': format_datetime(now + timedelta(seconds=3), usegmt=True)},
            'instrument_id': 'XXBTZUSD', 'base': 'BTC', 'quote': 'USD', 'http_status': 200}
        if name != 'pair':
            step = 86400 if name == 'daily' else 3600
            rows = payloads[name]['result']['XXBTZUSD']
            item.update(interval_seconds=step, completed_rows=len(rows)-1,
                returned_rows=len(rows), excluded_final_current_interval=1, gap_count=0,
                first_completed_open_utc=stamp(datetime.fromtimestamp(rows[0][0], timezone.utc)),
                latest_completed_close_utc=stamp(datetime.fromtimestamp(rows[-2][0]+step, timezone.utc)))
        manifest['items'].append(item)
    return manifest, blobs, stamp(now + timedelta(seconds=10))


class SourceCustodyTests(unittest.TestCase):
    def test_valid_capture_is_healthy_but_never_source_admitted(self):
        manifest, blobs, asof = fixture()
        before = copy.deepcopy(manifest)
        result = inspect_custody(manifest, blobs, as_of_utc=asof)
        self.assertEqual(manifest, before)
        self.assertEqual(result['health_status'], 'PASS')
        self.assertEqual(result['status'], 'CAPTURED_NOT_ADMITTED')
        self.assertEqual(result['reason'], 'ORIGINAL_PROVIDER_FIRST_KNOWN_UNVERIFIED')
        self.assertFalse(result['source_admitted'])
        self.assertFalse(result['forecast_issued'])
        self.assertEqual(result['forecast_status'], 'UNAVAILABLE')
        self.assertEqual(result['completed_rows'], {'daily': 253, 'hourly': 73})
        self.assertNotIn('100', json.dumps(result))

    def test_capture_cannot_self_promote_any_authority_flag(self):
        for key, value in [('status', 'RELEASED'), ('validation_status', 'PASS'),
            ('original_historical_provider_first_known_verified', True),
            ('new_forecast_issued', True), ('outcome_scoring_performed', True),
            ('round3_access', True), ('collector_commit_sha', 'a' * 40)]:
            with self.subTest(key=key):
                manifest, blobs, asof = fixture()
                manifest[key] = value
                with self.assertRaises(ValueError):
                    inspect_custody(manifest, blobs, as_of_utc=asof)

    def reject_payload(self, name, mutate):
        manifest, blobs, asof = fixture()
        doc = json.loads(blobs[name]); mutate(doc)
        blobs[name] = json.dumps(doc).encode()
        item = next(x for x in manifest['items'] if x['name'] == name)
        item.update(bytes=len(blobs[name]), sha256=hashlib.sha256(blobs[name]).hexdigest())
        with self.assertRaises(ValueError):
            inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_usdt_or_wrong_instrument_rejected(self):
        self.reject_payload('pair', lambda d: d['result']['XXBTZUSD'].update(quote='USDT'))
        self.reject_payload('pair', lambda d: d['result']['XXBTZUSD'].update(base='ETH'))

    def test_gap_and_duplicate_rejected_even_with_rehashed_payload(self):
        for shift in (-3600, 3600):
            self.reject_payload('hourly', lambda d: d['result']['XXBTZUSD'][10].__setitem__(0,
                d['result']['XXBTZUSD'][10][0] + shift))

    def test_ohlc_inversion_and_nonfinite_rejected(self):
        for value in ('999', 'NaN', 'Infinity', '-1', True):
            self.reject_payload('daily', lambda d: d['result']['XXBTZUSD'][0].__setitem__(3, value))

    def test_raw_hash_mutation_rejected(self):
        manifest, blobs, asof = fixture()
        # Same-length, still-valid OHLC mutation isolates the digest guard;
        # neither byte count nor the OHLC/clock guards can hide its removal.
        blobs['daily'] = blobs['daily'].replace(b'"100"', b'"101"', 1)
        with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_wrong_interval_and_false_completeness_rejected(self):
        for key, value in [('interval_seconds', 3600), ('completed_rows', 999),
            ('gap_count', 1), ('excluded_final_current_interval', 0),
            ('latest_completed_close_utc', '2026-10-25T00:00:00Z')]:
            with self.subTest(key=key):
                manifest, blobs, asof = fixture(); manifest['items'][1][key] = value
                with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_future_capture_stale_source_and_false_http_clock_rejected(self):
        manifest, blobs, asof = fixture()
        for cutoff in ('2026-10-24T12:00:00Z', '2026-10-27T13:30:00Z'):
            with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=cutoff)
        manifest['items'][1]['response_headers']['date'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_missing_payload_duplicate_item_traversal_rejected(self):
        for change in ('missing', 'duplicate', 'traversal'):
            manifest, blobs, asof = fixture()
            if change == 'missing': blobs.pop('hourly')
            if change == 'duplicate': manifest['items'][2] = manifest['items'][1]
            if change == 'traversal': manifest['items'][1]['exact_relative_path'] = '../daily.json'
            with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_provider_error_and_wrong_pair_key_rejected(self):
        self.reject_payload('daily', lambda d: d.update(error=['EGeneral:unavailable']))
        self.reject_payload('hourly', lambda d: d['result'].__setitem__('ETHUSD', []))

    def test_uncommitted_final_bar_cannot_be_shifted_or_counted(self):
        self.reject_payload('hourly', lambda d: d['result']['XXBTZUSD'][-1].__setitem__(0,
            d['result']['XXBTZUSD'][-1][0] + 3600))

    def test_duplicate_json_key_rejected(self):
        manifest, blobs, asof = fixture()
        blobs['pair'] = (b'{"error":["masked"],"error":[],"result":'
                         b'{"XXBTZUSD":{"base":"XXBT","quote":"ZUSD"}}}')
        item = manifest['items'][0]
        item.update(bytes=len(blobs['pair']), sha256=hashlib.sha256(blobs['pair']).hexdigest())
        with self.assertRaises(ValueError): inspect_custody(manifest, blobs, as_of_utc=asof)

    def test_malformed_private_number_never_leaks_in_exception_or_traceback(self):
        import traceback
        manifest, blobs, asof = fixture()
        marker = 'SYNTHETIC_RESTRICTED_NUMBER_SENTINEL'
        doc = json.loads(blobs['daily'])
        doc['result']['XXBTZUSD'][0][3] = marker
        blobs['daily'] = json.dumps(doc).encode()
        item = manifest['items'][1]
        item.update(bytes=len(blobs['daily']), sha256=hashlib.sha256(blobs['daily']).hexdigest())
        try:
            inspect_custody(manifest, blobs, as_of_utc=asof)
        except ValueError as error:
            self.assertEqual(str(error), 'PROVIDER_VALUE_INVALID')
            self.assertNotIn(marker, ''.join(traceback.format_exception(error)))
        else:
            self.fail('malformed private provider number was accepted')
