import json
from types import SimpleNamespace

import pytest

import aurum.mt5_client as client
from aurum.cli import main
from aurum.mt5_client import TIMEFRAME_SECONDS, diagnose, fetch_history

NOW = 1_728_000_050
SYMBOL = "XAUUSDm"


def bar(timestamp, **overrides):
    return {
        "time": timestamp,
        "open": 2400.0,
        "high": 2402.0,
        "low": 2399.0,
        "close": 2401.0,
        "tick_volume": 42,
        "spread": 23,
        **overrides,
    }


def history(timeframe, count=2):
    seconds = TIMEFRAME_SECONDS[timeframe]
    current_open = NOW // seconds * seconds
    return [bar(current_open - index * seconds) for index in range(count, 0, -1)]


@pytest.fixture
def mt5(monkeypatch, tmp_path):
    (tmp_path / "Files").mkdir()
    terminal = SimpleNamespace(connected=True, trade_allowed=True, commondata_path=str(tmp_path))
    account = SimpleNamespace(
        login=98765432,
        trade_mode=0,
        server="Broker-Demo",
        currency="USD",
        balance=1000.0,
        equity=1000.0,
        margin=0.0,
        margin_free=1000.0,
        leverage=500,
        trade_allowed=True,
        trade_expert=True,
    )
    symbol = SimpleNamespace(
        digits=2,
        point=0.01,
        trade_mode=4,
        trade_stops_level=10,
        trade_freeze_level=0,
        trade_tick_size=0.01,
        trade_tick_value=1.0,
        trade_contract_size=100.0,
        filling_mode=1,
        trade_calc_mode=4,
        volume_min=0.01,
        volume_max=50.0,
        volume_step=0.01,
        margin_initial=0.0,
        margin_maintenance=0.0,
        currency_margin="USD",
    )
    tick = SimpleNamespace(bid=2400.0, ask=2400.25, time=NOW)
    calls = []

    def select(name, selected):
        calls.append(("select", name, selected))
        return name == SYMBOL and selected

    def copy_rates(name, timeframe, start, count):
        calls.append(("rates", name, timeframe, start, count))
        assert name == SYMBOL and start == 1
        return history(timeframe, count)

    module = SimpleNamespace(
        initialize=lambda: True,
        terminal_info=lambda: terminal,
        account_info=lambda: account,
        symbol_select=select,
        symbol_info=lambda name: symbol if name == SYMBOL else None,
        symbol_info_tick=lambda name: tick if name == SYMBOL else None,
        copy_rates_from_pos=copy_rates,
        shutdown=lambda: calls.append("shutdown"),
        calls=calls,
        **{f"TIMEFRAME_{name}": name for name in TIMEFRAME_SECONDS},
    )
    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=lambda _: module))
    monkeypatch.setattr(client, "time", SimpleNamespace(time=lambda: NOW))
    return module


def test_missing_mt5_is_not_ready(monkeypatch):
    def missing(_):
        raise ImportError("not installed")

    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=missing))
    assert diagnose(SYMBOL)["reason_code"] == "MT5_PACKAGE_MISSING"
    assert fetch_history(SYMBOL, "M15", 1)["reason_code"] == "MT5_PACKAGE_MISSING"


def test_doctor_reports_broker_properties_and_reads_only_closed_bars(mt5, capsys):
    assert main(["doctor", "--symbol", SYMBOL]) == 0
    output = capsys.readouterr().out
    report = json.loads(output)
    assert report["status"] == report["connection_status"] == "CONNECTED"
    assert report["quote_status"] == report["history_status"] == "READY"
    assert report["common_files_status"] == "AVAILABLE"
    assert report["model_status"] == "NOT_IMPLEMENTED"
    assert report["closed_snapshot"] == {
        "decision_time_utc": NOW - 50,
        "bar_open_times_utc": {tf: history(tf)[-1]["time"] for tf in TIMEFRAME_SECONDS},
    }
    assert report["symbol"] == SYMBOL and report["server"] == "Broker-Demo"
    assert report["account_mask"] == "***32"
    assert report["leverage"] == 500 and report["leverage_matches_2000"] is False
    assert report["balance"] == 1000 and report["margin_free"] == 1000
    assert report["spread_points"] == 25
    assert report["symbol_properties"]["entry_directions"] == ["BUY", "SELL"]
    assert report["symbol_properties"]["trade_contract_size"] == 100
    assert report["symbol_properties"]["volume_step"] == 0.01
    assert report["symbol_properties"]["margin_initial"] == 0
    assert report["action"] == "WAIT" and report["execution_available"] is False
    assert "98765432" not in output and mt5.terminal_info().commondata_path not in output
    assert mt5.calls == [
        ("select", SYMBOL, True),
        *(("rates", SYMBOL, tf, 1, 2) for tf in TIMEFRAME_SECONDS),
        "shutdown",
    ]


@pytest.mark.parametrize(
    ("failure", "reason"),
    [
        ("initialize", "MT5_INITIALIZE_FAILED"),
        ("terminal_info", "MT5_DISCONNECTED"),
        ("account_info", "MT5_DISCONNECTED"),
        ("symbol_select", "SYMBOL_UNAVAILABLE"),
        ("symbol_info", "SYMBOL_DATA_MISSING"),
        ("symbol_info_tick", "TICK_INVALID_OR_STALE"),
    ],
)
def test_doctor_returns_specific_reason_on_mt5_failure(mt5, failure, reason):
    setattr(mt5, failure, lambda *_: None)
    report = diagnose(SYMBOL)
    assert report["status"] == "NOT_READY" and report["reason_code"] == reason
    assert report["action"] == "WAIT"
    assert mt5.calls.count("shutdown") == (0 if failure == "initialize" else 1)


@pytest.mark.parametrize(
    ("target", "field", "value", "reason"),
    [
        ("terminal_info", "connected", False, "MT5_DISCONNECTED"),
        ("terminal_info", "trade_allowed", False, "MT5_TRADE_NOT_ALLOWED"),
        ("account_info", "trade_allowed", False, "MT5_TRADE_NOT_ALLOWED"),
        ("account_info", "trade_expert", False, "MT5_TRADE_NOT_ALLOWED"),
        ("account_info", "login", 0, "MT5_ACCOUNT_INVALID"),
        ("account_info", "server", "", "MT5_ACCOUNT_INVALID"),
        ("account_info", "trade_mode", 3, "MT5_ACCOUNT_INVALID"),
        ("account_info", "margin_free", float("nan"), "MT5_ACCOUNT_INVALID"),
        ("account_info", "margin", -1.0, "MT5_ACCOUNT_INVALID"),
        ("symbol_info", "trade_mode", 0, "SYMBOL_TRADE_NOT_ALLOWED"),
        ("symbol_info", "trade_mode", 3, "SYMBOL_TRADE_NOT_ALLOWED"),
        ("symbol_info", "trade_mode", 5, "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "digits", -1, "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "volume_min", 100.0, "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "volume_step", 100.0, "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "margin_initial", -1, "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "currency_margin", "", "SYMBOL_METADATA_INVALID"),
        ("symbol_info", "point", 0.0, "SYMBOL_METADATA_INVALID"),
        ("symbol_info_tick", "bid", 0, "TICK_INVALID_OR_STALE"),
        ("symbol_info_tick", "ask", float("nan"), "TICK_INVALID_OR_STALE"),
        ("symbol_info_tick", "time", NOW - 121, "TICK_INVALID_OR_STALE"),
        ("symbol_info_tick", "time", NOW + 1, "TICK_INVALID_OR_STALE"),
        ("terminal_info", "commondata_path", "relative", "COMMON_FILES_UNAVAILABLE"),
        ("terminal_info", "commondata_path", None, "COMMON_FILES_UNAVAILABLE"),
    ],
)
def test_doctor_rejects_invalid_metadata_and_denied_permissions(mt5, target, field, value, reason):
    method = getattr(mt5, target)
    obj = method(SYMBOL) if target.startswith("symbol_info") else method()
    setattr(obj, field, value)
    report = diagnose(SYMBOL)
    assert report["status"] == "NOT_READY" and report["reason_code"] == reason
    if reason.endswith("TRADE_NOT_ALLOWED"):
        assert report["connection_status"] == "CONNECTED"
        assert report["permission_status"] == "DENIED"
        assert report["history_status"] == "READY"
    assert mt5.calls[-1] == "shutdown"


def test_doctor_rejects_nonfinite_spread_before_serialization(mt5, capsys):
    mt5.symbol_info(SYMBOL).point = 1e-308
    mt5.symbol_info_tick(SYMBOL).ask = 1e308
    assert main(["doctor", "--symbol", SYMBOL]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["reason_code"] == "TICK_INVALID_OR_STALE" and report["spread_points"] is None


def test_diagnostics_preserves_readiness_for_one_allowed_direction(mt5):
    mt5.symbol_info(SYMBOL).trade_mode = 2
    mt5.account_info().login = 12
    mt5.symbol_info_tick(SYMBOL).ask = mt5.symbol_info_tick(SYMBOL).bid
    report = diagnose(SYMBOL)
    assert report["status"] == "CONNECTED"
    assert report["account_mask"] == "***"
    assert report["spread_points"] == 0
    assert report["symbol_properties"]["entry_directions"] == ["SELL"]


@pytest.mark.parametrize(
    ("rates", "expected"),
    [
        (None, "HISTORY_UNAVAILABLE"),
        ([], "HISTORY_INSUFFICIENT"),
        (history("H1", 1), "HISTORY_INSUFFICIENT"),
        (history("H1", 3), "HISTORY_PAYLOAD_INVALID"),
        ([{}, {}], "HISTORY_PAYLOAD_INVALID"),
        ([bar(True), *history("H1", 1)], "HISTORY_PAYLOAD_INVALID"),
        ([bar(NOW - 7200, tick_volume=1.5), *history("H1", 1)], "HISTORY_PAYLOAD_INVALID"),
        ([bar(NOW - 7200, open="2400"), *history("H1", 1)], "HISTORY_PAYLOAD_INVALID"),
        ([bar(NOW - 7200, open=float("nan")), *history("H1", 1)], "DATA_PRICE_INVALID"),
        ([bar(NOW - 7200, tick_volume=-1), *history("H1", 1)], "DATA_VOLUME_INVALID"),
        (history("H1")[::-1], "DATA_TIMESTAMP_INVALID"),
        (history("H1", 1) * 2, "DATA_TIMESTAMP_INVALID"),
        ([*history("H1", 1), bar(NOW - 50)], "DATA_BAR_NOT_CLOSED"),
        ([bar(NOW - 10850), bar(NOW - 7250)], "DATA_STALE"),
        ([bar(NOW - 3710), *history("H1", 1)], "DATA_BAR_OVERLAP"),
        ([bar(NOW - 10850), *history("H1", 1)], "DATA_GAP_UNEXPLAINED"),
        ([*history("H1", 2)[:1], bar(NOW - 3650, spread=0.5)], "DATA_SPREAD_INVALID"),
        ([*history("H1", 2)[:1], bar(NOW - 3650, high=24010)], "DATA_BAR_OUTLIER"),
    ],
)
def test_bad_history_is_visible_in_doctor_and_never_returned_as_data(mt5, rates, expected):
    copy_rates = mt5.copy_rates_from_pos
    mt5.copy_rates_from_pos = lambda name, tf, start, count: (
        rates if tf == "H1" else copy_rates(name, tf, start, count)
    )
    doctor = diagnose(SYMBOL)
    assert doctor["status"] == "NOT_READY" and doctor["reason_code"] == "HISTORY_NOT_READY"
    assert doctor["history"]["M15"]["status"] == "READY"
    assert doctor["history"]["H1"]["reason_code"] == expected
    fetched = fetch_history(SYMBOL, "H1", 2)
    assert fetched["status"] == "NOT_READY" and fetched["reason_code"] == expected
    assert "bars" not in fetched


@pytest.mark.parametrize("timeframe", TIMEFRAME_SECONDS)
def test_fetch_returns_closed_utc_bars_and_source_metadata(mt5, capsys, timeframe, tmp_path):
    records = history(timeframe)
    seconds = TIMEFRAME_SECONDS[timeframe]
    records[0]["time"] -= seconds
    config = tmp_path / "history.yaml"
    config.write_text(
        f"history_session_closures_utc: [[{records[0]['time'] + seconds}, {records[1]['time']}]]\n",
        encoding="utf-8",
    )
    mt5.copy_rates_from_pos = lambda name, tf, start, count: (
        records if (name, tf, start, count) == (SYMBOL, timeframe, 1, 2) else None
    )
    mt5.account_info().trade_allowed = False
    assert (
        main(
            [
                "fetch-data",
                "--symbol",
                SYMBOL,
                "--timeframe",
                timeframe,
                "--bars",
                "2",
                "--config",
                str(config),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    report = json.loads(output)
    assert report["status"] == "READY" and report["action"] == "WAIT"
    assert report["symbol"] == SYMBOL and report["timeframe"] == timeframe
    assert report["source"] == {"provider": "MetaTrader5", "server": "Broker-Demo"}
    assert report["point"] == 0.01
    assert report["bars"] == [{**record, "spread_price": 0.23} for record in records]
    assert report["history"]["gap_timestamps_utc"] == [records[-1]["time"]]
    assert report["history"]["gaps"] == [
        {
            "first_missing_open_utc": records[0]["time"] + seconds,
            "next_bar_open_utc": records[1]["time"],
            "kind": "SCHEDULED_CLOSURE",
        }
    ]
    assert "98765432" not in output and mt5.calls[-1] == "shutdown"


def test_fetch_cli_exits_nonzero_on_unexplained_gap(mt5, capsys):
    records = history("M15")
    records[0]["time"] -= 900
    mt5.copy_rates_from_pos = lambda *_: records
    assert main(["fetch-data", "--symbol", SYMBOL, "--bars", "2"]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "NOT_READY" and report["reason_code"] == "DATA_GAP_UNEXPLAINED"
    assert report["action"] == "WAIT" and report["execution_available"] is False
    assert report["history"]["gaps"][0]["kind"] == "UNKNOWN" and "bars" not in report


def test_fetch_stale_at_exact_close_age_boundary(mt5):
    mt5.copy_rates_from_pos = lambda *_: [bar(NOW - 2700), bar(NOW - 1800)]
    result = fetch_history(SYMBOL, "M15", 2)
    assert result["reason_code"] == "DATA_STALE" and "bars" not in result
    assert result["history"]["last_bar_close_age_seconds"] == 900


def test_zero_historical_spread_can_be_exported_but_blocks_snapshot(mt5):
    copy_rates = mt5.copy_rates_from_pos

    def with_zero_spread(name, timeframe, start, count):
        records = copy_rates(name, timeframe, start, count)
        if timeframe == "M15":
            records[-1]["spread"] = 0
        return records

    mt5.copy_rates_from_pos = with_zero_spread
    result = fetch_history(SYMBOL, "M15", 2)
    assert result["status"] == "READY" and result["bars"][-1]["spread_price"] is None
    diagnostic = diagnose(SYMBOL)
    assert (
        diagnostic["status"] == "NOT_READY"
        and diagnostic["reason_code"] == "DATA_SPREAD_UNAVAILABLE"
    )


def test_doctor_uses_h4_closed_before_m15_cutoff(mt5):
    copy_rates = mt5.copy_rates_from_pos
    newest_h4 = NOW - 30 - TIMEFRAME_SECONDS["H4"]
    older_h4 = newest_h4 - TIMEFRAME_SECONDS["H4"]

    def h4_closed_after_m15(name, timeframe, start, count):
        if timeframe == "H4":
            return [bar(older_h4), bar(newest_h4, close="malformed future value")]
        return copy_rates(name, timeframe, start, count)

    mt5.copy_rates_from_pos = h4_closed_after_m15
    result = diagnose(SYMBOL)
    assert result["status"] == "CONNECTED"
    assert result["history"]["H4"]["last_bar_open_utc"] == older_h4
    assert result["history"]["H4"]["evaluated_bars"] == 1
    assert result["closed_snapshot"]["bar_open_times_utc"]["H4"] == older_h4


@pytest.mark.parametrize("count", ["0", "-1", "100001"])
def test_invalid_history_request_fails_before_mt5(mt5, capsys, count):
    mt5.initialize = lambda: pytest.fail("invalid history request initialized MT5")
    assert main(["fetch-data", "--bars", count]) == 2
    assert json.loads(capsys.readouterr().out)["reason_code"] == "HISTORY_REQUEST_INVALID"


def test_unknown_timeframe_rejected_before_mt5(mt5):
    mt5.initialize = lambda: pytest.fail("unsupported timeframe initialized MT5")
    with pytest.raises(SystemExit) as exc:
        main(["fetch-data", "--timeframe", "M1"])
    assert exc.value.code == 2
    assert fetch_history(SYMBOL, "M1", 2)["reason_code"] == "HISTORY_REQUEST_INVALID"


@pytest.mark.parametrize("operation", [diagnose, lambda symbol: fetch_history(symbol, "M15", 2)])
def test_session_change_discards_data_and_account_details(mt5, operation):
    first = mt5.account_info()
    snapshots = iter([first, SimpleNamespace(**(vars(first) | {"server": "Other-Demo"}))])
    mt5.account_info = lambda: next(snapshots)
    report = operation(SYMBOL)
    assert report["status"] == "NOT_READY" and report["reason_code"] == "MT5_ACCOUNT_CHANGED"
    assert "bars" not in report and "account_mask" not in report
    assert mt5.calls[-1] == "shutdown"


def test_fetch_rejects_missing_point(mt5):
    mt5.symbol_info(SYMBOL).point = None
    assert fetch_history(SYMBOL, "M15", 2)["reason_code"] == "SYMBOL_METADATA_INVALID"


def test_diagnostics_exception_still_shuts_down_and_cli_fails(mt5, capsys):
    def fail():
        raise RuntimeError("private diagnostic details")

    mt5.terminal_info = fail
    assert main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert json.loads(output)["reason_code"] == "MT5_DIAGNOSTICS_FAILED"
    assert "private diagnostic details" not in output and mt5.calls == ["shutdown"]
