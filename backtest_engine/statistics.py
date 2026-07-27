from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Iterable, Sequence


@dataclass(frozen=True)
class WalkForwardSplit:
    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]
    purged_indices: tuple[int, ...]
    embargo_indices: tuple[int, ...]


def pinball_loss(observed: float, quantile_forecast: float, quantile: float) -> float:
    if not 0.0 < quantile < 1.0:
        raise ValueError("quantile must be strictly between 0 and 1")
    error = observed - quantile_forecast
    return quantile * error if error >= 0.0 else (quantile - 1.0) * error


def interval_score(observed: float, lower: float, upper: float, alpha: float) -> float:
    if lower > upper:
        raise ValueError("lower cannot exceed upper")
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between 0 and 1")
    score = upper - lower
    if observed < lower:
        score += (2.0 / alpha) * (lower - observed)
    elif observed > upper:
        score += (2.0 / alpha) * (observed - upper)
    return score


def empirical_coverage(observed: Sequence[float], lower: Sequence[float], upper: Sequence[float]) -> float:
    if not (len(observed) == len(lower) == len(upper)):
        raise ValueError("observed, lower and upper must have equal length")
    if not observed:
        raise ValueError("at least one observation is required")
    hits = sum(1 for y, lo, hi in zip(observed, lower, upper) if lo <= y <= hi)
    return hits / len(observed)


def mean_interval_width(lower: Sequence[float], upper: Sequence[float]) -> float:
    if len(lower) != len(upper):
        raise ValueError("lower and upper must have equal length")
    if not lower:
        raise ValueError("at least one interval is required")
    widths = []
    for lo, hi in zip(lower, upper):
        if lo > hi:
            raise ValueError("lower cannot exceed upper")
        widths.append(hi - lo)
    return sum(widths) / len(widths)


def participation_ratio(eigenvalues: Iterable[float]) -> float:
    values = [float(value) for value in eigenvalues if float(value) > 0.0]
    if not values:
        raise ValueError("at least one positive eigenvalue is required")
    total = sum(values)
    squared = sum(value * value for value in values)
    return (total * total) / squared


def entropy_effective_rank(eigenvalues: Iterable[float]) -> float:
    values = [float(value) for value in eigenvalues if float(value) > 0.0]
    if not values:
        raise ValueError("at least one positive eigenvalue is required")
    total = sum(values)
    probabilities = [value / total for value in values]
    entropy = -sum(probability * math.log(probability) for probability in probabilities)
    return math.exp(entropy)


def moving_block_bootstrap_indices(
    sample_size: int,
    block_length: int,
    replications: int,
    seed: int,
) -> list[tuple[int, ...]]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if not 1 <= block_length <= sample_size:
        raise ValueError("block_length must be between 1 and sample_size")
    if replications <= 0:
        raise ValueError("replications must be positive")

    rng = random.Random(seed)
    starts = range(0, sample_size - block_length + 1)
    output: list[tuple[int, ...]] = []
    for _ in range(replications):
        indices: list[int] = []
        while len(indices) < sample_size:
            start = rng.choice(starts)
            indices.extend(range(start, start + block_length))
        output.append(tuple(indices[:sample_size]))
    return output


def stationary_bootstrap_indices(
    sample_size: int,
    mean_block_length: float,
    replications: int,
    seed: int,
) -> list[tuple[int, ...]]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if mean_block_length < 1.0:
        raise ValueError("mean_block_length must be at least 1")
    if replications <= 0:
        raise ValueError("replications must be positive")

    restart_probability = 1.0 / mean_block_length
    rng = random.Random(seed)
    output: list[tuple[int, ...]] = []

    for _ in range(replications):
        current = rng.randrange(sample_size)
        indices: list[int] = []
        for _position in range(sample_size):
            indices.append(current)
            if rng.random() < restart_probability:
                current = rng.randrange(sample_size)
            else:
                current = (current + 1) % sample_size
        output.append(tuple(indices))
    return output


def purged_expanding_walk_forward(
    sample_size: int,
    minimum_train_size: int,
    test_size: int,
    purge: int,
    embargo: int,
    step: int | None = None,
) -> list[WalkForwardSplit]:
    if sample_size <= 0:
        raise ValueError("sample_size must be positive")
    if minimum_train_size <= 0 or test_size <= 0:
        raise ValueError("training and test sizes must be positive")
    if purge < 0 or embargo < 0:
        raise ValueError("purge and embargo cannot be negative")
    step_size = test_size if step is None else step
    if step_size <= 0:
        raise ValueError("step must be positive")

    splits: list[WalkForwardSplit] = []
    test_start = minimum_train_size + purge
    while test_start + test_size <= sample_size:
        train_end_exclusive = test_start - purge
        train = tuple(range(0, train_end_exclusive))
        purged = tuple(range(train_end_exclusive, test_start))
        test = tuple(range(test_start, test_start + test_size))
        embargo_end = min(sample_size, test_start + test_size + embargo)
        embargoed = tuple(range(test_start + test_size, embargo_end))
        splits.append(WalkForwardSplit(train, test, purged, embargoed))
        test_start += step_size
    return splits


def benjamini_hochberg(p_values: dict[str, float], alpha: float) -> dict[str, dict[str, float | bool]]:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between 0 and 1")
    if not p_values:
        return {}
    for key, value in p_values.items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"invalid p-value for {key}: {value}")

    ordered = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    count = len(ordered)
    largest_rejected_rank = 0
    for rank, (_key, value) in enumerate(ordered, start=1):
        if value <= (rank / count) * alpha:
            largest_rejected_rank = rank

    raw_adjusted = [(key, value * count / rank) for rank, (key, value) in enumerate(ordered, start=1)]
    adjusted_monotone: list[tuple[str, float]] = []
    running = 1.0
    for key, value in reversed(raw_adjusted):
        running = min(running, value)
        adjusted_monotone.append((key, min(1.0, running)))
    adjusted = dict(reversed(adjusted_monotone))

    return {
        key: {
            "p_value": value,
            "adjusted_p_value": adjusted[key],
            "rejected": rank <= largest_rejected_rank,
        }
        for rank, (key, value) in enumerate(ordered, start=1)
    }


def leave_one_out_means(values: Sequence[float]) -> tuple[float, ...]:
    if len(values) < 2:
        raise ValueError("at least two values are required")
    total = sum(values)
    denominator = len(values) - 1
    return tuple((total - value) / denominator for value in values)
