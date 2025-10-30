"""
Local MCP Process Launcher

Purpose: Launch a local MCP server process (that serves HTTP JSON-RPC)
and manage its lifecycle so the existing HTTP-based MCPClient can connect.

Mode: "process_http" — we assume the launched command exposes an HTTP endpoint
specified by MCP_LOCAL_URL (e.g., http://127.0.0.1:8787/mcp).

This avoids changing MCPClient or implementing STDIO protocol here.
"""
from __future__ import annotations

import subprocess
import sys
import os
import time
from typing import Optional, List


class LocalMCPProcess:
    """Encapsulates a local MCP process started via command/args."""

    def __init__(self, command: str, args: Optional[List[str]] = None):
        self.command = command
        self.args = args or []
        self.proc: Optional[subprocess.Popen] = None

    def start(self) -> None:
        if self.proc and self.proc.poll() is None:
            return
        creationflags = 0
        # On Windows, use CREATE_NEW_PROCESS_GROUP to allow graceful termination if needed
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP  # type: ignore[attr-defined]

        self.proc = subprocess.Popen(
            [self.command, *self.args],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL,
            text=True,
            creationflags=creationflags,
        )

    def is_running(self) -> bool:
        return self.proc is not None and self.proc.poll() is None

    def terminate(self) -> None:
        if not self.proc:
            return
        try:
            if os.name == "nt":
                self.proc.terminate()
            else:
                self.proc.terminate()
        except Exception:
            pass


def wait_for_http(url: str, timeout_seconds: int = 30) -> bool:
    """Wait until the MCP HTTP endpoint responds, up to timeout."""
    import httpx

    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            # tools/list is the canonical capability check
            resp = httpx.post(url, json={
                "jsonrpc": "2.0",
                "method": "tools/list",
                "params": {},
                "id": 1
            }, timeout=3.0)
            if resp.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def launch_local_mcp_if_needed() -> Optional[LocalMCPProcess]:
    """
    If MCP_MODE=process_http, launch the local MCP process using
    MCP_PROCESS_COMMAND and MCP_PROCESS_ARGS (JSON array or space-separated string).
    Returns the process wrapper or None if not launched.
    """
    mode = os.getenv("MCP_MODE", "http").lower()
    if mode != "process_http":
        return None

    command = os.getenv("MCP_PROCESS_COMMAND")
    args_raw = os.getenv("MCP_PROCESS_ARGS", "")
    local_url = os.getenv("MCP_LOCAL_URL")

    if not command or not local_url:
        print("⚠️  MCP process_http 模式需要 MCP_PROCESS_COMMAND 和 MCP_LOCAL_URL")
        return None

    # Parse args: prefer JSON array, fallback to space-split
    args: List[str] = []
    if args_raw:
        try:
            import json
            parsed = json.loads(args_raw)
            if isinstance(parsed, list):
                args = [str(x) for x in parsed]
            else:
                args = [a for a in str(args_raw).split(" ") if a]
        except Exception:
            args = [a for a in str(args_raw).split(" ") if a]

    proc = LocalMCPProcess(command, args)
    print(f"🚀 启动本地 MCP 进程: {command} {' '.join(args)}")
    proc.start()

    ok = wait_for_http(local_url, timeout_seconds=int(os.getenv("MCP_START_TIMEOUT", "30")))
    if not ok:
        print(f"⚠️  本地 MCP 未在超时内就绪: {local_url}")
    else:
        print(f"✅ 本地 MCP 就绪: {local_url}")
    return proc


