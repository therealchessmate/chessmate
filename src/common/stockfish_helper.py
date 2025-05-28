# chessmate/common/stockfish_helper.py

import subprocess
from pathlib import Path
import os

def run_cmd(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)

def clone_repo(git_url: str, target_path: Path):
    if target_path.exists():
        print(f"Repo already exists at {target_path}, skipping clone.")
    else:
        print(f"Cloning {git_url} into {target_path} ...")
        run_cmd(["git", "clone", git_url, str(target_path)])

def build_stockfish(repo_path: Path):
    print(f"Building Stockfish at {repo_path} ...")
    run_cmd(["make", "-j4"], cwd=repo_path)
    binary_path = repo_path / ("stockfish.exe" if os.name == "nt" else "stockfish")
    if not binary_path.exists():
        raise FileNotFoundError(f"Build failed, binary not found at {binary_path}")
    print(f"Built binary at {binary_path}")
    return binary_path

def launch_stockfish(binary_path: Path):
    proc = subprocess.Popen(
        [str(binary_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    return proc

def send_command(proc, cmd):
    proc.stdin.write(cmd + "\n")
    proc.stdin.flush()

def read_line(proc):
    return proc.stdout.readline().strip()
