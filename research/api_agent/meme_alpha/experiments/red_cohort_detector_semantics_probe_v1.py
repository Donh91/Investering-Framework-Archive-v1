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
TARGET_CONSTANTS = {"FIRST_N_BUYERS", "MIN_LAUNCHES", "MAX_COHORT_SIZE"}
TARGET_FUNCTIONS = {"group_buyers_by_mint", "build_pair_counts", "merge_into_cohorts", "score_cohort", "main"}


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


def expr(node: ast.AST | None) -> str | None:
    if node is None:
        return None
    try:
        return ast.unparse(node)
    except Exception:
        return None


def is_relevant_text(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in KEYWORDS)


def function_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    args = list(node.args.posonlyargs) + list(node.args.args)
    defaults = [None] * (len(args) - len(node.args.defaults)) + list(node.args.defaults)
    params = []
    for arg, default in zip(args, defaults):
        params.append({"name": arg.arg, "default_expr": expr(default), "default_literal": literal(default) if default else None})
    return {"name": node.name, "parameters": params}


def function_operations(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    allowed = (ast.Assign, ast.AnnAssign, ast.AugAssign, ast.For, ast.If, ast.Return, ast.Expr)
    for sub in ast.walk(node):
        if not isinstance(sub, allowed):
            continue
        text = expr(sub)
        if not text or not is_relevant_text(text):
            continue
        compact = re.sub(r"\s+", " ", text.strip())
        out.append({"node": type(sub).__name__, "expr": compact[:800]})
    # stable unique order, favor shorter directly interpretable operations
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in sorted(out, key=lambda x: (len(x["expr"]), x["expr"])):
        if item["expr"] in seen:
            continue
        seen.add(item["expr"])
        deduped.append(item)
    return deduped[:100]


def inspect_source(source: str) -> dict[str, Any]:
    tree = ast.parse(source)
    constant_expressions: dict[str, str | None] = {}
    assignments: list[dict[str, Any]] = []
    comparisons: list[str] = []
    function_semantics: dict[str, Any] = {}

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in TARGET_FUNCTIONS:
            function_semantics[node.name] = {
                "signature": function_signature(node),
                "operations": function_operations(node),
            }
        elif isinstance(node, ast.Assign):
            rhs = expr(node.value)
            for target in node.targets:
                if isinstance(target, ast.Name) and is_relevant_text(target.id):
                    assignments.append({"name": target.id, "expr": rhs, "literal_value": literal(node.value)})
                    if target.id in TARGET_CONSTANTS:
                        constant_expressions[target.id] = rhs
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if is_relevant_text(node.target.id):
                rhs = expr(node.value)
                assignments.append({"name": node.target.id, "expr": rhs, "literal_value": literal(node.value) if node.value else None})
                if node.target.id in TARGET_CONSTANTS:
                    constant_expressions[node.target.id] = rhs
        elif isinstance(node, ast.AugAssign):
            text = expr(node)
            if text and is_relevant_text(text):
                assignments.append({"name": expr(node.target), "expr": text, "literal_value": None})
        elif isinstance(node, ast.Compare):
            text = expr(node)
            if text and is_relevant_text(text):
                comparisons.append(text)

    source_lines = source.splitlines()
    fingerprints = []
    for idx, line in enumerate(source_lines, start=1):
        stripped = re.sub(r"\s+", " ", line.strip())
        if stripped and not stripped.startswith("#") and is_relevant_text(stripped):
            fingerprints.append({"line": idx, "sha256": sha256_bytes(stripped.encode()), "length": len(stripped)})

    return {
        "source_sha256": sha256_bytes(source.encode()),
        "line_count": len(source_lines),
        "constant_expressions": {k: constant_expressions.get(k) for k in sorted(TARGET_CONSTANTS)},
        "relevant_assignments": assignments[:160],
        "relevant_comparisons": sorted(set(comparisons)),
        "target_function_semantics": function_semantics,
        "keyword_line_fingerprints": fingerprints[:180],
        "raw_source_archived": False,
    }


def archive_inventory(zf: zipfile.ZipFile) -> list[dict[str, Any]]:
    out = []
    for info in zf.infolist():
        if info.is_dir():
            continue
        out.append({
            "basename": Path(info.filename).name,
            "path_sha256": sha256_bytes(info.filename.encode()),
            "uncompressed_bytes": info.file_size,
            "compressed_bytes": info.compress_size,
        })
    return sorted(out, key=lambda x: x["basename"])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with zipfile.ZipFile(args.zip) as zf:
        inventory = archive_inventory(zf)
        detector_member = member_by_basename(zf, "analyze_sniper_cohorts.py")
        source = zf.read(detector_member).decode("utf-8")
        detector = inspect_source(source)
        catalogue = list(jsonl_rows(zf, member_by_basename(zf, "sniper_cohorts.jsonl")))
        intra = list(jsonl_rows(zf, member_by_basename(zf, "sniper_cohorts_intra.jsonl.gz")))

    result = {
        "experiment": "RED_COHORT_DETECTOR_SEMANTICS_PROBE_v1_2",
        "source": "RED-COHORT-2026-v1.1.1",
        "archive_inventory": inventory,
        "detector": detector,
        "catalogue": {
            "rows": len(catalogue),
            "n_launches_min": min((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "n_launches_max": max((int(r.get("n_launches", 0)) for r in catalogue), default=None),
            "cohort_size_min": min((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
            "cohort_size_max": max((int(r.get("cohort_size", 0)) for r in catalogue), default=None),
        },
        "intra_launch": {
            "rows": len(intra),
            "window_sec_values": sorted({int(r.get("window_sec", 0)) for r in intra if r.get("window_sec") is not None}),
            "first_rank_min": min((int(r.get("first_rank", 0)) for r in intra), default=None),
            "first_rank_max": max((int(r.get("first_rank", 0)) for r in intra), default=None),
        },
        "scientific_question": "derive exact persistence criteria and replay causally in event-time order; a cohort signal may only affect strictly subsequent launches after its qualifying evidence exists",
        "authority": {"research_only": True, "automatic_trading": False, "buy_now_promotion": False, "live_threshold_change": False},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, sort_keys=True))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
