import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path


class DeviceController:
    """Minimal hardware controller used by integration tests."""

    async def connect(self) -> None:
        print("[HW] Connecting to robot…")

    async def run_self_test(self) -> str:
        print("[HW] Running self-test.")
        await asyncio.sleep(0.5)
        return "OK"

    async def run_demo(self) -> int:
        print("[HW] Executing demo.py")
        repo_root = (
            subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True)
            .strip()
        )
        env = os.environ.copy()
        cmd = [sys.executable, "demo.py"]
        if os.getenv("SIMULATION") == "1":
            cmd.extend(["--backend", "sim"])
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=repo_root,
            env=env,
        )
        stdout, stderr = await proc.communicate()
        output = stdout.decode()
        error = stderr.decode()
        print(output)
        if error:
            print(error, file=sys.stderr)
        m = re.search(r"Actual position:\s*(\d+)", output)
        return int(m.group(1)) if m else -1

    def close(self) -> None:
        print("[HW] Disconnected.")
