import logging
import os

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


