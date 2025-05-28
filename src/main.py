from pathlib import Path

from data.helper_functions import load_config
from setup_env import run as run_setup_env
from engines.setup_stockfish import run as run_setup_stockfish  
from ml.dispatcher_app import DispatcherApp
from utils.logger import setup_logger

# Step 1: Load config once
CONFIG_PATH = Path("config.yaml")
config = load_config(CONFIG_PATH)

# Step 2: Setup environment
run_setup_env(config, CONFIG_PATH)

# Step 3: Setup logger
log_path = config["paths"]["logs"]
logger = setup_logger(log_path)

# Step 4: Ensure stockfish & clone repos
run_setup_stockfish(config)

# Step 5: Set user/platform/game details
username = "Hikaru"
platform_name = "ChessCom"
number_of_games = 25

# Step 6: Run dispatcher app
# dispatcher_app = DispatcherApp.start(config)
# dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")
