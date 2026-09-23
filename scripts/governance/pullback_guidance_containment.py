from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Iterable

LABELS = ("MILD", "MODERATE", "LARGE", "EXTREME")
FORBIDDEN_ACTIONS = ("TRIM", "TRIM_A_BID", "REDUCE", "EXIT", "SELL")
FORBIDDEN_REBUY = ("UNLOCK", "LOCK", "ACTIVE", "BLOCKED")
FORBIDDEN_CALIBRATION = ("HIT", "MISS", "SUCCESS", "FAILURE", "FAILED")
REQUIRED_REPRO_FIELDS = (
    "measurement_asset",
    "reference_anchor",
    "reference_time",
    "drawdown_method",
    "drawdown_value",
    "volatility_adjustment",
    "classification_band_source",
    "hard_trigger_count",
    "hard_trigger_definitions",
    "source_quality",
    "framework_acceptance",
)
ACTIVE_PROMPT_PATHS = (
    Path("07_PROMPTS_AND_AGENTS/prompts/HANDLEKOMPAS_v1.md"),
    Path("07_PROMPTS_AND_AGENTS/action_compass/GLOBAL_ACTION_COMPASS_ROUTE_v1.json"),
    Path("07_PROMPTS_AND_AGENTS/action_compass/2026-09-16__global-action-compass-invocation-contract-v1__canonical.md"),
)
ACTIVE_SCRIPT_ROOTS = (
    Path("scripts/data_ping"),
    Path("scripts/pullback_learning"),
    Path("scripts/intraday_execution"),
)
BOUNDARY_MARKERS = (
    "GUIDANCE_ONLY",
    "QUALITATIVE_LABEL_ALONE",
    "NOT_AUTOMATIC",
    "DO NOT INFER",
    "NEVER INFER",
    "CANNOT",
    "MUST NOT",
    "FORBIDDEN",
)


def normalized(text: str) -> str:
    return text.upper().replace("→", "->")


def has_full_reproducibility_authority(text: str) -> bool:
    upper = normalized(text)
    if not all(field.upper() in upper for field in REQUIRED_REPRO_FIELDS):
        return False
    return bool(
        re.search(r'["\']?OWNER_AUTHORIZED["\']?\s*[:=]\s*(?:TRUE|["\']TRUE["\'])', upper)
        or re.search(r'MECHANICAL_CLASSIFICATION_AUTHORITY\s*[:=]\s*(?:AUTHORIZED|OWNER_AUTHORIZED)', upper)
    )


def context_windows(text: str, radius: int = 260) -> Iterable[str]:
    upper = normalized(text)
    for match in re.finditer(r"PULLBACK", upper):
        start = max(0, match.start() - radius)
        end = min(len(upper), match.end() + radius)
        yield upper[start:end]


def _contains_label(text: str) -> bool:
    return any(re.search(rf"\b{label}\b", text) for label in LABELS)


def _direct_mapping(window: str) -> bool:
    labels = "|".join(LABELS)
    actions = "|".join(FORBIDDEN_ACTIONS)
    mapping = re.compile(
        rf"\b(?:{labels})\b\s*(?:->|=>|=|:)\s*(?:[^\n]{{0,50}}\b(?:{actions})\b)",
        re.IGNORECASE,
    )
    return bool(mapping.search(window))


def _structured_action_mapping(window: str) -> bool:
    if not _contains_label(window):
        return False
    patterns = (
        r'["\']?(?:PORTFOLIO_)?ACTION["\']?\s*[:=]\s*["\']?(?:TRIM|TRIM_A_BID|REDUCE|EXIT|SELL)\b',
        r'["\']?REBUY(?:_STATE|_STATUS)?["\']?\s*[:=]\s*["\']?(?:UNLOCK|LOCK|ACTIVE|BLOCKED)\b',
        r'["\']?RECOVERY(?:_FAILURE|_STATE)?["\']?\s*[:=]\s*["\']?(?:FAIL|FAILED|FAILURE|TRUE)\b',
        r'["\']?CALIBRATION(?:_OUTCOME|_STATE|_VERDICT)?["\']?\s*[:=]\s*["\']?(?:HIT|MISS|SUCCESS|FAILURE|FAILED)\b',
    )
    return any(re.search(pattern, window, re.IGNORECASE) for pattern in patterns)


def _conditional_mechanical_use(window: str) -> bool:
    if not _contains_label(window):
        return False
    labels = "|".join(LABELS)
    effects = "|".join((*FORBIDDEN_ACTIONS, *FORBIDDEN_CALIBRATION, "REBUY", "RECOVERY_FAILURE"))
    return bool(
        re.search(
            rf"(?:IF|WHEN|CASE).{{0,120}}\b(?:{labels})\b.{{0,140}}(?:RETURN|ACTION|REBUY|RECOVERY|CALIBRATION).{{0,80}}\b(?:{effects})\b",
            window,
            re.IGNORECASE | re.DOTALL,
        )
    )


def inspect_text(text: str, source: str = "<memory>") -> list[dict]:
    if has_full_reproducibility_authority(text):
        return []
    findings: list[dict] = []
    for index, window in enumerate(context_windows(text), start=1):
        # Explicit negative/governance statements are evidence of containment,
        # not mechanical consumers. Only suppress when a boundary marker occurs
        # in the same local pullback context.
        boundary = any(marker in window for marker in BOUNDARY_MARKERS)
        direct = _direct_mapping(window)
        structured = _structured_action_mapping(window)
        conditional = _conditional_mechanical_use(window)
        if (direct or structured or conditional) and not boundary:
            findings.append(
                {
                    "source": source,
                    "window": index,
                    "reason": "QUALITATIVE_PULLBACK_LABEL_HAS_STANDALONE_MECHANICAL_EFFECT",
                    "direct_mapping": direct,
                    "structured_mapping": structured,
                    "conditional_mapping": conditional,
                }
            )
    return findings


def active_paths(repo_root: Path) -> list[Path]:
    paths: set[Path] = set()
    for root in ACTIVE_SCRIPT_ROOTS:
        full = repo_root / root
        if full.exists():
            paths.update(p for p in full.rglob("*.py") if p.is_file())
    for rel in ACTIVE_PROMPT_PATHS:
        full = repo_root / rel
        if full.is_file():
            paths.add(full)
    return sorted(paths)


def scan_repo(repo_root: Path) -> dict:
    findings: list[dict] = []
    scanned: list[str] = []
    for path in active_paths(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        scanned.append(rel)
        findings.extend(inspect_text(path.read_text(encoding="utf-8", errors="replace"), rel))
    return {
        "contract": "PULLBACK_GUIDANCE_CONTAINMENT_READOUT_v1",
        "policy": "PULLBACK_POLICY_V0_2",
        "policy_status": "GUIDANCE_ONLY",
        "mechanical_classification_authority": "SUSPENDED_UNTIL_SPEC_COMPLETE",
        "portfolio_action_from_qualitative_label_alone": False,
        "scanned_paths": scanned,
        "scanned_path_count": len(scanned),
        "violations": findings,
        "violation_count": len(findings),
        "status": "PASS" if not findings else "FAIL",
        "market_semantic_change": False,
        "threshold_change": False,
        "portfolio_authority_change": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--json-output", type=Path)
    args = parser.parse_args()
    result = scan_repo(args.repo_root)
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.json_output:
        args.json_output.parent.mkdir(parents=True, exist_ok=True)
        args.json_output.write_text(payload, encoding="utf-8")
    print(payload, end="")
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
