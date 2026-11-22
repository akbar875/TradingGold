import ast
import re
from pathlib import Path

from aurum.config import load_config

ROOT = Path(__file__).resolve().parents[1]


def test_python_has_no_order_or_position_mutation_calls():
    banned = {"order_send", "OrderSend", "OrderSendAsync"}
    for directory in ("python", "dashboard"):
        for path in (ROOT / directory).rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    name = getattr(node.func, "attr", getattr(node.func, "id", ""))
                    assert name not in banned, str(path)


def test_ea_foundation_has_no_execution_api():
    for path in (ROOT / "mt5").rglob("*"):
        if path.suffix in (".mq5", ".mqh"):
            text = path.read_text()
            assert not re.search(r"\b(OrderSend|OrderSendAsync|CTrade)\b", text)


def test_presets_keep_auto_disabled():
    for path in (ROOT / "mt5/Presets").glob("*.set"):
        text = path.read_text()
        assert "InpEnableAutoTrade=false" in text
        assert "InpSignalOnly=true" in text
        assert "InpDemoOnly=true" in text


def test_shared_python_mql_defaults_match():
    config = load_config(ROOT / "config/default.yaml")
    mapping = {
        "InpSignalOnly": config.signal_only,
        "InpEnableAutoTrade": config.auto_trade,
        "InpDemoOnly": config.demo_only,
        "InpRequireAI": config.require_ai,
        "InpRequireLeverage2000": config.require_leverage_2000,
        "InpRequireNewsFilter": config.require_news_filter,
        "InpEmergencyKillSwitch": config.emergency_kill_switch,
        "InpRiskPercentPerTrade": config.risk_percent_per_trade,
        "InpMaxLot": config.max_lot,
    }
    source = (ROOT / "mt5/Experts/Aurum_Expert_AI_XAUUSD.mq5").read_text()
    for name, value in mapping.items():
        literal = str(value).lower()
        assert re.search(rf"input \w+ {name} = {re.escape(literal)};", source)
        for path in (ROOT / "mt5/Presets").glob("*.set"):
            assert f"{name}={literal}" in path.read_text()
