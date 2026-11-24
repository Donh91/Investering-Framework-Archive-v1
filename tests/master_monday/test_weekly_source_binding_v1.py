import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from scripts.master_monday.weekly_source_binding_v1 import capture_binding, verify_binding, canonical, write_binding_sidecar, verify_sidecar

ROOT=Path(__file__).resolve().parents[2]
class Binding(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'03_DAILY_CAPTURE_LOGS';self.file=self.root/'weekly/2026/W47.json';self.file.parent.mkdir(parents=True)
        self.raw=(ROOT/'03_DAILY_CAPTURE_LOGS/weekly/2026/W47.json').read_bytes();self.file.write_bytes(self.raw)
        self.pointer={'contract':'LATEST_WEEKLY_CALIBRATION_POINTER_v3','path':'weekly/2026/W47.json','iso_year':2026,'iso_week':47}
        self.binding=capture_binding(self.root,self.pointer,2026,47,'2026-11-23T09:42:55Z')
        self.freeze={'contract':'WEEKLY_ORCHESTRATION_FREEZE_v5','iso_year':2026,'iso_week':47,'created_at_utc':'2026-11-23T09:42:55Z','weekly_capture_bridge':{'sha256':hashlib.sha256(canonical(self.pointer)).hexdigest()},'weekly_source_binding':self.binding,'freeze_sha256':None}
        self.freeze['freeze_sha256']=hashlib.sha256(canonical(self.freeze)).hexdigest()
    def verify(self):return verify_binding(self.freeze,self.pointer,self.root,self.freeze['freeze_sha256'])
    def test_byte_binding_does_not_claim_first_known(self):
        result=self.verify();self.assertEqual(result['status'],'BYTE_BINDING_VERIFIED');self.assertEqual(result['source_sha256'],hashlib.sha256(self.raw).hexdigest());self.assertFalse(result['scientific_pit_eligible']);self.assertEqual(result['first_known_status'],'UNKNOWN')
    def test_changed_source_and_stolen_id_fail(self):
        self.file.write_bytes(self.raw+b' ');self.assertEqual(self.verify()['reason'],'SOURCE_BINDING_OR_BYTES_MISMATCH')
        self.file.write_bytes(self.raw);self.freeze['weekly_source_binding']['source_id']='OTHER';self.assertEqual(self.verify()['reason'],'FREEZE_HASH_MISMATCH')
    def test_pointer_freeze_and_binding_checks_fail(self):
        self.assertEqual(verify_binding(self.freeze,self.pointer,self.root,'0'*64)['reason'],'FREEZE_HASH_MISMATCH')
        self.pointer['iso_week']=46;self.assertEqual(self.verify()['reason'],'POINTER_HASH_MISMATCH')
    def test_historical_freeze_without_binding_is_unknown(self):
        old={'contract':'WEEKLY_ORCHESTRATION_FREEZE_v5','iso_year':2026,'iso_week':47,'weekly_capture_bridge':{'sha256':hashlib.sha256(canonical(self.pointer)).hexdigest()}}
        old['freeze_sha256']=hashlib.sha256(canonical(old)).hexdigest()
        self.assertEqual(verify_binding(old,self.pointer,self.root,old['freeze_sha256'])['reason'],'SOURCE_BINDING_MISSING')
    def test_sidecar_is_idempotent_and_conflicting_rewrite_fails(self):
        path=write_binding_sidecar(self.root, self.freeze)
        original=path.read_bytes()
        self.assertEqual(write_binding_sidecar(self.root, self.freeze).read_bytes(),original)
        path.write_bytes(b'tampered')
        with self.assertRaisesRegex(ValueError,'SOURCE_BINDING_WRITE_ONCE_CONFLICT'):
            write_binding_sidecar(self.root,self.freeze)
    def test_consumer_readback_fails_if_receipt_missing_or_changed(self):
        args=(self.root,self.freeze,self.pointer,self.root,self.freeze['freeze_sha256'])
        self.assertEqual(verify_sidecar(*args)['reason'],'SOURCE_BINDING_RECEIPT_MISSING')
        path=write_binding_sidecar(self.root,self.freeze)
        self.assertEqual(verify_sidecar(*args)['status'],'BYTE_BINDING_AND_RECEIPT_VERIFIED')
        path.write_bytes(path.read_bytes()+b' ')
        self.assertEqual(verify_sidecar(*args)['reason'],'SOURCE_BINDING_RECEIPT_MISMATCH')
    def test_rehashed_stolen_id_fails_byte_binding(self):
        self.freeze['weekly_source_binding']['source_id']='OTHER'
        self.freeze['freeze_sha256']=None
        self.freeze['freeze_sha256']=hashlib.sha256(canonical(self.freeze)).hexdigest()
        self.assertEqual(self.verify()['reason'],'SOURCE_BINDING_OR_BYTES_MISMATCH')
    def test_future_source_is_unknown(self):
        self.assertEqual(capture_binding(self.root,self.pointer,2026,47,'2026-11-23T09:00:00Z')['reason'],'SOURCE_FUTURE_OR_INVALID_CLOCK')
    def test_pointer_path_cannot_escape_or_change_week(self):
        for value in ('../../other.json','weekly/2026/W46.json'):
            self.pointer['path']=value
            self.assertEqual(capture_binding(self.root,self.pointer,2026,47,'2026-11-23T09:42:55Z')['status'],'UNKNOWN')

class ArchivedW47(unittest.TestCase):
    def test_authentic_w47_freeze_is_not_retroactively_attested(self):
        import subprocess
        freeze=json.loads((ROOT/'research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json').read_text())
        pointer=json.loads(subprocess.check_output(['git','show','ec36550041fe48b2976c06733dc4bad093b9eed5:03_DAILY_CAPTURE_LOGS/weekly/LATEST_WEEKLY_CALIBRATION.json'],cwd=ROOT))
        result=verify_binding(freeze,pointer,ROOT/'03_DAILY_CAPTURE_LOGS',freeze['freeze_sha256'])
        self.assertEqual(result['status'],'UNKNOWN')
        self.assertEqual(result['reason'],'SOURCE_BINDING_MISSING')
        self.assertFalse(result['scientific_pit_eligible'])

class ProducerIntegration(unittest.TestCase):
    def test_existing_controller_writes_byte_binding(self):
        import subprocess,sys
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/'capture'; weekly=root/'weekly'; close=root/'weekly_close'
            (weekly/'2026').mkdir(parents=True);close.mkdir(parents=True)
            raw=(ROOT/'03_DAILY_CAPTURE_LOGS/weekly/2026/W47.json').read_bytes()
            (weekly/'2026/W47.json').write_bytes(raw)
            pointer={'contract':'LATEST_WEEKLY_CALIBRATION_POINTER_v3','path':'weekly/2026/W47.json','iso_year':2026,'iso_week':47}
            (weekly/'LATEST_WEEKLY_CALIBRATION.json').write_bytes(canonical(pointer))
            package={'final':True,'close_mode':'FINAL_COMPLETED_ISO_WEEK','completeness':'COMPLETE','iso_year':2026,'iso_week':47,'window_end_utc':'2026-11-23T00:00:00Z'}
            (close/'W47.json').write_bytes(canonical(package))
            cp={**package,'contract':'WEEKLY_MARKET_CLOSE_POINTER_v3','path':'weekly_close/W47.json','sha256':hashlib.sha256(canonical(package)).hexdigest()}
            (close/'LATEST_WEEKLY_MARKET_CLOSE.json').write_bytes(canonical(cp))
            output=Path(tmp)/'freeze.json'
            subprocess.run([sys.executable,str(ROOT/'scripts/orchestration/weekly_orchestration_controller.py'),'--capture-root',str(root),'--accepted-data-ping-root',str(Path(tmp)/'empty'),'--output',str(output),'--now-utc','2026-11-23T09:46:18Z'],check=True,capture_output=True)
            freeze=json.loads(output.read_bytes())
            self.assertEqual(freeze['weekly_source_binding']['sha256'],hashlib.sha256(raw).hexdigest())
            verified=verify_binding(freeze,pointer,root,freeze['freeze_sha256'])
            self.assertEqual(verified['status'],'BYTE_BINDING_VERIFIED')
            self.assertEqual(verified['first_known_status'],'UNKNOWN')
            (weekly/'2026/W47.json').write_bytes(raw+b' ')
            self.assertEqual(verify_binding(freeze,pointer,root,freeze['freeze_sha256'])['status'],'UNKNOWN')
