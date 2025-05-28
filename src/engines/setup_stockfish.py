import os
import subprocess
import shutil
import platform
import logging

logger = logging.getLogger("chessmate")

def clone_repo_if_missing(repo_url: str, local_path: str):
    if os.path.exists(local_path):
        logger.info(f"Repo already exists at {local_path}")
        return
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    logger.info(f"Cloning repo from {repo_url} to {local_path}...")
    try:
        subprocess.run(["git", "clone", repo_url, local_path], check=True)
        logger.info(f"Successfully cloned {repo_url}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to clone repo: {e}")
        raise


def get_stockfish_arch():
    """
    Detect the correct architecture string to pass to Stockfish's makefile.
    """
    arch = platform.machine().lower()
    if arch == "x86_64":
        return "x86-64"  # dash, not underscore
    elif arch in ("arm64", "aarch64"):
        return "armv8"  # stockfish uses armv8
    else:
        logger.warning(f"Unknown machine arch '{arch}', defaulting to x86-64")
        return "x86-64"


def build_stockfish(source_path, arch=None, copy_to=None, force_rebuild=False):
    """
    Build Stockfish if not already built or if force_rebuild is True.

    Args:
        source_path: Path to the Stockfish repo root.
        arch: Architecture string (e.g. 'arm64', 'x86_64'). If None, detect automatically.
        copy_to: Optional path to copy the built binary after build.
        force_rebuild: If True, always rebuild even if binary exists.
    """
    if copy_to and os.path.exists(copy_to) and not force_rebuild:
        logger.info(f"Binary already exists at {copy_to}, skipping build.")
        return

    if arch is None:
        arch = platform.machine()
        if arch.lower() == "armv8":
            arch = "arm64"
    logger.info(f"Building Stockfish for arch: {arch}")

    src_path = os.path.join(source_path, "src")
    try:
        subprocess.run(["make", f"ARCH={arch}"], cwd=src_path, check=True)
        logger.info("Stockfish built successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Stockfish: {e}")
        return

    if copy_to:
        os.makedirs(os.path.dirname(copy_to), exist_ok=True)
        binary_source = os.path.join(src_path, "stockfish")
        if os.path.exists(binary_source):
            shutil.copy(binary_source, copy_to)
            logger.info(f"Copied binary to {copy_to}")
        else:
            logger.warning(f"Binary not found at {binary_source}; skipping copy.")


def run(config):
    stockfish_repos = config.get("stockfish_repos", {})
    official_path = stockfish_repos.get("official_path")
    official_url = stockfish_repos.get("official_url")
    patched_path = stockfish_repos.get("patched_path")
    patched_url = stockfish_repos.get("patched_url")
    binaries_path = config["paths"]["stockfish"]

    force_rebuild_official = config.get("force_rebuild", {}).get("official_stockfish", False)
    force_rebuild_patched = config.get("force_rebuild", {}).get("patched_stockfish", False)

    if not all([official_path, official_url, patched_path, patched_url]):
        raise ValueError("Stockfish repo paths or URLs are missing in config file")

    clone_repo_if_missing(official_url, official_path)
    build_stockfish(
        official_path,
        copy_to=os.path.join(binaries_path, "official_stockfish"),
        force_rebuild=force_rebuild_official
    )

    clone_repo_if_missing(patched_url, patched_path)
    build_stockfish(
        patched_path,
        copy_to=os.path.join(binaries_path, "patched_stockfish"),
        force_rebuild=force_rebuild_patched
    )

