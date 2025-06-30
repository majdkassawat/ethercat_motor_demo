import argparse
import os
import subprocess
import sys
import time
import shutil
import zipfile
from pathlib import Path

REMOTE = "origin"
BRANCH = "main"
RESULTS_PREFIX = "results/"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hardware-in-the-loop test runner")
    p.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="run tests automatically without prompting",
    )
    p.add_argument(
        "--sleep",
        type=int,
        default=60,
        metavar="SECONDS",
        help="how long to wait between polling cycles (default: 60)",
    )
    return p.parse_args()


def repo_root() -> Path:
    out = subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True)
    return Path(out.strip())


def run(cmd, cwd=None):
    print(f"+ {cmd}")
    return subprocess.call(cmd, shell=True, cwd=cwd) == 0


def run_tests(root: Path) -> bool:
    return run("pytest -s --alluredir TestResults tests/hardware/test_device_controller.py", cwd=root)


def generate_report(root: Path) -> bool:
    if shutil.which("allure") is None:
        print("Allure CLI not found, skipping report generation")
        return False
    return run("allure generate TestResults -o AllureReport --clean", cwd=root)


def zip_report(root: Path, sha: str) -> Path:
    zip_name = root / f"allure-{sha}.zip"
    if zip_name.exists():
        zip_name.unlink()
    with zipfile.ZipFile(zip_name, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in (root / "AllureReport").rglob("*"):
            if p.is_file():
                zf.write(p, p.relative_to(root / "AllureReport"))
    return zip_name


def push_results(root: Path, sha: str, zip_path: Path):
    branch = RESULTS_PREFIX + sha
    run(f"git checkout -B {branch}", cwd=root)
    run(f"git add {zip_path.name}", cwd=root)
    run(f"git commit -m 'Add Allure report for {sha}'", cwd=root)
    run(f"git push {REMOTE} {branch}", cwd=root)
    run(f"git checkout {BRANCH}", cwd=root)


def main():
    args = parse_args()
    root = repo_root()
    while True:
        run(f"git fetch {REMOTE}", cwd=root)
        local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        remote_sha = subprocess.check_output(["git", "rev-parse", f"{REMOTE}/{BRANCH}"], cwd=root, text=True).strip()
        if local_sha == remote_sha:
            print(f"No new commit. Sleeping {args.sleep} s.")
            time.sleep(args.sleep)
            continue
        run(f"git reset --hard {REMOTE}/{BRANCH}", cwd=root)
        if not args.yes:
            ans = input(f"New commit {remote_sha[:7]} detected. Run integration tests now? [y/N] ")
            if ans.lower() != 'y':
                continue
        else:
            print(f"New commit {remote_sha[:7]} detected. Running integration tests...")
        if not run_tests(root):
            print("Tests failed")
            continue
        if generate_report(root):
            zip_path = zip_report(root, remote_sha[:7])
            push_results(root, remote_sha[:7], zip_path)


if __name__ == "__main__":
    main()
