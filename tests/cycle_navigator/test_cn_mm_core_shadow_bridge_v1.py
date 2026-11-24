import copy
import json
import unittest
from datetime import timedelta
from pathlib import Path
import tempfile
from unittest.mock import patch
from scripts.research import cn_mm_core_shadow_bridge_v1 as bridge
from scripts.research.cn_mm_core_shadow_bridge_v1 import CORE, evaluate_rows, read_rows

START = "2026-11-16T00:00:00Z"
END = "2026-11-23T00:00:00Z"
FLOOR = "2026-10-24T12:00:00Z"
MUTABLE = {"outcome_24h", "outcome_72h", "outcome_7d", "mae_24h", "mfe_24h"}


def row(hour, e, b, d):
    states = (e, b, d, e and b, e and d, b and d, e and b and d)
    return {"event_id": f"PSR_20261122T{hour:02d}0000Z",
            "observation_timestamp_utc": f"2026-11-22T{hour:02d}:00:00Z",
            "information_cutoff_utc": f"2026-11-22T{hour:02d}:00:00Z",
            "row_integrity_contract": "SHARED_ROW_P0_BINDING_v1",
            "source_version_commit": "a"*40, "provenance_hash": "b"*64,
            "source_binding_manifest": "{}", "candidate_decisions": json.dumps(dict(zip(CORE, states))),
            "outcome_24h": "1", "mae_24h": "-5"}


class CoreBridge(unittest.TestCase):
    def replay(self, rows, verify=None):
        def check(projection, at, decisions):
            self.assertFalse(MUTABLE.intersection(projection))
            if verify:
                verify(projection, at, decisions)
        return evaluate_rows(rows, START, END, FLOOR, check, MUTABLE)

    def test_reuse_candidate_and_pivotal_family(self):
        result = self.replay([row(12, True, False, True)])
        self.assertEqual(result["status"], "CORE_REPLAY_AT_OBSERVATION_ONLY")
        self.assertFalse(result["latest_observation"]["decisions"]["C07_SIMPLE_3"])
        self.assertTrue(result["attribution"]["BREADTH_SURVIVAL"]["pivotal_in_frozen_and_rule"])
        self.assertFalse(result["attribution"]["ETHBTC_PERSISTENCE"]["pivotal_in_frozen_and_rule"])
        changed = self.replay([row(12, True, True, True)])
        self.assertTrue(changed["latest_observation"]["decisions"]["C07_SIMPLE_3"])
        self.assertFalse(changed["attribution"]["BREADTH_SURVIVAL"]["pivotal_in_frozen_and_rule"])

    def test_outcomes_cannot_affect_projection(self):
        rows = [row(12, True, False, True)]
        before = self.replay(rows)
        rows[0].update(outcome_24h="0", mae_24h="999999", outcome_7d="1")
        self.assertEqual(before, self.replay(rows))

    def test_ordered_intervals_are_not_original_sequence_equivalence(self):
        rows = [row(0, False, False, False), row(1, True, False, False),
                row(2, True, False, True), row(3, True, True, True)]
        result = self.replay(list(reversed(rows)))["transition_diagnostic"]
        self.assertEqual(result["status"], "ORDERED_OBSERVATION_INTERVALS")
        self.assertFalse(result["original_sequence_equivalence"])
        self.assertFalse(result["event_time_certified"])
        same_interval = self.replay([rows[0], rows[-1]])["transition_diagnostic"]
        self.assertEqual(same_interval["status"], "ORDER_NOT_ESTABLISHED")

    def test_rejected_latest_row_has_no_fallback(self):
        def reject(projection, at, decisions):
            if projection["event_id"].endswith("120000Z"):
                raise ValueError("SOURCE_BINDING_FAILED")
        result = self.replay([row(11, True, True, True), row(12, False, False, False)], reject)
        self.assertEqual(result["status"], "UNKNOWN")
        self.assertIsNone(result["latest_observation"])

    def test_wrong_cutoff_duplicate_and_future(self):
        a = row(12, True, True, True)
        self.assertEqual(self.replay([a, copy.deepcopy(a)])["status"], "UNKNOWN")
        altered = copy.deepcopy(a)
        altered["information_cutoff_utc"] = END
        self.assertEqual(self.replay([altered])["status"], "UNKNOWN")
        future = copy.deepcopy(a)
        future["observation_timestamp_utc"] = END
        self.assertEqual(self.replay([a, future]), self.replay([a]))

    def test_ambiguous_candidate_json_and_csv_rejected(self):
        a = row(12, True, True, True)
        a["candidate_decisions"] = '{"C01_ETHBTC":true,"C01_ETHBTC":false}'
        self.assertEqual(self.replay([a])["status"], "UNKNOWN")
        for raw in (b"x,x\n1,2\n", b"x,y\n1\n", b"x,y\n1,2,3\n"):
            with self.assertRaises(ValueError):
                read_rows(raw)

    def test_no_observations(self):
        self.assertEqual(self.replay([])["reason"], "NO_ELIGIBLE_OBSERVATIONS")


def _real_w47_owner_replay(self):
    owner = bridge.load_owner()
    raw = (bridge.ROOT / bridge.LEDGER).read_bytes()
    rows = [r for r in read_rows(raw) if r["event_id"] == "PSR_20261122T224954Z"]
    self.assertEqual(len(rows), 1)
    at = bridge.clock(rows[0]["observation_timestamp_utc"])
    eligible = set(owner.eligible_candidates())
    self.assertTrue(set(CORE).issubset(eligible))

    def verify(row, cutoff, decisions):
        owner.verify_frozen_provenance(row)
        owner.validate_core_decision_contract(row, decisions, eligible)
        owner.verify_source_bindings(row, cutoff)

    args = (bridge.iso(at), bridge.iso(at + timedelta(seconds=1)), FLOOR,
            verify, owner.PROVENANCE_MUTABLE_FIELDS)
    # Direct call exposes the underlying verifier error instead of only UNKNOWN.
    projection = {k: v for k, v in rows[0].items() if k not in owner.PROVENANCE_MUTABLE_FIELDS}
    verify(projection, at, json.loads(projection["candidate_decisions"]))
    result = evaluate_rows(rows, *args)
    self.assertEqual(result["status"], "CORE_REPLAY_AT_OBSERVATION_ONLY")
    self.assertFalse(result["latest_observation"]["decisions"]["C07_SIMPLE_3"])
    self.assertTrue(result["attribution"]["ETHBTC_PERSISTENCE"]["pivotal_in_frozen_and_rule"])
    altered = copy.deepcopy(rows)
    altered[0]["source_version_commit"] = "0" * 40
    self.assertEqual(evaluate_rows(altered, *args)["status"], "UNKNOWN")
    altered = copy.deepcopy(rows)
    altered[0]["outcome_24h"] = "1" if rows[0]["outcome_24h"] == "0" else "0"
    self.assertEqual(evaluate_rows(altered, *args), result)
    head = bridge.git("rev-parse", "HEAD").decode().strip()
    pinned = owner.PinnedSourceReplay(bridge.ROOT, head)
    freeze = {"window_start_utc": bridge.iso(at),
              "window_end_utc": bridge.iso(at + timedelta(seconds=1)),
              "created_at_utc": bridge.iso(at + timedelta(seconds=2))}
    packet = {"checkout_sha": head, "ledger_sha256": bridge.sha(raw), "core": result}
    diag = bridge.verify_packet_projection(packet, freeze, raw, pinned.registry_raw, repo=bridge.ROOT)
    self.assertEqual(diag["persistence"]["side"], rows[0]["ethbtc_derived_state"])
    self.assertFalse(diag["persistence"]["scientific_pit_eligible"])
    self.assertIsNone(diag["persistence"]["stable_confirmation_utc"])
    self.assertEqual(diag["sequence"]["observation_n"], 1)
    self.assertFalse(diag["sequence"]["forecast_authority"])
    forged = copy.deepcopy(packet)
    forged["core"]["latest_observation"]["decisions"]["C07_SIMPLE_3"] = True
    with self.assertRaisesRegex(ValueError, "SHADOW_PROJECTION_MISMATCH"):
        bridge.verify_packet_projection(forged, freeze, raw, pinned.registry_raw, repo=bridge.ROOT)



class ExistingOwnerReplay(unittest.TestCase):
    def test_real_w47_row_uses_existing_byte_replay_and_frozen_candidates(self):
        # The repository-wide suite imports and mutates owner modules in many
        # fixtures. Exercise the real production CLI's fresh-process context,
        # without skipping, mocking or weakening any of the source verifiers.
        import subprocess
        import sys
        result = subprocess.run(
            [sys.executable, "-c",
             "import runpy, unittest; "
             "ns=runpy.run_path('tests/cycle_navigator/test_cn_mm_core_shadow_bridge_v1.py'); "
             "ns['_real_w47_owner_replay'](unittest.TestCase())"],
            cwd=bridge.ROOT, capture_output=True, text=True, timeout=120,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_existing_workflow_wires_readback_without_paid_context_change(self):
        workflow = (bridge.ROOT / ".github/workflows/weekly-api-calibration-shadow.yml").read_text()
        self.assertEqual(workflow.count("python scripts/research/cn_mm_core_shadow_bridge_v1.py"), 2)
        self.assertIn("--output runtime/weekly-calibration/CN_MM_CORE_SHADOW.json", workflow)
        self.assertIn("--publish-from runtime/weekly-calibration/CN_MM_CORE_SHADOW.json", workflow)
        self.assertIn("paths.append(Path(Path('runtime/cn_mm_core_shadow_path.txt').read_text().strip()))", workflow)
        self.assertIn("--context-file runtime/weekly-calibration/context.json", workflow)


class DurableShadowPublication(unittest.TestCase):
    def test_exact_binding_write_once_and_authority(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            head, freeze_sha = "a" * 40, "b" * 64
            frozen = b"fixture freeze"
            source = {"freeze_sha256": freeze_sha, "iso_year": 2026, "iso_week": 47}
            base = {"contract": "CN_MM_CORE_SHADOW_BRIDGE_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
                    "checkout_sha": head, "freeze_sha256": freeze_sha, "freeze_file_sha256": bridge.sha(frozen),
                    "first_known_status": "UNKNOWN", "scientific_pit_eligible": False,
                    "forecast_authority": False, "portfolio_execution": False, "canonical_effect": False,
                    "ledger_sha256": None, "core": bridge.unknown("NO_ELIGIBLE_OBSERVATIONS")}
            path = root / "packet.json"
            out = root / "research/api_agent/outputs/weekly/2026/W47"

            def write(value):
                packet = dict(value)
                packet["packet_sha256"] = bridge.sha(bridge.canon(packet))
                path.write_bytes(bridge.canon(packet))

            write(base)
            with patch.object(bridge, "ROOT", root), patch.object(bridge, "freeze_identity", return_value=(Path("freeze"), frozen, source)):
                target = bridge.publish_packet(path, Path("freeze"), head, out)
                self.assertEqual(target.read_bytes(), path.read_bytes())
                self.assertEqual(bridge.publish_packet(path, Path("freeze"), head, out), target)
                with self.assertRaisesRegex(ValueError, "ROUTE_MISMATCH"):
                    bridge.publish_packet(path, Path("freeze"), head, root / "wrong")
                write({**base, "forecast_authority": True})
                with self.assertRaisesRegex(ValueError, "AUTHORITY_MISMATCH"):
                    bridge.publish_packet(path, Path("freeze"), head, out)
                write({**base, "core": bridge.unknown("CHANGED")})
                with self.assertRaisesRegex(ValueError, "WRITE_ONCE_CONFLICT"):
                    bridge.publish_packet(path, Path("freeze"), head, out)


class CNConsumer(unittest.TestCase):
    def test_real_git_binding_and_missing_receipt_are_nontrading(self):
        import subprocess
        import csv
        import io
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)

            def git(*args):
                return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True).stdout

            def write(path, raw):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)

            git("init", "-q")
            git("config", "user.email", "fixture@example.invalid")
            git("config", "user.name", "Fixture")
            freeze_sha = "b" * 64
            pointer = {"iso_year": 2026, "iso_week": 47, "freeze_sha256": freeze_sha}
            freeze = {**pointer, "window_start_utc": START, "window_end_utc": END,
                      "created_at_utc": "2026-11-23T09:45:00Z"}
            frozen = bridge.canon(freeze)
            frozen_path = root / "research/master_monday_preflight/frozen/2026/W47/WEEKLY_EVIDENCE_FREEZE.json"
            write(frozen_path, frozen)
            sample = row(12, True, False, True)
            buffer = io.StringIO(newline="")
            writer = csv.DictWriter(buffer, fieldnames=list(sample))
            writer.writeheader()
            writer.writerow(sample)
            ledger = buffer.getvalue().encode()
            write(root / bridge.LEDGER, ledger)
            registry = {"core_activation_rule": {"start_only_when": list(bridge.SINGLES), "candidates": list(CORE)},
                        "families": [{"family_id": k, "prospective_eligibility_start": FLOOR} for k in bridge.SINGLES]}
            write(root / bridge.BASE / "TRANSFORM_FREEZE_REGISTRY.json", bridge.canon(registry))
            git("add", ".")
            git("commit", "-qm", "source")
            head = git("rev-parse", "HEAD").decode().strip()
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            core = evaluate_rows([row(12, True, False, True)], START, END, FLOOR, lambda *_: None, MUTABLE)
            packet = {"contract": "CN_MM_CORE_SHADOW_BRIDGE_v1", "authority": "RESEARCH_ONLY_NON_CANONICAL",
                      "checkout_sha": head, "freeze_sha256": freeze_sha, "freeze_file_sha256": bridge.sha(frozen),
                      "completed_week": "2026-W47", "first_known_status": "UNKNOWN", "scientific_pit_eligible": False,
                      "forecast_authority": False, "portfolio_execution": False, "canonical_effect": False,
                      "target_semantics": "ETHBTC_FORWARD_RELATIVE_RETURN_GT_ZERO_NOT_ALTSEASON_LIFECYCLE",
                      "ledger_sha256": bridge.sha(ledger), "core": core}
            packet["packet_sha256"] = bridge.sha(bridge.canon(packet))
            path = root / f"research/api_agent/outputs/weekly/2026/W47/CN_MM_CORE_SHADOW_{freeze_sha}.json"
            write(path, bridge.canon(packet))
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            git("add", ".")
            git("commit", "-qm", "shadow")
            result = bridge.consume_cn_shadow(root, pointer)
            # A self-hashed synthetic ledger without source owners is not evidence.
            self.assertEqual(result["status"], "UNKNOWN")
            self.assertIsNone(result["shadow_candidate_decision"])
            self.assertFalse(result["official_forecast_effect"])
            self.assertFalse(result["scientific_pit_eligible"])
            path.write_bytes(path.read_bytes() + b" ")
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
            forged = copy.deepcopy(packet)
            forged["core"]["latest_observation"]["decisions"]["C07_SIMPLE_3"] = True
            forged.pop("packet_sha256")
            forged["packet_sha256"] = bridge.sha(bridge.canon(forged))
            write(path, bridge.canon(forged))
            git("add", ".")
            git("commit", "-qm", "forged shadow")
            self.assertEqual(bridge.consume_cn_shadow(root, pointer)["status"], "UNKNOWN")
