"""Read-only MT5 diagnostics and closed-bar history."""

import importlib
import math
import time
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from numbers import Real
from operator import index
from pathlib import Path
from types import ModuleType
from typing import Any

from aurum.contracts import Bar
from aurum.data_quality import gap_timestamps, validate_closed_bars

TIMEFRAME_SECONDS = {"M15": 900, "H1": 3600, "H4": 14400}
MAX_HISTORY_BARS = 100_000
DOCTOR_HISTORY_BARS = 2
MAX_TICK_AGE_SECONDS = 120

# ENUM_SYMBOL_TRADE_MODE. Directional modes each permit one entry direction.
ENTRY_DIRECTIONS = {1: ["BUY"], 2: ["SELL"], 4: ["BUY", "SELL"]}


class _Unavailable(Exception):
    """A public reason code with no raw terminal details."""


def _status(status: str, reason: str) -> dict[str, Any]:
    return {
        "status": status,
        "reason_code": reason,
        "action": "WAIT",
        "execution_available": False,
    }


@contextmanager
def _session() -> Iterator[ModuleType]:
    try:
        mt5 = importlib.import_module("MetaTrader5")
    except ImportError as exc:
        raise _Unavailable("MT5_PACKAGE_MISSING") from exc
    if not mt5.initialize():
        raise _Unavailable("MT5_INITIALIZE_FAILED")
    try:
        yield mt5
    finally:
        mt5.shutdown()


def _connected(mt5: ModuleType) -> tuple[Any, Any]:
    terminal, account = mt5.terminal_info(), mt5.account_info()
    if terminal is None or account is None or terminal.connected is not True:
        raise _Unavailable("MT5_DISCONNECTED")
    return terminal, account


def _identity(account: Any) -> tuple[int, str, int]:
    login, server, mode = account.login, account.server, account.trade_mode
    if (
        type(login) is not int
        or login <= 0
        or not isinstance(server, str)
        or not server.strip()
        or type(mode) is not int
        or mode not in (0, 1, 2)
    ):
        raise _Unavailable("MT5_ACCOUNT_INVALID")
    return login, server, mode


def _verify_identity(mt5: ModuleType, expected: tuple[int, str, int]) -> None:
    _, account = _connected(mt5)
    if _identity(account) != expected:
        raise _Unavailable("MT5_ACCOUNT_CHANGED")


def _select_symbol(mt5: ModuleType, symbol: str) -> Any:
    if not mt5.symbol_select(symbol, True):
        raise _Unavailable("SYMBOL_UNAVAILABLE")
    info = mt5.symbol_info(symbol)
    if info is None:
        raise _Unavailable("SYMBOL_DATA_MISSING")
    return info


def _finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def _account_report(terminal: Any, account: Any, login: int) -> dict[str, Any]:
    if (
        type(account.leverage) is not int
        or account.leverage <= 0
        or not isinstance(account.currency, str)
        or not account.currency.strip()
        or not all(
            _finite(value)
            for value in (account.balance, account.equity, account.margin, account.margin_free)
        )
        or account.margin < 0
        or type(terminal.trade_allowed) is not bool
        or type(account.trade_allowed) is not bool
        or type(account.trade_expert) is not bool
    ):
        raise _Unavailable("MT5_ACCOUNT_INVALID")
    digits = str(login)
    return {
        "account_mask": "***" + digits[-2:] if len(digits) > 2 else "***",
        "server": account.server,
        "account_trade_mode": account.trade_mode,
        "currency": account.currency,
        "balance": account.balance,
        "equity": account.equity,
        "margin": account.margin,
        "margin_free": account.margin_free,
        "leverage": account.leverage,
        "leverage_matches_2000": account.leverage == 2000,
        "terminal_trade_allowed": terminal.trade_allowed,
        "account_trade_allowed": account.trade_allowed,
        "account_expert_allowed": account.trade_expert,
    }


def _symbol_report(info: Any) -> dict[str, Any]:
    metadata = {
        field: getattr(info, field)
        for field in (
            "digits",
            "trade_mode",
            "trade_stops_level",
            "trade_freeze_level",
            "filling_mode",
            "trade_calc_mode",
            "point",
            "trade_tick_size",
            "trade_tick_value",
            "trade_contract_size",
            "volume_min",
            "volume_max",
            "volume_step",
            "margin_initial",
            "margin_maintenance",
        )
    }
    integers = (
        "digits",
        "trade_mode",
        "trade_stops_level",
        "trade_freeze_level",
        "filling_mode",
        "trade_calc_mode",
    )
    positive = (
        "point",
        "trade_tick_size",
        "trade_tick_value",
        "trade_contract_size",
        "volume_min",
        "volume_max",
        "volume_step",
    )
    if (
        any(type(metadata[key]) is not int or metadata[key] < 0 for key in integers)
        or metadata["trade_mode"] > 4
        or any(not _finite(metadata[key]) or metadata[key] <= 0 for key in positive)
        or metadata["volume_min"] > metadata["volume_max"]
        or metadata["volume_step"] > metadata["volume_max"]
        or any(
            not _finite(metadata[key]) or metadata[key] < 0
            for key in ("margin_initial", "margin_maintenance")
        )
        or not isinstance(info.currency_margin, str)
        or not info.currency_margin.strip()
    ):
        raise _Unavailable("SYMBOL_METADATA_INVALID")
    return {
        **metadata,
        "currency_margin": info.currency_margin,
        "entry_directions": ENTRY_DIRECTIONS.get(info.trade_mode, []).copy(),
    }


def _tick_report(tick: Any, point: float, now_utc: float) -> dict[str, Any]:
    if (
        tick is None
        or not all(_finite(value) for value in (tick.bid, tick.ask, tick.time))
        or not 0 < tick.bid <= tick.ask
        or not 0 <= now_utc - tick.time <= MAX_TICK_AGE_SECONDS
    ):
        raise _Unavailable("TICK_INVALID_OR_STALE")
    spread_points = (tick.ask - tick.bid) / point
    if not math.isfinite(spread_points):
        raise _Unavailable("TICK_INVALID_OR_STALE")
    return {"time_utc": tick.time, "bid": tick.bid, "ask": tick.ask, "spread_points": spread_points}


def _bar(row: Any) -> Bar:
    timestamp, volume = row["time"], row["tick_volume"]
    prices = [row[key] for key in ("open", "high", "low", "close", "spread")]
    if (
        isinstance(timestamp, bool)
        or isinstance(volume, bool)
        or any(isinstance(value, bool) or not isinstance(value, Real) for value in prices)
    ):
        raise TypeError("HISTORY_PAYLOAD_INVALID")
    open_price, high, low, close, spread = map(float, prices)
    return Bar(index(timestamp), open_price, high, low, close, index(volume), spread)


def _history(
    mt5: ModuleType, symbol: str, timeframe: str, count: int, now_utc: int
) -> tuple[dict[str, Any], list[Bar]]:
    seconds = TIMEFRAME_SECONDS[timeframe]
    rates = mt5.copy_rates_from_pos(symbol, getattr(mt5, f"TIMEFRAME_{timeframe}"), 1, count)
    report: dict[str, Any] = {"requested_bars": count, "received_bars": 0, "status": "NOT_READY"}
    try:
        if rates is None:
            return {**report, "reason_code": "HISTORY_UNAVAILABLE"}, []
        report["received_bars"] = len(rates)
        if len(rates) < count:
            return {**report, "reason_code": "HISTORY_INSUFFICIENT"}, []
        if len(rates) > count:
            return {**report, "reason_code": "HISTORY_PAYLOAD_INVALID"}, []
        bars = [_bar(row) for row in rates]
    except (KeyError, TypeError, ValueError, IndexError, OverflowError):
        return {**report, "reason_code": "HISTORY_PAYLOAD_INVALID"}, []
    try:
        validate_closed_bars(bars, now_utc=now_utc, seconds=seconds)
    except ValueError as exc:
        return {**report, "reason_code": str(exc)}, []

    last_open = bars[-1].time
    close_age = now_utc - (last_open + seconds)
    stale = close_age >= seconds
    report.update(
        status="NOT_READY" if stale else "READY",
        reason_code="DATA_STALE" if stale else "HISTORY_READY",
        first_bar_open_utc=bars[0].time,
        last_bar_open_utc=last_open,
        last_bar_close_utc=last_open + seconds,
        last_bar_close_age_seconds=close_age,
        gap_timestamps_utc=gap_timestamps(bars, seconds=seconds),
    )
    return report, [] if stale else bars


def _common_files_status(terminal: Any) -> str:
    location = getattr(terminal, "commondata_path", None)
    if not isinstance(location, str) or not location:
        return "UNAVAILABLE"
    root = Path(location)
    try:
        return "AVAILABLE" if root.is_absolute() and (root / "Files").is_dir() else "UNAVAILABLE"
    except (OSError, ValueError):
        return "UNAVAILABLE"


def diagnose(symbol: str) -> dict[str, Any]:
    report: dict[str, Any] = {
        "symbol": symbol,
        "connection_status": "NOT_READY",
        "quote_status": "NOT_CHECKED",
        "permission_status": "NOT_CHECKED",
        "history_status": "NOT_CHECKED",
        "common_files_status": "NOT_CHECKED",
        "model_status": "NOT_IMPLEMENTED",
    }
    try:
        with _session() as mt5:
            terminal, account = _connected(mt5)
            report["connection_status"] = "CONNECTED"
            identity = _identity(account)
            report.update(_account_report(terminal, account, identity[0]))
            info = _select_symbol(mt5, symbol)
            report["symbol_properties"] = _symbol_report(info)
            allowed = (
                info.trade_mode in ENTRY_DIRECTIONS
                and terminal.trade_allowed
                and account.trade_allowed
                and account.trade_expert
            )
            report["permission_status"] = "ALLOWED" if allowed else "DENIED"
            report["common_files_status"] = _common_files_status(terminal)

            tick = mt5.symbol_info_tick(symbol)
            now = time.time()
            try:
                report["tick"] = _tick_report(tick, info.point, now)
            except _Unavailable:
                report["quote_status"] = "NOT_READY"
                report["spread_points"] = None
            else:
                report["quote_status"] = "READY"
                report["spread_points"] = report["tick"]["spread_points"]

            history = {
                timeframe: _history(mt5, symbol, timeframe, DOCTOR_HISTORY_BARS, int(now))[0]
                for timeframe in TIMEFRAME_SECONDS
            }
            report["history"] = history
            history_ready = all(check["status"] == "READY" for check in history.values())
            report["history_status"] = "READY" if history_ready else "NOT_READY"
            _verify_identity(mt5, identity)
            if info.trade_mode not in ENTRY_DIRECTIONS:
                raise _Unavailable("SYMBOL_TRADE_NOT_ALLOWED")
            if not allowed:
                raise _Unavailable("MT5_TRADE_NOT_ALLOWED")
            if report["quote_status"] != "READY":
                raise _Unavailable("TICK_INVALID_OR_STALE")
            if not history_ready:
                raise _Unavailable("HISTORY_NOT_READY")
            if report["common_files_status"] != "AVAILABLE":
                raise _Unavailable("COMMON_FILES_UNAVAILABLE")
    except _Unavailable as exc:
        if str(exc) in ("MT5_ACCOUNT_CHANGED", "MT5_DISCONNECTED", "MT5_ACCOUNT_INVALID"):
            return {**_status("NOT_READY", str(exc)), "symbol": symbol}
        return {**report, **_status("NOT_READY", str(exc))}
    return {**report, **_status("CONNECTED", "DIAGNOSTICS_ONLY")}


def fetch_history(symbol: str, timeframe: str, count: int) -> dict[str, Any]:
    if (
        timeframe not in TIMEFRAME_SECONDS
        or type(count) is not int
        or not 1 <= count <= MAX_HISTORY_BARS
    ):
        return _status("ERROR", "HISTORY_REQUEST_INVALID")
    try:
        with _session() as mt5:
            _, account = _connected(mt5)
            identity = _identity(account)
            info = _select_symbol(mt5, symbol)
            if not _finite(info.point) or info.point <= 0:
                raise _Unavailable("SYMBOL_METADATA_INVALID")
            history, bars = _history(mt5, symbol, timeframe, count, int(time.time()))
            _verify_identity(mt5, identity)
            if not bars:
                return {**_status("NOT_READY", history["reason_code"]), "history": history}
            return {
                **_status("READY", "HISTORY_READY"),
                "source": {"provider": "MetaTrader5", "server": identity[1]},
                "symbol": symbol,
                "timeframe": timeframe,
                "point": info.point,
                "history": history,
                "bars": [asdict(bar) for bar in bars],
            }
    except _Unavailable as exc:
        return _status("NOT_READY", str(exc))
