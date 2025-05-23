from datetime import datetime, timedelta
from data.helper_functions import load_config

from ml.dispatcher_app import DispatcherApp

config = load_config()

username = "MagnusCarlsen"
start_dt_utc = datetime(2023, 1, 1)
end_dt_utc = datetime(2023, 12, 31)

dispatcher_app = DispatcherApp.run(config)

#     app = DispatcherApp(environment=environment, test_runs=test_runs)
#     app.run(username, start_dt_utc, end_dt_utc)
    
