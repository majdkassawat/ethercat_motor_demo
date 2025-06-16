import configparser
import datetime
import os
import subprocess
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent / "config"
OUTPUT_DIR = Path(__file__).resolve().parent / "outputs"


def load_config():
    cfg = configparser.ConfigParser()
    if CONFIG_FILE.exists():
        cfg.read(CONFIG_FILE)
    return cfg


def run_tests():
    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = OUTPUT_DIR / f"test_{timestamp}.log"

    env = os.environ.copy()
    backend = env.get("BACKEND", "hw")
    start = datetime.datetime.now()
    proc = subprocess.run(
        ["pytest", "-s", "tests/hardware/test_device_controller.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        env=env,
    )
    end = datetime.datetime.now()

    with open(output_path, "w") as f:
        f.write(f"test_name=DeviceController\n")
        f.write(f"start={start.isoformat()}\n")
        f.write(f"end={end.isoformat()}\n")
        f.write(f"duration={(end-start).total_seconds():.2f}s\n")
        f.write(f"backend={backend}\n")
        f.write(f"returncode={proc.returncode}\n\n")
        f.write(proc.stdout)

    return output_path


def git_commit(path: Path):
    subprocess.run(["git", "add", str(path)])
    subprocess.run(["git", "commit", "-m", f"Add test output {path.name}"])


def main():
    load_config()  # placeholder for credentials usage
    log_file = run_tests()
    git_commit(log_file)


if __name__ == "__main__":
    main()
