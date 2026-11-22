"""Module boundaries for later phases; no fabricated predictions or fills."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class Action(StrEnum):
    BUY = "BUY"
    SELL = "SELL"
    WAIT = "WAIT"


@dataclass(frozen=True)
class Bar:
    """UTC epoch seconds; spread is in broker points, not price units."""

    time: int
    open: float
    high: float
    low: float
    close: float
    tick_volume: int
    spread: float


@dataclass(frozen=True)
class Decision:
    action: Action = Action.WAIT
    reason_code: str = "ENGINE_NOT_IMPLEMENTED"


class FeatureBuilder(Protocol):
    def build(self, closed_bars: Sequence[Bar]) -> Sequence[Mapping[str, float]]: ...


class Predictor(Protocol):
    def predict(self, features: Mapping[str, float], *, now_utc: int) -> Decision: ...
