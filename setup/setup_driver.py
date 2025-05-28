import subprocess
import sys
from pathlib import Path
from logger import get_logger

SETUP_DIR = Path(__file__).parent
CONFIG_PATH = SETUP_DIR / "setup.yaml"
VENV_DIR = Path("venv")
PYTHON = VENV_DIR / "bin" / "python"

# Basic logger setup for this setup_driver
logger = get_logger("setup")

def ensure_pip():
    try:
        import pip
    except ImportError:
        logger.info("pip not found. Installing...")
        subprocess.run([sys.executable, "-m", "ensurepip", "--upgrade"], check=True)

def ensure_pyyaml():
    try:
        import yaml
    except ImportError:
        logger.info("PyYAML not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyyaml"], check=True)

def ensure_ruamel():
    try:
        import ruamel.yaml
    except ImportError:
        logger.info("ruamel.yaml not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "ruamel.yaml"], check=True)        

def load_config():
    import yaml
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def main():
    ensure_pip()
    ensure_pyyaml()
    ensure_ruamel()

    config = load_config()

    # Lazy import after dependencies are ensured
    sys.path.insert(0, str(SETUP_DIR))
    from setup_env import run as run_setup_env

    run_setup_env(config, CONFIG_PATH)

    from setup_stockfish import run as run_setup_stockfish
    run_setup_stockfish(config)

    logger.info("Done.")
    logger.info("Activate the venv using the following command in the terminal/cmd:")
    logger.info("  # Linux/macOS")
    logger.info("  source venv/bin/activate")
    logger.info("")
    logger.info("  # Windows CMD")
    logger.info("  venv\\Scripts\\activate.bat")
    logger.info("")
    logger.info("  # Windows PowerShell")
    logger.info("  venv\\Scripts\\Activate.ps1")
    logger.info("")
    logger.info("You can now run `src/main.py` inside the virtual environment.")

if __name__ == "__main__":
    main()
