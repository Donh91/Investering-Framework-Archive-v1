from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from scripts.orchestration.weekly_orchestration_controller import expected_completed_week

ROOT=Path(__file__).resolve().parents[2]


class DurableRepairTests(unittest.TestCase):
    def test_copenhagen_summer_week_window(self):
        values=expected_completed_week(datetime(2026,8,3,0,20,tzinfo=timezone.utc))
        year,week,local_start,local_end,start_utc,end_utc,exchange_end=values
        self.assertEqual((year,week),(2026,31))
        self.assertEqual(local_start.isoformat(),'2026-07-27T00:00:00+02:00')
        self.assertEqual(local_end.isoformat(),'2026-08-03T00:00:00+02:00')
        self.assertEqual(start_utc.isoformat(),'2026-07-26T22:00:00+00:00')
        self.assertEqual(end_utc.isoformat(),'2026-08-02T22:00:00+00:00')
        self.assertEqual(exchange_end.isoformat(),'2026-08-03T00:00:00+00:00')

    def test_copenhagen_winter_week_window(self):
        values=expected_completed_week(datetime(2026,1,5,2,20,tzinfo=timezone.utc))
        _,_,local_start,local_end,start_utc,end_utc,_=values
        self.assertEqual(local_start.isoformat(),'2025-12-29T00:00:00+01:00')
        self.assertEqual(local_end.isoformat(),'2026-01-05T00:00:00+01:00')
        self.assertEqual(start_utc.isoformat(),'2025-12-28T23:00:00+00:00')
        self.assertEqual(end_utc.isoformat(),'2026-01-04T23:00:00+00:00')

    def test_context_uses_copenhagen_day_key(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); daily=root/'daily'; daily.mkdir()
            for idx,stamp in enumerate(('2026-08-02T21:30:00Z','2026-08-02T22:30:00Z')):
                d=daily/str(idx);d.mkdir()
                (d/'DAILY_DIRECTOR_OUTPUT.json').write_text(json.dumps({'generated_at_utc':stamp,'value':idx}))
                (d/'DAILY_DIRECTOR_RECEIPT.json').write_text(json.dumps({'created_at_utc':stamp}))
            weekly=root/'weekly.json';weekly.write_text('{}')
            freeze=root/'freeze.json';freeze.write_text(json.dumps({'iso_year':2026,'iso_week':31,'window_start_utc':'2026-08-02T20:00:00Z','window_end_utc':'2026-08-03T23:00:00Z','freeze_sha256':'abc'}))
            out=root/'context.json'
            p=subprocess.run(['python',str(ROOT/'scripts/api_agent/build_weekly_calibration_context.py'),'--weekly-pointer',str(weekly),'--daily-output-root',str(daily),'--freeze-file',str(freeze),'--output',str(out)],capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr)
            value=json.loads(out.read_text())
            self.assertEqual([r['local_day_key'] for r in value['daily_director_rows']],['2026-08-02','2026-08-03'])
            self.assertIn('Europe/Copenhagen local date',value['selection_rule'])

    def test_readback_compares_remote_bytes_and_blob(self):
        with tempfile.TemporaryDirectory() as td:
            repo=Path(td)
            subprocess.run(['git','init'],cwd=repo,check=True,capture_output=True)
            subprocess.run(['git','config','user.email','test@example.com'],cwd=repo,check=True)
            subprocess.run(['git','config','user.name','test'],cwd=repo,check=True)
            path=repo/'artifact.txt';path.write_text('committed\n')
            subprocess.run(['git','add','artifact.txt'],cwd=repo,check=True)
            subprocess.run(['git','commit','-m','init'],cwd=repo,check=True,capture_output=True)
            blob=subprocess.run(['git','rev-parse','HEAD:artifact.txt'],cwd=repo,check=True,capture_output=True,text=True).stdout.strip()
            committed_sha=hashlib.sha256(b'committed\n').hexdigest()
            manifest=repo/'manifest.json';manifest.write_text(json.dumps({'artifacts':[{'path':'artifact.txt','sha256':committed_sha,'blob_sha':blob}]}))
            receipt=repo/'receipt.json'
            ok=subprocess.run(['python',str(ROOT/'scripts/orchestration/verify_durable_readback.py'),'--manifest',str(manifest),'--ref','HEAD','--output',str(receipt)],cwd=repo,capture_output=True,text=True)
            self.assertEqual(ok.returncode,0,ok.stderr)
            self.assertEqual(json.loads(receipt.read_text())['status'],'DURABLE_PASS')
            path.write_text('local-only-change\n')
            manifest.write_text(json.dumps({'artifacts':[{'path':'artifact.txt','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'blob_sha':blob}]}))
            bad=subprocess.run(['python',str(ROOT/'scripts/orchestration/verify_durable_readback.py'),'--manifest',str(manifest),'--ref','HEAD','--output',str(receipt)],cwd=repo,capture_output=True,text=True)
            self.assertNotEqual(bad.returncode,0)
            row=json.loads(receipt.read_text())['artifacts'][0]
            self.assertNotEqual(row['expected_sha256'],row['readback_sha256'])


if __name__=='__main__': unittest.main()
