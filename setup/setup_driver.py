import sys
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = PROJECT_ROOT / ".venv"

def running_inside_venv():
    return Path(sys.prefix) == VENV_DIR.resolve()

def create_venv():
    print("[INFO] Creating virtual environment...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)

def install_early_dependencies():
    print("[INFO] Installing early dependencies (PyYAML, ruamel.yaml)...")
    pip_executable = VENV_DIR / "bin" / "pip"
    subprocess.run([str(pip_executable), "install", "pyyaml", "ruamel.yaml"], check=True)


def load_config(config_path):
    import yaml
    if not config_path.exists():
        print("[WARN] setup.yaml not found, returning empty config")
        return {}
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def main():
    config_path = Path(__file__).parent / "setup.yaml"

    if not running_inside_venv():
        create_venv()
        install_early_dependencies()
        venv_python = VENV_DIR / "bin" / "python"
        print(f"[INFO] Relaunching script inside virtual environment: {venv_python}")
        subprocess.run([str(venv_python), *sys.argv], check=True)
        return

    print("[INFO] Running inside virtual environment")
    config = load_config(config_path)
    print("[INFO] Loaded config:", config)

    from setup_env import run as run_env_requirements
    run_env_requirements(config, config_path)

    from setup_stockfish import run as run_setup_stockfish
    run_setup_stockfish(config)

if __name__ == "__main__":
    main()
