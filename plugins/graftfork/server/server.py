#!/usr/bin/env python3
"""GraftFork Antigravity MCP App Server.

Provides local git fork divergence inspection, GraftFork test-gate summary,
and an interactive side-pane / inline MCP App (`ui://graftfork/inspector.html`).
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server.fastmcp import FastMCP

APP_URI = "ui://graftfork/inspector.html"
HTML_PATH = Path(os.environ.get("GRAFTFORK_APP_HTML", Path(__file__).with_name("inspector.html")))
DEFAULT_REPO = os.environ.get("GRAFTFORK_DEFAULT_REPO", "/home/craigm26/Graft")

PANE_META = {
    "ui": {"resourceUri": APP_URI},
    "com.google.antigravity/ui": {
        "entrypoints": [
            {"type": "aux_pane", "title": "GraftFork Inspector"},
            {"type": "global", "title": "GraftFork Inspector"},
        ]
    },
}
INLINE_META = {"ui": {"resourceUri": APP_URI}}

mcp = FastMCP("graftfork-inspector")


def _git(repo: Path, *args: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), *args],
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=4,
        ).strip()
    except Exception:
        return ""


def _inspect_repo(repo_path: str) -> dict[str, Any]:
    p = Path(repo_path or DEFAULT_REPO).expanduser()
    if not p.exists() or not (p / ".git").exists():
        return {
            "repo_path": str(p),
            "valid_git": False,
            "error": "Not a git repository",
            "commits": [],
        }
    branch = _git(p, "rev-parse", "--abbrev-ref", "HEAD")
    remote = _git(p, "remote", "get-url", "origin")
    latest_tag = _git(p, "describe", "--tags", "--abbrev=0") or "none"
    ahead = _git(p, "rev-list", "--count", f"{latest_tag}..HEAD") if latest_tag != "none" else "0"
    log_raw = _git(p, "log", "-n", "6", "--pretty=format:%h|%s")
    commits = []
    for line in log_raw.splitlines():
        if "|" in line:
            sha, msg = line.split("|", 1)
            commits.append({"sha": sha, "subject": msg})
    dirty = bool(_git(p, "status", "--porcelain"))
    return {
        "repo_path": str(p),
        "valid_git": True,
        "branch": branch,
        "remote": remote,
        "latest_tag": latest_tag,
        "commits_since_tag": int(ahead) if ahead.isdigit() else 0,
        "dirty": dirty,
        "commits": commits,
    }


def _snapshot(repo_path: str = "") -> dict[str, Any]:
    return {
        "graft_cli_installed": shutil.which("graft") is not None,
        "benchmark": {
            "wrong_moves": 0,
            "results_url": "https://graftfork.com/results",
            "try_url": "https://graftfork.com",
            "claude_directory_url": "https://claude.ai/directory/graftfork",
        },
        "repo": _inspect_repo(repo_path or DEFAULT_REPO),
    }


def _result(summary: str, data: dict[str, Any]) -> types.CallToolResult:
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=summary)],
        structuredContent=data,
    )


@mcp.resource(
    APP_URI,
    name="GraftFork Inspector",
    mime_type="text/html;profile=mcp-app",
    meta={"ui": {"prefersBorder": False}},
)
def inspector_html() -> str:
    return HTML_PATH.read_text(encoding="utf-8")


@mcp.tool(name="open_graftfork_inspector", title="GraftFork Inspector", meta=PANE_META)
def open_graftfork_inspector(repo_path: str = "") -> types.CallToolResult:
    """Open the interactive GraftFork Carry Inspector side pane."""
    snap = _snapshot(repo_path)
    r = snap["repo"]
    summary = (
        f"GraftFork Inspector ready. Repo={r['repo_path']}, branch={r.get('branch', '?')}, "
        f"commits_since_tag={r.get('commits_since_tag', 0)}, benchmark wrong_moves=0."
    )
    return _result(summary, snap)


@mcp.tool(name="graft_inspect_local_repo", title="Inspect Local Fork", meta=INLINE_META)
def graft_inspect_local_repo(repo_path: str = "") -> types.CallToolResult:
    """Inspect a local git fork's branch, latest tag, and recent commits to carry."""
    snap = _snapshot(repo_path)
    r = snap["repo"]
    return _result(
        f"Fork {r['repo_path']} ({r.get('branch', '?')}): {r.get('commits_since_tag', 0)} commits since tag {r.get('latest_tag', 'none')}.",
        snap,
    )


@mcp.tool(name="graft_benchmark_status", title="GraftFork Benchmark Status", meta=INLINE_META)
def graft_benchmark_status() -> types.CallToolResult:
    """Return GraftFork's public test-gate guarantee and quick commands."""
    snap = _snapshot()
    return _result(
        "GraftFork public benchmark: 0 wrong moves (https://graftfork.com/results). "
        "CLI: `npm i -g graftfork` · Claude Connector: https://claude.ai/directory/graftfork",
        snap,
    )


if __name__ == "__main__":
    mcp.run()
