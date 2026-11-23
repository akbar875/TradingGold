"""Causal validation for UTC market history and decision snapshots."""

from bisect import bisect_right
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import pairwise
from math import isfinite

from aurum.contracts import Bar

TIMEFRAME_SECONDS = {"M15": 900, "H1": 3600, "H4": 14400}


def _finite_number(value: object) -> bool:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return isfinite(value)
    except OverflowError:
        return False


@dataclass(frozen=True)
class HistoryPolicy:
    max_bar_move_percent: float = 10.0
    session_closures_utc: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        if (
            not _finite_number(self.max_bar_move_percent)
            or not 0 < self.max_bar_move_percent <= 100
        ):
            raise ValueError("CONFIG_HISTORY_MOVE_INVALID")
        previous_end = -1
        for bounds in self.session_closures_utc:
            if not isinstance(bounds, tuple) or len(bounds) != 2:
                raise ValueError("CONFIG_HISTORY_CLOSURES_INVALID")
            start, end = bounds
            if type(start) is not int or type(end) is not int or not previous_end < start < end:
                raise ValueError("CONFIG_HISTORY_CLOSURES_INVALID")
            previous_end = end


DEFAULT_HISTORY_POLICY = HistoryPolicy()


def _utc_seconds(value: int) -> bool:
    return type(value) is int and value >= 0


def spread_to_price(points: float, point: float) -> float | None:
    """Convert a historical spread. Zero points means unavailable for analysis."""
    if not _finite_number(points) or points < 0 or not float(points).is_integer():
        raise ValueError("DATA_SPREAD_INVALID")
    if not _finite_number(point) or point <= 0:
        raise ValueError("SYMBOL_METADATA_INVALID")
    if points == 0:
        return None
    price = float(points) * float(point)
    if not isfinite(price):
        raise ValueError("DATA_SPREAD_INVALID")
    return price


def validate_closed_bars(
    bars: Sequence[Bar],
    *,
    now_utc: int,
    seconds: int = 900,
    policy: HistoryPolicy = DEFAULT_HISTORY_POLICY,
    point: float = 1.0,
) -> None:
    if not bars or type(seconds) is not int or seconds <= 0:
        raise ValueError("DATA_EMPTY_OR_TIMEFRAME_INVALID")
    if not _utc_seconds(now_utc):
        raise ValueError("DATA_TIMESTAMP_INVALID")
    previous: Bar | None = None
    max_move = policy.max_bar_move_percent / 100
    for bar in bars:
        if not _utc_seconds(bar.time) or (previous is not None and bar.time <= previous.time):
            raise ValueError("DATA_TIMESTAMP_INVALID")
        if previous is not None and bar.time < previous.time + seconds:
            raise ValueError("DATA_BAR_OVERLAP")
        if bar.time + seconds > now_utc:
            raise ValueError("DATA_BAR_NOT_CLOSED")
        prices = (bar.open, bar.high, bar.low, bar.close)
        if not all(_finite_number(price) and price > 0 for price in prices):
            raise ValueError("DATA_PRICE_INVALID")
        if not (bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high):
            raise ValueError("DATA_OHLC_INVALID")
        if type(bar.tick_volume) is not int or bar.tick_volume < 0:
            raise ValueError("DATA_VOLUME_INVALID")
        spread_to_price(bar.spread, point)
        reference = bar.open if previous is None else previous.close
        if (
            abs(bar.high - reference) / reference > max_move
            or abs(bar.low - reference) / reference > max_move
            or (bar.high - bar.low) / bar.open > max_move
        ):
            raise ValueError("DATA_BAR_OUTLIER")
        previous = bar


@dataclass(frozen=True)
class HistoryGap:
    first_missing_open_utc: int
    next_bar_open_utc: int
    kind: str


def history_gaps(
    bars: Sequence[Bar],
    *,
    seconds: int = 900,
    policy: HistoryPolicy = DEFAULT_HISTORY_POLICY,
) -> list[HistoryGap]:
    """Classify already validated bars using explicitly supplied broker closures."""
    gaps = []
    closures = policy.session_closures_utc
    for previous, current in pairwise(bars):
        start = previous.time + seconds
        if start >= current.time:
            continue
        index = bisect_right(closures, start, key=lambda interval: interval[0]) - 1
        scheduled = index >= 0 and current.time <= closures[index][1]
        gaps.append(
            HistoryGap(start, current.time, "SCHEDULED_CLOSURE" if scheduled else "UNKNOWN")
        )
    return gaps


def gap_timestamps(bars: Sequence[Bar], *, seconds: int = 900) -> list[int]:
    """Return the open timestamp after each gap in validated bars."""
    return [gap.next_bar_open_utc for gap in history_gaps(bars, seconds=seconds)]


def closed_snapshot(
    history: Mapping[str, Sequence[Bar]],
    *,
    decision_utc: int,
    minimum_bars: int = 1,
    policy: HistoryPolicy = DEFAULT_HISTORY_POLICY,
) -> dict[str, Bar]:
    """Select decision inputs using only observations closed by the M15 cutoff."""
    if not _utc_seconds(decision_utc) or type(minimum_bars) is not int or minimum_bars <= 0:
        raise ValueError("DATA_SNAPSHOT_REQUEST_INVALID")
    snapshot = {}
    for timeframe, seconds in TIMEFRAME_SECONDS.items():
        available = []
        for bar in history.get(timeframe, ()):
            if not _utc_seconds(bar.time):
                raise ValueError("DATA_TIMESTAMP_INVALID")
            if bar.time + seconds <= decision_utc:
                available.append(bar)
        if available:
            validate_closed_bars(available, now_utc=decision_utc, seconds=seconds, policy=policy)
        if len(available) < minimum_bars:
            raise ValueError("WARMUP")
        latest = available[-1]
        if decision_utc - (latest.time + seconds) >= seconds:
            raise ValueError("DATA_STALE")
        if any(
            gap.kind == "UNKNOWN" for gap in history_gaps(available, seconds=seconds, policy=policy)
        ):
            raise ValueError("DATA_GAP_UNEXPLAINED")
        snapshot[timeframe] = latest
    if snapshot["M15"].spread == 0:
        raise ValueError("DATA_SPREAD_UNAVAILABLE")
    return snapshot
