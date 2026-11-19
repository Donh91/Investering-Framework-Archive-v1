"""No-network validation of owner-reviewed grouped provider settlement evidence.

Private CSVs are verified outside this module by the owner/independent reviewer.
Only aggregate daily spend, SHA-256, a Bridge pin and native receipt references
are admitted here. No provider identity, payment or release authority.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_CEILING
import math
import re

KEY = "owner_astra_provider_period_settlements"
SETTLED = "CONSUMED_SETTLED_OWNER_PROVIDER_EVIDENCE"
SCOPE = "aggregate for period; no per-request/per-model allocation; not a final invoice"
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
CONTRACT = re.compile(r"OWNER_ASTRA_PROVIDER_PERIOD_SETTLEMENT_(\d{8})_V1\Z")
ID = re.compile(r"ASTRA-[A-Z0-9]{1,24}(?:-[A-Z0-9]{1,24}){1,10}\Z")
RESPONSE = re.compile(r"resp_[A-Za-z0-9_-]{4,180}\Z")
GROUP_FIELDS = {"contract", "source", "usage_csv_sha256", "bridge_commit", "evidence_path",
                "observed_period_start", "observed_period_end", "coverage_cutoff_utc", "export_before_utc",
                "provider_period_spend_usd", "daily_provider_spend_usd", "amount_scope", "no_replay",
                "native_receipts", "additional_native_runs"}
RECEIPT_FIELDS = {"work_id", "run_id", "result_comment_id", "response_id", "receipt_sha256",
                  "started_at", "completed_at", "conclusion", "estimated_upper_usd"}
OTHER_FIELDS = {"route", "run_id", "result_comment_id", "receipt_sha256", "started_at", "completed_at",
                "conclusion"}


def require(ok, code="GROUP_INVALID"):
    if not ok:
        raise ValueError("ASTRA_PROVIDER_SETTLEMENT_" + code)


def money(v):
    require(type(v) in (int, float) and 0 <= v <= 1_000_000_000 and math.isfinite(v), "AMOUNT_INVALID")
    return Decimal(str(v))


def day(v):
    require(isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", v) is not None, "DAY_INVALID")
    try:
        parsed = date.fromisoformat(v)
        require(2020 <= parsed.year <= 2099, "DAY_INVALID")
        return parsed
    except ValueError as exc:
        raise ValueError("ASTRA_PROVIDER_SETTLEMENT_DAY_INVALID") from exc


def utc(v):
    require(isinstance(v, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", v) is not None,
            "TIME_INVALID")
    try:
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("ASTRA_PROVIDER_SETTLEMENT_TIME_INVALID") from exc


def hex_match(regex, v):
    return isinstance(v, str) and regex.fullmatch(v) is not None and v != "0" * len(v)


def groups(ledger, rows):
    """Return (settled ids, per-UTC-month provision) after cross-binding every receipt.

    Provider daily upper bound is max per day across covering exports, not sum
    of repeated cumulative daily amounts. Unique native estimates are summed
    separately; use the greater of both totals for each month. Legacy settlement
    provision and ordinary cost receipts remain additive in the outer guard,
    intentionally conservative where old aggregate overlap cannot be allocated.
    """
    data = ledger.get(KEY, [])
    require(isinstance(data, list) and len(data) <= 10000)
    require(isinstance(rows, list))
    by_id = {}
    for row in rows:
        require(isinstance(row, dict) and isinstance(row.get("work_id"), str), "ROW_INVALID")
        work = row["work_id"]
        require(work not in by_id, "DUPLICATE_WORK")
        by_id[work] = row
    contracts, hashes, runs, result_ids, receipt_hashes, responses = set(), set(), set(), set(), set(), set()
    claimed, daily, estimates = set(), {}, {}
    for group in data:
        require(isinstance(group, dict) and set(group) == GROUP_FIELDS)
        contract = group["contract"]
        match = CONTRACT.fullmatch(contract) if isinstance(contract, str) else None
        require(match is not None and contract not in contracts, "DUPLICATE_OR_INVALID_CONTRACT")
        contracts.add(contract)
        start, end = day(group["observed_period_start"]), day(group["observed_period_end"])
        require(start <= end and (end - start).days < 366, "PERIOD_INVALID")
        stamp = match.group(1)
        export_date = day(stamp[:4] + "-" + stamp[4:6] + "-" + stamp[6:])
        require(end <= export_date, "CONTRACT_DATE_MISMATCH")
        cutoff, export_before = utc(group["coverage_cutoff_utc"]), utc(group["export_before_utc"])
        require(cutoff.date() == end and cutoff < export_before
                and export_before == datetime.combine(export_date + timedelta(days=1), datetime.min.time(), timezone.utc),
                "EXPORT_WINDOW_INVALID")
        require(group["source"] == "owner provider cost CSV export " + export_date.isoformat()
                and group["amount_scope"] == SCOPE and group["no_replay"] is True, "AUTHORITY_INVALID")
        digest = group["usage_csv_sha256"]
        require(hex_match(HEX64, digest) and digest not in hashes and hex_match(HEX40, group["bridge_commit"]),
                "EVIDENCE_INVALID")
        hashes.add(digest)
        path = group["evidence_path"]
        require(isinstance(path, str) and re.fullmatch(r"reports/claude/automated/\d{4}/\d{2}/[A-Za-z0-9_-]+/evidence/[A-Za-z0-9_.-]+\.csv", path) is not None,
                "EVIDENCE_PATH_INVALID")
        amounts = group["daily_provider_spend_usd"]
        expected = {(start + timedelta(days=i)).isoformat() for i in range((end - start).days + 1)}
        require(isinstance(amounts, dict) and set(amounts) == expected, "DAILY_COVERAGE_INVALID")
        parsed = {k: money(v) for k, v in amounts.items()}
        provider = money(group["provider_period_spend_usd"])
        require(provider == sum(parsed.values(), Decimal(0)).quantize(Decimal("0.000001"), rounding=ROUND_CEILING),
                "AGGREGATE_MISMATCH")
        for k, v in parsed.items():
            daily[k] = max(daily.get(k, Decimal(0)), v)
        native, other = group["native_receipts"], group["additional_native_runs"]
        require(isinstance(native, list) and native and isinstance(other, list), "NATIVE_EVIDENCE_REQUIRED")
        for proof, is_astra in [(p, True) for p in native] + [(p, False) for p in other]:
            require(isinstance(proof, dict) and set(proof) == (RECEIPT_FIELDS if is_astra else OTHER_FIELDS),
                    "RECEIPT_INVALID")
            run, comment, receipt = proof["run_id"], proof["result_comment_id"], proof["receipt_sha256"]
            require(type(run) is int and run > 0 and run not in runs and type(comment) is int and comment > 0
                    and comment not in result_ids and hex_match(HEX64, receipt) and receipt not in receipt_hashes,
                    "DUPLICATE_OR_INVALID_RECEIPT")
            runs.add(run); result_ids.add(comment); receipt_hashes.add(receipt)
            launched, finished = utc(proof["started_at"]), utc(proof["completed_at"])
            require(start <= launched.date() <= finished.date() <= end and launched <= finished <= cutoff
                    and proof["conclusion"] == "success", "RUN_NOT_COVERED")
            if not is_astra:
                require(proof["route"] == "RESEARCH_LAB_SOL", "ROUTE_INVALID")
                # Already represented by the ordinary receipt root; no Astra reservation to release.
                continue
            work = proof["work_id"]
            require(isinstance(work, str) and ID.fullmatch(work) is not None and work not in claimed
                    and work in by_id, "WORK_NOT_BOUND")
            row = by_id[work]
            response = proof["response_id"]
            estimate = money(proof["estimated_upper_usd"])
            require(isinstance(response, str) and RESPONSE.fullmatch(response) is not None and response not in responses,
                    "RESPONSE_INVALID")
            responses.add(response)
            require(row.get("status") == SETTLED and row.get("settlement_group") == contract
                    and row.get("no_retry") is True and row.get("reconciliation_required") is False
                    and row.get("consumed_run_id") == run and row.get("consumed_response_id") == response
                    and row.get("consumed_receipt_sha256") == receipt
                    and estimate > 0 and estimate <= money(row.get("upper_usd"))
                    and money(row.get("consumed_estimated_upper_usd")) == estimate,
                    "ROW_PROOF_MISMATCH")
            claimed.add(work)
            month = launched.date().replace(day=1)
            while month <= finished.date():
                key = month.strftime("%Y-%m")
                estimates[key] = estimates.get(key, Decimal(0)) + estimate
                month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    require(claimed == {w for w, row in by_id.items() if row.get("status") == SETTLED}, "UNBOUND_SETTLED_ROW")
    for work, row in by_id.items():
        if work not in claimed:
            require(row.get("consumed_run_id") not in runs and row.get("consumed_response_id") not in responses,
                    "SETTLED_EVIDENCE_REUSED")
    # Round the provider union up at the same six-decimal precision as the admitted export.
    provider_by_month = {}
    for k, v in daily.items():
        provider_by_month[k[:7]] = provider_by_month.get(k[:7], Decimal(0)) + v
    months = set(provider_by_month) | set(estimates)
    upper = {m: max(provider_by_month.get(m, Decimal(0)).quantize(Decimal("0.000001"), rounding=ROUND_CEILING),
                    estimates.get(m, Decimal(0))) for m in months}
    return claimed, upper


def validate_append_only(before, after):
    """Review-time check: earlier approved settlements/history may not be edited.

    This is a base-vs-candidate check for the owner/reviewer, not a claim that
    runtime can authenticate a private evidence file from its public digest.
    """
    old_groups = before.get(KEY, [])
    new_groups = after.get(KEY, [])
    require(isinstance(old_groups, list) and isinstance(new_groups, list)
            and new_groups[:len(old_groups)] == old_groups, "HISTORY_REWRITE")
    old_rows = before.get("astra_mission_reservations", [])
    new_rows = after.get("astra_mission_reservations", [])
    groups(before, old_rows)
    groups(after, new_rows)
    index = {r["work_id"]: r for r in new_rows}
    for row in old_rows:
        if row.get("status") == SETTLED:
            require(index.get(row["work_id"]) == row, "HISTORY_REWRITE")
        elif row["work_id"] in index and index[row["work_id"]].get("status") == SETTLED:
            final = index[row["work_id"]]
            for field in ("created_month_utc", "lower_usd", "upper_usd", "source", "one_paid_post_max", "authorization"):
                require(final.get(field) == row.get(field), "HISTORICAL_CEILING_OR_AUTHORITY_CHANGED")
            require(isinstance(final.get("basis"), str) and final["basis"].startswith(row.get("basis", "")), "HISTORY_REWRITE")
            for field in ("consumed_run_id", "consumed_response_id", "consumed_estimated_upper_usd"):
                if field in row:
                    require(final.get(field) == row[field], "HISTORY_REWRITE")
