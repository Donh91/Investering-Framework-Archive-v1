"""Section 3: append-only ETF vintage ledger (one row per asset / session / observation / source vintage).

Sources (read-only):
  A. research/etf_owner/**/owner_snapshot.json         FLO owner snapshots v1..v4 (history_rows)
  B. 03_DAILY_CAPTURE_LOGS/etf/**/<HHMMSS>_<session>.json   settled double-read captures v2
  C. 03_DAILY_CAPTURE_LOGS/evidence_lifecycle/settled_etf  settled run receipts (verification + re-verification)
  D. 02_DATA_PING accepted payloads + Farside supplements   July human/agent-mediated observations
  E. truth-layer history pack v1 (retrospective vintage, Project export uploaded 2026-07-26T19:28:44Z)
  F. live Farside read by this lab (2026-09-23T15:29:04Z)

No timestamp is invented: every observed_at_utc is a field in the evidence file or the git commit time of
the file that first contained it (documented upper bound). Missing times stay null with a status.
"""
from __future__ import annotations

import glob
import json
import re
import subprocess
from collections import defaultdict
from datetime import datetime

from etf_lab_common import (LIVE, PACK, REPO, WORK, is_session, iso, live_table, num, pack_rows, session_close_utc,
                            sha256_bytes, sha256_json, ts, write_json)

OUT = WORK / "out"
PROJECT_EXPORT_UPLOADED_AT = "2026-07-26T19:28:44Z"  # Projects metadata created_at of "Etf btc.md" / "ETF eth.md"
PACK_COMMIT = "4e2ba082d"
TOL = lambda total: max(0.2, abs(total) * 0.01)  # owner parity semantics
ETH_TICK = ["ETHA", "ETHB", "FETH", "ETHW", "TETH", "ETHV", "QETH", "EZET", "MSSE", "ETHE", "ETH"]
BTC_TICK = ["IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC", "BRRR", "HODL", "BTCW", "MSBT", "GBTC", "BTC"]
TICKERS = {"BTC": BTC_TICK, "ETH": ETH_TICK}


def git_first_commit(paths: list[str]) -> dict[str, tuple[str, str]]:
    """path -> (commit, commit_time_utc) of the commit that ADDED the file."""
    out: dict[str, tuple[str, str]] = {}
    res = subprocess.run(["git", "log", "--diff-filter=A", "--name-only", "--format=@@%H %cI", "--", *sorted(set(paths))],
                         cwd=REPO, capture_output=True, text=True, check=True).stdout
    cur = None
    for line in res.splitlines():
        if line.startswith("@@"):
            h, t = line[2:].split(" ")
            cur = (h, iso(datetime.fromisoformat(t)))
        elif line.strip() and cur:
            out[line.strip()] = cur  # log is newest-first; keep overwriting -> oldest add wins
    return out


def row_values(asset, headers, values):
    return {h: v for h, v in zip(headers, values)}


def make_row(*, asset, session, source, observed_at, observed_at_basis, source_retrieved_at, verification_completed_at,
             source_hash, fund_headers, fund_values, reported_total, workflow_status, session_final_claim, evidence_path,
             git_commit, observation_kind, value_scope="FUND_LEVEL", notes=None, not_source_revision=None):
    known = [v for v in (fund_values or []) if v is not None]
    calc = round(sum(known), 4) if fund_values is not None else None
    unknown = [h for h, v in zip(fund_headers or [], fund_values or []) if v is None]
    parity = None if reported_total is None or calc is None else abs(calc - reported_total) <= TOL(reported_total)
    norm = {"h": fund_headers, "v": fund_values, "t": reported_total}
    return {
        "asset": asset, "session_date": session, "is_nyse_session": is_session(session),
        "observation_source": source, "observation_kind": observation_kind, "value_scope": value_scope,
        "observed_at_utc": observed_at, "observed_at_basis": observed_at_basis,
        "source_retrieved_at_utc": source_retrieved_at, "verification_completed_at_utc": verification_completed_at,
        "source_hash": source_hash,
        "schema_hash": sha256_json(fund_headers) if fund_headers else None,
        "row_hash": sha256_json(norm),
        "fund_header_set": fund_headers, "fund_count": len(fund_headers) if fund_headers else None,
        "fund_values": fund_values,
        "reported_total": reported_total, "calculated_total": calc, "parity": parity,
        "unknown_cell_count": len(unknown) if fund_values is not None else None, "unknown_funds": unknown,
        "session_final_claim": session_final_claim, "workflow_status": workflow_status,
        "source_evidence_path": evidence_path, "git_commit": git_commit[0] if git_commit else None,
        "git_commit_time_utc": git_commit[1] if git_commit else None,
        "not_source_revision": not_source_revision, "notes": notes,
    }


# --------------------------------------------------------------------------- A. FLO owner snapshots
def flo_rows(commits):
    rows, attempts = [], []
    for p in sorted(glob.glob(str(REPO / "research/etf_owner/20*/**/owner_snapshot.json"), recursive=True)):
        rel = p.split(str(REPO) + "/")[1]
        d = json.loads(open(p).read())
        t = d["retrieved_at_utc"]
        attempts.append({"lane": "FLO_OWNER_SNAPSHOT", "at": t, "status": d.get("status"), "errors": d.get("errors"), "path": rel,
                         "sessions_seen": {a: sorted({r["date"] if "date" in r else None for r in rs}) for a, rs in (d.get("history_rows") or {}).items()}})
        hist = d.get("history_rows") or {}
        items = [(a, r) for a, rs in hist.items() for r in rs] if hist else [(r["asset"], r) for r in d.get("rows", [])]
        for asset, r in items:
            date = r.get("date")
            if date is None:  # v1 rows carry date_label only
                from etf_lab_common import owner_module
                date = owner_module().parse_date_label(r["date_label"]).isoformat()
            headers = r.get("fund_headers")
            if headers is None:  # v1 snapshot: order was the frozen canonical schema of that time (BTC 12, ETH 10)
                frozen = BTC_TICK if asset == "BTC" else [h for h in ETH_TICK if h != "MSSE"]
                headers = frozen if len(r["fund_values"]) == len(frozen) else None
            rows.append(make_row(asset=asset, session=date, source=d["contract"], observed_at=t, observed_at_basis="snapshot.retrieved_at_utc",
                                 source_retrieved_at=t, verification_completed_at=None, source_hash=(d.get("source_hashes") or {}).get(asset),
                                 fund_headers=headers, fund_values=r["fund_values"], reported_total=r["reported_total"],
                                 workflow_status=d.get("status"), session_final_claim=r.get("session_final", "NOT_RECORDED_v1"),
                                 evidence_path=rel, git_commit=commits.get(rel), observation_kind="REAL_TIME_CAPTURE",
                                 notes={"header_mode": r.get("header_mode")}))
        if d.get("errors"):
            for e in d["errors"]:
                attempts[-1].setdefault("asset_errors", []).append(e)
    return rows, attempts


# --------------------------------------------------------------------------- B/C. settled captures + receipts
def settled_rows(commits):
    receipts = []
    for p in sorted(glob.glob(str(REPO / "03_DAILY_CAPTURE_LOGS/evidence_lifecycle/settled_etf/**/*.json"), recursive=True)):
        d = json.loads(open(p).read())
        receipts.append({"path": p.split(str(REPO) + "/")[1], "retrieval_start": d["retrieval_start_time"], "retrieval_complete": d["retrieval_complete_time"],
                         "validated": d["provenance_validation_time"], "artifact_hash": d["artifact_hash"], "repo_head_sha": d.get("repo_head_sha")})
    caps = {}
    rows, attempts = [], []
    for p in sorted(glob.glob(str(REPO / "03_DAILY_CAPTURE_LOGS/etf/20*/**/*.json"), recursive=True)):
        rel = p.split(str(REPO) + "/")[1]
        d = json.loads(open(p).read())
        caps[d["row_signature_sha256"]] = (rel, d)
        t = d["retrieved_at_utc"]
        # verification completion: the lifecycle receipt of the same run (retrieval second-start within 5 s)
        vc = next((r["validated"] for r in receipts if abs((ts(r["retrieval_start"]) - ts(t)).total_seconds()) <= 5), None)
        for r in d["rows"]:
            rows.append(make_row(asset=r["asset"], session=r["date"], source=d["contract"], observed_at=t, observed_at_basis="capture.retrieved_at_utc (second read)",
                                 source_retrieved_at=t, verification_completed_at=vc, source_hash=(d.get("source_hashes_second") or {}).get(r["asset"]),
                                 fund_headers=r["fund_headers"], fund_values=r["fund_values"], reported_total=r["reported_total"],
                                 workflow_status="PASS", session_final_claim=r.get("session_final"), evidence_path=rel, git_commit=commits.get(rel),
                                 observation_kind="REAL_TIME_CAPTURE",
                                 notes={"verification": d.get("verification"), "row_signature_sha256": d["row_signature_sha256"],
                                        "verification_completed_basis": "lifecycle receipt provenance_validation_time" if vc else "NO_MATCHING_RECEIPT"}))
    # re-verification: a later successful run whose pointer signature equals an already-stored capture
    for r in receipts:
        rel, d = caps.get(r["artifact_hash"], (None, None))
        attempts.append({"lane": "SETTLED_DOUBLE_READ", "at": r["retrieval_start"], "status": "PASS", "validated": r["validated"], "path": r["path"],
                         "latest_session": d["session_date"] if d else None})
        if d is None or abs((ts(r["retrieval_start"]) - ts(d["retrieved_at_utc"])).total_seconds()) <= 5:
            continue
        for row in d["rows"]:
            rows.append(make_row(asset=row["asset"], session=row["date"], source="SETTLED_REVERIFICATION_RECEIPT", observed_at=r["retrieval_start"],
                                 observed_at_basis="lifecycle receipt retrieval_start_time (pointer signature equals stored capture)",
                                 source_retrieved_at=r["retrieval_start"], verification_completed_at=r["validated"], source_hash=None,
                                 fund_headers=row["fund_headers"], fund_values=row["fund_values"], reported_total=row["reported_total"],
                                 workflow_status="PASS", session_final_claim=True, evidence_path=r["path"], git_commit=commits.get(r["path"]),
                                 observation_kind="REAL_TIME_CAPTURE", notes={"re_verified_capture": rel}))
    return rows, attempts, receipts


# --------------------------------------------------------------------------- D. July supplements / DATA PING
SUPP_DIR = "02_DATA_PING/operational_handoffs/accepted_logs/supplements/"
TIME_KEYS = ("received_at_utc", "verification_time_utc", "created_at_utc")


def _asset_ctx(key):
    k = key.lower()
    if k.startswith("btc") or k == "btc_etf":
        return "BTC"
    if k.startswith("eth") or k == "eth_etf":
        return "ETH"
    if k.startswith("sol"):
        return "SOL"
    return None


def _date(v):
    from etf_lab_common import owner_module
    if not isinstance(v, str):
        return None
    d = owner_module().parse_date_label(v)
    return d.isoformat() if d else None


def walk_supplement(obj, asset=None, date=None, path="$"):
    """Yield (asset, date, funds{ticker:value}, total, json_path) for every dict that carries a session total."""
    if isinstance(obj, dict):
        d = _date(obj.get("Date") or obj.get("date") or obj.get("session_date")) or date
        m = re.fullmatch(r"(?:btc|eth)_(\d{4})_(\d{2})_(\d{2})", path.rsplit(".", 1)[-1])
        if m:
            d = "-".join(m.groups())
        total = obj.get("Total", obj.get("total_usd_m", obj.get("api_row_total_usd_m")))
        funds = {}
        for k, v in obj.items():
            base = k.replace("_usd_m", "").replace("BTC_mini", "BTC")
            if base in BTC_TICK + ETH_TICK and (isinstance(v, (int, float)) or v in ("NOT_REPORTED",)):
                funds[base] = None if v == "NOT_REPORTED" else float(v)
        for k in ("issuers_usd_m",):
            if isinstance(obj.get(k), dict):
                funds.update({kk: float(vv) for kk, vv in obj[k].items() if isinstance(vv, (int, float))})
        if asset in ("BTC", "ETH") and d and isinstance(total, (int, float)) and "current" not in path.lower():
            yield asset, d, funds, float(total), path
        for k, v in obj.items():
            yield from walk_supplement(v, _asset_ctx(k) or asset, d, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_supplement(v, asset, date, f"{path}[{i}]")


def supplement_rows(commits):
    rows = []
    files = sorted(glob.glob(str(REPO / SUPP_DIR / "*.json")))
    files = [f for f in files if re.search(r"farside|etf", f.split("/")[-1], re.I)]
    for f in files:
        rel = f.split(str(REPO) + "/")[1]
        d = json.loads(open(f).read())
        explicit = next((d[k] for k in TIME_KEYS if isinstance(d.get(k), str) and "T" in d[k]), None)
        commit = commits.get(rel)
        observed, basis = (explicit, "file timestamp field") if explicit else ((commit[1], "git commit time of file (date-only or approx timestamp in file)") if commit else (None, "UNKNOWN"))
        transcription_error = "20jul-eth-flow-revision" in rel
        seen = set()
        for asset, date, funds, total, jp in walk_supplement(d):
            if "superseded_provisional" in jp or "prior_logged" in jp:
                continue
            key = (asset, date, total, tuple(sorted(funds.items())))
            if key in seen:
                continue
            seen.add(key)
            headers = [h for h in TICKERS[asset] if h in funds] if funds else None
            values = [funds[h] for h in headers] if headers else None
            rows.append(make_row(asset=asset, session=date, source="DATA_PING_FARSIDE_SUPPLEMENT", observed_at=observed, observed_at_basis=basis,
                                 source_retrieved_at=None, verification_completed_at=None, source_hash=sha256_bytes(open(f, "rb").read()),
                                 fund_headers=headers, fund_values=values, reported_total=total, workflow_status=d.get("status") or d.get("source_status"),
                                 session_final_claim="NOT_CLAIMED", evidence_path=rel + "#" + jp, git_commit=commit, observation_kind="MEDIATED_CAPTURE",
                                 value_scope="FUND_LEVEL_PARTIAL" if headers and len(headers) < len(TICKERS[asset]) - 1 else ("FUND_LEVEL" if headers else "TOTAL_ONLY"),
                                 not_source_revision="TRANSCRIPTION_ERROR_SUPERSEDED_2026-07-22T06:03:35Z" if transcription_error and asset == "ETH" and date == "2026-07-20" else None))
    # 16 Jul provisional (DATA PING V5 accepted payload) and 20 Jul ETH first observation (W30 evidence): explicit single-value evidence
    manual = [
        ("BTC", "2026-07-16", {"IBIT": None}, 45.7, "2026-07-17T03:41:48Z", "02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-17T034148Z__data-ping-v5__accepted-payload.json#$.etf"),
        ("ETH", "2026-07-16", {}, -28.0, "2026-07-17T03:41:48Z", "02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-17T034148Z__data-ping-v5__accepted-payload.json#$.etf"),
        ("BTC", "2026-07-17", {"IBIT": 136.5}, 132.3, "2026-07-19T20:00:33Z", "02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-19T200033Z__data-ping-v6__accepted-payload.json#$.etf"),
        ("ETH", "2026-07-17", {}, 36.7, "2026-07-19T20:00:33Z", "02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-19T200033Z__data-ping-v6__accepted-payload.json#$.etf"),
        ("ETH", "2026-07-20", {}, 38.0, "2026-07-21T15:47:56Z", "03_WEEKLY_OPERATIONS/forecast_experiments/2026-W30/evidence/2026-07-21T154756Z__data-ping-v6-raw-enrichment__shadow.json"),
    ]
    for asset, date, funds, total, t, path in manual:
        headers = list(funds) or None
        rows.append(make_row(asset=asset, session=date, source="DATA_PING_ACCEPTED_PAYLOAD", observed_at=t, observed_at_basis="payload/evidence timestamp in file name and body",
                             source_retrieved_at=None, verification_completed_at=None, source_hash=None, fund_headers=headers,
                             fund_values=[funds[h] for h in headers] if headers else None, reported_total=total, workflow_status="ACCEPTED",
                             session_final_claim="NOT_CLAIMED", evidence_path=path, git_commit=commits.get(path.split("#")[0]),
                             observation_kind="MEDIATED_CAPTURE", value_scope="TOTAL_PLUS_NAMED_FUNDS" if headers else "TOTAL_ONLY",
                             notes={"ibit_not_reported": True} if funds.get("IBIT", 0) is None else None))
    return rows


# --------------------------------------------------------------------------- E/F. retrospective vintages
def pack_vintage_rows(commits):
    rows = []
    for asset in ("BTC", "ETH"):
        for r in pack_rows(asset):
            headers = [k for k in r if k not in ("date", "Total")]
            malformed = r.get("Total") in (None, "")
            vals = [float(r[h]) if r[h] not in ("", None) else None for h in headers]
            rel = f"{PACK.relative_to(REPO)}/data/us_spot_{asset.lower()}_etf_flows_daily_{r['date'][:4]}.csv"
            rows.append(make_row(asset=asset, session=r["date"], source="TRUTH_LAYER_HISTORY_PACK_v1", observed_at=PROJECT_EXPORT_UPLOADED_AT,
                                 observed_at_basis="Project upload created_at of the source exports (earliest documented existence of this vintage)",
                                 source_retrieved_at=None, verification_completed_at=None, source_hash=None,
                                 fund_headers=headers, fund_values=vals, reported_total=None if malformed else float(r["Total"]),
                                 workflow_status="MALFORMED_ROW_TOTAL_MISSING" if malformed else "STRUCTURE_VALIDATED",
                                 session_final_claim="NOT_CLAIMED", evidence_path=rel, git_commit=commits.get(rel), observation_kind="RETROSPECTIVE_VINTAGE",
                                 notes={"dash_zero_filled_by_export": True},
                                 not_source_revision="PACK_V1_MALFORMED_ROW_TOTAL_MISSING_#1212" if malformed else None))
    return rows


def live_vintage_rows():
    rec = json.loads((LIVE / "fetch_receipt.json").read_text())
    rows = []
    for asset in ("BTC", "ETH"):
        t = live_table(asset)
        tick = t["header_rows"][0][1:-1]
        at = rec[asset.lower()]["retrieved_at_utc"]
        for r in t["date_rows"]:
            if r["date"] >= at[:10]:
                continue  # owner rule: rows dated on/after the UTC retrieval date are not session candidates
            vals = [num(c) for c in r["cells"][1:-1]]
            if not any(v is not None for v in vals) and num(r["cells"][-1]) is None:
                continue
            rows.append(make_row(asset=asset, session=r["date"], source="LAB_LIVE_READ_2026_09_23", observed_at=at, observed_at_basis="lab capture retrieved_at_utc",
                                 source_retrieved_at=rec[asset.lower()]["request_started_utc"], verification_completed_at=None,
                                 source_hash=rec[asset.lower()]["sha256"], fund_headers=tick, fund_values=vals, reported_total=num(r["cells"][-1]),
                                 workflow_status="LAB_READ", session_final_claim="NOT_CLAIMED", evidence_path="live/" + asset.lower() + ".html",
                                 git_commit=None, observation_kind="REAL_TIME_CAPTURE" if r["date"] >= "2026-09-17" else "RETROSPECTIVE_VINTAGE",
                                 notes={"table_content_sha256": t["table_content_sha256"]}))
    return rows


def build():
    paths = [p.split(str(REPO) + "/")[1] for p in glob.glob(str(REPO / "research/etf_owner/20*/**/*.json"), recursive=True)]
    paths += [p.split(str(REPO) + "/")[1] for p in glob.glob(str(REPO / "03_DAILY_CAPTURE_LOGS/etf/20*/**/*.json"), recursive=True)]
    paths += [p.split(str(REPO) + "/")[1] for p in glob.glob(str(REPO / "03_DAILY_CAPTURE_LOGS/evidence_lifecycle/settled_etf/**/*.json"), recursive=True)]
    paths += [p.split(str(REPO) + "/")[1] for p in glob.glob(str(REPO / SUPP_DIR / "*.json"))]
    paths += [p.split(str(REPO) + "/")[1] for p in glob.glob(str(PACK / "data/*.csv"))]
    paths += ["02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-17T034148Z__data-ping-v5__accepted-payload.json",
              "02_DATA_PING/operational_handoffs/accepted_logs/payloads/2026-07-19T200033Z__data-ping-v6__accepted-payload.json",
              "03_WEEKLY_OPERATIONS/forecast_experiments/2026-W30/evidence/2026-07-21T154756Z__data-ping-v6-raw-enrichment__shadow.json"]
    commits = git_first_commit(paths)
    a_rows, a_att = flo_rows(commits)
    b_rows, b_att, receipts = settled_rows(commits)
    d_rows = supplement_rows(commits)
    e_rows = pack_vintage_rows(commits)
    f_rows = live_vintage_rows()
    rows = a_rows + b_rows + d_rows + e_rows + f_rows
    # observed_at can never precede the evidence's own git commit? (commit is an UPPER bound; explicit times may precede it)
    for r in rows:
        r["observed_at_status"] = "KNOWN" if r["observed_at_utc"] else "UNKNOWN"
    rows.sort(key=lambda r: (r["asset"], r["session_date"], r["observed_at_utc"] or "9999", r["observation_source"], r["row_hash"]))
    # de-duplicate exact duplicates (same asset/session/time/source/row) — append-only key
    seen, ledger = set(), []
    for r in rows:
        k = (r["asset"], r["session_date"], r["observed_at_utc"], r["observation_source"], r["row_hash"], r["source_evidence_path"])
        if k in seen:
            continue
        seen.add(k)
        r["ledger_key"] = sha256_json(list(k))[:24]
        ledger.append(r)
    attempts = sorted(a_att + b_att, key=lambda x: x["at"])
    return ledger, attempts, receipts


if __name__ == "__main__":
    ledger, attempts, receipts = build()
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "ledger_raw.jsonl").open("w") as h:
        for r in ledger:
            h.write(json.dumps(r, sort_keys=True) + "\n")
    write_json(OUT / "capture_attempts.json", attempts)
    from collections import Counter
    print(len(ledger), Counter(r["observation_source"] for r in ledger))
    print(Counter(r["observed_at_status"] for r in ledger))
