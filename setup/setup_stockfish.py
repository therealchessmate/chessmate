import os
import subprocess
import shutil
import platform
import logging

logger = logging.getLogger("setup")

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

def checkout_stockfish_tag(repo_path: str, tag: str):
    logger.info(f"Checking out Stockfish tag '{tag}' in {repo_path}")
    try:
        subprocess.run(["git", "fetch", "--all", "--tags"], cwd=repo_path, check=True)
        subprocess.run(["git", "checkout", f"tags/{tag}", "-b", f"build-{tag}"], cwd=repo_path, check=True)
        logger.info(f"Checked out Stockfish tag {tag}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to checkout tag {tag}: {e}")
        raise

def get_stockfish_arch(stockfish_tag=None):
    # Use tag to decide architecture for build, fallback to platform detection
    if stockfish_tag:
        # For NNUE builds, use "apple-silicon"
        if stockfish_tag.upper() == "SF_CLASSICAl":
            return "x86-64"
        # For pre-NNUE or older builds, use "x86-64"
        else:
            return "apple-silicon"

    # Fallback platform detection
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Darwin":  # macOS
        if machine == "arm64":
            return "apple-silicon"
        elif machine == "x86_64":
            return "x86-64-avx2"
    elif system == "Linux":
        if machine == "x86_64":
            return "x86-64-avx2"
        elif "arm" in machine or "aarch" in machine:
            return "armv8"
    elif system == "Windows":
        return "x86-64"
    raise RuntimeError(f"Unsupported platform: {system} {machine}")

def build_stockfish(source_path, arch=None, copy_to=None, force_rebuild=False):
    if copy_to and os.path.exists(copy_to) and not force_rebuild:
        logger.info(f"Binary already exists at {copy_to}, skipping build.")
        return

    arch = arch or get_stockfish_arch()
    logger.info(f"Building Stockfish for arch: {arch}")

    src_path = os.path.join(source_path, "src")
    try:
        subprocess.run(["make", "-j", "profile-build", f"ARCH={arch}"], cwd=src_path, check=True)
        logger.info("Stockfish built successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Stockfish: {e}")
        raise

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
    official_tag = config.get("tags", {}).get("official_stockfish", "sf_17.1")
    patched_tag = config.get("tags", {}).get("patched_stockfish", "sf_17.1")

    force_rebuild_official = config.get("force_rebuild", {}).get("official_stockfish", False)
    force_rebuild_patched = config.get("force_rebuild", {}).get("patched_stockfish", False)

    if not all([official_path, official_url, patched_path, patched_url]):
        raise ValueError("Stockfish repo paths or URLs are missing in config file")

    # Clone and checkout official Stockfish
    clone_repo_if_missing(official_url, official_path)
    checkout_stockfish_tag(official_path, official_tag)
    # Pass arch based on official_tag here:
    arch_official = get_stockfish_arch(official_tag)
    build_stockfish(
        official_path,
        arch=arch_official,
        copy_to=os.path.join(binaries_path, "official_stockfish"),
        force_rebuild=force_rebuild_official
    )

    # Clone and checkout patched Stockfish
    create_patched_version = False
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
