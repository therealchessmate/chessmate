# utils/logger.py

import logging
import os
import json
from data.helper_functions import load_config


def setup_logger(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    logger = logging.getLogger("chessmate")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    return logger

config = load_config()


log_path = config["paths"]["logs"]
logger = setup_logger(log_path)
