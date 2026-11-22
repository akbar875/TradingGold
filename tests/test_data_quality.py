from dataclasses import replace

import pytest

from aurum.contracts import Bar
from aurum.data_quality import gap_timestamps, validate_closed_bars

BAR = Bar(time=900, open=100, high=105, low=95, close=101, tick_volume=10, spread=12)


def test_closed_bar_boundary():
    validate_closed_bars([BAR], now_utc=1800)
    with pytest.raises(ValueError, match="NOT_CLOSED"):
        validate_closed_bars([BAR], now_utc=1799)


@pytest.mark.parametrize(
    "bars",
    [
        [],
        [BAR, BAR],
        [BAR, replace(BAR, time=0)],
        [replace(BAR, close=float("nan"))],
        [replace(BAR, low=102)],
        [replace(BAR, spread=-1)],
        [replace(BAR, high=float("inf"))],
        [replace(BAR, tick_volume=-1)],
    ],
)
def test_invalid_data_rejected(bars):
    with pytest.raises(ValueError):
        validate_closed_bars(bars, now_utc=10000)


def test_gap_report_does_not_invent_holiday():
    assert gap_timestamps([BAR, replace(BAR, time=2700)]) == [2700]
