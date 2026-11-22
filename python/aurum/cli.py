"""Foundation CLI. Unavailable product commands fail explicitly, never simulate."""

import argparse
import json
import platform
from dataclasses import replace
from pathlib import Path

from aurum import __version__
from aurum.config import load_config
from aurum.mt5_client import TIMEFRAME_SECONDS, diagnose, fetch_history

PENDING = {
    "train": "AU-017/AU-018/AU-019",
    "evaluate": "AU-019/AU-020",
    "predict": "AU-020/AU-021",
    "run": "AU-020/AU-021",
    "backtest": "AU-023",
    "export-signals": "AU-024",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aurum MT5 — scaffolding SIGNAL ONLY")
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("doctor", "fetch-data", "show-config", *PENDING):
        sub = commands.add_parser(name)
        sub.add_argument("--config", type=Path, default=Path("config/default.yaml"))
        sub.add_argument("--symbol")
        if name == "doctor":
            sub.add_argument("--offline", action="store_true")
        if name in ("predict", "run"):
            sub.add_argument("--once", action="store_true")
        if name == "fetch-data":
            sub.add_argument("--bars", type=int, default=10000)
            sub.add_argument("--timeframe", choices=TIMEFRAME_SECONDS)
    args = parser.parse_args(argv)
    try:
        settings = load_config(args.config)
        if args.symbol is not None:
            settings = replace(settings, symbol=args.symbol)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "ERROR", "reason": str(exc)}, ensure_ascii=False))
        return 2
    if args.command == "show-config":
        print(json.dumps(settings.to_dict(), indent=2))
        return 0
    if args.command in PENDING:
        print(
            json.dumps(
                {
                    "status": "NOT_IMPLEMENTED",
                    "issue": PENDING[args.command],
                    "action": "WAIT",
                    "execution_available": False,
                }
            )
        )
        return 2
    status = {
        "version": __version__,
        "python": platform.python_version(),
        "mode": "SIGNAL_ONLY",
        "execution_available": False,
        "action": "WAIT",
    }
    if args.command == "doctor" and args.offline:
        status.update({"status": "OFFLINE", "reason_code": "BROKER_NOT_CHECKED"})
    else:
        try:
            if args.command == "fetch-data":
                status.update(
                    fetch_history(settings.symbol, args.timeframe or settings.timeframe, args.bars)
                )
            else:
                status.update(diagnose(settings.symbol))
        except Exception:
            status.update({"status": "NOT_READY", "reason_code": "MT5_DIAGNOSTICS_FAILED"})
    print(json.dumps(status, indent=2, ensure_ascii=False, allow_nan=False))
    if status["status"] == "ERROR":
        return 2
    return 0 if status["status"] in ("OFFLINE", "CONNECTED", "READY") else 1


if __name__ == "__main__":
    raise SystemExit(main())
