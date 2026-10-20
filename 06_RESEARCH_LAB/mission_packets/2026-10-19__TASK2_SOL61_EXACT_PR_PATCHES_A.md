# FROZEN GITHUB PR REVIEW SOURCE: #1675
Exact SHA: 0e7ac446edd51063d2a4aa2a41a71c8abe27bf0f
Base at capture: eeb298aba14d3d0763aef674ca61113a6eb0bfa1
Draft: true
CI: Monthly AI Learning Council Gate=success | Storage Health Gate=success | Experiment Lifecycle Gate=success | Data Architecture Gate=success
COMPLETE changed-file list: scripts/experiments/experiment_lifecycle.py; scripts/experiments/sensor_relationship_compression.py; scripts/experiments/source_git_anchor.py; scripts/research/monthly_ai_learning_council.py; tests/experiments/test_experiment_lifecycle.py; tests/experiments/test_sensor_relationship_compression.py; tests/experiments/test_source_git_anchor.py; tests/research/test_monthly_ai_learning_council.py
Research input only. This is a GitHub patch excerpt, not full surrounding code. Omitted/unreadable code is UNKNOWN. Do not infer runtime execution.

### scripts/experiments/experiment_lifecycle.py (patch_chars=22361, included=5700)
```diff
@@ -5,16 +5,33 @@
 import hashlib
 import itertools
 import json
+import math
 import sys
 from datetime import datetime, timedelta, timezone
 from pathlib import Path
 from typing import Any
 
+try:
+    from scripts.experiments.source_git_anchor import AcceptedMainSource
+except ModuleNotFoundError:  # Direct script invocation from the existing workflow.
+    from source_git_anchor import AcceptedMainSource
+
 sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
 
 from metric_resolver import (  # noqa: E402  (path is prepared immediately above)
     CAPTURE_DOCUMENT_ROOT,
     canonical_path,
+    resolve_for_forecast,
+)
+sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "learning"))
+from outcome_maturation_engine import classify as classify_frozen_outcome  # noqa: E402
+from mature_exact_settlement_forecasts import validate_evidence as validate_original_settlement_evidence  # noqa: E402
+from forecast_settlement_price_owner import (  # noqa: E402
+    SettlementSourceError,
+    validate_forecast as validate_original_price_forecast,
+    last_closed_minute_open,
+    parse_binance,
+    parse_okx,
 )
 
 UTC = timezone.utc
@@ -259,34 +276,306 @@ def unique_candidate_rows(candidate_root: Path) -> tuple[list[tuple[Path, dict[s
     return rows, duplicate_count
 
 
+def outcome_bound_to_frozen_forecast(
+    outcome: dict[str, Any], frozen: dict[str, Any], outcome_root: Path,
+    *, source_anchor: AcceptedMainSource | None = None,
+    forecast_path: Path | None = None,
+) -> bool:
+    """Narrow status-eligible evidence: a self-declared score flag is insufficient.
+
+    Uses the original frozen forecast's canonical SHA, first-frozen scientific
+    admission and exact-target-time settlement contract. This still is NOT an
+    independent assessment of forecast skill or external vendor evidence.
+    """
+    if frozen.get("contract") != "FROZEN_FORECAST_v1" or frozen.get("unit_contract_version") != UNIT_CONTRACT_VERSION:
+        return False
+    if frozen.get("forecast_id") != outcome.get("forecast_id"):
+        return False
+    if outcome.get("forecast_sha256") != sha(frozen):
+        return False
+    admission = frozen.get("scientific_admission")
+    if not isinstance(admission, dict) or admission.get("status") != "QUALIFIED_FOR_FORWARD_TEST":
+        return False
+    exact = "FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1"
+    if frozen.get("settlement_contract_version") != exact or outcome.get("settlement_contract_version") != exact:
+        return False
+    due = frozen.get("outcome_due_utc")
+    target = outcome.get("settlement_target_utc")
+    observed = outcome.get("settlement_observation_utc")
+    if not isinstance(due, str) or not isinstance(target, str) or not isinstance(observed, str):
+        return False
+    try:
+        if dt(due) != dt(target) or dt(due) != dt(observed):
+            return False
+    except (ValueError, TypeError):
+        return False
+    offset = outcome.get("settlement_offset_seconds")
+    if type(offset) not in (int, float) or not float(offset) == 0.0:
+        return False
+    if not isinstance(outcome.get("evidence_sha256"), str) or len(outcome["evidence_sha256"]) != 64:
+        return False
+    forecast_id = str(frozen["forecast_id"])
+    # A file-derived ID must never become a path traversal or symlink target.
+    if (not forecast_id.startswith("EXP-FC-") or len(forecast_id) > 128
+            or not forecast_id.isascii()
+            or any(not (c.isalnum() or c in "_-") for c in forecast_id)):
+        return False
+    original = outcome_root.parent
+    # Canonical settlement producer writes immutable binding and evidence
+    # beside outcome_memory; do not trust a self-declared outcome result.
+    binding_path = original / "settlement_bindings" / f"{forecast_id}.json"
+    evidence_file = original / "settlement_evidence" / f"{forecast_id}.json"
+    try:
+        for path in (binding_path, evidence_file):
+            if path.is_symlink() or path.resolve() != path.absolute():
+                return False
+        binding = read(binding_path)
+        evidence = read(evidence_file)
+    except (OSError, ValueError, UnicodeError):
+        return False
+    if not isinstance(binding, dict) or not isinstance(evidence, dict):
+        return False
+    if binding.get("contract") != "FORECAST_SETTLEMENT_OUTCOME_BINDING_v1":
+        return False
+    if evidence.get("contract") != "FORECAST_SETTLEMENT_EVIDENCE_v1":
+        return False
+    # Recompute producer's signed-by-source JSON content digest, including
+    # original result HIT/MISS, not just an outcome-supplied 64-char claim.
+    expected = sha({k: v for k, v in binding.items() if k != "binding_sha256"})
+    if binding.get("binding_sha256") != expected:
+        return False
+    if binding.get("outcome_sha256") != sha(outcome):
+        return False
+    if binding.get("forecast_id") != forecast_id or binding.get("forecast_sha256") != sha(frozen):
+        return False
+    if binding.get("outcome_path") != f"research/framework_memory/outcome_memory/{forecast_id}.json":
+        return False
+    evidence_ref = f"research/framework_memory/settlement_evidence/{forecast_id}.json"
+    if binding.get("evidence_path") != evidence_ref or outcome.get("evidence_path") != evidence_ref:
+        return False
+    if evidence.get("forecast_id") != forecast_id or evidence.get("forecast_sha256") != sha(frozen):
+        return False
+    if binding.get("evidence_sha256") != sha(evidence) or outcome.get("evidence_sha256") != sha(evidence):
+        return False
+    if binding.get("settlement_target_utc") != outcome.get("settlement_target_utc"):
+
[TRUNCATED 16661 chars - no claim of full coverage]
```

### scripts/experiments/source_git_anchor.py (patch_chars=6385, included=5700)
```diff
@@ -0,0 +1,131 @@
+"""Bounded first accepted Git custody; no supplier/PIT or skill admission.
+
+Pins remote main once per registry. Missing/shallow history fails closed.
+Never fetches, deepens, rewrites refs or trusts PR/local-main as authority.
+"""
+from __future__ import annotations
+
+import hashlib
+import os
+import re
+import subprocess
+import time
+from datetime import datetime
+from pathlib import Path
+
+ALLOWED_ORIGINS = frozenset((
+    "https://github.com/Donh91/Investering-Framework-Archive-v1.git",
+    "https://github.com/Donh91/Investering-Framework-Archive-v1",
+    "git@github.com:Donh91/Investering-Framework-Archive-v1.git",
+))
+
+
+class SourceGitAnchorUnavailable(RuntimeError):
+    pass
+
+
+class SourceGitAnchorBudgetExceeded(SourceGitAnchorUnavailable):
+    """The whole registry build must stop; partial source coverage is unsafe."""
+
+
+def _git(root: Path, *args: str) -> bytes:
+    try:
+        env = dict(os.environ, GIT_NO_REPLACE_OBJECTS="1",
+                   GIT_NO_LAZY_FETCH="1", GIT_TERMINAL_PROMPT="0")
+        return subprocess.run(
+            ("git", "--no-replace-objects", "-C", str(root), *args),
+            check=True, capture_output=True, timeout=5, env=env,
+        ).stdout
+    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
+        raise SourceGitAnchorUnavailable("CANONICAL_MAIN_HISTORY_UNVERIFIED") from exc
+
+
+class AcceptedMainSource:
+    """Per-build immutable head and bounded path history lookup cache."""
+
+    def __init__(self, repo_root: Path, *, fixture_origin: str | None = None):
+        self.root = repo_root.resolve()
+        self.fixture_origin = fixture_origin
+        self.head: str | None = None
+        self.initialized = False
+        self.originals: dict[str, tuple[bytes, int]] = {}
+        self.lookups = 0
+        self.deadline = time.monotonic() + 15
+
+    def _main(self) -> str:
+        if not self.initialized:
+            self.initialized = True
+            if _git(self.root, "rev-parse", "--is-shallow-repository").strip() != b"false":
+                raise SourceGitAnchorUnavailable("SHALLOW_HISTORY")
+            if _git(self.root, "for-each-ref", "--format=%(refname)", "refs/replace").strip():
+                raise SourceGitAnchorUnavailable("REPLACED_HISTORY")
+            graft = _git(self.root, "rev-parse", "--git-path", "info/grafts").decode().strip()
+            graft_path = Path(graft) if Path(graft).is_absolute() else self.root / graft
+            if graft_path.exists():
+                raise SourceGitAnchorUnavailable("GRAFTED_HISTORY")
+            url = _git(self.root, "remote", "get-url", "origin").decode().strip()
+            if url not in ({self.fixture_origin} if self.fixture_origin else ALLOWED_ORIGINS):
+                raise SourceGitAnchorUnavailable("WRONG_ORIGIN")
+            remote = _git(self.root, "ls-remote", "--exit-code", "origin", "refs/heads/main").decode()
+            match = re.fullmatch(r"([0-9a-f]{40})\s+refs/heads/main\s*", remote)
+            if match is None:
+                raise SourceGitAnchorUnavailable("MAIN_UNAVAILABLE")
+            head = match.group(1)
+            _git(self.root, "cat-file", "-e", head + "^{commit}")
+            self.head = head
+        if self.head is None:
+            raise SourceGitAnchorUnavailable("MAIN_UNAVAILABLE")
+        return self.head
+
+    def matches(self, relative_path: Path, expected_sha256: str, *,
+                accepted_before: datetime | None = None,
+                accepted_after: datetime | None = None) -> bool:
+        try:
+            if time.monotonic() > self.deadline or self.lookups >= 128:
+                raise SourceGitAnchorBudgetExceeded("SOURCE_ANCHOR_LOOKUP_BUDGET_EXCEEDED")
+            if not isinstance(expected_sha256, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
+                return False
+            rel = Path(relative_path)
+            if rel.is_absolute() or not rel.parts or ".." in rel.parts:
+                return False
+            path = self.root / rel
+            if (path.is_symlink() or not path.is_file() or path.resolve() != path
+                    or path.stat().st_size > 10_000_000):
+                return False
+            head = self._main()
+            key = rel.as_posix()
+            if key not in self.originals:
+                self.lookups += 1
+                revisions = _git(self.root, "rev-list", "--reverse", "--first-parent",
+                                 head, "--", key).splitlines()
+                if not revisions:
+                    return False
+                first = revisions[0].decode("ascii")
+                _git(self.root, "merge-base", "--is-ancestor", first, head)
+                entry = _git(self.root, "ls-tree", first, "--", key).decode()
+                if not entry.startswith(("100644 blob ", "100755 blob ")):
+                    return False
+                if int(_git(self.root, "cat-file", "-s", f"{first}:{key}")) > 10_000_000:
+                    return False
+                original = _git(self.root, "show", f"{first}:{key}")
+                self.originals[key] = (original, 0)
+            original, _untrusted_commit_clock = self.originals[key]
+            # Git author/committer timestamps are contributor-controlled. They
+            # prove object custody, not when GitHub accepted an object to main.
+            # Until a separately authenticated server-side acceptance receipt
+            # is supplied, temporal/PIT predicates must remain UNKNOWN/false.
+            if accepted_before is not None or accepted_after is not None:
+                return False
[TRUNCATED 685 chars - no claim of full coverage]
```

### scripts/research/monthly_ai_learning_council.py (patch_chars=2408, included=2408)
```diff
@@ -44,16 +44,18 @@ def compact_experiment_registry(registry: dict[str, Any], limit: int = 100) -> d
         state = str(row.get("state") or "UNKNOWN")
         states[state] = states.get(state, 0) + 1
         matured = int(row.get("matured_outcome_count", 0) or 0)
+        eligible = int(row.get("scientific_score_eligible_outcome_count", 0) or 0)
         if matured > 0 or state.startswith("MATURED"):
             rows.append({
                 "candidate_id": row.get("candidate_id"),
                 "title": row.get("title"),
                 "kind": row.get("kind"),
                 "state": state,
                 "matured_outcome_count": matured,
+                "scientific_score_eligible_outcome_count": eligible,
                 "scientific_admission_status": row.get("scientific_admission_status"),
             })
-    rows.sort(key=lambda x: (-int(x.get("matured_outcome_count", 0)), str(x.get("candidate_id"))))
+    rows.sort(key=lambda x: (-int(x.get("scientific_score_eligible_outcome_count", 0)), str(x.get("candidate_id"))))
     return {
         "contract": registry.get("contract"),
         "candidate_count": len([x for x in registry.get("candidates", []) if isinstance(x, dict)]),
@@ -198,11 +200,17 @@ def deterministic_claims(context: dict[str, Any], floor: int) -> tuple[list[dict
     learned, challenged = [], []
     rows = context.get("evidence_census", {}).get("experiment_registry", {}).get("matured_candidates", []) or []
     for row in rows:
-        n = int(row.get("matured_outcome_count", 0) or 0)
+        # Lifecycle maturity is not equivalent to scientific score eligibility.
+        # Old snapshots lacking the explicit eligible denominator fail closed.
+        n = int(row.get("scientific_score_eligible_outcome_count", 0) or 0)
         if n < floor:
             continue
         state = str(row.get("state") or "")
-        compact = {"candidate_id": row.get("candidate_id"), "title": row.get("title"), "matured_outcome_count": n, "state": state}
+        compact = {
+            "candidate_id": row.get("candidate_id"), "title": row.get("title"),
+            "matured_outcome_count": int(row.get("matured_outcome_count", 0) or 0),
+            "scientific_score_eligible_outcome_count": n, "state": state,
+        }
         if state == "MATURED_SUPPORTED":
             learned.append(compact)
         elif state == "MATURED_NOT_SUPPORTED":
```

### tests/experiments/test_experiment_lifecycle.py (patch_chars=33836, included=5700)
```diff
@@ -1,4 +1,5 @@
 import json
+import os
 import subprocess
 import sys
 import tempfile
@@ -112,4 +113,548 @@ def test_same_capture_forecasts_share_event_window_and_frozen_controls(self):
                 self.assertEqual(row["controls"]["control_freeze_time_utc"],"2026-08-05T10:00:00Z");self.assertEqual(row["controls"]["always_wait"],"ALWAYS_WAIT");self.assertEqual(row["unit_contract_version"],"FORECAST_TARGET_UNITS_v2")
 
 
+
+class CensoredOutcomeIntegrityTests(unittest.TestCase):
+    """Task2 science: raw receipt != MATURED != scientifically scoreable."""
+
+    def sample_registry(self, root: Path, outcomes: list[dict], forecasts=None):
+        from scripts.experiments.experiment_lifecycle import registry
+        cr=root/"candidates"; ob=root/"observations"; fr=root/"forecasts"
+        oc=root/"outcomes"; rc=root/"receipts"
+        for folder in (cr,ob,fr,oc,rc):
+            folder.mkdir(parents=True,exist_ok=True)
+        (cr/"test.json").write_text(json.dumps({
+            "contract":"EXPERIMENT_CANDIDATE_v1","candidate_id":"EC-censor",
+            "created_at_utc":"2026-09-01T00:00:00Z",
+            "spec":{"kind":"SENSOR_COMBINATION","title":"Synthetic sensor control"}
+        }))
+        ids=forecasts or [str(x.get("forecast_id")) for x in outcomes]
+        from scripts.experiments.experiment_lifecycle import sha
+        frozen_by_id={}
+        for i,fid in enumerate(ids):
+            frozen={
+                "contract":"FROZEN_FORECAST_v1",
+                "source_candidate_id":"EC-censor","forecast_id":fid,
+                "unit_contract_version":"FORECAST_TARGET_UNITS_v2",
+                "frozen_at_utc":"2026-09-01T00:00:00Z",
+                "outcome_due_utc":"2026-09-02T00:00:00Z",
+                "settlement_contract_version":"FORECAST_SETTLEMENT_EXACT_TARGET_TIME_v1",
+                "scientific_admission":{"status":"QUALIFIED_FOR_FORWARD_TEST"},
+                "metric_path":"market_metrics.spot.BTCUSDT.close",
+                "metric_path_root":"CAPTURE_DOCUMENT_ROOT",
+                "direction":"UP","start_value":100.0,
+                "threshold_pct":1.0,"target_mode":"PCT_MOVE",
+            }
+            frozen_by_id[fid]=frozen
+            (fr/f"{i}.json").write_text(json.dumps(frozen))
+        # Establish an isolated accepted-main trust root BEFORE outcome data.
+        # Production never accepts this test remote from a forecast field.
+        from unittest.mock import patch
+        origin = root / ".fixture-origin.git"
+        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
+        def fixture_git(*args, stamp="2026-09-01T00:00:01Z"):
+            return subprocess.run(["git", "-C", str(root), *args], check=True,
+                capture_output=True, env=dict(os.environ, GIT_AUTHOR_NAME="Fixture",
+                GIT_AUTHOR_EMAIL="fixture@example.invalid", GIT_COMMITTER_NAME="Fixture",
+                GIT_COMMITTER_EMAIL="fixture@example.invalid", GIT_AUTHOR_DATE=stamp,
+                GIT_COMMITTER_DATE=stamp))
+        fixture_git("init", "-q", "-b", "main")
+        fixture_git("remote", "add", "origin", origin.as_uri())
+        fixture_git("add", "forecasts", "candidates")
+        fixture_git("commit", "-qm", "first prospective forecast fixture")
+        allow = patch("scripts.experiments.source_git_anchor.ALLOWED_ORIGINS", {origin.as_uri()})
+        allow.start()
+        self.addCleanup(allow.stop)
+        bindings=root/"settlement_bindings"
+        evidence_root=root/"settlement_evidence"
+        bindings.mkdir(); evidence_root.mkdir()
+        for i,original in enumerate(outcomes):
+            outcome=dict(original)
+            fid=outcome["forecast_id"]
+            frozen=frozen_by_id[fid]
+            expected=original.get("result")
+            price=102.0 if expected=="HIT" else 100.2 if expected=="MISS" else 100.0
+            # Full synthetic RAW source is required by the *original*
+            # canonical settlement validator (not only a self-hashed JSON).
+            import hashlib
+            raw_path=root/"raw"/fid/"source.json"
+            raw_path.parent.mkdir(parents=True,exist_ok=True)
+            from datetime import datetime,timedelta,timezone
+            due=datetime.fromisoformat(frozen["outcome_due_utc"].replace("Z","+00:00"))
+            prior=due-timedelta(minutes=1)
+            open_ms=int(prior.timestamp()*1000)
+            close_ms=int(due.timestamp()*1000)-1
+            # Real 1m Binance row shape, made from entirely synthetic prices.
+            # Only the original raw close may establish a scoreable outcome.
+            raw_bytes=json.dumps([[open_ms,"100","104","99",str(price),
+                                   "1",close_ms]],separators=(",",":")).encode()
+            raw_path.write_bytes(raw_bytes)
+            evidence={"contract":"FORECAST_SETTLEMENT_EVIDENCE_v1",
+                      "forecast_id":fid,"forecast_sha256":sha(frozen),
+                      "settlement_contract_version":frozen["settlement_contract_version"],
+                      "settlement_target_utc":frozen["outcome_due_utc"],
+                      "captured_at_utc":frozen["outcome_due_utc"],
+                      "captured_at_semantics":"ADJUDICATION_TARGET_TIME_NOT_SOURCE_OBSERVATION",
+                      "metric_path":frozen["metric_path"],
+                      "source_candle_confirmed":True,
+                      "source_candle_open_utc":prior.isoformat().replace("+00:00","Z"),
+                      "source_candle_close_utc":(due-timedelta(milliseconds=1)).isoformat().replace("+00:00","Z"),
+                      "source_candle_offset_seconds":-0.001,
+     
[TRUNCATED 28136 chars - no claim of full coverage]
```

### tests/experiments/test_source_git_anchor.py (patch_chars=7915, included=5700)
```diff
@@ -0,0 +1,154 @@
+"""Offline adversarial tests of canonical first Git publication anchoring."""
+import hashlib
+import subprocess
+import tempfile
+import unittest
+from pathlib import Path
+
+from scripts.experiments.source_git_anchor import AcceptedMainSource, first_accepted_main_raw
+
+
+def git(root, *args):
+    return subprocess.run(("git", "-C", str(root), *args), check=True,
+                          capture_output=True, timeout=10).stdout
+
+
+class CanonicalSourceAnchorTests(unittest.TestCase):
+    def setUp(self):
+        self.tmp = tempfile.TemporaryDirectory()
+        self.addCleanup(self.tmp.cleanup)
+        parent = Path(self.tmp.name)
+        self.root = parent / "checkout"
+        self.root.mkdir()
+        self.origin = parent / "origin.git"
+        git(parent, "init", "-q", "--bare", str(self.origin))
+        git(self.root, "init", "-q", "-b", "main")
+        git(self.root, "config", "user.name", "SyntheticFixture")
+        git(self.root, "config", "user.email", "fixture@example.invalid")
+        git(self.root, "remote", "add", "origin", self.origin.as_uri())
+        self.rel = Path("raw/EXP-FC-test/source.json")
+        self.source = self.root / self.rel
+        self.source.parent.mkdir(parents=True)
+        self.original = b'[[1,"100","104","99","100.2","1",59999]]'
+        self.source.write_bytes(self.original)
+        git(self.root, "add", self.rel.as_posix())
+        git(self.root, "commit", "-qm", "first accepted synthetic receipt")
+        git(self.root, "push", "-q", "-u", "origin", "main")
+        self.digest = hashlib.sha256(self.original).hexdigest()
+
+    def check(self, digest=None, path=None, *, fixture=True):
+        kw = {"fixture_origin": self.origin.as_uri()} if fixture else {}
+        return first_accepted_main_raw(
+            self.root, self.rel if path is None else path,
+            self.digest if digest is None else digest, **kw,
+        )
+
+    def test_first_original_git_blob_accepted(self):
+        self.assertTrue(self.check())
+
+    def test_untrusted_pr_worktree_still_reads_remote_main(self):
+        git(self.root, "checkout", "-qb", "untrusted-pr")
+        self.assertTrue(self.check())
+
+    def test_coordinated_raw_digest_and_market_forgery_rejected(self):
+        forged = self.original.replace(b"100.2", b"102.0")
+        self.source.write_bytes(forged)
+        self.assertFalse(self.check(hashlib.sha256(forged).hexdigest()))
+
+    def test_later_canonical_commit_cannot_replace_first_acceptance(self):
+        forged = self.original.replace(b"100.2", b"102.0")
+        self.source.write_bytes(forged)
+        git(self.root, "add", self.rel.as_posix())
+        git(self.root, "commit", "-qm", "later mutation")
+        git(self.root, "push", "-q", "origin", "main")
+        self.assertFalse(self.check(hashlib.sha256(forged).hexdigest()))
+
+    def test_branch_only_source_not_accepted(self):
+        git(self.root, "checkout", "-qb", "untrusted-pr")
+        relative = Path("raw/EXP-FC-new/source.json")
+        extra = self.root / relative
+        extra.parent.mkdir(parents=True)
+        extra.write_bytes(b"forged")
+        git(self.root, "add", relative.as_posix())
+        git(self.root, "commit", "-qm", "PR-only fake source")
+        self.assertFalse(self.check(hashlib.sha256(b"forged").hexdigest(), relative))
+
+    def test_local_ref_override_does_not_override_remote(self):
+        git(self.root, "checkout", "-qb", "untrusted-pr")
+        self.source.write_bytes(b"counterfeit")
+        git(self.root, "add", self.rel.as_posix())
+        git(self.root, "commit", "-qm", "PR mutation")
+        git(self.root, "branch", "-f", "main", "HEAD")
+        self.assertFalse(self.check(hashlib.sha256(b"counterfeit").hexdigest()))
+
+    def test_remote_main_advances_without_trusting_stale_local_ref(self):
+        writer = Path(self.tmp.name) / "independent-writer"
+        subprocess.run(("git", "clone", "-q", "-b", "main", self.origin.as_uri(),
+                        str(writer)), check=True, capture_output=True, timeout=10)
+        git(writer, "config", "user.name", "IndependentSyntheticPublisher")
+        git(writer, "config", "user.email", "independent@example.invalid")
+        (writer / "unrelated.txt").write_text("unrelated new official main publication")
+        git(writer, "add", "unrelated.txt")
+        git(writer, "commit", "-qm", "legitimate later unrelated update")
+        git(writer, "push", "-q", "origin", "main")
+        first_local_main = git(self.root, "rev-parse", "main").decode().strip()
+        self.assertFalse(self.check(), "Missing current-main objects must not trigger an implicit fetch")
+        git(self.root, "fetch", "-q", "origin", "main")
+        self.assertTrue(self.check())
+        self.assertEqual(git(self.root, "rev-parse", "main").decode().strip(),
+                         first_local_main)
+
+    def test_untrusted_remote_and_missing_remote_fail_closed(self):
+        self.assertFalse(self.check(fixture=False))
+        git(self.root, "remote", "remove", "origin")
+        self.assertFalse(self.check())
+
+    def test_wrong_digest_missing_raw_and_escape_fail_closed(self):
+        self.assertFalse(self.check("0" * 64))
+        self.assertFalse(self.check(path=Path("../raw/EXP-FC-test/source.json")))
+        self.source.unlink()
+        self.assertFalse(self.check())
+
+    def test_symlink_fails_closed(self):
+        self.source.unlink()
+        self.source.symlink_to(self.origin)
+        self.assertFalse(self.check())
+
+    def test_shallow_history_fails_closed(self):
+        parent = Path(self.tmp.name)
+        git(self.root, "commit", "--allow-empt
[TRUNCATED 2215 chars - no claim of full coverage]
```

### tests/research/test_monthly_ai_learning_council.py (patch_chars=1525, included=1525)
```diff
@@ -73,13 +73,15 @@ def test_ai_hypothesis_is_research_only_candidate(self) -> None:
 
     def test_learning_claim_requires_floor(self) -> None:
         ctx = {"evidence_census": {"experiment_registry": {"matured_candidates": [
-            {"candidate_id": "A", "state": "MATURED_SUPPORTED", "matured_outcome_count": 24},
-            {"candidate_id": "B", "state": "MATURED_SUPPORTED", "matured_outcome_count": 25},
-            {"candidate_id": "C", "state": "MATURED_NOT_SUPPORTED", "matured_outcome_count": 30},
+            {"candidate_id": "A", "state": "MATURED_SUPPORTED", "matured_outcome_count": 24, "scientific_score_eligible_outcome_count": 24},
+            {"candidate_id": "B", "state": "MATURED_SUPPORTED", "matured_outcome_count": 25, "scientific_score_eligible_outcome_count": 25},
+            {"candidate_id": "C", "state": "MATURED_NOT_SUPPORTED", "matured_outcome_count": 30, "scientific_score_eligible_outcome_count": 30},
+            {"candidate_id": "MIXED", "state": "MATURED_SUPPORTED", "matured_outcome_count": 25, "scientific_score_eligible_outcome_count": 1},
         ]}}}
         learned, challenged = deterministic_claims(ctx, 25)
         self.assertEqual([x["candidate_id"] for x in learned], ["B"])
         self.assertEqual([x["candidate_id"] for x in challenged], ["C"])
+        self.assertNotIn("MIXED", [x["candidate_id"] for x in learned + challenged])
 
     def test_finalize_preserves_firewall_when_ai_missing(self) -> None:
         with tempfile.TemporaryDirectory() as td:
```