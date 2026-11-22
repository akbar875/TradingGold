import importlib.util
import json
import re
from hashlib import sha256
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("publisher", ROOT / "scripts/publish_issues.py")
publisher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(publisher)


def test_baseline_files_match_original_sha256():
    manifest = json.loads((ROOT / "docs/BASELINE_HASHES.json").read_text(encoding="utf-8"))
    assert set(manifest) == {
        "BACKLOG_ISSUES_AURUM_MT5.md",
        "PRD_AURUM_EXPERT_AI_MT5_V3.md",
        "PROMPT_CODEX_AURUM_EXPERT_AI_MT5_V3.md",
        "README_ID.md",
        "aurum_ai.py",
        "xauusd-trading-demo.html",
    }
    for filename, expected in manifest.items():
        assert sha256((ROOT / filename).read_bytes()).hexdigest() == expected, filename


def test_all_seed_issues_have_unique_ids_and_acceptance():
    issues = publisher.issue_files(ROOT / "docs/issues")
    assert {row[0] for row in issues} == {f"AU-{n:03}" for n in range(1, 34)}
    for _, _, path in issues:
        text = path.read_text(encoding="utf-8")
        for required in ("Acceptance criteria", "Skenario tes", "Dependencies", "Status:"):
            assert required in text


@pytest.mark.parametrize(
    "remote",
    ["https://github.com/akbar875/TradingGold.git", "git@github.com:akbar875/TradingGold.git"],
)
def test_remote_detection(remote):
    assert publisher.github_repo(remote) == "akbar875/TradingGold"


def test_dry_run_never_uses_gh(monkeypatch, capsys):
    calls = []

    def run(args):
        calls.append(args)
        assert args[0] == "git"
        return "https://github.com/akbar875/TradingGold.git"

    monkeypatch.setattr(publisher, "run", run)
    assert publisher.main(["--dry-run"]) == 0
    assert json.loads(capsys.readouterr().out)["count"] == 33
    assert len(calls) == 1


def test_publisher_skips_existing_marker(monkeypatch):
    calls = []

    def run(args):
        calls.append(args)
        if args[0] == "git":
            return "https://github.com/akbar875/TradingGold.git"
        if args[1] == "api":
            return "[AU-001] existing"
        return ""

    monkeypatch.setattr(publisher, "run", run)
    monkeypatch.setattr(publisher.shutil, "which", lambda _: "gh")
    assert publisher.main(["--publish"]) == 0
    created = [c for c in calls if c[:3] == ["gh", "issue", "create"]]
    assert len(created) == 32
    assert all(not re.search(r"\[AU-001\]", " ".join(c)) for c in created)
    assert all("--body-file" in c for c in created)


def test_json_schema_itself_is_valid():
    schema = json.loads((ROOT / "config/signal.schema.json").read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
