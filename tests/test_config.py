from dataclasses import replace

import pytest

from aurum.config import Settings, load_config


def test_safe_defaults():
    config = load_config("config/default.yaml")
    assert config == Settings()
    assert config.signal_only and config.demo_only and not config.auto_trade
    assert config.risk_percent_per_trade == 0.25


@pytest.mark.parametrize(
    "change",
    [
        {"auto_trade": True},
        {"signal_only": False},
        {"demo_only": False},
        {"live_trading_confirmation": "ENABLE"},
        {"partial_tp": True},
        {"max_lot": float("nan")},
        {"max_lot": float("inf")},
        {"max_lot": -1},
        {"max_entries_per_day": True},
        {"signal_only": "false"},
        {"timeframe": "M5"},
        {"risk_percent_per_trade": 101},
        {"symbol": "../XAUUSD"},
        {"min_planned_rr": 1.5},
        {"history_max_bar_move_percent": 101},
        {"history_session_closures_utc": ((0, 10), (5, 20))},
        {"history_session_closures_utc": ((True, 100),)},
    ],
)
def test_invalid_or_execution_config_rejected(change):
    with pytest.raises(ValueError):
        replace(Settings(), **change)


@pytest.mark.parametrize(
    "text",
    [
        "[]",
        "auto_trdae: true",
        "signal_only: 'false'",
        "confirmation_timeframes: H1",
        "symbol: [",
        "history_session_closures_utc: [2026-11-23]",
        "history_session_closures_utc: [[1, 2, 3]]",
    ],
)
def test_bad_yaml_fails_closed(tmp_path, text):
    path = tmp_path / "bad.yaml"
    path.write_text(text)
    with pytest.raises(ValueError):
        load_config(path)


def test_broker_suffix_preserved():
    assert replace(Settings(), symbol="XAUUSD.a").symbol == "XAUUSD.a"
