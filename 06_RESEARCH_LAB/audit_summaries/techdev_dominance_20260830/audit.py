"""Offline exploratory audit. No production imports, trading, or source interpolation.

Run with numpy and pandas. Inputs are separately preserved raw source files.
This does not reconstruct TechDev SAR or claim prospective framework evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_prices(path):
    frame = pd.read_csv(path, usecols=["time", "PriceUSD"])
    frame["time"] = pd.to_datetime(frame["time"])
    if frame.time.duplicated().any() or not frame.time.is_monotonic_increasing:
        raise ValueError("BTC_DUPLICATE_OR_UNSORTED_DATES")
    prices = frame.set_index("time").PriceUSD.astype(float)
    if (prices.dropna() <= 0).any():
        raise ValueError("BTC_NONPOSITIVE_PRICE")
    return prices.reindex(pd.date_range(prices.index.min(), prices.index.max(), freq="D"))


def make_rows(prices, sp):
    if sp.index.duplicated().any() or not sp.index.is_monotonic_increasing:
        raise ValueError("SP_DUPLICATE_OR_UNSORTED_DATES")
    sp = sp.dropna()
    change = sp.pct_change(fill_method=None)
    ma200 = prices.rolling(200, min_periods=200).mean()
    rows = []
    for d, pct in change.items():
        if pd.isna(pct) or pct == 0 or d not in prices.index or pd.isna(prices[d]):
            continue
        entry = d + pd.Timedelta(days=1)  # PriceUSD d is end-of-day d.
        close = pd.Timestamp(d.date()).tz_localize("America/New_York") + pd.Timedelta(hours=16)
        close = close.tz_convert("UTC").tz_localize(None)
        if not close < entry:
            raise ValueError("NONCAUSAL_SP_CLASSIFICATION")
        row = {"session_date": d, "entry_utc": entry, "sp_green": int(pct > 0),
               "btc_above_200d": None if pd.isna(ma200[d]) else int(prices[d] > ma200[d])}
        for h in range(1, 6):
            end = d + pd.Timedelta(days=h)
            path = prices.reindex(pd.date_range(d, end, freq="D"))
            row[f"r{h}"] = float(np.log(path.iloc[-1] / path.iloc[0])) if path.notna().all() else np.nan
        previous = d - pd.Timedelta(days=1)
        row["same_day"] = float(np.log(prices[d] / prices[previous])) if previous in prices.index and pd.notna(prices[previous]) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def mean_diff(y, g):
    return float(y[g == 1].mean() - y[g == 0].mean())


def infer(y, g, settings):
    n = len(y)
    rng = np.random.default_rng(settings["seed"])
    length = min(settings["block_length_sessions"], n)
    deltas = []
    for _ in range(settings["replications"]):
        starts = rng.integers(0, n, size=math.ceil(n / length))
        ix = ((starts[:, None] + np.arange(length)) % n).reshape(-1)[:n]
        if len(np.unique(g[ix])) == 2:
            deltas.append(mean_diff(y[ix], g[ix]))
    low, high = np.quantile(deltas, [0.025, 0.975])
    observed = mean_diff(y, g)
    offsets = rng.integers(21, n - 20, size=1999)
    nulls = np.array([mean_diff(y, np.roll(g, int(offset))) for offset in offsets])
    p = (1 + np.sum(np.abs(nulls) >= abs(observed))) / (1 + len(nulls))
    return float(low), float(high), float(p)


def holm(p_values):
    order = np.argsort(p_values)
    adjusted = np.zeros(len(order))
    running = 0.0
    for rank, ix in enumerate(order):
        running = max(running, (len(order) - rank) * p_values[ix])
        adjusted[ix] = min(1.0, running)
    return adjusted


def summarize(rows, methods):
    groups = {"ALL": rows, "PRE_2018": rows[rows.session_date < "2018-01-01"],
              "2018_TO_2023": rows[(rows.session_date >= "2018-01-01") & (rows.session_date < "2024-01-01")],
              "ETF_ERA_FROM_2024_01_11": rows[rows.session_date >= "2024-01-11"],
              "BTC_ABOVE_200D": rows[rows.btc_above_200d == 1],
              "BTC_NOT_ABOVE_200D": rows[rows.btc_above_200d == 0]}
    result = []
    for group, selected in groups.items():
        for h in range(1, 6):
            sub = selected.dropna(subset=[f"r{h}"])
            y, g = sub[f"r{h}"].to_numpy(), sub.sp_green.to_numpy()
            if len(y) < 43 or len(np.unique(g)) < 2:
                continue
            low, high, p = infer(y, g, methods["appendix"]["block_bootstrap"])
            result.append({"group": group, "horizon_calendar_days": h, "n": len(y),
                "green_n": int(sum(g == 1)), "red_n": int(sum(g == 0)),
                "first_session": str(sub.session_date.min().date()), "last_session": str(sub.session_date.max().date()),
                "mean_green_log_bps": y[g == 1].mean() * 10000,
                "mean_red_log_bps": y[g == 0].mean() * 10000,
                "mean_all_log_bps": y.mean() * 10000,
                "green_minus_red_log_bps": mean_diff(y, g) * 10000,
                "ci95_low_bps": low * 10000, "ci95_high_bps": high * 10000,
                "green_positive_fraction": float((y[g == 1] > 0).mean()),
                "red_positive_fraction": float((y[g == 0] > 0).mean()),
                "green_median_simple_pct": float(np.median(np.expm1(y[g == 1])) * 100),
                "red_median_simple_pct": float(np.median(np.expm1(y[g == 0])) * 100),
                "circular_shift_p_two_sided": p})
    out = pd.DataFrame(result)
    out["holm_p_5_horizons"] = np.nan
    for group in out.group.unique():
        mask = out.group == group
        out.loc[mask, "holm_p_5_horizons"] = holm(out.loc[mask, "circular_shift_p_two_sided"].to_numpy())
    return out


def strategy_diagnostic(prices, rows, costs):
    complete = rows.dropna(subset=["r1"])
    start, end = complete.session_date.min(), complete.session_date.max()
    dates = pd.date_range(start, end, freq="D")
    # Return indexed by the source label of its entry price, not the outcome date.
    daily = np.log(prices.shift(-1) / prices).reindex(dates)
    if daily.isna().any():
        raise ValueError("STRATEGY_PATH_GAP")
    green_dates = set(complete.loc[complete.sp_green == 1, "session_date"])
    all_dates = set(complete.session_date)
    strategies = {"GREEN_NEXT_1D": np.array([int(d in green_dates) for d in dates]),
                  "ALL_SP_SESSIONS_NEXT_1D": np.array([int(d in all_dates) for d in dates]),
                  "BTC_CALENDAR_HOLD": np.ones(len(dates), dtype=int)}
    result = []
    for name, position in strategies.items():
        turnover = np.abs(np.diff(np.r_[0, position]))
        turnover[-1] += position[-1]  # final liquidation
        for cost in costs:
            net = position * daily.to_numpy() + turnover * np.log1p(-cost / 10000)
            wealth = np.exp(np.r_[0.0, np.cumsum(net)])
            result.append({"strategy": name, "one_way_cost_bps": cost,
                "calendar_days": len(dates), "exposure_days": int(sum(position)),
                "one_way_turnovers": int(sum(turnover)), "gross_or_net_multiple": wealth[-1],
                "max_drawdown_pct": float((wealth / np.maximum.accumulate(wealth) - 1).min() * 100),
                "cash_return_assumed": 0, "tax_and_spread_beyond_cost_not_modeled": True})
    return pd.DataFrame(result)


def run(inputs, output, private_rows):
    methods = json.loads((ROOT / "METHODS.json").read_text())
    expected = {"btc_coinmetrics.csv": "06495ff8e643432e6948b7b4686ce44fc106217287dabdc1b38351d9ddec46c3",
                "fred_sp500.csv": "95e95d915919f646ab0da268bf99bc9247446301006dc4c0a229f4f740fb4a99"}
    for name, sha in expected.items():
        if digest(inputs / name) != sha:
            raise ValueError(f"FROZEN_INPUT_HASH_MISMATCH:{name}")
    prices = load_prices(inputs / "btc_coinmetrics.csv")
    sp_frame = pd.read_csv(inputs / "fred_sp500.csv", parse_dates=["observation_date"])
    sp = pd.to_numeric(sp_frame.set_index("observation_date").SP500, errors="coerce")
    rows = make_rows(prices, sp)
    output.mkdir(parents=True, exist_ok=True)
    summary = summarize(rows, methods)
    summary.to_csv(output / "APPENDIX_RESULTS.csv", index=False, float_format="%.10f")
    strategy_diagnostic(prices, rows, methods["appendix"]["cost_per_one_way_turnover_bps"]).to_csv(output / "APPENDIX_STRATEGIES.csv", index=False, float_format="%.10f")
    # Use exactly the same eligible one-day sessions for same-day versus next-day comparison.
    same = rows.dropna(subset=["r1", "same_day"])
    comparison = []
    for col, label in [("same_day", "DESCRIPTIVE_SAME_UTC_DAY_NOT_TRADABLE"), ("r1", "NEXT_UTC_DAY_AFTER_SP_CLOSE")]:
        y, g = same[col].to_numpy(), same.sp_green.to_numpy()
        comparison.append({"timing": label, "n": len(y), "green_mean_log_bps": y[g == 1].mean() * 10000,
                           "red_mean_log_bps": y[g == 0].mean() * 10000,
                           "difference_log_bps": mean_diff(y, g) * 10000})
    pd.DataFrame(comparison).to_csv(output / "APPENDIX_TIMING_COMPARISON.csv", index=False, float_format="%.10f")
    if private_rows:
        rows.to_csv(private_rows, index=False, float_format="%.12f")
    receipt = {"authority": "EXPLORATORY_HISTORICAL_RESEARCH_NOT_FORWARD_EVIDENCE",
               "script_sha256": digest(__file__), "methods_sha256": digest(ROOT / "METHODS.json"),
               "raw_input_hashes": expected, "eligible_1d_sessions": int(rows.r1.notna().sum()),
               "btc_last_valid_price_label": str(prices.dropna().index.max().date()),
               "btc_last_valid_price_instant_utc": str(prices.dropna().index.max() + pd.Timedelta(days=1)),
               "sp_last_valid_session": str(sp.dropna().index.max().date()),
               "full_history_since_2010": False, "original_dollar_chart_reproduced": False,
               "original_techdev_reproduced": False,
               "round3_values_read": False, "output_files": {p.name: digest(p) for p in sorted(output.glob("APPENDIX_*.csv"))}}
    (output / "APPENDIX_RUN_RECEIPT.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(summary[summary.group == "ALL"].to_string(index=False))


def self_test():
    dates = pd.date_range("2024-01-01", periods=220, freq="D")
    prices = pd.Series(np.arange(100.0, 320.0), index=dates)
    sp = pd.Series([100, 101, 99, 99, 100], index=pd.to_datetime(["2024-07-01", "2024-07-02", "2024-07-03", "2024-07-05", "2024-07-08"]))
    original = make_rows(prices, sp)
    r = original.iloc[0]
    assert r.entry_utc == pd.Timestamp("2024-07-03")
    assert r.sp_green == 1
    assert np.isclose(r.r1, np.log(prices["2024-07-03"] / prices["2024-07-02"]))
    assert pd.Timestamp("2024-07-05") not in set(original.session_date)  # flat excluded
    changed = prices.copy()
    changed.loc["2024-07-03":] *= 2
    revised = make_rows(changed, sp).iloc[0]
    assert revised.sp_green == r.sp_green and revised.btc_above_200d == r.btc_above_200d
    assert revised.r1 != r.r1  # future prices change only outcomes
    missing = prices.copy()
    missing["2024-07-04"] = np.nan
    gap = make_rows(missing, sp).iloc[0]
    assert pd.notna(gap.r1) and pd.isna(gap.r2) and pd.isna(gap.r5)
    assert np.allclose(holm(np.array([0.01, 0.04, 0.03])), [0.03, 0.06, 0.06])
    for bad in [pd.concat([sp, sp.iloc[-1:]]), sp.iloc[::-1]]:
        try:
            make_rows(prices, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid dates accepted")
    print("PASS: end-of-day alignment; no future conditioning; flat exclusion; missing-path exclusion; Holm; duplicate and order rejection")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--inputs", type=Path)
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--private-rows", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
    elif args.inputs:
        run(args.inputs, args.output, args.private_rows)
    else:
        parser.error("choose --self-test or --inputs")
