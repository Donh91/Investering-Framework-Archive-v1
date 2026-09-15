from __future__ import annotations

import argparse
import ast
import gzip
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Iterable

KEYWORDS = ("cohort", "launch", "rank", "score", "window", "wallet", "buyer", "pair", "union", "edge", "min_", "max_")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def member_by_basename(zf: zipfile.ZipFile, basename: str) -> str:
    for name in zf.namelist():
        if Path(name).name == basename:
            return name
    raise FileNotFoundError(basename)


def jsonl_rows(zf: zipfile.ZipFile, member: str) -> Iterable[dict[str, Any]]:
    raw = zf.read(member)
    stream = gzip.GzipFile(fileobj=io.BytesIO(raw), mode="rb") if member.endswith(".gz") else io.BytesIO(raw)
    for line in stream:
        if line.strip():
            yield json.loads(line)


def literal(value: ast.AST) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        return None


def is_relevant(name: str) -> bool:
    low = name.lower()
    return any(k in low for k in KEYWORDS)


def inspect_source(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    constants: dict[str, Any] = {}
    functions: list[str] = []
    comparisons: list[dict[str, Any]] = []
    assignments: list[dict[str, Any]] = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.Assign):
            value = literal(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name) and is_relevant(target.id):
                    assignments.append({"name": target.id, "literal_value": value})
                    if target.id.isupper():
                        constants[target.id] = value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            if is_relevant(name):
                value = literal(node.value) if node.value is not None else None
                assignments.append({"name": name, "literal_value": value})
                if name.isupper():
                    constants[name] = value
        elif isinstance(node, ast.Compare):
            text = ast.unparse(node)
            if any(k in text.lower() for k in KEYWORDS):
                comparisons.append({"expr": text[:300]})

    source_lines = source.splitlines()
    keyword_line_summaries: list[dict[str, Any]] = []
    for idx, line in enumerate(source_lines, start=1):
        low = line.lower()
        if any(k in low for k in ("min_", "cohort", "first_rank", "score", "n_launch", "union", "window_sec")):
            stripped = re.sub(r"\s+", " ", line.strip())
            if stripped and not stripped.startswith("#"):
                keyword_line_summaries.append({"line": idx, "sha256": hashlib.sha256(stripped.encode()).hexdigest(), "length": len(stripped)})

    return {
        "source_sha256": sha256_bytes(source.encode("utf-8")),
        "line_count": len(source_lines),
        "relevant_constants": constants,
        "relevant_assignments": assignments[:80],
        "function_names": sorted(functions),
        "relevant_comparisons": comparisons[:100],
        "keyword_line_fingerprints": keyword_line_summaries[:120],
        "raw_source_archived": False,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        detector_member = member_by_basename(zf, "analyze_sniper_cohorts.py")
        source_bytes = zf.read(detector_member)
        source = source_bytes.decode("utf-8")
        detector = inspect_source(source)

        catalogue_member = member_by_basename(zf, "sniper_cohorts.jsonl")
        intra_member = member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")
        catalogue = list(jsonl_rows(zf, catalogue_member))
        intra = list(jsonl_rows(zf, intra_member))

    catalogue_keys = sorted({k for row in catalogue for k in row})
    intra_keys = sorted({k for row in intra for k in row})
    result = {
        "experiment": "RED_COHORT_DETECTOR_SEMANTICS_PROBE_v1",
        "source": "RED-COHORT-2026-v1.1.1",
        "detector": detector,
        "catalogue": {
            "rows": len(catalogue),
            "keys": catalogue_keys,
            "n_launches_min": min((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "n_launches_max": max((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "cohort_size_min": min((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
            "cohort_size_max": max((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
        },
        "intra_launch": {
            "rows": len(intra),
            "keys": intra_keys,
            "window_sec_values": sorted({int(r.get("window_sec", 0)) for r in intra if r.get("window_sec") is not None}),
            "first_rank_min": min((int(r.get("first_rank", 0)) for r in intra), default=None),
            "first_rank_max": max((int(r.get("first_rank", 0)) for r in intra), default=None),
        },
        "scientific_question": "derive exact persistence criteria and then replay them causally in event-time order to compute earliest-knowable cohort timestamps",
        "authority": {
            "research_only": True,
            "automatic_trading": False,
            "buy_now_promotion": False,
            "live_threshold_change": False,
        },
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
