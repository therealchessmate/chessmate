# Google Cloud version
import os
from dispatcher.dispatch_manager import DispatchManager
from datetime import datetime
import pytz
from dispatcher.connection.connection_sf import ConnectionSF
from logging import get_logger
import config
from pyspark.sql import SparkSession

def get_secret(key: str) -> str:
    """
    Placeholder for a Google Cloud secret manager or env var.
    Replace with your actual secret-fetching implementation.
    """
    return os.getenv(key)

def main() -> None:
    """
    The main method for the dispatcher application.
    Initializes services and starts the run cycle.
    """
    test_runs = int(os.getenv("TEST_RUNS", "3"))
    environment = os.getenv("ENVIRONMENT", "dev")  # Options: dev, tst, prd

    development_run = environment == 'dev'
    acceptance_run = environment == 'tst'
    prod_run = environment == 'prd'

    logger = get_logger("sf_evaluation")

    # google cloud service base URLs 
    gc_base_url = 'https://api.gc.engine/api'
    gc_acceptance_url = 'https://api.gc-acc.engine/api'

    # API endpoint for Stockfish evaluation
    gc_api_path = 'v1/evaluate'

    if acceptance_run:
        gc_acc_user = get_secret('gc-acc-user')
        gc_acc_pwd = get_secret('gc-acc-pwd')
        stockfish_acc = ConnectionSF(
            gc_acceptance_url,
            gc_api_path,
            logger,
            gc_acc_user,
            gc_acc_pwd,
            development_run,
            acceptance_run
        )
        ems_dict = {
            "api-acceptance": stockfish_acc
        }
    else:
        sf_user = get_secret('gc-user')
        sf_pwd = get_secret('gc-pwd')
        stockfish_conn = Connection_gc(
            gc_base_url,
            gc_api_path,
            logger,
            sf_user,
            sf_pwd,
            development_run,
            acceptance_run
        )

        logger.info("DISPATCHER")
        ems_dict = {
            "api-stockfish": stockfish_conn
        }

    
    spark = SparkSession.builder.appName("Stockfish_Dispatcher").getOrCreate()

    dispatcher = DispatchManager(logger, spark, ems_dict)

    try:
        last_evaluation_dt = spark.sql(
            f"SELECT * FROM {config.nemo_catalog}.evaluation_calculated ORDER BY last_delta_dt DESC LIMIT 1"
        ).collect()[0].last_delta_dt

        last_delta_dt = spark.sql(
            f"SELECT * FROM {config.nemo_catalog}.evaluation_delta ORDER BY minute_start DESC LIMIT 1"
        ).collect()[0].minute_start

    except Exception:
        logger.info("First run, tables don't exist yet.")
        now_utc = datetime.now().replace(tzinfo=pytz.UTC)
        last_evaluation_dt = now_utc
        last_delta_dt = now_utc

    logger.info("LOOP")
    if prod_run:
        while True:
            try:
                last_evaluation_dt, last_delta_dt = dispatcher.update_delta_and_evaluations(last_evaluation_dt, last_delta_dt)
            except Exception as e:
                logger.exception(e)
    else:
        remaining_runs = test_runs
        while remaining_runs > 0:
            try:
                last_evaluation_dt, last_delta_dt = dispatcher.update_delta_and_evaluations(last_evaluation_dt, last_delta_dt)
                remaining_runs -= 1
            except Exception as e:
                logger.exception(e)

if __name__ == "__main__":
    main()
