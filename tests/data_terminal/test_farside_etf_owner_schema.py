from __future__ import annotations

import unittest
from datetime import date

from scripts.data_terminal import farside_etf_owner as owner


ETH10 = ["ETHA", "ETHB", "FETH", "ETHW", "TETH", "ETHV", "QETH", "EZET", "ETHE", "ETH"]
ETH11 = ETH10[:8] + ["MSSE"] + ETH10[8:]
BTC12 = ["IBIT", "FBTC", "BITB", "ARKB", "BTCO", "EZBC", "BRRR", "HODL", "BTCW", "MSBT", "GBTC", "BTC"]
TODAY = date(2026, 9, 23)


def row(cells, tag="td"):
    return "<tr>" + "".join(f"<{tag}>{cell}</{tag}>" for cell in cells) + "</tr>"


def values_for(tickers):
    vals = ["0.0"] * len(tickers)
    vals[0] = "10.0"
    vals[-1] = "2.0"
    return vals


def new_layout(tickers, *, total_label="Total", data=None):
    data = data or values_for(tickers)
    total = sum(float(v) for v in data if v not in {"-", ""})
    return (
        "<table><thead>"
        + row(["", *tickers, total_label], "th")
        + row(["Fee", *["0.25%"] * len(tickers), ""], "th")
        + "</thead><tbody>"
        + row(["18 Sep 2026", *data, str(total)])
        + "</tbody></table>"
    )


def old_two_row(tickers, data=None):
    data = data or values_for(tickers)
    total = sum(float(v) for v in data if v not in {"-", ""})
    issuers = ["Issuer"] * len(tickers)
    return (
        "<table>"
        + row(["", *issuers, "Total"], "th")
        + row(["", *tickers, ""])
        + row(["18 Sep 2026", *data, str(total)])
        + "</table>"
    )


def direct_layout(tickers):
    data = values_for(tickers)
    total = sum(float(v) for v in data)
    return "<table>" + row(["Date", *tickers, "Total"], "th") + row(["18 Sep 2026", *data, str(total)]) + "</table>"


class FarsideOwnerSchemaBindingTests(unittest.TestCase):
    def test_accepts_current_eth_msse_schema_by_name(self):
        rows, headers, mode = owner.parse_table(new_layout(ETH11), "ETH", TODAY)
        self.assertEqual(headers[1:-1], ETH11)
        self.assertEqual(mode, "SOURCE_TICKER_HEADER:FARSIDE_ETH_v2_11F_MSSE")
        decorated = owner.decorate(rows[0], headers, mode)
        self.assertEqual(decorated["fund_headers"], ETH11)
        self.assertTrue(decorated["total_parity"])

    def test_preserves_legacy_eth_two_row_schema(self):
        rows, headers, mode = owner.parse_table(old_two_row(ETH10), "ETH", TODAY)
        self.assertEqual(headers[1:-1], ETH10)
        self.assertEqual(mode, "SOURCE_TWO_ROW_TICKER_HEADER")
        self.assertTrue(owner.decorate(rows[0], headers, mode)["total_parity"])

    def test_preserves_btc_direct_schema(self):
        rows, headers, mode = owner.parse_table(direct_layout(BTC12), "BTC", TODAY)
        self.assertEqual(headers[1:-1], BTC12)
        self.assertEqual(mode, "DIRECT_DATE_TOTAL")
        self.assertTrue(owner.decorate(rows[0], headers, mode)["total_parity"])

    def test_rejects_same_width_unknown_ticker(self):
        bad = [("MSSX" if ticker == "MSSE" else ticker) for ticker in ETH11]
        with self.assertRaisesRegex(ValueError, "UNKNOWN_SCHEMA_REVISION"):
            owner.parse_table(new_layout(bad), "ETH", TODAY)

    def test_rejects_reordered_known_tickers_even_when_total_still_matches(self):
        bad = list(ETH11)
        i, j = bad.index("ETHE"), bad.index("ETH")
        bad[i], bad[j] = bad[j], bad[i]
        with self.assertRaisesRegex(ValueError, "REORDERED"):
            owner.parse_table(new_layout(bad), "ETH", TODAY)

    def test_rejects_duplicate_ticker(self):
        bad = [("ETHE" if ticker == "ETH" else ticker) for ticker in ETH11]
        with self.assertRaisesRegex(ValueError, "DUPLICATE_TICKER"):
            owner.parse_table(new_layout(bad), "ETH", TODAY)

    def test_rejects_headerless_exact_width_rows(self):
        data = values_for(ETH11)
        total = sum(float(v) for v in data)
        html = "<table>" + row(["18 Sep 2026", *data, str(total)]) + "</table>"
        with self.assertRaisesRegex(ValueError, "HEADER_NOT_FOUND"):
            owner.parse_table(html, "ETH", TODAY)

    def test_rejects_missing_total_label(self):
        with self.assertRaisesRegex(ValueError, "HEADER_NOT_FOUND"):
            owner.parse_table(new_layout(ETH11, total_label="Tot"), "ETH", TODAY)

    def test_short_data_row_fails_during_decoration(self):
        html = new_layout(ETH11)
        rows, headers, mode = owner.parse_table(html, "ETH", TODAY)
        broken = dict(rows[0])
        broken["values"] = broken["values"][:-1]
        broken["raw_cells"] = broken["raw_cells"][:-1]
        with self.assertRaisesRegex(ValueError, "COLUMN_COUNT_DRIFT"):
            owner.decorate(broken, headers, mode)


if __name__ == "__main__":
    unittest.main()
