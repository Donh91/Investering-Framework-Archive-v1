#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import mean
from typing import Iterable, NamedTuple

CONTRACT = "ONCHAIN_INCREMENTAL_VALUE_REPLAY_v0_1"
BASELINE_FEATURES = ("ret1", "ret3", "dd6")
CHALLENGER_FEATURES = BASELINE_FEATURES + ("mvrv", "mvrv_d1")

class ReplayError(ValueError):
    pass

class Row(NamedTuple):
    date: str
    price: float
    mvrv: float

def _finite(value: float) -> bool:
    return math.isfinite(value)

def load_rows(path: Path) -> list[Row]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "price", "mvrv"}
        if not required.issubset(set(reader.fieldnames or [])):
            raise ReplayError("input_requires_date_price_mvrv")
        rows: list[Row] = []
        for raw in reader:
            try:
                price = float(raw["price"])
                mvrv = float(raw["mvrv"])
            except (TypeError, ValueError) as exc:
                raise ReplayError("non_numeric_input") from exc
            if price <= 0 or not _finite(price) or mvrv <= 0 or not _finite(mvrv):
                raise ReplayError("invalid_input_value")
            rows.append(Row(raw["date"], price, mvrv))
    if len(rows) < 24:
        raise ReplayError("insufficient_rows")
    if [row.date for row in rows] != sorted(row.date for row in rows):
        raise ReplayError("rows_not_sorted")
    if len({row.date for row in rows}) != len(rows):
        raise ReplayError("duplicate_dates")
    return rows

def _rolling_max(values: list[float], end: int, width: int) -> float:
    start = max(0, end - width + 1)
    return max(values[start : end + 1])

def build_dataset(rows: list[Row], horizon_rows: int) -> list[dict[str, float | str]]:
    if horizon_rows < 1:
        raise ReplayError("horizon_must_be_positive")
    prices = [row.price for row in rows]
    logs = [math.log(value) for value in prices]
    data: list[dict[str, float | str]] = []
    for index in range(3, len(rows) - horizon_rows):
        data.append({
            "date": rows[index].date,
            "ret1": logs[index] - logs[index - 1],
            "ret3": logs[index] - logs[index - 3],
            "dd6": prices[index] / _rolling_max(prices, index, 6) - 1.0,
            "mvrv": rows[index].mvrv,
            "mvrv_d1": rows[index].mvrv - rows[index - 1].mvrv,
            "target": logs[index + horizon_rows] - logs[index],
        })
    return data

def _standardize(train: list[list[float]], test: list[float]) -> tuple[list[list[float]], list[float]]:
    columns = len(test)
    means = [mean(row[col] for row in train) for col in range(columns)]
    scales: list[float] = []
    for col in range(columns):
        variance = mean((row[col] - means[col]) ** 2 for row in train)
        scale = math.sqrt(variance)
        scales.append(scale if scale > 1e-12 else 1.0)
    train_std = [[(row[col] - means[col]) / scales[col] for col in range(columns)] for row in train]
    test_std = [(test[col] - means[col]) / scales[col] for col in range(columns)]
    return train_std, test_std

def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    n = len(vector)
    augmented = [matrix[i][:] + [vector[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda row: abs(augmented[row][col]))
        if abs(augmented[pivot][col]) < 1e-12:
            raise ReplayError("singular_system")
        augmented[col], augmented[pivot] = augmented[pivot], augmented[col]
        divisor = augmented[col][col]
        augmented[col] = [value / divisor for value in augmented[col]]
        for row in range(n):
            if row == col:
                continue
            factor = augmented[row][col]
            if factor == 0:
                continue
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[col])]
    return [augmented[i][-1] for i in range(n)]

def _ridge_fit_predict(train_x: list[list[float]], train_y: list[float], test_x: list[float], alpha: float) -> float:
    if alpha <= 0:
        raise ReplayError("alpha_must_be_positive")
    standardized, test_std = _standardize(train_x, test_x)
    x = [[1.0] + row for row in standardized]
    test = [1.0] + test_std
    p = len(test)
    xtx = [[0.0 for _ in range(p)] for _ in range(p)]
    xty = [0.0 for _ in range(p)]
    for row, target in zip(x, train_y):
        for i in range(p):
            xty[i] += row[i] * target
            for j in range(p):
                xtx[i][j] += row[i] * row[j]
    for i in range(1, p):
        xtx[i][i] += alpha
    coefficients = _solve(xtx, xty)
    return sum(coef * value for coef, value in zip(coefficients, test))

def walk_forward(dataset: list[dict[str, float | str]], features: Iterable[str], min_train: int, alpha: float) -> list[dict[str, float | str]]:
    feature_names = tuple(features)
    if min_train < 8:
        raise ReplayError("min_train_too_small")
    if len(dataset) <= min_train:
        raise ReplayError("insufficient_walk_forward_rows")
    output: list[dict[str, float | str]] = []
    for index in range(min_train, len(dataset)):
        train = dataset[:index]
        train_x = [[float(row[name]) for name in feature_names] for row in train]
        train_y = [float(row["target"]) for row in train]
        test_x = [float(dataset[index][name]) for name in feature_names]
        prediction = _ridge_fit_predict(train_x, train_y, test_x, alpha)
        output.append({"date": dataset[index]["date"], "actual": float(dataset[index]["target"]), "prediction": prediction})
    return output

def score(predictions: list[dict[str, float | str]]) -> dict[str, float | int]:
    if not predictions:
        raise ReplayError("no_predictions")
    errors = [abs(float(row["actual"]) - float(row["prediction"])) for row in predictions]
    direction = [(float(row["actual"]) >= 0) == (float(row["prediction"]) >= 0) for row in predictions]
    return {"n": len(predictions), "mae_log_return": sum(errors) / len(errors), "direction_accuracy": sum(direction) / len(direction)}

def run(rows: list[Row], horizon_rows: int, min_train: int, alpha: float) -> dict[str, object]:
    dataset = build_dataset(rows, horizon_rows)
    baseline = score(walk_forward(dataset, BASELINE_FEATURES, min_train, alpha))
    challenger = score(walk_forward(dataset, CHALLENGER_FEATURES, min_train, alpha))
    baseline_mae = float(baseline["mae_log_return"])
    challenger_mae = float(challenger["mae_log_return"])
    mae_improvement = (baseline_mae - challenger_mae) / baseline_mae if baseline_mae else 0.0
    direction_delta = float(challenger["direction_accuracy"]) - float(baseline["direction_accuracy"])
    verdict = "PROMISING_ONLY" if mae_improvement >= 0.05 and direction_delta >= 0.05 else "NO_ROBUST_INCREMENTAL_VALUE"
    return {
        "contract": CONTRACT,
        "horizon_rows": horizon_rows,
        "min_train": min_train,
        "alpha": alpha,
        "baseline_features": list(BASELINE_FEATURES),
        "challenger_features": list(CHALLENGER_FEATURES),
        "baseline": baseline,
        "challenger": challenger,
        "mae_improvement_fraction": mae_improvement,
        "direction_accuracy_delta": direction_delta,
        "verdict": verdict,
        "evidence_class": "RETROSPECTIVE_RESEARCH_ONLY_NOT_PROSPECTIVE_EVIDENCE",
        "authority": "NONE",
    }

def main() -> int:
    parser = argparse.ArgumentParser(description="Deterministic research-only MVRV incremental-value replay.")
    parser.add_argument("--input", type=Path, required=True, help="Local transient CSV with date,price,mvrv. Do not commit provider raw data.")
    parser.add_argument("--horizon-rows", type=int, default=1)
    parser.add_argument("--min-train", type=int, default=18)
    parser.add_argument("--alpha", type=float, default=10.0)
    args = parser.parse_args()
    result = run(load_rows(args.input), args.horizon_rows, args.min_train, args.alpha)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
