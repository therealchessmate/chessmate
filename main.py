from data.helper_functions import load_config
from utils.logger import setup_logger
from engines.setup_stockfish import ensure_stockfish_installed

from ml.dispatcher_app import DispatcherApp

config = load_config()
ensure_stockfish_installed(config["paths"]["stockfish"])

username = "Hikaru"
platform_name = "ChessCom"
number_of_games = 25

# dispatcher_app = DispatcherApp.start(config)
# dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")
