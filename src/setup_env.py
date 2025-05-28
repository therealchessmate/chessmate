import subprocess
import sys
from pathlib import Path
from ruamel.yaml import YAML

yaml = YAML()

VENV_DIR = Path("venv")
PIP = VENV_DIR / "bin" / "pip"
PYTHON = VENV_DIR / "bin" / "python"

REQUIREMENTS_DIR = Path("requirements")
REQUIREMENTS_IN = REQUIREMENTS_DIR / "requirements.in"
REQUIREMENTS_TXT = REQUIREMENTS_DIR / "requirements.txt"
DEV_REQUIREMENTS_IN = REQUIREMENTS_DIR / "dev-requirements.in"
DEV_REQUIREMENTS_TXT = REQUIREMENTS_DIR / "dev-requirements.txt"

def create_venv():
    if not VENV_DIR.exists():
        print("[SETUP] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        print("[SETUP] Virtual environment already exists.")

def install_pip_tools():
    print("[SETUP] Installing pip-tools...")
    subprocess.run([str(PIP), "install", "--upgrade", "pip", "setuptools", "wheel", "pip-tools"], check=True)

def compile_requirements():
    print("[SETUP] Compiling user and dev requirements...")
    subprocess.run([str(PYTHON), "-m", "piptools", "compile", str(REQUIREMENTS_IN)], check=True)
    subprocess.run([str(PYTHON), "-m", "piptools", "compile", str(DEV_REQUIREMENTS_IN)], check=True)

def install_dependencies(config):
    print("[SETUP] Installing user dependencies...")
    subprocess.run([str(PIP), "install", "-r", str(REQUIREMENTS_TXT)], check=True)

    if config.get("install_dev_dependencies", False):
        print("[SETUP] Installing dev dependencies...")
        subprocess.run([str(PIP), "install", "-r", str(DEV_REQUIREMENTS_TXT)], check=True)
    else:
        print("[SETUP] Skipping dev dependencies...")

def update_config_flag(config, config_path):
    config["first_time_setup"] = False
    with open(config_path, "w") as f:
        yaml.dump(config, f)
    print("[SETUP] Config updated: first_time_setup = false")

def run(config, config_path):
    if config.get("first_time_setup", False):
        create_venv()
        install_pip_tools()
        compile_requirements()
        install_dependencies(config)
        update_config_flag(config, config_path)
        print("[SETUP] Environment setup complete.")
    else:
        print("[SETUP] Skipping setup: already completed.")