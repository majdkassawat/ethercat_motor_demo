import asyncio
import os
import re
import subprocess
import sys
from pathlib import Path


class DeviceController:
    """Minimal hardware controller used by integration tests."""

    def __init__(self) -> None:
        self.servo = None

    async def connect(self) -> None:
        print("[HW] Connecting to robot…")
        if os.getenv("SIMULATION") == "1":
            from servo_simulator import ServoSimulator
            self.servo = ServoSimulator()
            self.servo.open()
        else:
            from ethercat_servo import EthercatServo
            from get_adapter_name import get_adapter_name
            ifname = os.getenv("ECAT_IFNAME", get_adapter_name())
            self.servo = EthercatServo(ifname=ifname)
            self.servo.open()

    async def run_self_test(self) -> str:
        print("[HW] Running self-test.")
        await asyncio.sleep(0.5)
        if self.servo:
            try:
                self.servo.enable_operation()
            except Exception:
                pass
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
        if self.servo:
            try:
                self.servo.close()
            except Exception:
                pass
        print("[HW] Disconnected.")
