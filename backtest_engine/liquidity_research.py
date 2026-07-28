from __future__ import annotations

from dataclasses import dataclass
import math
import random
from typing import Iterable, Sequence


class ResearchContractViolation(ValueError):
    """Raised when a research contract would permit leakage or invalid inference."""


@dataclass(frozen=True)
class LagResult:
    lag: int
    correlation: float
    sample_size: int


@dataclass(frozen=True)
class WalkForwardSplit:
    train_start: int
    train_end_exclusive: int
    test_start: int
    test_end_exclusive: int


def _finite_pairs(x: Sequence[float], y: Sequence[float]) -> list[tuple[float, float]]:
    if len(x) != len(y):
        raise ResearchContractViolation("series lengths differ")
    pairs = []
    for left, right in zip(x, y):
        if math.isfinite(left) and math.isfinite(right):
            pairs.append((float(left), float(right)))
    return pairs


def pearson_correlation(x: Sequence[float], y: Sequence[float]) -> float:
    pairs = _finite_pairs(x, y)
    if len(pairs) < 3:
        raise ResearchContractViolation("at least three finite pairs are required")
    xs = [pair[0] for pair in pairs]
    ys = [pair[1] for pair in pairs]
    x_mean = sum(xs) / len(xs)
    y_mean = sum(ys) / len(ys)
    x_var = sum((value - x_mean) ** 2 for value in xs)
    y_var = sum((value - y_mean) ** 2 for value in ys)
    if x_var <= 0 or y_var <= 0:
        raise ResearchContractViolation("zero-variance series")
    covariance = sum((left - x_mean) * (right - y_mean) for left, right in pairs)
    return covariance / math.sqrt(x_var * y_var)


def first_differences(values: Sequence[float]) -> list[float]:
    return [float(values[index]) - float(values[index - 1]) for index in range(1, len(values))]


def lagged_correlation(predictor: Sequence[float], outcome: Sequence[float], lag: int) -> LagResult:
    if lag < 0:
        raise ResearchContractViolation("negative lag would let the outcome lead the predictor")
    if len(predictor) != len(outcome):
        raise ResearchContractViolation("series lengths differ")
    if lag >= len(predictor) - 2:
        raise ResearchContractViolation("lag leaves too few observations")
    x = [float(value) for value in predictor[: len(predictor) - lag or None]]
    y = [float(value) for value in outcome[lag:]]
    return LagResult(lag=lag, correlation=pearson_correlation(x, y), sample_size=len(x))


def scan_lags(predictor: Sequence[float], outcome: Sequence[float], lags: Iterable[int]) -> list[LagResult]:
    results = [lagged_correlation(predictor, outcome, int(lag)) for lag in lags]
    return sorted(results, key=lambda row: row.lag)


def rolling_beta(predictor: Sequence[float], outcome: Sequence[float], window: int) -> list[float | None]:
    if window < 3:
        raise ResearchContractViolation("window must be at least three")
    if len(predictor) != len(outcome):
        raise ResearchContractViolation("series lengths differ")
    result: list[float | None] = [None] * len(predictor)
    for end in range(window, len(predictor) + 1):
        x = [float(value) for value in predictor[end - window : end]]
        y = [float(value) for value in outcome[end - window : end]]
        x_mean = sum(x) / window
        y_mean = sum(y) / window
        denominator = sum((value - x_mean) ** 2 for value in x)
        if denominator <= 0:
            result[end - 1] = None
            continue
        numerator = sum((left - x_mean) * (right - y_mean) for left, right in zip(x, y))
        result[end - 1] = numerator / denominator
    return result


def holm_adjust(p_values: Sequence[float]) -> list[float]:
    count = len(p_values)
    order = sorted(range(count), key=lambda index: p_values[index])
    adjusted = [0.0] * count
    running = 0.0
    for rank, index in enumerate(order):
        candidate = min(1.0, (count - rank) * float(p_values[index]))
        running = max(running, candidate)
        adjusted[index] = running
    return adjusted


def benjamini_hochberg_adjust(p_values: Sequence[float]) -> list[float]:
    count = len(p_values)
    order = sorted(range(count), key=lambda index: p_values[index], reverse=True)
    adjusted = [0.0] * count
    running = 1.0
    for reverse_rank, index in enumerate(order, start=1):
        rank = count - reverse_rank + 1
        candidate = min(1.0, float(p_values[index]) * count / rank)
        running = min(running, candidate)
        adjusted[index] = running
    return adjusted


def block_permutation_family_max(
    predictor: Sequence[float],
    outcome: Sequence[float],
    lags: Sequence[int],
    *,
    block_size: int,
    permutations: int,
    seed: int,
) -> list[float]:
    if block_size < 1 or permutations < 1:
        raise ResearchContractViolation("positive block size and permutation count required")
    if len(predictor) != len(outcome):
        raise ResearchContractViolation("series lengths differ")
    rng = random.Random(seed)
    blocks = [list(outcome[start : start + block_size]) for start in range(0, len(outcome), block_size)]
    maxima = []
    for _ in range(permutations):
        order = list(range(len(blocks)))
        rng.shuffle(order)
        shuffled = [value for index in order for value in blocks[index]][: len(outcome)]
        family = scan_lags(predictor, shuffled, lags)
        maxima.append(max(abs(row.correlation) for row in family))
    return maxima


def purged_expanding_walk_forward(
    sample_size: int,
    *,
    min_train: int,
    test_size: int,
    purge: int,
    embargo: int,
    final_holdout: int,
) -> list[WalkForwardSplit]:
    values = (sample_size, min_train, test_size, purge, embargo, final_holdout)
    if any(value < 0 for value in values):
        raise ResearchContractViolation("split parameters cannot be negative")
    if min_train < 3 or test_size < 1:
        raise ResearchContractViolation("insufficient train or test size")
    development_end = sample_size - final_holdout
    if development_end <= min_train + purge:
        raise ResearchContractViolation("final holdout leaves no development split")

    splits = []
    train_end = min_train
    while True:
        test_start = train_end + purge
        test_end = test_start + test_size
        if test_end > development_end:
            break
        splits.append(WalkForwardSplit(0, train_end, test_start, test_end))
        train_end = test_end + embargo
    if not splits:
        raise ResearchContractViolation("no valid walk-forward splits")
    return splits


def validate_dag(nodes: Sequence[str], edges: Sequence[tuple[str, str]]) -> list[str]:
    node_set = set(nodes)
    if len(node_set) != len(nodes):
        raise ResearchContractViolation("duplicate DAG node")
    adjacency = {node: [] for node in nodes}
    indegree = {node: 0 for node in nodes}
    for source, target in edges:
        if source not in node_set or target not in node_set:
            raise ResearchContractViolation("edge references unknown node")
        adjacency[source].append(target)
        indegree[target] += 1

    queue = sorted(node for node, degree in indegree.items() if degree == 0)
    order = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for target in sorted(adjacency[node]):
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
                queue.sort()
    if len(order) != len(nodes):
        raise ResearchContractViolation("DAG contains a cycle")
    return order
