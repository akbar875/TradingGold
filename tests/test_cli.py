import json

import pytest

from aurum.cli import PENDING, main


def test_offline_doctor_never_connects(monkeypatch, capsys):
    def forbidden(*args):
        raise AssertionError("Offline mode attempted a broker connection")

    monkeypatch.setattr("aurum.cli.diagnose", forbidden)
    assert main(["doctor", "--offline"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "OFFLINE"
    assert report["execution_available"] is False


@pytest.mark.parametrize("command", PENDING)
def test_unimplemented_commands_do_not_report_success(command, capsys):
    assert main([command]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "NOT_IMPLEMENTED"
    assert report["action"] == "WAIT"


def test_missing_config_is_error(tmp_path, capsys):
    assert main(["doctor", "--offline", "--config", str(tmp_path / "missing")]) == 2
    assert json.loads(capsys.readouterr().out)["status"] == "ERROR"


@pytest.mark.parametrize(
    ("contents", "reason"),
    [
        ("require_news_filter: true\nrequire_news_filter: false\n", "CONFIG_DUPLICATE_KEY"),
        ("<<: {require_news_filter: true}\nrequire_news_filter: false", "CONFIG_DUPLICATE_KEY"),
        ("!!map []", "CONFIG_YAML_INVALID"),
        ("unexpected: true\n123: false\n", "CONFIG_KEY_NOT_STRING"),
        ("max_lot: " + "9" * 400, "CONFIG_INVALID: max_lot"),
        ('symbol: "XAUUSD\\0"', "CONFIG_SYMBOL_INVALID"),
        (b"\xff", "CONFIG_ENCODING_INVALID"),
    ],
)
def test_invalid_config_returns_structured_error(tmp_path, capsys, contents, reason):
    config_path = tmp_path / "invalid.yaml"
    config_path.write_bytes(contents if isinstance(contents, bytes) else contents.encode("utf-8"))

    assert main(["show-config", "--config", str(config_path)]) == 2
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "ERROR"
    assert report["reason"].startswith(reason)


@pytest.mark.parametrize("symbol", ["../INVALID", "", "   ", "XAUUSD\t"])
def test_invalid_symbol_override_stops_before_mt5(monkeypatch, capsys, symbol):
    def forbidden(*args):
        pytest.fail("Invalid symbol reached MT5 diagnostics")

    monkeypatch.setattr("aurum.cli.diagnose", forbidden)
    assert main(["doctor", "--symbol", symbol]) == 2
    assert json.loads(capsys.readouterr().out) == {
        "status": "ERROR",
        "reason": "CONFIG_SYMBOL_INVALID",
    }


def test_symbol_override_is_displayed_and_used(monkeypatch, capsys):
    def diagnose(symbol, *, policy):
        assert policy.max_bar_move_percent == 10
        return {"status": "CONNECTED", "symbol": symbol}

    monkeypatch.setattr("aurum.cli.diagnose", diagnose)
    for command in ("show-config", "doctor"):
        assert main([command, "--symbol", "XAUUSDm"]) == 0
        assert json.loads(capsys.readouterr().out)["symbol"] == "XAUUSDm"
