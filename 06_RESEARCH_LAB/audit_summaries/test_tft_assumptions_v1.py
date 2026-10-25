"""Research-only, dependency-free falsifiers for the source TFT demo.

Not a market backtest, not source PIT admission, not a forecasting model.
Source: zadescoxp/Temporal-Fusion-Transformer-Price-Prediction
commit f1d35896a02ba054c5abf5ac08fc8f627d504f2c
"""
from __future__ import annotations
import math
from statistics import NormalDist
import unittest

_NORMAL = NormalDist()
Z_90 = _NORMAL.inv_cdf(0.90)


def nominal_eighty_percent_coverage(days: int, rho: float) -> float:
    """True coverage if daily N(0,1) returns have equicorrelation rho.

    Source implementation assembles per-step marginal 10/90 quantiles
    with root-sum-square. Its band is +/- z90*sqrt(days).
    For a valid equicorrelation matrix, rho >= -1/(days-1).
    """
    if days < 1 or not (-1.0 / max(1, days-1) <= rho <= 1.0):
        raise ValueError("Invalid horizon/correlation")
    true_variance = days * (1.0 + (days - 1.0) * rho)
    if true_variance <= 0:
        return 1.0
    half_width = Z_90 * math.sqrt(days)
    return 2.0 * _NORMAL.cdf(half_width / math.sqrt(true_variance)) - 1.0


def source_style_mdd(returns: list[float]) -> float:
    equity = []
    wealth = 1.0
    for r in returns:
        wealth *= (1.0 + r)
        equity.append(wealth)
    peak = float('-inf')
    trough = 0.0
    for wealth in equity:
        peak = max(peak, wealth)
        trough = min(trough, wealth / peak - 1.0)
    return trough


def capital_aware_mdd(returns: list[float]) -> float:
    wealth = peak = 1.0
    trough = 0.0
    for r in returns:
        wealth *= (1.0 + r)
        peak = max(peak, wealth)
        trough = min(trough, wealth / peak - 1.0)
    return trough


class TFTResearchNegativeControls(unittest.TestCase):
    def test_independent_normal_days_cover_nominal_eighty_percent(self):
        for h in (1, 3, 7, 14, 21):
            self.assertAlmostEqual(nominal_eighty_percent_coverage(h, 0.0), .80, places=10)

    def test_correlated_returns_break_root_sum_square_coverage(self):
        self.assertLess(nominal_eighty_percent_coverage(7, 0.5), 0.50)
        self.assertLess(nominal_eighty_percent_coverage(7, 1.0), 0.40)
        self.assertLess(nominal_eighty_percent_coverage(21, 1.0), 0.25)

    def test_original_style_mdd_omits_initial_capital_peak(self):
        returns = [-0.20, 0.25]
        self.assertAlmostEqual(source_style_mdd(returns), 0.0)
        self.assertAlmostEqual(capital_aware_mdd(returns), -0.20)

    def test_close_and_intrawindow_extrema_are_distinct_targets(self):
        completed_bars = [(100.0, 100.0), (90.0, 110.0), (100.0, 120.0)]
        horizon_low = min(low for low, _ in completed_bars)
        horizon_high = max(high for _, high in completed_bars)
        final_close = 115.0
        self.assertEqual((horizon_low, horizon_high), (90.0, 120.0))
        self.assertNotEqual(final_close, horizon_low)
        self.assertNotEqual(final_close, horizon_high)

    def test_invalid_correlation_inputs_rejected(self):
        with self.assertRaises(ValueError):
            nominal_eighty_percent_coverage(7, -1.0)


if __name__ == "__main__":
    unittest.main()
