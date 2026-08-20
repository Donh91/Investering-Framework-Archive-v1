#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LAB = REPO / "06_RESEARCH_LAB" / "historical_altseason_pullback_v1"
ART = LAB / "artifacts"
PROMPT = REPO / "07_PROMPTS_AND_AGENTS" / "historical_altseason_pullback" / "COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md"
DIST = REPO / "dist" / "cowork_historical_altseason"
STAGE = DIST / "COWORK_RESEARCH_INPUT"
ZIP_PATH = DIST / "HISTORICAL_ALTSEASON_COWORK_INPUT_BUNDLE.zip"
MANIFEST_PATH = DIST / "COWORK_INPUT_MANIFEST.json"
SHA_PATH = DIST / "COWORK_INPUT_BUNDLE_SHA256.txt"

MAX_INDIVIDUAL_FILE_BYTES = 250 * 1024 * 1024

REQUIRED_BASE = [
    LAB / "config.json",
    LAB / "README.md",
    LAB / "CLAUDE_COWORK_DEEP_RESEARCH_BRIEF.md",
    PROMPT,
]

CORE_SELECTED_PATHS = [
    LAB,
    REPO / "scripts" / "historical_lab",
    REPO / ".github" / "workflows" / "historical-altseason-lab-gate.yml",
    REPO / ".github" / "workflows" / "historical-altseason-free-bootstrap.yml",
    REPO / ".github" / "workflows" / "historical-altseason-cfgi-enrichment.yml",
    PROMPT,
]

PROSPECTIVE_SELECTED_PATHS = [
    REPO / "00_ARCHIVE_CONTROL",
    REPO / "01_CORE_FRAMEWORK",
    REPO / "04_MARKET_LEARNING" / "entry_signals",
    REPO / "04_MARKET_LEARNING" / "breadth",
    REPO / "04_MARKET_LEARNING" / "pullback_learning",
    REPO / "04_MARKET_LEARNING" / "rotation_survival",
    REPO / "04_MARKET_LEARNING" / "stress_flush",
    REPO / "04_MARKET_LEARNING" / "sensor_tournament",
    REPO / "04_MARKET_LEARNING" / "truth_layer",
    REPO / "04_MARKET_LEARNING" / "forward_tests",
    REPO / "04_MARKET_LEARNING" / "data_ping",
    REPO / "04_MARKET_LEARNING" / "master_monday",
    REPO / "04_MARKET_LEARNING" / "cycle_navigator",
    REPO / "04_MARKET_LEARNING" / "etf",
    REPO / "04_MARKET_LEARNING" / "stablecoin_deployment",
    REPO / "04_MARKET_LEARNING" / "stablecoin_validation",
    REPO / "03_DAILY_CAPTURE_LOGS" / "hourly",
    REPO / "03_DAILY_CAPTURE_LOGS" / "breadth_rich",
    REPO / "03_DAILY_CAPTURE_LOGS" / "pullback_forensics",
    REPO / "03_DAILY_CAPTURE_LOGS" / "cfgi_weekly",
    REPO / "03_DAILY_CAPTURE_LOGS" / "stablecoin_liquidity",
    REPO / "03_DAILY_CAPTURE_LOGS" / "etf",
]

SECRET_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
SECRET_NAMES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
SKIP_PARTS = {".git", "__pycache__", "node_modules", ".venv", "venv", "dist"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()


def safe_file(path: Path) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    rel_parts = set(path.relative_to(REPO).parts)
    if rel_parts & SKIP_PARTS:
        return False
    if path.name in SECRET_NAMES or path.suffix.lower() in SECRET_SUFFIXES:
        return False
    if path.stat().st_size > MAX_INDIVIDUAL_FILE_BYTES:
        return False
    return True


def iter_source_files(path: Path):
    if not path.exists():
        return
    if path.is_file():
        if safe_file(path):
            yield path
        return
    for item in sorted(path.rglob("*")):
        if safe_file(item):
            yield item


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_readiness() -> dict:
    for path in REQUIRED_BASE:
        if not path.exists() or path.stat().st_size == 0:
            raise SystemExit(f"COWORK_BUNDLE_BLOCKED missing_base={path.relative_to(REPO)}")

    cfg = load_json(LAB / "config.json")
    readiness_cfg = cfg["readiness"]

    required_artifacts = list(readiness_cfg["free_stage_required_artifacts"]) + list(
        readiness_cfg["cfgi_stage_required_artifacts"]
    )
    required_artifacts.append("RESEARCH_READINESS_MANIFEST.json")

    missing = []
    for name in sorted(set(required_artifacts)):
        p = ART / name
        if not p.exists() or p.stat().st_size == 0:
            missing.append(name)
    if missing:
        raise SystemExit(f"COWORK_BUNDLE_BLOCKED missing_artifacts={missing}")

    manifest = load_json(ART / "RESEARCH_READINESS_MANIFEST.json")
    if manifest.get("readiness_verdict") != "PASS":
        raise SystemExit(
            f"COWORK_BUNDLE_BLOCKED readiness={manifest.get('readiness_verdict')} blockers={manifest.get('blockers')}"
        )
    if manifest.get("blockers"):
        raise SystemExit(f"COWORK_BUNDLE_BLOCKED blockers={manifest.get('blockers')}")
    if manifest.get("automatic_promotion") is not False:
        raise SystemExit("COWORK_BUNDLE_BLOCKED automatic_promotion_not_false")
    if manifest.get("historical_findings_max_classification") != "FORWARD_TEST":
        raise SystemExit("COWORK_BUNDLE_BLOCKED historical_promotion_ceiling_changed")

    billing = load_json(ART / "CFGI_BILLING.json")
    g = cfg["cfgi"]
    if billing.get("status") != "PASS":
        raise SystemExit(f"COWORK_BUNDLE_BLOCKED cfgi_billing_status={billing.get('status')}")
    expected = billing.get("expected_worst_case_credits")
    actual = billing.get("actual_credits_used_from_headers")
    remaining = billing.get("final_credits_remaining")
    if expected is None or expected > g["expected_credit_hard_cap"]:
        raise SystemExit("COWORK_BUNDLE_BLOCKED cfgi_expected_credit_guard")
    if actual is not None and actual > g["expected_credit_hard_cap"] + 1:
        raise SystemExit("COWORK_BUNDLE_BLOCKED cfgi_actual_credit_guard")
    if remaining is None or remaining < g["minimum_credits_reserve"]:
        raise SystemExit("COWORK_BUNDLE_BLOCKED cfgi_reserve_guard")

    authority = cfg["authority"]
    required_authority = {
        "research_only": True,
        "portfolio_execution": False,
        "canonical_market_state": False,
        "automatic_rule_changes": False,
        "promotion_requires_separate_review": True,
    }
    for key, expected_value in required_authority.items():
        if authority.get(key) is not expected_value:
            raise SystemExit(f"COWORK_BUNDLE_BLOCKED authority={key}")

    return {
        "readiness_manifest": manifest,
        "cfgi_billing": billing,
        "authority": authority,
        "required_artifacts": sorted(set(required_artifacts)),
    }


def copy_file(src: Path, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def build_bundle():
    readiness = validate_readiness()

    if DIST.exists():
        shutil.rmtree(DIST)
    STAGE.mkdir(parents=True, exist_ok=True)

    included: list[dict] = []
    optional_missing: list[str] = []
    skipped_large: list[dict] = []
    seen: set[Path] = set()

    selections = [("CORE", p) for p in CORE_SELECTED_PATHS] + [
        ("PROSPECTIVE_2026", p) for p in PROSPECTIVE_SELECTED_PATHS
    ]

    for section, selection in selections:
        if not selection.exists():
            optional_missing.append(str(selection.relative_to(REPO)))
            continue
        candidates = [selection] if selection.is_file() else sorted(selection.rglob("*"))
        for src in candidates:
            if not src.is_file() or src.is_symlink():
                continue
            if src in seen:
                continue
            rel_repo = src.relative_to(REPO)
            if set(rel_repo.parts) & SKIP_PARTS:
                continue
            if src.name in SECRET_NAMES or src.suffix.lower() in SECRET_SUFFIXES:
                continue
            size = src.stat().st_size
            if size > MAX_INDIVIDUAL_FILE_BYTES:
                skipped_large.append({"path": str(rel_repo), "size_bytes": size})
                continue
            seen.add(src)
            dest = STAGE / section / "REPO" / rel_repo
            copy_file(src, dest)
            included.append(
                {
                    "section": section,
                    "source_path": str(rel_repo),
                    "bundle_path": str(dest.relative_to(STAGE)),
                    "size_bytes": size,
                    "sha256": sha256(src),
                }
            )

    prompt_dest = STAGE / "PROMPT" / PROMPT.name
    copy_file(PROMPT, prompt_dest)

    bundle_readme = STAGE / "BUNDLE_README.md"
    bundle_readme.write_text(
        "# Historical Altseason Cowork Research Input Bundle\n\n"
        "Start with `PROMPT/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md`.\n\n"
        "The CORE section contains the historical laboratory, its artifacts, code and workflow contracts.\n"
        "The PROSPECTIVE_2026 section contains selected framework evidence for out-of-sample comparison only.\n\n"
        "The research is strictly research-only. Historical findings may not be promoted above FORWARD_TEST.\n",
        encoding="utf-8",
    )

    source_selection = {
        "core": [str(p.relative_to(REPO)) for p in CORE_SELECTED_PATHS],
        "prospective_2026": [str(p.relative_to(REPO)) for p in PROSPECTIVE_SELECTED_PATHS],
        "selection_principle": "Historical lab complete, plus targeted 2026 entry, breadth, pullback, rotation, stress, CFGI, liquidity, ETF and governance evidence.",
    }

    manifest = {
        "contract": "COWORK_HISTORICAL_ALTSEASON_INPUT_MANIFEST_v1",
        "generated_at_utc": utc_now(),
        "repo_head": git_head(),
        "authority": readiness["authority"],
        "readiness_verdict": readiness["readiness_manifest"].get("readiness_verdict"),
        "historical_findings_max_classification": "FORWARD_TEST",
        "automatic_promotion": False,
        "cfgi_billing_summary": {
            "status": readiness["cfgi_billing"].get("status"),
            "expected_worst_case_credits": readiness["cfgi_billing"].get("expected_worst_case_credits"),
            "actual_credits_used_from_headers": readiness["cfgi_billing"].get("actual_credits_used_from_headers"),
            "final_credits_remaining": readiness["cfgi_billing"].get("final_credits_remaining"),
        },
        "source_selection": source_selection,
        "included_file_count": len(included),
        "included_total_bytes": sum(x["size_bytes"] for x in included),
        "optional_missing": optional_missing,
        "skipped_large_files": skipped_large,
        "files": included,
        "cowork_entrypoint": "PROMPT/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md",
        "expected_output_zip": "HISTORICAL_ALTSEASON_COWORK_OPUS5_RESEARCH_PACKAGE.zip",
    }

    stage_manifest = STAGE / "COWORK_INPUT_MANIFEST.json"
    stage_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(STAGE.rglob("*")):
            if path.is_file():
                zf.write(path, arcname=str(Path("COWORK_RESEARCH_INPUT") / path.relative_to(STAGE)))

    zip_sha = sha256(ZIP_PATH)
    SHA_PATH.write_text(f"{zip_sha}  {ZIP_PATH.name}\n", encoding="utf-8")

    # Open-test the final archive and ensure its embedded manifest exists.
    with zipfile.ZipFile(ZIP_PATH, "r") as zf:
        bad = zf.testzip()
        if bad is not None:
            raise SystemExit(f"COWORK_BUNDLE_BLOCKED corrupt_zip_member={bad}")
        names = set(zf.namelist())
        required_zip_members = {
            "COWORK_RESEARCH_INPUT/COWORK_INPUT_MANIFEST.json",
            "COWORK_RESEARCH_INPUT/PROMPT/COWORK_OPUS5_MASTER_RESEARCH_PROMPT.md",
            "COWORK_RESEARCH_INPUT/BUNDLE_README.md",
        }
        if not required_zip_members.issubset(names):
            raise SystemExit("COWORK_BUNDLE_BLOCKED required_zip_members_missing")

    result = {
        "status": "PASS",
        "zip": str(ZIP_PATH.relative_to(REPO)),
        "zip_sha256": zip_sha,
        "files": len(included),
        "bytes": ZIP_PATH.stat().st_size,
        "repo_head": manifest["repo_head"],
        "readiness": manifest["readiness_verdict"],
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    try:
        build_bundle()
    except subprocess.CalledProcessError as exc:
        print(f"COWORK_BUNDLE_BLOCKED git_error={exc}", file=sys.stderr)
        raise
