from types import SimpleNamespace

import pytest

import aurum.mt5_client as client
from aurum.mt5_client import diagnose


def test_missing_mt5_is_not_ready(monkeypatch):
    def missing(_):
        raise ImportError("not installed")

    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=missing))
    assert diagnose("XAUUSD")["reason_code"] == "MT5_PACKAGE_MISSING"


@pytest.mark.parametrize(
    "connected,stale,expected",
    [
        (False, False, "MT5_DISCONNECTED"),
        (True, True, "TICK_INVALID_OR_STALE"),
        (True, False, "DIAGNOSTICS_ONLY"),
    ],
)
def test_diagnostics_mask_and_close(monkeypatch, connected, stale, expected):
    calls = []
    terminal = SimpleNamespace(connected=connected, trade_allowed=True)
    account = SimpleNamespace(login=12345678, leverage=2000, trade_allowed=True)
    module = SimpleNamespace(
        initialize=lambda: True,
        terminal_info=lambda: terminal,
        account_info=lambda: account,
        symbol_select=lambda symbol, selected: True,
        symbol_info=lambda symbol: SimpleNamespace(point=0.01),
        symbol_info_tick=lambda symbol: SimpleNamespace(
            bid=100, ask=101, time=0 if stale else 1000
        ),
        shutdown=lambda: calls.append("shutdown"),
    )
    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=lambda _: module))
    monkeypatch.setattr(client, "time", SimpleNamespace(time=lambda: 1000))
    report = diagnose("XAUUSDm")
    assert report["reason_code"] == expected
    assert "12345678" not in str(report)
    assert calls == ["shutdown"]
    if connected and not stale:
        assert report["status"] == "CONNECTED"
        assert report["symbol"] == "XAUUSDm"
        assert report["execution_available"] is False


@pytest.mark.parametrize(
    ("failure", "reason", "expected_shutdown"),
    [
        ("initialize", "MT5_INITIALIZE_FAILED", []),
        ("symbol_select", "SYMBOL_UNAVAILABLE", ["shutdown"]),
        ("symbol_info", "SYMBOL_DATA_MISSING", ["shutdown"]),
        ("symbol_info_tick", "SYMBOL_DATA_MISSING", ["shutdown"]),
    ],
)
def test_diagnostics_failure_reports_not_ready(monkeypatch, failure, reason, expected_shutdown):
    calls = []
    module = SimpleNamespace(
        initialize=lambda: True,
        terminal_info=lambda: SimpleNamespace(connected=True),
        account_info=lambda: SimpleNamespace(),
        symbol_select=lambda *_: True,
        symbol_info=lambda _: SimpleNamespace(),
        symbol_info_tick=lambda _: SimpleNamespace(),
        shutdown=lambda: calls.append("shutdown"),
    )
    monkeypatch.setattr(module, failure, lambda *_: None)
    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=lambda _: module))
    assert diagnose("XAUUSDm") == {"status": "NOT_READY", "reason_code": reason}
    assert calls == expected_shutdown


def test_diagnostics_exception_still_shuts_down_and_cli_fails(monkeypatch, capsys):
    from aurum.cli import main

    calls = []

    def fail():
        raise RuntimeError("private diagnostic details")

    module = SimpleNamespace(
        initialize=lambda: True,
        terminal_info=fail,
        shutdown=lambda: calls.append("shutdown"),
    )
    monkeypatch.setattr(client, "importlib", SimpleNamespace(import_module=lambda _: module))
    assert main(["doctor"]) == 1
    output = capsys.readouterr().out
    assert '"reason_code": "MT5_DIAGNOSTICS_FAILED"' in output
    assert "private diagnostic details" not in output
    assert calls == ["shutdown"]
