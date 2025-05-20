import os
import sys
from logic.lichess_wrapper import LichessWrapper

RUN_LOCAL = os.getenv("RUN_LOCAL", "False").strip().lower() == "true"

if RUN_LOCAL:
    database_connector = None
else:
    # Get DB connector specified for platform (implement later)
    database_connector = "DB_CONNECTION_PLACEHOLDER"

if __name__ == "__main__":
    from datetime import datetime, timedelta

    lichess = LichessWrapper(token="your_token_here")  # or None if public

    username = "MagnusCarlsen"
    start_dt = datetime(2023, 1, 1)
    end_dt = datetime(2023, 12, 31)

    pgns = lichess.get_pgns_by_user(username, start_dt, end_dt)
    print(pgns[:1000])  # Print first 1000 chars of PGNs
