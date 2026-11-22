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


def complete_issue(repo: str, issue_id: str, pull_request: int) -> None:
    """Close only an owned seed issue after its explicitly linked PR is merged."""
    login = run(["gh", "api", "user", "--jq", ".login"])
    matches = json.loads(
        run(
            [
                "gh",
                "issue",
                "list",
                "--repo",
                repo,
                "--state",
                "all",
                "--limit",
                "1000",
                "--json",
                "number,title,author,state",
            ]
        )
    )
    matches = [row for row in matches if row["title"].startswith(f"[{issue_id}] ")]
    if len(matches) != 1:
        raise ValueError("Issue harus ditemukan tepat satu kali")
    issue = matches[0]
    if issue["author"]["login"].casefold() != login.casefold():
        raise ValueError("Tidak boleh menutup issue milik orang lain")
    pr = json.loads(run(["gh", "api", f"repos/{repo}/pulls/{pull_request}"]))
    if (
        not pr["merged_at"]
        or pr["base"]["ref"] != "main"
        or pr["base"]["repo"]["full_name"].casefold() != repo.casefold()
        or not re.search(
            rf"(?im)^\s*(?:closes|fixes|resolves|issue:)\s+#{issue['number']}\s*$", pr["body"] or ""
        )
    ):
        raise ValueError("PR harus merged ke main repo ini dan merujuk Issue: #issue")
    if issue["state"] == "CLOSED":
        print(f"SKIP {issue_id}: sudah CLOSED; merged PR #{pull_request} terverifikasi")
        return
    print(
        run(["gh", "issue", "close", str(issue["number"]), "--repo", repo, "--reason", "completed"])
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--publish", action="store_true")
    parser.add_argument("--provider", choices=["auto", "github"], default="auto")
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument("--complete", metavar="AU-ID", help="Selesaikan seed issue milik sendiri")
    parser.add_argument("--pull-request", type=int, help="PR merged yang menyelesaikan issue")
    args = parser.parse_args(argv)
    try:
        repo = github_repo(run(["git", "remote", "get-url", "origin"]))
        issues = issue_files(ROOT / "docs/issues")
        if args.complete:
            if (
                args.complete not in {row[0] for row in issues}
                or not args.pull_request
                or args.pull_request < 1
            ):
                raise ValueError("--complete membutuhkan ID lokal dan --pull-request positif")
            if not args.publish:
                print(
                    json.dumps(
                        {
                            "status": "DRY_RUN",
                            "repo": repo,
                            "complete": args.complete,
                            "pull_request": args.pull_request,
                        }
                    )
                )
                return 0
        elif args.pull_request:
            raise ValueError("--pull-request membutuhkan --complete")
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
        if args.complete:
            complete_issue(repo, args.complete, args.pull_request)
            return 0
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
