import os
import stat
import zipfile
import tarfile
import platform
import requests

from utils.logger import logger

def find_stockfish_binary(root_path, binary_name):
    for dirpath, _, filenames in os.walk(root_path):
        if binary_name in filenames:
            return os.path.join(dirpath, binary_name)
    return None

def ensure_stockfish_installed(stockfish_path: str) -> str:
    binary_name = "stockfish"
    if platform.system() == "Windows":
        binary_name += ".exe"

    expected_binary_path = os.path.join(stockfish_path, binary_name)

    # Instead of just checking expected_binary_path,
    # search recursively for any existing binary:
    actual_binary = find_stockfish_binary(stockfish_path, binary_name)
    if actual_binary:
        logger.info(f"Stockfish already present at {actual_binary}")
        if actual_binary != expected_binary_path:
            os.replace(actual_binary, expected_binary_path)
        return expected_binary_path

    os.makedirs(stockfish_path, exist_ok=True)

    system = platform.system()
    if system == "Darwin":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-macos-m1-apple-silicon.tar"
        archive_path = os.path.join(stockfish_path, "stockfish.tar")  # save as .tar
    elif system == "Linux":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-linux.zip"
        archive_path = os.path.join(stockfish_path, "stockfish.zip")  # save as .zip
    elif system == "Windows":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows.zip"
        archive_path = os.path.join(stockfish_path, "stockfish.zip")  # save as .zip
    else:
        logger.error(f"Unsupported OS: {system}")
        raise RuntimeError(f"Unsupported OS: {system}")

    logger.info(f"Downloading Stockfish from {url}...")
    response = requests.get(url)
    response.raise_for_status()

    with open(archive_path, "wb") as f:
        f.write(response.content)
    logger.info("Download complete.")

    logger.info("Extracting...")
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as archive:
            archive.extractall(stockfish_path)
    elif archive_path.endswith(".tar") or archive_path.endswith(".tar.gz") or archive_path.endswith(".tgz"):
        with tarfile.open(archive_path, "r:*") as archive:
            archive.extractall(stockfish_path)
    else:
        logger.error(f"Unknown archive format: {archive_path}")
        raise RuntimeError(f"Unknown archive format: {archive_path}")

    os.remove(archive_path)

    actual_binary = find_stockfish_binary(stockfish_path, binary_name)
    if actual_binary is None:
        logger.error("Failed to find Stockfish binary after extraction.")
        raise FileNotFoundError("Stockfish binary not found after installation.")

    if actual_binary != binary_path:
        os.replace(actual_binary, binary_path)

    # Set exec perms
    if system != "Windows":
        os.chmod(binary_path, os.stat(binary_path).st_mode | stat.S_IEXEC)

    # Check file exists
    if not os.path.isfile(binary_path):
        logger.error("Failed to install Stockfish.")
        raise FileNotFoundError("Stockfish binary not found after installation.")

    logger.info(f"Stockfish installed at {binary_path}")
    return binary_path
