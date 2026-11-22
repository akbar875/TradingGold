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
