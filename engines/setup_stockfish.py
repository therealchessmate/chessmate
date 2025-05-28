import os
import tarfile
import zipfile
import platform
import requests
from utils.logger import logger

def ensure_stockfish_installed(stockfish_path: str) -> str:
    stockfish_dir = os.path.join(stockfish_path, "stockfish")

    # ✅ If folder exists, skip everything
    if os.path.isdir(stockfish_dir):
        logger.info(f"Stockfish folder already exists at {stockfish_dir}")
        return stockfish_dir

    os.makedirs(stockfish_path, exist_ok=True)

    system = platform.system()
    if system == "Darwin":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-macos-m1-apple-silicon.tar"
        archive_path = os.path.join(stockfish_path, "stockfish.tar")
    elif system == "Linux":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-linux.zip"
        archive_path = os.path.join(stockfish_path, "stockfish.zip")
    elif system == "Windows":
        url = "https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-windows.zip"
        archive_path = os.path.join(stockfish_path, "stockfish.zip")
    else:
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
        raise RuntimeError(f"Unknown archive format: {archive_path}")

    os.remove(archive_path)
    logger.info(f"Stockfish extracted to {stockfish_path}")
    return stockfish_dir
