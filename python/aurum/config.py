"""Strict, immutable configuration. Unknown keys fail closed."""

from collections.abc import Hashable
from dataclasses import asdict, dataclass, fields
from math import isfinite
from pathlib import Path
from typing import Any

import yaml

from aurum.data_quality import HistoryPolicy


class _ConfigLoader(yaml.SafeLoader):
    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        if not isinstance(node, yaml.MappingNode):
            raise ValueError("CONFIG_YAML_INVALID")
        self.flatten_mapping(node)
        mapping: dict[Hashable, Any] = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str):
                raise ValueError("CONFIG_KEY_NOT_STRING")
            if key in mapping:
                raise ValueError(f"CONFIG_DUPLICATE_KEY: {key!r}")
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


@dataclass(frozen=True)
class Settings:
    schema_version: str = "1.0"
    symbol: str = "XAUUSD"
    timeframe: str = "M15"
    confirmation_timeframes: tuple[str, ...] = ("H1", "H4")
    signal_only: bool = True
    auto_trade: bool = False
    demo_only: bool = True
    live_trading_confirmation: str = ""
    require_leverage_2000: bool = True
    require_ai: bool = False
    require_news_filter: bool = True
    emergency_kill_switch: bool = False
    risk_percent_per_trade: float = 0.25
    max_lot: float = 0.05
    max_daily_loss_percent: float = 2.0
    max_entries_per_day: int = 3
    max_open_positions_per_symbol: int = 1
    max_margin_use_percent: float = 15.0
    max_consecutive_losses: int = 3
    break_even_at_r: float = 1.0
    trailing_start_r: float = 1.5
    max_stop_distance_atr: float = 3.0
    min_planned_rr: float = 2.0
    partial_tp: bool = False
    label_horizon_bars: int = 8
    random_seed: int = 42
    signal_ttl_seconds: int = 120
    history_max_bar_move_percent: float = 10.0
    history_session_closures_utc: tuple[tuple[int, int], ...] = ()

    def __post_init__(self) -> None:
        defaults = {f.name: f.default for f in fields(self)}
        for name, default in defaults.items():
            value = getattr(self, name)
            if isinstance(default, bool):
                valid = type(value) is bool
            elif isinstance(default, int):
                valid = type(value) is int and value > 0
            elif isinstance(default, float):
                try:
                    valid = type(value) in (int, float) and isfinite(value) and value > 0
                except OverflowError:
                    valid = False
            else:
                valid = type(value) is type(default)
            if not valid:
                raise ValueError(f"CONFIG_INVALID: {name}")
        if self.schema_version != "1.0" or self.timeframe != "M15":
            raise ValueError("CONFIG_SCHEMA_OR_TIMEFRAME_UNSUPPORTED")
        if not self.symbol or any(
            c.isspace() or not c.isprintable() or c in "/\\," for c in self.symbol
        ):
            raise ValueError("CONFIG_SYMBOL_INVALID")
        if self.confirmation_timeframes != ("H1", "H4"):
            raise ValueError("CONFIG_CONFIRMATION_TIMEFRAMES_UNSUPPORTED")
        if self.risk_percent_per_trade > 100 or self.max_daily_loss_percent > 100:
            raise ValueError("CONFIG_RISK_PERCENT_INVALID")
        if self.max_margin_use_percent > 100 or self.min_planned_rr < 2:
            raise ValueError("CONFIG_MARGIN_OR_RR_INVALID")
        # Foundation deliberately cannot enable execution, even on demo.
        if self.auto_trade or not self.signal_only or not self.demo_only:
            raise ValueError("EXECUTION_NOT_IMPLEMENTED: gunakan SIGNAL_ONLY")
        if self.live_trading_confirmation or self.partial_tp:
            raise ValueError("EXECUTION_NOT_IMPLEMENTED")
        self.history_policy()

    def history_policy(self) -> HistoryPolicy:
        return HistoryPolicy(self.history_max_bar_move_percent, self.history_session_closures_utc)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def load_config(path: str | Path) -> Settings:
    try:
        source = Path(path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("CONFIG_ENCODING_INVALID") from exc
    try:
        payload = yaml.load(source, Loader=_ConfigLoader)
    except (yaml.YAMLError, RecursionError) as exc:
        raise ValueError("CONFIG_YAML_INVALID") from exc
    if not isinstance(payload, dict):
        raise ValueError("CONFIG_NOT_A_MAPPING")
    unknown = set(payload) - {f.name for f in fields(Settings)}
    if unknown:
        raise ValueError(f"CONFIG_UNKNOWN_KEYS: {sorted(unknown)}")
    if "confirmation_timeframes" in payload:
        value = payload["confirmation_timeframes"]
        if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
            raise ValueError("CONFIG_CONFIRMATION_TIMEFRAMES_INVALID")
        payload["confirmation_timeframes"] = tuple(value)
    if "history_session_closures_utc" in payload:
        closures = payload["history_session_closures_utc"]
        if not isinstance(closures, list) or not all(isinstance(pair, list) for pair in closures):
            raise ValueError("CONFIG_HISTORY_CLOSURES_INVALID")
        payload["history_session_closures_utc"] = tuple(tuple(pair) for pair in closures)
    return Settings(**payload)
