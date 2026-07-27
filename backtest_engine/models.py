from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class Authority(str, Enum):
    DIRECT = "DIRECT"
    DERIVED_SAME_VENUE = "DERIVED_SAME_VENUE"
    DERIVED_CROSS_SOURCE = "DERIVED_CROSS_SOURCE"
    INDEX_PROXY = "INDEX_PROXY"
    PERPETUAL_PROXY = "PERPETUAL_PROXY"
    RECONSTRUCTION = "RECONSTRUCTION"


class MarketType(str, Enum):
    SPOT = "SPOT"
    PERPETUAL_SWAP = "PERPETUAL_SWAP"
    INDEX = "INDEX"
    ETF_FLOW = "ETF_FLOW"
    MACRO = "MACRO"
    FIXTURE = "FIXTURE"


@dataclass(frozen=True)
class DatasetIdentity:
    dataset_id: str
    venue: str
    market_type: MarketType
    authority: Authority
    timezone_basis: str


@dataclass(frozen=True)
class TemporalPoint:
    knowledge_at_utc: str
    decision_at_utc: str
    execution_at_utc: str
    label_end_utc: str
