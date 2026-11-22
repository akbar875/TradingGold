"""Minimal closed-bar validator. Session-aware gap classification is AU-006."""

from collections.abc import Sequence
from itertools import pairwise
from math import isfinite

from aurum.contracts import Bar


def validate_closed_bars(bars: Sequence[Bar], *, now_utc: int, seconds: int = 900) -> None:
    if not bars or seconds <= 0:
        raise ValueError("DATA_EMPTY_OR_TIMEFRAME_INVALID")
    previous = -1
    for bar in bars:
        if type(bar.time) is not int or bar.time <= previous or bar.time < 0:
            raise ValueError("DATA_TIMESTAMP_INVALID")
        if bar.time + seconds > now_utc:
            raise ValueError("DATA_BAR_NOT_CLOSED")
        prices = (bar.open, bar.high, bar.low, bar.close)
        if not all(isfinite(x) and x > 0 for x in prices):
            raise ValueError("DATA_PRICE_INVALID")
        if not (bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high):
            raise ValueError("DATA_OHLC_INVALID")
        if not isfinite(bar.spread) or bar.spread < 0 or bar.tick_volume < 0:
            raise ValueError("DATA_VOLUME_OR_SPREAD_INVALID")
        previous = bar.time


def gap_timestamps(bars: Sequence[Bar], *, seconds: int = 900) -> list[int]:
    """Report gaps without inventing market holiday/session classifications."""
    return [b.time for a, b in pairwise(bars) if b.time - a.time != seconds]
