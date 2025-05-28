from data.helper_functions import load_config
from utils.logger import setup_logger
from engines.setup_stockfish import ensure_stockfish_installed
from engines.stockfish_helper import clone_and_prepare_repos  
from ml.dispatcher_app import DispatcherApp

# Setup
config = load_config()
clone_and_prepare_repos(config)

# Step 3: Set user/platform/game details
username = "Hikaru"
platform_name = "ChessCom"
number_of_games = 25

# Step 4: Run dispatcher app (uncomment to enable)
# dispatcher_app = DispatcherApp.start(config)
# dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")
