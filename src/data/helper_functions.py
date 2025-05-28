import json
import importlib


def load_config(path="config.json"):
    with open(path, "r") as f:
        return json.load(f)
    

def load_class(import_path: str):
    """Dynamically import a class from string path."""
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


