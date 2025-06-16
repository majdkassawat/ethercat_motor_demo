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
    root = repo_root()
    while True:
        run(f"git fetch {REMOTE}", cwd=root)
        local_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        remote_sha = subprocess.check_output(["git", "rev-parse", f"{REMOTE}/{BRANCH}"], cwd=root, text=True).strip()
        if local_sha == remote_sha:
            print("No new commit. Sleeping 60 s.")
            time.sleep(60)
            continue
        run(f"git reset --hard {REMOTE}/{BRANCH}", cwd=root)
        ans = input(f"New commit {remote_sha[:7]} detected. Run integration tests now? [y/N] ")
        if ans.lower() != 'y':
            continue
        if not run_tests(root):
            print("Tests failed")
            continue
        if generate_report(root):
            zip_path = zip_report(root, remote_sha[:7])
            push_results(root, remote_sha[:7], zip_path)


if __name__ == "__main__":
    main()
