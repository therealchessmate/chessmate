#!/usr/bin/env python3
"""
setup_stockfish.py
- Clones Stockfish (official/patched) if missing
- Checks out a given tag into a local branch (no detached HEAD)
- Builds with robust fallbacks across older/newer Makefiles
- Copies the engine binary to a given path

Expected config shape:
{
  "stockfish_repos": {
    "official_path": "/abs/path/stockfish_official",
    "official_url":  "https://github.com/official-stockfish/Stockfish.git",
    "patched_path":  "/abs/path/stockfish_patched",
    "patched_url":   "https://github.com/therealchessmate/PatchedClassicalSF.git"
  },
  "paths": {
    "stockfish": "/abs/path/binaries"   # where to drop built binaries
  },
  "tags": {
    "official_stockfish": "SF_classical",  # example
    "patched_stockfish":  "SF_classical"   # example
  },
  "force_rebuild": {
    "official_stockfish": false,
    "patched_stockfish":  false
  }
}
"""

import os
import subprocess
import shutil
import platform
import logging
from typing import List, Optional

# -------------------
# Logging
# -------------------
logger = logging.getLogger("setup")
if not logger.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(_h)
logger.setLevel(logging.INFO)


# -------------------
# Git helpers
# -------------------
def run_cmd(cmd: List[str], cwd: Optional[str] = None) -> None:
    """Run a command, raise if non-zero, stream output."""
    logger.debug(f"Running: {' '.join(cmd)} (cwd={cwd or os.getcwd()})")
    subprocess.run(cmd, cwd=cwd, check=True)


def clone_repo_if_missing(repo_url: str, local_path: str) -> None:
    if os.path.exists(local_path) and os.path.isdir(os.path.join(local_path, ".git")):
        logger.info(f"Repo already exists at {local_path}")
        return
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    logger.info(f"Cloning repo from {repo_url} to {local_path}...")
    run_cmd(["git", "clone", repo_url, local_path])
    logger.info(f"Successfully cloned {repo_url}")


def checkout_stockfish_tag(repo_path: str, tag: str) -> None:
    """
    Create a local branch from the tag (avoid detached HEAD).
    If branch exists, re-create it at the tag.
    """
    branch = f"build-{tag}"
    logger.info(f"Checking out Stockfish tag '{tag}' in {repo_path}")
    try:
        run_cmd(["git", "fetch", "--all", "--tags"], cwd=repo_path)
        # Delete existing branch if present (to ensure it tracks the tag)
        # Ignore errors if it doesn't exist.
        subprocess.run(["git", "branch", "-D", branch], cwd=repo_path)
        # Create branch at tag
        run_cmd(["git", "checkout", f"tags/{tag}", "-b", branch], cwd=repo_path)
        logger.info(f"Checked out Stockfish tag '{tag}' onto branch '{branch}'")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to checkout tag {tag}: {e}")
        raise


# -------------------
# Build logic
# -------------------
def get_stockfish_arch(stockfish_tag: Optional[str] = None) -> str:
    """
    Choose a sensible default ARCH based on platform.
    We don’t assume tag semantics; we’ll try fallbacks in build_stockfish().
    """
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":
        if machine == "arm64":
            return "arm64"           # primary (older tags)
        elif machine == "x86_64":
            return "x86-64"
    elif system == "Linux":
        if machine == "x86_64":
            return "x86-64"
        elif "arm" in machine or "aarch" in machine:
            return "armv8"
    elif system == "Windows":
        return "x86-64"

    raise RuntimeError(f"Unsupported platform: {system} {machine}")


def build_stockfish(source_path: str,
                    arch: Optional[str] = None,
                    copy_to: Optional[str] = None,
                    force_rebuild: bool = False) -> None:
    """
    Build Stockfish with robust fallbacks:
    - Try target 'profile-build', then 'build'
    - Try ARCH values in sequence (platform-appropriate)
    - Lastly try with no ARCH to let Makefile auto-detect
    """
    # Skip if binary already exists and no force rebuild requested
    if copy_to and os.path.exists(copy_to) and not force_rebuild:
        logger.info(f"Binary already exists at {copy_to}, skipping build.")
        return

    src_path = os.path.join(source_path, "src")
    if not os.path.isdir(src_path):
        raise RuntimeError(f"src path not found: {src_path}")

    system = platform.system()
    machine = platform.machine().lower()

    # Prepare ARCH candidates
    arch_candidates: List[Optional[str]] = []
    if arch:
        arch_candidates.append(arch)

    if system == "Darwin" and machine == "arm64":
        for a in ("arm64", "apple-silicon"):
            if a not in arch_candidates:
                arch_candidates.append(a)
    elif system == "Darwin" and machine == "x86_64":
        for a in ("x86-64", "x86-64-modern", "x86-64-avx2"):
            if a not in arch_candidates:
                arch_candidates.append(a)
    elif system == "Linux" and machine == "x86_64":
        for a in ("x86-64", "x86-64-modern", "x86-64-avx2"):
            if a not in arch_candidates:
                arch_candidates.append(a)
    else:
        for a in ("x86-64", "armv8"):
            if a not in arch_candidates:
                arch_candidates.append(a)

    # Also allow Makefile auto-detection (no ARCH)
    arch_candidates.append(None)

    # Targets to try
    targets = ["profile-build", "build"]

    # Clean before trying (best effort)
    subprocess.run(["make", "clean"], cwd=src_path)

    last_err: Optional[Exception] = None
    for tgt in targets:
        for a in arch_candidates:
            cmd = ["make", "-j", tgt] + ([f"ARCH={a}"] if a else [])
            logger.info(f"Building Stockfish: {' '.join(cmd)} (cwd={src_path})")
            try:
                run_cmd(cmd, cwd=src_path)
                logger.info("Stockfish built successfully.")

                # Determine the built binary path
                binary_source = os.path.join(src_path, "stockfish")
                if not os.path.exists(binary_source):
                    # Some older tags/builds might place it differently; add fallback checks here if needed.
                    raise FileNotFoundError(f"Binary not found at {binary_source}")

                if copy_to:
                    os.makedirs(os.path.dirname(copy_to), exist_ok=True)
                    shutil.copy(binary_source, copy_to)
                    logger.info(f"Copied binary to {copy_to}")

                return  # success
            except Exception as e:
                last_err = e
                logger.warning(f"Build failed with target={tgt} ARCH={a or 'auto'}: {e}")
                # Try next combination
                continue

    raise RuntimeError(
        f"Stockfish build failed after trying targets={targets} and ARCHs={arch_candidates}"
    ) from last_err


# -------------------
# Orchestration
# -------------------
def run(config: dict) -> None:
    stockfish_repos = config.get("stockfish_repos", {})
    official_path = stockfish_repos.get("official_path")
    official_url = stockfish_repos.get("official_url")
    patched_path = stockfish_repos.get("patched_path")
    patched_url = stockfish_repos.get("patched_url")

    binaries_path = config["paths"]["stockfish"]
    official_tag = config.get("tags", {}).get("official_stockfish", "SF_classical")
    patched_tag = config.get("tags", {}).get("patched_stockfish", "SF_classical")

    force_rebuild_official = config.get("force_rebuild", {}).get("official_stockfish", False)
    force_rebuild_patched = config.get("force_rebuild", {}).get("patched_stockfish", False)

    if not all([official_path, official_url, patched_path, patched_url]):
        raise ValueError("Stockfish repo paths or URLs are missing in config file")

    # Optional: build official Stockfish
    create_official_version = False
    if create_official_version:
        clone_repo_if_missing(official_url, official_path)
        checkout_stockfish_tag(official_path, official_tag)
        arch_official = get_stockfish_arch(official_tag)
        build_stockfish(
            official_path,
            arch=arch_official,
            copy_to=os.path.join(binaries_path, "official_stockfish"),
            force_rebuild=force_rebuild_official
        )

    # Build patched Stockfish
    create_patched_version = True
    if create_patched_version:
        clone_repo_if_missing(patched_url, patched_path)
        checkout_stockfish_tag(patched_path, patched_tag)
        arch_patched = get_stockfish_arch(patched_tag)
        build_stockfish(
            patched_path,
            arch=arch_patched,
            copy_to=os.path.join(binaries_path, "patched_stockfish"),
            force_rebuild=force_rebuild_patched
        )
