import copy
import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.cycle_navigator.prospective_range_bridge import BRIDGE_PATH, load_bridge


class ProspectiveBridgeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        (self.repo / BRIDGE_PATH).parent.mkdir(parents=True)
        actuals = {'iso_year': 2026, 'iso_week': 43, 'readiness': 'READY',
                   'generated_at_utc': '2026-10-26T05:00:00Z',
                   'hourly_gap_diagnostics': {'expected_hours': 168,
                                              'observed_hours': 168,
                                              'missing_hour_count': 0}}
        self.sources = {'prior_published_ranges': 'published.md',
                        'completed_week_actuals': 'actuals.json'}
        (self.repo / 'published.md').write_text('Original published ranges')
        (self.repo / 'actuals.json').write_text(json.dumps(actuals))
        subprocess.run(['git', 'init', '-q', str(self.repo)], check=True)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'published.md', 'actuals.json'], check=True)
        fixture_env = {**os.environ, 'GIT_AUTHOR_DATE': '2026-10-26T05:00:00Z',
                       'GIT_COMMITTER_DATE': '2026-10-26T05:00:00Z'}
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Original sources'],
            check=True, env=fixture_env)
        commit = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD']).decode().strip()
        provenance = {}
        for key, path in self.sources.items():
            provenance[key] = path
            provenance[key + '_commit'] = commit
            provenance[key + '_sha256'] = hashlib.sha256((self.repo / path).read_bytes()).hexdigest()
        bands = {a: {'low': 10, 'high': 20} for a in ('BTC', 'ETH')}
        self.bridge = {'contract': 'CN_PROSPECTIVE_RANGE_BRIDGE_v1',
            'status': 'READY_CONTINUITY_BASELINE', 'target_week': '2026-W44',
            'source_week': '2026-W43', 'source_cutoff_utc': '2026-10-26T00:00:00Z',
            'generated_at_utc': '2026-10-26T06:00:00Z', 'generated_after_source_week_close': True,
            'provenance': provenance, 'weekly': bands,
            'intraday': {k: copy.deepcopy(bands) for k in ('day_1_2', 'day_3_4', 'day_5_7')}}
        self.freeze = datetime(2026, 10, 26, 7, tzinfo=timezone.utc)
        (self.repo / BRIDGE_PATH).write_text(json.dumps(self.bridge))
        self.commit_bridge('2026-10-26T06:30:00Z')

    def commit_bridge(self, stamp):
        subprocess.run(['git', '-C', str(self.repo), 'add', BRIDGE_PATH.as_posix()], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Frozen bridge'],
            check=True, env={**os.environ, 'GIT_AUTHOR_DATE': stamp, 'GIT_COMMITTER_DATE': stamp})

    def read(self):
        (self.repo / BRIDGE_PATH).write_text(json.dumps(self.bridge))
        return load_bridge(self.repo, target_year=2026, target_week=44, freeze_at=self.freeze)

    def reject(self, reason):
        result = self.read()
        self.assertIn(reason, result['reason_codes'])
        self.assertFalse(result['range_values_admitted'])
        self.assertNotIn('weekly', result)
        self.assertNotIn('intraday', result)

    def test_exact_source_bound_bridge(self):
        result = self.read()
        self.assertEqual(result['consumer_receipt']['status'], 'READY')
        self.assertFalse(result['consumer_receipt']['scientific_admission'])

    def test_mutable_bridge_cannot_reuse_original_source_custody(self):
        self.bridge['weekly']['BTC']['high'] = 21
        self.reject('BRIDGE_COMMITTED_BYTES_MISMATCH')

    def test_bridge_never_committed_is_not_original_forecast(self):
        path = Path('uncommitted-bridge.json')
        (self.repo / path).write_text(json.dumps(self.bridge))
        result = load_bridge(self.repo, target_year=2026, target_week=44,
                             freeze_at=self.freeze, path=path)
        self.assertEqual(result['reason_codes'], ['BRIDGE_COMMIT_UNVERIFIED'])
        self.assertNotIn('weekly', result)

    def test_bridge_commit_later_than_forecast_freeze(self):
        self.bridge['weekly']['BTC']['high'] = 21
        (self.repo / BRIDGE_PATH).write_text(json.dumps(self.bridge))
        self.commit_bridge('2026-10-26T07:00:01Z')
        self.reject('BRIDGE_COMMITTED_AFTER_FORECAST_FREEZE')

    def test_wrong_week_or_year(self):
        for target in ('2026-W39', '2025-W44'):
            with self.subTest(target=target):
                self.bridge['target_week'] = target
                self.reject('BRIDGE_TARGET_WEEK_MISMATCH')

    def test_wrong_source_week(self):
        self.bridge['source_week'] = '2026-W42'
        self.reject('BRIDGE_SOURCE_WEEK_MISMATCH')

    def test_late_generation_not_original_forecast(self):
        self.bridge['generated_at_utc'] = '2026-10-26T07:00:01Z'
        self.reject('BRIDGE_GENERATED_AFTER_FORECAST_FREEZE')

    def test_missing_original_generation(self):
        del self.bridge['generated_at_utc']
        self.reject('BRIDGE_OR_FREEZE_TIMESTAMP_UNVERIFIED')

    def test_source_period_must_be_closed(self):
        self.bridge['source_cutoff_utc'] = '2026-10-25T00:00:00Z'
        self.reject('BRIDGE_SOURCE_PERIOD_NOT_CLOSED')

    def test_source_hash_mutation_and_missing_source(self):
        (self.repo / 'actuals.json').write_text('{}')
        self.reject('BRIDGE_SOURCE_HASH_MISMATCH:completed_week_actuals')
        (self.repo / 'actuals.json').unlink()
        self.reject('BRIDGE_SOURCE_MISSING:completed_week_actuals')

    def test_source_hash_absent(self):
        del self.bridge['provenance']['completed_week_actuals_sha256']
        self.reject('BRIDGE_SOURCE_BINDING_MISSING:completed_week_actuals')

    def test_commit_custody_missing(self):
        del self.bridge['provenance']['prior_published_ranges_commit']
        self.reject('BRIDGE_SOURCE_COMMIT_MISSING:prior_published_ranges')

    def test_fabricated_commit(self):
        self.bridge['provenance']['prior_published_ranges_commit'] = 'a' * 40
        self.reject('BRIDGE_SOURCE_COMMIT_UNVERIFIED:prior_published_ranges')

    def test_valid_current_hash_does_not_replace_original_committed_bytes(self):
        raw = b'Later replacement'
        (self.repo / 'published.md').write_bytes(raw)
        self.bridge['provenance']['prior_published_ranges_sha256'] = hashlib.sha256(raw).hexdigest()
        self.reject('BRIDGE_FROZEN_SOURCE_HASH_MISMATCH:prior_published_ranges')

    def test_commit_after_claimed_generation_rejected(self):
        self.bridge['generated_at_utc'] = '2026-10-26T04:59:59Z'
        self.reject('BRIDGE_SOURCE_COMMITTED_AFTER_GENERATION:prior_published_ranges')

    def test_mutated_actuals_do_not_replace_original_commit(self):
        value = json.loads((self.repo / 'actuals.json').read_text())
        value['generated_at_utc'] = '2026-10-26T06:30:00Z'
        raw = json.dumps(value).encode()
        (self.repo / 'actuals.json').write_bytes(raw)
        self.bridge['provenance']['completed_week_actuals_sha256'] = hashlib.sha256(raw).hexdigest()
        self.reject('BRIDGE_FROZEN_SOURCE_HASH_MISMATCH:completed_week_actuals')

    def test_committed_actuals_with_future_generated_time_rejected(self):
        value = json.loads((self.repo / 'actuals.json').read_text())
        value['generated_at_utc'] = '2026-10-26T06:30:00Z'
        raw = json.dumps(value).encode()
        (self.repo / 'actuals.json').write_bytes(raw)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'actuals.json'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Bound actuals'],
            check=True, env={**os.environ, 'GIT_AUTHOR_DATE': '2026-10-26T05:30:00Z',
                            'GIT_COMMITTER_DATE': '2026-10-26T05:30:00Z'})
        commit = subprocess.check_output(['git', '-C', str(self.repo), 'rev-parse', 'HEAD']).decode().strip()
        self.bridge['provenance']['completed_week_actuals_commit'] = commit
        self.bridge['provenance']['completed_week_actuals_sha256'] = hashlib.sha256(raw).hexdigest()
        self.reject('BRIDGE_ACTUALS_NOT_FINAL_AT_GENERATION')

    def test_actuals_generated_before_source_week_closed_is_rejected(self):
        # A source can be correctly hash-bound and committed after week close,
        # yet falsely claim its complete final actuals were generated earlier.
        value = json.loads((self.repo / 'actuals.json').read_text())
        value['generated_at_utc'] = '2026-10-25T23:59:59Z'
        raw = json.dumps(value).encode()
        (self.repo / 'actuals.json').write_bytes(raw)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'actuals.json'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Bound pre-close actuals'],
            check=True, env={**os.environ, 'GIT_AUTHOR_DATE': '2026-10-26T05:35:00Z',
                            'GIT_COMMITTER_DATE': '2026-10-26T05:35:00Z'})
        self.bridge['provenance']['completed_week_actuals_commit'] = subprocess.check_output(
            ['git', '-C', str(self.repo), 'rev-parse', 'HEAD']).decode().strip()
        self.bridge['provenance']['completed_week_actuals_sha256'] = hashlib.sha256(raw).hexdigest()
        self.reject('BRIDGE_ACTUALS_NOT_FINAL_AT_GENERATION')

    def test_bridge_commit_before_claimed_generation_is_rejected(self):
        # Valid source bindings and an on-time committed file are insufficient
        # when generation is self-reported AFTER the committed bridge existed.
        self.bridge['generated_at_utc'] = '2026-10-26T06:45:00Z'
        (self.repo / BRIDGE_PATH).write_text(json.dumps(self.bridge))
        self.commit_bridge('2026-10-26T06:35:00Z')
        self.reject('BRIDGE_COMMITTED_BEFORE_GENERATION')

    def rebind_original_actuals(self, value):
        raw = json.dumps(value).encode()
        (self.repo / 'actuals.json').write_bytes(raw)
        subprocess.run(['git', '-C', str(self.repo), 'add', 'actuals.json'], check=True)
        subprocess.run(['git', '-C', str(self.repo), '-c', 'user.name=Fixture',
            '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'Bound source health'],
            check=True, env={**os.environ, 'GIT_AUTHOR_DATE': '2026-10-26T05:40:00Z',
                            'GIT_COMMITTER_DATE': '2026-10-26T05:40:00Z'})
        self.bridge['provenance']['completed_week_actuals_commit'] = subprocess.check_output(
            ['git', '-C', str(self.repo), 'rev-parse', 'HEAD']).decode().strip()
        self.bridge['provenance']['completed_week_actuals_sha256'] = hashlib.sha256(raw).hexdigest()

    def test_ready_label_without_hourly_diagnostics_is_rejected(self):
        value = json.loads((self.repo / 'actuals.json').read_text())
        del value['hourly_gap_diagnostics']
        self.rebind_original_actuals(value)
        self.reject('BRIDGE_ACTUALS_HOURLY_COVERAGE_UNVERIFIED')

    def test_ready_label_with_zero_observed_hours_is_rejected(self):
        value = json.loads((self.repo / 'actuals.json').read_text())
        value['hourly_gap_diagnostics']['observed_hours'] = 0
        value['hourly_gap_diagnostics']['missing_hour_count'] = 168
        self.rebind_original_actuals(value)
        self.reject('BRIDGE_ACTUALS_HOURLY_COVERAGE_UNVERIFIED')

    def test_invalid_band_no_partial_admission(self):
        self.bridge['intraday']['day_5_7']['ETH']['low'] = float('nan')
        self.reject('BRIDGE_RANGES_INVALID')

    def test_actual_current_archive_bridge_excluded_from_w44(self):
        root = Path(__file__).resolve().parents[2]
        value = load_bridge(root, target_year=2026, target_week=44, freeze_at=self.freeze)
        self.assertEqual(value['reason_codes'], ['BRIDGE_TARGET_WEEK_MISMATCH'])
        self.assertNotIn('weekly', value)


if __name__ == '__main__':
    unittest.main()
