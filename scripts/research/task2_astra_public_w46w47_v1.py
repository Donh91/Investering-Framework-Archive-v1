#!/usr/bin/env python3
"""Owner-only, one-use, PUBLIC-source Astra High Task2 research, GitHub Actions.

Distinct from the TWO consumed Nov13 Astra IDs and the disabled realdata V2.
Research-only text/model reasoning; no Code Interpreter/tool generated costs,
trading, new scheduler, forecast rewrite, private data or paid retry.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.api_agent import manual_astra_task2_high_v1 as core

ISSUE = 1596
MODEL = "gpt-6-astra"
MISSION = "ASTRA-HIGH-TASK2-PUBLIC-W46W47-20261116-ONE"
TRIGGER = "OWNER_LAUNCH_ASTRA_TASK2_PUBLIC_W46W47_20261116_ONE_SHOT"
CLAIM_MARKER = "TASK2_ASTRA_PUBLIC_W46W47_PAID_CLAIM_V1 mission=" + MISSION
MAX_COST = 10.0
MAX_REQUEST_BYTES = 500_000
MAX_OUTPUT_TOKENS = 85_000
INPUT_USD_M = 10.0
OUTPUT_USD_M = 50.0
RESP_ID = re.compile(r"resp_[A-Za-z0-9_-]{4,180}\Z")
LEDGER = ROOT / "research/api_agent/coordination/API_PENDING_BILLING_RISK_V1.json"
REPO = "Donh91/Investering-Framework-Archive-v1"
SOURCE = (
  "05_CYCLE_NAVIGATOR/weekly/2026/W46/CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
  "05_CYCLE_NAVIGATOR/weekly/2026/W47/CYCLE_NAVIGATOR_FORECAST_FREEZE.json",
  "06_RESEARCH_LAB/task2_challenger_a/issued/2026/W47/CHALLENGER_A_FROZEN_ISSUANCE.json",
  "04_MARKET_LEARNING/handlekompas/research/2026-11-13__W46_PULLBACK_FAILURE_RPL_V1.md",
  "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-15_W46_EMERGENCY_PREW47_DIAGNOSTIC_v1.md",
  "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/W46_PREWEEK_BINANCE_SPOT_DIAGNOSTIC_20261115_v1.json",
  "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-16_W46_SOURCE_METHOD_CORRECTIONS_v1.md",
  "06_RESEARCH_LAB/hugging_face_task2_audit_20261022/kompas_scientific_edge_program_v2_1/2026-11-14_ASTRA_HIGH_AUDITED_RESULTS_REGISTER_v1.md",
)
INSTRUCTIONS = """TASK2 OWNER-APPROVED ASTRA HIGH PUBLIC DATA STUDY, NOV 16 2026.
Your input is an immutable GitHub checkout excerpt with per-file SHA256 and
an original main commit SHA. This is RESEARCH ONLY, not live policy.

Prior paid Astra one-shots 43419077122 and 43436726016 have run already:
DO NOT reproduce their report, claim a new independent backtest or spend
resources describing their prior conclusions. Treat their audited failures
as adversarial source material. The source W46 spot data is RETROSPECTIVE
and exposed, one dependent week, NOT prospective or PIT-confirmed.
W47 CN and Challenger A are ORIGINAL ISSUANCE only, NOT mature outcomes.
Do not score W47; independently inspect W47 source and release clock gaps.
Do not treat multiple hourly issues as independent drawdowns.

MANDATORY: (A) Reconstruct the W46 failure hypotheses and source-qualified
BTC/ETH daily close vs frozen-point baseline (point and interval skill are
different). Do not claim execution of Python, tools or web queries.
(B) Stress-test early 3/5 -> 4/5 risk escalation concept without inventing
historical trigger timestamps. Distinguish source, issued warning,
first-consumer delivery, actionable price, and counterfactual.
(C) Show a source-legal plan for 1-3d, 5-7d and 2-3w independent tests with
persistence, confidence intervals, baseline and abstention denominators.
(D) Inspect original W47 freeze vs Challenger A; assess legal prospective
testing, 8-week one-look, sample independence, negative controls and
NO promotion from current W47.
(E) Alpha Lab paper wallet v4 decisions/fills/exits and actual costs are
MISSING: G3/G5 actual trade economics NOT EVALUABLE. You MAY give
clearly NON_EMPIRICAL break-even sensitivity; never imply verified PnL.
(F) Propose at most THREE high-EV original owner code/test interventions,
with frozen prerequisites and disconfirming evidence. No live changes.

Output evidence table with file SHA citation; explicitly separate:
VERIFIED_INPUT, REPRODUCIBLE_ARITHMETIC, DEVELOPMENT_ONLY,
HYPOTHESIS, MISSING_SOURCE, NOT_EVALUABLE.
Require independent Claude methodological audit before adoption.
Do not execute code, use tools, issue orders, change budgets, launch agents,
modify weights/models or access private content. Reject unsupported claims.
"""

def fail(reason):
    raise ValueError(reason)

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_head() -> str:
    head = os.getenv("GITHUB_SHA", "")
    if not re.fullmatch(r"[a-f0-9]{40}", head):
        fail("ORIGINAL_MAIN_SOURCE_SHA_UNVERIFIED")
    return head

def owner_event() -> dict:
    if (os.getenv("GITHUB_EVENT_NAME") != "issue_comment"
            or os.getenv("GITHUB_ACTOR") != "Donh91"
            or os.getenv("GITHUB_REPOSITORY") != REPO
            or os.getenv("GITHUB_REF") != "refs/heads/main"):
        fail("NATIVE_OWNER_EVENT_REQUIRED")
    path = Path(core.required_env("GITHUB_EVENT_PATH"))
    event = core.read(path)
    comment = event.get("comment") or {}
    issue = event.get("issue") or {}
    if (event.get("action") != "created" or issue.get("number") != ISSUE
            or issue.get("pull_request") is not None
            or comment.get("user", {}).get("login") != "Donh91"
            or comment.get("author_association") != "OWNER"
            or comment.get("body") != TRIGGER):
        fail("EXACT_ONE_TIME_OWNER_TRIGGER_REQUIRED")
    git_head()
    return event

def check_reservation():
    ledger = core.read(LEDGER)
    rows = ledger.get("owner_reservations")
    if (ledger.get("absolute_budget_usd") not in (50, 100) or not isinstance(rows, list)
            or (ledger.get("absolute_budget_usd") == 100 and ledger.get("owner_astra_program_budget_authorization") != "OWNER_INTERACTIVE_2026-11-16_FIVE_ASTRA_HIGH_V1")):
        fail("CANONICAL_SHARED_BUDGET_UNVERIFIED")
    good = [x for x in rows if isinstance(x, dict)
            and x.get("work_id") == MISSION
            and x.get("status") == "OWNER_RESERVED_PREHTTP"
            and x.get("upper_usd") == 10
            and x.get("one_paid_post_max") == 1
            and x.get("reconciliation_required") is True]
    if len(good) != 1:
        fail("DISTINCT_AST RA_10USD_RESERVATION_REQUIRED".replace(" ", ""))

def source_packet() -> tuple[str, list[dict]]:
    meta, fragments = [], [INSTRUCTIONS]
    total = 0
    for relative in SOURCE:
        p = ROOT / relative
        if not p.is_file() or p.is_symlink():
            fail("SOURCE_NOT_AVAILABLE:" + relative)
        raw = p.read_bytes()
        if (len(raw) > 210_000
                or any(token in raw for token in (b"sk-proj-", b"-----BEGIN PRIVATE KEY-----", b"github_pat_"))):
            fail("PUBLIC_SOURCE_UNSAFE_OR_OVERSIZE:" + relative)
        text = raw.decode("utf-8")
        total += len(raw)
        rec = {"path": relative, "sha256": digest(raw), "bytes": len(raw)}
        meta.append(rec)
        fragments.append("\nSOURCE FILE " + relative + " sha256=" + rec["sha256"] + "\n" + text)
    if total > 750_000:
        fail("TOTAL_SOURCE_BYTES_TOO_LARGE")
    return "\n".join(fragments), meta

def prepare(out: Path, *, preview: bool):
    # Offline preview cannot reserve or send a paid request.
    if not preview:
        owner_event()
        check_reservation()
    body, sources = source_packet()
    sha = git_head()
    prompt = "Source-main " + sha + "\n" + body
    payload = {"model": MODEL, "reasoning": {"effort": "high"},
               "max_output_tokens": MAX_OUTPUT_TOKENS,
               "background": True, "store": True,
               "input": [{"role": "user", "content": [{"type": "input_text", "text": prompt}]}]}
    data = core.canonical(payload)
    theoretical = (len(data) * INPUT_USD_M + MAX_OUTPUT_TOKENS * OUTPUT_USD_M) / 1_000_000
    if len(data) > MAX_REQUEST_BYTES or theoretical > MAX_COST:
        fail("PAID_MAXIMUM_BUDGET_NOT_BOUNDED")
    meta = {"contract": "TASK2_AST RA_PUBLIC_W46W47_PREPARED_v1".replace(" ", ""),
            "mission": MISSION, "source_main_sha": sha,
            "request_sha256": digest(data),
            "request_bytes": len(data), "max_output_tokens": MAX_OUTPUT_TOKENS,
            "worst_case_text_only_usd": round(theoretical, 6),
            "owner_reservation_usd": 10,
            "external_tools": False, "alpha_v4_pnl": "NOT_EVALUABLE",
            "sources": sources, "source_count": len(sources)}
    out.mkdir(parents=True, exist_ok=True)
    core.write_once(out / "request.json", payload)
    core.write_once(out / "source_manifest.json", meta)
    print("ASTRA_PUBLIC_PREPARED_NO_PAID_POST", meta["source_main_sha"],
          meta["request_sha256"], meta["worst_case_text_only_usd"])

def claims(token: str):
    for n in range(1, 15):
        rows = core.http_json("GET",
            "https://api.github.com/repos/" + REPO + "/issues/1596/comments?per_page=100&page=" + str(n),
            github_token=token, timeout=45)
        if not isinstance(rows, list):
            fail("DURABLE_CLAIM_CENSUS_INVALID")
        if any(CLAIM_MARKER in str(v.get("body", "")) for v in rows if isinstance(v, dict)):
            fail("ASTRA_ONE_USE_CLAIM_ALREADY_CONSUMED")
        if len(rows) < 100:
            return
    fail("DURABLE_CLAIM_CENSUS_TRUNCATED")

def reserve(out: Path):
    event = owner_event()
    check_reservation()
    prepared = core.read(out / "source_manifest.json")
    request = core.read(out / "request.json")
    if (prepared["source_main_sha"] != git_head()
            or prepared["request_sha256"] != digest(core.canonical(request))):
        fail("PREPARED_PAYLOAD_MISMATCH")
    if request.get("tools") or request.get("max_output_tokens") != MAX_OUTPUT_TOKENS:
        fail("UNBOUNDED_OR_TOOL_ENABLED_REQUEST")
    token = core.required_env("GITHUB_TOKEN")
    claims(token)
    reply = core.http_json("GET", core.API + "/models/" + MODEL,
                           api_key=core.required_env("OPENAI_API_KEY"), timeout=45)
    if reply.get("id") != MODEL:
        fail("API_PROJECT_LACKS_AST RA_MODEL".replace(" ", ""))
    claim = {"mission": MISSION, "run_id": core.required_env("GITHUB_RUN_ID"),
             "source_main_sha": prepared["source_main_sha"],
             "request_sha256": prepared["request_sha256"],
             "trigger_id": event["comment"].get("id"), "max_post_attempts": 1,
             "owner_reserved_usd": 10, "created_at": datetime.now(timezone.utc).isoformat()}
    text = CLAIM_MARKER + " run=" + claim["run_id"] + " request_sha256=" + claim["request_sha256"] + " no_retry=true research_only=true"
    response = core.http_json("POST", "https://api.github.com/repos/" + REPO + "/issues/1596/comments",
                              github_token=token, body={"body": text}, timeout=45)
    if type(response.get("id")) is not int:
        fail("NATIVE_ONE_USE_CLAIM_NOT_PERSISTED")
    claim["claim_comment_id"] = response["id"]
    core.write_once(out / "claim.json", claim)
    print("ASTRA_PUBLIC_DURABLE_CLAIM_NO_POST", claim["claim_comment_id"])

def mark_attempt(out: Path):
    claim = core.read(out / "claim.json")
    request = core.read(out / "request.json")
    if claim["mission"] != MISSION or claim["request_sha256"] != digest(core.canonical(request)):
        fail("ONE_USE_CLAIM_OR_REQUEST_INVALID")
    core.write_once(out / "attempt.json", {"mission": MISSION,
        "run_id": claim["run_id"], "request_sha256": claim["request_sha256"],
        "attempts": 1, "never_retry_ambiguous": True,
        "marked_at": datetime.now(timezone.utc).isoformat()})

def submit(out: Path):
    claim = core.read(out / "claim.json")
    attempt = core.read(out / "attempt.json")
    request = core.read(out / "request.json")
    if (attempt["mission"] != MISSION or attempt.get("attempts") != 1
            or attempt["request_sha256"] != claim["request_sha256"]
            or digest(core.canonical(request)) != claim["request_sha256"]
            or request.get("tools") or request["model"] != MODEL
            or request["reasoning"]["effort"] != "high"):
        fail("PAID_POST_VALIDATION_FAILED")
    response = core.http_json("POST", core.API + "/responses",
                              api_key=core.required_env("OPENAI_API_KEY"),
                              body=request, timeout=115)
    rid = response.get("id")
    if not isinstance(rid, str) or not RESP_ID.fullmatch(rid):
        fail("PAID_POST_HANDLE_UNKNOWN_NO_RETRY")
    core.write_once(out / "handle.json", {"response_id": rid,
        "mission": MISSION, "source_main_sha": claim["source_main_sha"],
        "request_sha256": claim["request_sha256"]})
    print("ASTRA_PUBLIC_REAL_POST_HANDLE", rid, response.get("status"))

def collect(out: Path):
    handle = core.read(out / "handle.json")
    rid = handle["response_id"]
    if not RESP_ID.fullmatch(rid):
        fail("INVALID_RESPONSE_HANDLE")
    key = core.required_env("OPENAI_API_KEY")
    deadline = time.monotonic() + 3900
    while True:
        response = core.http_json("GET", core.API + "/responses/" + rid,
                                  api_key=key, timeout=75)
        if response.get("id") != rid or response.get("model") not in (MODEL, None):
            fail("PROVIDER_RESPONSE_IDENTITY_MISMATCH")
        status = response.get("status")
        if status not in ("queued", "in_progress"):
            break
        if time.monotonic() + 20 >= deadline:
            core.write_once(out / "pending.json", {"response_id": rid, "no_repost": True,
                "status": "RUNNING_GET_ONLY", "source_main_sha": handle["source_main_sha"]})
            print("ASTRA_PUBLIC_RETRIEVAL_DEFERRED_NO_REPOST", rid)
            return 2
        time.sleep(20)
    txt = core.response_text(response)
    usage = response.get("usage") or {}
    n1, n2 = usage.get("input_tokens") or 0, usage.get("output_tokens") or 0
    if type(n1) is not int or type(n2) is not int or min(n1, n2) < 0:
        fail("PROVIDER_USAGE_UNVERIFIED")
    est = (n1 * INPUT_USD_M + n2 * OUTPUT_USD_M) / 1_000_000
    receipt = {"mission": MISSION, "response_id": rid, "status": status,
        "source_main_sha": handle["source_main_sha"], "request_sha256": handle["request_sha256"],
        "output_sha256": digest(txt.encode()), "bytes": len(txt.encode()),
        "usage": usage, "estimated_text_model_usd": round(est, 6),
        "provider_invoice_not_verified": True, "alpha_pnl": "NOT_EVALUABLE",
        "authority": "ADVISORY_ONLY_INDEPENDENT_CLAUDE_REVIEW_REQUIRED",
        "created_at": datetime.now(timezone.utc).isoformat()}
    core.write_once(out / "receipt.json", receipt)
    if txt:
        (out / "ASTRA_TASK2_PUBLIC_W46W47_RESEARCH.md").write_text(txt, encoding="utf-8")
    if status != "completed" or not txt or est > MAX_COST:
        print("ASTRA_PUBLIC_OUTPUT_NOT_ACCEPTED", status, est)
        return 3
    print("ASTRA_PUBLIC_RESEARCH_COMPLETE", rid, receipt["output_sha256"], est)
    return 0

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=("preview", "prepare", "reserve", "mark_attempt", "submit", "collect"))
    parser.add_argument("--out", type=Path, default=Path("runtime/astra-public-w46w47"))
    a = parser.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    action = {"preview": lambda: prepare(a.out, preview=True),
              "prepare": lambda: prepare(a.out, preview=False),
              "reserve": lambda: reserve(a.out),
              "mark_attempt": lambda: mark_attempt(a.out),
              "submit": lambda: submit(a.out),
              "collect": lambda: collect(a.out)}
    return action[a.stage]()

if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except Exception as ex:
        print("ASTRA_PUBLIC_FAIL_CLOSED", type(ex).__name__, str(ex)[:130], file=sys.stderr)
        sys.exit(1)
