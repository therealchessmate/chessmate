from pathlib import Path

from data.helper_functions import load_config
from ml.dispatcher_app import DispatcherApp
from utils.logger import setup_logger

# Step 1: Load config once
CONFIG_PATH = "config.yaml"
config = load_config(CONFIG_PATH)

# Step 2: Set user/platform/game details
username = "Hikaru"
platform_name = "ChessCom"
number_of_games = 25

# Step 3: Run dispatcher app
dispatcher_app = DispatcherApp.start(config)
dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")
