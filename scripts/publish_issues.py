"""Publish reviewed local issue bodies to GitHub; default is a network-free dry run."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def github_repo(remote: str) -> str:
    match = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:)([\w.-]+/[\w.-]+?)(?:\.git)?", remote
    )
    if not match:
        raise ValueError("Remote GitHub tidak didukung")
    return match[1]


def run(args: list[str]) -> str:
    result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if result.returncode:
        # Never echo stderr containing possible auth/URL secrets.
        raise RuntimeError(f"Perintah {args[0]} {args[1]} gagal (exit {result.returncode})")
    return result.stdout.strip()


def issue_files(directory: Path) -> list[tuple[str, str, Path]]:
    issues = []
    seen = set()
    for path in sorted(directory.glob("AU-*.md")):
        first = path.read_text(encoding="utf-8").splitlines()[0]
        match = re.fullmatch(r"# (\[(AU-\d{3})\] .+)", first)
        if not match or match[2] in seen:
            raise ValueError(f"ID/judul issue invalid/duplikat: {path.name}")
        seen.add(match[2])
        issues.append((match[2], match[1], path))
    if not issues:
        raise ValueError("Tidak ada issue lokal")
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--provider", choices=["auto", "github"], default="auto")
    parser.add_argument("--label", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        repo = github_repo(run(["git", "remote", "get-url", "origin"]))
        issues = issue_files(ROOT / "docs/issues")
        if not args.publish:
            print(
                json.dumps(
                    {
                        "status": "DRY_RUN",
                        "repo": repo,
                        "count": len(issues),
                        "issues": [x[1] for x in issues],
                    },
                    indent=2,
                )
            )
            return 0
        if not shutil.which("gh"):
            raise RuntimeError("NOT PUBLISHED: GitHub CLI (gh) belum tersedia")
        run(["gh", "auth", "status"])
        titles = run(
            [
                "gh",
                "api",
                "--paginate",
                f"repos/{repo}/issues?state=all&per_page=100",
                "--jq",
                ".[] | select(.pull_request == null) | .title",
            ]
        )
        existing = set(re.findall(r"^\[(AU-\d{3})\] ", titles, re.MULTILINE))
        for issue_id, title, path in issues:
            if issue_id in existing:
                print(f"SKIP {issue_id}: sudah ada")
                continue
            command = [
                "gh",
                "issue",
                "create",
                "--repo",
                repo,
                "--title",
                title,
                "--body-file",
                str(path),
            ]
            for label in args.label:
                command.extend(["--label", label])
            print(run(command))
            existing.add(issue_id)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
