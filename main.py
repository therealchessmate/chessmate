import os
import sys
from logic.lichess_wrapper import LichessWrapper
from data.gc_connector import GCPostgresConnector
from ml.dispatcher_app import DispatcherApp

RUN_LOCAL = os.getenv("RUN_LOCAL", "False").strip().lower() == "true"

if RUN_LOCAL:
    database_connector = None
else:
    # Get DB connector specified for gc
    database_connector = GCPostgresConnector()

if __name__ == "__main__":
    from datetime import datetime, timedelta

    lichess = LichessWrapper(token="None") 

    username = "MagnusCarlsen"
    start_dt_utc = datetime(2023, 1, 1)
    end_dt_utc = datetime(2023, 12, 31)

    environment = os.getenv("ENVIRONMENT", "dev")
    test_runs = int(os.getenv("TEST_RUNS", "3"))

    app = DispatcherApp(environment=environment, test_runs=test_runs)
    app.run(username, start_dt_utc, end_dt_utc)
    
