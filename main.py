from datetime import datetime, timedelta
from data.helper_functions import load_config

from ml.dispatcher_app import DispatcherApp

config = load_config()

username = "MetiForce"
platform_name = "Lichess"
number_of_games = 10

dispatcher_app = DispatcherApp.start(config)
dispatcher_app.analyse(username, platform_name, number_of_games=number_of_games)

print("done")