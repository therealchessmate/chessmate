import os
import subprocess
import sys
import yaml
from pathlib import Path

CONFIG_PATH = Path("config.yaml")
VENV_DIR = Path("venv")

def create_venv():
    if not VENV_DIR.exists():
        print("[SETUP] Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    else:
        print("[SETUP] Virtual environment already exists.")

def install_dependencies():
    pip_path = VENV_DIR / "bin" / "pip"
    print("[SETUP] Installing dependencies from requirements.txt...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)

def update_config_flag():
    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    config["first_time_setup"] = False

    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)

    print("[SETUP] Config updated: first_time_setup = false")

def is_first_time_setup():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError("Missing config.yaml")

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f)

    return config.get("first_time_setup", False)

def run():
    if is_first_time_setup():
        create_venv()
        install_dependencies()
        update_config_flag()
        print("[SETUP] Environment setup complete.")
    else:
        print("[SETUP] Skipping setup: already completed.")