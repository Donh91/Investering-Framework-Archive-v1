"""Section 2: reproduce the live Farside ETH/BTC table shape and mechanically test schema repairs.

Research only. The production owner is imported read-only; variants are applied to an in-memory
copy of CANONICAL_FUND_HEADERS. Nothing here is a repair of the production owner.
"""
from __future__ import annotations

import copy
import json
from datetime import date

from etf_lab_common import LIVE, WORK, live_table, num, owner_module, write_json, sha256_json

OUT = WORK / "out"
TODAY = date(2026, 9, 23)
FROZEN_ETH = ["ETHA", "ETHB", "FETH", "ETHW", "TETH", "ETHV", "QETH", "EZET", "ETHE", "ETH"]
FROZEN_BTC = ["IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC", "BRRR", "HODL", "BTCW", "MSBT", "GBTC", "BTC"]
ISSUERS_OLD = ["Blackrock", "Blackrock", "Fidelity", "Bitwise", "21 Shares", "VanEck", "Invesco", "Franklin", "Grayscale", "Grayscale"]

# Registry used by the STRICT research prototype (the packet proposes the owner keeps such a registry).
SCHEMA_REGISTRY = {
    "ETH": [
        {"schema_id": "FARSIDE_ETH_v1_10F", "tickers": FROZEN_ETH, "effective": "2024-07-23"},
        {"schema_id": "FARSIDE_ETH_v2_11F_MSSE", "tickers": FROZEN_ETH[:8] + ["MSSE"] + FROZEN_ETH[8:],
         "effective": "first live observation 2026-09-18 (retroactive values from 2026-07-27)",
         "revision_kind": "KNOWN_ADDITIVE_SCHEMA_REVISION", "added": ["MSSE"]},
    ],
    "BTC": [{"schema_id": "FARSIDE_BTC_v1_12F", "tickers": FROZEN_BTC, "effective": "2024-01-11"}],
}


# --------------------------------------------------------------------------- HTML fixtures
def _row(cells, tag="td"):
    return "<tr>" + "".join(f"<{tag}><span class=\"tabletext\">{c}</span></{tag}>" for c in cells) + "</tr>\n"


def html_new_layout(tickers, rows, first="", with_fee=True, total_label="Total"):
    """Current (2026-09) Farside ETH layout: one th ticker row (blank first cell, Total last) then a Fee th row."""
    h = '<table class="etf"><thead>' + _row([first, *tickers, total_label], "th")
    if with_fee:
        h += _row(["Fee", *["0.25%"] * len(tickers), ""], "th")
    h += "</thead><tbody>" + _row(["Seed", *["1.0"] * len(tickers), "1"])
    for cells in rows:
        h += _row(cells)
    return h + _row(["Total", *["0"] * (len(tickers) + 1)]) + "</tbody></table>"


def html_old_two_row(tickers, issuers, rows):
    """Pre-2026-09-18 ETH layout reproduced by the architecture fixture (7c17bb367): issuer row ending in Total, ticker row."""
    h = "<table>" + _row(["", *issuers, "Total"], "th") + _row(["", *tickers, ""])
    for cells in rows:
        h += _row(cells)
    return h + "</table>"


def html_direct(tickers, rows):
    """BTC layout: Date ... Total header row."""
    h = "<table>" + _row(["Date", *tickers, "Total"], "th")
    for cells in rows:
        h += _row(cells)
    return h + "</table>"


# --------------------------------------------------------------------------- parser variants
def run_production(html, asset, extra_eth=None):
    mod = owner_module()
    if extra_eth is not None:
        mod.CANONICAL_FUND_HEADERS = copy.deepcopy(mod.CANONICAL_FUND_HEADERS)
        mod.CANONICAL_FUND_HEADERS["ETH"] = extra_eth
    rows, headers, mode = mod.parse_table(html, asset, TODAY)
    decorated = [mod.decorate(r, headers, mode) for r in rows]
    return decorated, headers, mode


def strict_prototype(html, asset):
    """Research prototype of the proposed fail-closed binding (NOT production).

    1. Bind columns only from a source ticker row (never from width).
    2. Ticker row must be unique, end in Total, and exactly equal a registered schema.
    3. A registered schema reached by insertion of registered tickers is KNOWN_ADDITIVE_SCHEMA_REVISION.
    4. Anything else fails closed as UNKNOWN_SCHEMA_REVISION.
    """
    import re
    from etf_lab_common import clean
    mod = owner_module()
    trs = re.findall(r"<tr\b[^>]*>(.*?)</tr>", html, re.I | re.S)
    candidates = []
    for i, tr in enumerate(trs):
        cells = [clean(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if not cells or mod.parse_date_label(cells[0]) is not None:
            continue
        norm = mod.normalized_header(cells)
        if norm and norm[-1] == "total" and norm[0] in ("", "date"):
            tick = [c.upper() for c in cells[1:-1]]
            if all(re.fullmatch(r"[A-Z0-9]{2,6}", t) for t in tick):
                candidates.append(tick)
            elif i + 1 < len(trs):  # issuer-name row: tickers follow on the next row
                nxt = [clean(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", trs[i + 1], re.I | re.S)]
                t2 = [c.upper() for c in nxt[1:-1]]
                if len(t2) == len(tick) and all(re.fullmatch(r"[A-Z0-9]{2,6}", t) for t in t2):
                    candidates.append(t2)
    if len(candidates) != 1:
        raise ValueError("HEADER_NOT_FOUND" if not candidates else "HEADER_AMBIGUOUS")
    tickers = candidates[0]
    if len(set(tickers)) != len(tickers):
        raise ValueError("DUPLICATE_TICKER")
    registry = SCHEMA_REGISTRY[asset]
    match = next((s for s in registry if s["tickers"] == tickers), None)
    if match is None:
        if set(tickers) == set(registry[-1]["tickers"]):
            raise ValueError("UNKNOWN_SCHEMA_REVISION:REORDERED")
        raise ValueError("UNKNOWN_SCHEMA_REVISION")
    headers = ["Date", *tickers, "Total"]
    # same row scanner semantics as the production owner, with the bound headers
    parsed = []
    for tr in trs:
        cells = [clean(c) for c in re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if len(cells) < 3:
            continue
        d = mod.parse_date_label(cells[0])
        if d is None or d >= TODAY:
            continue
        values = [mod.parse_number(c) for c in cells[1:]]
        if not any(v is not None for v in values):
            continue
        parsed.append({"asset": asset, "date": d.isoformat(), "date_label": cells[0], "values": values, "raw_cells": cells})
    mode = "STRICT_SOURCE_TICKER_BINDING:" + match["schema_id"] + (":" + match.get("revision_kind", "BASELINE"))
    return [mod.decorate(r, headers, mode) for r in parsed], headers, mode


VARIANTS = {
    "PRODUCTION_MAIN": lambda html, asset: run_production(html, asset),
    "SCRATCH_ADD_MSSE_TO_FROZEN_SCHEMA": lambda html, asset: run_production(html, asset, FROZEN_ETH[:8] + ["MSSE"] + FROZEN_ETH[8:]),
    "STRICT_REGISTRY_PROTOTYPE": strict_prototype,
}


def evaluate(fixture, variant_fn):
    try:
        rows, headers, mode = variant_fn(fixture["html"], fixture["asset"])
    except ValueError as exc:
        return {"outcome": "FAIL_CLOSED", "error": str(exc)}
    truth = fixture["truth_tickers"]
    if truth is None:  # negative fixture with no valid source schema: any acceptance binds a non-existent schema
        return {"outcome": "ACCEPTED_INVALID_SOURCE_SCHEMA", "header_mode": mode, "rows": len(rows), "fund_headers": headers[1:-1],
                "parity_failures": sum(1 for r in rows if r["total_parity"] is False)}
    mislabels = []
    for r in rows:
        src = {t: r["raw_cells"][1 + i] for i, t in enumerate(truth)} if truth else None
        if src is None:
            continue
        for fund, raw in zip(r["fund_headers"], r["raw_cells"][1:-1]):
            if fund in src and src[fund] != raw:
                mislabels.append({"date": r["date"], "fund": fund, "bound_raw": raw, "source_raw": src[fund]})
                break
            if fund not in src:
                mislabels.append({"date": r["date"], "fund": fund, "bound_raw": raw, "source_raw": "FUND_NOT_IN_SOURCE"})
                break
    parity_fail = sum(1 for r in rows if r["total_parity"] is False)
    return {"outcome": "SILENT_MISLABEL" if mislabels else "ACCEPTED_MAPPING_MATCHES_SOURCE",
            "header_mode": mode, "rows": len(rows), "fund_headers": headers[1:-1],
            "parity_failures": parity_fail, "mislabel_rows": len({m["date"] for m in mislabels}), "mislabel_example": mislabels[:1]}


def main():
    eth, btc = live_table("ETH"), live_table("BTC")
    receipt = json.loads((LIVE / "fetch_receipt.json").read_text())
    eth_tickers = eth["header_rows"][0][1:-1]
    btc_tickers = btc["header_rows"][0][1:-1]
    msse_idx = eth_tickers.index("MSSE")

    # ---------- live reproduction facts
    widths = sorted({len(r["cells"]) for r in eth["date_rows"]})
    msse_nonblank = [r for r in eth["date_rows"] if num(r["cells"][1 + msse_idx]) is not None]
    msse_nonzero = [r for r in msse_nonblank if num(r["cells"][1 + msse_idx]) not in (0.0,)]
    msse_raw_before = sorted({r["cells"][1 + msse_idx] for r in eth["date_rows"] if r["date"] < (msse_nonblank[0]["date"] if msse_nonblank else "9")})
    recon = {"rows": 0, "parity_with_msse": 0, "parity_without_msse_only_when_msse_zero_or_blank": 0, "parity_fail": []}
    for r in eth["date_rows"]:
        vals = [num(c) for c in r["cells"][1:-1]]
        tot = num(r["cells"][-1])
        if tot is None:
            continue
        recon["rows"] += 1
        calc = sum(v for v in vals if v is not None)
        tol = max(0.2, abs(tot) * 0.01)
        if abs(calc - tot) <= tol:
            recon["parity_with_msse"] += 1
        else:
            recon["parity_fail"].append({"date": r["date"], "calc": round(calc, 1), "total": tot})
        m = vals[msse_idx]
        calc_wo = calc - (m or 0.0)
        if abs(calc_wo - tot) <= tol and (m in (None, 0.0) or abs(m) <= tol):
            recon["parity_without_msse_only_when_msse_zero_or_blank"] += 1
    footer = eth["footer_total_rows"][0]["cells"] if eth["footer_total_rows"] else None

    # ---------- fixtures
    def rows_for(table, n=None, until=None):
        rs = [r["cells"] for r in table["date_rows"] if until is None or r["date"] <= until]
        return rs[-n:] if n else rs

    eth_rows = rows_for(eth)
    recent = rows_for(eth, until="2026-09-22")[-25:]
    no_msse = [c[:1 + msse_idx] + c[2 + msse_idx:] for c in recent]
    tick_no_msse = eth_tickers[:msse_idx] + eth_tickers[msse_idx + 1:]
    fixtures = []

    def fx(fid, asset, html, truth, note, kind):
        fixtures.append({"fixture_id": fid, "asset": asset, "html": html, "truth_tickers": truth, "note": note, "kind": kind})

    raw_eth_html = (LIVE / "eth.html").read_text(encoding="utf-8", errors="replace")
    raw_btc_html = (LIVE / "btc.html").read_text(encoding="utf-8", errors="replace")
    fx("LIVE_ETH_CURRENT_PAGE", "ETH", raw_eth_html, eth_tickers, "captured page, all 555 date rows", "LIVE")
    fx("LIVE_BTC_CURRENT_PAGE", "BTC", raw_btc_html, btc_tickers, "captured page, all date rows", "LIVE")
    fx("RECENT_HISTORY_ETH_LAST25_NEW_LAYOUT", "ETH", html_new_layout(eth_tickers, recent), eth_tickers, "last 25 live sessions through 2026-09-22", "HISTORY")
    fx("OLD_SHAPE_ETH_TWO_ROW_10F", "ETH", html_old_two_row(tick_no_msse, ISSUERS_OLD, no_msse), tick_no_msse,
       "pre-change layout (issuer row + ticker row, 10 funds) as frozen in tests/architecture fixture 7c17bb367; values = live minus MSSE column", "OLD_SHAPE")
    fx("ISOLATE_LAYOUT_ONLY_NEW_LAYOUT_10F", "ETH", html_new_layout(tick_no_msse, no_msse), tick_no_msse,
       "new single ticker-row layout WITHOUT MSSE: isolates the layout change", "ISOLATION")
    fx("ISOLATE_MSSE_ONLY_OLD_TWO_ROW_11F", "ETH", html_old_two_row(eth_tickers, ISSUERS_OLD[:8] + ["Morgan Stanley"] + ISSUERS_OLD[8:], recent), eth_tickers,
       "old two-row layout WITH MSSE: isolates the added column", "ISOLATION")
    fx("OLD_SHAPE_BTC_DIRECT", "BTC", html_direct(btc_tickers, rows_for(btc)[-25:]), btc_tickers, "BTC Date..Total layout", "OLD_SHAPE")
    # negatives
    bad_hdr = html_new_layout(eth_tickers, recent, total_label="Tot")
    fx("NEG_MALFORMED_HEADER_NO_TOTAL_LABEL", "ETH", bad_hdr, eth_tickers, "header last cell 'Tot' (no Total label), same width", "NEGATIVE")
    fx("NEG_MALFORMED_HEADER_NO_HEADER_ROW", "ETH", "<table>" + "".join(_row(c) for c in recent) + "</table>", eth_tickers,
       "no header row at all, 12-value rows (tests width-only binding)", "NEGATIVE")
    unk_t = eth_tickers[:msse_idx] + ["XETH"] + eth_tickers[msse_idx:]
    unk_rows = [c[:1 + msse_idx] + ["5.0"] + c[1 + msse_idx:] for c in recent]
    fx("NEG_UNKNOWN_COLUMN_ADDED", "ETH", html_new_layout(unk_t, unk_rows), unk_t, "unregistered ticker XETH inserted (13 funds)", "NEGATIVE")
    ren_t = [("MSSX" if t == "MSSE" else t) for t in eth_tickers]
    fx("NEG_UNKNOWN_COLUMN_SAME_WIDTH", "ETH", html_new_layout(ren_t, recent), ren_t, "MSSE replaced by unregistered MSSX, width unchanged", "NEGATIVE")
    i_e, i_x = eth_tickers.index("ETHE"), eth_tickers.index("ETH")
    re_t = list(eth_tickers); re_t[i_e], re_t[i_x] = re_t[i_x], re_t[i_e]
    re_rows = []
    for c in recent:
        c = list(c); c[1 + i_e], c[1 + i_x] = c[1 + i_x], c[1 + i_e]; re_rows.append(c)
    fx("NEG_REORDERED_COLUMNS_ETH", "ETH", html_new_layout(re_t, re_rows), re_t, "source swaps ETHE/ETH columns (header and values), width unchanged", "NEGATIVE")
    b_e, b_x = btc_tickers.index("GBTC"), btc_tickers.index("BTC")
    rb_t = list(btc_tickers); rb_t[b_e], rb_t[b_x] = rb_t[b_x], rb_t[b_e]
    rb_rows = []
    for c in rows_for(btc)[-25:]:
        c = list(c); c[1 + b_e], c[1 + b_x] = c[1 + b_x], c[1 + b_e]; rb_rows.append(c)
    fx("NEG_REORDERED_COLUMNS_BTC", "BTC", html_direct(rb_t, rb_rows), rb_t, "source swaps GBTC/BTC columns", "NEGATIVE")
    dup_t = list(eth_tickers); dup_t[i_x] = "ETHE"
    fx("NEG_DUPLICATE_TICKER", "ETH", html_new_layout(dup_t, recent), None, "ETHE appears twice (ETH header renamed)", "NEGATIVE")
    nt_t = eth_tickers
    nt_rows = [c[:-1] for c in recent]
    fx("NEG_MISSING_TOTAL_COLUMN", "ETH", html_new_layout(nt_t[:-1], nt_rows, total_label=nt_t[-1]),
       None, "Total column removed from header and every row", "NEGATIVE")
    short = [list(c) for c in recent]; short[-1] = short[-1][:-1]
    fx("NEG_MISSING_TOTAL_CELL_ONE_ROW", "ETH", html_new_layout(eth_tickers, short), eth_tickers, "latest row lacks its Total cell (row short by one)", "NEGATIVE")

    matrix = []
    for f in fixtures:
        row = {"fixture_id": f["fixture_id"], "asset": f["asset"], "kind": f["kind"], "note": f["note"],
               "fixture_sha256": sha256_json(f["html"])}
        for name, fn in VARIANTS.items():
            row[name] = evaluate(f, fn)
        matrix.append(row)

    # expected verdicts: every NEGATIVE fixture must FAIL_CLOSED; LIVE/HISTORY must be ACCEPTED_CORRECT
    def verdict(variant):
        bad = []
        for m in matrix:
            o = m[variant]["outcome"]
            if m["kind"] == "NEGATIVE" and o != "FAIL_CLOSED":
                bad.append({"fixture": m["fixture_id"], "outcome": o, "mode": m[variant].get("header_mode")})
            if m["kind"] in ("LIVE", "HISTORY") and o != "ACCEPTED_MAPPING_MATCHES_SOURCE":
                bad.append({"fixture": m["fixture_id"], "outcome": o, "error": m[variant].get("error")})
        return {"passes_contract": not bad, "violations": bad}

    result = {
        "contract": "ETF_LIVE_SCHEMA_REPRODUCTION_v1",
        "generated_by": "etf_out/work/lab/live_schema_lab.py (research only)",
        "source_capture": receipt,
        "capture_client": "urllib with the owner's User-Agent (same client path as farside_etf_owner.py); curl with the same UA received a Cloudflare 403 challenge page and was not retried or circumvented",
        "raw_html_is_not_a_stable_vintage_id": "raw page sha256 differs on every fetch (6b37840e.. at 15:28:53Z via owner, eceaf80c.. at 15:29:03Z); a vintage id must hash the parsed table, see table_content_sha256",
        "eth": {
            "table_content_sha256": eth["table_content_sha256"],
            "html_structure": "one <table class=\"etf\">; <thead> holds a <th> ticker row whose FIRST cell is blank and LAST cell is 'Total', followed by a <th> Fee row; <tbody> starts with a <td> Seed row, a stray unclosed <tr>, then date rows; footer <td> Total row",
            "ticker_row": eth["header_rows"][0],
            "issuer_name_row_present": False,
            "fund_count": len(eth_tickers),
            "msse_position": {"index_in_funds_0_based": msse_idx, "between": [eth_tickers[msse_idx - 1], eth_tickers[msse_idx + 1]]},
            "meta_rows": [m["cells"] for m in eth["meta_rows"] if m["label"] in ("Fee", "Seed")],
            "footer_total_row": footer,
            "date_rows": len(eth["date_rows"]), "date_row_cell_widths": widths,
            "first_date": eth["date_rows"][0]["date"], "last_date": eth["date_rows"][-1]["date"],
            "msse": {"first_non_blank_date": msse_nonblank[0]["date"] if msse_nonblank else None,
                     "non_blank_rows": len(msse_nonblank), "non_zero_rows": len(msse_nonzero),
                     "raw_cell_values_before_first_value": msse_raw_before,
                     "seed_cell": next((m["cells"][1 + msse_idx] for m in eth["meta_rows"] if m["label"] == "Seed"), None),
                     "values": [{"date": r["date"], "raw": r["cells"][1 + msse_idx]} for r in msse_nonblank]},
            "blank_zero_absent_semantics": {
                "dash": "'-' parses to None (unknown). Used both for funds not yet launched (e.g. MSSE before 2026-07-27, ETHB early rows) and, per July supplements, for funds not yet reported (IBIT 2026-07-16 provisional). The page does not distinguish the two.",
                "zero": "'0.0' is a reported zero flow",
                "absent_column": "a fund column that did not exist in an earlier layout (MSSE before 2026-09-18) has no cell at all in earlier vintages",
            },
            "total_reconciliation_live": recon,
            "second_change_detected": {
                "finding": "LAYOUT_CHANGE_IN_ADDITION_TO_MSSE",
                "before": "issuer-name row [blank, Blackrock, ..., Total] followed by ticker row [blank, ETHA, ..., blank] (matched by SOURCE_TWO_ROW_TICKER_HEADER; every stored v4 ETH snapshot 2026-08-10..2026-09-15 reports that mode)",
                "after": "single ticker row [blank, ETHA, ..., MSSE, ..., Total] followed by a Fee row; no issuer-name row",
                "consequence": "the owner's two-row path can never match the new layout; the only path that can bind it is the exact-width fallback",
                "last_observed_old_layout": "2026-09-17T11:35:26Z (last settled capture, owner PASS)",
                "first_observed_new_layout": "UNKNOWN in repo (first failing settled run 2026-09-18; its snapshot is not committed). Confirmed live 2026-09-23T11:16:50Z (owner snapshot, HEADER_NOT_FOUND) and 15:29:04Z (this capture).",
            },
            "two_row_header_valid": False,
        },
        "btc": {"table_content_sha256": btc["table_content_sha256"], "header_row": btc["header_rows"][0], "fund_count": len(btc_tickers),
                "date_rows": len(btc["date_rows"]), "date_row_cell_widths": sorted({len(r["cells"]) for r in btc["date_rows"]}),
                "first_date": btc["date_rows"][0]["date"], "last_date": btc["date_rows"][-1]["date"],
                "header_mode_in_production": "DIRECT_DATE_TOTAL", "footer_total_row": btc["footer_total_rows"][0]["cells"] if btc["footer_total_rows"] else None},
        "variants": {
            "PRODUCTION_MAIN": "scripts/data_terminal/farside_etf_owner.py at b854dbc31 unchanged",
            "SCRATCH_ADD_MSSE_TO_FROZEN_SCHEMA": "same code, CANONICAL_FUND_HEADERS['ETH'] with MSSE inserted between EZET and ETHE (the smallest likely repair)",
            "STRICT_REGISTRY_PROTOTYPE": "research prototype: bind by source ticker row only, exact match to a registered schema, explicit KNOWN_ADDITIVE_SCHEMA_REVISION for MSSE, no width fallback",
        },
        "fixture_matrix": matrix,
        "contract_verdicts": {v: verdict(v) for v in VARIANTS},
    }
    write_json(OUT / "ETF_LIVE_SCHEMA_REPRODUCTION.json", result)
    for m in matrix:
        print(m["fixture_id"].ljust(42), *[(m[v]["outcome"] + ":" + (m[v].get("header_mode") or m[v].get("error") or ""))[:60].ljust(62) for v in VARIANTS])
    print(json.dumps(result["contract_verdicts"], indent=1)[:3000])
    print(json.dumps({k: result["eth"][k] for k in ("msse_position", "date_rows", "date_row_cell_widths", "first_date", "last_date")}))
    print(json.dumps({k: v for k, v in result["eth"]["msse"].items() if k != "values"}), json.dumps(recon)[:600])


if __name__ == "__main__":
    main()
