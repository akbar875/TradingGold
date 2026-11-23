from dataclasses import replace

import pytest

from aurum.contracts import Bar
from aurum.data_quality import (
    HistoryPolicy,
    closed_snapshot,
    gap_timestamps,
    history_gaps,
    spread_to_price,
    validate_closed_bars,
)

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


@pytest.mark.parametrize(
    ("changed", "reason"),
    [
        ({"tick_volume": float("nan")}, "DATA_VOLUME_INVALID"),
        ({"tick_volume": 1.5}, "DATA_VOLUME_INVALID"),
        ({"tick_volume": True}, "DATA_VOLUME_INVALID"),
        ({"tick_volume": "x"}, "DATA_VOLUME_INVALID"),
        ({"spread": 0.5}, "DATA_SPREAD_INVALID"),
        ({"open": True}, "DATA_PRICE_INVALID"),
        ({"open": 10**400}, "DATA_PRICE_INVALID"),
        ({"high": 150, "close": 145}, "DATA_BAR_OUTLIER"),
    ],
)
def test_malformed_and_outlier_bars_have_specific_reason_codes(changed, reason):
    with pytest.raises(ValueError, match=f"^{reason}$"):
        validate_closed_bars([replace(BAR, **changed)], now_utc=1800)


def test_overlap_is_rejected_even_with_increasing_open_times():
    with pytest.raises(ValueError, match="DATA_BAR_OVERLAP"):
        validate_closed_bars([BAR, replace(BAR, time=960)], now_utc=2700)


def test_gap_requires_complete_explicit_broker_closure():
    bars = [BAR, replace(BAR, time=3600)]
    covered = HistoryPolicy(session_closures_utc=((1800, 3600),))
    partial = HistoryPolicy(session_closures_utc=((1800, 3500),))
    assert history_gaps(bars, policy=covered)[0].kind == "SCHEDULED_CLOSURE"
    assert history_gaps(bars, policy=partial)[0].kind == "UNKNOWN"


def test_spread_price_uses_broker_point_and_preserves_unknown():
    assert spread_to_price(23, 0.01) == pytest.approx(0.23)
    assert spread_to_price(23, 0.001) == pytest.approx(0.023)
    assert spread_to_price(0, 0.01) is None
    with pytest.raises(ValueError, match="SYMBOL_METADATA_INVALID"):
        spread_to_price(23, 0)
    with pytest.raises(ValueError, match="DATA_SPREAD_INVALID"):
        spread_to_price(23, 1e308)


def test_snapshot_uses_historical_m15_cutoff_and_ignores_future_values():
    decision = 14400
    closed = {"M15": 13500, "H1": 10800, "H4": 0}
    history = {
        tf: [replace(BAR, time=open_utc), replace(BAR, time=decision)]
        for tf, open_utc in closed.items()
    }
    selected = closed_snapshot(history, decision_utc=decision)
    assert {tf: bar.time for tf, bar in selected.items()} == closed
    mutated = {tf: [bars[0], replace(bars[1], close=float("nan"))] for tf, bars in history.items()}
    assert closed_snapshot(mutated, decision_utc=decision) == selected


def test_snapshot_excludes_htf_bars_already_open_but_not_closed():
    history = {
        "M15": [replace(BAR, time=14400)],
        "H1": [replace(BAR, time=10800), replace(BAR, time=14400, close=float("nan"))],
        "H4": [replace(BAR, time=0), replace(BAR, time=14400, close=float("nan"))],
    }
    snapshot = closed_snapshot(history, decision_utc=15300)
    assert snapshot["H1"].time == 10800 and snapshot["H4"].time == 0


@pytest.mark.parametrize(
    ("m15_opens", "spread", "minimum", "expected"),
    [
        ([13500], 12, 2, "WARMUP"),
        ([11700, 13500], 12, 1, "DATA_GAP_UNEXPLAINED"),
        ([12600], 12, 1, "DATA_STALE"),
        ([13500], 0, 1, "DATA_SPREAD_UNAVAILABLE"),
    ],
)
def test_snapshot_rejects_unusable_history(m15_opens, spread, minimum, expected):
    history = {
        "M15": [replace(BAR, time=open_utc, spread=spread) for open_utc in m15_opens],
        "H1": [replace(BAR, time=10800)],
        "H4": [replace(BAR, time=0)],
    }
    with pytest.raises(ValueError, match=f"^{expected}$"):
        closed_snapshot(history, decision_utc=14400, minimum_bars=minimum)


def test_utc_cutoff_and_timestamp_must_be_nonnegative_integer_seconds():
    with pytest.raises(ValueError, match="DATA_TIMESTAMP_INVALID"):
        validate_closed_bars([BAR], now_utc=1800.0)
    with pytest.raises(ValueError, match="DATA_TIMESTAMP_INVALID"):
        closed_snapshot({"M15": [replace(BAR, time=-1)]}, decision_utc=1800)
    with pytest.raises(ValueError, match="DATA_SNAPSHOT_REQUEST_INVALID"):
        closed_snapshot({}, decision_utc=1800, minimum_bars=0)
