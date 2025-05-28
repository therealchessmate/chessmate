import importlib
import yaml
import os

def load_config(config_path: str = "config.yaml") -> dict:
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config

def load_class(import_path: str):
    """Dynamically import a class from string path."""
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


