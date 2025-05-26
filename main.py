from datetime import datetime, timedelta
from data.helper_functions import load_config

from ml.dispatcher_app import DispatcherApp

config = load_config()

username = "Hikaru"
platform_name = "ChessCom"
number_of_games = 25

dispatcher_app = DispatcherApp.start(config)
dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")