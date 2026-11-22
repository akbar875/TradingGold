"""Read-only MT5 adapter, lazy imported so offline tooling needs no terminal."""

import importlib
import math
import time
from types import ModuleType
from typing import Any


def diagnose(symbol: str) -> dict[str, Any]:
    try:
        mt5: ModuleType = importlib.import_module("MetaTrader5")
    except ImportError:
        return {"status": "NOT_READY", "reason_code": "MT5_PACKAGE_MISSING"}
    if not mt5.initialize():
        return {"status": "NOT_READY", "reason_code": "MT5_INITIALIZE_FAILED"}
    try:
        terminal, account = mt5.terminal_info(), mt5.account_info()
        if terminal is None or account is None or not terminal.connected:
            return {"status": "NOT_READY", "reason_code": "MT5_DISCONNECTED"}
        if not mt5.symbol_select(symbol, True):
            return {"status": "NOT_READY", "reason_code": "SYMBOL_UNAVAILABLE"}
        info, tick = mt5.symbol_info(symbol), mt5.symbol_info_tick(symbol)
        if info is None or tick is None:
            return {"status": "NOT_READY", "reason_code": "SYMBOL_DATA_MISSING"}
        valid_tick = (
            all(math.isfinite(x) for x in (tick.bid, tick.ask, info.point))
            and tick.bid > 0
            and tick.ask >= tick.bid
            and info.point > 0
            and 0 <= time.time() - tick.time <= 120
        )
        return {
            "status": "CONNECTED" if valid_tick else "NOT_READY",
            "reason_code": "DIAGNOSTICS_ONLY" if valid_tick else "TICK_INVALID_OR_STALE",
            "account_mask": "***" + str(account.login)[-2:],
            "symbol": symbol,
            "leverage": account.leverage,
            "leverage_matches_2000": account.leverage == 2000,
            "terminal_trade_allowed": terminal.trade_allowed,
            "account_trade_allowed": account.trade_allowed,
            "spread_points": (tick.ask - tick.bid) / info.point if valid_tick else None,
            "history_status": "NOT_CHECKED",
            "model_status": "NOT_IMPLEMENTED",
            "execution_available": False,
        }
    finally:
        mt5.shutdown()
